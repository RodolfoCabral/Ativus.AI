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
    const descDiv = document.getElementById('atividade-descricao');
    if (!descDiv) return;
    // obter os id da URL
    const urlParams = new URLSearchParams(window.location.search);
    const osId = urlParams.get('id') || urlParams.get('os_id');
    if (!osId) return;
    descDiv.innerHTML = '<div class="text-muted">Carregando atividades...</div>';
    fetch(`/api/os/${osId}/atividades`, { credentials: 'include' })
        .then(r => {
            if (!r.ok) throw new Error('Falha ao carregar atividades');
            return r.json();
        })
        .then(data => {
            if (!Array.isArray(data.atividades)) {
                descDiv.innerHTML = '<div class="text-danger">Nenhuma atividade encontrada.</div>';
                return;
            }
            if (data.atividades.length === 0) {
                descDiv.innerHTML = '<div class="text-muted">Nenhuma atividade vinculada a esta OS.</div>';
                return;
            }
            // construir HTML
            let html = '<div class="atividades-list">';
            data.atividades.forEach((atividade, idx) => {
                const status = atividade.status || '';
                html += `
                    <div class="atividade-item mb-2 p-2 border rounded" data-atividade-id="${atividade.id}">
                        <div><strong>${atividade.ordem || (idx+1)}.</strong> ${atividade.descricao}</div>
                        <div class="mt-2 d-flex gap-2 align-items-center">
                            <label class="btn btn-sm btn-outline-success ${status==='conforme' ? 'active' : ''}"><input type="radio" name="status_${atividade.id}" value="conforme" ${status==='conforme'?'checked':''}> C</label>
                            <label class="btn btn-sm btn-outline-danger ${status==='nao_conforme' ? 'active' : ''}"><input type="radio" name="status_${atividade.id}" value="nao_conforme" ${status==='nao_conforme'?'checked':''}> NC</label>
                            <label class="btn btn-sm btn-outline-secondary ${status==='nao_aplicavel' ? 'active' : ''}"><input type="radio" name="status_${atividade.id}" value="nao_aplicavel" ${status==='nao_aplicavel'?'checked':''}> NA</label>
                            <textarea class="form-control form-control-sm ms-2 observacao-text" placeholder="Observação" rows="1">${atividade.observacao || ''}</textarea>
                        </div>
                    </div>
                `;
            });
            html += '</div>';
            descDiv.innerHTML = html;

            // adicionar listeners para salvar
            descDiv.querySelectorAll('.atividade-item').forEach(item => {
                const atividadeId = item.dataset.atividadeId;
                const radios = item.querySelectorAll(`input[type="radio"][name="status_${atividadeId}"]`);
                const textarea = item.querySelector('.observacao-text');
                radios.forEach(r => r.addEventListener('change', () => {
                    const status = r.value;
                    const obs = textarea.value;
                    fetch(`/api/os/atividades/${atividadeId}/avaliar`, {
                        method: 'PUT',
                        credentials: 'include',
                        headers: {'Content-Type':'application/json'},
                        body: JSON.stringify({status: status, observacao: obs})
                    }).then(res => {
                        if (!res.ok) throw new Error('Erro ao salvar');
                        console.log('Salvo', atividadeId, status);
                    }).catch(err => console.error(err));
                }));
                textarea.addEventListener('blur', () => {
                    const checked = item.querySelector(`input[type="radio"][name="status_${atividadeId}"]:checked`);
                    const status = checked ? checked.value : null;
                    const obs = textarea.value;
                    fetch(`/api/os/atividades/${atividadeId}/avaliar`, {
                        method: 'PUT',
                        credentials: 'include',
                        headers: {'Content-Type':'application/json'},
                        body: JSON.stringify({status: status, observacao: obs})
                    }).then(res => {
                        if (!res.ok) throw new Error('Erro ao salvar obs');
                        console.log('Obs salva', atividadeId);
                    }).catch(err => console.error(err));
                });
            });
        })
        .catch(err => {
            console.error(err);
            descDiv.innerHTML = '<div class="text-danger">Erro ao carregar atividades.</div>';
        });
}

// Tentar carregar in-page ao carregar o DOM
document.addEventListener('DOMContentLoaded', function() {
    setTimeout(carregarAtividadesNaPagina, 800);
});

