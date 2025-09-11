/**
 * Integração entre PMP e Programação
 * 
 * Este arquivo contém funções para integrar o sistema de Plano Mestre de Manutenção (PMP)
 * com o sistema de Programação de Ordens de Serviço.
 */

// Inicialização
document.addEventListener('DOMContentLoaded', function() {
    console.log('🔄 Inicializando integração PMP...');
    
    // Verificar se estamos na página de programação
    if (window.location.pathname.includes('programacao')) {
        inicializarIntegracaoPMP();
    }
});

// Inicializar integração PMP
function inicializarIntegracaoPMP() {
    console.log('✅ Integração PMP inicializada');
    
    // Adicionar estilos CSS
    adicionarEstilosPMP();
    
    // Adicionar observador para detectar quando as OS são carregadas
    observarCarregamentoOS();
    
    // Verificar pendências de PMP
    verificarPendenciasPMP();
}

// Adicionar estilos CSS para elementos PMP
function adicionarEstilosPMP() {
    const style = document.createElement('style');
    style.textContent = `
        .pmp-badge {
            background-color: #9c27b0;
            color: white;
            padding: 2px 6px;
            border-radius: 4px;
            font-size: 0.7rem;
            font-weight: bold;
            margin-right: 4px;
        }
        
        .frequencia-badge {
            background-color: #4caf50;
            color: white;
            padding: 2px 6px;
            border-radius: 4px;
            font-size: 0.7rem;
            font-weight: bold;
        }
        
        .pmp-card {
            border-left: 3px solid #9c27b0 !important;
            background: linear-gradient(to right, rgba(156, 39, 176, 0.05), transparent) !important;
        }
        
        .pmp-card:hover {
            box-shadow: 0 3px 10px rgba(156, 39, 176, 0.2) !important;
        }
        
        .pmp-info {
            color: #9c27b0;
            font-weight: 500;
        }
        
        .btn-desprogramar {
            position: absolute;
            top: 5px;
            right: 5px;
            background-color: #f44336;
            color: white;
            border: none;
            border-radius: 50%;
            width: 20px;
            height: 20px;
            font-size: 10px;
            display: flex;
            align-items: center;
            justify-content: center;
            cursor: pointer;
            opacity: 0.7;
            transition: opacity 0.2s;
        }
        
        .btn-desprogramar:hover {
            opacity: 1;
        }
        
        .chamado-agendado {
            position: relative;
        }
        
        .context-menu {
            background-color: white;
            border-radius: 4px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.2);
            padding: 5px 0;
            z-index: 9999;
        }
        
        .context-menu-item {
            padding: 8px 15px;
            cursor: pointer;
            font-size: 14px;
            display: flex;
            align-items: center;
            gap: 8px;
        }
        
        .context-menu-item:hover {
            background-color: #f0e6f5;
        }
    `;
    document.head.appendChild(style);
}

// Verificar pendências de PMP
async function verificarPendenciasPMP() {
    try {
        const response = await fetch('/api/pmp/verificar-pendencias-hoje');
        if (response.ok) {
            const data = await response.json();
            
            if (data.total_pendencias > 0) {
                // Adicionar badge de pendências ao botão
                const btnVerificarPendencias = document.getElementById('btn-verificar-pendencias');
                if (btnVerificarPendencias) {
                    const badge = document.createElement('span');
                    badge.className = 'pendencias-badge';
                    badge.textContent = data.total_pendencias;
                    badge.style.backgroundColor = '#f44336';
                    badge.style.color = 'white';
                    badge.style.borderRadius = '50%';
                    badge.style.padding = '2px 6px';
                    badge.style.marginLeft = '5px';
                    badge.style.fontSize = '0.7rem';
                    btnVerificarPendencias.appendChild(badge);
                }
            }
        }
    } catch (error) {
        console.error('Erro ao verificar pendências de PMP:', error);
    }
}

// Observar carregamento de OS
function observarCarregamentoOS() {
    // Verificar se já existem OS carregadas
    const osCards = document.querySelectorAll('.chamado-card');
    if (osCards.length > 0) {
        processarOSCarregadas();
        return;
    }
    
    // Configurar observador para detectar quando as OS são carregadas
    const observer = new MutationObserver((mutations) => {
        for (const mutation of mutations) {
            if (mutation.addedNodes.length > 0) {
                const osCards = document.querySelectorAll('.chamado-card');
                if (osCards.length > 0) {
                    processarOSCarregadas();
                    break;
                }
            }
        }
    });
    
    // Observar o container de OS
    const container = document.querySelector('.priority-lines');
    if (container) {
        observer.observe(container, { childList: true, subtree: true });
    }
    
    // Verificar novamente após um tempo
    setTimeout(() => {
        const osCards = document.querySelectorAll('.chamado-card');
        if (osCards.length > 0) {
            processarOSCarregadas();
        }
    }, 2000);
}

// Processar OS carregadas
function processarOSCarregadas() {
    console.log('🔄 Processando OS carregadas...');
    
    // Adicionar drag entre prioridades
    adicionarDragEntrePrioridades();
    
    // Adicionar botões de desprogramar
    adicionarBotoesDesprogramar();
    
    // Configurar observador para detectar novas OS agendadas
    const observer = new MutationObserver((mutations) => {
        for (const mutation of mutations) {
            if (mutation.addedNodes.length > 0) {
                adicionarBotoesDesprogramar();
                break;
            }
        }
    });
    
    // Observar o container de OS agendadas
    const containers = document.querySelectorAll('.dia-chamados');
    containers.forEach(container => {
        observer.observe(container, { childList: true, subtree: true });
    });
}

// Função para adicionar drag entre prioridades
function adicionarDragEntrePrioridades() {
    const priorityLines = document.querySelectorAll('.priority-line');
    
    priorityLines.forEach(line => {
        // Tornar as linhas de prioridade drop zones
        line.addEventListener('dragover', handlePriorityDragOver);
        line.addEventListener('drop', handlePriorityDrop);
    });
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
    const prioridade = this.dataset.prioridade;
    if (!prioridade) return;
    
    // Atualizar prioridade da OS
    atualizarPrioridadeOS(osId, prioridade);
}

// Função para atualizar prioridade da OS
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
            // Recarregar dados
            if (typeof loadData === 'function') {
                await loadData();
                if (typeof renderPriorityLines === 'function') renderPriorityLines();
            }
            
            // Mostrar notificação
            if (typeof showNotification === 'function') {
                showNotification(`Prioridade da OS #${osId} atualizada para ${prioridade}`, 'success');
            }
        } else {
            throw new Error('Erro ao atualizar prioridade da OS');
        }
    } catch (error) {
        console.error('Erro ao atualizar prioridade da OS:', error);
        if (typeof showNotification === 'function') {
            showNotification(`Erro ao atualizar prioridade: ${error.message}`, 'error');
        }
    }
}

// Função para programar OS
async function programarOS(osId, userId, dateStr) {
    try {
        console.log(`🔄 Programando OS #${osId} para usuário #${userId} na data ${dateStr}`);
        
        // Verificar se temos o ID da OS
        if (!osId) {
            console.error('❌ ID da OS não fornecido');
            if (typeof showNotification === 'function') {
                showNotification('Erro: ID da OS não fornecido', 'error');
            }
            return;
        }
        
        // Verificar se temos a data
        if (!dateStr) {
            console.error('❌ Data não fornecida');
            if (typeof showNotification === 'function') {
                showNotification('Erro: Data não fornecida', 'error');
            }
            return;
        }
        
        // Verificar se temos o ID do usuário
        if (!userId) {
            console.error('❌ ID do usuário não fornecido');
            if (typeof showNotification === 'function') {
                showNotification('Erro: ID do usuário não fornecido', 'error');
            }
            return;
        }
        
        // Obter nome do usuário
        let userName = null;
        
        // Método 1: Obter do DOM
        const userElement = document.querySelector(`[data-user-id="${userId}"]`);
        if (userElement) {
            const userRow = userElement.closest('.usuario-row');
            if (userRow) {
                userName = userRow.getAttribute('data-user-name');
                console.log(`✅ Nome do usuário obtido do DOM: ${userName}`);
            }
        }
        
        // Método 2: Obter da lista de usuários
        if (!userName && typeof usuarios !== 'undefined' && Array.isArray(usuarios)) {
            const usuario = usuarios.find(u => u.id == userId);
            if (usuario && usuario.name) {
                userName = usuario.name;
                console.log(`✅ Nome do usuário obtido da lista: ${userName}`);
            }
        }
        
        // Se ainda não temos o nome, usar um valor padrão
        if (!userName) {
            console.warn(`⚠️ Nome do usuário não encontrado para ID ${userId}`);
            userName = `Usuário #${userId}`;
        }
        
        // Preparar dados para API
        const data = {
            id: parseInt(osId),
            data_programada: dateStr,
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
            const result = await response.json();
            console.log('✅ OS programada com sucesso:', result);
            
            // Recarregar dados
            if (typeof loadData === 'function') {
                await loadData();
                if (typeof renderPriorityLines === 'function') renderPriorityLines();
                if (typeof renderUsuarios === 'function') renderUsuarios();
            }
            
            // Mostrar notificação
            if (typeof showNotification === 'function') {
                const dataFormatada = formatarData(dateStr);
                showNotification(`OS #${osId} programada para ${dataFormatada} com ${userName}`, 'success');
            }
            
        } else {
            // Tentar obter mensagem de erro
            let errorMessage = 'Erro ao programar OS';
            try {
                const errorData = await response.json();
                errorMessage = errorData.error || errorMessage;
            } catch (e) {
                console.error('Erro ao processar resposta de erro:', e);
            }
            
            throw new Error(errorMessage);
        }
        
    } catch (error) {
        console.error('❌ Erro ao programar OS:', error);
        if (typeof showNotification === 'function') {
            showNotification(`Erro ao programar OS: ${error.message}`, 'error');
        }
    }
}

// Função para formatar data
function formatarData(dateStr) {
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
            
            // Mostrar notificação
            if (typeof showNotification === 'function') {
                showNotification(`OS #${osId} desprogramada`, 'success');
            }
            
            // Recarregar dados
            if (typeof loadData === 'function') {
                await loadData();
                if (typeof renderPriorityLines === 'function') renderPriorityLines();
                if (typeof renderUsuarios === 'function') renderUsuarios();
            }
            
        } else {
            throw new Error(result.error || 'Erro ao desprogramar OS');
        }
        
    } catch (error) {
        console.error('❌ Erro ao desprogramar OS:', error);
        if (typeof showNotification === 'function') {
            showNotification(`Erro ao desprogramar OS: ${error.message}`, 'error');
        }
    }
}

// Função para adicionar botão de desprogramar nas OS agendadas
function adicionarBotoesDesprogramar() {
    const osAgendadas = document.querySelectorAll('.chamado-agendado');
    
    osAgendadas.forEach(osCard => {
        if (!osCard.querySelector('.btn-desprogramar')) {
            const btnDesprogramar = document.createElement('button');
            btnDesprogramar.className = 'btn-desprogramar';
            btnDesprogramar.innerHTML = '<i class="fas fa-times"></i>';
            btnDesprogramar.title = 'Desprogramar OS';
            btnDesprogramar.onclick = (e) => {
                e.stopPropagation();
                const osId = osCard.dataset.osId;
                desprogramarOS(osId);
            };
            
            osCard.appendChild(btnDesprogramar);
        }
    });
}

// Função para formatar frequência
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

// Exportar funções para uso global
window.programarOS = programarOS;
window.desprogramarOS = desprogramarOS;
window.formatarData = formatarData;
window.formatarFrequencia = formatarFrequencia;

console.log('✅ Script de integração PMP carregado com sucesso!');

