/**
 * SOLUCAO_RADICAL.JS
 * 
 * Esta é uma solução radical que substitui completamente o sistema de drag and drop
 * para garantir que funcione em todas as situações, incluindo após desprogramação.
 */

console.log('🔧 Carregando solução radical para drag and drop...');

// Função para inicializar o sistema de drag and drop do zero
function inicializarDragDropRadical() {
    console.log('🔄 Inicializando sistema de drag and drop radical...');
    
    // Remover todos os eventos de drag and drop existentes
    document.querySelectorAll('.chamado-card').forEach(card => {
        card.removeAttribute('draggable');
        
        // Remover todos os event listeners
        const newCard = card.cloneNode(true);
        card.parentNode.replaceChild(newCard, card);
    });
    
    document.querySelectorAll('.dia-container').forEach(cell => {
        // Remover todos os event listeners
        const newCell = cell.cloneNode(true);
        cell.parentNode.replaceChild(newCell, cell);
    });
    
    // Adicionar novos eventos de drag and drop
    document.querySelectorAll('.chamado-card').forEach(card => {
        card.setAttribute('draggable', 'true');
        
        // Adicionar evento dragstart
        card.addEventListener('dragstart', function(e) {
            console.log(`🔄 Drag iniciado para OS #${this.getAttribute('data-os-id')}`);
            
            // Armazenar referência ao elemento arrastado
            window.draggedElement = this;
            
            // Adicionar classe de arrastar
            this.classList.add('dragging');
            
            // Definir dados de transferência
            e.dataTransfer.setData('text/plain', this.getAttribute('data-os-id'));
            e.dataTransfer.effectAllowed = 'move';
        });
        
        // Adicionar evento dragend
        card.addEventListener('dragend', function() {
            console.log(`🔄 Drag finalizado para OS #${this.getAttribute('data-os-id')}`);
            
            // Remover classe de arrastar
            this.classList.remove('dragging');
            
            // Limpar referência ao elemento arrastado
            window.draggedElement = null;
        });
    });
    
    // Adicionar eventos às células do calendário
    document.querySelectorAll('.dia-container').forEach(cell => {
        // Adicionar evento dragover
        cell.addEventListener('dragover', function(e) {
            e.preventDefault();
            e.stopPropagation();
            
            // Adicionar classe de hover
            this.classList.add('drag-over');
            
            // Permitir drop
            e.dataTransfer.dropEffect = 'move';
        });
        
        // Adicionar evento dragleave
        cell.addEventListener('dragleave', function() {
            // Remover classe de hover
            this.classList.remove('drag-over');
        });
        
        // Adicionar evento drop
        cell.addEventListener('drop', function(e) {
            console.log('🔄 Drop detectado');
            
            e.preventDefault();
            e.stopPropagation();
            
            // Remover classe de hover
            this.classList.remove('drag-over');
            
            // Obter ID da OS do elemento arrastado
            let osId;
            
            if (window.draggedElement) {
                osId = window.draggedElement.getAttribute('data-os-id');
            } else {
                osId = e.dataTransfer.getData('text/plain');
            }
            
            if (!osId) {
                console.error('❌ ID da OS não encontrado');
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
                programarOSComNomeUsuarioRadical(osId, dateStr, userName);
            } else {
                // Tentar obter o nome do usuário da lista global
                if (typeof window.usuarios !== 'undefined' && Array.isArray(window.usuarios)) {
                    const usuario = window.usuarios.find(u => u.id == userId);
                    if (usuario && usuario.name) {
                        programarOSComNomeUsuarioRadical(osId, dateStr, usuario.name);
                    } else {
                        console.warn(`⚠️ Nome do usuário não encontrado para ID ${userId}, usando valor padrão`);
                        programarOSComNomeUsuarioRadical(osId, dateStr, `Técnico #${userId}`);
                    }
                } else {
                    console.error('❌ Lista de usuários não encontrada');
                    programarOSComNomeUsuarioRadical(osId, dateStr, `Técnico #${userId}`);
                }
            }
            
            return false;
        });
    });
    
    console.log('✅ Sistema de drag and drop radical inicializado com sucesso!');
}

// Função para programar OS com nome do usuário (versão radical)
function programarOSComNomeUsuarioRadical(osId, dateStr, userName) {
    console.log(`🔄 Programando OS #${osId} para ${dateStr} com usuário ${userName} (versão radical)`);
    
    // Verificar se a função original existe
    if (typeof window.programarOSComNomeUsuario === 'function') {
        // Chamar a função original
        window.programarOSComNomeUsuario(osId, dateStr, userName);
    } else {
        // Implementação alternativa
        const url = `/api/ordens-servico/${osId}/programar`;
        
        // Dados para enviar
        const data = {
            data_programada: dateStr,
            usuario_responsavel: userName,
            status: 'programada'
        };
        
        // Enviar requisição
        fetch(url, {
            method: 'PUT',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(data)
        })
        .then(response => {
            if (response.ok) {
                console.log(`✅ OS #${osId} programada com sucesso para ${dateStr} com usuário ${userName}`);
                
                // Mostrar notificação
                showNotification(`OS #${osId} programada para ${userName}`, 'success');
                
                // Recarregar ordens de serviço
                if (typeof window.loadOrdensServico === 'function') {
                    setTimeout(window.loadOrdensServico, 500);
                }
            } else {
                console.error(`❌ Erro ao programar OS #${osId}: ${response.status} ${response.statusText}`);
                
                // Mostrar notificação
                showNotification(`Erro ao programar OS #${osId}`, 'error');
                
                // Tentar método alternativo
                programarOSLocalmente(osId, dateStr, userName);
            }
        })
        .catch(error => {
            console.error(`❌ Erro ao programar OS #${osId}: ${error}`);
            
            // Mostrar notificação
            showNotification(`Erro ao programar OS #${osId}`, 'error');
            
            // Tentar método alternativo
            programarOSLocalmente(osId, dateStr, userName);
        });
    }
}

// Função para programar OS localmente (versão radical)
function programarOSLocalmente(osId, dateStr, userName) {
    console.log(`🔄 Tentando programar OS #${osId} localmente (versão radical)`);
    
    // Verificar se a função original existe
    if (typeof window.programarOSLocalmente === 'function') {
        // Chamar a função original
        window.programarOSLocalmente(osId, dateStr, userName);
    } else {
        // Implementação alternativa
        
        // Encontrar a OS na lista
        const os = window.ordensServico.find(o => o.id == osId);
        if (os) {
            // Atualizar dados da OS
            os.data_programada = dateStr;
            os.usuario_responsavel = userName;
            os.status = 'programada';
            
            console.log(`✅ OS #${osId} programada localmente para ${dateStr} com usuário ${userName}`);
            
            // Mostrar notificação
            showNotification(`OS #${osId} programada para ${userName}`, 'success');
            
            // Recarregar ordens de serviço
            if (typeof window.renderPriorityLines === 'function') {
                setTimeout(window.renderPriorityLines, 500);
            }
        } else {
            console.error(`❌ OS #${osId} não encontrada na lista`);
            
            // Mostrar notificação
            showNotification(`Erro ao programar OS #${osId}`, 'error');
        }
    }
}

// Função para mostrar notificação (versão radical)
function showNotification(message, type = 'info') {
    console.log(`🔔 Notificação: ${message} (${type})`);
    
    // Verificar se a função original existe
    if (typeof window.showNotification === 'function') {
        // Chamar a função original
        window.showNotification(message, type);
    } else {
        // Implementação alternativa
        
        // Remover notificações existentes
        document.querySelectorAll('.notification').forEach(notification => {
            notification.remove();
        });
        
        // Criar elemento de notificação
        const notification = document.createElement('div');
        notification.className = `notification ${type}`;
        notification.textContent = message;
        
        // Adicionar ao DOM
        document.body.appendChild(notification);
        
        // Mostrar notificação
        setTimeout(() => {
            notification.classList.add('show');
        }, 10);
        
        // Remover notificação após 5 segundos
        setTimeout(() => {
            notification.classList.remove('show');
            setTimeout(() => {
                notification.remove();
            }, 300);
        }, 5000);
    }
}

// Sobrescrever a função desprogramarOS para reinicializar os eventos após desprogramação
if (typeof window.desprogramarOS === 'function') {
    console.log('✅ Função desprogramarOS encontrada, aplicando correção radical...');
    
    // Salvar a função original
    window.desprogramarOS_original = window.desprogramarOS;
    
    // Sobrescrever a função
    window.desprogramarOS = function(osId) {
        console.log(`🔧 Função desprogramarOS radical executada para OS #${osId}`);
        
        // Chamar a função original
        const result = window.desprogramarOS_original(osId);
        
        // Após desprogramação, reinicializar o sistema de drag and drop
        setTimeout(function() {
            console.log('🔄 Desprogramação concluída, reinicializando sistema de drag and drop...');
            inicializarDragDropRadical();
            
            // Forçar a recriação dos cards de OS
            setTimeout(function() {
                console.log('🔄 Forçando renderização das linhas de prioridade...');
                if (typeof window.renderPriorityLines === 'function') {
                    window.renderPriorityLines();
                    
                    // Reinicializar novamente após renderização
                    setTimeout(inicializarDragDropRadical, 500);
                }
            }, 500);
        }, 1000);
        
        return result;
    };
}

// Função para adicionar atributos data-user-name a todos os elementos de usuário
function adicionarAtributosUsuario() {
    console.log('🔧 Adicionando atributos de usuário (versão radical)...');
    
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

// Aplicar correções quando o DOM estiver carregado
document.addEventListener('DOMContentLoaded', function() {
    console.log('🔧 DOM carregado, aplicando solução radical...');
    
    // Adicionar atributos de usuário
    setTimeout(adicionarAtributosUsuario, 500);
    
    // Inicializar sistema de drag and drop radical
    setTimeout(inicializarDragDropRadical, 1000);
});

// Aplicar correções imediatamente se o DOM já estiver carregado
if (document.readyState === 'complete' || document.readyState === 'interactive') {
    console.log('🔧 DOM já carregado, aplicando solução radical imediatamente...');
    
    // Adicionar atributos de usuário
    setTimeout(adicionarAtributosUsuario, 500);
    
    // Inicializar sistema de drag and drop radical
    setTimeout(inicializarDragDropRadical, 1000);
}

// Configurar um observador para adicionar atributos a novos elementos
const observer = new MutationObserver(function(mutations) {
    mutations.forEach(function(mutation) {
        if (mutation.type === 'childList' && mutation.addedNodes.length > 0) {
            // Verificar se novos elementos foram adicionados
            setTimeout(function() {
                adicionarAtributosUsuario();
                inicializarDragDropRadical();
            }, 100);
        }
    });
});

// Configurar observador para todo o documento
observer.observe(document.body, {
    childList: true,
    subtree: true
});

// Adicionar botão de reinicialização
function adicionarBotaoReinicializacao() {
    console.log('🔧 Adicionando botão de reinicialização...');
    
    // Criar botão
    const botao = document.createElement('button');
    botao.textContent = '🔄 Reinicializar Drag & Drop';
    botao.style.position = 'fixed';
    botao.style.bottom = '20px';
    botao.style.right = '20px';
    botao.style.zIndex = '9999';
    botao.style.padding = '10px 15px';
    botao.style.backgroundColor = '#6c5ce7';
    botao.style.color = 'white';
    botao.style.border = 'none';
    botao.style.borderRadius = '5px';
    botao.style.cursor = 'pointer';
    botao.style.boxShadow = '0 2px 5px rgba(0,0,0,0.2)';
    
    // Adicionar evento de clique
    botao.addEventListener('click', function() {
        console.log('🔄 Reinicializando sistema de drag and drop manualmente...');
        inicializarDragDropRadical();
        showNotification('Sistema de drag and drop reinicializado', 'info');
    });
    
    // Adicionar ao DOM
    document.body.appendChild(botao);
}

// Adicionar botão de reinicialização
setTimeout(adicionarBotaoReinicializacao, 2000);

console.log('✅ Solução radical para drag and drop carregada com sucesso!');

