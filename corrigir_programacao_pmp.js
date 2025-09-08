// CORREÇÃO PARA EXIBIR OS DE PMP NA TELA DE PROGRAMAÇÃO
// Substitua a função renderPriorityLines() no arquivo programacao.js

// Renderizar linhas de prioridade
function renderPriorityLines() {
    const prioridades = ['baixa', 'media', 'alta', 'seguranca', 'preventiva'];
    
    prioridades.forEach(prioridade => {
        const container = document.getElementById(`chamados-${prioridade}`);
        if (!container) return;
        
        // Filtrar OS por prioridade e status
        let osFiltered;
        if (prioridade === 'preventiva') {
            // CORREÇÃO: Para preventivas, incluir OS abertas sem usuário E OS de PMP
            osFiltered = ordensServico.filter(os => {
                // Condição 1: Prioridade preventiva e status aberta sem usuário responsável
                const condicao1 = os.prioridade === prioridade && 
                                 os.status === 'aberta' &&
                                 (!os.usuario_responsavel || os.usuario_responsavel === null || os.usuario_responsavel === '');
                
                // Condição 2: OS gerada por PMP (independente do status)
                const condicao2 = os.pmp_id && os.pmp_id !== null && os.status === 'aberta';
                
                return condicao1 || condicao2;
            });
        } else {
            // Para outras prioridades: apenas status 'aberta'
            osFiltered = ordensServico.filter(os => 
                os.prioridade === prioridade && 
                os.status === 'aberta' &&
                (!os.pmp_id || os.pmp_id === null) // Excluir OS de PMP das outras prioridades
            );
        }
        
        if (osFiltered.length === 0) {
            container.innerHTML = '<div class="empty-priority">Nenhuma OS nesta prioridade</div>';
            return;
        }
        
        container.innerHTML = osFiltered.map(os => createOSCard(os)).join('');
        
        // Adicionar funcionalidade de drag
        osFiltered.forEach(os => {
            const element = container.querySelector(`[data-os-id="${os.id}"]`);
            if (element) {
                addDragListeners(element);
            }
        });
    });
}

// CORREÇÃO: Atualizar função createOSCard para mostrar badge PMP
function createOSCard(os) {
    // Verificar se é OS de PMP
    const isPMP = os.pmp_id && os.pmp_id !== null;
    const pmpBadge = isPMP ? `<div class="pmp-badge">PMP</div>` : '';
    const frequenciaBadge = isPMP && os.frequencia_origem ? 
        `<div class="frequencia-badge">${os.frequencia_origem}</div>` : '';
    
    return `
        <div class="chamado-card ${isPMP ? 'pmp-card' : ''}" data-os-id="${os.id}" draggable="true" onclick="verificarExecucaoOS(${os.id})">
            <div class="chamado-header">
                <div class="chamado-id">OS #${os.id}</div>
                ${pmpBadge}
                ${frequenciaBadge}
            </div>
            <div class="chamado-descricao">${os.descricao}</div>
            <div class="chamado-info">
                <div class="info-line">
                    <i class="fas fa-tools"></i>
                    ${formatTipoManutencao(os.tipo_manutencao)}
                </div>
                <div class="info-line">
                    <i class="fas fa-industry"></i>
                    ${formatOficina(os.oficina)}
                </div>
                <div class="info-line">
                    <i class="fas fa-clock"></i>
                    ${os.hh}h (${os.qtd_pessoas}p × ${os.horas}h)
                </div>
                <div class="info-line">
                    <i class="fas fa-building"></i>
                    ${os.filial_tag} - ${os.setor_tag} - ${os.equipamento_tag}
                </div>
                ${isPMP ? `
                <div class="info-line pmp-info">
                    <i class="fas fa-calendar-alt"></i>
                    Próxima: ${formatDate(os.data_proxima_geracao)} | Seq: #${os.numero_sequencia || 1}
                </div>
                ` : ''}
            </div>
        </div>
    `;
}

// Função auxiliar para formatar data
function formatDate(dateString) {
    if (!dateString) return 'N/A';
    const date = new Date(dateString);
    return date.toLocaleDateString('pt-BR');
}

// CORREÇÃO: Adicionar estilos CSS para badges PMP
const pmpStyles = `
<style>
.pmp-card {
    border-left: 4px solid #9c27b0 !important;
    background: linear-gradient(135deg, #f8f4ff 0%, #ffffff 100%);
}

.chamado-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 8px;
}

.pmp-badge {
    background: #9c27b0;
    color: white;
    padding: 2px 8px;
    border-radius: 12px;
    font-size: 10px;
    font-weight: bold;
    text-transform: uppercase;
}

.frequencia-badge {
    background: #4caf50;
    color: white;
    padding: 2px 6px;
    border-radius: 8px;
    font-size: 9px;
    margin-left: 4px;
}

.pmp-info {
    color: #9c27b0;
    font-size: 11px;
    font-weight: 500;
}

.pmp-info i {
    color: #9c27b0;
}
</style>
`;

// Adicionar estilos ao head
if (!document.getElementById('pmp-styles')) {
    const styleElement = document.createElement('div');
    styleElement.id = 'pmp-styles';
    styleElement.innerHTML = pmpStyles;
    document.head.appendChild(styleElement);
}

