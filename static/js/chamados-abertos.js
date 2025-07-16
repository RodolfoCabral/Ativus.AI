// Variáveis globais
let chamados = [];
let chamadosFiltrados = [];
let estatisticas = {};

// Inicialização da página
document.addEventListener('DOMContentLoaded', function() {
    console.log('Página de chamados em aberto carregada');
    carregarDados();
});

// Carregar dados
async function carregarDados() {
    console.log('Iniciando carregamento de dados...');
    
    try {
        // Mostrar indicador de carregamento
        mostrarCarregando();
        
        await Promise.all([
            carregarChamados(),
            carregarEstatisticas(),
            carregarFiliais()
        ]);
        
        console.log('Dados carregados com sucesso');
        aplicarFiltros();
        
        // Esconder indicador de carregamento
        esconderCarregando();
        
    } catch (error) {
        console.error('Erro ao carregar dados:', error);
        esconderCarregando();
        mostrarErro('Erro ao carregar dados dos chamados. Tente recarregar a página.');
    }
}

// Carregar chamados em aberto
async function carregarChamados() {
    try {
        const response = await fetch('/api/chamados?status=abertos');
        if (response.ok) {
            const data = await response.json();
            chamados = data.chamados || [];
            console.log('Chamados carregados:', chamados.length);
        } else {
            throw new Error('Erro ao carregar chamados');
        }
    } catch (error) {
        console.error('Erro ao carregar chamados:', error);
        throw error;
    }
}

// Carregar estatísticas
async function carregarEstatisticas() {
    try {
        const response = await fetch('/api/chamados/estatisticas');
        if (response.ok) {
            const data = await response.json();
            estatisticas = data.estatisticas || {};
            atualizarEstatisticas();
        } else {
            throw new Error('Erro ao carregar estatísticas');
        }
    } catch (error) {
        console.error('Erro ao carregar estatísticas:', error);
        // Não interrompe o carregamento se as estatísticas falharem
    }
}

// Carregar filiais para filtro
async function carregarFiliais() {
    try {
        const response = await fetch('/api/filiais');
        if (response.ok) {
            const data = await response.json();
            const filiais = data.filiais || [];
            
            const selectFilial = document.getElementById('filtro-filial');
            filiais.forEach(filial => {
                const option = document.createElement('option');
                option.value = filial.id;
                option.textContent = `${filial.tag} - ${filial.descricao}`;
                selectFilial.appendChild(option);
            });
        }
    } catch (error) {
        console.error('Erro ao carregar filiais:', error);
    }
}

// Atualizar estatísticas na interface
function atualizarEstatisticas() {
    document.getElementById('total-abertos').textContent = 
        (estatisticas.abertos || 0) + (estatisticas.em_andamento || 0);
    document.getElementById('alta-prioridade').textContent = estatisticas.alta_prioridade || 0;
    document.getElementById('seguranca').textContent = estatisticas.seguranca || 0;
}

// Aplicar filtros
function aplicarFiltros() {
    try {
        console.log('Aplicando filtros...');
        
        const filtroPrioridade = document.getElementById('filtro-prioridade')?.value || '';
        const filtroFilial = document.getElementById('filtro-filial')?.value || '';
        
        console.log('Filtros:', { prioridade: filtroPrioridade, filial: filtroFilial });
        console.log('Total de chamados:', chamados.length);
        
        chamadosFiltrados = chamados.filter(chamado => {
            // Filtrar apenas chamados abertos ou em andamento
            if (!['aberto', 'em_andamento'].includes(chamado.status)) {
                return false;
            }
            
            // Filtro de prioridade
            if (filtroPrioridade && chamado.prioridade !== filtroPrioridade) {
                return false;
            }
            
            // Filtro de filial
            if (filtroFilial && chamado.filial_id.toString() !== filtroFilial) {
                return false;
            }
            
            return true;
        });
        
        console.log('Chamados filtrados:', chamadosFiltrados.length);
        renderizarChamados();
        
    } catch (error) {
        console.error('Erro ao aplicar filtros:', error);
        mostrarErro('Erro ao filtrar chamados. Tente recarregar a página.');
    }
}

// Renderizar chamados na interface
function renderizarChamados() {
    const container = document.getElementById('chamados-grid');
    
    if (chamadosFiltrados.length === 0) {
        container.innerHTML = `
            <div class="empty-state">
                <i class="fas fa-inbox"></i>
                <h3>Nenhum chamado encontrado</h3>
                <p>Não há chamados em aberto que correspondam aos filtros selecionados.</p>
            </div>
        `;
        return;
    }
    
    // Ordenar por prioridade e data
    const prioridadeOrdem = { 'seguranca': 4, 'alta': 3, 'media': 2, 'baixa': 1 };
    chamadosFiltrados.sort((a, b) => {
        const prioridadeA = prioridadeOrdem[a.prioridade] || 0;
        const prioridadeB = prioridadeOrdem[b.prioridade] || 0;
        
        if (prioridadeA !== prioridadeB) {
            return prioridadeB - prioridadeA; // Maior prioridade primeiro
        }
        
        // Se mesma prioridade, ordenar por data (mais recente primeiro)
        return new Date(b.data_criacao) - new Date(a.data_criacao);
    });
    
    container.innerHTML = chamadosFiltrados.map(chamado => criarCardChamado(chamado)).join('');
    
    // Adicionar event listeners para botões de conversão em OS
    adicionarEventListenersConverterOS();
}

// Criar card de chamado
function criarCardChamado(chamado) {
    const dataFormatada = formatarData(chamado.data_criacao);
    const prioridadeClass = `prioridade-${chamado.prioridade}`;
    const prioridadeTexto = {
        'baixa': 'Baixa',
        'media': 'Média',
        'alta': 'Alta',
        'seguranca': 'Segurança'
    }[chamado.prioridade] || chamado.prioridade;
    
    return `
        <div class="chamado-card">
            <div class="chamado-header">
                <div class="chamado-id">Chamado #${chamado.id}</div>
                <div class="chamado-prioridade ${prioridadeClass}">${prioridadeTexto}</div>
            </div>
            
            <div class="chamado-descricao">
                ${chamado.descricao}
            </div>
            
            <div class="chamado-info">
                <div class="info-item">
                    <i class="fas fa-building"></i>
                    <span>${chamado.filial_tag} - ${chamado.filial_descricao}</span>
                </div>
                <div class="info-item">
                    <i class="fas fa-layer-group"></i>
                    <span>${chamado.setor_tag} - ${chamado.setor_descricao}</span>
                </div>
                <div class="info-item">
                    <i class="fas fa-cog"></i>
                    <span>${chamado.equipamento_tag} - ${chamado.equipamento_descricao}</span>
                </div>
                <div class="info-item">
                    <i class="fas fa-info-circle"></i>
                    <span>Status: ${formatarStatus(chamado.status)}</span>
                </div>
            </div>
            
            <div class="chamado-actions">
                <button class="btn-converter-os" 
                        data-chamado-id="${chamado.id}"
                        data-chamado-descricao="${chamado.descricao.replace(/"/g, '&quot;')}"
                        data-chamado-prioridade="${chamado.prioridade}"
                        data-filial-id="${chamado.filial_id}"
                        data-setor-id="${chamado.setor_id}"
                        data-equipamento-id="${chamado.equipamento_id}">
                    <i class="fas fa-tools"></i>
                    Converter em OS
                </button>
            </div>
            
            <div class="chamado-footer">
                <div class="chamado-solicitante">
                    <i class="fas fa-user"></i> ${chamado.solicitante}
                </div>
                <div class="chamado-data">${dataFormatada}</div>
            </div>
        </div>
    `;
}

// Formatar data
function formatarData(dataString) {
    const data = new Date(dataString);
    return data.toLocaleString('pt-BR', {
        day: '2-digit',
        month: '2-digit',
        year: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
    });
}

// Formatar status
function formatarStatus(status) {
    const statusMap = {
        'aberto': 'Aberto',
        'em_andamento': 'Em Andamento',
        'resolvido': 'Resolvido',
        'fechado': 'Fechado'
    };
    return statusMap[status] || status;
}

// Mostrar erro
function mostrarErro(mensagem) {
    const container = document.getElementById('chamados-grid');
    container.innerHTML = `
        <div class="empty-state">
            <i class="fas fa-exclamation-triangle" style="color: #dc3545;"></i>
            <h3>Erro ao carregar dados</h3>
            <p>${mensagem}</p>
            <button class="btn-primary" onclick="carregarDados()">
                <i class="fas fa-redo"></i> Tentar Novamente
            </button>
        </div>
    `;
}



// Variáveis para conversão em OS
let filiaisOS = [];
let setoresOS = [];
let equipamentosOS = [];
let chamadoSelecionado = null;

// Adicionar event listeners para botões de conversão em OS
function adicionarEventListenersConverterOS() {
    const botoes = document.querySelectorAll('.btn-converter-os');
    botoes.forEach(botao => {
        botao.addEventListener('click', function() {
            const chamadoData = {
                id: this.dataset.chamadoId,
                descricao: this.dataset.chamadoDescricao,
                prioridade: this.dataset.chamadoPrioridade,
                filial_id: this.dataset.filialId,
                setor_id: this.dataset.setorId,
                equipamento_id: this.dataset.equipamentoId
            };
            abrirModalConverterOS(chamadoData);
        });
    });
}

// Função para abrir modal de conversão em OS
function abrirModalConverterOS(chamado) {
    console.log('Abrindo modal para chamado:', chamado);
    chamadoSelecionado = chamado;
    
    // Verificar se o modal existe
    const modal = document.getElementById('converter-os-modal');
    if (!modal) {
        console.error('Modal converter-os-modal não encontrado!');
        alert('Erro: Modal não encontrado. Verifique se a página foi carregada corretamente.');
        return;
    }
    
    console.log('Modal encontrado:', modal);
    
    // Preencher dados do chamado
    const chamadoIdField = document.getElementById('chamado-id');
    const descricaoField = document.getElementById('os-descricao');
    const prioridadeField = document.getElementById('prioridade-os');
    
    if (chamadoIdField) {
        chamadoIdField.value = chamado.id;
        console.log('Chamado ID preenchido:', chamado.id);
    }
    if (descricaoField) {
        descricaoField.value = chamado.descricao;
        console.log('Descrição preenchida:', chamado.descricao);
    }
    if (prioridadeField) {
        prioridadeField.value = chamado.prioridade;
        console.log('Prioridade preenchida:', chamado.prioridade);
    }
    
    // Carregar dados para os selects
    carregarDadosOS();
    
    // Mostrar modal com múltiplas tentativas
    modal.style.display = 'flex';
    modal.style.visibility = 'visible';
    modal.style.opacity = '1';
    
    // Forçar reflow
    modal.offsetHeight;
    
    console.log('Modal exibido - display:', modal.style.display);
    console.log('Modal exibido - visibility:', modal.style.visibility);
    
    // Verificação adicional após um pequeno delay
    setTimeout(() => {
        const computedStyle = window.getComputedStyle(modal);
        console.log('Computed display:', computedStyle.display);
        console.log('Computed visibility:', computedStyle.visibility);
    }, 100);
}

// Fechar modal de conversão em OS
function fecharModalConverterOS() {
    document.getElementById('converter-os-modal').style.display = 'none';
    document.getElementById('converter-os-form').reset();
    chamadoSelecionado = null;
}

// Carregar dados para o formulário de OS
async function carregarDadosOS() {
    try {
        // Carregar filiais
        await carregarFiliaisOS();
        
        // Se há um chamado selecionado, pré-selecionar os dados
        if (chamadoSelecionado) {
            // Selecionar filial
            document.getElementById('filial-os').value = chamadoSelecionado.filial_id;
            
            // Carregar setores da filial
            await carregarSetoresOS();
            
            // Selecionar setor
            document.getElementById('setor-os').value = chamadoSelecionado.setor_id;
            
            // Carregar equipamentos do setor
            await carregarEquipamentosOS();
            
            // Selecionar equipamento
            document.getElementById('equipamento-os').value = chamadoSelecionado.equipamento_id;
        }
        
    } catch (error) {
        console.error('Erro ao carregar dados para OS:', error);
        showNotification('Erro ao carregar dados', 'error');
    }
}

// Carregar filiais para OS
async function carregarFiliaisOS() {
    try {
        const response = await fetch('/api/filiais');
        if (response.ok) {
            const data = await response.json();
            filiaisOS = data.filiais || [];
            
            const select = document.getElementById('filial-os');
            select.innerHTML = '<option value="">Selecione uma filial</option>';
            
            filiaisOS.forEach(filial => {
                const option = document.createElement('option');
                option.value = filial.id;
                option.textContent = `${filial.tag} - ${filial.descricao}`;
                select.appendChild(option);
            });
        }
    } catch (error) {
        console.error('Erro ao carregar filiais:', error);
    }
}

// Carregar setores para OS
async function carregarSetoresOS() {
    const filialId = document.getElementById('filial-os').value;
    const setorSelect = document.getElementById('setor-os');
    const equipamentoSelect = document.getElementById('equipamento-os');
    
    // Limpar selects dependentes
    setorSelect.innerHTML = '<option value="">Carregando setores...</option>';
    equipamentoSelect.innerHTML = '<option value="">Selecione um setor primeiro</option>';
    
    if (!filialId) {
        setorSelect.innerHTML = '<option value="">Selecione uma filial primeiro</option>';
        return;
    }
    
    try {
        const response = await fetch(`/api/setores?filial_id=${filialId}`);
        if (response.ok) {
            const data = await response.json();
            setoresOS = data.setores || [];
            
            setorSelect.innerHTML = '<option value="">Selecione um setor</option>';
            
            setoresOS.forEach(setor => {
                const option = document.createElement('option');
                option.value = setor.id;
                option.textContent = `${setor.tag} - ${setor.descricao}`;
                setorSelect.appendChild(option);
            });
        }
    } catch (error) {
        console.error('Erro ao carregar setores:', error);
        setorSelect.innerHTML = '<option value="">Erro ao carregar setores</option>';
    }
}

// Carregar equipamentos para OS
async function carregarEquipamentosOS() {
    const setorId = document.getElementById('setor-os').value;
    const equipamentoSelect = document.getElementById('equipamento-os');
    
    equipamentoSelect.innerHTML = '<option value="">Carregando equipamentos...</option>';
    
    if (!setorId) {
        equipamentoSelect.innerHTML = '<option value="">Selecione um setor primeiro</option>';
        return;
    }
    
    try {
        const response = await fetch(`/api/equipamentos?setor_id=${setorId}`);
        if (response.ok) {
            const data = await response.json();
            equipamentosOS = data.equipamentos || [];
            
            equipamentoSelect.innerHTML = '<option value="">Selecione um equipamento</option>';
            
            equipamentosOS.forEach(equipamento => {
                const option = document.createElement('option');
                option.value = equipamento.id;
                option.textContent = `${equipamento.tag} - ${equipamento.descricao}`;
                equipamentoSelect.appendChild(option);
            });
        }
    } catch (error) {
        console.error('Erro ao carregar equipamentos:', error);
        equipamentoSelect.innerHTML = '<option value="">Erro ao carregar equipamentos</option>';
    }
}

// Calcular HH (Homem-Hora)
function calcularHH() {
    const qtdPessoas = parseFloat(document.getElementById('qtd-pessoas').value) || 0;
    const horas = parseFloat(document.getElementById('horas').value) || 0;
    const hh = qtdPessoas * horas;
    
    document.getElementById('hh-display').textContent = hh.toFixed(1);
}

// Salvar ordem de serviço
async function salvarOrdemServico() {
    try {
        const form = document.getElementById('converter-os-form');
        const formData = new FormData(form);
        
        // Validar campos obrigatórios
        const requiredFields = ['descricao', 'tipo_manutencao', 'oficina', 'condicao_ativo', 'prioridade', 'qtd_pessoas', 'horas', 'filial_id', 'setor_id', 'equipamento_id'];
        
        for (const field of requiredFields) {
            if (!formData.get(field)) {
                showNotification('Por favor, preencha todos os campos obrigatórios', 'error');
                return;
            }
        }
        
        // Calcular HH
        const qtdPessoas = parseFloat(formData.get('qtd_pessoas'));
        const horas = parseFloat(formData.get('horas'));
        const hh = qtdPessoas * horas;
        
        // Preparar dados para envio
        const osData = {
            chamado_id: parseInt(formData.get('chamado_id')),
            descricao: formData.get('descricao'),
            tipo_manutencao: formData.get('tipo_manutencao'),
            oficina: formData.get('oficina'),
            condicao_ativo: formData.get('condicao_ativo'),
            qtd_pessoas: qtdPessoas,
            horas: horas,
            hh: hh,
            prioridade: formData.get('prioridade'),
            filial_id: parseInt(formData.get('filial_id')),
            setor_id: parseInt(formData.get('setor_id')),
            equipamento_id: parseInt(formData.get('equipamento_id'))
        };
        
        // Enviar dados
        const response = await fetch('/api/ordens-servico', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(osData)
        });
        
        if (response.ok) {
            const result = await response.json();
            showNotification('Ordem de Serviço criada com sucesso!', 'success');
            fecharModalConverterOS();
            
            // Recarregar chamados para atualizar a lista
            await carregarDados();
        } else {
            const error = await response.json();
            showNotification(error.error || 'Erro ao criar Ordem de Serviço', 'error');
        }
        
    } catch (error) {
        console.error('Erro ao salvar OS:', error);
        showNotification('Erro interno do servidor', 'error');
    }
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


// Funções de feedback visual
function mostrarCarregando() {
    const container = document.getElementById('chamados-grid');
    if (container) {
        container.innerHTML = `
            <div class="loading-state">
                <div class="loading-spinner"></div>
                <p>Carregando chamados...</p>
            </div>
        `;
    }
    
    // Adicionar estilos de carregamento se não existirem
    if (!document.getElementById('loading-styles')) {
        const styles = document.createElement('style');
        styles.id = 'loading-styles';
        styles.textContent = `
            .loading-state {
                display: flex;
                flex-direction: column;
                align-items: center;
                justify-content: center;
                padding: 60px 20px;
                color: #666;
            }
            .loading-spinner {
                width: 40px;
                height: 40px;
                border: 4px solid #f3f3f3;
                border-top: 4px solid #007bff;
                border-radius: 50%;
                animation: spin 1s linear infinite;
                margin-bottom: 16px;
            }
            @keyframes spin {
                0% { transform: rotate(0deg); }
                100% { transform: rotate(360deg); }
            }
            .error-state {
                display: flex;
                flex-direction: column;
                align-items: center;
                justify-content: center;
                padding: 60px 20px;
                color: #dc3545;
                text-align: center;
            }
            .error-state i {
                font-size: 48px;
                margin-bottom: 16px;
                opacity: 0.7;
            }
            .error-state h3 {
                margin: 0 0 8px 0;
                font-size: 18px;
            }
            .error-state p {
                margin: 0 0 20px 0;
                opacity: 0.8;
            }
            .btn-retry {
                background: #007bff;
                color: white;
                border: none;
                padding: 10px 20px;
                border-radius: 6px;
                cursor: pointer;
                font-size: 14px;
                display: flex;
                align-items: center;
                gap: 8px;
            }
            .btn-retry:hover {
                background: #0056b3;
            }
        `;
        document.head.appendChild(styles);
    }
}

function esconderCarregando() {
    // A função renderizarChamados já substitui o conteúdo do container
    console.log('Carregamento concluído');
}

function mostrarErro(mensagem) {
    const container = document.getElementById('chamados-grid');
    if (container) {
        container.innerHTML = `
            <div class="error-state">
                <i class="fas fa-exclamation-triangle"></i>
                <h3>Erro ao carregar chamados</h3>
                <p>${mensagem}</p>
                <button class="btn-retry" onclick="carregarDados()">
                    <i class="fas fa-redo"></i> Tentar Novamente
                </button>
            </div>
        `;
    }
    
    // Também mostrar notificação
    showNotification(mensagem, 'error');
}

