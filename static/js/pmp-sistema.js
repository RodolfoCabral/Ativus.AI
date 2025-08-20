// Sistema PMP - JavaScript
let equipamentoAtual = null;
let pmpsGeradas = [];
let pmpSelecionada = null;
let atividadesOriginais = [];

// Inicialização
document.addEventListener('DOMContentLoaded', function() {
    carregarEquipamentoFromURL();
    configurarEventos();
});

// Configurar eventos
function configurarEventos() {
    // Sidebar toggle
    const sidebarToggle = document.querySelector('.sidebar-toggle');
    if (sidebarToggle) {
        sidebarToggle.addEventListener('click', function() {
            document.querySelector('.sidebar').classList.toggle('collapsed');
        });
    }
}

// Carregar equipamento da URL
function carregarEquipamentoFromURL() {
    const urlParams = new URLSearchParams(window.location.search);
    const equipamentoId = urlParams.get('equipamento');
    
    if (equipamentoId) {
        carregarEquipamento(equipamentoId);
    } else {
        mostrarSelecaoEquipamento();
    }
}

// Mostrar seleção de equipamento
function mostrarSelecaoEquipamento() {
    document.getElementById('equipamento-tag').textContent = '-';
    document.getElementById('equipamento-desc').textContent = 'Selecione um equipamento';
    
    const pmpsLista = document.getElementById('pmps-lista');
    pmpsLista.innerHTML = `
        <div class="empty-state">
            <i class="fas fa-search"></i>
            <h3>Selecione um Equipamento</h3>
            <p>Acesse através do Plano Mestre de um equipamento</p>
        </div>
    `;
}

// Carregar equipamento
async function carregarEquipamento(equipamentoId) {
    try {
        showLoading('Carregando equipamento...');
        
        // Buscar dados do equipamento
        const response = await fetch(`/api/equipamentos/${equipamentoId}`);
        if (!response.ok) {
            throw new Error('Equipamento não encontrado');
        }
        
        equipamentoAtual = await response.json();
        
        // Atualizar interface
        document.getElementById('equipamento-tag').textContent = equipamentoAtual.tag;
        document.getElementById('equipamento-desc').textContent = equipamentoAtual.descricao;
        
        // Carregar atividades do plano mestre
        await carregarAtividades(equipamentoId);
        
        hideLoading();
        
    } catch (error) {
        console.error('Erro ao carregar equipamento:', error);
        hideLoading();
        alert('Erro ao carregar equipamento: ' + error.message);
    }
}

// Carregar atividades do plano mestre
async function carregarAtividades(equipamentoId) {
    try {
        const response = await fetch(`/api/plano-mestre/equipamento/${equipamentoId}`);
        if (!response.ok) {
            throw new Error('Erro ao carregar atividades');
        }
        
        const data = await response.json();
        atividadesOriginais = data.atividades || [];
        
        console.log('Atividades carregadas:', atividadesOriginais);
        
    } catch (error) {
        console.error('Erro ao carregar atividades:', error);
        atividadesOriginais = [];
    }
}

// Gerar PMPs automaticamente
function gerarPMPs() {
    if (!equipamentoAtual) {
        alert('Selecione um equipamento primeiro');
        return;
    }
    
    if (atividadesOriginais.length === 0) {
        alert('Nenhuma atividade encontrada para este equipamento');
        return;
    }
    
    showLoading('Gerando PMPs...');
    
    // Agrupar atividades por critérios
    const grupos = agruparAtividades(atividadesOriginais);
    
    // Gerar PMPs para cada grupo
    pmpsGeradas = [];
    let contador = 1;
    
    for (const grupo of grupos) {
        const pmp = {
            id: `pmp-${contador}`,
            codigo: `PMP-${contador.toString().padStart(2, '0')}-${equipamentoAtual.tag}`,
            descricao: gerarDescricaoPMP(grupo),
            tipo: grupo.tipo_manutencao,
            oficina: grupo.oficina,
            frequencia: grupo.frequencia,
            condicao: grupo.status_ativo ? 'Funcionando' : 'Parado',
            atividades: grupo.atividades,
            equipamento_id: equipamentoAtual.id,
            // Configurações padrão
            num_pessoas: 1,
            dias_antecipacao: 0,
            tempo_pessoa: 0.5,
            forma_impressao: 'comum',
            dias_semana: ['terca']
        };
        
        pmpsGeradas.push(pmp);
        contador++;
    }
    
    // Atualizar interface
    renderizarPMPs();
    
    hideLoading();
    
    if (pmpsGeradas.length > 0) {
        selecionarPMP(pmpsGeradas[0]);
    }
}

// Agrupar atividades por critérios
function agruparAtividades(atividades) {
    const grupos = new Map();
    
    for (const atividade of atividades) {
        // Criar chave única baseada nos critérios de agrupamento
        const chave = `${atividade.oficina || 'sem-oficina'}_${atividade.frequencia || 'sem-frequencia'}_${atividade.tipo_manutencao || 'sem-tipo'}_${atividade.status_ativo ? 'funcionando' : 'parado'}`;
        
        if (!grupos.has(chave)) {
            grupos.set(chave, {
                oficina: atividade.oficina,
                frequencia: atividade.frequencia,
                tipo_manutencao: atividade.tipo_manutencao,
                status_ativo: atividade.status_ativo,
                atividades: []
            });
        }
        
        grupos.get(chave).atividades.push(atividade);
    }
    
    return Array.from(grupos.values());
}

// Gerar descrição da PMP
function gerarDescricaoPMP(grupo) {
    const tipoManutencao = grupo.tipo_manutencao || 'Manutenção';
    const oficina = grupo.oficina || 'Geral';
    const frequencia = grupo.frequencia || 'Periódica';
    
    return `${tipoManutencao.toUpperCase()} ${frequencia.toUpperCase()} - ${oficina.toUpperCase()}`;
}

// Renderizar lista de PMPs
function renderizarPMPs() {
    const pmpsLista = document.getElementById('pmps-lista');
    
    if (pmpsGeradas.length === 0) {
        pmpsLista.innerHTML = `
            <div class="empty-state">
                <i class="fas fa-clipboard-list"></i>
                <h3>Nenhuma PMP gerada</h3>
                <p>Clique em "Gerar PMPs" para criar os procedimentos</p>
            </div>
        `;
        return;
    }
    
    let html = '';
    
    for (const pmp of pmpsGeradas) {
        const ativo = pmp === pmpSelecionada ? 'active' : '';
        
        html += `
            <div class="pmp-item ${ativo}" onclick="selecionarPMP('${pmp.id}')">
                <div class="pmp-codigo">${pmp.codigo}</div>
                <div class="pmp-descricao">${pmp.descricao}</div>
                <div class="pmp-detalhes">
                    <span>${pmp.oficina}</span>
                    <span>${pmp.atividades.length} atividades</span>
                </div>
            </div>
        `;
    }
    
    pmpsLista.innerHTML = html;
}

// Selecionar PMP
function selecionarPMP(pmpId) {
    if (typeof pmpId === 'string') {
        pmpSelecionada = pmpsGeradas.find(p => p.id === pmpId);
    } else {
        pmpSelecionada = pmpId;
    }
    
    if (!pmpSelecionada) return;
    
    // Atualizar interface
    renderizarPMPs(); // Re-renderizar para atualizar seleção
    preencherFormularioPMP();
    renderizarAtividadesAgrupadas();
    
    // Atualizar título
    document.getElementById('pmp-title').textContent = pmpSelecionada.codigo;
}

// Preencher formulário da PMP
function preencherFormularioPMP() {
    if (!pmpSelecionada) return;
    
    document.getElementById('descricao-os').value = pmpSelecionada.descricao;
    document.getElementById('tipo').value = pmpSelecionada.tipo || '';
    document.getElementById('oficina').value = pmpSelecionada.oficina || '';
    document.getElementById('frequencia').value = pmpSelecionada.frequencia || '';
    document.getElementById('condicao').value = pmpSelecionada.condicao || '';
    document.getElementById('num-pessoas').value = pmpSelecionada.num_pessoas || 1;
    document.getElementById('dias-antecipacao').value = pmpSelecionada.dias_antecipacao || 0;
    document.getElementById('tempo-pessoa').value = pmpSelecionada.tempo_pessoa || 0.5;
    document.getElementById('forma-impressao').value = pmpSelecionada.forma_impressao || 'comum';
    
    // Dias da semana
    const diasSemana = ['domingo', 'segunda', 'terca', 'quarta', 'quinta', 'sexta', 'sabado'];
    diasSemana.forEach(dia => {
        const checkbox = document.getElementById(dia);
        if (checkbox) {
            checkbox.checked = pmpSelecionada.dias_semana && pmpSelecionada.dias_semana.includes(dia);
        }
    });
}

// Renderizar atividades agrupadas
function renderizarAtividadesAgrupadas() {
    const container = document.getElementById('atividades-agrupadas');
    
    if (!pmpSelecionada || !pmpSelecionada.atividades || pmpSelecionada.atividades.length === 0) {
        container.innerHTML = `
            <div class="empty-state">
                <i class="fas fa-tasks"></i>
                <h3>Nenhuma atividade</h3>
                <p>Esta PMP não possui atividades</p>
            </div>
        `;
        return;
    }
    
    let html = '';
    
    for (const atividade of pmpSelecionada.atividades) {
        html += `
            <div class="atividade-item">
                <input type="checkbox" class="atividade-checkbox" checked disabled>
                <div class="atividade-desc">${atividade.descricao}</div>
                <div class="atividade-detalhes">
                    ${atividade.conjunto || ''} | ${atividade.ponto_controle || ''}
                </div>
            </div>
        `;
    }
    
    container.innerHTML = html;
}

// Trocar aba
function trocarAba(aba) {
    // Remover classe active de todas as abas
    document.querySelectorAll('.pmp-tab').forEach(tab => {
        tab.classList.remove('active');
    });
    
    document.querySelectorAll('.tab-content').forEach(content => {
        content.classList.remove('active');
    });
    
    // Ativar aba selecionada
    event.target.classList.add('active');
    document.getElementById(`tab-${aba}`).classList.add('active');
}

// Salvar PMP
async function salvarPMP() {
    if (!pmpSelecionada) {
        alert('Selecione uma PMP primeiro');
        return;
    }
    
    try {
        showLoading('Salvando PMP...');
        
        // Coletar dados do formulário
        const dadosPMP = {
            codigo: pmpSelecionada.codigo,
            descricao: document.getElementById('descricao-os').value,
            equipamento_id: equipamentoAtual.id,
            tipo: document.getElementById('tipo').value,
            oficina: document.getElementById('oficina').value,
            frequencia: document.getElementById('frequencia').value,
            condicao: document.getElementById('condicao').value,
            num_pessoas: parseInt(document.getElementById('num-pessoas').value) || 1,
            dias_antecipacao: parseInt(document.getElementById('dias-antecipacao').value) || 0,
            tempo_pessoa: parseFloat(document.getElementById('tempo-pessoa').value) || 0.5,
            forma_impressao: document.getElementById('forma-impressao').value,
            dias_semana: coletarDiasSemana(),
            atividades_ids: pmpSelecionada.atividades.map(a => a.id)
        };
        
        // Salvar no backend
        const response = await fetch('/api/pmps', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(dadosPMP)
        });
        
        if (!response.ok) {
            throw new Error('Erro ao salvar PMP');
        }
        
        const resultado = await response.json();
        
        // Atualizar ID da PMP
        pmpSelecionada.id = resultado.id;
        
        hideLoading();
        alert('PMP salva com sucesso!');
        
    } catch (error) {
        console.error('Erro ao salvar PMP:', error);
        hideLoading();
        alert('Erro ao salvar PMP: ' + error.message);
    }
}

// Coletar dias da semana selecionados
function coletarDiasSemana() {
    const dias = [];
    const diasSemana = ['domingo', 'segunda', 'terca', 'quarta', 'quinta', 'sexta', 'sabado'];
    
    diasSemana.forEach(dia => {
        const checkbox = document.getElementById(dia);
        if (checkbox && checkbox.checked) {
            dias.push(dia);
        }
    });
    
    return dias;
}

// Funções de loading
function showLoading(message = 'Carregando...') {
    const pmpsLista = document.getElementById('pmps-lista');
    pmpsLista.innerHTML = `
        <div class="loading">
            <i class="fas fa-spinner"></i>
            <p>${message}</p>
        </div>
    `;
}

function hideLoading() {
    // O loading será substituído pelo conteúdo normal
}

// Funções utilitárias
function formatarTexto(texto) {
    if (!texto) return '-';
    return texto.charAt(0).toUpperCase() + texto.slice(1);
}

function formatarFrequencia(frequencia, pontoControle) {
    if (!frequencia) return '-';
    
    let resultado = formatarTexto(frequencia);
    if (pontoControle) {
        resultado += ` / ${pontoControle}`;
    }
    
    return resultado;
}

// Navegação para equipamento específico
function irParaEquipamento(equipamentoId) {
    window.location.href = `/pmp-sistema?equipamento=${equipamentoId}`;
}

// Voltar para seleção de equipamento
function voltarSelecaoEquipamento() {
    window.location.href = '/pmp-sistema';
}

