// Variáveis globais
let ordensServico = [];
let usuarios = [];
let currentWeek = getCurrentWeek();
let currentYear = new Date().getFullYear();
let draggedElement = null;

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
        
        // Configurar navegação de semanas
        document.getElementById('prev-week').addEventListener('click', function() {
            currentWeek--;
            updateWeekDisplay();
            renderUsuarios();
        });
        
        document.getElementById('next-week').addEventListener('click', function() {
            currentWeek++;
            updateWeekDisplay();
            renderUsuarios();
        });
        
        // Configurar botão de verificar pendências
        document.getElementById('btn-verificar-pendencias').addEventListener('click', function() {
            verificarPendencias();
        });
        
        // Configurar botão de gerar OS pendentes
        document.getElementById('btn-gerar-os-pendentes').addEventListener('click', function() {
            gerarOSPendentes();
        });
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
            // Tentar API original
            response = await fetch('/api/ordens-servico?status=abertas');
            if (response.ok) {
                data = await response.json();
                console.log('✅ API original funcionou');
            } else {
                throw new Error('API original falhou');
            }
        } catch (error) {
            console.warn('⚠️ API original falhou, tentando alternativa...');
            
            // Usar API alternativa
            response = await fetch('/api/ordens-servico-programacao?status=abertas');
            if (response.ok) {
                data = await response.json();
                console.log('✅ API alternativa funcionou');
            } else {
                throw new Error('Ambas APIs falharam');
            }
        }
        
        ordensServico = data.ordens_servico || [];
        console.log(`📊 Total de OS carregadas: ${ordensServico.length}`);
        
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
        
        // Carregar também OS programadas
        try {
            let responseProgramadas;
            try {
                responseProgramadas = await fetch('/api/ordens-servico?status=programada');
            } catch {
                responseProgramadas = await fetch('/api/ordens-servico-programacao?status=programada');
            }
            
            if (responseProgramadas.ok) {
                const dataProgramadas = await responseProgramadas.json();
                const osProgramadas = dataProgramadas.ordens_servico || [];
                
                // Adicionar OS programadas à lista
                ordensServico = [...ordensServico, ...osProgramadas];
                console.log(`📊 OS programadas adicionadas: ${osProgramadas.length}`);
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
        if (prioridade === 'preventiva') {
            // CORREÇÃO: Lógica melhorada para preventivas
            osFiltered = ordensServico.filter(os => {
                // Condição 1: Prioridade preventiva normal
                const condicao1 = os.prioridade === 'preventiva' && 
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
    return `
        <div class="chamado-agendado" data-os-id="${os.id}" onclick="verificarExecucaoOS(${os.id})" oncontextmenu="event.preventDefault(); handleOSContextMenu(event, ${os.id})">
            <div class="chamado-id">OS #${os.id}</div>
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
    
    return ordensServico.filter(os => {
        // Verificar se a OS está programada para esta data
        const dataMatch = os.data_programada === date;
        
        // Verificar se o usuário é responsável pela OS
        const usuarioMatch = os.usuario_responsavel === usuario.name || 
                           os.usuario_responsavel === usuario.id ||
                           (os.status === 'programada' && os.usuario_responsavel === usuario.name);
        
        return dataMatch && usuarioMatch;
    });
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

// Obter iniciais do nome
function getInitials(name) {
    if (!name) return '?';
    
    const parts = name.split(' ');
    if (parts.length === 1) return parts[0].charAt(0).toUpperCase();
    
    return (parts[0].charAt(0) + parts[parts.length - 1].charAt(0)).toUpperCase();
}

// Obter classe de carga de trabalho
function getWorkloadClass(osAgendadas) {
    const count = osAgendadas.length;
    
    if (count === 0) return 'workload-empty';
    if (count <= 2) return 'workload-light';
    if (count <= 4) return 'workload-medium';
    return 'workload-heavy';
}

// Obter indicador de carga de trabalho
function getWorkloadIndicator(osAgendadas) {
    const count = osAgendadas.length;
    
    if (count === 0) return 'indicator-empty';
    if (count <= 2) return 'indicator-light';
    if (count <= 4) return 'indicator-medium';
    return 'indicator-heavy';
}

// Obter dias da semana
function getDaysOfWeek(weekOffset, year) {
    const today = new Date();
    const currentDay = today.getDay(); // 0 = Domingo, 1 = Segunda, ..., 6 = Sábado
    
    // Calcular o início da semana (segunda-feira)
    const startOfWeek = new Date(today);
    startOfWeek.setDate(today.getDate() - currentDay + 1 + (weekOffset * 7));
    
    // Gerar os dias da semana
    const weekDays = [];
    for (let i = 0; i < 5; i++) { // Segunda a Sexta
        const day = new Date(startOfWeek);
        day.setDate(startOfWeek.getDate() + i);
        
        // Formatar a data como YYYY-MM-DD
        const date = day.toISOString().split('T')[0];
        
        weekDays.push({
            date: date,
            day: day.getDate(),
            month: day.getMonth() + 1,
            year: day.getFullYear()
        });
    }
    
    return weekDays;
}

// Obter semana atual
function getCurrentWeek() {
    return 0; // 0 = semana atual
}

// Atualizar exibição da semana
function updateWeekDisplay() {
    const weekElement = document.querySelector('.semana-navegacao');
    if (!weekElement) return;
    
    const today = new Date();
    const targetDate = new Date(today);
    
    // Ajustar para a semana desejada
    targetDate.setDate(today.getDate() + (currentWeek * 7));
    
    // Calcular o número da semana
    const startOfYear = new Date(targetDate.getFullYear(), 0, 1);
    const days = Math.floor((targetDate - startOfYear) / (24 * 60 * 60 * 1000));
    const weekNumber = Math.ceil((days + startOfYear.getDay() + 1) / 7);
    
    // Obter dias da semana para mostrar período
    const diasSemana = getDaysOfWeek(currentWeek, targetDate.getFullYear());
    const primeiroDia = diasSemana[0];
    const ultimoDia = diasSemana[diasSemana.length - 1];
    
    // Nomes dos meses
    const meses = [
        'Janeiro', 'Fevereiro', 'Março', 'Abril', 'Maio', 'Junho',
        'Julho', 'Agosto', 'Setembro', 'Outubro', 'Novembro', 'Dezembro'
    ];
    
    // Formatar período
    const periodoTexto = `${primeiroDia.day}/${primeiroDia.month} ${meses[primeiroDia.month-1]} - ${ultimoDia.day}/${ultimoDia.month} ${meses[ultimoDia.month-1]}`;
    
    // Atualizar texto
    weekElement.innerHTML = `Semana ${weekNumber} | Ano ${targetDate.getFullYear()}<br><span class="periodo-semana">${periodoTexto}</span>`;
    
    // Adicionar classe de animação
    weekElement.classList.add('week-changed');
    
    // Remover classe após animação
    setTimeout(() => {
        weekElement.classList.remove('week-changed');
    }, 1000);
}

// Adicionar listeners de drag para OS
function addDragListeners(element) {
    element.addEventListener('dragstart', handleDragStart);
    element.addEventListener('dragend', handleDragEnd);
}

// Adicionar listeners de drop para zonas de drop
function addDropZoneListeners() {
    document.querySelectorAll('.dia-container').forEach(zone => {
        zone.addEventListener('dragover', handleDragOver);
        zone.addEventListener('dragenter', handleDragEnter);
        zone.addEventListener('dragleave', handleDragLeave);
        zone.addEventListener('drop', handleDrop);
    });
}

// Handlers de drag and drop
function handleDragStart(e) {
    this.classList.add('dragging');
    e.dataTransfer.effectAllowed = 'move';
    e.dataTransfer.setData('text/plain', this.getAttribute('data-os-id'));
    
    // Armazenar elemento arrastado
    draggedElement = this;
    
    // Remover classes de hover
    document.querySelectorAll('.dia-container').forEach(zone => {
        zone.classList.remove('drag-over');
    });
}

function handleDragEnd(e) {
    this.classList.remove('dragging');
    draggedElement = null;
    
    // Remover classes de hover
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

// FUNÇÃO CORRIGIDA: handleDrop
function handleDrop(e) {
    e.stopPropagation();
    e.preventDefault();
    
    // Remover classe de hover
    this.classList.remove('drag-over');
    
    // Verificar se temos um elemento arrastado
    if (!draggedElement) {
        console.error('❌ Elemento arrastado não encontrado');
        return false;
    }
    
    // Obter ID da OS do elemento arrastado
    const osId = draggedElement.getAttribute('data-os-id');
    if (!osId) {
        console.error('❌ ID da OS não encontrado no elemento arrastado');
        return false;
    }
    
    // Obter data do elemento de destino
    const dateStr = this.getAttribute('data-date');
    if (!dateStr) {
        console.error('❌ Data não encontrada no elemento de destino');
        return false;
    }
    
    // Obter ID e nome do usuário do elemento de destino
    const userId = this.getAttribute('data-user-id');
    const userName = this.getAttribute('data-user-name');
    
    console.log(`🔄 Drop detectado: OS #${osId} para data ${dateStr} com usuário ID ${userId}, nome: ${userName}`);
    
    // Verificar se a data está no formato correto (YYYY-MM-DD)
    if (!dateStr.match(/^\d{4}-\d{2}-\d{2}$/)) {
        console.error(`❌ Formato de data inválido: ${dateStr}`);
        showNotification(`Erro: Formato de data inválido (${dateStr})`, 'error');
        return false;
    }
    
    // Verificar se temos o nome do usuário
    if (!userName) {
        console.error('❌ Nome do usuário não encontrado');
        showNotification('Erro: Nome do usuário não encontrado', 'error');
        return false;
    }
    
    // Programar OS diretamente com o nome do usuário
    programarOSComNomeUsuario(osId, dateStr, userName);
    
    return false;
}

// FUNÇÃO CORRIGIDA: programarOSComNomeUsuario
async function programarOSComNomeUsuario(osId, date, userName) {
    try {
        console.log(`🔄 Programando OS #${osId} para ${date} com usuário ${userName}`);
        
        // Verificar se a data está no formato correto (YYYY-MM-DD)
        if (!date || !date.match(/^\d{4}-\d{2}-\d{2}$/)) {
            console.error(`❌ Formato de data inválido: ${date}`);
            showNotification(`Erro: Formato de data inválido (${date})`, 'error');
            return;
        }
        
        // Verificar se o nome do usuário é válido
        if (!userName || userName.startsWith('Técnico #')) {
            console.error(`❌ Nome de usuário inválido: ${userName}`);
            showNotification(`Erro: Nome de usuário inválido (${userName})`, 'error');
            return;
        }
        
        // Preparar dados para API
        const data = {
            id: parseInt(osId),
            data_programada: date,
            usuario_responsavel: userName,
            status: 'programada'
        };
        
        console.log('📤 Enviando dados para API:', data);
        
        // Enviar para API
        const response = await fetch(`/api/ordens-servico/${osId}/programar`, {
            method: 'PUT',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(data)
        });
        
        if (response.ok) {
            const responseData = await response.json();
            console.log('✅ OS programada com sucesso:', responseData);
            
            // Atualizar OS na lista local
            const osIndex = ordensServico.findIndex(os => os.id == osId);
            if (osIndex !== -1) {
                ordensServico[osIndex].data_programada = date;
                ordensServico[osIndex].usuario_responsavel = userName;
                ordensServico[osIndex].status = 'programada';
            }
            
            // Renderizar novamente
            renderPriorityLines();
            renderUsuarios();
            
            // Mostrar notificação de sucesso com data formatada
            const dataFormatada = formatDate(date);
            showNotification(`OS #${osId} programada para ${dataFormatada} com ${userName}`, 'success');
        } else {
            // Tentar obter mensagem de erro
            let errorMessage = 'Erro ao programar OS';
            try {
                const errorData = await response.json();
                errorMessage = errorData.error || errorMessage;
            } catch (e) {
                console.error('Erro ao processar resposta de erro:', e);
            }
            
            console.error(`❌ Erro ao programar OS: ${errorMessage}`);
            showNotification(`Erro: ${errorMessage}`, 'error');
            
            // Método alternativo: programar localmente
            programarOSAlternativa(osId, date, userName);
        }
    } catch (error) {
        console.error('❌ Erro ao programar OS:', error);
        showNotification('Erro ao programar OS. Tentando método alternativo...', 'error');
        
        // Método alternativo: programar localmente
        programarOSAlternativa(osId, date, userName);
    }
}

// Método alternativo para programar OS localmente
function programarOSAlternativa(osId, date, userName) {
    console.log(`🔄 Programando OS #${osId} localmente para ${date} com usuário ${userName}`);
    
    try {
        // Atualizar OS na lista local
        const osIndex = ordensServico.findIndex(os => os.id == osId);
        if (osIndex !== -1) {
            ordensServico[osIndex].data_programada = date;
            ordensServico[osIndex].usuario_responsavel = userName;
            ordensServico[osIndex].status = 'programada';
            
            console.log('✅ OS programada localmente com sucesso');
            
            // Renderizar novamente
            renderPriorityLines();
            renderUsuarios();
            
            // Mostrar notificação de sucesso com data formatada
            const dataFormatada = formatDate(date);
            showNotification(`OS #${osId} programada para ${dataFormatada} com ${userName} (modo local)`, 'success');
            
            return true;
        } else {
            console.error(`❌ OS #${osId} não encontrada na lista local`);
            showNotification(`Erro: OS #${osId} não encontrada`, 'error');
            return false;
        }
    } catch (error) {
        console.error('❌ Erro ao programar OS localmente:', error);
        showNotification('Erro ao programar OS localmente', 'error');
        return false;
    }
}

// Função para desprogramar OS
async function desprogramarOS(osId) {
    try {
        console.log(`🔄 Desprogramando OS #${osId}`);
        
        const response = await fetch(`/api/ordens-servico/${osId}/desprogramar`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            }
        });
        
        if (response.ok) {
            const result = await response.json();
            console.log('✅ OS desprogramada com sucesso:', result);
            
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
            
            // Mostrar notificação
            showNotification(`OS #${osId} desprogramada com sucesso`, 'success');
        } else {
            throw new Error('Erro ao desprogramar OS');
        }
    } catch (error) {
        console.error('❌ Erro ao desprogramar OS:', error);
        showNotification('Erro ao desprogramar OS. Tentando método alternativo...', 'warning');
        
        // Método alternativo: desprogramar localmente
        desprogramarOSLocalmente(osId);
    }
}

// Método alternativo para desprogramar OS localmente
function desprogramarOSLocalmente(osId) {
    try {
        console.log(`🔄 Desprogramando OS #${osId} localmente`);
        
        // Atualizar OS na lista local
        const osIndex = ordensServico.findIndex(os => os.id == osId);
        if (osIndex !== -1) {
            ordensServico[osIndex].data_programada = null;
            ordensServico[osIndex].usuario_responsavel = null;
            ordensServico[osIndex].status = 'aberta';
            
            console.log('✅ OS desprogramada localmente com sucesso');
            
            // Renderizar novamente
            renderPriorityLines();
            renderUsuarios();
            
            // Mostrar notificação
            showNotification(`OS #${osId} desprogramada localmente`, 'success');
            
            return true;
        } else {
            console.error(`❌ OS #${osId} não encontrada na lista local`);
            showNotification(`Erro: OS #${osId} não encontrada`, 'error');
            return false;
        }
    } catch (error) {
        console.error('❌ Erro ao desprogramar OS localmente:', error);
        showNotification('Erro ao desprogramar OS localmente', 'error');
        return false;
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

// FUNÇÃO CORRIGIDA: formatDate
function formatDate(dateStr) {
    try {
        // Verificar se a data está no formato ISO (YYYY-MM-DD)
        if (dateStr && dateStr.match(/^\d{4}-\d{2}-\d{2}$/)) {
            const [year, month, day] = dateStr.split('-');
            return `${day}/${month}/${year}`;
        }
        
        // Tentar converter outras strings de data
        const date = new Date(dateStr);
        if (isNaN(date.getTime())) {
            console.error(`❌ Data inválida: ${dateStr}`);
            return dateStr; // Retornar a string original se não conseguir converter
        }
        
        // Formatar no padrão brasileiro
        const day = String(date.getDate()).padStart(2, '0');
        const month = String(date.getMonth() + 1).padStart(2, '0');
        const year = date.getFullYear();
        
        return `${day}/${month}/${year}`;
    } catch (e) {
        console.error(`❌ Erro ao formatar data: ${dateStr}`, e);
        return dateStr;
    }
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
    notification.textContent = message;
    
    // Estilizar notificação
    notification.style.padding = '10px 15px';
    notification.style.marginBottom = '10px';
    notification.style.borderRadius = '4px';
    notification.style.boxShadow = '0 2px 5px rgba(0,0,0,0.2)';
    notification.style.animation = 'slide-in 0.3s ease-out';
    notification.style.maxWidth = '300px';
    
    // Estilizar por tipo
    switch (type) {
        case 'info':
            notification.style.backgroundColor = '#e3f2fd';
            notification.style.borderLeft = '4px solid #2196f3';
            notification.style.color = '#0d47a1';
            break;
        case 'success':
            notification.style.backgroundColor = '#e8f5e9';
            notification.style.borderLeft = '4px solid #4caf50';
            notification.style.color = '#1b5e20';
            break;
        case 'warning':
            notification.style.backgroundColor = '#fff8e1';
            notification.style.borderLeft = '4px solid #ffc107';
            notification.style.color = '#ff6f00';
            break;
        case 'error':
            notification.style.backgroundColor = '#ffebee';
            notification.style.borderLeft = '4px solid #f44336';
            notification.style.color = '#b71c1c';
            break;
    }
    
    // Adicionar ao container
    notificationContainer.appendChild(notification);
    
    // Remover após 5 segundos
    setTimeout(() => {
        notification.style.opacity = '0';
        notification.style.transform = 'translateX(100%)';
        notification.style.transition = 'opacity 0.5s, transform 0.5s';
        
        setTimeout(() => {
            if (notification.parentNode) {
                notification.parentNode.removeChild(notification);
            }
        }, 500);
    }, 5000);
}

// Verificar pendências
function verificarPendencias() {
    fetch('/api/pmp/verificar-pendencias-hoje')
        .then(response => {
            if (!response.ok) {
                throw new Error('Erro ao verificar pendências');
            }
            return response.json();
        })
        .then(data => {
            if (data.total_pendencias > 0) {
                showNotification(`Existem ${data.total_pendencias} OS pendentes para geração hoje.`, 'warning');
            } else {
                showNotification('Não há OS pendentes para geração hoje.', 'info');
            }
        })
        .catch(error => {
            console.error('Erro:', error);
            showNotification('Erro ao verificar pendências. Tente novamente.', 'error');
        });
}

// Gerar OS pendentes
function gerarOSPendentes() {
    fetch('/api/pmp/gerar-os-pendentes', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        }
    })
        .then(response => {
            if (!response.ok) {
                throw new Error('Erro ao gerar OS pendentes');
            }
            return response.json();
        })
        .then(data => {
            showNotification(`${data.os_geradas.length} OS geradas com sucesso. ${data.erros.length} erros.`, 'success');
            // Recarregar ordens de serviço
            loadOrdensServico().then(() => {
                renderPriorityLines();
                renderUsuarios();
            });
        })
        .catch(error => {
            console.error('Erro:', error);
            showNotification('Erro ao gerar OS pendentes. Tente novamente.', 'error');
        });
}

// Adicionar estilos para notificações
function addNotificationStyles() {
    const style = document.createElement('style');
    style.textContent = `
        @keyframes slide-in {
            from {
                opacity: 0;
                transform: translateX(100%);
            }
            to {
                opacity: 1;
                transform: translateX(0);
            }
        }
        
        .week-changed {
            animation: highlight 1s ease-in-out;
        }
        
        @keyframes highlight {
            0% { background-color: rgba(156, 39, 176, 0.1); }
            50% { background-color: rgba(156, 39, 176, 0.2); }
            100% { background-color: transparent; }
        }
        
        .periodo-semana {
            font-size: 0.8em;
            opacity: 0.8;
        }
    `;
    document.head.appendChild(style);
}

// Inicializar estilos
addNotificationStyles();

console.log('✅ Script de programação carregado com sucesso!');

