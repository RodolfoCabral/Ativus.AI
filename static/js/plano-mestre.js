// Plano Mestre - JavaScript
// Variáveis globais
let equipamentoAtual = null;
let atividades = [];
let atividadeEditando = null;

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
        equipamentoAtual = JSON.parse(equipamentoSelecionado);
        
        // Atualizar informações do equipamento no header
        document.getElementById('equipamento-tag').textContent = equipamentoAtual.tag || 'TAG-001';
        document.getElementById('equipamento-desc').textContent = equipamentoAtual.descricao || 'Equipamento';
        
        console.log('📋 Dados do equipamento carregados:', equipamentoAtual);
    } else {
        // Dados padrão se não houver equipamento selecionado
        console.log('⚠️ Nenhum equipamento selecionado, usando dados padrão');
        equipamentoAtual = null;
    }
}

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


// Abrir sistema PMP
function abrirSistemaPMP() {
    if (!equipamentoAtual) {
        alert('Nenhum equipamento selecionado');
        return;
    }
    
    // Redirecionar para o sistema PMP com o equipamento atual
    window.location.href = `/pmp-sistema?equipamento=${equipamentoAtual.id}`;
}



// ========================================
// FUNCIONALIDADES PMP INTEGRADAS
// ========================================

// Variáveis globais para PMP
let pmpsAtual = [];
let pmpSelecionada = null;

// Gerar PMPs integrado na aba
async function gerarPMPsIntegrado() {
    if (!equipamentoAtual) {
        alert('Nenhum equipamento selecionado');
        return;
    }
    
    console.log('🔄 Gerando PMPs para equipamento:', equipamentoAtual.id);
    
    try {
        // Mostrar loading
        mostrarLoadingPMP();
        
        // Chamar API para gerar PMPs
        const response = await fetch(`/api/pmp/equipamento/${equipamentoAtual.id}/gerar`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            }
        });
        
        if (!response.ok) {
            throw new Error(`Erro HTTP: ${response.status}`);
        }
        
        const resultado = await response.json();
        console.log('✅ Resposta da API:', resultado);
        
        // Verificar se a resposta tem o formato correto
        let pmps;
        if (resultado.success && resultado.pmps) {
            // Formato: {success: true, message: "...", pmps: [...]}
            pmps = resultado.pmps;
        } else if (Array.isArray(resultado)) {
            // Formato: [...]
            pmps = resultado;
        } else {
            throw new Error('Formato de resposta inválido da API');
        }
        
        console.log('✅ PMPs extraídas:', pmps);
        
        // Verificar se pmps é um array
        if (!Array.isArray(pmps)) {
            throw new Error('PMPs retornadas não são um array');
        }
        
        // Atualizar interface
        pmpsAtual = pmps;
        renderizarPMPsIntegradas(pmps);
        
        // Atualizar informações do equipamento na sidebar PMP
        atualizarInfoEquipamentoPMP();
        
    } catch (error) {
        console.error('❌ Erro ao gerar PMPs:', error);
        alert('Erro ao gerar PMPs: ' + error.message);
        esconderLoadingPMP();
    }
}

// Mostrar loading na área de PMPs
function mostrarLoadingPMP() {
    const container = document.getElementById('pmps-lista-integrated');
    container.innerHTML = `
        <div class="loading-pmp">
            <i class="fas fa-spinner fa-spin"></i>
            <p>Gerando PMPs...</p>
        </div>
    `;
}

// Esconder loading na área de PMPs
function esconderLoadingPMP() {
    const container = document.getElementById('pmps-lista-integrated');
    container.innerHTML = `
        <div class="empty-state-pmp">
            <i class="fas fa-clipboard-list"></i>
            <h4>Nenhuma PMP gerada</h4>
            <p>Clique em "Gerar PMPs" para criar os procedimentos</p>
        </div>
    `;
}

// Renderizar lista de PMPs na sidebar integrada
function renderizarPMPsIntegradas(pmps) {
    const container = document.getElementById('pmps-lista-integrated');
    
    if (!pmps || pmps.length === 0) {
        container.innerHTML = `
            <div class="empty-state-pmp">
                <i class="fas fa-clipboard-list"></i>
                <h4>Nenhuma PMP encontrada</h4>
                <p>As atividades não puderam ser agrupadas em PMPs</p>
            </div>
        `;
        return;
    }
    
    let html = '';
    pmps.forEach((pmp, index) => {
        html += `
            <div class="pmp-item-integrated ${index === 0 ? 'active' : ''}" 
                 onclick="selecionarPMPIntegrada(${pmp.id}, this)">
                <div class="pmp-codigo">${pmp.codigo}</div>
                <div class="pmp-descricao-item">${pmp.descricao}</div>
                <div class="pmp-detalhes-item">
                    <span>${pmp.atividades_count || 0} atividades</span>
                    <span class="status-badge status-ativo">Ativo</span>
                </div>
            </div>
        `;
    });
    
    container.innerHTML = html;
    
    // Selecionar primeira PMP automaticamente
    if (pmps.length > 0) {
        selecionarPMPIntegrada(pmps[0].id, container.querySelector('.pmp-item-integrated'));
    }
}

// Selecionar uma PMP específica
async function selecionarPMPIntegrada(pmpId, elemento) {
    // Remover seleção anterior
    document.querySelectorAll('.pmp-item-integrated').forEach(item => {
        item.classList.remove('active');
    });
    
    // Adicionar seleção atual
    if (elemento) {
        elemento.classList.add('active');
    } else {
        // Se elemento não foi fornecido, encontrar e selecionar o elemento correto
        const pmpElement = document.querySelector(`[onclick*="selecionarPMPIntegrada(${pmpId}"]`);
        if (pmpElement) {
            pmpElement.classList.add('active');
        }
    }
    
    console.log('📋 Selecionando PMP:', pmpId);
    
    try {
        // SEMPRE buscar dados atualizados do servidor
        console.log('🔄 Buscando dados atualizados da PMP do servidor...');
        const response = await fetch(`/api/pmp/${pmpId}`);
        if (!response.ok) {
            throw new Error(`Erro HTTP: ${response.status}`);
        }
        
        const pmp = await response.json();
        console.log('✅ Detalhes da PMP carregados do servidor:', pmp);
        
        // Atualizar variável global com dados frescos do servidor
        pmpSelecionada = pmp;
        
        // Renderizar formulário com dados atualizados
        renderizarFormularioPMP(pmp);
        
    } catch (error) {
        console.error('❌ Erro ao carregar PMP:', error);
        alert('Erro ao carregar detalhes da PMP: ' + error.message);
    }
}

// Renderizar formulário da PMP selecionada
function renderizarFormularioPMP(pmp) {
    const container = document.getElementById('pmp-form-integrated');
    const titleDisplay = document.getElementById('pmp-title-display');
    
    // Atualizar título
    titleDisplay.textContent = pmp.codigo + ' - ' + pmp.descricao;
    
    // Renderizar formulário baseado na imagem fornecida
    container.innerHTML = `
        <div class="pmp-form-content">
            <!-- Seção: Descrição da O.S. -->
            <div class="pmp-form-section full-width">
                <div class="pmp-form-section-title">Descrição da O.S.</div>
                <input type="text" class="pmp-form-control" 
                       value="${pmp.descricao}" readonly>
            </div>
            
            <!-- Seção: Informações Básicas -->
            <div class="pmp-form-section">
                <div class="pmp-form-section-title">Informações Básicas</div>
                <div class="pmp-form-row">
                    <div class="pmp-form-group">
                        <label class="pmp-form-label">Tipo</label>
                        <input type="text" class="pmp-form-control" 
                               value="${pmp.tipo || 'Preventiva Periódica'}" readonly>
                    </div>
                    <div class="pmp-form-group">
                        <label class="pmp-form-label">Oficina</label>
                        <input type="text" class="pmp-form-control" 
                               value="${pmp.oficina || 'Mecânica'}" readonly>
                    </div>
                </div>
                <div class="pmp-form-row">
                    <div class="pmp-form-group">
                        <label class="pmp-form-label">Frequência</label>
                        <input type="text" class="pmp-form-control" 
                               value="${pmp.frequencia || 'Mensal'}" readonly>
                    </div>
                    <div class="pmp-form-group">
                        <label class="pmp-form-label">Condição</label>
                        <input type="text" class="pmp-form-control" 
                               value="${pmp.condicao || 'Funcionando'}" readonly>
                    </div>
                </div>
            </div>
            
            <!-- Seção: Configurações -->
            <div class="pmp-form-section">
                <div class="pmp-form-section-title">Configurações</div>
                <div class="pmp-form-row">
                    <div class="pmp-form-group">
                        <label class="pmp-form-label">Nº de pessoas para execução</label>
                        <input type="number" class="pmp-form-control" id="pmp-num-pessoas" 
                               value="${pmp.num_pessoas || 1}" min="1">
                    </div>
                    <div class="pmp-form-group">
                        <label class="pmp-form-label">Nº de dias para antecipar a geração de O.S.</label>
                        <input type="number" class="pmp-form-control" id="pmp-dias-antecipacao" 
                               value="${pmp.dias_antecipacao || 0}" min="0">
                    </div>
                </div>
                <div class="pmp-form-row">
                    <div class="pmp-form-group">
                        <label class="pmp-form-label">Tempo por pessoa (em horas decimais)</label>
                        <input type="number" class="pmp-form-control" id="pmp-tempo-pessoa" 
                               value="${pmp.tempo_pessoa || 1.0}" step="0.1" min="0">
                    </div>
                    <div class="pmp-form-group">
                        <label class="pmp-form-label">Forma de impressão da O.S.</label>
                        <select class="pmp-form-control" id="pmp-forma-impressao">
                            <option value="comum" ${(pmp.forma_impressao || 'comum') === 'comum' ? 'selected' : ''}>Comum</option>
                            <option value="detalhada" ${pmp.forma_impressao === 'detalhada' ? 'selected' : ''}>Detalhada</option>
                            <option value="resumida" ${pmp.forma_impressao === 'resumida' ? 'selected' : ''}>Resumida</option>
                        </select>
                    </div>
                </div>
            </div>
        </div>
        
        <!-- Seção: Atividades da PMP -->
        <div class="pmp-atividades-section">
            <div class="pmp-atividades-header">
                Atividades incluídas nesta PMP (${pmp.atividades ? pmp.atividades.length : 0})
            </div>
            <div class="pmp-atividades-lista">
                ${renderizarAtividadesPMP(pmp.atividades || [])}
            </div>
        </div>
        
        <!-- Botão Salvar -->
        <div style="text-align: right; margin-top: 20px;">
            <button class="btn-gerar-pmps" onclick="salvarAlteracoesPMP()">
                <i class="fas fa-save"></i>
                Salvar Alterações
            </button>
        </div>
    `;
}

// Renderizar lista de atividades da PMP
function renderizarAtividadesPMP(atividades) {
    if (!atividades || atividades.length === 0) {
        return `
            <div class="pmp-atividade-item">
                <div class="pmp-atividade-desc">Nenhuma atividade encontrada</div>
            </div>
        `;
    }
    
    return atividades.map(atividade => `
        <div class="pmp-atividade-item">
            <div class="pmp-atividade-desc">${atividade.descricao}</div>
            <div class="pmp-atividade-detalhes">
                ${atividade.oficina} • ${atividade.frequencia} • ${atividade.tipo_manutencao}
            </div>
        </div>
    `).join('');
}

// Atualizar informações do equipamento na sidebar PMP
function atualizarInfoEquipamentoPMP() {
    if (equipamentoAtual) {
        document.getElementById('equipamento-tag-pmp').textContent = equipamentoAtual.tag || '-';
        document.getElementById('equipamento-desc-pmp').textContent = equipamentoAtual.descricao || 'Equipamento';
    }
}

// Salvar alterações da PMP
async function salvarAlteracoesPMP() {
    if (!pmpSelecionada) {
        alert('Nenhuma PMP selecionada');
        return;
    }
    
    try {
        console.log('💾 Iniciando salvamento da PMP:', pmpSelecionada.id);
        
        // Coletar dados do formulário pelos IDs dos campos
        const formData = {};
        
        // Campos de configuração (principais)
        const numPessoas = document.getElementById('pmp-num-pessoas');
        if (numPessoas) {
            formData.num_pessoas = parseInt(numPessoas.value) || 1;
            console.log('📝 num_pessoas coletado:', formData.num_pessoas);
        }
        
        const diasAntecipacao = document.getElementById('pmp-dias-antecipacao');
        if (diasAntecipacao) {
            formData.dias_antecipacao = parseInt(diasAntecipacao.value) || 0;
            console.log('📝 dias_antecipacao coletado:', formData.dias_antecipacao);
        }
        
        const tempoPessoa = document.getElementById('pmp-tempo-pessoa');
        if (tempoPessoa) {
            formData.tempo_pessoa = parseFloat(tempoPessoa.value) || 1.0;
            console.log('📝 tempo_pessoa coletado:', formData.tempo_pessoa);
        }
        
        const formaImpressao = document.getElementById('pmp-forma-impressao');
        if (formaImpressao) {
            formData.forma_impressao = formaImpressao.value || 'comum';
            console.log('📝 forma_impressao coletado:', formData.forma_impressao);
        }
        
        // Outros campos opcionais
        const descricao = document.getElementById('pmp-descricao');
        if (descricao && descricao.value !== pmpSelecionada.descricao) {
            formData.descricao = descricao.value;
            console.log('📝 descricao coletado:', formData.descricao);
        }
        
        const tipo = document.getElementById('pmp-tipo');
        if (tipo && tipo.value !== pmpSelecionada.tipo) {
            formData.tipo = tipo.value;
            console.log('📝 tipo coletado:', formData.tipo);
        }
        
        const oficina = document.getElementById('pmp-oficina');
        if (oficina && oficina.value !== pmpSelecionada.oficina) {
            formData.oficina = oficina.value;
            console.log('📝 oficina coletado:', formData.oficina);
        }
        
        const frequencia = document.getElementById('pmp-frequencia');
        if (frequencia && frequencia.value !== pmpSelecionada.frequencia) {
            formData.frequencia = frequencia.value;
            console.log('📝 frequencia coletado:', formData.frequencia);
        }
        
        const condicao = document.getElementById('pmp-condicao');
        if (condicao && condicao.value !== pmpSelecionada.condicao) {
            formData.condicao = condicao.value;
            console.log('📝 condicao coletado:', formData.condicao);
        }
        
        console.log('📦 Dados coletados para envio:', formData);
        
        // Verificar se há dados para enviar
        if (Object.keys(formData).length === 0) {
            alert('Nenhuma alteração detectada');
            return;
        }
        
        // Chamar API de atualização
        console.log('🚀 Enviando dados para API...');
        const response = await fetch(`/api/pmp/${pmpSelecionada.id}/atualizar`, {
            method: 'PUT',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(formData)
        });
        
        console.log('📡 Resposta da API recebida:', response.status, response.statusText);
        
        if (!response.ok) {
            const errorText = await response.text();
            console.error('❌ Erro na resposta da API:', errorText);
            throw new Error(`Erro HTTP ${response.status}: ${response.statusText}`);
        }
        
        const resultado = await response.json();
        console.log('✅ Resultado da API:', resultado);
        
        if (resultado.success) {
            // Atualizar PMP selecionada com dados retornados
            if (resultado.pmp) {
                pmpSelecionada = resultado.pmp;
                console.log('🔄 PMP selecionada atualizada:', pmpSelecionada);
                
                // Atualizar lista de PMPs se disponível
                if (window.pmpsAtual) {
                    const index = window.pmpsAtual.findIndex(p => p.id === pmpSelecionada.id);
                    if (index !== -1) {
                        window.pmpsAtual[index] = pmpSelecionada;
                        console.log('🔄 Lista de PMPs atualizada');
                    }
                }
                
                // CORREÇÃO: Recarregar formulário com dados atualizados
                console.log('🔄 Recarregando formulário com dados atualizados...');
                renderizarFormularioPMP(pmpSelecionada);
            }
            
            // Mostrar campos atualizados se disponível
            if (resultado.campos_atualizados && resultado.campos_atualizados.length > 0) {
                console.log('📝 Campos atualizados:', resultado.campos_atualizados);
            }
            
            alert('Alterações salvas com sucesso!');
        } else {
            console.error('❌ API retornou erro:', resultado.message);
            alert('Erro ao salvar: ' + resultado.message);
        }
        
    } catch (error) {
        console.error('❌ Erro ao salvar alterações da PMP:', error);
        alert('Erro ao salvar alterações: ' + error.message);
    }
}

// Carregar PMPs existentes ao trocar para a aba
async function carregarPMPsExistentes() {
    if (!equipamentoAtual) {
        return;
    }
    
    try {
        console.log('🔄 Carregando PMPs existentes para equipamento:', equipamentoAtual.id);
        
        const response = await fetch(`/api/pmp/equipamento/${equipamentoAtual.id}`);
        if (!response.ok) {
            throw new Error(`Erro HTTP: ${response.status}`);
        }
        
        const pmps = await response.json();
        console.log('📋 PMPs existentes carregadas:', pmps);
        
        if (pmps && pmps.length > 0) {
            pmpsAtual = pmps;
            renderizarPMPsIntegradas(pmps);
            atualizarInfoEquipamentoPMP();
            
            // CORREÇÃO: Se havia uma PMP selecionada, recarregar seus dados atualizados
            if (pmpSelecionada) {
                console.log('🔄 Recarregando dados da PMP selecionada:', pmpSelecionada.id);
                await selecionarPMPIntegrada(pmpSelecionada.id, null);
            }
        }
        
    } catch (error) {
        console.error('❌ Erro ao carregar PMPs existentes:', error);
        // Não mostrar erro para o usuário, apenas manter estado vazio
    }
}

// Modificar a função de inicialização de tabs para carregar PMPs
function inicializarTabsComPMP() {
    const tabs = document.querySelectorAll('.nav-tab');
    const contents = document.querySelectorAll('.tab-content');
    
    tabs.forEach(tab => {
        tab.addEventListener('click', function() {
            const targetTab = this.getAttribute('data-tab');
            
            // Remover classe active de todas as tabs e conteúdos
            tabs.forEach(t => t.classList.remove('active'));
            contents.forEach(c => c.classList.remove('active'));
            
            // Adicionar classe active na tab e conteúdo selecionados
            this.classList.add('active');
            document.getElementById(targetTab).classList.add('active');
            
            // Se mudou para aba de procedimentos, carregar PMPs existentes
            if (targetTab === 'procedimentos') {
                setTimeout(() => {
                    atualizarInfoEquipamentoPMP();
                    carregarPMPsExistentes();
                }, 100);
            }
        });
    });
}

// Substituir a inicialização de tabs original
document.addEventListener('DOMContentLoaded', function() {
    // Remover a chamada original de inicializarTabs() e usar a nova
    inicializarTabsComPMP();
});

