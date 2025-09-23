// JavaScript para funcionalidade de atividades de OS
// Adicionar ao final do arquivo programacao.js existente ou incluir separadamente

// Função para abrir modal de atividades quando clicar na OS
function abrirModalAtividades(osId) {
    console.log('Abrindo modal de atividades para OS:', osId);
    
    // Verificar se o modal já existe
    let modal = document.getElementById('modal-atividades-os');
    if (!modal) {
        modal = criarModalAtividades();
        document.body.appendChild(modal);
    }
    
    // Limpar conteúdo anterior
    const listaAtividades = modal.querySelector('#lista-atividades-modal');
    listaAtividades.innerHTML = `
        <div class="text-center py-4">
            <div class="spinner-border text-primary" role="status">
                <span class="visually-hidden">Carregando...</span>
            </div>
            <p class="mt-2">Carregando atividades...</p>
        </div>
    `;
    
    // Mostrar modal
    const bootstrapModal = new bootstrap.Modal(modal);
    bootstrapModal.show();
    
    // Buscar atividades da OS
    fetch(`/api/os/${osId}/atividades`)
        .then(response => {
            if (!response.ok) {
                throw new Error('Erro ao carregar atividades');
            }
            return response.json();
        })
        .then(data => {
            // Preencher informações da OS
            modal.querySelector('#os-numero-modal').textContent = osId;
            modal.querySelector('#os-descricao-modal').textContent = data.os_descricao;
            modal.querySelector('#os-tipo-modal').textContent = data.os_tipo;
            modal.querySelector('#os-status-modal').textContent = data.os_status;
            
            // Renderizar atividades
            renderizarAtividadesModal(data.atividades, listaAtividades);
        })
        .catch(error => {
            console.error('Erro:', error);
            listaAtividades.innerHTML = `
                <div class="alert alert-danger">
                    <i class="fas fa-exclamation-triangle"></i>
                    Erro ao carregar atividades: ${error.message}
                </div>
            `;
        });
}

// Função para criar o modal de atividades
function criarModalAtividades() {
    const modal = document.createElement('div');
    modal.className = 'modal fade';
    modal.id = 'modal-atividades-os';
    modal.tabIndex = '-1';
    modal.setAttribute('aria-labelledby', 'modalAtividadesLabel');
    modal.setAttribute('aria-hidden', 'true');
    
    modal.innerHTML = `
        <div class="modal-dialog modal-lg">
            <div class="modal-content">
                <div class="modal-header bg-primary text-white">
                    <h5 class="modal-title" id="modalAtividadesLabel">
                        <i class="fas fa-list-check"></i>
                        Lista de Execução - OS #<span id="os-numero-modal"></span>
                    </h5>
                    <button type="button" class="btn-close btn-close-white" data-bs-dismiss="modal" aria-label="Fechar"></button>
                </div>
                <div class="modal-body">
                    <div class="os-info mb-3 p-3 bg-light rounded">
                        <div class="row">
                            <div class="col-md-6">
                                <strong>Descrição:</strong> <span id="os-descricao-modal"></span>
                            </div>
                            <div class="col-md-3">
                                <strong>Tipo:</strong> <span id="os-tipo-modal"></span>
                            </div>
                            <div class="col-md-3">
                                <strong>Status:</strong> <span id="os-status-modal"></span>
                            </div>
                        </div>
                    </div>
                    
                    <div id="lista-atividades-modal"></div>
                </div>
                <div class="modal-footer">
                    <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">
                        <i class="fas fa-times"></i> Fechar
                    </button>
                </div>
            </div>
        </div>
    `;
    
    return modal;
}

// Função para renderizar as atividades no modal
function renderizarAtividadesModal(atividades, container) {
    if (!atividades || atividades.length === 0) {
        container.innerHTML = `
            <div class="alert alert-info">
                <i class="fas fa-info-circle"></i>
                Nenhuma atividade cadastrada para esta OS.
            </div>
        `;
        return;
    }
    
    container.innerHTML = '';
    
    atividades.forEach((atividade, index) => {
        const atividadeElement = criarElementoAtividade(atividade, index + 1);
        container.appendChild(atividadeElement);
    });
}

// Função para criar elemento de atividade
function criarElementoAtividade(atividade, numero) {
    const div = document.createElement('div');
    div.className = `atividade-item mb-3 p-3 border rounded ${getClasseStatusAtividade(atividade.status)}`;
    div.setAttribute('data-atividade-id', atividade.id);
    
    div.innerHTML = `
        <div class="atividade-header d-flex align-items-center mb-2">
            <span class="atividade-numero badge bg-primary me-2">${numero}</span>
            <h6 class="atividade-descricao mb-0 flex-grow-1">${atividade.descricao}</h6>
            <span class="atividade-status-icon">${getIconeStatusAtividade(atividade.status)}</span>
        </div>
        
        ${atividade.instrucao ? `
            <div class="atividade-instrucao mb-2 p-2 bg-light rounded">
                <small><strong>Instrução:</strong> ${atividade.instrucao}</small>
            </div>
        ` : ''}
        
        <div class="atividade-avaliacao">
            <div class="row">
                <div class="col-md-6">
                    <label class="form-label small">Avaliação de Conformidade:</label>
                    <select class="form-select form-select-sm status-select" data-atividade-id="${atividade.id}">
                        <option value="pendente" ${atividade.status === 'pendente' ? 'selected' : ''}>⏳ Pendente</option>
                        <option value="conforme" ${atividade.status === 'conforme' ? 'selected' : ''}>✅ Conforme</option>
                        <option value="nao_conforme" ${atividade.status === 'nao_conforme' ? 'selected' : ''}>❌ Não Conforme</option>
                        <option value="nao_aplicavel" ${atividade.status === 'nao_aplicavel' ? 'selected' : ''}>➖ Não Aplicável</option>
                    </select>
                </div>
                <div class="col-md-6">
                    <label class="form-label small">Observação:</label>
                    <textarea class="form-control form-control-sm observacao-textarea" 
                              data-atividade-id="${atividade.id}" 
                              rows="2" 
                              placeholder="Observações sobre a execução...">${atividade.observacao || ''}</textarea>
                </div>
            </div>
        </div>
    `;
    
    // Adicionar listeners para mudanças
    const selectStatus = div.querySelector('.status-select');
    const textareaObs = div.querySelector('.observacao-textarea');
    
    selectStatus.addEventListener('change', (e) => {
        const novoStatus = e.target.value;
        div.className = `atividade-item mb-3 p-3 border rounded ${getClasseStatusAtividade(novoStatus)}`;
        
        const iconeElement = div.querySelector('.atividade-status-icon');
        iconeElement.innerHTML = getIconeStatusAtividade(novoStatus);
        
        salvarAvaliacaoAtividade(atividade.id, novoStatus, textareaObs.value);
    });
    
    textareaObs.addEventListener('blur', (e) => {
        salvarAvaliacaoAtividade(atividade.id, selectStatus.value, e.target.value);
    });
    
    return div;
}

// Função para salvar avaliação da atividade
function salvarAvaliacaoAtividade(atividadeId, status, observacao) {
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
            throw new Error('Erro ao salvar avaliação');
        }
        return response.json();
    })
    .then(data => {
        console.log('Avaliação salva:', data);
        // Opcional: mostrar notificação de sucesso
    })
    .catch(error => {
        console.error('Erro ao salvar avaliação:', error);
        // Opcional: mostrar notificação de erro
    });
}

// Funções auxiliares para classes e ícones
function getClasseStatusAtividade(status) {
    switch (status) {
        case 'conforme': return 'border-success bg-light-success';
        case 'nao_conforme': return 'border-danger bg-light-danger';
        case 'nao_aplicavel': return 'border-secondary bg-light-secondary';
        default: return 'border-warning bg-light-warning';
    }
}

function getIconeStatusAtividade(status) {
    switch (status) {
        case 'conforme': return '<i class="fas fa-check-circle text-success"></i>';
        case 'nao_conforme': return '<i class="fas fa-times-circle text-danger"></i>';
        case 'nao_aplicavel': return '<i class="fas fa-ban text-secondary"></i>';
        default: return '<i class="fas fa-clock text-warning"></i>';
    }
}

// Modificar a função de clique na OS existente para incluir o modal de atividades
// Esta parte deve ser integrada ao seu código existente de programacao.js

// Exemplo de como integrar com o clique existente na OS:
/*
// Adicionar esta linha onde você já tem o evento de clique na OS
// Por exemplo, se você tem algo como:

document.addEventListener('click', function(e) {
    if (e.target.closest('.os-item') || e.target.closest('.chamado-item')) {
        const osElement = e.target.closest('.os-item, .chamado-item');
        const osId = osElement.dataset.osId || osElement.dataset.chamadoId;
        
        // Verificar se a OS tem PMP (tem atividades)
        if (osElement.dataset.pmpId) {
            // Abrir modal de atividades
            abrirModalAtividades(osId);
        } else {
            // Comportamento original para OS sem PMP
            // ... seu código existente ...
        }
    }
});
*/
