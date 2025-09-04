/**
 * Integração entre PMPs e tela de programação
 * Adiciona funcionalidades específicas para OS geradas por PMPs
 */

// Função para gerar OS quando data de início é definida na PMP
async function gerarOSFromPMP(pmpId, dataInicio, usuariosResponsaveis = []) {
    try {
        console.log('🔄 Gerando OS para PMP:', pmpId);
        
        const response = await fetch('/api/pmp/gerar-os', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                pmp_id: pmpId,
                data_inicio_plano: dataInicio
            })
        });
        
        const result = await response.json();
        
        if (response.ok && result.success) {
            console.log('✅ OS gerada com sucesso:', result.os.id);
            
            // Mostrar notificação
            if (typeof showNotification === 'function') {
                const destino = result.vai_para === 'carteira_tecnico' ? 
                    'carteira do técnico' : 'chamados por prioridade';
                showNotification(`OS #${result.os.id} criada e adicionada à ${destino}`, 'success');
            }
            
            // Recarregar dados da programação se estivermos na tela
            if (typeof loadData === 'function') {
                await loadData();
                if (typeof renderPriorityLines === 'function') renderPriorityLines();
                if (typeof renderUsuarios === 'function') renderUsuarios();
            }
            
            return result;
        } else {
            throw new Error(result.error || 'Erro ao gerar OS');
        }
        
    } catch (error) {
        console.error('❌ Erro ao gerar OS:', error);
        if (typeof showNotification === 'function') {
            showNotification(`Erro ao gerar OS: ${error.message}`, 'error');
        }
        throw error;
    }
}

// Função para verificar pendências de OS para PMPs
async function verificarPendenciasPMP() {
    try {
        console.log('🔍 Verificando pendências de PMPs');
        
        const response = await fetch('/api/pmp/verificar-pendencias-hoje');
        const result = await response.json();
        
        if (response.ok && result.success) {
            const pendencias = result.pendencias || [];
            
            if (pendencias.length > 0) {
                console.log(`📋 Encontradas ${pendencias.length} pendências`);
                
                // Mostrar notificação sobre pendências
                if (typeof showNotification === 'function') {
                    const criticas = result.resumo.criticas || 0;
                    const hoje = result.resumo.hoje || 0;
                    
                    let message = `${pendencias.length} OS pendentes de PMPs`;
                    if (criticas > 0) message += ` (${criticas} críticas)`;
                    if (hoje > 0) message += ` (${hoje} para hoje)`;
                    
                    showNotification(message, criticas > 0 ? 'warning' : 'info');
                }
                
                return pendencias;
            } else {
                console.log('✅ Nenhuma pendência encontrada');
                return [];
            }
        } else {
            throw new Error(result.error || 'Erro ao verificar pendências');
        }
        
    } catch (error) {
        console.error('❌ Erro ao verificar pendências:', error);
        return [];
    }
}

// Função para gerar OS pendentes automaticamente
async function gerarOSPendentes(limite = 10) {
    try {
        console.log('🤖 Gerando OS pendentes automaticamente');
        
        const response = await fetch('/api/pmp/gerar-os-pendentes', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ limite })
        });
        
        const result = await response.json();
        
        if (response.ok && result.success) {
            const geradas = result.os_geradas || [];
            const erros = result.erros || [];
            
            console.log(`✅ ${geradas.length} OS geradas, ${erros.length} erros`);
            
            // Mostrar notificação
            if (typeof showNotification === 'function') {
                if (geradas.length > 0) {
                    showNotification(`${geradas.length} OS geradas automaticamente`, 'success');
                }
                if (erros.length > 0) {
                    showNotification(`${erros.length} erros na geração automática`, 'warning');
                }
            }
            
            // Recarregar dados da programação
            if (typeof loadData === 'function') {
                await loadData();
                if (typeof renderPriorityLines === 'function') renderPriorityLines();
                if (typeof renderUsuarios === 'function') renderUsuarios();
            }
            
            return result;
        } else {
            throw new Error(result.error || 'Erro ao gerar OS pendentes');
        }
        
    } catch (error) {
        console.error('❌ Erro ao gerar OS pendentes:', error);
        if (typeof showNotification === 'function') {
            showNotification(`Erro na geração automática: ${error.message}`, 'error');
        }
        throw error;
    }
}

// Função para obter cronograma de uma PMP
async function obterCronogramaPMP(pmpId) {
    try {
        console.log('📅 Obtendo cronograma da PMP:', pmpId);
        
        const response = await fetch(`/api/pmp/${pmpId}/cronograma-geracao`);
        const result = await response.json();
        
        if (response.ok && result.success) {
            console.log('✅ Cronograma obtido:', result.cronograma.length, 'datas');
            return result;
        } else {
            throw new Error(result.error || 'Erro ao obter cronograma');
        }
        
    } catch (error) {
        console.error('❌ Erro ao obter cronograma:', error);
        throw error;
    }
}

// Função para adicionar indicadores visuais de OS de PMP
function adicionarIndicadoresPMP() {
    // Adicionar classe especial para OS geradas por PMP
    const osCards = document.querySelectorAll('.chamado-card[data-os-id]');
    
    osCards.forEach(card => {
        const osId = card.getAttribute('data-os-id');
        const os = ordensServico.find(o => o.id == osId);
        
        if (os && os.pmp_id) {
            // Adicionar indicador visual de que é uma OS de PMP
            card.classList.add('os-pmp');
            
            // Adicionar badge PMP
            if (!card.querySelector('.pmp-badge')) {
                const badge = document.createElement('div');
                badge.className = 'pmp-badge';
                badge.innerHTML = '<i class="fas fa-calendar-check"></i> PMP';
                badge.title = `OS gerada pela PMP - Sequência #${os.numero_sequencia || 1}`;
                card.appendChild(badge);
            }
            
            // Adicionar informações de frequência
            if (os.frequencia_origem && !card.querySelector('.frequencia-info')) {
                const freqInfo = document.createElement('div');
                freqInfo.className = 'frequencia-info';
                freqInfo.innerHTML = `<i class="fas fa-repeat"></i> ${formatarFrequencia(os.frequencia_origem)}`;
                freqInfo.title = `Frequência: ${os.frequencia_origem}`;
                card.appendChild(freqInfo);
            }
        }
    });
}

// Função melhorada para drag and drop de OS de PMP
function melhorarDragDropPMP() {
    // Interceptar o drop para OS de PMP
    const originalHandleDrop = window.handleDrop;
    
    window.handleDrop = function(e) {
        e.preventDefault();
        
        this.classList.remove('drag-over');
        
        if (draggedElement !== this) {
            const osId = draggedElement.dataset.osId;
            const userId = this.dataset.userId;
            const date = this.dataset.date;
            
            // Verificar se é OS de PMP
            const os = ordensServico.find(o => o.id == osId);
            
            if (os && os.pmp_id) {
                // Confirmar movimento de OS de PMP
                const confirmacao = confirm(
                    `Esta é uma OS gerada por PMP (${formatarFrequencia(os.frequencia_origem || 'semanal')}).\n\n` +
                    `Deseja realmente programá-la para outro usuário?\n\n` +
                    `OS: #${osId}\n` +
                    `Usuário: ${getUserById(parseInt(userId))?.name}\n` +
                    `Data: ${formatDate(date)}`
                );
                
                if (!confirmacao) {
                    return false;
                }
            }
            
            programarOS(osId, userId, date);
        }
        
        return false;
    };
}

// Função para adicionar drag entre prioridades
function adicionarDragEntrePrioridades() {
    const priorityLines = document.querySelectorAll('.priority-line');
    
    priorityLines.forEach(line => {
        // Tornar as linhas de prioridade drop zones
        line.addEventListener('dragover', handlePriorityDragOver);
        line.addEventListener('drop', handlePriorityDrop);
        line.addEventListener('dragenter', handlePriorityDragEnter);
        line.addEventListener('dragleave', handlePriorityDragLeave);
    });
}

// Handlers para drag entre prioridades
function handlePriorityDragOver(e) {
    e.preventDefault();
    e.dataTransfer.dropEffect = 'move';
}

function handlePriorityDragEnter(e) {
    e.preventDefault();
    this.classList.add('priority-drag-over');
}

function handlePriorityDragLeave(e) {
    this.classList.remove('priority-drag-over');
}

function handlePriorityDrop(e) {
    e.preventDefault();
    this.classList.remove('priority-drag-over');
    
    if (draggedElement && draggedElement !== this) {
        const osId = draggedElement.dataset.osId;
        const novaPrioridade = this.classList.contains('preventiva') ? 'preventiva' :
                              this.classList.contains('alta') ? 'alta' :
                              this.classList.contains('media') ? 'media' :
                              this.classList.contains('baixa') ? 'baixa' :
                              this.classList.contains('seguranca') ? 'seguranca' : null;
        
        if (novaPrioridade) {
            moverPrioridadeOS(osId, novaPrioridade);
        }
    }
    
    return false;
}

// Função para mover OS entre prioridades
async function moverPrioridadeOS(osId, novaPrioridade) {
    try {
        console.log(`🔄 Movendo OS ${osId} para prioridade ${novaPrioridade}`);
        
        const response = await fetch(`/api/ordens-servico/${osId}/mover-prioridade`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                prioridade: novaPrioridade
            })
        });
        
        const result = await response.json();
        
        if (response.ok && result.success) {
            console.log('✅ Prioridade alterada com sucesso');
            
            // Mostrar notificação
            if (typeof showNotification === 'function') {
                showNotification(`OS #${osId} movida para prioridade ${novaPrioridade}`, 'success');
            }
            
            // Recarregar dados
            if (typeof loadData === 'function') {
                await loadData();
                if (typeof renderPriorityLines === 'function') renderPriorityLines();
                if (typeof renderUsuarios === 'function') renderUsuarios();
            }
            
        } else {
            throw new Error(result.error || 'Erro ao mover prioridade');
        }
        
    } catch (error) {
        console.error('❌ Erro ao mover prioridade:', error);
        if (typeof showNotification === 'function') {
            showNotification(`Erro ao mover OS: ${error.message}`, 'error');
        }
    }
}

// Função para desprogramar OS (voltar para chamados)
async function desprogramarOS(osId) {
    try {
        console.log(`🔄 Desprogramando OS ${osId}`);
        
        const response = await fetch(`/api/ordens-servico/${osId}/desprogramar`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            }
        });
        
        const result = await response.json();
        
        if (response.ok && result.success) {
            console.log('✅ OS desprogramada com sucesso');
            
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

// Função para adicionar botão de geração automática
function adicionarBotaoGeracaoAutomatica() {
    const header = document.querySelector('.programacao-header');
    if (!header || header.querySelector('.btn-geracao-automatica')) return;
    
    const btnContainer = document.createElement('div');
    btnContainer.className = 'btn-container';
    
    // Botão para verificar pendências
    const btnVerificar = document.createElement('button');
    btnVerificar.className = 'btn btn-secondary btn-verificar-pendencias';
    btnVerificar.innerHTML = '<i class="fas fa-search"></i> Verificar Pendências';
    btnVerificar.onclick = verificarPendenciasPMP;
    
    // Botão para gerar OS pendentes
    const btnGerar = document.createElement('button');
    btnGerar.className = 'btn btn-primary btn-geracao-automatica';
    btnGerar.innerHTML = '<i class="fas fa-magic"></i> Gerar OS Pendentes';
    btnGerar.onclick = () => gerarOSPendentes(20);
    
    btnContainer.appendChild(btnVerificar);
    btnContainer.appendChild(btnGerar);
    header.appendChild(btnContainer);
}

// Inicialização quando a página carrega
document.addEventListener('DOMContentLoaded', function() {
    // Aguardar um pouco para garantir que outros scripts carregaram
    setTimeout(() => {
        console.log('🔧 Inicializando integração PMP');
        
        // Adicionar botões de geração automática
        adicionarBotaoGeracaoAutomatica();
        
        // Verificar pendências automaticamente
        verificarPendenciasPMP();
        
        // Melhorar drag and drop para OS de PMP
        melhorarDragDropPMP();
        
        // Adicionar drag entre prioridades
        adicionarDragEntrePrioridades();
        
        // Adicionar indicadores visuais após renderização
        const observer = new MutationObserver(() => {
            adicionarIndicadoresPMP();
            adicionarBotoesDesprogramar();
        });
        
        // Observar mudanças no container de chamados
        const chamadasSection = document.querySelector('.chamados-section');
        if (chamadasSection) {
            observer.observe(chamadasSection, { childList: true, subtree: true });
        }
        
        // Observar mudanças no grid de usuários
        const usuariosGrid = document.getElementById('usuarios-grid');
        if (usuariosGrid) {
            observer.observe(usuariosGrid, { childList: true, subtree: true });
        }
        
    }, 1000);
});

// Exportar funções para uso global
window.pmpIntegration = {
    gerarOSFromPMP,
    verificarPendenciasPMP,
    gerarOSPendentes,
    obterCronogramaPMP,
    adicionarIndicadoresPMP,
    formatarFrequencia,
    melhorarDragDropPMP,
    moverPrioridadeOS,
    desprogramarOS,
    adicionarDragEntrePrioridades
};

