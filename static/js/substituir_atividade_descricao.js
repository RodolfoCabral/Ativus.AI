// ADICIONE ESTE CÓDIGO NO FINAL DO ARQUIVO static/js/executar-os.js

console.log('🎯 Iniciando substituição da div atividade-descricao');

// Função para buscar atividades da PMP e substituir a div
function substituirAtividadeDescricao() {
    console.log('🔍 Procurando div atividade-descricao...');
    
    // Encontrar a div específica
    const atividadeDescricaoDiv = document.getElementById('atividade-descricao');
    
    if (!atividadeDescricaoDiv) {
        console.log('❌ Div atividade-descricao não encontrada');
        return;
    }
    
    console.log('✅ Div atividade-descricao encontrada:', atividadeDescricaoDiv);
    
    // Obter o ID da OS da URL
    const urlParams = new URLSearchParams(window.location.search);
    const osId = urlParams.get('id');
    
    if (!osId) {
        console.log('❌ ID da OS não encontrado na URL');
        return;
    }
    
    console.log('📋 OS ID:', osId);
    
    // Buscar informações da OS e suas atividades
    buscarAtividadesPMP(osId, atividadeDescricaoDiv);
}

// Função para buscar atividades da PMP
function buscarAtividadesPMP(osId, targetDiv) {
    console.log('📡 Buscando atividades da PMP para OS:', osId);
    
    // Primeiro, buscar informações da OS para obter o PMP ID
    fetch(`/api/os/${osId}/atividades`, {
        method: 'GET',
        headers: {
            'Content-Type': 'application/json',
        },
        credentials: 'same-origin'
    })
    .then(response => {
        console.log('📡 Resposta da API:', response.status);
        
        if (response.status === 401) {
            console.log('❌ Não autorizado');
            return null;
        }
        
        if (response.status === 404) {
            console.log('ℹ️ Nenhuma atividade encontrada - OS pode não ter PMP');
            return null;
        }
        
        if (!response.ok) {
            throw new Error(`Erro HTTP: ${response.status}`);
        }
        
        return response.json();
    })
    .then(data => {
        console.log('📊 Dados recebidos:', data);
        
        if (data && data.atividades && data.atividades.length > 0) {
            console.log(`✅ ${data.atividades.length} atividades encontradas!`);
            
            // Substituir a div pelas atividades
            substituirDivPorAtividades(targetDiv, data.atividades, data.os_descricao);
        } else {
            console.log('ℹ️ Nenhuma atividade encontrada - mantendo conteúdo original');
        }
    })
    .catch(error => {
        console.error('❌ Erro ao buscar atividades:', error);
        console.log('ℹ️ Mantendo conteúdo original da div');
    });
}

// Função para substituir a div pelas atividades
function substituirDivPorAtividades(targetDiv, atividades, osDescricao) {
    console.log('🔄 Substituindo div por atividades...');
    
    // Criar HTML das atividades
    let html = `
        <div class="atividades-pmp-container">
            <div class="pmp-header mb-3">
                <h6 class="text-primary mb-2">
                    <i class="fas fa-list-check"></i> Lista de Atividades da PMP
                </h6>
                <small class="text-muted">${osDescricao}</small>
            </div>
            
            <div class="atividades-lista">
    `;
    
    atividades.forEach((atividade, index) => {
        const statusBadge = getStatusBadge(atividade.status);
        
        html += `
            <div class="atividade-item mb-3 p-3 border rounded" 
                 data-atividade-id="${atividade.id}"
                 style="background: white; border-left: 4px solid ${getStatusColor(atividade.status)};">
                
                <div class="d-flex align-items-start justify-content-between mb-2">
                    <div class="atividade-info flex-grow-1">
                        <div class="d-flex align-items-center mb-1">
                            <span class="badge bg-secondary me-2">${index + 1}</span>
                            <strong class="atividade-titulo">${atividade.descricao}</strong>
                        </div>
                        
                        ${atividade.instrucao ? `
                            <div class="atividade-instrucao mt-2 p-2 bg-light rounded">
                                <small><strong>Instrução:</strong> ${atividade.instrucao}</small>
                            </div>
                        ` : ''}
                    </div>
                    
                    <div class="status-badge ms-3">
                        ${statusBadge}
                    </div>
                </div>
                
                <div class="atividade-controles">
                    <div class="row align-items-center">
                        <div class="col-md-6">
                            <label class="form-label small mb-1"><strong>Avaliação:</strong></label>
                            <div class="btn-group w-100" role="group">
                                <input type="radio" class="btn-check" name="status_${atividade.id}" 
                                       id="conforme_${atividade.id}" value="conforme" 
                                       ${atividade.status === 'conforme' ? 'checked' : ''}
                                       onchange="atualizarStatusAtividade(${atividade.id}, 'conforme')">
                                <label class="btn btn-outline-success btn-sm" for="conforme_${atividade.id}">
                                    ✅ C
                                </label>
                                
                                <input type="radio" class="btn-check" name="status_${atividade.id}" 
                                       id="nao_conforme_${atividade.id}" value="nao_conforme" 
                                       ${atividade.status === 'nao_conforme' ? 'checked' : ''}
                                       onchange="atualizarStatusAtividade(${atividade.id}, 'nao_conforme')">
                                <label class="btn btn-outline-danger btn-sm" for="nao_conforme_${atividade.id}">
                                    ❌ NC
                                </label>
                                
                                <input type="radio" class="btn-check" name="status_${atividade.id}" 
                                       id="nao_aplicavel_${atividade.id}" value="nao_aplicavel" 
                                       ${atividade.status === 'nao_aplicavel' ? 'checked' : ''}
                                       onchange="atualizarStatusAtividade(${atividade.id}, 'nao_aplicavel')">
                                <label class="btn btn-outline-secondary btn-sm" for="nao_aplicavel_${atividade.id}">
                                    ➖ NA
                                </label>
                            </div>
                        </div>
                        
                        <div class="col-md-6">
                            <label class="form-label small mb-1"><strong>Observação:</strong></label>
                            <textarea class="form-control form-control-sm observacao-atividade" 
                                      data-atividade-id="${atividade.id}"
                                      rows="2" 
                                      placeholder="Observações..."
                                      onblur="salvarObservacaoAtividade(${atividade.id}, this.value)">${atividade.observacao || ''}</textarea>
                        </div>
                    </div>
                </div>
            </div>
        `;
    });
    
    html += `
            </div>
            
            <div class="atividades-footer mt-3 text-center">
                <button type="button" class="btn btn-primary" onclick="salvarTodasAvaliacoes()">
                    <i class="fas fa-save"></i> Salvar Todas as Avaliações
                </button>
            </div>
        </div>
        
        <style>
        .atividade-item {
            transition: all 0.3s ease;
        }
        .atividade-item:hover {
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
        }
        .btn-check:checked + .btn-outline-success {
            background-color: #28a745;
            border-color: #28a745;
            color: white;
        }
        .btn-check:checked + .btn-outline-danger {
            background-color: #dc3545;
            border-color: #dc3545;
            color: white;
        }
        .btn-check:checked + .btn-outline-secondary {
            background-color: #6c757d;
            border-color: #6c757d;
            color: white;
        }
        </style>
    `;
    
    // Substituir o conteúdo da div
    targetDiv.innerHTML = html;
    
    console.log('✅ Div substituída com sucesso!');
}

// Função para obter badge de status
function getStatusBadge(status) {
    switch (status) {
        case 'conforme':
            return '<span class="badge bg-success">✅ Conforme</span>';
        case 'nao_conforme':
            return '<span class="badge bg-danger">❌ Não Conforme</span>';
        case 'nao_aplicavel':
            return '<span class="badge bg-secondary">➖ Não Aplicável</span>';
        default:
            return '<span class="badge bg-warning">⏳ Pendente</span>';
    }
}

// Função para obter cor do status
function getStatusColor(status) {
    switch (status) {
        case 'conforme': return '#28a745';
        case 'nao_conforme': return '#dc3545';
        case 'nao_aplicavel': return '#6c757d';
        default: return '#ffc107';
    }
}

// Função para atualizar status da atividade
function atualizarStatusAtividade(atividadeId, novoStatus) {
    console.log(`📝 Atualizando status da atividade ${atividadeId} para: ${novoStatus}`);
    
    // Atualizar visualmente
    const atividadeDiv = document.querySelector(`[data-atividade-id="${atividadeId}"]`);
    if (atividadeDiv) {
        // Atualizar cor da borda
        atividadeDiv.style.borderLeftColor = getStatusColor(novoStatus);
        
        // Atualizar badge
        const statusBadge = atividadeDiv.querySelector('.status-badge');
        if (statusBadge) {
            statusBadge.innerHTML = getStatusBadge(novoStatus);
        }
    }
    
    // Salvar no servidor
    const observacao = atividadeDiv ? atividadeDiv.querySelector('.observacao-atividade').value : '';
    salvarAtividadeNoServidor(atividadeId, novoStatus, observacao);
}

// Função para salvar observação da atividade
function salvarObservacaoAtividade(atividadeId, observacao) {
    console.log(`📝 Salvando observação da atividade ${atividadeId}`);
    
    // Obter status atual
    const statusRadio = document.querySelector(`input[name="status_${atividadeId}"]:checked`);
    const status = statusRadio ? statusRadio.value : 'pendente';
    
    salvarAtividadeNoServidor(atividadeId, status, observacao);
}

// Função para salvar atividade no servidor
function salvarAtividadeNoServidor(atividadeId, status, observacao) {
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
        if (response.ok) {
            console.log(`✅ Atividade ${atividadeId} salva com sucesso`);
            
            // Feedback visual
            const atividadeDiv = document.querySelector(`[data-atividade-id="${atividadeId}"]`);
            if (atividadeDiv) {
                atividadeDiv.style.boxShadow = '0 0 10px rgba(40, 167, 69, 0.5)';
                setTimeout(() => {
                    atividadeDiv.style.boxShadow = '';
                }, 1500);
            }
        } else {
            throw new Error(`Erro HTTP: ${response.status}`);
        }
    })
    .catch(error => {
        console.error(`❌ Erro ao salvar atividade ${atividadeId}:`, error);
        
        // Feedback visual de erro
        const atividadeDiv = document.querySelector(`[data-atividade-id="${atividadeId}"]`);
        if (atividadeDiv) {
            atividadeDiv.style.boxShadow = '0 0 10px rgba(220, 53, 69, 0.5)';
            setTimeout(() => {
                atividadeDiv.style.boxShadow = '';
            }, 2000);
        }
    });
}

// Função para salvar todas as avaliações
function salvarTodasAvaliacoes() {
    console.log('💾 Salvando todas as avaliações...');
    
    const atividades = document.querySelectorAll('.atividade-item[data-atividade-id]');
    let promises = [];
    
    atividades.forEach(atividadeDiv => {
        const atividadeId = atividadeDiv.dataset.atividadeId;
        const statusRadio = document.querySelector(`input[name="status_${atividadeId}"]:checked`);
        const status = statusRadio ? statusRadio.value : 'pendente';
        const observacao = atividadeDiv.querySelector('.observacao-atividade').value;
        
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
            const allOk = responses.every(response => response.ok);
            
            if (allOk) {
                alert('✅ Todas as avaliações foram salvas com sucesso!');
                console.log('🎉 Todas as avaliações salvas!');
            } else {
                alert('⚠️ Algumas avaliações podem não ter sido salvas. Verifique e tente novamente.');
            }
        })
        .catch(error => {
            console.error('❌ Erro ao salvar avaliações:', error);
            alert('❌ Erro ao salvar avaliações. Tente novamente.');
        });
}

// EXECUÇÃO AUTOMÁTICA
console.log('⚡ Iniciando execução automática...');

// Tentar várias vezes para garantir que funcione
setTimeout(substituirAtividadeDescricao, 500);
setTimeout(substituirAtividadeDescricao, 1000);
setTimeout(substituirAtividadeDescricao, 2000);
setTimeout(substituirAtividadeDescricao, 3000);

// Event listeners
document.addEventListener('DOMContentLoaded', function() {
    console.log('🚀 DOM carregado - executando substituirAtividadeDescricao');
    setTimeout(substituirAtividadeDescricao, 100);
});

window.addEventListener('load', function() {
    console.log('🌐 Window carregada - executando substituirAtividadeDescricao');
    setTimeout(substituirAtividadeDescricao, 100);
});

console.log('✅ Script de substituição da atividade-descricao carregado!');
