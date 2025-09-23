// MODIFICAÇÕES NECESSÁRIAS NO SEU ARQUIVO static/js/programacao.js
// Adicione estas modificações ao seu arquivo existente

// ============================================================================
// INÍCIO DAS MODIFICAÇÕES - Funcionalidade de Atividades de OS
// ============================================================================

// 1. Adicionar esta função no final do arquivo programacao.js
function adicionarBotaoAtividades(chamadoElement, chamadoData) {
    // Verificar se a OS tem PMP (tem atividades)
    if (chamadoData.pmp_id) {
        // Adicionar badge PMP
        const pmpBadge = document.createElement('span');
        pmpBadge.className = 'badge bg-info ms-2';
        pmpBadge.textContent = 'PMP';
        
        // Adicionar botão de atividades
        const btnAtividades = document.createElement('button');
        btnAtividades.className = 'btn btn-sm btn-outline-primary ms-2';
        btnAtividades.innerHTML = '<i class="fas fa-list-check"></i>';
        btnAtividades.title = 'Ver Lista de Execução';
        btnAtividades.onclick = (e) => {
            e.stopPropagation();
            abrirModalAtividades(chamadoData.id);
        };
        
        // Adicionar ao elemento
        const headerElement = chamadoElement.querySelector('.chamado-header') || chamadoElement.querySelector('.os-header');
        if (headerElement) {
            headerElement.appendChild(pmpBadge);
            headerElement.appendChild(btnAtividades);
        }
    }
}

// 2. Modificar a função renderChamado existente para incluir o botão de atividades
// Encontre a função renderChamado no seu código e adicione esta linha no final:
/*
function renderChamado(chamado) {
    // ... seu código existente para renderizar o chamado ...
    
    // ADICIONAR ESTA LINHA NO FINAL DA FUNÇÃO:
    adicionarBotaoAtividades(chamadoElement, chamado);
    
    return chamadoElement;
}
*/

// 3. Ou se você usa uma função diferente para renderizar OS, adicione lá:
/*
function renderizarOS(os) {
    // ... seu código existente ...
    
    // ADICIONAR ESTA LINHA NO FINAL:
    adicionarBotaoAtividades(osElement, os);
    
    return osElement;
}
*/

// ============================================================================
// FIM DAS MODIFICAÇÕES
// ============================================================================

// EXEMPLO COMPLETO de como integrar com o clique existente:
/*
// Se você já tem um evento de clique nas OS, modifique assim:

document.addEventListener('click', function(e) {
    const chamadoElement = e.target.closest('.chamado-item');
    if (chamadoElement) {
        const chamadoId = chamadoElement.dataset.chamadoId;
        const pmpId = chamadoElement.dataset.pmpId;
        
        // Se tem PMP, abrir modal de atividades
        if (pmpId) {
            abrirModalAtividades(chamadoId);
        } else {
            // Comportamento original para OS sem PMP
            // ... seu código existente ...
        }
    }
});
*/

// IMPORTANTE: Certifique-se de incluir o arquivo atividades-os.js na sua página:
// <script src="{{ url_for('static', filename='js/atividades-os.js') }}"></script>
