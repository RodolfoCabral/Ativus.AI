document.addEventListener("DOMContentLoaded", function () {
    // Esta função será chamada quando o DOM estiver pronto
    initializeAtividadesOS();
});

function initializeAtividadesOS() {
    // Adicionar um listener de clique a todos os elementos que representam uma OS
    // Usamos delegação de eventos para lidar com OS adicionadas dinamicamente
    document.body.addEventListener("click", function (event) {
        const osElement = event.target.closest(".os-card, .os-item"); // Adapte o seletor para o seu HTML
        if (osElement) {
            const osId = osElement.dataset.osId;
            if (osId) {
                abrirModalAtividades(osId);
            }
        }
    });
}

function abrirModalAtividades(osId) {
    // Verificar se o modal já existe, senão criar
    let modal = document.getElementById("modal-atividades-os");
    if (!modal) {
        modal = criarModalAtividades();
        document.body.appendChild(modal);
    }

    // Mostrar o modal e carregar os dados
    const bootstrapModal = new bootstrap.Modal(modal);
    bootstrapModal.show();

    // Limpar conteúdo anterior e mostrar spinner
    const listaAtividades = modal.querySelector("#lista-atividades-modal");
    listaAtividades.innerHTML = `<div class="text-center"><div class="spinner-border" role="status"><span class="visually-hidden">Carregando...</span></div></div>`;

    // Buscar os detalhes da OS e suas atividades
    fetch(`/api/os/${osId}/atividades`, { credentials: 'include' })
        .then(response => {
            if (!response.ok) {
                throw new Error("Falha ao carregar atividades");
            }
            return response.json();
        })
        .then(atividades => {
            // Preencher os detalhes da OS (adapte conforme necessário)
            modal.querySelector("#os-numero-modal").textContent = osId;
            // ... preencher outros detalhes da OS ...

            renderizarAtividades(listaAtividades, atividades);
        })
        .catch(error => {
            listaAtividades.innerHTML = `<div class="alert alert-danger">${error.message}</div>`;
        });
}

function criarModalAtividades() {
    const modalElement = document.createElement("div");
    modalElement.className = "modal fade";
    modalElement.id = "modal-atividades-os";
    modalElement.innerHTML = `
        <div class="modal-dialog modal-lg">
            <div class="modal-content">
                <div class="modal-header">
                    <h5 class="modal-title">Lista de Execução - OS #<span id="os-numero-modal"></span></h5>
                    <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
                </div>
                <div class="modal-body">
                    <div id="lista-atividades-modal"></div>
                </div>
                <div class="modal-footer">
                    <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Fechar</button>
                </div>
            </div>
        </div>
    `;
    return modalElement;
}

function renderizarAtividades(container, atividades) {
    if (atividades.length === 0) {
        container.innerHTML = `<div class="alert alert-info">Nenhuma atividade para esta OS.</div>`;
        return;
    }

    container.innerHTML = "";
    atividades.forEach(atividade => {
        const atividadeDiv = document.createElement("div");
        atividadeDiv.className = "atividade-item mb-3 p-3 border rounded";
        atividadeDiv.innerHTML = `
            <h6>${atividade.ordem}. ${atividade.descricao}</h6>
            <div class="row">
                <div class="col-md-6">
                    <label class="form-label">Status</label>
                    <select class="form-select status-select" data-atividade-id="${atividade.id}">
                        <option value="pendente" ${atividade.status === "pendente" ? "selected" : ""}>Pendente</option>
                        <option value="conforme" ${atividade.status === "conforme" ? "selected" : ""}>Conforme</option>
                        <option value="nao_conforme" ${atividade.status === "nao_conforme" ? "selected" : ""}>Não Conforme</option>
                        <option value="nao_aplicavel" ${atividade.status === "nao_aplicavel" ? "selected" : ""}>Não Aplicável</option>
                    </select>
                </div>
                <div class="col-md-6">
                    <label class="form-label">Observação</label>
                    <textarea class="form-control observacao-textarea" data-atividade-id="${atividade.id}">${atividade.observacao || ""}</textarea>
                </div>
            </div>
        `;
        container.appendChild(atividadeDiv);
    });

    // Adicionar listeners para salvar as alterações
    container.querySelectorAll(".status-select, .observacao-textarea").forEach(element => {
        element.addEventListener("change", (event) => {
            const atividadeId = event.target.dataset.atividadeId;
            const status = container.querySelector(`.status-select[data-atividade-id="${atividadeId}"]`).value;
            const observacao = container.querySelector(`.observacao-textarea[data-atividade-id="${atividadeId}"]`).value;
            salvarAvaliacao(atividadeId, status, observacao);
        });
    });
}

function salvarAvaliacao(atividadeId, status, observacao) {
    fetch(`/api/os/atividades/${atividadeId}/avaliar`, {
        method: "PUT",
        headers: {
            "Content-Type": "application/json",
        },
        body: JSON.stringify({ status, observacao }),
    })
    .then(response => {
        if (!response.ok) {
            throw new Error("Falha ao salvar avaliação");
        }
        // Opcional: mostrar uma notificação de sucesso
        console.log(`Atividade ${atividadeId} salva com sucesso!`);
    })
    .catch(error => {
        // Opcional: mostrar uma notificação de erro
        console.error(error.message);
    });
}



// Se estivermos na página de executar-os (presença da div #atividade-descricao), carregar e renderizar as atividades diretamente na página
function carregarAtividadesNaPagina() {
    console.log('🔄 INICIANDO carregarAtividadesNaPagina()');
    
    // ETAPA 1: Verificar se existe o elemento de destino
    const descDiv = document.getElementById('atividade-descricao');
    console.log('📍 ETAPA 1 - Elemento atividade-descricao:', descDiv);
    console.log('📍 ETAPA 1 - Elemento existe?', !!descDiv);
    
    if (!descDiv) {
        console.log('❌ ETAPA 1 - Elemento #atividade-descricao não encontrado. Saindo da função.');
        return;
    }
    
    // ETAPA 2: Obter parâmetros da URL
    console.log('📍 ETAPA 2 - Obtendo parâmetros da URL');
    const urlParams = new URLSearchParams(window.location.search);
    console.log('📍 ETAPA 2 - URL completa:', window.location.href);
    console.log('📍 ETAPA 2 - Query string:', window.location.search);
    console.log('📍 ETAPA 2 - URLSearchParams:', urlParams.toString());
    
    const osIdFromId = urlParams.get('id');
    const osIdFromOsId = urlParams.get('os_id');
    const osId = osIdFromId || osIdFromOsId;
    
    console.log('📍 ETAPA 2 - Parâmetro "id":', osIdFromId);
    console.log('📍 ETAPA 2 - Parâmetro "os_id":', osIdFromOsId);
    console.log('📍 ETAPA 2 - OS ID final escolhido:', osId);
    
    if (!osId) {
        console.log('❌ ETAPA 2 - Nenhum ID de OS encontrado na URL. Saindo da função.');
        return;
    }
    
    // ETAPA 3: Mostrar loading
    console.log('📍 ETAPA 3 - Definindo estado de carregamento');
    descDiv.innerHTML = '<div class="text-muted">Carregando atividades...</div>';
    console.log('📍 ETAPA 3 - HTML de loading definido');
    
    // ETAPA 4: Fazer requisição para API
    console.log('📍 ETAPA 4 - Iniciando requisição para API');
    const apiUrl = `/api/os/${osId}/atividades`;
    console.log('📍 ETAPA 4 - URL da API:', apiUrl);
    console.log('📍 ETAPA 4 - Fazendo fetch com credentials: include');
    
    fetch(apiUrl, { credentials: 'include' })
        .then(r => {
            console.log('📍 ETAPA 5 - Resposta recebida da API');
            console.log('📍 ETAPA 5 - Status da resposta:', r.status);
            console.log('📍 ETAPA 5 - Status text:', r.statusText);
            console.log('📍 ETAPA 5 - Headers da resposta:', Object.fromEntries(r.headers.entries()));
            console.log('📍 ETAPA 5 - Response OK?', r.ok);
            
            if (!r.ok) {
                console.log('❌ ETAPA 5 - Resposta não OK, lançando erro');
                throw new Error(`Falha ao carregar atividades - Status: ${r.status} ${r.statusText}`);
            }
            
            console.log('✅ ETAPA 5 - Resposta OK, convertendo para JSON');
            return r.json();
        })
        .then(data => {
            console.log('📍 ETAPA 6 - Dados JSON recebidos');
            console.log('📍 ETAPA 6 - Dados completos:', data);
            console.log('📍 ETAPA 6 - Tipo de data:', typeof data);
            console.log('📍 ETAPA 6 - data.atividades existe?', 'atividades' in data);
            console.log('📍 ETAPA 6 - data.atividades:', data.atividades);
            console.log('📍 ETAPA 6 - data.atividades é array?', Array.isArray(data.atividades));
            
            if (!Array.isArray(data.atividades)) {
                console.log('❌ ETAPA 6 - data.atividades não é um array');
                descDiv.innerHTML = '<div class="text-danger">Nenhuma atividade encontrada.</div>';
                return;
            }
            
            console.log('📍 ETAPA 6 - Quantidade de atividades:', data.atividades.length);
            
            if (data.atividades.length === 0) {
                console.log('📍 ETAPA 6 - Nenhuma atividade encontrada');
                descDiv.innerHTML = '<div class="text-muted">Nenhuma atividade vinculada a esta OS.</div>';
                return;
            }
            
            // ETAPA 7: Construir HTML das atividades
            console.log('📍 ETAPA 7 - Construindo HTML das atividades');
            let html = '<div class="atividades-list">';
            
            data.atividades.forEach((atividade, idx) => {
                console.log(`📍 ETAPA 7 - Processando atividade ${idx + 1}:`, atividade);
                console.log(`📍 ETAPA 7 - Atividade ${idx + 1} - ID:`, atividade.id);
                console.log(`📍 ETAPA 7 - Atividade ${idx + 1} - Descrição:`, atividade.descricao);
                console.log(`📍 ETAPA 7 - Atividade ${idx + 1} - Status:`, atividade.status);
                console.log(`📍 ETAPA 7 - Atividade ${idx + 1} - Ordem:`, atividade.ordem);
                console.log(`📍 ETAPA 7 - Atividade ${idx + 1} - Observação:`, atividade.observacao);
                
                const status = atividade.status || '';
                html += `
                    <div class="atividade-item mb-3 p-3 border rounded" data-atividade-id="${atividade.id}">
                        <div class="mb-2"><strong>${atividade.ordem || (idx+1)}.</strong> ${atividade.descricao}</div>
                        
                        <div class="row">
                            <div class="col-md-6">
                                <div class="d-flex gap-2 mb-2">
                                    <label class="btn btn-sm ${status==='conforme' ? 'btn-success' : 'btn-outline-success'} flex-fill" style="min-width: 60px;">
                                        <input type="radio" name="status_${atividade.id}" value="conforme" ${status==='conforme'?'checked':''} style="display: none;"> 
                                        ✓ C
                                    </label>
                                    <label class="btn btn-sm ${status==='nao_conforme' ? 'btn-danger' : 'btn-outline-danger'} flex-fill" style="min-width: 60px;">
                                        <input type="radio" name="status_${atividade.id}" value="nao_conforme" ${status==='nao_conforme'?'checked':''} style="display: none;"> 
                                        ✗ NC
                                    </label>
                                    <label class="btn btn-sm ${status==='nao_aplicavel' ? 'btn-secondary' : 'btn-outline-secondary'} flex-fill" style="min-width: 60px;">
                                        <input type="radio" name="status_${atividade.id}" value="nao_aplicavel" ${status==='nao_aplicavel'?'checked':''} style="display: none;"> 
                                        ○ NA
                                    </label>
                                </div>
                            </div>
                            <div class="col-md-6">
                                <textarea class="form-control form-control-sm observacao-text" placeholder="Observação..." rows="2">${atividade.observacao || ''}</textarea>
                            </div>
                        </div>
                    </div>
                `;
            });
            html += '</div>';
            
            console.log('📍 ETAPA 7 - HTML construído, tamanho:', html.length);
            console.log('📍 ETAPA 7 - Definindo HTML no elemento');
            descDiv.innerHTML = html;
            console.log('✅ ETAPA 7 - HTML definido com sucesso');

            // ETAPA 8: Adicionar event listeners
            console.log('📍 ETAPA 8 - Adicionando event listeners');
            const atividadeItems = descDiv.querySelectorAll('.atividade-item');
            console.log('📍 ETAPA 8 - Quantidade de itens de atividade encontrados:', atividadeItems.length);
            
            atividadeItems.forEach((item, itemIdx) => {
                const atividadeId = item.dataset.atividadeId;
                console.log(`📍 ETAPA 8 - Configurando listeners para atividade ${itemIdx + 1}, ID: ${atividadeId}`);
                
                const labels = item.querySelectorAll('label.btn');
                const textarea = item.querySelector('.observacao-text');
                
                console.log(`📍 ETAPA 8 - Atividade ${atividadeId} - Labels encontrados:`, labels.length);
                console.log(`📍 ETAPA 8 - Atividade ${atividadeId} - Textarea encontrada:`, !!textarea);
                
                // Adicionar listeners para os labels (botões customizados)
                labels.forEach((label, labelIdx) => {
                    const radio = label.querySelector('input[type="radio"]');
                    if (radio) {
                        console.log(`📍 ETAPA 8 - Adicionando listener para label ${labelIdx + 1} da atividade ${atividadeId}`);
                        
                        label.addEventListener('click', (e) => {
                            e.preventDefault();
                            
                            // Desmarcar outros botões da mesma atividade
                            labels.forEach(l => {
                                l.classList.remove('btn-success', 'btn-danger', 'btn-secondary');
                                l.classList.add('btn-outline-success', 'btn-outline-danger', 'btn-outline-secondary');
                                const r = l.querySelector('input[type="radio"]');
                                if (r) r.checked = false;
                            });
                            
                            // Marcar o botão clicado
                            radio.checked = true;
                            const status = radio.value;
                            
                            // Aplicar estilo ativo
                            if (status === 'conforme') {
                                label.classList.remove('btn-outline-success');
                                label.classList.add('btn-success');
                            } else if (status === 'nao_conforme') {
                                label.classList.remove('btn-outline-danger');
                                label.classList.add('btn-danger');
                            } else if (status === 'nao_aplicavel') {
                                label.classList.remove('btn-outline-secondary');
                                label.classList.add('btn-secondary');
                            }
                            
                            const obs = textarea ? textarea.value : '';
                            console.log(`🔄 EVENTO LABEL - Atividade ${atividadeId}, Status: ${status}, Obs: ${obs}`);
                            
                            // Salvar via API
                            fetch(`/api/os/atividades/${atividadeId}/avaliar`, {
                                method: 'PUT',
                                credentials: 'include',
                                headers: {'Content-Type':'application/json'},
                                body: JSON.stringify({status: status, observacao: obs})
                            }).then(res => {
                                console.log(`✅ RESPOSTA LABEL - Atividade ${atividadeId}, Status resposta: ${res.status}`);
                                if (!res.ok) throw new Error('Erro ao salvar');
                                console.log('✅ SUCESSO LABEL - Salvo', atividadeId, status);
                                
                                // Adicionar classe visual de feedback
                                item.classList.remove('avaliada', 'nao-conforme', 'nao-aplicavel');
                                if (status === 'conforme') item.classList.add('avaliada');
                                else if (status === 'nao_conforme') item.classList.add('nao-conforme');
                                else if (status === 'nao_aplicavel') item.classList.add('nao-aplicavel');
                                
                            }).catch(err => {
                                console.error('❌ ERRO LABEL - ', err);
                            });
                        });
                    }
                });
                
                if (textarea) {
                    console.log(`📍 ETAPA 8 - Adicionando listener blur para textarea da atividade ${atividadeId}`);
                    textarea.addEventListener('blur', () => {
                        const checked = item.querySelector(`input[type="radio"][name="status_${atividadeId}"]:checked`);
                        const status = checked ? checked.value : null;
                        const obs = textarea.value;
                        console.log(`🔄 EVENTO TEXTAREA - Atividade ${atividadeId}, Status: ${status}, Obs: ${obs}`);
                        
                        fetch(`/api/os/atividades/${atividadeId}/avaliar`, {
                            method: 'PUT',
                            credentials: 'include',
                            headers: {'Content-Type':'application/json'},
                            body: JSON.stringify({status: status, observacao: obs})
                        }).then(res => {
                            console.log(`✅ RESPOSTA TEXTAREA - Atividade ${atividadeId}, Status resposta: ${res.status}`);
                            if (!res.ok) throw new Error('Erro ao salvar obs');
                            console.log('✅ SUCESSO TEXTAREA - Obs salva', atividadeId);
                        }).catch(err => {
                            console.error('❌ ERRO TEXTAREA - ', err);
                        });
                    });
                }
            });
            
            console.log('✅ ETAPA 8 - Todos os event listeners configurados');
            console.log('🎉 SUCESSO TOTAL - Atividades carregadas e configuradas com sucesso!');
        })
        .catch(err => {
            console.error('❌ ERRO GERAL - Erro capturado:', err);
            console.error('❌ ERRO GERAL - Tipo do erro:', typeof err);
            console.error('❌ ERRO GERAL - Mensagem:', err.message);
            console.error('❌ ERRO GERAL - Stack:', err.stack);
            descDiv.innerHTML = '<div class="text-danger">Erro ao carregar atividades.</div>';
        });
}

// Tentar carregar in-page ao carregar o DOM
document.addEventListener('DOMContentLoaded', function() {
    console.log('🚀 DOM CARREGADO - Iniciando processo de carregamento de atividades');
    console.log('🚀 DOM CARREGADO - URL atual:', window.location.href);
    console.log('🚀 DOM CARREGADO - Aguardando 800ms antes de executar carregarAtividadesNaPagina');
    
    setTimeout(() => {
        console.log('⏰ TIMEOUT EXECUTADO - Chamando carregarAtividadesNaPagina após 800ms');
        carregarAtividadesNaPagina();
    }, 800);
});

