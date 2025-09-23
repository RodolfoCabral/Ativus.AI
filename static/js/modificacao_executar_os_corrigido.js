// MODIFICAÇÃO PARA O ARQUIVO static/js/executar-os.js
// Adicione este código no final do arquivo executar-os.js

// Função para carregar e exibir atividades da OS na tela de execução
function carregarAtividadesOS() {
    // Obter o ID da OS da URL
    const urlParams = new URLSearchParams(window.location.search);
    const osId = urlParams.get('id') || urlParams.get('os_id');
    
    if (!osId) {
        console.log('ID da OS não encontrado na URL');
        return;
    }
    
    console.log('🔍 Carregando atividades para OS:', osId);
    
    // Buscar atividades da OS
    fetch(`/api/os/${osId}/atividades`, {
        method: 'GET',
        headers: {
            'Content-Type': 'application/json',
        },
        credentials: 'same-origin' // Incluir cookies de sessão
    })
    .then(response => {
        console.log('📡 Resposta da API atividades:', response.status);
        
        if (response.status === 401) {
            console.log('❌ Não autorizado - redirecionando para login');
            window.location.href = '/login';
            return;
        }
        
        if (!response.ok) {
            throw new Error(`Erro HTTP: ${response.status}`);
        }
        
        return response.json();
    })
    .then(data => {
        console.log('📊 Atividades carregadas:', data);
        
        if (data && data.atividades && data.atividades.length > 0) {
            console.log(`✅ ${data.atividades.length} atividades encontradas`);
            // Substituir a lista de execução atual pelas atividades
            substituirListaExecucao(data.atividades);
        } else {
            console.log('ℹ️ Nenhuma atividade encontrada para esta OS');
            // Não fazer nada, manter a interface original
        }
    })
    .catch(error => {
        console.error('❌ Erro ao carregar atividades:', error);
        // Não fazer nada, manter a interface original
    });
}

// Função para substituir a lista de execução atual
function substituirListaExecucao(atividades) {
    console.log('🔄 Substituindo lista de execução...');
    
    // Procurar pelo campo de descrição da atividade
    const descricaoField = document.querySelector('textarea[placeholder*="Descrição da Atividade"], input[placeholder*="Descrição da Atividade"], textarea[name*="descricao"], input[name*="descricao"]');
    
    if (!descricaoField) {
        console.log('❌ Campo de descrição não encontrado');
        return;
    }
    
    // Encontrar o container pai
    let container = descricaoField.closest('.form-group') || 
                   descricaoField.closest('.mb-3') || 
                   descricaoField.closest('.row') ||
                   descricaoField.parentElement;
    
    if (!container) {
        console.log('❌ Container não encontrado');
        return;
    }
    
    // Procurar por um container maior que contenha "Lista de Execução"
    let listaContainer = container;
    const elementos = document.querySelectorAll('*');
    
    for (let elemento of elementos) {
        if (elemento.textContent && elemento.textContent.includes('Lista de Execução')) {
            listaContainer = elemento.closest('.form-group') || 
                           elemento.closest('.mb-3') || 
                           elemento.closest('.card-body') ||
                           elemento.closest('.container') ||
                           elemento;
            break;
        }
    }
    
    console.log('📍 Container encontrado:', listaContainer);
    
    // Criar nova estrutura com as atividades
    const novaListaHTML = criarListaAtividadesHTML(atividades);
    
    // Substituir o conteúdo
    listaContainer.innerHTML = novaListaHTML;
    
    // Adicionar listeners para as mudanças
    adicionarListenersAtividades();
    
    console.log('✅ Lista de execução substituída com sucesso!');
}

// Função para criar o HTML da lista de atividades
function criarListaAtividadesHTML(atividades) {
    let html = `
        <div class="lista-atividades-execucao">
            <h5><i class="fas fa-list-check"></i> Lista de Execução</h5>
            <p class="text-muted">Avalie cada atividade conforme sua execução:</p>
            <div class="atividades-container">
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
            </div>
            <div class="mt-3 text-center">
                <button type="button" class="btn btn-success" onclick="salvarTodasAtividades()">
                    <i class="fas fa-save"></i> Salvar Todas as Avaliações
                </button>
            </div>
        </div>
        
        <style>
        .atividade-execucao {
            transition: all 0.3s ease;
        }
        .atividade-execucao:hover {
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
        }
        .border-success { border-color: #28a745 !important; background-color: #f8fff9; }
        .border-danger { border-color: #dc3545 !important; background-color: #fff8f8; }
        .border-secondary { border-color: #6c757d !important; background-color: #f8f9fa; }
        .border-warning { border-color: #ffc107 !important; background-color: #fffbf0; }
        </style>
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
    console.log(`💾 Salvando atividade ${atividadeId}: ${status}`);
    
    fetch(`/api/os/atividades/${atividadeId}/avaliar`, {
        method: 'PUT',
        headers: {
            'Content-Type': 'application/json',
        },
        credentials: 'same-origin',
        body: JSON.stringify({
            status: status,
            observacao: observacao
        })
    })
    .then(response => {
        if (response.status === 401) {
            console.log('❌ Não autorizado - redirecionando para login');
            window.location.href = '/login';
            return;
        }
        
        if (!response.ok) {
            throw new Error(`Erro HTTP: ${response.status}`);
        }
        return response.json();
    })
    .then(data => {
        console.log('✅ Atividade salva:', data);
        mostrarFeedbackSalvo(atividadeId);
    })
    .catch(error => {
        console.error('❌ Erro ao salvar atividade:', error);
        mostrarErroSalvar(atividadeId);
    });
}

// Função para salvar todas as atividades
function salvarTodasAtividades() {
    console.log('💾 Salvando todas as atividades...');
    
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
            credentials: 'same-origin',
            body: JSON.stringify({
                status: status,
                observacao: observacao
            })
        });
        
        promises.push(promise);
    });
    
    Promise.all(promises)
        .then(responses => {
            // Verificar se todas as respostas foram bem-sucedidas
            const allOk = responses.every(response => response.ok);
            
            if (allOk) {
                alert('✅ Todas as atividades foram salvas com sucesso!');
            } else {
                alert('⚠️ Algumas atividades podem não ter sido salvas. Verifique e tente novamente.');
            }
        })
        .catch(error => {
            console.error('❌ Erro ao salvar atividades:', error);
            alert('❌ Erro ao salvar atividades. Tente novamente.');
        });
}

// Funções auxiliares para classes e ícones
function getStatusClass(status) {
    switch (status) {
        case 'conforme': return 'border-success';
        case 'nao_conforme': return 'border-danger';
        case 'nao_aplicavel': return 'border-secondary';
        default: return 'border-warning';
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
        const originalBoxShadow = container.style.boxShadow;
        container.style.boxShadow = '0 0 10px rgba(40, 167, 69, 0.5)';
        setTimeout(() => {
            container.style.boxShadow = originalBoxShadow;
        }, 1500);
    }
}

function mostrarErroSalvar(atividadeId) {
    const container = document.querySelector(`[data-atividade-id="${atividadeId}"]`);
    if (container) {
        const originalBoxShadow = container.style.boxShadow;
        container.style.boxShadow = '0 0 10px rgba(220, 53, 69, 0.5)';
        setTimeout(() => {
            container.style.boxShadow = originalBoxShadow;
        }, 2000);
    }
}

// Inicializar quando a página carregar
document.addEventListener('DOMContentLoaded', function() {
    console.log('🚀 Inicializando sistema de atividades...');
    // Aguardar um pouco para garantir que a página carregou completamente
    setTimeout(carregarAtividadesOS, 2000);
});

// Também tentar carregar quando a janela carregar completamente
window.addEventListener('load', function() {
    console.log('🌐 Página carregada completamente');
    setTimeout(carregarAtividadesOS, 1000);
});
