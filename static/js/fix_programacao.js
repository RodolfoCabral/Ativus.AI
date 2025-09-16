/**
 * FIX_PROGRAMACAO.JS
 * 
 * Este script corrige o problema de programação/desprogramação de OS.
 * 
 * PROBLEMA IDENTIFICADO:
 * - Quando uma OS é desprogramada e depois reprogramada, a data é enviada como "1" em vez de YYYY-MM-DD
 * - O usuário responsável é enviado como "Técnico #2025-09-13" em vez do nome real
 * 
 * SOLUÇÃO:
 * - Sobrescrever as funções problemáticas com versões corrigidas
 * - Garantir que os dados corretos sejam enviados para a API
 */

// Executar quando o DOM estiver carregado
document.addEventListener('DOMContentLoaded', function() {
    console.log('🔧 Aplicando correções para programação/desprogramação de OS...');
    
    // Aguardar um momento para garantir que os outros scripts foram carregados
    setTimeout(aplicarCorrecoes, 1000);
});

// Aplicar correções
function aplicarCorrecoes() {
    console.log('🔧 Aplicando correções para programação/desprogramação de OS...');
    
    // Sobrescrever a função handleDrop
    if (typeof window.handleDrop === 'function') {
        console.log('✅ Sobrescrevendo função handleDrop');
        window.handleDrop_original = window.handleDrop;
        window.handleDrop = handleDrop_corrigido;
    }
    
    // Sobrescrever a função programarOS
    if (typeof window.programarOS === 'function') {
        console.log('✅ Sobrescrevendo função programarOS');
        window.programarOS_original = window.programarOS;
        window.programarOS = programarOS_corrigido;
    }
    
    // Sobrescrever a função programarOSComNomeUsuario
    if (typeof window.programarOSComNomeUsuario === 'function') {
        console.log('✅ Sobrescrevendo função programarOSComNomeUsuario');
        window.programarOSComNomeUsuario_original = window.programarOSComNomeUsuario;
        window.programarOSComNomeUsuario = programarOSComNomeUsuario_corrigido;
    }
    
    // Sobrescrever a função desprogramarOS
    if (typeof window.desprogramarOS === 'function') {
        console.log('✅ Sobrescrevendo função desprogramarOS');
        window.desprogramarOS_original = window.desprogramarOS;
        window.desprogramarOS = desprogramarOS_corrigido;
    }
    
    console.log('✅ Correções aplicadas com sucesso!');
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
    
    // Obter ID e nome do usuário do elemento de destino
    const userId = this.getAttribute('data-user-id');
    const userName = this.getAttribute('data-user-name');
    
    console.log(`🔄 Drop detectado: OS #${osId} para data ${dateStr} com usuário ID ${userId}, nome: ${userName}`);
    
    // Verificar se a data está no formato correto (YYYY-MM-DD)
    if (!dateStr.match(/^\d{4}-\d{2}-\d{2}$/)) {
        console.error(`❌ Formato de data inválido: ${dateStr}`);
        if (typeof window.showNotification === 'function') {
            window.showNotification(`Erro: Formato de data inválido (${dateStr})`, 'error');
        }
        return false;
    }
    
    // Verificar se temos o nome do usuário
    if (!userName) {
        console.error('❌ Nome do usuário não encontrado');
        
        // Tentar obter o nome do usuário de outra forma
        const userRow = this.closest('.usuario-row');
        if (userRow) {
            const userNameElement = userRow.querySelector('.usuario-nome');
            if (userNameElement) {
                userName = userNameElement.textContent.trim();
                console.log(`✅ Nome do usuário obtido do DOM: ${userName}`);
            }
        }
        
        // Se ainda não temos o nome, usar um valor padrão
        if (!userName) {
            console.warn(`⚠️ Nome do usuário não encontrado, usando valor padrão`);
            userName = `Usuário #${userId}`;
        }
    }
    
    // Programar OS diretamente com o nome do usuário
    programarOSComNomeUsuario_corrigido(osId, dateStr, userName);
    
    return false;
}

// Função programarOS corrigida
function programarOS_corrigido(osId, userId, dateStr) {
    console.log(`🔄 Função programarOS_corrigido executada: OS #${osId}, usuário #${userId}, data ${dateStr}`);
    
    try {
        // Verificar se temos o ID da OS
        if (!osId) {
            console.error('❌ ID da OS não fornecido');
            if (typeof window.showNotification === 'function') {
                window.showNotification('Erro: ID da OS não fornecido', 'error');
            }
            return;
        }
        
        // Verificar se temos a data
        if (!dateStr) {
            console.error('❌ Data não fornecida');
            if (typeof window.showNotification === 'function') {
                window.showNotification('Erro: Data não fornecida', 'error');
            }
            return;
        }
        
        // Verificar se temos o ID do usuário
        if (!userId) {
            console.error('❌ ID do usuário não fornecido');
            if (typeof window.showNotification === 'function') {
                window.showNotification('Erro: ID do usuário não fornecido', 'error');
            }
            return;
        }
        
        // Verificar se a data está no formato correto (YYYY-MM-DD)
        if (!dateStr.match(/^\d{4}-\d{2}-\d{2}$/)) {
            console.error(`❌ Formato de data inválido: ${dateStr}`);
            if (typeof window.showNotification === 'function') {
                window.showNotification(`Erro: Formato de data inválido (${dateStr})`, 'error');
            }
            return;
        }
        
        // Obter nome do usuário
        let userName = null;
        
        // Método 1: Obter do DOM
        const userElements = document.querySelectorAll(`[data-user-id="${userId}"]`);
        if (userElements.length > 0) {
            for (const userElement of userElements) {
                const userRow = userElement.closest('.usuario-row');
                if (userRow) {
                    userName = userRow.getAttribute('data-user-name');
                    if (userName) {
                        console.log(`✅ Nome do usuário obtido do DOM: ${userName}`);
                        break;
                    }
                    
                    const userNameElement = userRow.querySelector('.usuario-nome');
                    if (userNameElement) {
                        userName = userNameElement.textContent.trim();
                        console.log(`✅ Nome do usuário obtido do DOM: ${userName}`);
                        break;
                    }
                }
            }
        }
        
        // Método 2: Obter da lista de usuários
        if (!userName && typeof window.usuarios !== 'undefined' && Array.isArray(window.usuarios)) {
            const usuario = window.usuarios.find(u => u.id == userId);
            if (usuario && usuario.name) {
                userName = usuario.name;
                console.log(`✅ Nome do usuário obtido da lista: ${userName}`);
            }
        }
        
        // Se ainda não temos o nome, usar um valor padrão
        if (!userName) {
            console.warn(`⚠️ Nome do usuário não encontrado para ID ${userId}`);
            userName = `Usuário #${userId}`;
        }
        
        // Programar OS com nome do usuário
        programarOSComNomeUsuario_corrigido(osId, dateStr, userName);
        
    } catch (error) {
        console.error('❌ Erro ao programar OS:', error);
        if (typeof window.showNotification === 'function') {
            window.showNotification(`Erro ao programar OS: ${error.message}`, 'error');
        }
    }
}

// Função programarOSComNomeUsuario corrigida
async function programarOSComNomeUsuario_corrigido(osId, date, userName) {
    console.log(`🔄 Função programarOSComNomeUsuario_corrigido executada: OS #${osId}, data ${date}, usuário ${userName}`);
    
    try {
        // Verificar se a data está no formato correto (YYYY-MM-DD)
        if (!date || !date.match(/^\d{4}-\d{2}-\d{2}$/)) {
            console.error(`❌ Formato de data inválido: ${date}`);
            if (typeof window.showNotification === 'function') {
                window.showNotification(`Erro: Formato de data inválido (${date})`, 'error');
            }
            return;
        }
        
        // Verificar se o nome do usuário é válido
        if (!userName) {
            console.error(`❌ Nome de usuário não fornecido`);
            if (typeof window.showNotification === 'function') {
                window.showNotification(`Erro: Nome de usuário não fornecido`, 'error');
            }
            return;
        }
        
        // Preparar dados para API
        const data = {
            id: parseInt(osId),
            data_programada: date,
            usuario_responsavel: userName,
            status: 'programada'
        };
        
        console.log('📤 Enviando dados para API:', data);
        
        // Enviar para API
        const response = await fetch(`/api/ordens-servico/${osId}/programar`, {
            method: 'PUT',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(data)
        });
        
        if (response.ok) {
            const responseData = await response.json();
            console.log('✅ OS programada com sucesso:', responseData);
            
            // Atualizar OS na lista local
            if (typeof window.ordensServico !== 'undefined' && Array.isArray(window.ordensServico)) {
                const osIndex = window.ordensServico.findIndex(os => os.id == osId);
                if (osIndex !== -1) {
                    window.ordensServico[osIndex].data_programada = date;
                    window.ordensServico[osIndex].usuario_responsavel = userName;
                    window.ordensServico[osIndex].status = 'programada';
                }
            }
            
            // Renderizar novamente
            if (typeof window.renderPriorityLines === 'function') window.renderPriorityLines();
            if (typeof window.renderUsuarios === 'function') window.renderUsuarios();
            
            // Mostrar notificação de sucesso com data formatada
            const dataFormatada = formatarData(date);
            if (typeof window.showNotification === 'function') {
                window.showNotification(`OS #${osId} programada para ${dataFormatada} com ${userName}`, 'success');
            }
        } else {
            // Tentar obter mensagem de erro
            let errorMessage = 'Erro ao programar OS';
            try {
                const errorData = await response.json();
                errorMessage = errorData.error || errorMessage;
            } catch (e) {
                console.error('Erro ao processar resposta de erro:', e);
            }
            
            console.error(`❌ Erro ao programar OS: ${errorMessage}`);
            if (typeof window.showNotification === 'function') {
                window.showNotification(`Erro: ${errorMessage}`, 'error');
            }
            
            // Método alternativo: programar localmente
            programarOSLocalmente(osId, date, userName);
        }
    } catch (error) {
        console.error('❌ Erro ao programar OS:', error);
        if (typeof window.showNotification === 'function') {
            window.showNotification('Erro ao programar OS. Tentando método alternativo...', 'error');
        }
        
        // Método alternativo: programar localmente
        programarOSLocalmente(osId, date, userName);
    }
}

// Função para programar OS localmente
function programarOSLocalmente(osId, date, userName) {
    console.log(`🔄 Programando OS #${osId} localmente para ${date} com usuário ${userName}`);
    
    try {
        // Atualizar OS na lista local
        if (typeof window.ordensServico !== 'undefined' && Array.isArray(window.ordensServico)) {
            const osIndex = window.ordensServico.findIndex(os => os.id == osId);
            if (osIndex !== -1) {
                window.ordensServico[osIndex].data_programada = date;
                window.ordensServico[osIndex].usuario_responsavel = userName;
                window.ordensServico[osIndex].status = 'programada';
                
                console.log('✅ OS programada localmente com sucesso');
                
                // Renderizar novamente
                if (typeof window.renderPriorityLines === 'function') window.renderPriorityLines();
                if (typeof window.renderUsuarios === 'function') window.renderUsuarios();
                
                // Mostrar notificação de sucesso com data formatada
                const dataFormatada = formatarData(date);
                if (typeof window.showNotification === 'function') {
                    window.showNotification(`OS #${osId} programada para ${dataFormatada} com ${userName} (modo local)`, 'success');
                }
                
                return true;
            } else {
                console.error(`❌ OS #${osId} não encontrada na lista local`);
                if (typeof window.showNotification === 'function') {
                    window.showNotification(`Erro: OS #${osId} não encontrada`, 'error');
                }
                return false;
            }
        } else {
            console.error('❌ Lista de ordens de serviço não disponível');
            if (typeof window.showNotification === 'function') {
                window.showNotification('Erro: Lista de ordens de serviço não disponível', 'error');
            }
            return false;
        }
    } catch (error) {
        console.error('❌ Erro ao programar OS localmente:', error);
        if (typeof window.showNotification === 'function') {
            window.showNotification('Erro ao programar OS localmente', 'error');
        }
        return false;
    }
}

// Função desprogramarOS corrigida
async function desprogramarOS_corrigido(osId) {
    console.log(`🔄 Função desprogramarOS_corrigido executada: OS #${osId}`);
    
    try {
        // Verificar se temos o ID da OS
        if (!osId) {
            console.error('❌ ID da OS não fornecido');
            if (typeof window.showNotification === 'function') {
                window.showNotification('Erro: ID da OS não fornecido', 'error');
            }
            return;
        }
        
        // Enviar para API
        const response = await fetch(`/api/ordens-servico/${osId}/desprogramar`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            }
        });
        
        if (response.ok) {
            const result = await response.json();
            console.log('✅ OS desprogramada com sucesso:', result);
            
            // Atualizar OS na lista local
            if (typeof window.ordensServico !== 'undefined' && Array.isArray(window.ordensServico)) {
                const osIndex = window.ordensServico.findIndex(os => os.id == osId);
                if (osIndex !== -1) {
                    window.ordensServico[osIndex].data_programada = null;
                    window.ordensServico[osIndex].usuario_responsavel = null;
                    window.ordensServico[osIndex].status = 'aberta';
                }
            }
            
            // Renderizar novamente
            if (typeof window.renderPriorityLines === 'function') window.renderPriorityLines();
            if (typeof window.renderUsuarios === 'function') window.renderUsuarios();
            
            // Mostrar notificação
            if (typeof window.showNotification === 'function') {
                window.showNotification(`OS #${osId} desprogramada com sucesso`, 'success');
            }
        } else {
            // Tentar obter mensagem de erro
            let errorMessage = 'Erro ao desprogramar OS';
            try {
                const errorData = await response.json();
                errorMessage = errorData.error || errorMessage;
            } catch (e) {
                console.error('Erro ao processar resposta de erro:', e);
            }
            
            console.error(`❌ Erro ao desprogramar OS: ${errorMessage}`);
            if (typeof window.showNotification === 'function') {
                window.showNotification(`Erro: ${errorMessage}`, 'error');
            }
            
            // Método alternativo: desprogramar localmente
            desprogramarOSLocalmente(osId);
        }
    } catch (error) {
        console.error('❌ Erro ao desprogramar OS:', error);
        if (typeof window.showNotification === 'function') {
            window.showNotification('Erro ao desprogramar OS. Tentando método alternativo...', 'error');
        }
        
        // Método alternativo: desprogramar localmente
        desprogramarOSLocalmente(osId);
    }
}

// Função para desprogramar OS localmente
function desprogramarOSLocalmente(osId) {
    console.log(`🔄 Desprogramando OS #${osId} localmente`);
    
    try {
        // Atualizar OS na lista local
        if (typeof window.ordensServico !== 'undefined' && Array.isArray(window.ordensServico)) {
            const osIndex = window.ordensServico.findIndex(os => os.id == osId);
            if (osIndex !== -1) {
                window.ordensServico[osIndex].data_programada = null;
                window.ordensServico[osIndex].usuario_responsavel = null;
                window.ordensServico[osIndex].status = 'aberta';
                
                console.log('✅ OS desprogramada localmente com sucesso');
                
                // Renderizar novamente
                if (typeof window.renderPriorityLines === 'function') window.renderPriorityLines();
                if (typeof window.renderUsuarios === 'function') window.renderUsuarios();
                
                // Mostrar notificação
                if (typeof window.showNotification === 'function') {
                    window.showNotification(`OS #${osId} desprogramada localmente`, 'success');
                }
                
                return true;
            } else {
                console.error(`❌ OS #${osId} não encontrada na lista local`);
                if (typeof window.showNotification === 'function') {
                    window.showNotification(`Erro: OS #${osId} não encontrada`, 'error');
                }
                return false;
            }
        } else {
            console.error('❌ Lista de ordens de serviço não disponível');
            if (typeof window.showNotification === 'function') {
                window.showNotification('Erro: Lista de ordens de serviço não disponível', 'error');
            }
            return false;
        }
    } catch (error) {
        console.error('❌ Erro ao desprogramar OS localmente:', error);
        if (typeof window.showNotification === 'function') {
            window.showNotification('Erro ao desprogramar OS localmente', 'error');
        }
        return false;
    }
}

// Função para formatar data
function formatarData(dateStr) {
    try {
        // Verificar se a data está no formato ISO (YYYY-MM-DD)
        if (dateStr && dateStr.match(/^\d{4}-\d{2}-\d{2}$/)) {
            const [year, month, day] = dateStr.split('-');
            return `${day}/${month}/${year}`;
        }
        
        // Tentar converter outras strings de data
        const date = new Date(dateStr);
        if (isNaN(date.getTime())) {
            console.error(`❌ Data inválida: ${dateStr}`);
            return dateStr; // Retornar a string original se não conseguir converter
        }
        
        // Formatar no padrão brasileiro
        const day = String(date.getDate()).padStart(2, '0');
        const month = String(date.getMonth() + 1).padStart(2, '0');
        const year = date.getFullYear();
        
        return `${day}/${month}/${year}`;
    } catch (e) {
        console.error(`❌ Erro ao formatar data: ${dateStr}`, e);
        return dateStr;
    }
}

// Aplicar correções imediatamente se o DOM já estiver carregado
if (document.readyState === 'complete' || document.readyState === 'interactive') {
    setTimeout(aplicarCorrecoes, 1000);
}

