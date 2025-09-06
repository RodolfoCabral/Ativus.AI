// CORREÇÃO FINAL - PROGRAMAÇÃO COM API ALTERNATIVA
// Substitua a função loadOrdensServico() no arquivo programacao.js

// Carregar ordens de serviço em aberto
async function loadOrdensServico() {
    try {
        console.log('🔄 Carregando OS...');
        
        // CORREÇÃO: Tentar API original primeiro, depois alternativa
        let response;
        let data;
        
        try {
            // Tentar API original
            response = await fetch('/api/ordens-servico?status=abertas');
            if (response.ok) {
                data = await response.json();
                console.log('✅ API original funcionou');
            } else {
                throw new Error('API original falhou');
            }
        } catch (error) {
            console.warn('⚠️ API original falhou, tentando alternativa...');
            
            // Usar API alternativa
            response = await fetch('/api/ordens-servico-programacao?status=abertas');
            if (response.ok) {
                data = await response.json();
                console.log('✅ API alternativa funcionou');
            } else {
                throw new Error('Ambas APIs falharam');
            }
        }
        
        ordensServico = data.ordens_servico || [];
        console.log(`📊 Total de OS carregadas: ${ordensServico.length}`);
        
        // Debug: mostrar OS de PMP
        const osPMP = ordensServico.filter(os => os.pmp_id && os.pmp_id !== null);
        console.log(`🔧 OS de PMP encontradas: ${osPMP.length}`);
        
        if (osPMP.length > 0) {
            console.log('📋 OS de PMP:', osPMP.map(os => ({
                id: os.id,
                descricao: os.descricao.substring(0, 30) + '...',
                status: os.status,
                prioridade: os.prioridade,
                pmp_id: os.pmp_id
            })));
        }
        
        // Carregar também OS programadas
        try {
            let responseProgramadas;
            try {
                responseProgramadas = await fetch('/api/ordens-servico?status=programada');
            } catch {
                responseProgramadas = await fetch('/api/ordens-servico-programacao?status=programada');
            }
            
            if (responseProgramadas.ok) {
                const dataProgramadas = await responseProgramadas.json();
                const osProgramadas = dataProgramadas.ordens_servico || [];
                
                // Adicionar OS programadas à lista
                ordensServico = [...ordensServico, ...osProgramadas];
                console.log(`📊 OS programadas adicionadas: ${osProgramadas.length}`);
                console.log(`📊 Total final: ${ordensServico.length}`);
            }
        } catch (error) {
            console.warn('⚠️ Erro ao carregar OS programadas:', error);
        }
        
    } catch (error) {
        console.error('❌ Erro ao carregar OS:', error);
        ordensServico = [];
        
        // Mostrar notificação de erro para o usuário
        showNotification('Erro ao carregar ordens de serviço. Recarregue a página.', 'error');
    }
}

// CORREÇÃO: Função melhorada para renderizar prioridades
function renderPriorityLines() {
    const prioridades = ['baixa', 'media', 'alta', 'seguranca', 'preventiva'];
    
    console.log('🎨 Renderizando linhas de prioridade...');
    
    prioridades.forEach(prioridade => {
        const container = document.getElementById(`chamados-${prioridade}`);
        if (!container) {
            console.warn(`⚠️ Container não encontrado: chamados-${prioridade}`);
            return;
        }
        
        let osFiltered;
        if (prioridade === 'preventiva') {
            // CORREÇÃO: Lógica melhorada para preventivas
            osFiltered = ordensServico.filter(os => {
                // Condição 1: Prioridade preventiva normal
                const condicao1 = os.prioridade === 'preventiva' && 
                                 os.status === 'aberta' &&
                                 (!os.usuario_responsavel || os.usuario_responsavel === null || os.usuario_responsavel === '');
                
                // Condição 2: Qualquer OS de PMP aberta (independente da prioridade)
                const condicao2 = os.pmp_id && os.pmp_id !== null && os.status === 'aberta';
                
                return condicao1 || condicao2;
            });
            
            console.log(`🔧 Preventivas filtradas: ${osFiltered.length}`);
            if (osFiltered.length > 0) {
                console.log('📋 IDs das preventivas:', osFiltered.map(os => os.id));
            }
        } else {
            // Para outras prioridades: excluir OS de PMP
            osFiltered = ordensServico.filter(os => 
                os.prioridade === prioridade && 
                os.status === 'aberta' &&
                (!os.pmp_id || os.pmp_id === null)
            );
        }
        
        if (osFiltered.length === 0) {
            container.innerHTML = '<div class="empty-priority">Nenhuma OS nesta prioridade</div>';
            return;
        }
        
        // Renderizar cards
        container.innerHTML = osFiltered.map(os => createOSCard(os)).join('');
        
        // Adicionar funcionalidade de drag
        osFiltered.forEach(os => {
            const element = container.querySelector(`[data-os-id="${os.id}"]`);
            if (element) {
                addDragListeners(element);
            }
        });
        
        console.log(`✅ ${prioridade}: ${osFiltered.length} OS renderizadas`);
    });
}

// CORREÇÃO: Função de notificação melhorada
function showNotification(message, type = 'info') {
    // Remover notificação existente
    const existing = document.querySelector('.notification');
    if (existing) {
        existing.remove();
    }
    
    // Criar nova notificação
    const notification = document.createElement('div');
    notification.className = `notification notification-${type}`;
    notification.innerHTML = `
        <div class="notification-content">
            <span>${message}</span>
            <button onclick="this.parentElement.parentElement.remove()">×</button>
        </div>
    `;
    
    // Adicionar estilos se não existirem
    if (!document.getElementById('notification-styles')) {
        const styles = document.createElement('style');
        styles.id = 'notification-styles';
        styles.textContent = `
            .notification {
                position: fixed;
                top: 20px;
                right: 20px;
                padding: 15px;
                border-radius: 5px;
                color: white;
                z-index: 10000;
                max-width: 400px;
            }
            .notification-error { background: #f44336; }
            .notification-success { background: #4caf50; }
            .notification-info { background: #2196f3; }
            .notification-content {
                display: flex;
                justify-content: space-between;
                align-items: center;
            }
            .notification button {
                background: none;
                border: none;
                color: white;
                font-size: 18px;
                cursor: pointer;
                margin-left: 10px;
            }
        `;
        document.head.appendChild(styles);
    }
    
    // Adicionar ao DOM
    document.body.appendChild(notification);
    
    // Remover automaticamente após 5 segundos
    setTimeout(() => {
        if (notification.parentElement) {
            notification.remove();
        }
    }, 5000);
}

