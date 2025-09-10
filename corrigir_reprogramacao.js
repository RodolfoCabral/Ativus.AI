/**
 * Script para corrigir o problema de reprogramação de OS
 * 
 * Problema:
 * - Ao reprogramar uma OS, a data está sendo enviada como "1" em vez do formato correto "YYYY-MM-DD"
 * - O usuário responsável está sendo enviado como "Técnico #2025-09-09" em vez do nome correto
 * 
 * Solução:
 * - Corrigir a função handleDrop para garantir que a data e o usuário sejam passados corretamente
 * - Melhorar a função programarOS para obter o nome do usuário corretamente
 * - Adicionar validações robustas para garantir que os dados estejam no formato correto
 */

// Função corrigida para lidar com o drop de OS
function handleDrop(e) {
    e.stopPropagation();
    e.preventDefault();
    
    // Remover classe de hover
    this.classList.remove('drag-over');
    
    // Verificar se temos um elemento arrastado
    if (!draggedElement) {
        console.error('❌ Elemento arrastado não encontrado');
        return false;
    }
    
    // Obter ID da OS do elemento arrastado
    const osId = draggedElement.getAttribute('data-os-id');
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
        showNotification(`Erro: Formato de data inválido (${dateStr})`, 'error');
        return false;
    }
    
    // Verificar se temos o nome do usuário
    if (!userName) {
        console.error('❌ Nome do usuário não encontrado');
        showNotification('Erro: Nome do usuário não encontrado', 'error');
        return false;
    }
    
    // Programar OS diretamente com o nome do usuário
    programarOSComNomeUsuario(osId, dateStr, userName);
    
    return false;
}

// Função corrigida para programar OS com nome do usuário
async function programarOSComNomeUsuario(osId, date, userName) {
    try {
        console.log(`🔄 Programando OS #${osId} para ${date} com usuário ${userName}`);
        
        // Verificar se a data está no formato correto (YYYY-MM-DD)
        if (!date || !date.match(/^\d{4}-\d{2}-\d{2}$/)) {
            console.error(`❌ Formato de data inválido: ${date}`);
            showNotification(`Erro: Formato de data inválido (${date})`, 'error');
            return;
        }
        
        // Verificar se o nome do usuário é válido
        if (!userName || userName.startsWith('Técnico #')) {
            console.error(`❌ Nome de usuário inválido: ${userName}`);
            showNotification(`Erro: Nome de usuário inválido (${userName})`, 'error');
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
            const osIndex = ordensServico.findIndex(os => os.id == osId);
            if (osIndex !== -1) {
                ordensServico[osIndex].data_programada = date;
                ordensServico[osIndex].usuario_responsavel = userName;
                ordensServico[osIndex].status = 'programada';
            }
            
            // Renderizar novamente
            renderPriorityLines();
            renderUsuarios();
            
            // Mostrar notificação de sucesso com data formatada
            const dataFormatada = formatDate(date);
            showNotification(`OS #${osId} programada para ${dataFormatada} com ${userName}`, 'success');
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
            showNotification(`Erro: ${errorMessage}`, 'error');
            
            // Método alternativo: programar localmente
            programarOSAlternativa(osId, date, userName);
        }
    } catch (error) {
        console.error('❌ Erro ao programar OS:', error);
        showNotification('Erro ao programar OS. Tentando método alternativo...', 'error');
        
        // Método alternativo: programar localmente
        programarOSAlternativa(osId, date, userName);
    }
}

// Método alternativo para programar OS localmente
function programarOSAlternativa(osId, date, userName) {
    console.log(`🔄 Programando OS #${osId} localmente para ${date} com usuário ${userName}`);
    
    try {
        // Atualizar OS na lista local
        const osIndex = ordensServico.findIndex(os => os.id == osId);
        if (osIndex !== -1) {
            ordensServico[osIndex].data_programada = date;
            ordensServico[osIndex].usuario_responsavel = userName;
            ordensServico[osIndex].status = 'programada';
            
            console.log('✅ OS programada localmente com sucesso');
            
            // Renderizar novamente
            renderPriorityLines();
            renderUsuarios();
            
            // Mostrar notificação de sucesso com data formatada
            const dataFormatada = formatDate(date);
            showNotification(`OS #${osId} programada para ${dataFormatada} com ${userName} (modo local)`, 'success');
            
            return true;
        } else {
            console.error(`❌ OS #${osId} não encontrada na lista local`);
            showNotification(`Erro: OS #${osId} não encontrada`, 'error');
            return false;
        }
    } catch (error) {
        console.error('❌ Erro ao programar OS localmente:', error);
        showNotification('Erro ao programar OS localmente', 'error');
        return false;
    }
}

// Função para desprogramar OS
async function desprogramarOS(osId) {
    try {
        console.log(`🔄 Desprogramando OS #${osId}`);
        
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
            const osIndex = ordensServico.findIndex(os => os.id == osId);
            if (osIndex !== -1) {
                ordensServico[osIndex].data_programada = null;
                ordensServico[osIndex].usuario_responsavel = null;
                ordensServico[osIndex].status = 'aberta';
            }
            
            // Renderizar novamente
            renderPriorityLines();
            renderUsuarios();
            
            // Mostrar notificação
            showNotification(`OS #${osId} desprogramada com sucesso`, 'success');
        } else {
            throw new Error('Erro ao desprogramar OS');
        }
    } catch (error) {
        console.error('❌ Erro ao desprogramar OS:', error);
        showNotification('Erro ao desprogramar OS. Tentando método alternativo...', 'warning');
        
        // Método alternativo: desprogramar localmente
        desprogramarOSLocalmente(osId);
    }
}

// Método alternativo para desprogramar OS localmente
function desprogramarOSLocalmente(osId) {
    try {
        console.log(`🔄 Desprogramando OS #${osId} localmente`);
        
        // Atualizar OS na lista local
        const osIndex = ordensServico.findIndex(os => os.id == osId);
        if (osIndex !== -1) {
            ordensServico[osIndex].data_programada = null;
            ordensServico[osIndex].usuario_responsavel = null;
            ordensServico[osIndex].status = 'aberta';
            
            console.log('✅ OS desprogramada localmente com sucesso');
            
            // Renderizar novamente
            renderPriorityLines();
            renderUsuarios();
            
            // Mostrar notificação
            showNotification(`OS #${osId} desprogramada localmente`, 'success');
            
            return true;
        } else {
            console.error(`❌ OS #${osId} não encontrada na lista local`);
            showNotification(`Erro: OS #${osId} não encontrada`, 'error');
            return false;
        }
    } catch (error) {
        console.error('❌ Erro ao desprogramar OS localmente:', error);
        showNotification('Erro ao desprogramar OS localmente', 'error');
        return false;
    }
}

// Função para formatar data
function formatDate(dateStr) {
    try {
        // Verificar se a data está no formato ISO (YYYY-MM-DD)
        if (dateStr.match(/^\d{4}-\d{2}-\d{2}$/)) {
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

// Exportar funções para uso global
window.handleDrop = handleDrop;
window.programarOSComNomeUsuario = programarOSComNomeUsuario;
window.programarOSAlternativa = programarOSAlternativa;
window.desprogramarOS = desprogramarOS;
window.desprogramarOSLocalmente = desprogramarOSLocalmente;
window.formatDate = formatDate;

console.log('✅ Script de correção de reprogramação carregado com sucesso!');

