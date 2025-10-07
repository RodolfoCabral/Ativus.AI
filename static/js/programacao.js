let ordensServico = [];
let usuarios = [];
let currentWeek = getCurrentWeek();
let currentYear = new Date().getFullYear();

// Inicialização da página
document.addEventListener('DOMContentLoaded', function() {
    console.log('Página de programação carregada');
    initializePage();
});

// Inicializar página
async function initializePage() {
    try {
        updateWeekDisplay();
        await loadData();
        renderPriorityLines();
        renderUsuarios();
    } catch (error) {
        console.error('Erro ao inicializar página:', error);
        showNotification('Erro ao carregar dados da programação', 'error');
    }
}

// Carregar dados
async function loadData() {
    try {
        await Promise.all([
            loadOrdensServico(),
            loadUsuarios()
        ]);
    } catch (error) {
        console.error('Erro ao carregar dados:', error);
        throw error;
    }
}

// Carregar ordens de serviço em aberto
async function loadOrdensServico() {
    try {
        console.log('🔄 Carregando OS...');
        
        // CORREÇÃO: Tentar API original primeiro, depois alternativa
        let response;
        let data;
        
        try {
            // Tentar API original - incluir OS abertas E concluídas
            response = await fetch('/api/ordens-servico?status=abertas,concluida');
            if (response.ok) {
                data = await response.json();
                console.log('✅ API original funcionou');
            } else {
                throw new Error('API original falhou');
            }
        } catch (error) {
            console.warn('⚠️ API original falhou, tentando alternativa...');
            
            // Usar API alternativa - incluir OS abertas E concluídas
            response = await fetch('/api/ordens-servico-programacao?status=abertas,concluida');
            if (response.ok) {
                data = await response.json();
                console.log('✅ API alternativa funcionou');
            } else {
                throw new Error('Ambas APIs falharam');
            }
        }
        
        ordensServico = data.ordens_servico || [];
        console.log(`📊 Total de OS carregadas: ${ordensServico.length}`);
        
        // Verificar duplicação inicial
        const osIdsIniciais = ordensServico.map(os => os.id);
        const duplicadasIniciais = osIdsIniciais.filter((id, index) => osIdsIniciais.indexOf(id) !== index);
        if (duplicadasIniciais.length > 0) {
            console.warn(`⚠️ DUPLICAÇÃO INICIAL DETECTADA:`, duplicadasIniciais);
            ordensServico = ordensServico.filter((os, index, arr) => 
                arr.findIndex(o => o.id === os.id) === index
            );
            console.log(`✅ ${duplicadasIniciais.length} OS duplicadas removidas do carregamento inicial`);
        }
        
        // Debug: mostrar OS de PMP
        const osPMP = ordensServico.filter(os => os.pmp_id && os.pmp_id !== null);
        console.log(`🔧 OS de PMP encontradas: ${osPMP.length}`);
        
        if (osPMP.length > 0) {
            console.log('📋 OS de PMP:', osPMP.map(os => ({
                id: os.id,
                descricao: os.descricao.substring(0, 30) + '...',
                status: os.status,
                prioridade: os.prioridade,
                pmp_id: os.pmp_id
            })));
        }
        
        // Carregar também OS programadas e concluídas (evitando duplicação)
        try {
            let responseProgramadas;
            try {
                responseProgramadas = await fetch('/api/ordens-servico?status=programada,concluida');
            } catch {
                responseProgramadas = await fetch('/api/ordens-servico-programacao?status=programada,concluida');
            }
            
            if (responseProgramadas.ok) {
                const dataProgramadas = await responseProgramadas.json();
                const osProgramadas = dataProgramadas.ordens_servico || [];
                
                // Filtrar OS que já não estão na lista (evitar duplicação)
                const osExistentesIds = new Set(ordensServico.map(os => os.id));
                const osNovas = osProgramadas.filter(os => !osExistentesIds.has(os.id));
                
                // Adicionar apenas OS novas à lista
                ordensServico = [...ordensServico, ...osNovas];
                console.log(`📊 OS programadas adicionadas: ${osNovas.length} (${osProgramadas.length - osNovas.length} duplicadas removidas)`);
                console.log(`📊 Total final: ${ordensServico.length}`);
            }
        } catch (error) {
            console.warn('⚠️ Erro ao carregar OS programadas:', error);
        }
        
    } catch (error) {
        console.error('❌ Erro ao carregar OS:', error);
        ordensServico = [];
        
        // Mostrar notificação de erro para o usuário
        showNotification('Erro ao carregar ordens de serviço. Recarregue a página.', 'error');
    }
}

// Carregar usuários (apenas perfil 'user')
async function loadUsuarios() {
    try {
        const response = await fetch('/api/users?profile=user');
        if (response.ok) {
            const data = await response.json();
            usuarios = data.users || [];
            console.log('Usuários carregados:', usuarios.length);
        } else {
            // Fallback: criar usuários de exemplo se API não estiver disponível
            usuarios = [
                { id: 1, name: 'João Silva', profile: 'user', cargo: 'Técnico' },
                { id: 2, name: 'Maria Santos', profile: 'user', cargo: 'Operador' },
                { id: 3, name: 'Pedro Costa', profile: 'user', cargo: 'Mecânico' }
            ];
        }
    } catch (error) {
        console.error('Erro ao carregar usuários:', error);
        // Fallback: usuários de exemplo
        usuarios = [
            { id: 1, name: 'João Silva', profile: 'user', cargo: 'Técnico' },
            { id: 2, name: 'Maria Santos', profile: 'user', cargo: 'Operador' },
            { id: 3, name: 'Pedro Costa', profile: 'user', cargo: 'Mecânico' }
        ];
    }
}

// Renderizar linhas de prioridade
function renderPriorityLines() {
    const prioridades = ['baixa', 'media', 'alta', 'seguranca', 'preventiva'];
    
    console.log('🎨 Renderizando linhas de prioridade...');
    
    prioridades.forEach(prioridade => {
        const container = document.getElementById(`chamados-${prioridade}`);
        if (!container) {
            console.warn(`⚠️ Container não encontrado: chamados-${prioridade}`);
            return;
        }
        
        let osFiltered;
        if ((os.prioridade === 'preventiva' || os.pmp_id || (os.descricao && os.descricao.toLowerCase().includes('pmp')))) {
            // CORREÇÃO: Lógica melhorada para preventivas
            osFiltered = ordensServico.filter(os => {
                // Condição 1: Prioridade preventiva normal
                const condicao1 = os.(os.prioridade === 'preventiva' || os.pmp_id || (os.descricao && os.descricao.toLowerCase().includes('pmp'))) && 
                                 os.status === 'aberta' &&
                                 (!os.usuario_responsavel || os.usuario_responsavel === null || os.usuario_responsavel === '');
                
                // Condição 2: Qualquer OS de PMP aberta (independente da prioridade)
                const condicao2 = os.pmp_id && os.pmp_id !== null && os.status === 'aberta';
                
                return condicao1 || condicao2;
            });
            
            console.log(`🔧 Preventivas filtradas: ${osFiltered.length}`);
            if (osFiltered.length > 0) {
                console.log('📋 IDs das preventivas:', osFiltered.map(os => os.id));
            }
        } else {
            // Para outras prioridades: excluir OS de PMP
            osFiltered = ordensServico.filter(os => 
                os.prioridade === prioridade && 
                os.status === 'aberta' &&
                (!os.pmp_id || os.pmp_id === null)
            );
        }
        
        if (osFiltered.length === 0) {
            container.innerHTML = '<div class="empty-priority">Nenhuma OS nesta prioridade</div>';
            return;
        }
        
        // Renderizar cards
        container.innerHTML = osFiltered.map(os => createOSCard(os)).join('');
        
        // Adicionar funcionalidade de drag
        osFiltered.forEach(os => {
            const element = container.querySelector(`[data-os-id="${os.id}"]`);
            if (element) {
                addDragListeners(element);
            }
        });
        
        console.log(`✅ ${prioridade}: ${osFiltered.length} OS renderizadas`);
    });
}

// Criar card de OS
function createOSCard(os) {
    // Verificar se é OS de PMP
    const isPMP = os.pmp_id && os.pmp_id !== null;
    const pmpBadge = isPMP ? `<div class="pmp-badge">PMP</div>` : '';
    const frequenciaBadge = isPMP && os.frequencia_origem ? 
        `<div class="frequencia-badge">${os.frequencia_origem}</div>` : '';
    
    return `
        <div class="chamado-card ${isPMP ? 'pmp-card' : ''}" data-os-id="${os.id}" draggable="true" onclick="verificarExecucaoOS(${os.id})">
            <div class="chamado-header">
                <div class="chamado-id">OS #${os.id}</div>
                <div class="badges">
                    ${pmpBadge}
                    ${frequenciaBadge}
                </div>
            </div>
            <div class="chamado-descricao">${os.descricao}</div>
            <div class="chamado-info">
                <div class="info-line">
                    <i class="fas fa-tools"></i>
                    ${formatTipoManutencao(os.tipo_manutencao)}
                </div>
                <div class="info-line">
                    <i class="fas fa-industry"></i>
                    ${formatOficina(os.oficina)}
                </div>
                <div class="info-line">
                    <i class="fas fa-clock"></i>
                    ${os.hh}h (${os.qtd_pessoas}p × ${os.horas}h)
                </div>
                <div class="info-line">
                    <i class="fas fa-building"></i>
                    ${os.filial_tag} - ${os.setor_tag} - ${os.equipamento_tag}
                </div>
                ${isPMP ? `
                <div class="info-line pmp-info">
                    <i class="fas fa-calendar-alt"></i>
                    Próxima: ${formatDate(os.data_proxima_geracao)} | Seq: #${os.numero_sequencia || 1}
                </div>
                ` : ''}
            </div>
        </div>
    `;
}

// Função auxiliar para formatar data
function formatDate(dateString) {
    if (!dateString) return 'N/A';
    
    try {
        // Verificar se a data é válida
        const date = new Date(dateString);
        if (isNaN(date.getTime())) {
            console.error(`❌ Data inválida: ${dateString}`);
            return 'Data inválida';
        }
        
        // Formatar data no padrão brasileiro
        const dia = String(date.getDate()).padStart(2, '0');
        const mes = String(date.getMonth() + 1).padStart(2, '0');
        const ano = date.getFullYear();
        
        return `${dia}/${mes}/${ano}`;
    } catch (error) {
        console.error(`❌ Erro ao formatar data: ${dateString}`, error);
        return 'Erro na data';
    }
}

// Renderizar usuários e calendário
function renderUsuarios() {
    const container = document.getElementById('usuarios-grid');
    
    if (usuarios.length === 0) {
        container.innerHTML = '<div class="loading">Nenhum usuário encontrado</div>';
        return;
    }
    
    container.innerHTML = usuarios.map(usuario => createUsuarioRow(usuario)).join('');
    
    // Adicionar event listeners para drop zones
    addDropZoneListeners();
}

// Criar linha de usuário com calendário
function createUsuarioRow(usuario) {
    const diasSemana = getDaysOfWeek(currentWeek, currentYear);
    
    return `
        <div class="usuario-row" data-user-name="${usuario.name}">
            <div class="usuario-info">
                <div class="usuario-avatar">
                    ${getInitials(usuario.name)}
                </div>
                <div class="usuario-nome">${usuario.name}</div>
                <div class="usuario-cargo">${usuario.cargo || 'Usuário'}</div>
            </div>
            
            <div class="dias-semana">
                ${diasSemana.map((dia, index) => createDiaContainer(dia, index, usuario.id, usuario.name)).join('')}
            </div>
        </div>
    `;
}

// Criar container de dia
function createDiaContainer(dia, dayIndex, userId, userName) {
    const diasNomes = ['SEG', 'TER', 'QUA', 'QUI', 'SEX', 'SAB', 'DOM'];
    const osAgendadas = getOSAgendadas(dia.date, userId);
    const workloadClass = getWorkloadClass(osAgendadas);
    
    return `
        <div class="dia-container ${workloadClass}" 
             data-date="${dia.date}" 
             data-user-id="${userId}"
             data-user-name="${userName}"
             data-day-index="${dayIndex}">
            <div class="dia-header">
                <div class="dia-nome">${diasNomes[dayIndex]}</div>
                <div class="dia-data">${dia.day}</div>
            </div>
            <div class="dia-chamados">
                ${osAgendadas.map(os => createOSAgendada(os)).join('')}
            </div>
            <div class="workload-indicator ${getWorkloadIndicator(osAgendadas)}"></div>
        </div>
    `;
}

// Criar OS agendada
function createOSAgendada(os) {
    // Determinar classe CSS baseada no status
    let statusClass = '';
    let statusIcon = '';
    
    if (os.status === 'concluida') {
        statusClass = 'os-concluida';
        statusIcon = '<i class="fas fa-check-circle status-icon"></i>';
    } else if (os.status === 'em_execucao') {
        statusClass = 'os-em-execucao';
        statusIcon = '<i class="fas fa-play-circle status-icon"></i>';
    } else {
        statusClass = 'os-pendente';
        statusIcon = '<i class="fas fa-clock status-icon"></i>';
    }
    
    return `
        <div class="chamado-agendado ${statusClass}" data-os-id="${os.id}" onclick="verificarExecucaoOS(${os.id})" oncontextmenu="event.preventDefault(); handleOSContextMenu(event, ${os.id})">
            <div class="chamado-header-mini">
                <div class="chamado-id">OS #${os.id}</div>
                ${statusIcon}
            </div>
            <div class="chamado-descricao-mini">${os.descricao.substring(0, 30)}...</div>
        </div>
    `;
}

// Handler para menu de contexto de OS (chamado diretamente do HTML)
function handleOSContextMenu(event, osId) {
    // Criar menu de contexto
    const contextMenu = document.createElement('div');
    contextMenu.className = 'context-menu';
    contextMenu.innerHTML = `
        <div class="context-menu-item" onclick="desprogramarOS(${osId}); document.body.removeChild(this.parentNode);">
            <i class="fas fa-times-circle"></i> Desprogramar OS
        </div>
    `;
    
    // Posicionar menu
    contextMenu.style.position = 'absolute';
    contextMenu.style.left = `${event.pageX}px`;
    contextMenu.style.top = `${event.pageY}px`;
    contextMenu.style.zIndex = '9999';
    contextMenu.style.background = 'white';
    contextMenu.style.boxShadow = '0 2px 10px rgba(0,0,0,0.2)';
    contextMenu.style.borderRadius = '4px';
    contextMenu.style.padding = '5px 0';
    
    // Estilizar item do menu
    const menuItems = contextMenu.querySelectorAll('.context-menu-item');
    menuItems.forEach(item => {
        item.style.padding = '8px 15px';
        item.style.cursor = 'pointer';
        item.style.fontSize = '14px';
        item.style.display = 'flex';
        item.style.alignItems = 'center';
        item.style.gap = '8px';
        
        // Hover
        item.addEventListener('mouseenter', () => {
            item.style.background = '#f0e6f5';
        });
        
        item.addEventListener('mouseleave', () => {
            item.style.background = 'transparent';
        });
    });
    
    // Adicionar ao body
    document.body.appendChild(contextMenu);
    
    // Remover menu ao clicar fora
    document.addEventListener('click', function removeMenu() {
        if (document.body.contains(contextMenu)) {
            document.body.removeChild(contextMenu);
        }
        document.removeEventListener('click', removeMenu);
    });
}

// Verificar se usuário pode executar OS - VERSÃO SIMPLIFICADA
async function verificarExecucaoOS(osId) {
    try {
        console.log('Clicou na OS:', osId);
        
        // Simplificar: sempre permitir acesso ao formulário
        // A verificação de permissões será feita na página de execução
        console.log('Redirecionando para formulário de execução');
        window.location.href = `/executar-os?id=${osId}`;
        
    } catch (error) {
        console.error('Erro ao abrir execução de OS:', error);
        showNotification('Erro ao abrir formulário de execução', 'error');
    }
}

// Obter OS agendadas para uma data e usuário
function getOSAgendadas(date, userId) {
    const usuario = getUserById(userId);
    if (!usuario) return [];
    
    // Usar Set para evitar duplicações
    const osEncontradas = new Set();
    const osAgendadas = [];
    const duplicadasDetectadas = [];
    
    ordensServico.forEach(os => {
        // Verificar se a OS está programada para esta data
        const dataMatch = os.data_programada === date;
        
        // Verificar se o usuário é responsável pela OS (simplificado)
        const usuarioMatch = os.usuario_responsavel === usuario.name || 
                           os.usuario_responsavel === usuario.id;
        
        if (dataMatch && usuarioMatch) {
            // Detectar duplicação
            if (osEncontradas.has(os.id)) {
                duplicadasDetectadas.push(os.id);
                console.warn(`🔄 DUPLICAÇÃO DETECTADA: OS #${os.id} para ${usuario.name} em ${date}`);
            } else {
                osEncontradas.add(os.id);
                osAgendadas.push(os);
            }
        }
    });
    
    // Log de debug se houver duplicações
    if (duplicadasDetectadas.length > 0) {
        console.error(`❌ ${duplicadasDetectadas.length} OS duplicadas removidas para ${usuario.name} em ${date}:`, duplicadasDetectadas);
    }
    
    return osAgendadas;
}

// Obter usuário por ID
function getUserById(userId) {
    // Converter para número se for string
    const id = typeof userId === 'string' ? parseInt(userId, 10) : userId;
    
    // Verificar se é um número válido
    if (isNaN(id)) {
        console.error(`❌ ID de usuário inválido: ${userId}`);
        return null;
    }
    
    // Procurar usuário pelo ID
    const usuario = usuarios.find(u => u.id === id);
    
    // Log para debug
    if (!usuario) {
        console.warn(`⚠️ Usuário não encontrado para ID: ${id}`);
        console.log('📋 Usuários disponíveis:', usuarios.map(u => ({ id: u.id, name: u.name })));
    }
    
    return usuario;
}

// Obter classe de workload
function getWorkloadClass(osAgendadas) {
    const totalHH = osAgendadas.reduce((sum, os) => sum + (os.hh || 0), 0);
    
    if (totalHH === 0) return 'workload-empty';
    if (totalHH <= 4) return 'workload-light';
    if (totalHH <= 8) return 'workload-medium';
    return 'workload-heavy';
}

// Obter indicador de workload
function getWorkloadIndicator(osAgendadas) {
    const totalHH = osAgendadas.reduce((sum, os) => sum + (os.hh || 0), 0);
    
    if (totalHH === 0) return 'indicator-empty';
    if (totalHH <= 4) return 'indicator-light';
    if (totalHH <= 8) return 'indicator-medium';
    return 'indicator-heavy';
}

// Obter iniciais do nome
function getInitials(name) {
    return name.split(' ')
        .map(word => word.charAt(0))
        .join('')
        .substring(0, 2)
        .toUpperCase();
}

// Obter semana atual
function getCurrentWeek() {
    const today = new Date();
    const dayOfWeek = today.getDay();
    const diff = today.getDate() - dayOfWeek + (dayOfWeek === 0 ? -6 : 1);
    const monday = new Date(today.setDate(diff));
    
    const weekNumber = getWeekNumber(monday);
    return weekNumber;
}

// Obter número da semana
function getWeekNumber(date) {
    const d = new Date(Date.UTC(date.getFullYear(), date.getMonth(), date.getDate()));
    const dayNum = d.getUTCDay() || 7;
    d.setUTCDate(d.getUTCDate() + 4 - dayNum);
    const yearStart = new Date(Date.UTC(d.getUTCFullYear(), 0, 1));
    return Math.ceil((((d - yearStart) / 86400000) + 1) / 7);
}

// Obter dias da semana
function getDaysOfWeek(weekNumber, year) {
    const jan1 = new Date(year, 0, 1);
    const days = (weekNumber - 1) * 7;
    const monday = new Date(jan1.getTime() + days * 24 * 60 * 60 * 1000);
    
    // Ajustar para segunda-feira
    const dayOfWeek = monday.getDay();
    const diff = monday.getDate() - dayOfWeek + (dayOfWeek === 0 ? -6 : 1);
    monday.setDate(diff);
    
    const weekDays = [];
    for (let i = 0; i < 7; i++) {
        const day = new Date(monday);
        day.setDate(monday.getDate() + i);
        weekDays.push({
            date: day.toISOString().split('T')[0],
            day: day.getDate(),
            month: day.getMonth() + 1
        });
    }
    
    return weekDays;
}

// Atualizar display da semana
function updateWeekDisplay() {
    const weekDays = getDaysOfWeek(currentWeek, currentYear);
    const firstDay = weekDays[0];
    const lastDay = weekDays[6];
    
    // Formatar datas para exibição
    const firstDayFormatted = `${String(firstDay.day).padStart(2, '0')}/${String(firstDay.month).padStart(2, '0')}`;
    const lastDayFormatted = `${String(lastDay.day).padStart(2, '0')}/${String(lastDay.month).padStart(2, '0')}`;
    
    // Obter nomes dos meses
    const meses = ['Janeiro', 'Fevereiro', 'Março', 'Abril', 'Maio', 'Junho', 
                  'Julho', 'Agosto', 'Setembro', 'Outubro', 'Novembro', 'Dezembro'];
    
    const firstDayDate = new Date(currentYear, firstDay.month - 1, firstDay.day);
    const lastDayDate = new Date(currentYear, lastDay.month - 1, lastDay.day);
    
    const firstMonthName = meses[firstDayDate.getMonth()];
    const lastMonthName = meses[lastDayDate.getMonth()];
    
    // Criar texto detalhado
    let displayText = `Semana ${currentWeek} | Ano ${currentYear}`;
    displayText += `<div class="week-dates">${firstDayFormatted} ${firstMonthName} - ${lastDayFormatted} ${lastMonthName}</div>`;
    
    const weekDisplay = document.getElementById('current-week');
    if (weekDisplay) {
        weekDisplay.innerHTML = displayText;
    }
    
    console.log(`📅 Semana atualizada: ${currentWeek}/${currentYear} (${firstDayFormatted} a ${lastDayFormatted})`);
}

// Navegação de semanas
function previousWeek() {
    if (currentWeek > 1) {
        currentWeek--;
    } else {
        currentWeek = 52;
        currentYear--;
    }
    
    // Atualizar display e renderizar
    updateWeekDisplay();
    renderUsuarios();
    
    // Feedback visual
    const weekNav = document.querySelector('.week-navigation');
    weekNav.classList.add('week-changed');
    setTimeout(() => {
        weekNav.classList.remove('week-changed');
    }, 500);
    
    // Notificação
    showNotification(`Semana ${currentWeek} de ${currentYear}`, 'info');
}

function nextWeek() {
    if (currentWeek < 52) {
        currentWeek++;
    } else {
        currentWeek = 1;
        currentYear++;
    }
    
    // Atualizar display e renderizar
    updateWeekDisplay();
    renderUsuarios();
    
    // Feedback visual
    const weekNav = document.querySelector('.week-navigation');
    weekNav.classList.add('week-changed');
    setTimeout(() => {
        weekNav.classList.remove('week-changed');
    }, 500);
    
    // Notificação
    showNotification(`Semana ${currentWeek} de ${currentYear}`, 'info');
}

// Adicionar listeners de drag
function addDragListeners(element) {
    element.addEventListener('dragstart', handleDragStart);
    element.addEventListener('dragend', handleDragEnd);
}

// Adicionar event listeners para drop zones
function addDropZoneListeners() {
    const dropZones = document.querySelectorAll('.dia-container');
    
    dropZones.forEach(zone => {
        zone.addEventListener('dragover', handleDragOver);
        zone.addEventListener('drop', handleDrop);
        zone.addEventListener('dragenter', handleDragEnter);
        zone.addEventListener('dragleave', handleDragLeave);
    });
    
    // Adicionar listeners para OS já agendadas
    document.querySelectorAll('.chamado-agendado').forEach(os => {
        os.addEventListener('contextmenu', handleContextMenu);
    });
}

// Handler para menu de contexto (clique direito)
function handleContextMenu(e) {
    e.preventDefault();
    
    const osId = this.getAttribute('data-os-id');
    if (!osId) return;
    
    // Criar menu de contexto
    const contextMenu = document.createElement('div');
    contextMenu.className = 'context-menu';
    contextMenu.innerHTML = `
        <div class="context-menu-item" data-action="desprogramar" data-os-id="${osId}">
            <i class="fas fa-times-circle"></i> Desprogramar OS
        </div>
    `;
    
    // Posicionar menu
    contextMenu.style.position = 'absolute';
    contextMenu.style.left = `${e.pageX}px`;
    contextMenu.style.top = `${e.pageY}px`;
    contextMenu.style.zIndex = '9999';
    contextMenu.style.background = 'white';
    contextMenu.style.boxShadow = '0 2px 10px rgba(0,0,0,0.2)';
    contextMenu.style.borderRadius = '4px';
    contextMenu.style.padding = '5px 0';
    
    // Estilizar item do menu
    const menuItems = contextMenu.querySelectorAll('.context-menu-item');
    menuItems.forEach(item => {
        item.style.padding = '8px 15px';
        item.style.cursor = 'pointer';
        item.style.fontSize = '14px';
        item.style.display = 'flex';
        item.style.alignItems = 'center';
        item.style.gap = '8px';
        
        // Hover
        item.addEventListener('mouseenter', () => {
            item.style.background = '#f0e6f5';
        });
        
        item.addEventListener('mouseleave', () => {
            item.style.background = 'transparent';
        });
        
        // Click
        item.addEventListener('click', () => {
            const action = item.getAttribute('data-action');
            const osId = item.getAttribute('data-os-id');
            
            if (action === 'desprogramar') {
                desprogramarOS(osId);
            }
            
            // Remover menu
            document.body.removeChild(contextMenu);
        });
    });
    
    // Adicionar ao body
    document.body.appendChild(contextMenu);
    
    // Remover menu ao clicar fora
    document.addEventListener('click', function removeMenu() {
        if (document.body.contains(contextMenu)) {
            document.body.removeChild(contextMenu);
        }
        document.removeEventListener('click', removeMenu);
    });
}

// Desprogramar OS
async function desprogramarOS(osId) {
    try {
        console.log(`🔄 Desprogramando OS #${osId}`);
        
        // Preparar dados para API
        const data = {
            id: parseInt(osId),
            data_programada: null,
            usuario_responsavel: null,
            status: 'aberta'
        };
        
        // Enviar para API
        const response = await fetch(`/api/ordens-servico/${osId}/desprogramar`, {
            method: 'PUT',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(data)
        });
        
        if (response.ok) {
            console.log('✅ OS desprogramada com sucesso');
            
            // Atualizar OS na lista local
            const osIndex = ordensServico.findIndex(os => os.id == osId);
            if (osIndex !== -1) {
                ordensServico[osIndex].data_programada = null;
                ordensServico[osIndex].usuario_responsavel = null;
                ordensServico[osIndex].status = 'aberta';
            }
            
            // Renderizar novamente
            renderPriorityLines();
            renderUsuarios();
            
            // Notificação
            showNotification(`OS #${osId} desprogramada com sucesso`, 'success');
        } else {
            console.error('❌ Erro ao desprogramar OS');
            
            // Tentar alternativa
            await desprogramarOSAlternativa(osId);
        }
    } catch (error) {
        console.error('Erro ao desprogramar OS:', error);
        
        // Tentar alternativa
        await desprogramarOSAlternativa(osId);
    }
}

// Método alternativo para desprogramar OS
async function desprogramarOSAlternativa(osId) {
    try {
        console.log(`🔄 Tentando desprogramar OS #${osId} (método alternativo)`);
        
        // Atualizar OS na lista local
        const osIndex = ordensServico.findIndex(os => os.id == osId);
        if (osIndex !== -1) {
            ordensServico[osIndex].data_programada = null;
            ordensServico[osIndex].usuario_responsavel = null;
            ordensServico[osIndex].status = 'aberta';
            
            console.log('✅ OS desprogramada localmente');
            
            // Renderizar novamente
            renderPriorityLines();
            renderUsuarios();
            
            // Notificação
            showNotification(`OS #${osId} desprogramada com sucesso`, 'success');
        } else {
            console.error('❌ OS não encontrada na lista local');
            showNotification('Erro ao desprogramar OS. Tente recarregar a página.', 'error');
        }
    } catch (error) {
        console.error('Erro ao desprogramar OS (método alternativo):', error);
        showNotification('Erro ao desprogramar OS. Tente recarregar a página.', 'error');
    }
}

// Handlers de drag and drop
let draggedElement = null;

function handleDragStart(e) {
    draggedElement = this;
    this.style.opacity = '0.5';
    e.dataTransfer.effectAllowed = 'move';
    e.dataTransfer.setData('text/plain', this.getAttribute('data-os-id'));
    this.classList.add('dragging');
}

function handleDragEnd(e) {
    this.style.opacity = '1';
    this.classList.remove('dragging');
    
    // Remover classes de hover de todas as drop zones
    document.querySelectorAll('.dia-container').forEach(zone => {
        zone.classList.remove('drag-over');
    });
}

function handleDragOver(e) {
    if (e.preventDefault) {
        e.preventDefault();
    }
    e.dataTransfer.dropEffect = 'move';
    return false;
}

function handleDragEnter(e) {
    this.classList.add('drag-over');
}

function handleDragLeave(e) {
    this.classList.remove('drag-over');
}

function handleDrop(e) {
    e.stopPropagation();
    e.preventDefault();
    
    // Remover classe de hover
    this.classList.remove('drag-over');
    
    if (!draggedElement) return;
    
    const osId = e.dataTransfer.getData('text/plain');
    const dateStr = this.getAttribute('data-date');
    const userId = this.getAttribute('data-user-id');
    const userName = this.getAttribute('data-user-name');
    
    // Garantir que a data está no formato correto (YYYY-MM-DD)
    let formattedDate = dateStr;
    
    // Verificar se a data está no formato correto
    if (dateStr && !dateStr.match(/^\d{4}-\d{2}-\d{2}$/)) {
        console.warn(`⚠️ Formato de data incorreto: ${dateStr}, tentando converter...`);
        
        try {
            const dateParts = dateStr.split('/');
            if (dateParts.length === 3) {
                // Converter de DD/MM/YYYY para YYYY-MM-DD
                formattedDate = `${dateParts[2]}-${dateParts[1]}-${dateParts[0]}`;
            } else {
                // Tentar criar um objeto Date e formatar
                const date = new Date(dateStr);
                if (!isNaN(date.getTime())) {
                    const year = date.getFullYear();
                    const month = String(date.getMonth() + 1).padStart(2, '0');
                    const day = String(date.getDate()).padStart(2, '0');
                    formattedDate = `${year}-${month}-${day}`;
                }
            }
        } catch (error) {
            console.error(`❌ Erro ao converter data: ${dateStr}`, error);
        }
    }
    
    console.log(`🔄 Drop detectado: OS #${osId} para ${formattedDate} com usuário ID ${userId}, nome: ${userName}`);
    
    // Programar OS para esta data e usuário
    if (userName) {
        // Se temos o nome do usuário diretamente, usar
        programarOSComNomeUsuario(osId, formattedDate, userName);
    } else {
        // Caso contrário, usar o método que busca o nome
        programarOS(osId, formattedDate, userId);
    }
    
    return false;
}

// Programar OS para uma data e usuário
async function programarOS(osId, date, userId) {
    try {
        console.log(`🔄 Tentando programar OS #${osId} para ${date} com usuário ID ${userId}`);
        
        // Verificar se temos o ID da OS
        if (!osId) {
            console.error('❌ ID da OS não fornecido');
            showNotification('Erro: ID da OS não fornecido', 'error');
            return;
        }
        
        // Verificar se temos a data
        if (!date) {
            console.error('❌ Data não fornecida');
            showNotification('Erro: Data não fornecida', 'error');
            return;
        }
        
        // Verificar se temos o ID do usuário
        if (!userId) {
            console.error('❌ ID do usuário não fornecido');
            showNotification('Erro: ID do usuário não fornecido', 'error');
            return;
        }
        
        // SOLUÇÃO DEFINITIVA: Usar nome do usuário diretamente do DOM
        const userElement = document.querySelector(`[data-user-id="${userId}"]`);
        let userName = null;
        
        if (userElement) {
            const userNameElement = userElement.closest('.usuario-row').querySelector('.usuario-nome');
            if (userNameElement) {
                userName = userNameElement.textContent.trim();
                console.log(`✅ Nome do usuário obtido do DOM: ${userName}`);
            }
        }
        
        // Se não conseguiu obter do DOM, tentar pelo ID
        if (!userName) {
            const usuario = getUserById(userId);
            if (usuario && usuario.name) {
                userName = usuario.name;
                console.log(`✅ Nome do usuário obtido do objeto: ${userName}`);
            }
        }
        
        // Se ainda não temos o nome, usar um valor padrão
        if (!userName) {
            userName = `Técnico #${userId}`;
            console.warn(`⚠️ Nome do usuário não encontrado, usando valor padrão: ${userName}`);
        }
        
        // Continuar com o nome do usuário
        programarOSComNomeUsuario(osId, date, userName);
    } catch (error) {
        console.error('Erro ao programar OS:', error);
        showNotification('Erro ao programar OS. Tente novamente.', 'error');
    }
}

// Função auxiliar para programar OS com nome do usuário
async function programarOSComNomeUsuario(osId, date, userName) {
    try {
        console.log(`🔄 Programando OS #${osId} para ${date} com usuário ${userName}`);
        
        // Preparar dados para API
        const data = {
            id: parseInt(osId),
            data_programada: date,
            usuario_responsavel: userName,
            status: 'programada'
        };
        
        // Enviar para API
        const response = await fetch(`/api/ordens-servico/${osId}/programar`, {
            method: 'PUT',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(data)
        });
        
        if (response.ok) {
            console.log('✅ OS programada com sucesso');
            
            // Atualizar OS na lista local (evitando duplicação)
            const osIndex = ordensServico.findIndex(os => os.id == osId);
            if (osIndex !== -1) {
                ordensServico[osIndex].data_programada = date;
                ordensServico[osIndex].usuario_responsavel = userName;
                ordensServico[osIndex].status = 'programada';
                console.log(`✅ OS #${osId} atualizada na lista local`);
            } else {
                console.warn(`⚠️ OS #${osId} não encontrada na lista local para atualização`);
            }
            
            // Verificar se não há duplicação na lista
            const osIds = ordensServico.map(os => os.id);
            const duplicadas = osIds.filter((id, index) => osIds.indexOf(id) !== index);
            if (duplicadas.length > 0) {
                console.error(`❌ DUPLICAÇÃO DETECTADA na lista após programação:`, duplicadas);
                // Remover duplicadas
                ordensServico = ordensServico.filter((os, index, arr) => 
                    arr.findIndex(o => o.id === os.id) === index
                );
                console.log(`✅ ${duplicadas.length} OS duplicadas removidas da lista`);
            }
            
            // Renderizar novamente
            renderPriorityLines();
            renderUsuarios();
            
            // Notificação
            showNotification(`OS #${osId} programada para ${formatDate(date)}`, 'success');
        } else {
            console.error('❌ Erro ao programar OS');
            
            // Tentar alternativa
            programarOSAlternativa(osId, date, userName);
        }
    } catch (error) {
        console.error('Erro ao programar OS:', error);
        
        // Tentar alternativa
        programarOSAlternativa(osId, date, userName);
    }
}

// Método alternativo para programar OS
async function programarOSAlternativa(osId, date, userName) {
    try {
        console.log(`🔄 Tentando programar OS #${osId} (método alternativo)`);
        
        // Atualizar OS na lista local
        const osIndex = ordensServico.findIndex(os => os.id == osId);
        if (osIndex !== -1) {
            ordensServico[osIndex].data_programada = date;
            ordensServico[osIndex].usuario_responsavel = userName;
            ordensServico[osIndex].status = 'programada';
            
            console.log('✅ OS programada localmente');
            
            // Renderizar novamente
            renderPriorityLines();
            renderUsuarios();
            
            // Notificação
            showNotification(`OS #${osId} programada para ${formatDate(date)}`, 'success');
        } else {
            console.error('❌ OS não encontrada na lista local');
            showNotification('Erro ao programar OS. Tente recarregar a página.', 'error');
        }
    } catch (error) {
        console.error('Erro ao programar OS (método alternativo):', error);
        showNotification('Erro ao programar OS. Tente recarregar a página.', 'error');
    }
}

// Formatadores
function formatTipoManutencao(tipo) {
    const tipos = {
        'corretiva': 'Corretiva',
        'preventiva': 'Preventiva',
        'preditiva': 'Preditiva',
        'melhoria': 'Melhoria'
    };
    return tipos[tipo] || tipo;
}

function formatOficina(oficina) {
    return oficina || 'Não definida';
}

// Função para mostrar notificações
function showNotification(message, type = 'info') {
    // Verificar se já existe um container de notificações
    let notificationContainer = document.getElementById('notification-container');
    
    if (!notificationContainer) {
        // Criar container se não existir
        notificationContainer = document.createElement('div');
        notificationContainer.id = 'notification-container';
        notificationContainer.style.position = 'fixed';
        notificationContainer.style.top = '20px';
        notificationContainer.style.right = '20px';
        notificationContainer.style.zIndex = '9999';
        document.body.appendChild(notificationContainer);
    }
    
    // Criar notificação
    const notification = document.createElement('div');
    notification.className = `notification ${type}`;
    notification.innerHTML = `
        <div class="notification-icon">
            <i class="fas ${getIconForType(type)}"></i>
        </div>
        <div class="notification-content">
            ${message}
        </div>
        <button class="notification-close">
            <i class="fas fa-times"></i>
        </button>
    `;
    
    // Estilizar notificação
    notification.style.display = 'flex';
    notification.style.alignItems = 'center';
    notification.style.padding = '12px 16px';
    notification.style.marginBottom = '10px';
    notification.style.borderRadius = '8px';
    notification.style.boxShadow = '0 4px 12px rgba(0,0,0,0.15)';
    notification.style.backgroundColor = getColorForType(type);
    notification.style.color = '#fff';
    notification.style.fontSize = '14px';
    notification.style.opacity = '0';
    notification.style.transform = 'translateX(50px)';
    notification.style.transition = 'all 0.3s ease';
    
    // Adicionar ao container
    notificationContainer.appendChild(notification);
    
    // Animar entrada
    setTimeout(() => {
        notification.style.opacity = '1';
        notification.style.transform = 'translateX(0)';
    }, 10);
    
    // Configurar botão de fechar
    const closeButton = notification.querySelector('.notification-close');
    closeButton.style.background = 'none';
    closeButton.style.border = 'none';
    closeButton.style.color = '#fff';
    closeButton.style.cursor = 'pointer';
    closeButton.style.marginLeft = '10px';
    
    closeButton.addEventListener('click', () => {
        closeNotification(notification);
    });
    
    // Auto-fechar após 5 segundos
    setTimeout(() => {
        closeNotification(notification);
    }, 5000);
}

// Função auxiliar para fechar notificação
function closeNotification(notification) {
    notification.style.opacity = '0';
    notification.style.transform = 'translateX(50px)';
    
    setTimeout(() => {
        notification.remove();
    }, 300);
}

// Funções auxiliares para notificações
function getIconForType(type) {
    switch (type) {
        case 'success': return 'fa-check-circle';
        case 'error': return 'fa-exclamation-circle';
        case 'warning': return 'fa-exclamation-triangle';
        case 'info':
        default: return 'fa-info-circle';
    }
}

function getColorForType(type) {
    switch (type) {
        case 'success': return '#28a745';
        case 'error': return '#dc3545';
        case 'warning': return '#ffc107';
        case 'info':
        default: return '#9956a8';
    }
}

// Adicionar estilos para notificações
function addNotificationStyles() {
    const style = document.createElement('style');
    style.textContent = `
        .notification {
            animation: fadeInRight 0.3s ease;
        }
        
        .notification-icon {
            margin-right: 12px;
            font-size: 18px;
        }
        
        .notification-content {
            flex: 1;
        }
        
        @keyframes fadeInRight {
            from {
                opacity: 0;
                transform: translateX(50px);
            }
            to {
                opacity: 1;
                transform: translateX(0);
            }
        }
    `;
    document.head.appendChild(style);
}

// Adicionar estilos para notificações quando o DOM estiver pronto
document.addEventListener('DOMContentLoaded', addNotificationStyles);



// Função para atualizar status de OS na programação
function atualizarStatusOSNaProgramacao(osId, novoStatus) {
    console.log(`🔄 Atualizando status da OS ${osId} para ${novoStatus}`);
    
    // Encontrar e atualizar a OS no array
    const osIndex = ordensServico.findIndex(os => os.id === osId);
    if (osIndex !== -1) {
        ordensServico[osIndex].status = novoStatus;
        console.log(`✅ Status da OS ${osId} atualizado no array`);
    }
    
    // Atualizar visualmente todos os elementos da OS na página
    const osElements = document.querySelectorAll(`[data-os-id="${osId}"]`);
    osElements.forEach(element => {
        // Remover classes de status antigas
        element.classList.remove('os-pendente', 'os-em-execucao', 'os-concluida');
        
        // Adicionar nova classe de status
        if (novoStatus === 'concluida') {
            element.classList.add('os-concluida');
            
            // Atualizar ícone se existir
            const statusIcon = element.querySelector('.status-icon');
            if (statusIcon) {
                statusIcon.className = 'fas fa-check-circle status-icon';
            }
            
            console.log(`✅ OS ${osId} marcada como concluída visualmente`);
        } else if (novoStatus === 'em_execucao') {
            element.classList.add('os-em-execucao');
            
            const statusIcon = element.querySelector('.status-icon');
            if (statusIcon) {
                statusIcon.className = 'fas fa-play-circle status-icon';
            }
        } else {
            element.classList.add('os-pendente');
            
            const statusIcon = element.querySelector('.status-icon');
            if (statusIcon) {
                statusIcon.className = 'fas fa-clock status-icon';
            }
        }
    });
}

// Função para escutar mudanças de status de OS (pode ser chamada de outras páginas)
window.atualizarStatusOSNaProgramacao = atualizarStatusOSNaProgramacao;

// Escutar eventos de storage para sincronizar entre abas
window.addEventListener('storage', function(e) {
    if (e.key === 'os_status_updated') {
        const data = JSON.parse(e.newValue);
        atualizarStatusOSNaProgramacao(data.osId, data.novoStatus);
        
        // Limpar o evento
        localStorage.removeItem('os_status_updated');
    }
});

// Função para notificar outras abas sobre mudança de status
function notificarMudancaStatusOS(osId, novoStatus) {
    localStorage.setItem('os_status_updated', JSON.stringify({
        osId: osId,
        novoStatus: novoStatus,
        timestamp: Date.now()
    }));
}

// Exportar função para uso em outras páginas
window.notificarMudancaStatusOS = notificarMudancaStatusOS;

// Verificação automática de OS pendentes de PMP
async function verificarOSPendentesPMP() {
    try {
        console.log('🔍 Verificando OS pendentes de PMP...');
        
        const response = await fetch('/api/pmp/verificar-pendencias-hoje');
        if (response.ok) {
            const data = await response.json();
            
            if (data.success && data.total_pendencias > 0) {
                console.log(`⚠️ ${data.total_pendencias} OS pendentes encontradas`);
                
                // Gerar OS pendentes automaticamente
                const gerarResponse = await fetch('/api/pmp/gerar-os-pendentes', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify({ limite: 20 })
                });
                
                if (gerarResponse.ok) {
                    const gerarData = await gerarResponse.json();
                    console.log(`✅ ${gerarData.os_geradas?.length || 0} OS geradas automaticamente`);
                    
                    // Recarregar a programação após gerar OS
                    if (gerarData.os_geradas?.length > 0) {
                        setTimeout(() => {
                            loadOrdensServico();
                        }, 2000);
                    }
                }
            } else {
                console.log('✅ Nenhuma OS pendente de PMP encontrada');
            }
        }
    } catch (error) {
        console.error('❌ Erro ao verificar OS pendentes:', error);
    }
}

// Executar verificação ao carregar a página
document.addEventListener('DOMContentLoaded', function() {
    // Aguardar 3 segundos após carregar para não interferir com outras operações
    setTimeout(verificarOSPendentesPMP, 3000);
    
    // Executar verificação a cada 30 minutos
    setInterval(verificarOSPendentesPMP, 30 * 60 * 1000);
});
