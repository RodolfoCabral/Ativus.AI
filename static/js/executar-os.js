// Variáveis globais
let ordemServico = null;
let execucaoAtual = null;
let materiaisEstoque = [];
let materiaisUtilizados = [];
let materialCounter = 0;

// Inicialização da página
document.addEventListener('DOMContentLoaded', function() {
    console.log('Página de execução de OS carregada');
    
    // Obter ID da OS da URL
    const urlParams = new URLSearchParams(window.location.search);
    const osId = urlParams.get('id');
    
    if (osId) {
        carregarOS(osId);
    } else {
        alert('ID da Ordem de Serviço não encontrado!');
        voltarProgramacao();
    }
    
    // Configurar event listeners
    configurarEventListeners();
});

// Configurar event listeners
function configurarEventListeners() {
    // Status de execução
    document.querySelectorAll('.status-option').forEach(option => {
        option.addEventListener('click', function() {
            const status = this.dataset.status;
            selecionarStatus(status);
        });
    });
    
    // Data e hora atual para início
    const agora = new Date();
    agora.setMinutes(agora.getMinutes() - agora.getTimezoneOffset());
    document.getElementById('data-inicio').value = agora.toISOString().slice(0, 16);
}

// Carregar dados da OS
async function carregarOS(osId) {
    try {
        console.log('Carregando OS:', osId);
        
        const response = await fetch(`/api/ordens-servico/${osId}`, {
            credentials: 'include'
        });
        if (response.ok) {
            const data = await response.json();
            ordemServico = data.ordem_servico;
            
            preencherDadosOS();
            await carregarExecucaoExistente();
            await carregarMateriaisEstoque();
            
        } else {
            throw new Error('Erro ao carregar ordem de serviço');
        }
    } catch (error) {
        console.error('Erro ao carregar OS:', error);
        alert('Erro ao carregar ordem de serviço. Tente novamente.');
        voltarProgramacao();
    }
}

// Preencher dados da OS na interface
function preencherDadosOS() {
    if (!ordemServico) return;
    
    document.getElementById('os-id').value = ordemServico.id;
    document.getElementById('os-numero').textContent = ordemServico.id;
    document.getElementById('os-descricao').textContent = ordemServico.descricao;
    document.getElementById('os-tipo').textContent = formatarTipoManutencao(ordemServico.tipo_manutencao);
    document.getElementById('os-oficina').textContent = formatarOficina(ordemServico.oficina);
    document.getElementById('os-equipamento').textContent = 
        `${ordemServico.equipamento_tag} - ${ordemServico.equipamento_descricao}`;
    document.getElementById('os-localizacao').textContent = 
        `${ordemServico.filial_tag} / ${ordemServico.setor_tag}`;
    
    // Status
    const statusElement = document.getElementById('os-status');
    statusElement.textContent = formatarStatus(ordemServico.status);
    statusElement.className = `status-badge status-${ordemServico.status.replace('_', '-')}`;
    
    // Prioridade
    const prioridadeElement = document.getElementById('os-prioridade');
    prioridadeElement.textContent = formatarPrioridade(ordemServico.prioridade);
    prioridadeElement.className = `prioridade-badge prioridade-${ordemServico.prioridade}`;
    
    // Descrição da atividade
    document.getElementById('atividade-descricao').textContent = ordemServico.descricao;
}

// Carregar execução existente (se houver)
async function carregarExecucaoExistente() {
    try {
        const response = await fetch(`/api/execucoes-os/por-os/${ordemServico.id}`, {
            credentials: 'include'
        });
        if (response.ok) {
            const data = await response.json();
            if (data.execucao) {
                execucaoAtual = data.execucao;
                preencherDadosExecucao();
            }
        }
    } catch (error) {
        console.error('Erro ao carregar execução:', error);
    }
}

// Preencher dados da execução existente
function preencherDadosExecucao() {
    if (!execucaoAtual) return;
    
    if (execucaoAtual.data_inicio) {
        const dataInicio = new Date(execucaoAtual.data_inicio);
        dataInicio.setMinutes(dataInicio.getMinutes() - dataInicio.getTimezoneOffset());
        document.getElementById('data-inicio').value = dataInicio.toISOString().slice(0, 16);
    }
    
    if (execucaoAtual.data_fim) {
        const dataFim = new Date(execucaoAtual.data_fim);
        dataFim.setMinutes(dataFim.getMinutes() - dataFim.getTimezoneOffset());
        document.getElementById('data-fim').value = dataFim.toISOString().slice(0, 16);
    }
    
    if (execucaoAtual.observacoes) {
        document.getElementById('observacoes').value = execucaoAtual.observacoes;
    }
    
    selecionarStatus(execucaoAtual.lista_execucao_status);
    
    // Carregar materiais utilizados
    carregarMateriaisUtilizados();
}

// Carregar materiais de estoque
async function carregarMateriaisEstoque() {
    try {
        const response = await fetch('/api/materiais-estoque', {
            credentials: 'include'
        });
        if (response.ok) {
            const data = await response.json();
            materiaisEstoque = data.materiais || [];
            console.log('Materiais de estoque carregados:', materiaisEstoque.length);
        }
    } catch (error) {
        console.error('Erro ao carregar materiais de estoque:', error);
    }
}

// Carregar materiais utilizados
async function carregarMateriaisUtilizados() {
    if (!execucaoAtual) return;
    
    try {
        const response = await fetch(`/api/materiais-utilizados/por-execucao/${execucaoAtual.id}`, {
            credentials: 'include'
        });
        if (response.ok) {
            const data = await response.json();
            materiaisUtilizados = data.materiais || [];
            
            // Renderizar materiais existentes
            materiaisUtilizados.forEach(material => {
                adicionarMaterialExistente(material);
            });
        }
    } catch (error) {
        console.error('Erro ao carregar materiais utilizados:', error);
    }
}

// Selecionar status de execução
function selecionarStatus(status) {
    document.querySelectorAll('.status-option').forEach(option => {
        option.classList.remove('conforme', 'nao-conforme');
        if (option.dataset.status === status) {
            option.classList.add(status === 'C' ? 'conforme' : 'nao-conforme');
        }
    });
    
    document.getElementById('lista-execucao-status').value = status;
}

// Adicionar material
function adicionarMaterial() {
    materialCounter++;
    const materialId = `material-${materialCounter}`;
    
    const materialHtml = `
        <div class="material-item" id="${materialId}">
            <div class="material-header">
                <strong>Material #${materialCounter}</strong>
                <button type="button" class="btn-remove-material" onclick="removerMaterial('${materialId}')">
                    <i class="fas fa-trash"></i>
                    Remover
                </button>
            </div>
            
            <div class="material-type-toggle">
                <div class="type-option active" data-type="estoque" onclick="selecionarTipoMaterial('${materialId}', 'estoque')">
                    Material de Estoque
                </div>
                <div class="type-option" data-type="avulso" onclick="selecionarTipoMaterial('${materialId}', 'avulso')">
                    Material Avulso
                </div>
            </div>
            
            <div class="material-fields">
                <!-- Campos para material de estoque -->
                <div class="estoque-fields">
                    <div class="form-row">
                        <div class="form-group">
                            <label class="form-label">Material de Estoque *</label>
                            <select class="form-control material-estoque-select" onchange="selecionarMaterialEstoque('${materialId}')">
                                <option value="">Selecione um material</option>
                                ${materiaisEstoque.map(m => `<option value="${m.id}" data-valor="${m.valor_unitario}" data-unidade="${m.unidade}">${m.nome} (${m.unidade})</option>`).join('')}
                            </select>
                        </div>
                        <div class="form-group">
                            <label class="form-label">Quantidade *</label>
                            <input type="number" class="form-control quantidade-input" min="0" step="0.01" value="1" onchange="calcularValorTotal('${materialId}')">
                        </div>
                    </div>
                </div>
                
                <!-- Campos para material avulso -->
                <div class="avulso-fields" style="display: none;">
                    <div class="form-row">
                        <div class="form-group">
                            <label class="form-label">Nome do Material *</label>
                            <input type="text" class="form-control nome-material-input" placeholder="Digite o nome do material">
                        </div>
                        <div class="form-group">
                            <label class="form-label">Valor Unitário *</label>
                            <input type="number" class="form-control valor-unitario-input" min="0" step="0.01" placeholder="0,00" onchange="calcularValorTotal('${materialId}')">
                        </div>
                    </div>
                    <div class="form-row">
                        <div class="form-group">
                            <label class="form-label">Quantidade *</label>
                            <input type="number" class="form-control quantidade-input" min="0" step="0.01" value="1" onchange="calcularValorTotal('${materialId}')">
                        </div>
                        <div class="form-group">
                            <label class="form-label">Valor Total</label>
                            <div class="valor-display valor-total-display">R$ 0,00</div>
                        </div>
                    </div>
                </div>
                
                <!-- Valor total para estoque -->
                <div class="estoque-total" style="margin-top: 12px;">
                    <label class="form-label">Valor Total</label>
                    <div class="valor-display valor-total-display">R$ 0,00</div>
                </div>
            </div>
        </div>
    `;
    
    document.getElementById('materiais-container').insertAdjacentHTML('beforeend', materialHtml);
}

// Adicionar material existente
function adicionarMaterialExistente(material) {
    materialCounter++;
    const materialId = `material-${materialCounter}`;
    
    const isEstoque = material.tipo_material === 'estoque';
    
    const materialHtml = `
        <div class="material-item" id="${materialId}" data-material-id="${material.id}">
            <div class="material-header">
                <strong>${material.nome_material}</strong>
                <button type="button" class="btn-remove-material" onclick="removerMaterial('${materialId}')">
                    <i class="fas fa-trash"></i>
                    Remover
                </button>
            </div>
            
            <div class="material-type-toggle">
                <div class="type-option ${isEstoque ? 'active' : ''}" data-type="estoque" onclick="selecionarTipoMaterial('${materialId}', 'estoque')">
                    Material de Estoque
                </div>
                <div class="type-option ${!isEstoque ? 'active' : ''}" data-type="avulso" onclick="selecionarTipoMaterial('${materialId}', 'avulso')">
                    Material Avulso
                </div>
            </div>
            
            <div class="material-fields">
                <!-- Campos preenchidos com dados existentes -->
                <div class="estoque-fields" style="display: ${isEstoque ? 'block' : 'none'};">
                    <div class="form-row">
                        <div class="form-group">
                            <label class="form-label">Material de Estoque *</label>
                            <select class="form-control material-estoque-select" onchange="selecionarMaterialEstoque('${materialId}')">
                                <option value="">Selecione um material</option>
                                ${materiaisEstoque.map(m => `<option value="${m.id}" data-valor="${m.valor_unitario}" data-unidade="${m.unidade}" ${m.id == material.material_estoque_id ? 'selected' : ''}>${m.nome} (${m.unidade})</option>`).join('')}
                            </select>
                        </div>
                        <div class="form-group">
                            <label class="form-label">Quantidade *</label>
                            <input type="number" class="form-control quantidade-input" min="0" step="0.01" value="${material.quantidade}" onchange="calcularValorTotal('${materialId}')">
                        </div>
                    </div>
                </div>
                
                <div class="avulso-fields" style="display: ${!isEstoque ? 'block' : 'none'};">
                    <div class="form-row">
                        <div class="form-group">
                            <label class="form-label">Nome do Material *</label>
                            <input type="text" class="form-control nome-material-input" value="${material.nome_material || ''}" placeholder="Digite o nome do material">
                        </div>
                        <div class="form-group">
                            <label class="form-label">Valor Unitário *</label>
                            <input type="number" class="form-control valor-unitario-input" min="0" step="0.01" value="${material.valor_unitario || 0}" placeholder="0,00" onchange="calcularValorTotal('${materialId}')">
                        </div>
                    </div>
                    <div class="form-row">
                        <div class="form-group">
                            <label class="form-label">Quantidade *</label>
                            <input type="number" class="form-control quantidade-input" min="0" step="0.01" value="${material.quantidade}" onchange="calcularValorTotal('${materialId}')">
                        </div>
                        <div class="form-group">
                            <label class="form-label">Valor Total</label>
                            <div class="valor-display valor-total-display">R$ ${material.valor_total.toFixed(2).replace('.', ',')}</div>
                        </div>
                    </div>
                </div>
                
                <div class="estoque-total" style="margin-top: 12px; display: ${isEstoque ? 'block' : 'none'};">
                    <label class="form-label">Valor Total</label>
                    <div class="valor-display valor-total-display">R$ ${material.valor_total.toFixed(2).replace('.', ',')}</div>
                </div>
            </div>
        </div>
    `;
    
    document.getElementById('materiais-container').insertAdjacentHTML('beforeend', materialHtml);
}

// Selecionar tipo de material
function selecionarTipoMaterial(materialId, tipo) {
    const materialItem = document.getElementById(materialId);
    
    // Atualizar botões
    materialItem.querySelectorAll('.type-option').forEach(option => {
        option.classList.remove('active');
        if (option.dataset.type === tipo) {
            option.classList.add('active');
        }
    });
    
    // Mostrar/esconder campos
    const estoqueFields = materialItem.querySelector('.estoque-fields');
    const avulsoFields = materialItem.querySelector('.avulso-fields');
    const estoqueTotal = materialItem.querySelector('.estoque-total');
    
    if (tipo === 'estoque') {
        estoqueFields.style.display = 'block';
        avulsoFields.style.display = 'none';
        estoqueTotal.style.display = 'block';
    } else {
        estoqueFields.style.display = 'none';
        avulsoFields.style.display = 'block';
        estoqueTotal.style.display = 'none';
    }
    
    calcularValorTotal(materialId);
}

// Selecionar material de estoque
function selecionarMaterialEstoque(materialId) {
    const materialItem = document.getElementById(materialId);
    const select = materialItem.querySelector('.material-estoque-select');
    const selectedOption = select.options[select.selectedIndex];
    
    if (selectedOption.value) {
        const valorUnitario = parseFloat(selectedOption.dataset.valor) || 0;
        calcularValorTotal(materialId);
    }
}

// Calcular valor total do material
function calcularValorTotal(materialId) {
    const materialItem = document.getElementById(materialId);
    const tipoAtivo = materialItem.querySelector('.type-option.active').dataset.type;
    
    let valorUnitario = 0;
    let quantidade = 0;
    
    if (tipoAtivo === 'estoque') {
        const select = materialItem.querySelector('.material-estoque-select');
        const selectedOption = select.options[select.selectedIndex];
        valorUnitario = parseFloat(selectedOption.dataset.valor) || 0;
        quantidade = parseFloat(materialItem.querySelector('.quantidade-input').value) || 0;
    } else {
        valorUnitario = parseFloat(materialItem.querySelector('.valor-unitario-input').value) || 0;
        quantidade = parseFloat(materialItem.querySelector('.quantidade-input').value) || 0;
    }
    
    const valorTotal = valorUnitario * quantidade;
    
    // Atualizar display do valor total
    const valorDisplay = materialItem.querySelector('.valor-total-display');
    valorDisplay.textContent = `R$ ${valorTotal.toFixed(2).replace('.', ',')}`;
}

// Remover material
function removerMaterial(materialId) {
    const materialItem = document.getElementById(materialId);
    if (materialItem) {
        materialItem.remove();
    }
}

// Salvar execução
async function salvarExecucao() {
    try {
        const dadosExecucao = coletarDadosExecucao();
        
        const response = await fetch('/api/execucoes-os', {
            method: execucaoAtual ? 'PUT' : 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            credentials: 'include',
            body: JSON.stringify(dadosExecucao)
        });
        
        if (response.ok) {
            const data = await response.json();
            execucaoAtual = data.execucao;
            
            // Salvar materiais
            await salvarMateriais();
            
            showNotification('Execução salva com sucesso!', 'success');
        } else {
            throw new Error('Erro ao salvar execução');
        }
    } catch (error) {
        console.error('Erro ao salvar execução:', error);
        showNotification('Erro ao salvar execução. Tente novamente.', 'error');
    }
}

// Encerrar OS
async function encerrarOS() {
    if (!confirm('Tem certeza que deseja encerrar esta Ordem de Serviço? Esta ação não pode ser desfeita.')) {
        return;
    }
    
    try {
        // Preencher data de fim se não estiver preenchida
        const dataFimInput = document.getElementById('data-fim');
        if (!dataFimInput.value) {
            const agora = new Date();
            agora.setMinutes(agora.getMinutes() - agora.getTimezoneOffset());
            dataFimInput.value = agora.toISOString().slice(0, 16);
        }
        
        // Salvar execução primeiro
        await salvarExecucao();
        
        // Encerrar OS
        const response = await fetch(`/api/ordens-servico/${ordemServico.id}/encerrar`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            credentials: 'include'
        });
        
        if (response.ok) {
            showNotification('Ordem de Serviço encerrada com sucesso!', 'success');
            
            // Notificar outras abas sobre a mudança de status
            if (window.notificarMudancaStatusOS) {
                window.notificarMudancaStatusOS(ordemServico.id, 'concluida');
            }
            
            // Também usar localStorage para sincronização
            localStorage.setItem('os_status_updated', JSON.stringify({
                osId: ordemServico.id,
                novoStatus: 'concluida',
                timestamp: Date.now()
            }));
            
            setTimeout(() => {
                voltarProgramacao();
            }, 2000);
        } else {
            throw new Error('Erro ao encerrar OS');
        }
    } catch (error) {
        console.error('Erro ao encerrar OS:', error);
        showNotification('Erro ao encerrar OS. Tente novamente.', 'error');
    }
}

// Coletar dados da execução
function coletarDadosExecucao() {
    const dados = {
        os_id: parseInt(document.getElementById('os-id').value),
        data_inicio: document.getElementById('data-inicio').value || null,
        data_fim: document.getElementById('data-fim').value || null,
        lista_execucao_status: document.getElementById('lista-execucao-status').value,
        observacoes: document.getElementById('observacoes').value || null
    };
    
    if (execucaoAtual) {
        dados.id = execucaoAtual.id;
    }
    
    return dados;
}

// Salvar materiais utilizados
async function salvarMateriais() {
    const materiaisContainer = document.getElementById('materiais-container');
    const materiaisItems = materiaisContainer.querySelectorAll('.material-item');
    
    for (const item of materiaisItems) {
        const materialData = coletarDadosMaterial(item);
        if (materialData) {
            try {
                const materialId = item.dataset.materialId;
                const method = materialId ? 'PUT' : 'POST';
                const url = materialId ? `/api/materiais-utilizados/${materialId}` : '/api/materiais-utilizados';
                
                if (materialId) {
                    materialData.id = parseInt(materialId);
                }
                
                const response = await fetch(url, {
                    method: method,
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    credentials: 'include',
                    body: JSON.stringify(materialData)
                });
                
                if (!response.ok) {
                    throw new Error('Erro ao salvar material');
                }
            } catch (error) {
                console.error('Erro ao salvar material:', error);
            }
        }
    }
}

// Coletar dados de um material
function coletarDadosMaterial(materialItem) {
    const tipoAtivo = materialItem.querySelector('.type-option.active').dataset.type;
    const quantidade = parseFloat(materialItem.querySelector('.quantidade-input').value) || 0;
    
    if (quantidade <= 0) return null;
    
    const dados = {
        execucao_id: execucaoAtual.id,
        tipo_material: tipoAtivo,
        quantidade: quantidade
    };
    
    if (tipoAtivo === 'estoque') {
        const select = materialItem.querySelector('.material-estoque-select');
        const materialEstoqueId = parseInt(select.value);
        const selectedOption = select.options[select.selectedIndex];
        
        if (!materialEstoqueId) return null;
        
        dados.material_estoque_id = materialEstoqueId;
        dados.valor_unitario = parseFloat(selectedOption.dataset.valor) || 0;
    } else {
        const nomeMaterial = materialItem.querySelector('.nome-material-input').value.trim();
        const valorUnitario = parseFloat(materialItem.querySelector('.valor-unitario-input').value) || 0;
        
        if (!nomeMaterial || valorUnitario <= 0) return null;
        
        dados.nome_material = nomeMaterial;
        dados.valor_unitario = valorUnitario;
    }
    
    dados.valor_total = dados.quantidade * dados.valor_unitario;
    
    return dados;
}

// Voltar para programação
function voltarProgramacao() {
    window.location.href = '/programacao';
}

// Funções de formatação
function formatarTipoManutencao(tipo) {
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

function formatarOficina(oficina) {
    const oficinas = {
        'mecanica': 'Mecânica',
        'eletrica': 'Elétrica',
        'automacao': 'Automação',
        'eletromecanico': 'Eletromecânico',
        'operacional': 'Operacional'
    };
    return oficinas[oficina] || oficina;
}

function formatarStatus(status) {
    const statuses = {
        'aberta': 'Aberta',
        'programada': 'Programada',
        'em_andamento': 'Em Andamento',
        'concluida': 'Concluída',
        'cancelada': 'Cancelada'
    };
    return statuses[status] || status;
}

function formatarPrioridade(prioridade) {
    const prioridades = {
        'baixa': 'Baixa',
        'media': 'Média',
        'alta': 'Alta',
        'seguranca': 'Segurança',
        'preventiva': 'Preventiva'
    };
    return prioridades[prioridade] || prioridade;
}

// Função de notificação (reutilizada de outros arquivos)
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

