/**
 * FIX_INVERSAO_PARAMETROS.JS
 * 
 * Este script corrige especificamente o problema de inversão de parâmetros
 * na função programarOS do arquivo pmp-integration.js
 */

console.log('🔧 Carregando correção para inversão de parâmetros...');

// Executar quando o DOM estiver carregado
document.addEventListener('DOMContentLoaded', function() {
    console.log('🔧 Aplicando correção para inversão de parâmetros...');
    
    // Aguardar um momento para garantir que todas as funções estejam carregadas
    setTimeout(function() {
        // Verificar se a função handleDrop existe no pmp-integration.js
        if (typeof window.handleDrop === 'function') {
            console.log('✅ Função handleDrop encontrada, aplicando correção...');
            
            // Salvar a função original
            window.handleDrop_original = window.handleDrop;
            
            // Sobrescrever a função handleDrop
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
                
                // Obter nome do usuário do elemento de destino
                const userName = this.getAttribute('data-user-name');
                
                console.log(`🔄 Drop detectado: OS #${osId} para ${dateStr} com usuário ID ${userId}${userName ? ', nome: ' + userName : ''}`);
                
                // CORREÇÃO CRÍTICA: Chamar programarOS com os parâmetros na ordem correta
                // A ordem correta é: osId, userId, dateStr
                if (typeof programarOS === 'function') {
                    programarOS(osId, userId, dateStr);
                } else if (typeof window.programarOS === 'function') {
                    window.programarOS(osId, userId, dateStr);
                } else {
                    console.error('❌ Função programarOS não encontrada');
                    
                    // Tentar programar diretamente com o nome do usuário
                    if (userName && typeof programarOSComNomeUsuario === 'function') {
                        programarOSComNomeUsuario(osId, dateStr, userName);
                    } else {
                        console.error('❌ Não foi possível programar a OS');
                    }
                }
                
                return false;
            };
            
            // Verificar se a função programarOS existe
            if (typeof window.programarOS === 'function') {
                console.log('✅ Função programarOS encontrada, aplicando correção...');
                
                // Salvar a função original
                window.programarOS_original = window.programarOS;
                
                // Sobrescrever a função programarOS
                window.programarOS = function(osId, userId, dateStr) {
                    console.log(`🔧 Função programarOS corrigida: OS #${osId}, usuário ID ${userId}, data ${dateStr}`);
                    
                    // Verificar se os parâmetros estão na ordem correta
                    if (typeof osId === 'string' && osId.includes('-')) {
                        console.warn('⚠️ Parâmetro osId parece ser uma data:', osId);
                        // Reordenar parâmetros: osId, userId, dateStr -> osId, dateStr, userId
                        return window.programarOS_original(osId, dateStr, userId);
                    }
                    
                    // Verificar se userId é uma data
                    if (typeof userId === 'string' && userId.includes('-')) {
                        console.warn('⚠️ Parâmetro userId parece ser uma data:', userId);
                        // Reordenar parâmetros: osId, userId, dateStr -> osId, dateStr, userId
                        return window.programarOS_original(osId, dateStr, userId);
                    }
                    
                    // Verificar se dateStr é um número
                    if (!isNaN(dateStr) && dateStr.toString().length <= 2) {
                        console.warn('⚠️ Parâmetro dateStr parece ser um ID:', dateStr);
                        // Reordenar parâmetros: osId, userId, dateStr -> osId, dateStr, userId
                        return window.programarOS_original(osId, userId, new Date().toISOString().split('T')[0]);
                    }
                    
                    // Chamar a função original com os parâmetros na ordem correta
                    return window.programarOS_original(osId, userId, dateStr);
                };
            }
            
            // Adicionar atributos data-user-name a todos os elementos de usuário
            adicionarAtributosUsuario();
        } else {
            console.warn('⚠️ Função handleDrop não encontrada, tentando novamente em 1 segundo...');
            setTimeout(arguments.callee, 1000);
        }
    }, 1000);
});

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
    
    // Configurar um observador para adicionar atributos a novos elementos
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

// Aplicar correções imediatamente se o DOM já estiver carregado
if (document.readyState === 'complete' || document.readyState === 'interactive') {
    setTimeout(function() {
        console.log('🔧 Aplicando correção imediatamente...');
        
        // Verificar se a função handleDrop existe
        if (typeof window.handleDrop === 'function') {
            console.log('✅ Função handleDrop encontrada, aplicando correção...');
            
            // Salvar a função original
            window.handleDrop_original = window.handleDrop;
            
            // Sobrescrever a função handleDrop
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
                
                // Obter nome do usuário do elemento de destino
                const userName = this.getAttribute('data-user-name');
                
                console.log(`🔄 Drop detectado: OS #${osId} para ${dateStr} com usuário ID ${userId}${userName ? ', nome: ' + userName : ''}`);
                
                // CORREÇÃO CRÍTICA: Chamar programarOS com os parâmetros na ordem correta
                // A ordem correta é: osId, userId, dateStr
                if (typeof programarOS === 'function') {
                    programarOS(osId, userId, dateStr);
                } else if (typeof window.programarOS === 'function') {
                    window.programarOS(osId, userId, dateStr);
                } else {
                    console.error('❌ Função programarOS não encontrada');
                    
                    // Tentar programar diretamente com o nome do usuário
                    if (userName && typeof programarOSComNomeUsuario === 'function') {
                        programarOSComNomeUsuario(osId, dateStr, userName);
                    } else {
                        console.error('❌ Não foi possível programar a OS');
                    }
                }
                
                return false;
            };
        }
        
        // Adicionar atributos data-user-name a todos os elementos de usuário
        adicionarAtributosUsuario();
    }, 500);
}

console.log('✅ Correção para inversão de parâmetros carregada com sucesso!');

