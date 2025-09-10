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
            renderUsuarios();
            renderPriorityLines();
            
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

