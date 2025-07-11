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
    try {
        await Promise.all([
            carregarChamados(),
            carregarEstatisticas(),
            carregarFiliais()
        ]);
        
        aplicarFiltros();
        
    } catch (error) {
        console.error('Erro ao carregar dados:', error);
        mostrarErro('Erro ao carregar dados dos chamados');
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
    const filtroPrioridade = document.getElementById('filtro-prioridade').value;
    const filtroFilial = document.getElementById('filtro-filial').value;
    
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
    
    renderizarChamados();
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

