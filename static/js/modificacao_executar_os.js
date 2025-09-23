// MODIFICAÇÃO PARA O ARQUIVO static/js/executar-os.js
// Adicione este código no final do arquivo executar-os.js

// Função para carregar e exibir atividades da OS na tela de execução
function carregarAtividadesOS() {
    // Obter o ID da OS da URL ou de algum elemento da página
    const urlParams = new URLSearchParams(window.location.search);
    const osId = urlParams.get('os_id') || urlParams.get('id');
    
    if (!osId) {
        console.log('ID da OS não encontrado na URL');
        return;
    }
    
    console.log('Carregando atividades para OS:', osId);
    
    // Buscar atividades da OS
    fetch(`/api/os/${osId}/atividades`)
        .then(response => {
            if (!response.ok) {
                throw new Error('Erro ao carregar atividades');
            }
            return response.json();
        })
        .then(data => {
            console.log('Atividades carregadas:', data);
            
            if (data.atividades && data.atividades.length > 0) {
                // Substituir a lista de execução atual pelas atividades
                substituirListaExecucao(data.atividades);
            } else {
                console.log('Nenhuma atividade encontrada para esta OS');
            }
        })
        .catch(error => {
            console.error('Erro ao carregar atividades:', error);
        });
}

// Função para substituir a lista de execução atual
function substituirListaExecucao(atividades) {
    // Encontrar o campo de descrição da atividade atual
    const descricaoAtividade = document.querySelector('input[name="descricao_atividade"], textarea[name="descricao_atividade"]');
    
    if (!descricaoAtividade) {
        console.log('Campo de descrição da atividade não encontrado');
        return;
    }
    
    // Encontrar o container da lista de execução
    const listaExecucaoContainer = descricaoAtividade.closest('.form-group') || descricaoAtividade.closest('.mb-3');
    
    if (!listaExecucaoContainer) {
        console.log('Container da lista de execução não encontrado');
        return;
    }
    
    // Criar nova estrutura com as atividades
    const novaListaHTML = criarListaAtividadesHTML(atividades);
    
    // Substituir o conteúdo
    listaExecucaoContainer.innerHTML = novaListaHTML;
    
    // Adicionar listeners para as mudanças
    adicionarListenersAtividades();
}

// Função para criar o HTML da lista de atividades
function criarListaAtividadesHTML(atividades) {
    let html = `
        <div class="lista-atividades-execucao">
            <h6><i class="fas fa-list-check"></i> Lista de Execução</h6>
            <p class="text-muted small">Marque cada atividade conforme sua execução:</p>
    `;
    
    atividades.forEach((atividade, index) => {
        const statusClass = getStatusClass(atividade.status);
        const statusIcon = getStatusIcon(atividade.status);
        
        html += `
            <div class="atividade-execucao mb-3 p-3 border rounded ${statusClass}" data-atividade-id="${atividade.id}">
                <div class="d-flex align-items-center mb-2">
                    <span class="badge bg-primary me-2">${index + 1}</span>
                    <strong class="flex-grow-1">${atividade.descricao}</strong>
                    <span class="status-icon">${statusIcon}</span>
                </div>
                
                ${atividade.instrucao ? `
                    <div class="instrucao-atividade mb-2 p-2 bg-light rounded">
                        <small><strong>Instrução:</strong> ${atividade.instrucao}</small>
                    </div>
                ` : ''}
                
                <div class="row">
                    <div class="col-md-6">
                        <label class="form-label small">Status de Execução:</label>
                        <select class="form-select form-select-sm status-atividade" data-atividade-id="${atividade.id}">
                            <option value="pendente" ${atividade.status === 'pendente' ? 'selected' : ''}>⏳ Pendente</option>
                            <option value="conforme" ${atividade.status === 'conforme' ? 'selected' : ''}>✅ Conforme</option>
                            <option value="nao_conforme" ${atividade.status === 'nao_conforme' ? 'selected' : ''}>❌ Não Conforme</option>
                            <option value="nao_aplicavel" ${atividade.status === 'nao_aplicavel' ? 'selected' : ''}>➖ Não Aplicável</option>
                        </select>
                    </div>
                    <div class="col-md-6">
                        <label class="form-label small">Observação:</label>
                        <textarea class="form-control form-control-sm observacao-atividade" 
                                  data-atividade-id="${atividade.id}" 
                                  rows="2" 
                                  placeholder="Observações sobre esta atividade...">${atividade.observacao || ''}</textarea>
                    </div>
                </div>
            </div>
        `;
    });
    
    html += `
            <div class="mt-3">
                <button type="button" class="btn btn-success btn-sm" onclick="salvarTodasAtividades()">
                    <i class="fas fa-save"></i> Salvar Todas as Avaliações
                </button>
            </div>
        </div>
    `;
    
    return html;
}

// Função para adicionar listeners às atividades
function adicionarListenersAtividades() {
    // Listeners para mudança de status
    document.querySelectorAll('.status-atividade').forEach(select => {
        select.addEventListener('change', function() {
            const atividadeId = this.dataset.atividadeId;
            const novoStatus = this.value;
            const container = this.closest('.atividade-execucao');
            
            // Atualizar visual
            container.className = `atividade-execucao mb-3 p-3 border rounded ${getStatusClass(novoStatus)}`;
            container.querySelector('.status-icon').innerHTML = getStatusIcon(novoStatus);
            
            // Salvar automaticamente
            const observacao = container.querySelector('.observacao-atividade').value;
            salvarAtividade(atividadeId, novoStatus, observacao);
        });
    });
    
    // Listeners para observações (salvar ao sair do campo)
    document.querySelectorAll('.observacao-atividade').forEach(textarea => {
        textarea.addEventListener('blur', function() {
            const atividadeId = this.dataset.atividadeId;
            const observacao = this.value;
            const container = this.closest('.atividade-execucao');
            const status = container.querySelector('.status-atividade').value;
            
            salvarAtividade(atividadeId, status, observacao);
        });
    });
}

// Função para salvar uma atividade individual
function salvarAtividade(atividadeId, status, observacao) {
    fetch(`/api/os/atividades/${atividadeId}/avaliar`, {
        method: 'PUT',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            status: status,
            observacao: observacao
        })
    })
    .then(response => {
        if (!response.ok) {
            throw new Error('Erro ao salvar atividade');
        }
        return response.json();
    })
    .then(data => {
        console.log('Atividade salva:', data);
        // Opcional: mostrar feedback visual
        mostrarFeedbackSalvo(atividadeId);
    })
    .catch(error => {
        console.error('Erro ao salvar atividade:', error);
        // Opcional: mostrar erro
        mostrarErroSalvar(atividadeId);
    });
}

// Função para salvar todas as atividades
function salvarTodasAtividades() {
    const atividades = document.querySelectorAll('.atividade-execucao');
    let promises = [];
    
    atividades.forEach(container => {
        const atividadeId = container.dataset.atividadeId;
        const status = container.querySelector('.status-atividade').value;
        const observacao = container.querySelector('.observacao-atividade').value;
        
        const promise = fetch(`/api/os/atividades/${atividadeId}/avaliar`, {
            method: 'PUT',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                status: status,
                observacao: observacao
            })
        });
        
        promises.push(promise);
    });
    
    Promise.all(promises)
        .then(() => {
            alert('✅ Todas as atividades foram salvas com sucesso!');
        })
        .catch(error => {
            console.error('Erro ao salvar atividades:', error);
            alert('❌ Erro ao salvar algumas atividades. Tente novamente.');
        });
}

// Funções auxiliares para classes e ícones
function getStatusClass(status) {
    switch (status) {
        case 'conforme': return 'border-success bg-light';
        case 'nao_conforme': return 'border-danger bg-light';
        case 'nao_aplicavel': return 'border-secondary bg-light';
        default: return 'border-warning bg-light';
    }
}

function getStatusIcon(status) {
    switch (status) {
        case 'conforme': return '<i class="fas fa-check-circle text-success"></i>';
        case 'nao_conforme': return '<i class="fas fa-times-circle text-danger"></i>';
        case 'nao_aplicavel': return '<i class="fas fa-ban text-secondary"></i>';
        default: return '<i class="fas fa-clock text-warning"></i>';
    }
}

// Funções de feedback visual
function mostrarFeedbackSalvo(atividadeId) {
    const container = document.querySelector(`[data-atividade-id="${atividadeId}"]`);
    if (container) {
        container.style.boxShadow = '0 0 10px rgba(40, 167, 69, 0.3)';
        setTimeout(() => {
            container.style.boxShadow = '';
        }, 1000);
    }
}

function mostrarErroSalvar(atividadeId) {
    const container = document.querySelector(`[data-atividade-id="${atividadeId}"]`);
    if (container) {
        container.style.boxShadow = '0 0 10px rgba(220, 53, 69, 0.3)';
        setTimeout(() => {
            container.style.boxShadow = '';
        }, 2000);
    }
}

// Inicializar quando a página carregar
document.addEventListener('DOMContentLoaded', function() {
    // Aguardar um pouco para garantir que a página carregou completamente
    setTimeout(carregarAtividadesOS, 1000);
});

// Também tentar carregar quando a janela carregar completamente
window.addEventListener('load', function() {
    setTimeout(carregarAtividadesOS, 500);
});
