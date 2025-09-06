// Variáveis globais
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
        // Carregar OS normais (abertas)
        const response = await fetch('/api/ordens-servico?status=abertas');
        if (response.ok) {
            const data = await response.json();
            ordensServico = data.ordens_servico || [];
            console.log('OS normais carregadas:', ordensServico.length);
        } else {
            throw new Error('Erro ao carregar ordens de serviço');
        }
        
        // Carregar também OS programadas (com usuário responsável)
        try {
            const responseProgramadas = await fetch('/api/ordens-servico?status=programada');
            if (responseProgramadas.ok) {
                const dataProgramadas = await responseProgramadas.json();
                const osProgramadas = dataProgramadas.ordens_servico || [];
                
                // Adicionar OS programadas à lista
                ordensServico = [...ordensServico, ...osProgramadas];
                console.log('OS programadas adicionadas:', osProgramadas.length);
                console.log('Total de OS:', ordensServico.length);
            }
        } catch (error) {
            console.warn('Erro ao carregar OS programadas:', error);
        }
        
    } catch (error) {
        console.error('Erro ao carregar OS:', error);
        ordensServico = [];
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
    
    prioridades.forEach(prioridade => {
        const container = document.getElementById(`chamados-${prioridade}`);
        if (!container) return;
        
        // Filtrar OS por prioridade e status
        let osFiltered;
        if (prioridade === 'preventiva') {
            // CORREÇÃO: Para preventivas, incluir OS abertas sem usuário E OS de PMP
            osFiltered = ordensServico.filter(os => {
                // Condição 1: Prioridade preventiva e status aberta sem usuário responsável
                const condicao1 = os.prioridade === prioridade && 
                                 os.status === 'aberta' &&
                                 (!os.usuario_responsavel || os.usuario_responsavel === null || os.usuario_responsavel === '');
                
                // Condição 2: OS gerada por PMP (independente do status, mas apenas abertas)
                const condicao2 = os.pmp_id && os.pmp_id !== null && os.status === 'aberta';
                
                return condicao1 || condicao2;
            });
        } else {
            // Para outras prioridades: apenas status 'aberta' e não PMP
            osFiltered = ordensServico.filter(os => 
                os.prioridade === prioridade && 
                os.status === 'aberta' &&
                (!os.pmp_id || os.pmp_id === null) // Excluir OS de PMP das outras prioridades
            );
        }
        
        if (osFiltered.length === 0) {
            container.innerHTML = '<div class="empty-priority">Nenhuma OS nesta prioridade</div>';
            return;
        }
        
        container.innerHTML = osFiltered.map(os => createOSCard(os)).join('');
        
        // Adicionar funcionalidade de drag
        osFiltered.forEach(os => {
            const element = container.querySelector(`[data-os-id="${os.id}"]`);
            if (element) {
                addDragListeners(element);
            }
        });
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
    const date = new Date(dateString);
    return date.toLocaleDateString('pt-BR');
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
        <div class="usuario-row">
            <div class="usuario-info">
                <div class="usuario-avatar">
                    ${getInitials(usuario.name)}
                </div>
                <div class="usuario-nome">${usuario.name}</div>
                <div class="usuario-cargo">${usuario.cargo || 'Usuário'}</div>
            </div>
            
            <div class="dias-semana">
                ${diasSemana.map((dia, index) => createDiaContainer(dia, index, usuario.id)).join('')}
            </div>
        </div>
    `;
}

// Criar container de dia
function createDiaContainer(dia, dayIndex, userId) {
    const diasNomes = ['SEG', 'TER', 'QUA', 'QUI', 'SEX', 'SAB', 'DOM'];
    const osAgendadas = getOSAgendadas(dia.date, userId);
    const workloadClass = getWorkloadClass(osAgendadas);
    
    return `
        <div class="dia-container ${workloadClass}" 
             data-date="${dia.date}" 
             data-user-id="${userId}"
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
        <div class="chamado-agendado" data-os-id="${os.id}" onclick="verificarExecucaoOS(${os.id})">
            <div class="chamado-id">OS #${os.id}</div>
            <div class="chamado-descricao-mini">${os.descricao.substring(0, 30)}...</div>
        </div>
    `;
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
    return usuarios.find(u => u.id === userId);
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
    
    const weekDisplay = document.getElementById('current-week');
    if (weekDisplay) {
        weekDisplay.textContent = `Semana ${currentWeek} - ${firstDay.day}/${firstDay.month} a ${lastDay.day}/${lastDay.month}/${currentYear}`;
    }
}

// Navegação de semanas
function previousWeek() {
    if (currentWeek > 1) {
        currentWeek--;
    } else {
        currentWeek = 52;
        currentYear--;
    }
    updateWeekDisplay();
    renderUsuarios();
}

function nextWeek() {
    if (currentWeek < 52) {
        currentWeek++;
    } else {
        currentWeek = 1;
        currentYear++;
    }
    updateWeekDisplay();
    renderUsuarios();
}

// Adicionar listeners de drag
function addDragListeners(element) {
    element.addEventListener('dragstart', handleDragStart);
    element.addEventListener('dragend', handleDragEnd);
}

// Adicionar listeners de drop zones
function addDropZoneListeners() {
    const dropZones = document.querySelectorAll('.dia-container');
    
    dropZones.forEach(zone => {
        zone.addEventListener('dragover', handleDragOver);
        zone.addEventListener('drop', handleDrop);
        zone.addEventListener('dragenter', handleDragEnter);
        zone.addEventListener('dragleave', handleDragLeave);
    });
}

// Handlers de drag and drop
let draggedElement = null;

function handleDragStart(e) {
    draggedElement = this;
    this.style.opacity = '0.5';
    e.dataTransfer.effectAllowed = 'move';
    e.dataTransfer.setData('text/html', this.outerHTML);
}

function handleDragEnd(e) {
    this.style.opacity = '';
    draggedElement = null;
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
    if (e.stopPropagation) {
        e.stopPropagation();
    }
    
    this.classList.remove('drag-over');
    
    if (draggedElement !== this) {
        const osId = draggedElement.dataset.osId;
        const userId = this.dataset.userId;
        const date = this.dataset.date;
        
        programarOS(osId, userId, date);
    }
    
    return false;
}

// Programar OS
async function programarOS(osId, userId, date) {
    try {
        const usuario = getUserById(parseInt(userId));
        if (!usuario) {
            showNotification('Usuário não encontrado', 'error');
            return;
        }
        
        const response = await fetch(`/api/ordens-servico/${osId}/programar`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                usuario_responsavel: usuario.name,
                data_programada: date
            })
        });
        
        if (response.ok) {
            showNotification(`OS #${osId} programada para ${usuario.name} em ${formatDate(date)}`, 'success');
            
            // Recarregar dados
            await loadOrdensServico();
            renderPriorityLines();
            renderUsuarios();
        } else {
            throw new Error('Erro ao programar OS');
        }
    } catch (error) {
        console.error('Erro ao programar OS:', error);
        showNotification('Erro ao programar OS', 'error');
    }
}

// Formatação
function formatTipoManutencao(tipo) {
    const tipos = {
        'corretiva': 'Corretiva',
        'melhoria': 'Melhoria',
        'setup': 'Setup',
        'pmoc': 'PMOC',
        'inspecao': 'Inspeção',
        'assistencia_tecnica': 'Assistência Técnica'
    };
    return tipos[tipo] || tipo;
}

function formatOficina(oficina) {
    const oficinas = {
        'mecanica': 'Mecânica',
        'eletrica': 'Elétrica',
        'automacao': 'Automação',
        'eletromecanico': 'Eletromecânico',
        'operacional': 'Operacional'
    };
    return oficinas[oficina] || oficina;
}

function formatDate(dateString) {
    const date = new Date(dateString);
    return date.toLocaleDateString('pt-BR');
}

// Função de notificação
function showNotification(message, type = 'info') {
    const notification = document.createElement('div');
    notification.className = `notification notification-${type}`;
    
    notification.innerHTML = `
        <div class="notification-content">
            <i class="fas fa-${type === 'success' ? 'check-circle' : type === 'error' ? 'exclamation-circle' : 'info-circle'}"></i>
            <span>${message}</span>
        </div>
    `;
    
    // Adicionar estilos se não existirem
    if (!document.getElementById('notification-styles')) {
        const styles = document.createElement('style');
        styles.id = 'notification-styles';
        styles.textContent = `
            .notification {
                position: fixed;
                top: 20px;
                right: 20px;
                padding: 16px 20px;
                border-radius: 8px;
                color: white;
                font-weight: 500;
                z-index: 10000;
                animation: slideIn 0.3s ease;
            }
            .notification-success { background: #28a745; }
            .notification-error { background: #dc3545; }
            .notification-info { background: #17a2b8; }
            .notification-content {
                display: flex;
                align-items: center;
                gap: 8px;
            }
            @keyframes slideIn {
                from { transform: translateX(100%); opacity: 0; }
                to { transform: translateX(0); opacity: 1; }
            }
        `;
        document.head.appendChild(styles);
    }
    
    document.body.appendChild(notification);
    
    setTimeout(() => {
        notification.style.animation = 'slideIn 0.3s ease reverse';
        setTimeout(() => {
            if (notification.parentNode) {
                notification.parentNode.removeChild(notification);
            }
        }, 300);
    }, 5000);
}

