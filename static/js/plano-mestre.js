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
    document.getElementById('tipoManutencao').value = atividade.tipoManutencao || '';
    document.getElementById('frequencia').value = atividade.frequencia || '';
    document.getElementById('conjunto').value = atividade.conjunto || '';
    document.getElementById('pontoControle').value = atividade.pontoControle || '';
    document.getElementById('valorFrequencia').value = atividade.valorFrequencia || '';
    document.getElementById('condicao').value = atividade.condicao || '';
    document.getElementById('statusAtivo').checked = atividade.status === 'funcionando';
}

// Limpar formulário
function limparFormulario() {
    document.getElementById('formAtividade').reset();
    document.getElementById('statusAtivo').checked = true;
}

// Salvar atividade
function salvarAtividade() {
    const form = document.getElementById('formAtividade');
    
    // Validar campos obrigatórios
    const descricao = document.getElementById('descricao').value.trim();
    if (!descricao) {
        alert('Por favor, preencha a descrição da atividade.');
        return;
    }
    
    // Coletar dados do formulário
    const atividade = {
        id: atividadeEditando ? atividadeEditando.id : Date.now(),
        descricao: descricao,
        oficina: document.getElementById('oficina').value,
        tipoManutencao: document.getElementById('tipoManutencao').value,
        frequencia: document.getElementById('frequencia').value,
        conjunto: document.getElementById('conjunto').value,
        pontoControle: document.getElementById('pontoControle').value,
        valorFrequencia: document.getElementById('valorFrequencia').value,
        condicao: document.getElementById('condicao').value,
        status: document.getElementById('statusAtivo').checked ? 'funcionando' : 'parado',
        dataCriacao: atividadeEditando ? atividadeEditando.dataCriacao : new Date().toISOString()
    };
    
    if (atividadeEditando) {
        // Atualizar atividade existente
        const index = atividades.findIndex(a => a.id === atividadeEditando.id);
        if (index !== -1) {
            atividades[index] = atividade;
        }
        console.log('✅ Atividade atualizada:', atividade);
    } else {
        // Adicionar nova atividade
        atividades.push(atividade);
        console.log('✅ Nova atividade adicionada:', atividade);
    }
    
    // Salvar no localStorage
    localStorage.setItem('planoMestreAtividades', JSON.stringify(atividades));
    
    // Atualizar lista
    renderizarAtividades();
    
    // Fechar modal
    fecharModalAtividade();
    
    // Mostrar feedback
    mostrarFeedback(atividadeEditando ? 'Atividade atualizada com sucesso!' : 'Atividade adicionada com sucesso!');
}

// Carregar atividades do localStorage
function carregarAtividades() {
    const atividadesSalvas = localStorage.getItem('planoMestreAtividades');
    if (atividadesSalvas) {
        atividades = JSON.parse(atividadesSalvas);
        console.log('📋 Atividades carregadas:', atividades.length);
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
        const statusClass = atividade.status === 'funcionando' ? 'status-funcionando' : 'status-parado';
        const statusText = atividade.status === 'funcionando' ? 'Funcionando' : 'Parado';
        
        html += `
            <div class="atividade-item">
                <div>
                    <input type="checkbox" class="checkbox-custom" onchange="toggleAtividade(${atividade.id})">
                </div>
                <div>${atividade.descricao}</div>
                <div>${formatarTexto(atividade.oficina)}</div>
                <div>${formatarFrequencia(atividade.frequencia, atividade.pontoControle)}</div>
                <div>${formatarTexto(atividade.tipoManutencao)}</div>
                <div>
                    <span class="status-badge ${statusClass}">${statusText}</span>
                </div>
                <div>${atividade.valorFrequencia || '-'}</div>
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

// Toggle status da atividade
function toggleAtividade(id) {
    console.log('🔄 Toggle atividade:', id);
    // Implementar lógica de toggle se necessário
}

// Copiar atividade
function copiarAtividade(id) {
    const atividade = atividades.find(a => a.id === id);
    if (atividade) {
        const novaAtividade = {
            ...atividade,
            id: Date.now(),
            descricao: `${atividade.descricao} (Cópia)`,
            dataCriacao: new Date().toISOString()
        };
        
        atividades.push(novaAtividade);
        localStorage.setItem('planoMestreAtividades', JSON.stringify(atividades));
        renderizarAtividades();
        
        mostrarFeedback('Atividade copiada com sucesso!');
        console.log('📋 Atividade copiada:', novaAtividade);
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

// Excluir atividade
function excluirAtividade(id) {
    const atividade = atividades.find(a => a.id === id);
    if (atividade && confirm(`Tem certeza que deseja excluir a atividade "${atividade.descricao}"?`)) {
        atividades = atividades.filter(a => a.id !== id);
        localStorage.setItem('planoMestreAtividades', JSON.stringify(atividades));
        renderizarAtividades();
        
        mostrarFeedback('Atividade excluída com sucesso!');
        console.log('🗑️ Atividade excluída:', id);
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

// Dados de exemplo para demonstração (remover em produção)
function adicionarDadosExemplo() {
    if (atividades.length === 0) {
        const exemplos = [
            {
                id: 1,
                descricao: 'Teste de isolamento elétrico',
                oficina: 'eletrica',
                tipoManutencao: 'preventiva-periodica',
                frequencia: 'trimestral',
                conjunto: 'conjunto-motoredutor',
                pontoControle: 'medicao',
                valorFrequencia: '90',
                condicao: 'funcionando',
                status: 'funcionando',
                dataCriacao: new Date().toISOString()
            },
            {
                id: 2,
                descricao: 'teste geração',
                oficina: 'mecanica',
                tipoManutencao: 'preventiva-periodica',
                frequencia: 'mensal',
                conjunto: '',
                pontoControle: 'visual',
                valorFrequencia: '30',
                condicao: 'funcionando',
                status: 'funcionando',
                dataCriacao: new Date().toISOString()
            },
            {
                id: 3,
                descricao: 'Teste valor',
                oficina: 'mecanica',
                tipoManutencao: 'preventiva-periodica',
                frequencia: 'mensal',
                conjunto: '',
                pontoControle: 'visual',
                valorFrequencia: '30',
                condicao: 'parado',
                status: 'parado',
                dataCriacao: new Date().toISOString()
            }
        ];
        
        atividades = exemplos;
        localStorage.setItem('planoMestreAtividades', JSON.stringify(atividades));
        renderizarAtividades();
        console.log('📋 Dados de exemplo adicionados');
    }
}

// Adicionar dados de exemplo na primeira carga (para demonstração)
setTimeout(() => {
    adicionarDadosExemplo();
}, 1000);

