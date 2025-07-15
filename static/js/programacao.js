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
        const response = await fetch('/api/ordens-servico?status=abertas');
        if (response.ok) {
            const data = await response.json();
            ordensServico = data.ordens_servico || [];
            console.log('OS carregadas:', ordensServico.length);
        } else {
            throw new Error('Erro ao carregar ordens de serviço');
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
        
        const osFiltered = ordensServico.filter(os => os.prioridade === prioridade && os.status === 'aberta');
        
        if (osFiltered.length === 0) {
            container.innerHTML = '<div class="empty-priority">Nenhuma OS nesta prioridade</div>';
            return;
        }
        
        container.innerHTML = osFiltered.map(os => createOSCard(os)).join('');
        
        // Adicionar funcionalidade de drag
        container.querySelectorAll('.chamado-card').forEach(card => {
            makeDraggable(card);
        });
    });
}

// Criar card de OS
function createOSCard(os) {
    return `
        <div class="chamado-card" data-os-id="${os.id}" draggable="true">
            <div class="chamado-id">OS #${os.id}</div>
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
    
    // Adicionar funcionalidade de drop nos dias
    container.querySelectorAll('.dia-container').forEach(dia => {
        makeDroppable(dia);
    });
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
        <div class="chamado-agendado" data-os-id="${os.id}">
            <div class="chamado-id">OS #${os.id}</div>
            <div class="chamado-descricao">${os.descricao}</div>
        </div>
    `;
}

// Funções auxiliares
function getCurrentWeek() {
    const now = new Date();
    const start = new Date(now.getFullYear(), 0, 1);
    const diff = now - start;
    const oneWeek = 1000 * 60 * 60 * 24 * 7;
    return Math.ceil(diff / oneWeek);
}

function getDaysOfWeek(week, year) {
    const firstDayOfYear = new Date(year, 0, 1);
    const daysToAdd = (week - 1) * 7;
    const startOfWeek = new Date(firstDayOfYear.getTime() + daysToAdd * 24 * 60 * 60 * 1000);
    
    // Ajustar para segunda-feira
    const dayOfWeek = startOfWeek.getDay();
    const mondayOffset = dayOfWeek === 0 ? -6 : 1 - dayOfWeek;
    const monday = new Date(startOfWeek.getTime() + mondayOffset * 24 * 60 * 60 * 1000);
    
    const days = [];
    for (let i = 0; i < 7; i++) {
        const day = new Date(monday.getTime() + i * 24 * 60 * 60 * 1000);
        days.push({
            date: day.toISOString().split('T')[0],
            day: day.getDate()
        });
    }
    
    return days;
}

function getInitials(name) {
    return name.split(' ').map(n => n[0]).join('').toUpperCase().substring(0, 2);
}

function getOSAgendadas(date, userId) {
    return ordensServico.filter(os => 
        os.data_programada === date && 
        os.usuario_responsavel === userId.toString() &&
        os.status === 'programada'
    );
}

function getWorkloadClass(osAgendadas) {
    const totalHH = osAgendadas.reduce((sum, os) => sum + (os.hh || 0), 0);
    if (totalHH > 16) return 'high-workload';
    if (totalHH > 8) return 'medium-workload';
    return 'low-workload';
}

function getWorkloadIndicator(osAgendadas) {
    const totalHH = osAgendadas.reduce((sum, os) => sum + (os.hh || 0), 0);
    if (totalHH > 16) return 'high';
    if (totalHH > 8) return 'medium';
    return 'low';
}

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

// Funcionalidades de drag and drop
function makeDraggable(element) {
    element.addEventListener('dragstart', function(e) {
        e.dataTransfer.setData('text/plain', element.dataset.osId);
        element.classList.add('dragging');
    });
    
    element.addEventListener('dragend', function(e) {
        element.classList.remove('dragging');
    });
}

function makeDroppable(element) {
    element.addEventListener('dragover', function(e) {
        e.preventDefault();
        element.classList.add('drag-over');
    });
    
    element.addEventListener('dragleave', function(e) {
        element.classList.remove('drag-over');
    });
    
    element.addEventListener('drop', function(e) {
        e.preventDefault();
        element.classList.remove('drag-over');
        
        const osId = e.dataTransfer.getData('text/plain');
        const date = element.dataset.date;
        const userId = element.dataset.userId;
        
        programarOS(osId, date, userId);
    });
}

// Programar OS
async function programarOS(osId, date, userId) {
    try {
        const usuario = usuarios.find(u => u.id.toString() === userId);
        if (!usuario) {
            showNotification('Usuário não encontrado', 'error');
            return;
        }
        
        const response = await fetch(`/api/ordens-servico/${osId}/programar`, {
            method: 'PUT',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                data_programada: date,
                usuario_responsavel: usuario.name
            })
        });
        
        if (response.ok) {
            showNotification('OS programada com sucesso!', 'success');
            await loadData();
            renderPriorityLines();
            renderUsuarios();
        } else {
            const error = await response.json();
            showNotification(error.error || 'Erro ao programar OS', 'error');
        }
        
    } catch (error) {
        console.error('Erro ao programar OS:', error);
        showNotification('Erro interno do servidor', 'error');
    }
}

// Navegação de semanas
function previousWeek() {
    currentWeek--;
    if (currentWeek < 1) {
        currentWeek = 52;
        currentYear--;
    }
    updateWeekDisplay();
    renderUsuarios();
}

function nextWeek() {
    currentWeek++;
    if (currentWeek > 52) {
        currentWeek = 1;
        currentYear++;
    }
    updateWeekDisplay();
    renderUsuarios();
}

function updateWeekDisplay() {
    document.getElementById('week-info').textContent = `Semana: ${currentWeek} | Ano: ${currentYear}`;
}

// Função para mostrar notificações
function showNotification(message, type = 'info') {
    // Criar elemento de notificação
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
            .empty-priority {
                padding: 20px;
                text-align: center;
                color: #666;
                font-style: italic;
            }
        `;
        document.head.appendChild(styles);
    }
    
    // Adicionar ao DOM
    document.body.appendChild(notification);
    
    // Remover após 5 segundos
    setTimeout(() => {
        notification.style.animation = 'slideIn 0.3s ease reverse';
        setTimeout(() => {
            if (notification.parentNode) {
                notification.parentNode.removeChild(notification);
            }
        }, 300);
    }, 5000);
}

