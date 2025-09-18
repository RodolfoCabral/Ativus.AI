/**
 * CORRECAO_DRAG_DROP.JS
 * 
 * Este script corrige o problema de drag and drop após desprogramação
 * Ele reinicializa os eventos de drag and drop para todas as OS após desprogramação
 */

console.log('🔧 Carregando correção para drag and drop...');

// Função para reinicializar os eventos de drag and drop
function reinicializarDragDrop() {
    console.log('🔄 Reinicializando eventos de drag and drop...');
    
    // Remover todos os eventos de drag and drop existentes
    const chamadoCards = document.querySelectorAll('.chamado-card');
    chamadoCards.forEach(card => {
        card.removeEventListener('dragstart', window.handleDragStart);
        card.removeEventListener('dragend', window.handleDragEnd);
        
        // Adicionar novamente os eventos
        card.addEventListener('dragstart', window.handleDragStart);
        card.addEventListener('dragend', window.handleDragEnd);
        card.setAttribute('draggable', 'true');
        
        console.log(`✅ Eventos reinicializados para OS #${card.getAttribute('data-os-id')}`);
    });
    
    // Reinicializar eventos de drop nas células do calendário
    const diaCells = document.querySelectorAll('.dia-container');
    diaCells.forEach(cell => {
        cell.removeEventListener('dragover', window.handleDragOver);
        cell.removeEventListener('dragleave', window.handleDragLeave);
        cell.removeEventListener('drop', window.handleDrop);
        
        // Adicionar novamente os eventos
        cell.addEventListener('dragover', window.handleDragOver);
        cell.addEventListener('dragleave', window.handleDragLeave);
        cell.addEventListener('drop', window.handleDrop);
        
        console.log(`✅ Eventos de drop reinicializados para célula ${cell.getAttribute('data-date')}`);
    });
}

// Sobrescrever a função desprogramarOS para reinicializar os eventos após desprogramação
if (typeof window.desprogramarOS === 'function') {
    console.log('✅ Função desprogramarOS encontrada, aplicando correção...');
    
    // Salvar a função original
    window.desprogramarOS_original = window.desprogramarOS;
    
    // Sobrescrever a função
    window.desprogramarOS = function(osId) {
        console.log(`🔧 Função desprogramarOS corrigida executada para OS #${osId}`);
        
        // Chamar a função original
        const result = window.desprogramarOS_original(osId);
        
        // Após desprogramação, reinicializar os eventos de drag and drop
        setTimeout(function() {
            console.log('🔄 Desprogramação concluída, reinicializando eventos...');
            reinicializarDragDrop();
            
            // Forçar a recriação dos cards de OS
            setTimeout(function() {
                console.log('🔄 Forçando renderização das linhas de prioridade...');
                if (typeof window.renderPriorityLines === 'function') {
                    window.renderPriorityLines();
                }
            }, 500);
        }, 1000);
        
        return result;
    };
}

// Corrigir a função handleDrop para garantir que os parâmetros estejam na ordem correta
if (typeof window.handleDrop === 'function') {
    console.log('✅ Função handleDrop encontrada, aplicando correção...');
    
    // Salvar a função original
    window.handleDrop_original = window.handleDrop;
    
    // Sobrescrever a função
    window.handleDrop = function(e) {
        console.log('🔧 Função handleDrop corrigida executada');
        
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
        
        // Obter nome do usuário do elemento de destino ou da linha do usuário
        let userName = this.getAttribute('data-user-name');
        if (!userName) {
            // Tentar obter o nome do usuário da linha do usuário
            const usuarioRow = document.querySelector(`.usuario-row[data-user-id="${userId}"]`);
            if (usuarioRow) {
                const nomeElement = usuarioRow.querySelector('.usuario-nome');
                if (nomeElement) {
                    userName = nomeElement.textContent.trim();
                }
            }
        }
        
        console.log(`🔄 Drop detectado: OS #${osId} para ${dateStr} com usuário ID ${userId}${userName ? ', nome: ' + userName : ''}`);
        
        // Programar OS diretamente com o nome do usuário
        if (userName) {
            // Chamar diretamente programarOSComNomeUsuario para evitar a função problemática programarOS
            if (typeof window.programarOSComNomeUsuario === 'function') {
                window.programarOSComNomeUsuario(osId, dateStr, userName);
            } else {
                console.error('❌ Função programarOSComNomeUsuario não encontrada');
            }
        } else {
            // Tentar obter o nome do usuário da lista global
            if (typeof window.usuarios !== 'undefined' && Array.isArray(window.usuarios)) {
                const usuario = window.usuarios.find(u => u.id == userId);
                if (usuario && usuario.name) {
                    if (typeof window.programarOSComNomeUsuario === 'function') {
                        window.programarOSComNomeUsuario(osId, dateStr, usuario.name);
                    }
                } else {
                    console.warn(`⚠️ Nome do usuário não encontrado para ID ${userId}, usando valor padrão`);
                    if (typeof window.programarOSComNomeUsuario === 'function') {
                        window.programarOSComNomeUsuario(osId, dateStr, `Técnico #${userId}`);
                    }
                }
            } else {
                console.error('❌ Lista de usuários não encontrada');
                // Último recurso: chamar a função original
                return window.handleDrop_original.call(this, e);
            }
        }
        
        return false;
    };
}

// Função para adicionar atributos data-user-name a todos os elementos de usuário
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

// Função para corrigir a criação de cards de OS
function corrigirCreateOSCard() {
    if (typeof window.createOSCard === 'function') {
        console.log('✅ Função createOSCard encontrada, aplicando correção...');
        
        // Salvar a função original
        window.createOSCard_original = window.createOSCard;
        
        // Sobrescrever a função
        window.createOSCard = function(os) {
            console.log(`🔧 Função createOSCard corrigida executada para OS #${os.id}`);
            
            // Chamar a função original
            const card = window.createOSCard_original(os);
            
            // Garantir que o card seja arrastável
            card.setAttribute('draggable', 'true');
            
            // Adicionar eventos de drag and drop
            card.addEventListener('dragstart', window.handleDragStart);
            card.addEventListener('dragend', window.handleDragEnd);
            
            console.log(`✅ Eventos de drag and drop adicionados para OS #${os.id}`);
            
            return card;
        };
    }
}

// Função para corrigir a renderização das linhas de prioridade
function corrigirRenderPriorityLines() {
    if (typeof window.renderPriorityLines === 'function') {
        console.log('✅ Função renderPriorityLines encontrada, aplicando correção...');
        
        // Salvar a função original
        window.renderPriorityLines_original = window.renderPriorityLines;
        
        // Sobrescrever a função
        window.renderPriorityLines = function() {
            console.log('🔧 Função renderPriorityLines corrigida executada');
            
            // Chamar a função original
            const result = window.renderPriorityLines_original();
            
            // Após renderização, reinicializar os eventos de drag and drop
            setTimeout(reinicializarDragDrop, 100);
            
            return result;
        };
    }
}

// Função para corrigir a função loadOrdensServico
function corrigirLoadOrdensServico() {
    if (typeof window.loadOrdensServico === 'function') {
        console.log('✅ Função loadOrdensServico encontrada, aplicando correção...');
        
        // Salvar a função original
        window.loadOrdensServico_original = window.loadOrdensServico;
        
        // Sobrescrever a função
        window.loadOrdensServico = function() {
            console.log('🔧 Função loadOrdensServico corrigida executada');
            
            // Chamar a função original
            const result = window.loadOrdensServico_original();
            
            // Após carregamento, reinicializar os eventos de drag and drop
            setTimeout(reinicializarDragDrop, 1000);
            
            return result;
        };
    }
}

// Aplicar correções quando o DOM estiver carregado
document.addEventListener('DOMContentLoaded', function() {
    console.log('🔧 DOM carregado, aplicando correções...');
    
    // Adicionar atributos de usuário
    setTimeout(adicionarAtributosUsuario, 500);
    
    // Corrigir funções
    setTimeout(function() {
        corrigirCreateOSCard();
        corrigirRenderPriorityLines();
        corrigirLoadOrdensServico();
        
        // Reinicializar eventos de drag and drop
        setTimeout(reinicializarDragDrop, 1000);
    }, 500);
});

// Aplicar correções imediatamente se o DOM já estiver carregado
if (document.readyState === 'complete' || document.readyState === 'interactive') {
    console.log('🔧 DOM já carregado, aplicando correções imediatamente...');
    
    // Adicionar atributos de usuário
    setTimeout(adicionarAtributosUsuario, 500);
    
    // Corrigir funções
    setTimeout(function() {
        corrigirCreateOSCard();
        corrigirRenderPriorityLines();
        corrigirLoadOrdensServico();
        
        // Reinicializar eventos de drag and drop
        setTimeout(reinicializarDragDrop, 1000);
    }, 500);
}

// Configurar um observador para adicionar atributos a novos elementos
const observer = new MutationObserver(function(mutations) {
    mutations.forEach(function(mutation) {
        if (mutation.type === 'childList' && mutation.addedNodes.length > 0) {
            // Verificar se novos elementos foram adicionados
            setTimeout(function() {
                adicionarAtributosUsuario();
                reinicializarDragDrop();
            }, 100);
        }
    });
});

// Configurar observador para todo o documento
observer.observe(document.body, {
    childList: true,
    subtree: true
});

console.log('✅ Correção para drag and drop carregada com sucesso!');

