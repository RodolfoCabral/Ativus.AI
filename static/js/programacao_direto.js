/**
 * Programação de Ordens de Serviço
 * 
 * Este arquivo contém as funções para gerenciar a programação de ordens de serviço.
 */

// Variáveis globais
let currentWeek = 0;
let currentYear = new Date().getFullYear();
let usuarios = [];
let ordensServico = [];
let draggedElement = null;

// Inicialização
document.addEventListener('DOMContentLoaded', function() {
    console.log('🔄 Inicializando programação...');
    
    // Configurar seletores de semana
    document.getElementById('prev-week').addEventListener('click', function() {
        currentWeek--;
        updateWeekDisplay();
        renderSemana();
    });
    
    document.getElementById('next-week').addEventListener('click', function() {
        currentWeek++;
        updateWeekDisplay();
        renderSemana();
    });
    
    // Configurar botões de ação
    document.getElementById('btn-verificar-pendencias').addEventListener('click', verificarPendencias);
    document.getElementById('btn-gerar-os-pendentes').addEventListener('click', gerarOSPendentes);
    
    // Carregar dados iniciais
    loadData();
    
    // Atualizar exibição da semana
    updateWeekDisplay();
});

// Carregar dados
async function loadData() {
    console.log('🔄 Carregando OS...');
    
    try {
        // Carregar usuários
        await loadUsuarios();
        
        // Carregar ordens de serviço
        try {
            // Tentar API original primeiro
            const response = await fetch('/api/ordens-servico');
            
            if (response.ok) {
                console.log('✅ API original funcionou');
                const data = await response.json();
                processarOrdensServico(data);
            } else {
                throw new Error('API original falhou');
            }
        } catch (error) {
            console.warn('⚠️ API original falhou, tentando alternativa:', error);
            
            // Tentar API alternativa
            try {
                const responseAlt = await fetch('/api/ordens-servico-programacao');
                
                if (responseAlt.ok) {
                    console.log('✅ API alternativa funcionou');
                    const dataAlt = await responseAlt.json();
                    processarOrdensServico(dataAlt);
                } else {
                    throw new Error('API alternativa também falhou');
                }
            } catch (errorAlt) {
                console.error('❌ Todas as APIs falharam:', errorAlt);
                showNotification('Erro ao carregar ordens de serviço', 'error');
            }
        }
    } catch (error) {
        console.error('❌ Erro ao carregar dados:', error);
        showNotification('Erro ao carregar dados', 'error');
    }
}

// Processar ordens de serviço
function processarOrdensServico(data) {
    console.log('🔄 Processando ordens de serviço...');
    
    // Armazenar ordens de serviço
    ordensServico = data;
    
    console.log('📊 Total de OS carregadas:', ordensServico.length);
    
    // Identificar OS de PMP
    const osPMP = ordensServico.filter(os => os.pmp_id);
    console.log('🔧 OS de PMP encontradas:', osPMP.length);
    
    if (osPMP.length > 0) {
        console.log('📋 OS de PMP:', osPMP);
    }
    
    // Adicionar OS programadas à lista de OS
    const osProgramadas = [];
    
    // Verificar se há OS programadas que não estão na lista
    if (Array.isArray(window.osProgramadasCache)) {
        for (const os of window.osProgramadasCache) {
            // Verificar se a OS já existe na lista
            const osExistente = ordensServico.find(o => o.id === os.id);
            
            if (!osExistente) {
                // Adicionar OS programada à lista
                ordensServico.push(os);
                osProgramadas.push(os);
            }
        }
        
        console.log('📊 OS programadas adicionadas:', osProgramadas.length);
        console.log('📊 Total final:', ordensServico.length);
    }
    
    // Renderizar dados
    renderPriorityLines();
    renderSemana();
}

// Carregar usuários
async function loadUsuarios() {
    try {
        const response = await fetch('/api/usuarios');
        
        if (response.ok) {
            const data = await response.json();
            usuarios = data;
            
            console.log('Usuários carregados:', usuarios.length);
            
            // Renderizar usuários
            renderUsuarios();
            
            return usuarios;
        } else {
            throw new Error('Erro ao carregar usuários');
        }
    } catch (error) {
        console.error('❌ Erro ao carregar usuários:', error);
        showNotification('Erro ao carregar usuários', 'error');
        
        // Tentar carregar usuários de forma alternativa
        try {
            const responseAlt = await fetch('/api/usuarios-alt');
            
            if (responseAlt.ok) {
                const dataAlt = await responseAlt.json();
                usuarios = dataAlt;
                
                console.log('Usuários carregados (alternativo):', usuarios.length);
                
                // Renderizar usuários
                renderUsuarios();
                
                return usuarios;
            }
        } catch (errorAlt) {
            console.error('❌ Erro ao carregar usuários (alternativo):', errorAlt);
        }
        
        return [];
    }
}

// Atualizar exibição da semana
function updateWeekDisplay() {
    // Obter data atual
    const today = new Date();
    
    // Ajustar para a semana selecionada
    const currentDate = new Date(today);
    currentDate.setDate(today.getDate() + (currentWeek * 7));
    
    // Obter número da semana
    const weekNumber = getWeekNumber(currentDate);
    
    // Obter ano
    const year = currentDate.getFullYear();
    currentYear = year;
    
    // Obter dias da semana
    const days = getDaysOfWeek(currentDate);
    
    // Atualizar exibição
    document.getElementById('week-number').textContent = weekNumber;
    document.getElementById('year-number').textContent = year;
    
    // Formatar datas de início e fim da semana
    const startDate = formatDateBR(days[0]);
    const endDate = formatDateBR(days[6]);
    
    // Atualizar exibição das datas
    document.getElementById('week-start-date').textContent = startDate;
    document.getElementById('week-end-date').textContent = endDate;
    
    // Adicionar classe de destaque temporariamente
    const weekInfo = document.querySelector('.week-info');
    weekInfo.classList.add('week-highlight');
    
    // Remover classe após animação
    setTimeout(() => {
        weekInfo.classList.remove('week-highlight');
    }, 1500);
}

// Obter número da semana
function getWeekNumber(date) {
    const d = new Date(date);
    d.setHours(0, 0, 0, 0);
    d.setDate(d.getDate() + 4 - (d.getDay() || 7));
    const yearStart = new Date(d.getFullYear(), 0, 1);
    return Math.ceil((((d - yearStart) / 86400000) + 1) / 7);
}

// Obter dias da semana
function getDaysOfWeek(date) {
    const d = new Date(date);
    const day = d.getDay();
    const diff = d.getDate() - day + (day === 0 ? -6 : 1); // Ajustar para começar na segunda-feira
    
    const monday = new Date(d.setDate(diff));
    
    const days = [];
    for (let i = 0; i < 7; i++) {
        const day = new Date(monday);
        day.setDate(monday.getDate() + i);
        days.push(day);
    }
    
    return days;
}

// Formatar data no padrão brasileiro
function formatDateBR(date) {
    const day = String(date.getDate()).padStart(2, '0');
    const month = String(date.getMonth() + 1).padStart(2, '0');
    
    // Obter nome do mês
    const monthNames = ['Janeiro', 'Fevereiro', 'Março', 'Abril', 'Maio', 'Junho', 'Julho', 'Agosto', 'Setembro', 'Outubro', 'Novembro', 'Dezembro'];
    const monthName = monthNames[date.getMonth()];
    
    return `${day}/${month} ${monthName}`;
}

// Renderizar linhas de prioridade
function renderPriorityLines() {
    console.log('🎨 Renderizando linhas de prioridade...');
    
    const container = document.getElementById('priority-lines-container');
    container.innerHTML = '';
    
    // Definir prioridades
    const prioridades = [
        { id: 'baixa', title: 'Prioridade Baixa', class: 'baixa' },
        { id: 'media', title: 'Prioridade Média', class: 'media' },
        { id: 'alta', title: 'Prioridade Alta', class: 'alta' },
        { id: 'seguranca', title: 'Segurança', class: 'seguranca' },
        { id: 'preventiva', title: 'Preventivas', class: 'preventiva', badge: 'PMP' }
    ];
    
    // Criar linhas de prioridade
    prioridades.forEach(prioridade => {
        // Filtrar OS por prioridade
        let osFiltradas = [];
        
        if (prioridade.id === 'preventiva') {
            // Para preventivas, incluir OS com pmp_id
            const preventivas = ordensServico.filter(os => 
                os.pmp_id && 
                os.status === 'aberta' && 
                !os.data_programada && 
                !os.usuario_responsavel
            );
            
            console.log('🔧 Preventivas filtradas:', preventivas.length);
            
            if (preventivas.length > 0) {
                const ids = preventivas.map(os => os.id);
                console.log('📋 IDs das preventivas:', ids);
            }
            
            osFiltradas = preventivas;
        } else {
            // Para outras prioridades, filtrar normalmente
            osFiltradas = ordensServico.filter(os => 
                os.prioridade === prioridade.id && 
                os.status === 'aberta' && 
                !os.data_programada && 
                !os.usuario_responsavel
            );
        }
        
        // Criar linha de prioridade
        const priorityLine = document.createElement('div');
        priorityLine.className = `priority-line ${prioridade.class}`;
        priorityLine.setAttribute('data-prioridade', prioridade.id);
        
        // Criar cabeçalho da linha
        const header = document.createElement('div');
        header.className = 'priority-line-header';
        
        const title = document.createElement('div');
        title.className = 'priority-line-title';
        title.textContent = prioridade.title;
        
        const badge = document.createElement('div');
        badge.className = `priority-line-badge ${prioridade.class}`;
        badge.textContent = prioridade.badge || prioridade.id.toUpperCase();
        
        header.appendChild(title);
        header.appendChild(badge);
        
        // Criar container de chamados
        const chamadosContainer = document.createElement('div');
        chamadosContainer.className = 'chamados-container';
        
        // Adicionar chamados
        if (osFiltradas.length > 0) {
            osFiltradas.forEach(os => {
                const chamadoCard = createOSCard(os);
                chamadosContainer.appendChild(chamadoCard);
            });
            
            console.log(`✅ ${prioridade.id}: ${osFiltradas.length} OS renderizadas`);
        } else {
            const emptyMessage = document.createElement('div');
            emptyMessage.className = 'empty-message';
            emptyMessage.textContent = `Nenhuma OS nesta prioridade`;
            chamadosContainer.appendChild(emptyMessage);
        }
        
        // Adicionar elementos à linha
        priorityLine.appendChild(header);
        priorityLine.appendChild(chamadosContainer);
        
        // Adicionar linha ao container
        container.appendChild(priorityLine);
        
        // Adicionar event listeners para drag and drop
        priorityLine.addEventListener('dragover', handlePriorityDragOver);
        priorityLine.addEventListener('drop', handlePriorityDrop);
    });
}

// Criar card de OS
function createOSCard(os) {
    const chamadoCard = document.createElement('div');
    chamadoCard.className = `chamado-card ${os.prioridade}`;
    chamadoCard.setAttribute('draggable', 'true');
    chamadoCard.setAttribute('data-os-id', os.id);
    
    // Adicionar classe PMP se for uma OS de PMP
    if (os.pmp_id) {
        chamadoCard.classList.add('pmp-card');
    }
    
    // ID da OS
    const chamadoId = document.createElement('div');
    chamadoId.className = 'chamado-id';
    chamadoId.textContent = `OS #${os.id}`;
    
    // Título da OS
    const chamadoTitulo = document.createElement('div');
    chamadoTitulo.className = 'chamado-titulo';
    chamadoTitulo.textContent = os.descricao || 'Sem descrição';
    
    // Informações da OS
    const chamadoInfo1 = document.createElement('div');
    chamadoInfo1.className = 'chamado-info';
    
    const equipamentoIcon = document.createElement('i');
    equipamentoIcon.className = 'fas fa-cog';
    
    const equipamentoText = document.createElement('span');
    equipamentoText.textContent = os.equipamento_id || 'Sem equipamento';
    
    chamadoInfo1.appendChild(equipamentoIcon);
    chamadoInfo1.appendChild(equipamentoText);
    
    // Informações adicionais
    const chamadoInfo2 = document.createElement('div');
    chamadoInfo2.className = 'chamado-info';
    
    const localIcon = document.createElement('i');
    localIcon.className = 'fas fa-map-marker-alt';
    
    const localText = document.createElement('span');
    localText.textContent = `${os.setor || 'Sem setor'} - ${os.filial || 'Sem filial'}`;
    
    chamadoInfo2.appendChild(localIcon);
    chamadoInfo2.appendChild(localText);
    
    // Adicionar badges para OS de PMP
    if (os.pmp_id) {
        const badgesContainer = document.createElement('div');
        badgesContainer.className = 'chamado-info';
        badgesContainer.style.marginTop = '5px';
        
        // Badge PMP
        const pmpBadge = document.createElement('span');
        pmpBadge.className = 'pmp-badge';
        pmpBadge.textContent = 'PMP';
        badgesContainer.appendChild(pmpBadge);
        
        // Badge de frequência
        if (os.frequencia_origem) {
            const freqBadge = document.createElement('span');
            freqBadge.className = 'frequencia-badge';
            freqBadge.textContent = formatarFrequencia(os.frequencia_origem);
            badgesContainer.appendChild(freqBadge);
        }
        
        // Adicionar ao card
        chamadoCard.appendChild(chamadoId);
        chamadoCard.appendChild(chamadoTitulo);
        chamadoCard.appendChild(chamadoInfo1);
        chamadoCard.appendChild(chamadoInfo2);
        chamadoCard.appendChild(badgesContainer);
    } else {
        // Adicionar ao card
        chamadoCard.appendChild(chamadoId);
        chamadoCard.appendChild(chamadoTitulo);
        chamadoCard.appendChild(chamadoInfo1);
        chamadoCard.appendChild(chamadoInfo2);
    }
    
    // Adicionar event listeners para drag and drop
    chamadoCard.addEventListener('dragstart', handleDragStart);
    chamadoCard.addEventListener('dragend', handleDragEnd);
    
    return chamadoCard;
}

// Formatar frequência
function formatarFrequencia(frequencia) {
    const frequencias = {
        'diaria': 'Diária',
        'semanal': 'Semanal',
        'quinzenal': 'Quinzenal',
        'mensal': 'Mensal',
        'bimestral': 'Bimestral',
        'trimestral': 'Trimestral',
        'semestral': 'Semestral',
        'anual': 'Anual'
    };
    
    return frequencias[frequencia] || frequencia;
}

// Criar card de OS agendada
function createOSAgendada(os) {
    const chamadoCard = document.createElement('div');
    chamadoCard.className = 'chamado-agendado';
    chamadoCard.setAttribute('data-os-id', os.id);
    
    // Adicionar classe PMP se for uma OS de PMP
    if (os.pmp_id) {
        chamadoCard.classList.add('pmp-card');
    }
    
    // Título da OS
    const chamadoTitulo = document.createElement('div');
    chamadoTitulo.className = 'chamado-titulo';
    chamadoTitulo.textContent = os.descricao || `OS #${os.id}`;
    
    // Informações da OS
    const chamadoInfo = document.createElement('div');
    chamadoInfo.className = 'chamado-info';
    
    const equipamentoIcon = document.createElement('i');
    equipamentoIcon.className = 'fas fa-cog';
    
    const equipamentoText = document.createElement('span');
    equipamentoText.textContent = os.equipamento_id || 'Sem equipamento';
    
    chamadoInfo.appendChild(equipamentoIcon);
    chamadoInfo.appendChild(equipamentoText);
    
    // Adicionar ao card
    chamadoCard.appendChild(chamadoTitulo);
    chamadoCard.appendChild(chamadoInfo);
    
    // Adicionar badges para OS de PMP
    if (os.pmp_id) {
        const badgesContainer = document.createElement('div');
        badgesContainer.className = 'chamado-info';
        badgesContainer.style.marginTop = '5px';
        
        // Badge PMP
        const pmpBadge = document.createElement('span');
        pmpBadge.className = 'pmp-badge';
        pmpBadge.textContent = 'PMP';
        badgesContainer.appendChild(pmpBadge);
        
        // Badge de frequência
        if (os.frequencia_origem) {
            const freqBadge = document.createElement('span');
            freqBadge.className = 'frequencia-badge';
            freqBadge.textContent = formatarFrequencia(os.frequencia_origem);
            badgesContainer.appendChild(freqBadge);
        }
        
        chamadoCard.appendChild(badgesContainer);
    }
    
    // Adicionar botão de desprogramar
    const btnDesprogramar = document.createElement('button');
    btnDesprogramar.className = 'btn-desprogramar';
    btnDesprogramar.innerHTML = '<i class="fas fa-times"></i>';
    btnDesprogramar.title = 'Desprogramar OS';
    btnDesprogramar.onclick = (e) => {
        e.stopPropagation();
        desprogramarOS(os.id);
    };
    
    chamadoCard.appendChild(btnDesprogramar);
    
    // Adicionar menu de contexto
    chamadoCard.addEventListener('contextmenu', function(e) {
        e.preventDefault();
        
        // Criar menu de contexto
        const contextMenu = document.createElement('div');
        contextMenu.className = 'context-menu';
        contextMenu.style.position = 'absolute';
        contextMenu.style.left = `${e.pageX}px`;
        contextMenu.style.top = `${e.pageY}px`;
        
        // Adicionar opção de desprogramar
        const desprogramarItem = document.createElement('div');
        desprogramarItem.className = 'context-menu-item';
        desprogramarItem.innerHTML = '<i class="fas fa-times"></i> Desprogramar OS';
        desprogramarItem.onclick = () => {
            desprogramarOS(os.id);
            document.body.removeChild(contextMenu);
        };
        
        contextMenu.appendChild(desprogramarItem);
        
        // Adicionar ao body
        document.body.appendChild(contextMenu);
        
        // Fechar menu ao clicar fora
        document.addEventListener('click', function closeMenu() {
            if (document.body.contains(contextMenu)) {
                document.body.removeChild(contextMenu);
            }
            document.removeEventListener('click', closeMenu);
        });
    });
    
    return chamadoCard;
}

// Renderizar usuários
function renderUsuarios() {
    const container = document.getElementById('usuarios-list');
    container.innerHTML = '';
    
    if (usuarios.length === 0) {
        container.innerHTML = '<div class="empty-message">Nenhum usuário encontrado</div>';
        return;
    }
    
    usuarios.forEach(usuario => {
        const row = document.createElement('div');
        row.className = 'usuario-row';
        row.setAttribute('data-user-id', usuario.id);
        row.setAttribute('data-user-name', usuario.name);
        
        const avatar = document.createElement('div');
        avatar.className = 'usuario-avatar';
        avatar.textContent = usuario.name.charAt(0).toUpperCase();
        
        const info = document.createElement('div');
        info.className = 'usuario-info';
        
        const nome = document.createElement('div');
        nome.className = 'usuario-nome';
        nome.textContent = usuario.name;
        
        const cargo = document.createElement('div');
        cargo.className = 'usuario-cargo';
        cargo.textContent = usuario.cargo || 'Técnico';
        
        info.appendChild(nome);
        info.appendChild(cargo);
        
        row.appendChild(avatar);
        row.appendChild(info);
        
        container.appendChild(row);
    });
    
    // Renderizar semana
    renderSemana();
}

// Renderizar semana
function renderSemana() {
    // Obter dias da semana
    const today = new Date();
    const currentDate = new Date(today);
    currentDate.setDate(today.getDate() + (currentWeek * 7));
    
    const days = getDaysOfWeek(currentDate);
    
    // Renderizar cabeçalho da semana
    renderSemanaHeader(days);
    
    // Renderizar grid da semana
    renderSemanaGrid(days);
}

// Renderizar cabeçalho da semana
function renderSemanaHeader(days) {
    const container = document.getElementById('semana-header');
    container.innerHTML = '';
    
    const dayNames = ['Segunda', 'Terça', 'Quarta', 'Quinta', 'Sexta', 'Sábado', 'Domingo'];
    
    days.forEach((day, index) => {
        const dayHeader = document.createElement('div');
        dayHeader.className = 'dia-header';
        
        // Destacar dia atual
        const today = new Date();
        if (day.getDate() === today.getDate() && 
            day.getMonth() === today.getMonth() && 
            day.getFullYear() === today.getFullYear()) {
            dayHeader.classList.add('today');
        }
        
        const dayName = document.createElement('div');
        dayName.className = 'dia-nome';
        dayName.textContent = dayNames[index];
        
        const dayDate = document.createElement('div');
        dayDate.className = 'dia-data';
        dayDate.textContent = formatDate(day);
        
        dayHeader.appendChild(dayName);
        dayHeader.appendChild(dayDate);
        
        container.appendChild(dayHeader);
    });
}

// Renderizar grid da semana
function renderSemanaGrid(days) {
    const container = document.getElementById('semana-grid');
    container.innerHTML = '';
    
    // Verificar se há usuários
    if (usuarios.length === 0) {
        container.innerHTML = '<div class="empty-message">Nenhum usuário encontrado</div>';
        return;
    }
    
    // Criar grid para cada usuário
    usuarios.forEach(usuario => {
        const usuarioSemana = document.createElement('div');
        usuarioSemana.className = 'usuario-semana';
        usuarioSemana.setAttribute('data-user-id', usuario.id);
        
        // Cabeçalho do usuário
        const header = document.createElement('div');
        header.className = 'usuario-semana-header';
        
        const avatar = document.createElement('div');
        avatar.className = 'usuario-semana-avatar';
        avatar.textContent = usuario.name.charAt(0).toUpperCase();
        
        const nome = document.createElement('div');
        nome.className = 'usuario-semana-nome';
        nome.textContent = usuario.name;
        
        header.appendChild(avatar);
        header.appendChild(nome);
        
        // Grid de dias
        const semanaGrid = document.createElement('div');
        semanaGrid.className = 'semana-grid';
        
        // Criar container para cada dia
        days.forEach(day => {
            const diaContainer = document.createElement('div');
            diaContainer.className = 'dia-container';
            diaContainer.setAttribute('data-date', formatDateISO(day));
            diaContainer.setAttribute('data-user-id', usuario.id);
            diaContainer.setAttribute('data-user-name', usuario.name);
            
            // Adicionar OS agendadas para este dia e usuário
            const osAgendadas = ordensServico.filter(os => 
                os.data_programada === formatDateISO(day) && 
                os.usuario_responsavel === usuario.name &&
                os.status === 'programada'
            );
            
            if (osAgendadas.length > 0) {
                osAgendadas.forEach(os => {
                    const osCard = createOSAgendada(os);
                    diaContainer.appendChild(osCard);
                });
            }
            
            // Adicionar event listeners para drag and drop
            diaContainer.addEventListener('dragover', handleDragOver);
            diaContainer.addEventListener('dragenter', handleDragEnter);
            diaContainer.addEventListener('dragleave', handleDragLeave);
            diaContainer.addEventListener('drop', handleDrop);
            
            semanaGrid.appendChild(diaContainer);
        });
        
        // Adicionar elementos ao container do usuário
        usuarioSemana.appendChild(header);
        usuarioSemana.appendChild(semanaGrid);
        
        // Adicionar ao container principal
        container.appendChild(usuarioSemana);
    });
    
    // Adicionar drop zones para todos os dias
    addDropZoneListeners();
}

// Adicionar listeners para drop zones
function addDropZoneListeners() {
    const dropZones = document.querySelectorAll('.dia-container');
    
    dropZones.forEach(zone => {
        // Verificar se já tem listeners
        if (zone.getAttribute('data-has-listeners') === 'true') {
            return;
        }
        
        zone.addEventListener('dragover', handleDragOver);
        zone.addEventListener('dragenter', handleDragEnter);
        zone.addEventListener('dragleave', handleDragLeave);
        zone.addEventListener('drop', handleDrop);
        
        // Marcar como tendo listeners
        zone.setAttribute('data-has-listeners', 'true');
    });
}

// Formatar data
function formatDate(date) {
    const day = String(date.getDate()).padStart(2, '0');
    const month = String(date.getMonth() + 1).padStart(2, '0');
    
    return `${day}/${month}`;
}

// Formatar data no formato ISO (YYYY-MM-DD)
function formatDateISO(date) {
    const year = date.getFullYear();
    const month = String(date.getMonth() + 1).padStart(2, '0');
    const day = String(date.getDate()).padStart(2, '0');
    
    return `${year}-${month}-${day}`;
}

// Verificar pendências
async function verificarPendencias() {
    try {
        const response = await fetch('/api/pmp/verificar-pendencias-hoje');
        
        if (response.ok) {
            const data = await response.json();
            
            if (data.total_pendencias > 0) {
                showNotification(`${data.total_pendencias} OS pendentes para hoje`, 'info');
            } else {
                showNotification('Nenhuma OS pendente para hoje', 'success');
            }
        } else {
            throw new Error('Erro ao verificar pendências');
        }
    } catch (error) {
        console.error('❌ Erro ao verificar pendências:', error);
        showNotification('Erro ao verificar pendências', 'error');
    }
}

// Gerar OS pendentes
async function gerarOSPendentes() {
    try {
        const response = await fetch('/api/pmp/gerar-os-pendentes', {
            method: 'POST'
        });
        
        if (response.ok) {
            const data = await response.json();
            
            if (data.total_geradas > 0) {
                showNotification(`${data.total_geradas} OS geradas com sucesso`, 'success');
                
                // Recarregar dados
                await loadData();
            } else {
                showNotification('Nenhuma OS pendente para gerar', 'info');
            }
        } else {
            throw new Error('Erro ao gerar OS pendentes');
        }
    } catch (error) {
        console.error('❌ Erro ao gerar OS pendentes:', error);
        showNotification('Erro ao gerar OS pendentes', 'error');
    }
}

// Event handlers para drag and drop
function handleDragStart(e) {
    this.classList.add('dragging');
    e.dataTransfer.setData('text/plain', this.getAttribute('data-os-id'));
    draggedElement = this;
}

function handleDragEnd(e) {
    this.classList.remove('dragging');
    draggedElement = null;
}

function handleDragOver(e) {
    e.preventDefault();
    e.dataTransfer.dropEffect = 'move';
}

function handleDragEnter(e) {
    e.preventDefault();
    this.classList.add('drag-over');
}

function handleDragLeave(e) {
    this.classList.remove('drag-over');
}

function handleDrop(e) {
    e.preventDefault();
    e.stopPropagation();
    
    // Remover classe de hover
    this.classList.remove('drag-over');
    
    // Obter ID da OS
    const osId = e.dataTransfer.getData('text/plain');
    if (!osId) return false;
    
    // Obter data do dia
    const dateStr = this.getAttribute('data-date');
    if (!dateStr) return false;
    
    // Obter ID do usuário
    const userId = this.getAttribute('data-user-id');
    if (!userId) return false;
    
    // Obter nome do usuário
    const userName = this.getAttribute('data-user-name');
    if (!userName) return false;
    
    console.log(`🔄 Drop detectado: OS #${osId} para ${dateStr} com usuário ID ${userId}, nome: ${userName}`);
    
    // Programar OS diretamente com o nome do usuário
    programarOSComNomeUsuario(osId, dateStr, userName);
    
    return false;
}

// Programar OS
function programarOS(osId, userId, dateStr) {
    console.log(`🔄 Tentando programar OS #${osId} para ${dateStr} com usuário ID ${userId}`);
    
    // Obter nome do usuário
    let userName = null;
    
    // Método 1: Obter do DOM
    const userElement = document.querySelector(`[data-user-id="${userId}"]`);
    if (userElement) {
        userName = userElement.getAttribute('data-user-name');
        if (userName) {
            console.log(`✅ Nome do usuário obtido do DOM: ${userName}`);
        }
    }
    
    // Método 2: Obter da lista de usuários
    if (!userName && Array.isArray(usuarios)) {
        const usuario = usuarios.find(u => u.id == userId);
        if (usuario && usuario.name) {
            userName = usuario.name;
            console.log(`✅ Nome do usuário obtido da lista: ${userName}`);
        } else {
            console.warn(`⚠️ Usuário não encontrado para ID: ${userId}`);
            console.log('📋 Usuários disponíveis:', usuarios);
        }
    }
    
    // Se ainda não temos o nome, usar um valor padrão
    if (!userName) {
        console.warn(`⚠️ Nome do usuário não encontrado, usando valor padrão: Técnico #${userId}`);
        userName = `Técnico #${userId}`;
    }
    
    // Programar OS com nome do usuário
    programarOSComNomeUsuario(osId, dateStr, userName);
}

// Programar OS com nome do usuário
async function programarOSComNomeUsuario(osId, date, userName) {
    console.log(`🔄 Programando OS #${osId} para ${date} com usuário ${userName}`);
    
    try {
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
            const result = await response.json();
            console.log('✅ OS programada com sucesso', result);
            
            // Atualizar OS na lista local
            const osIndex = ordensServico.findIndex(os => os.id == osId);
            if (osIndex !== -1) {
                ordensServico[osIndex].data_programada = date;
                ordensServico[osIndex].usuario_responsavel = userName;
                ordensServico[osIndex].status = 'programada';
            }
            
            // Armazenar OS programadas em cache
            if (!window.osProgramadasCache) {
                window.osProgramadasCache = [];
            }
            
            // Adicionar OS ao cache se não existir
            const osExistente = window.osProgramadasCache.find(os => os.id == osId);
            if (!osExistente) {
                const os = ordensServico.find(os => os.id == osId);
                if (os) {
                    window.osProgramadasCache.push({
                        ...os,
                        data_programada: date,
                        usuario_responsavel: userName,
                        status: 'programada'
                    });
                }
            }
            
            // Renderizar novamente
            renderPriorityLines();
            renderSemana();
            
            // Mostrar notificação
            showNotification(`OS #${osId} programada para ${formatDate(new Date(date))} com ${userName}`, 'success');
        } else {
            throw new Error('Erro ao programar OS');
        }
    } catch (error) {
        console.error('❌ Erro ao programar OS', error);
        
        // Tentar método alternativo
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
            renderSemana();
            
            // Mostrar notificação
            showNotification(`OS #${osId} programada para ${formatDate(new Date(date))} com ${userName} (modo local)`, 'success');
        } else {
            showNotification('Erro ao programar OS', 'error');
        }
    }
}

// Desprogramar OS
async function desprogramarOS(osId) {
    console.log(`🔄 Desprogramando OS ${osId}`);
    
    try {
        const response = await fetch(`/api/ordens-servico/${osId}/desprogramar`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            }
        });
        
        if (response.ok) {
            const result = await response.json();
            console.log('✅ OS desprogramada com sucesso', result);
            
            // Atualizar OS na lista local
            const osIndex = ordensServico.findIndex(os => os.id == osId);
            if (osIndex !== -1) {
                ordensServico[osIndex].data_programada = null;
                ordensServico[osIndex].usuario_responsavel = null;
                ordensServico[osIndex].status = 'aberta';
            }
            
            // Remover OS do cache
            if (window.osProgramadasCache) {
                window.osProgramadasCache = window.osProgramadasCache.filter(os => os.id != osId);
            }
            
            // Renderizar novamente
            renderPriorityLines();
            renderSemana();
            
            // Mostrar notificação
            showNotification(`OS #${osId} desprogramada com sucesso`, 'success');
        } else {
            throw new Error('Erro ao desprogramar OS');
        }
    } catch (error) {
        console.error('❌ Erro ao desprogramar OS', error);
        
        // Tentar método alternativo
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
            renderSemana();
            
            // Mostrar notificação
            showNotification(`OS #${osId} desprogramada com sucesso (modo local)`, 'success');
        } else {
            showNotification('Erro ao desprogramar OS', 'error');
        }
    }
}

// Handler para dragover em linhas de prioridade
function handlePriorityDragOver(e) {
    e.preventDefault();
    e.dataTransfer.dropEffect = 'move';
    this.classList.add('priority-drag-over');
}

// Handler para drop em linhas de prioridade
function handlePriorityDrop(e) {
    e.preventDefault();
    this.classList.remove('priority-drag-over');
    
    // Obter ID da OS
    const osId = e.dataTransfer.getData('text/plain');
    if (!osId) return;
    
    // Obter prioridade da linha
    const prioridade = this.getAttribute('data-prioridade');
    if (!prioridade) return;
    
    // Atualizar prioridade da OS
    atualizarPrioridadeOS(osId, prioridade);
}

// Atualizar prioridade da OS
async function atualizarPrioridadeOS(osId, prioridade) {
    try {
        const response = await fetch(`/api/ordens-servico/${osId}/prioridade`, {
            method: 'PUT',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ prioridade })
        });
        
        if (response.ok) {
            // Atualizar OS na lista local
            const osIndex = ordensServico.findIndex(os => os.id == osId);
            if (osIndex !== -1) {
                ordensServico[osIndex].prioridade = prioridade;
            }
            
            // Renderizar novamente
            renderPriorityLines();
            
            // Mostrar notificação
            showNotification(`Prioridade da OS #${osId} atualizada para ${prioridade}`, 'success');
        } else {
            throw new Error('Erro ao atualizar prioridade da OS');
        }
    } catch (error) {
        console.error('❌ Erro ao atualizar prioridade da OS', error);
        showNotification('Erro ao atualizar prioridade da OS', 'error');
    }
}

// Mostrar notificação
function showNotification(message, type = 'info') {
    // Remover notificações existentes
    const existingNotifications = document.querySelectorAll('.notification');
    existingNotifications.forEach(notification => {
        notification.remove();
    });
    
    // Criar notificação
    const notification = document.createElement('div');
    notification.className = `notification ${type}`;
    notification.textContent = message;
    
    // Adicionar ao body
    document.body.appendChild(notification);
    
    // Mostrar notificação
    setTimeout(() => {
        notification.classList.add('show');
    }, 10);
    
    // Remover notificação após 5 segundos
    setTimeout(() => {
        notification.classList.remove('show');
        
        // Remover do DOM após animação
        setTimeout(() => {
            if (document.body.contains(notification)) {
                document.body.removeChild(notification);
            }
        }, 300);
    }, 5000);
}

// Obter usuário por ID
function getUserById(userId) {
    // Converter para número se for string
    const id = typeof userId === 'string' ? parseInt(userId) : userId;
    
    // Verificar se é um número válido
    if (isNaN(id)) {
        console.error(`❌ ID de usuário inválido: ${userId}`);
        return null;
    }
    
    // Buscar usuário na lista
    if (Array.isArray(usuarios)) {
        const usuario = usuarios.find(u => u.id === id);
        if (usuario) {
            return usuario;
        }
    }
    
    console.warn(`⚠️ Usuário não encontrado para ID: ${userId}`);
    return null;
}

