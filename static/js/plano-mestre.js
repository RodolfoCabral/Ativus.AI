// Plano Mestre - JavaScript
document.addEventListener('DOMContentLoaded', function() {
    console.log('🔧 Plano Mestre carregado');
    
    // Inicializar funcionalidades
    inicializarTabs();
    carregarDadosEquipamento();
    carregarAtividades();
    
    // Sidebar toggle
    const sidebarToggle = document.querySelector('.sidebar-toggle');
    const sidebar = document.querySelector('.sidebar');
    
    if (sidebarToggle) {
        sidebarToggle.addEventListener('click', function() {
            sidebar.classList.toggle('collapsed');
        });
    }
});

// Carregar dados do equipamento selecionado
function carregarDadosEquipamento() {
    const equipamentoSelecionado = localStorage.getItem('equipamentoSelecionado');
    
    if (equipamentoSelecionado) {
        const equipamento = JSON.parse(equipamentoSelecionado);
        
        // Atualizar informações do equipamento no header
        document.getElementById('equipamento-tag').textContent = equipamento.tag || 'TAG-001';
        document.getElementById('equipamento-desc').textContent = equipamento.descricao || 'Equipamento';
        
        console.log('📋 Dados do equipamento carregados:', equipamento);
    } else {
        // Dados padrão se não houver equipamento selecionado
        console.log('⚠️ Nenhum equipamento selecionado, usando dados padrão');
    }
}

// Array para armazenar atividades
let atividades = [];
let atividadeEditando = null;

// Inicializar sistema de tabs
function inicializarTabs() {
    const tabs = document.querySelectorAll('.nav-tab');
    const contents = document.querySelectorAll('.tab-content');
    
    tabs.forEach(tab => {
        tab.addEventListener('click', function() {
            const targetTab = this.getAttribute('data-tab');
            
            // Remover active de todas as tabs
            tabs.forEach(t => t.classList.remove('active'));
            contents.forEach(c => c.classList.remove('active'));
            
            // Adicionar active na tab clicada
            this.classList.add('active');
            document.getElementById(targetTab).classList.add('active');
        });
    });
}

// Abrir modal para adicionar/editar atividade
function abrirModalAtividade(atividade = null) {
    const modal = document.getElementById('modalAtividade');
    const title = document.querySelector('.modal-title');
    
    if (atividade) {
        // Modo edição
        title.textContent = 'Editar Item Plano Mestre';
        atividadeEditando = atividade;
        preencherFormulario(atividade);
    } else {
        // Modo criação
        title.textContent = 'Item Plano Mestre';
        atividadeEditando = null;
        limparFormulario();
    }
    
    modal.classList.add('show');
    document.body.style.overflow = 'hidden';
}

// Fechar modal
function fecharModalAtividade() {
    const modal = document.getElementById('modalAtividade');
    modal.classList.remove('show');
    document.body.style.overflow = 'auto';
    limparFormulario();
    atividadeEditando = null;
}

// Preencher formulário com dados da atividade
function preencherFormulario(atividade) {
    document.getElementById('descricao').value = atividade.descricao || '';
    document.getElementById('oficina').value = atividade.oficina || '';
    document.getElementById('tipoManutencao').value = atividade.tipo_manutencao || '';
    document.getElementById('frequencia').value = atividade.frequencia || '';
    document.getElementById('conjunto').value = atividade.conjunto || '';
    document.getElementById('pontoControle').value = atividade.ponto_controle || '';
    document.getElementById('valorFrequencia').value = atividade.valor_frequencia || '';
    document.getElementById('condicao').value = atividade.condicao || '';
    document.getElementById('statusAtivo').checked = atividade.status_ativo !== false;
}

// Limpar formulário
function limparFormulario() {
    document.getElementById('formAtividade').reset();
    document.getElementById('statusAtivo').checked = true;
}

// Salvar atividade no banco de dados via API
async function salvarAtividade() {
    const form = document.getElementById('formAtividade');
    
    // Validar campos obrigatórios
    const descricao = document.getElementById('descricao').value.trim();
    if (!descricao) {
        alert('Por favor, preencha a descrição da atividade.');
        return;
    }
    
    try {
        // Obter ID do equipamento
        const equipamentoSelecionado = localStorage.getItem('equipamentoSelecionado');
        if (!equipamentoSelecionado) {
            alert('Nenhum equipamento selecionado.');
            return;
        }
        
        const equipamento = JSON.parse(equipamentoSelecionado);
        const equipamentoId = equipamento.id;
        
        // Coletar dados do formulário
        const dadosAtividade = {
            descricao: descricao,
            oficina: document.getElementById('oficina').value,
            tipo_manutencao: document.getElementById('tipoManutencao').value,
            frequencia: document.getElementById('frequencia').value,
            conjunto: document.getElementById('conjunto').value,
            ponto_controle: document.getElementById('pontoControle').value,
            valor_frequencia: parseInt(document.getElementById('valorFrequencia').value) || null,
            condicao: document.getElementById('condicao').value,
            status_ativo: document.getElementById('statusAtivo').checked
        };
        
        let response;
        let method;
        let url;
        
        if (atividadeEditando) {
            // Atualizar atividade existente
            method = 'PUT';
            url = `/api/plano-mestre/atividade/${atividadeEditando.id}`;
        } else {
            // Criar nova atividade
            method = 'POST';
            url = `/api/plano-mestre/equipamento/${equipamentoId}/atividades`;
        }
        
        response = await fetch(url, {
            method: method,
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(dadosAtividade)
        });
        
        if (!response.ok) {
            if (response.status === 401) {
                alert('Erro de autenticação. Faça login novamente.');
                return;
            }
            const errorData = await response.json();
            throw new Error(errorData.error || 'Erro ao salvar atividade');
        }
        
        const atividadeSalva = await response.json();
        console.log('✅ Atividade salva no banco:', atividadeSalva);
        
        // Recarregar atividades do banco
        await carregarAtividades();
        
        // Fechar modal
        fecharModalAtividade();
        
        // Mostrar feedback
        mostrarFeedback(atividadeEditando ? 'Atividade atualizada com sucesso!' : 'Atividade adicionada com sucesso!');
        
    } catch (error) {
        console.error('❌ Erro ao salvar atividade:', error);
        alert(`Erro ao salvar atividade: ${error.message}`);
    }
}

// Carregar atividades do banco de dados via API
async function carregarAtividades() {
    try {
        console.log('📋 Carregando atividades do banco de dados...');
        
        const equipamentoSelecionado = localStorage.getItem('equipamentoSelecionado');
        if (!equipamentoSelecionado) {
            console.log('⚠️ Nenhum equipamento selecionado');
            renderizarAtividades();
            return;
        }
        
        const equipamento = JSON.parse(equipamentoSelecionado);
        const equipamentoId = equipamento.id;
        
        const response = await fetch(`/api/plano-mestre/equipamento/${equipamentoId}`, {
            method: 'GET',
            headers: {
                'Content-Type': 'application/json'
            }
        });
        
        if (!response.ok) {
            if (response.status === 401) {
                console.log('❌ Erro de autenticação. Usando dados locais como fallback.');
                carregarAtividadesLocal();
                return;
            }
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        const data = await response.json();
        atividades = data.atividades || [];
        
        console.log('✅ Atividades carregadas do banco:', atividades.length);
        renderizarAtividades();
        
    } catch (error) {
        console.error('❌ Erro ao carregar atividades:', error);
        mostrarFeedback('Erro ao carregar atividades. Usando dados locais como fallback.', 'error');
        carregarAtividadesLocal();
    }
}

// Fallback para carregar atividades do localStorage
function carregarAtividadesLocal() {
    const atividadesSalvas = localStorage.getItem('planoMestreAtividades');
    if (atividadesSalvas) {
        atividades = JSON.parse(atividadesSalvas);
        console.log('📋 Atividades carregadas do localStorage:', atividades.length);
    } else {
        atividades = [];
    }
    renderizarAtividades();
}

// Renderizar lista de atividades
function renderizarAtividades() {
    const container = document.getElementById('atividades-container');
    
    if (atividades.length === 0) {
        container.innerHTML = `
            <div class="empty-state">
                <i class="fas fa-clipboard-list"></i>
                <h3>Nenhuma atividade cadastrada</h3>
                <p>Clique em "Adicionar Atividade" para começar a criar seu plano mestre</p>
            </div>
        `;
        return;
    }
    
    let html = '';
    atividades.forEach((atividade, index) => {
        // Mapear campos do banco de dados
        const statusClass = atividade.status_ativo ? 'status-funcionando' : 'status-parado';
        const statusText = atividade.status_ativo ? 'Funcionando' : 'Parado';
        const concluida = atividade.concluida || false;
        
        html += `
            <div class="atividade-item ${concluida ? 'atividade-concluida' : ''}">
                <div>
                    <input type="checkbox" class="checkbox-custom" 
                           ${concluida ? 'checked' : ''} 
                           onchange="toggleAtividade(${atividade.id})">
                </div>
                <div>${atividade.descricao}</div>
                <div>${formatarTexto(atividade.oficina)}</div>
                <div>${formatarFrequencia(atividade.frequencia, atividade.ponto_controle)}</div>
                <div>${formatarTexto(atividade.tipo_manutencao)}</div>
                <div>
                    <span class="status-badge ${statusClass}">${statusText}</span>
                </div>
                <div>${atividade.valor_frequencia || '-'}</div>
                <div>${formatarTexto(atividade.condicao)}</div>
                <div class="acoes-btns">
                    <button class="btn-acao btn-copiar" onclick="copiarAtividade(${atividade.id})" title="Copiar">
                        <i class="fas fa-copy"></i>
                    </button>
                    <button class="btn-acao btn-editar" onclick="editarAtividade(${atividade.id})" title="Editar">
                        <i class="fas fa-edit"></i>
                    </button>
                    <button class="btn-acao btn-excluir" onclick="excluirAtividade(${atividade.id})" title="Excluir">
                        <i class="fas fa-trash"></i>
                    </button>
                </div>
            </div>
        `;
    });
    
    container.innerHTML = html;
}

// Formatar texto para exibição
function formatarTexto(texto) {
    if (!texto) return '-';
    
    // Converter de kebab-case para texto legível
    return texto
        .replace(/-/g, ' ')
        .replace(/\b\w/g, l => l.toUpperCase());
}

// Formatar frequência e ponto de controle
function formatarFrequencia(frequencia, pontoControle) {
    const freq = formatarTexto(frequencia);
    const ponto = formatarTexto(pontoControle);
    
    if (freq === '-' && ponto === '-') return '-';
    if (freq === '-') return ponto;
    if (ponto === '-') return freq;
    
    return `${freq}`;
}

// Toggle status da atividade via API
async function toggleAtividade(id) {
    try {
        const atividade = atividades.find(a => a.id === id);
        if (!atividade) {
            console.log('⚠️ Atividade não encontrada:', id);
            return;
        }
        
        const novoStatus = !atividade.concluida;
        
        const response = await fetch(`/api/plano-mestre/atividade/${id}/toggle`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                concluida: novoStatus,
                observacoes: novoStatus ? 'Marcada como concluída via interface' : null
            })
        });
        
        if (!response.ok) {
            if (response.status === 401) {
                alert('Erro de autenticação. Faça login novamente.');
                return;
            }
            const errorData = await response.json();
            throw new Error(errorData.error || 'Erro ao alterar status da atividade');
        }
        
        const atividadeAtualizada = await response.json();
        console.log('🔄 Status da atividade alterado:', atividadeAtualizada);
        
        // Recarregar atividades do banco
        await carregarAtividades();
        
        mostrarFeedback(novoStatus ? 'Atividade marcada como concluída!' : 'Atividade desmarcada!');
        
    } catch (error) {
        console.error('❌ Erro ao alterar status da atividade:', error);
        alert(`Erro ao alterar status: ${error.message}`);
    }
}

// Copiar atividade via API
async function copiarAtividade(id) {
    try {
        const response = await fetch(`/api/plano-mestre/atividade/${id}/copiar`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            }
        });
        
        if (!response.ok) {
            if (response.status === 401) {
                alert('Erro de autenticação. Faça login novamente.');
                return;
            }
            const errorData = await response.json();
            throw new Error(errorData.error || 'Erro ao copiar atividade');
        }
        
        const atividadeCopiada = await response.json();
        console.log('📋 Atividade copiada:', atividadeCopiada);
        
        // Recarregar atividades do banco
        await carregarAtividades();
        
        mostrarFeedback('Atividade copiada com sucesso!');
        
    } catch (error) {
        console.error('❌ Erro ao copiar atividade:', error);
        alert(`Erro ao copiar atividade: ${error.message}`);
    }
}

// Editar atividade
function editarAtividade(id) {
    const atividade = atividades.find(a => a.id === id);
    if (atividade) {
        abrirModalAtividade(atividade);
        console.log('✏️ Editando atividade:', atividade);
    }
}

// Excluir atividade via API
async function excluirAtividade(id) {
    const atividade = atividades.find(a => a.id === id);
    if (!atividade) {
        alert('Atividade não encontrada.');
        return;
    }
    
    if (!confirm(`Tem certeza que deseja excluir a atividade "${atividade.descricao}"?`)) {
        return;
    }
    
    try {
        const response = await fetch(`/api/plano-mestre/atividade/${id}`, {
            method: 'DELETE',
            headers: {
                'Content-Type': 'application/json'
            }
        });
        
        if (!response.ok) {
            if (response.status === 401) {
                alert('Erro de autenticação. Faça login novamente.');
                return;
            }
            const errorData = await response.json();
            throw new Error(errorData.error || 'Erro ao excluir atividade');
        }
        
        console.log('🗑️ Atividade excluída:', id);
        
        // Recarregar atividades do banco
        await carregarAtividades();
        
        mostrarFeedback('Atividade excluída com sucesso!');
        
    } catch (error) {
        console.error('❌ Erro ao excluir atividade:', error);
        alert(`Erro ao excluir atividade: ${error.message}`);
    }
}

// Mostrar feedback ao usuário
function mostrarFeedback(mensagem, tipo = 'success') {
    // Criar elemento de feedback
    const feedback = document.createElement('div');
    feedback.style.cssText = `
        position: fixed;
        top: 20px;
        right: 20px;
        background: ${tipo === 'success' ? '#28a745' : '#dc3545'};
        color: white;
        padding: 12px 20px;
        border-radius: 6px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.2);
        z-index: 10000;
        font-size: 14px;
        font-weight: 500;
        animation: slideInRight 0.3s ease;
    `;
    feedback.textContent = mensagem;
    
    // Adicionar CSS da animação
    if (!document.getElementById('feedback-styles')) {
        const style = document.createElement('style');
        style.id = 'feedback-styles';
        style.textContent = `
            @keyframes slideInRight {
                from { transform: translateX(100%); opacity: 0; }
                to { transform: translateX(0); opacity: 1; }
            }
            @keyframes slideOutRight {
                from { transform: translateX(0); opacity: 1; }
                to { transform: translateX(100%); opacity: 0; }
            }
        `;
        document.head.appendChild(style);
    }
    
    document.body.appendChild(feedback);
    
    // Remover após 3 segundos
    setTimeout(() => {
        feedback.style.animation = 'slideOutRight 0.3s ease';
        setTimeout(() => {
            if (feedback.parentNode) {
                feedback.parentNode.removeChild(feedback);
            }
        }, 300);
    }, 3000);
}

// Fechar modal ao clicar fora
document.addEventListener('click', function(e) {
    const modal = document.getElementById('modalAtividade');
    if (e.target === modal) {
        fecharModalAtividade();
    }
});

// Fechar modal com ESC
document.addEventListener('keydown', function(e) {
    if (e.key === 'Escape') {
        fecharModalAtividade();
    }
});

// Sistema agora usa apenas dados do banco de dados - sem dados de exemplo

