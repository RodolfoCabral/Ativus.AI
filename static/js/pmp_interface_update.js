/**
 * Script para forçar atualização da interface após geração de OS PMP
 */

// Função para forçar recarregamento completo da programação
function forcarRecarregamentoProgramacao() {
    console.log('🔄 Forçando recarregamento completo da programação...');
    
    // Limpar dados existentes
    if (typeof ordensServico !== 'undefined') {
        ordensServico.length = 0;
    }
    
    // Recarregar dados
    if (typeof loadOrdensServico === 'function') {
        loadOrdensServico().then(() => {
            if (typeof renderPriorityLines === 'function') {
                renderPriorityLines();
                console.log('✅ Interface atualizada com novas OS');
            }
        }).catch(error => {
            console.error('❌ Erro ao recarregar:', error);
        });
    }
}

// Função para verificar e mostrar OS preventivas
function verificarOSPreventivas() {
    console.log('🔍 Verificando OS preventivas na interface...');
    
    if (typeof ordensServico !== 'undefined' && ordensServico.length > 0) {
        const preventivas = ordensServico.filter(os => {
            return (os.prioridade === 'preventiva' || 
                   os.pmp_id || 
                   os.tipo_manutencao === 'preventiva-periodica' ||
                   (os.descricao && os.descricao.toLowerCase().includes('pmp'))) &&
                   (os.status === 'aberta' || os.status === 'programada');
        });
        
        console.log(`📊 Total de OS preventivas encontradas: ${preventivas.length}`);
        
        if (preventivas.length > 0) {
            console.log('📋 Detalhes das OS preventivas:');
            preventivas.forEach((os, index) => {
                console.log(`   ${index + 1}. ID: ${os.id}, Descrição: ${os.descricao?.substring(0, 50)}..., Status: ${os.status}, PMP ID: ${os.pmp_id}`);
            });
        }
        
        return preventivas;
    }
    
    return [];
}

// Função para monitorar mudanças na programação
function monitorarMudancasProgramacao() {
    let ultimaContagem = 0;
    
    setInterval(() => {
        if (typeof ordensServico !== 'undefined') {
            const contagemAtual = ordensServico.length;
            
            if (contagemAtual !== ultimaContagem) {
                console.log(`📈 Mudança detectada: ${ultimaContagem} → ${contagemAtual} OS`);
                ultimaContagem = contagemAtual;
                
                // Verificar preventivas
                const preventivas = verificarOSPreventivas();
                
                if (preventivas.length > 0) {
                    console.log('🎯 Forçando renderização das preventivas...');
                    if (typeof renderPriorityLines === 'function') {
                        renderPriorityLines();
                    }
                }
            }
        }
    }, 5000); // Verificar a cada 5 segundos
}

// Função para debug da linha preventiva
function debugLinhaPreventiva() {
    console.log('🔧 DEBUG - Analisando linha preventiva...');
    
    const container = document.getElementById('chamados-preventiva');
    if (container) {
        console.log('📦 Container preventiva encontrado:', container);
        console.log('📄 Conteúdo atual:', container.innerHTML.substring(0, 200) + '...');
    } else {
        console.error('❌ Container preventiva não encontrado!');
    }
    
    // Verificar OS preventivas
    const preventivas = verificarOSPreventivas();
    
    if (preventivas.length > 0) {
        console.log('✅ OS preventivas existem, mas podem não estar sendo renderizadas');
        console.log('🔄 Tentando forçar renderização...');
        
        if (typeof renderPriorityLines === 'function') {
            renderPriorityLines();
            
            setTimeout(() => {
                const containerApos = document.getElementById('chamados-preventiva');
                if (containerApos) {
                    console.log('📄 Conteúdo após renderização:', containerApos.innerHTML.substring(0, 200) + '...');
                }
            }, 1000);
        }
    } else {
        console.log('⚠️ Nenhuma OS preventiva encontrada nos dados');
    }
}

// Inicializar monitoramento quando a página carregar
document.addEventListener('DOMContentLoaded', function() {
    console.log('🚀 Iniciando monitoramento de interface PMP...');
    
    // Aguardar 5 segundos para a página carregar completamente
    setTimeout(() => {
        monitorarMudancasProgramacao();
        
        // Debug inicial
        setTimeout(debugLinhaPreventiva, 2000);
    }, 5000);
});

// Exportar funções para uso global
window.forcarRecarregamentoProgramacao = forcarRecarregamentoProgramacao;
window.verificarOSPreventivas = verificarOSPreventivas;
window.debugLinhaPreventiva = debugLinhaPreventiva;
