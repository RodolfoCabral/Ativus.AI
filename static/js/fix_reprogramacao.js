/**
 * FIX_REPROGRAMACAO.JS
 * 
 * Este script corrige especificamente o problema de reprogramação de OS,
 * onde o sistema está confundindo a data com o ID do usuário.
 */

console.log('🔧 Carregando correção para reprogramação...');

// Executar quando o DOM estiver carregado
document.addEventListener('DOMContentLoaded', function() {
    console.log('🔧 Aplicando correção para reprogramação...');
    
    // Corrigir o problema imediatamente
    corrigirProblemaProgramacao();
    
    // Observar mudanças no DOM para aplicar correções quando necessário
    observarMudancasDOM();
});

// Corrigir o problema de programação
function corrigirProblemaProgramacao() {
    console.log('🔧 Corrigindo problema de programação...');
    
    // Corrigir função handleDrop em pmp-integration.js
    if (typeof window.handleDrop === 'function') {
        console.log('✅ Sobrescrevendo função handleDrop');
        window.handleDrop_original = window.handleDrop;
        window.handleDrop = handleDrop_corrigido;
    }
    
    // Adicionar atributos data-user-name a todos os elementos de usuário
    adicionarAtributosUsuario();
}

// Observar mudanças no DOM
function observarMudancasDOM() {
    console.log('🔧 Configurando observador de DOM...');
    
    // Criar um observador de mutações
    const observer = new MutationObserver(function(mutations) {
        mutations.forEach(function(mutation) {
            if (mutation.type === 'childList' && mutation.addedNodes.length > 0) {
                // Verificar se novos elementos de usuário foram adicionados
                adicionarAtributosUsuario();
            }
        });
    });
    
    // Configurar observador para todo o documento
    observer.observe(document.body, {
        childList: true,
        subtree: true
    });
}

// Adicionar atributos data-user-name a todos os elementos de usuário
function adicionarAtributosUsuario() {
    console.log('🔧 Adicionando atributos de usuário...');
    
    // Encontrar todos os elementos de usuário
    const usuarioRows = document.querySelectorAll('.usuario-row');
    usuarioRows.forEach(function(row) {
        // Verificar se já tem o atributo data-user-name
        if (!row.hasAttribute('data-user-name')) {
            // Obter nome do usuário
            const nomeElement = row.querySelector('.usuario-nome');
            if (nomeElement) {
                const nome = nomeElement.textContent.trim();
                row.setAttribute('data-user-name', nome);
                console.log(`✅ Atributo data-user-name adicionado: ${nome}`);
            }
        }
        
        // Adicionar atributo data-user-name aos dias da semana
        const userId = row.getAttribute('data-user-id');
        if (userId) {
            const diasContainer = document.querySelectorAll(`.dia-container[data-user-id="${userId}"]`);
            diasContainer.forEach(function(dia) {
                if (!dia.hasAttribute('data-user-name')) {
                    const nome = row.getAttribute('data-user-name');
                    if (nome) {
                        dia.setAttribute('data-user-name', nome);
                        console.log(`✅ Atributo data-user-name adicionado ao dia: ${nome}`);
                    }
                }
            });
        }
    });
}

// Função handleDrop corrigida
function handleDrop_corrigido(e) {
    console.log('🔄 Função handleDrop_corrigido executada');
    
    e.stopPropagation();
    e.preventDefault();
    
    // Remover classe de hover
    this.classList.remove('drag-over');
    
    // Verificar se temos um elemento arrastado
    if (!window.draggedElement) {
        console.error('❌ Elemento arrastado não encontrado');
        return false;
    }
    
    // Obter ID da OS do elemento arrastado
    const osId = window.draggedElement.getAttribute('data-os-id');
    if (!osId) {
        console.error('❌ ID da OS não encontrado no elemento arrastado');
        return false;
    }
    
    // Obter data do elemento de destino
    const dateStr = this.getAttribute('data-date');
    if (!dateStr) {
        console.error('❌ Data não encontrada no elemento de destino');
        return false;
    }
    
    // Obter ID do usuário do elemento de destino
    const userId = this.getAttribute('data-user-id');
    if (!userId) {
        console.error('❌ ID do usuário não encontrado no elemento de destino');
        return false;
    }
    
    console.log(`🔄 Drop detectado: OS #${osId} para ${dateStr} com usuário ID ${userId}`);
    
    // CORREÇÃO CRÍTICA: Verificar se userId não é uma data
    if (userId.includes('-')) {
        console.error(`❌ ID do usuário parece ser uma data: ${userId}`);
        
        // Tentar obter o ID do usuário correto
        const userIdCorreto = this.closest('.usuario-semana')?.getAttribute('data-user-id');
        if (userIdCorreto) {
            console.log(`✅ ID do usuário corrigido: ${userIdCorreto}`);
            programarOS(osId, userIdCorreto, dateStr);
            return false;
        }
        
        // Se não conseguir obter o ID correto, usar o nome do usuário diretamente
        const userName = this.getAttribute('data-user-name');
        if (userName) {
            console.log(`✅ Nome do usuário obtido: ${userName}`);
            if (typeof programarOSComNomeUsuario === 'function') {
                programarOSComNomeUsuario(osId, dateStr, userName);
                return false;
            }
        }
        
        console.error('❌ Não foi possível corrigir o ID do usuário');
        return false;
    }
    
    // Chamar a função original
    programarOS(osId, userId, dateStr);
    
    return false;
}

// Aplicar correções imediatamente se o DOM já estiver carregado
if (document.readyState === 'complete' || document.readyState === 'interactive') {
    corrigirProblemaProgramacao();
    setTimeout(observarMudancasDOM, 1000);
}

console.log('✅ Correção para reprogramação carregada com sucesso!');

