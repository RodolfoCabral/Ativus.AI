// Variáveis globais
let filiais = [];
let setores = [];
let equipamentos = [];
let userProfile = null;

// Inicialização da página
document.addEventListener('DOMContentLoaded', function() {
    console.log('Página de chamados carregada');
    carregarDadosIniciais();
    preencherDataHoraAtual();
    preencherNomeSolicitante();
});

// Carregar dados iniciais
async function carregarDadosIniciais() {
    try {
        // Carregar perfil do usuário
        await carregarPerfilUsuario();
        
        // Carregar filiais
        await carregarFiliais();
        
        console.log('Dados iniciais carregados com sucesso');
    } catch (error) {
        console.error('Erro ao carregar dados iniciais:', error);
        showNotification('Erro ao carregar dados iniciais', 'error');
    }
}

// Carregar perfil do usuário
async function carregarPerfilUsuario() {
    try {
        const response = await fetch('/api/user');
        if (response.ok) {
            userProfile = await response.json();
        } else {
            // Fallback se a API não estiver disponível
            userProfile = { profile: 'user', name: 'Usuário' };
        }
    } catch (error) {
        console.error('Erro ao carregar perfil do usuário:', error);
        userProfile = { profile: 'user', name: 'Usuário' };
    }
}

// Carregar filiais
async function carregarFiliais() {
    try {
        const response = await fetch('/api/filiais');
        if (response.ok) {
            const data = await response.json();
            filiais = data.filiais || [];
            
            const selectFilial = document.getElementById('filial');
            selectFilial.innerHTML = '<option value="">Selecione uma filial</option>';
            
            filiais.forEach(filial => {
                const option = document.createElement('option');
                option.value = filial.id;
                option.textContent = `${filial.tag} - ${filial.descricao}`;
                selectFilial.appendChild(option);
            });
        } else {
            throw new Error('Erro ao carregar filiais');
        }
    } catch (error) {
        console.error('Erro ao carregar filiais:', error);
        showNotification('Erro ao carregar filiais', 'error');
    }
}

// Carregar setores baseado na filial selecionada
async function carregarSetores() {
    const filialId = document.getElementById('filial').value;
    const selectSetor = document.getElementById('setor');
    const selectEquipamento = document.getElementById('equipamento');
    
    // Limpar setores e equipamentos
    selectSetor.innerHTML = '<option value="">Selecione um setor</option>';
    selectEquipamento.innerHTML = '<option value="">Selecione um equipamento</option>';
    selectSetor.disabled = true;
    selectEquipamento.disabled = true;
    
    if (!filialId) {
        return;
    }
    
    try {
        const response = await fetch(`/api/setores?filial_id=${filialId}`);
        if (response.ok) {
            const data = await response.json();
            setores = data.setores || [];
            
            if (setores.length > 0) {
                setores.forEach(setor => {
                    const option = document.createElement('option');
                    option.value = setor.id;
                    option.textContent = `${setor.tag} - ${setor.descricao}`;
                    selectSetor.appendChild(option);
                });
                selectSetor.disabled = false;
            } else {
                showNotification('Nenhum setor encontrado para esta filial', 'warning');
            }
        } else {
            throw new Error('Erro ao carregar setores');
        }
    } catch (error) {
        console.error('Erro ao carregar setores:', error);
        showNotification('Erro ao carregar setores', 'error');
    }
}

// Carregar equipamentos baseado no setor selecionado
async function carregarEquipamentos() {
    const setorId = document.getElementById('setor').value;
    const selectEquipamento = document.getElementById('equipamento');
    
    // Limpar equipamentos
    selectEquipamento.innerHTML = '<option value="">Selecione um equipamento</option>';
    selectEquipamento.disabled = true;
    
    if (!setorId) {
        return;
    }
    
    try {
        const response = await fetch(`/api/equipamentos?setor_id=${setorId}`);
        if (response.ok) {
            const data = await response.json();
            equipamentos = data.equipamentos || [];
            
            if (equipamentos.length > 0) {
                equipamentos.forEach(equipamento => {
                    const option = document.createElement('option');
                    option.value = equipamento.id;
                    option.textContent = `${equipamento.tag} - ${equipamento.descricao}`;
                    selectEquipamento.appendChild(option);
                });
                selectEquipamento.disabled = false;
            } else {
                showNotification('Nenhum equipamento encontrado para este setor', 'warning');
            }
        } else {
            throw new Error('Erro ao carregar equipamentos');
        }
    } catch (error) {
        console.error('Erro ao carregar equipamentos:', error);
        showNotification('Erro ao carregar equipamentos', 'error');
    }
}

// Preencher data e hora atual
function preencherDataHoraAtual() {
    const agora = new Date();
    const dataHoraFormatada = agora.toLocaleString('pt-BR', {
        day: '2-digit',
        month: '2-digit',
        year: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
    });
    
    document.getElementById('data_hora').value = dataHoraFormatada;
}

// Preencher nome do solicitante
function preencherNomeSolicitante() {
    const solicitanteInput = document.getElementById('solicitante');
    if (userProfile && userProfile.name) {
        solicitanteInput.value = userProfile.name;
    }
}

// Abrir modal de novo chamado
function openNovoChamadoForm() {
    const modal = document.getElementById('novo-chamado-modal');
    modal.classList.add('show');
    modal.style.display = 'flex';
    preencherDataHoraAtual();
    preencherNomeSolicitante();
}

// Fechar modal de novo chamado
function closeNovoChamadoModal() {
    document.getElementById('novo-chamado-modal').classList.remove('show');
    document.getElementById('novo-chamado-form').reset();
    // Resetar selects
    document.getElementById('setor').disabled = true;
    document.getElementById('equipamento').disabled = true;
}

// Navegar para outras páginas
function navigateTo(url) {
    window.location.href = url;
}

// Submeter formulário de novo chamado
document.getElementById('novo-chamado-form').addEventListener('submit', async function(e) {
    e.preventDefault();
    
    const formData = new FormData(this);
    const chamadoData = {
        descricao: formData.get('descricao'),
        filial_id: parseInt(formData.get('filial')),
        setor_id: parseInt(formData.get('setor')),
        equipamento_id: parseInt(formData.get('equipamento')),
        prioridade: formData.get('prioridade'),
        solicitante: formData.get('solicitante')
    };
    
    // Validar dados
    if (!chamadoData.descricao || !chamadoData.filial_id || !chamadoData.setor_id || 
        !chamadoData.equipamento_id || !chamadoData.prioridade || !chamadoData.solicitante) {
        showNotification('Por favor, preencha todos os campos obrigatórios', 'error');
        return;
    }
    
    try {
        // Mostrar indicador de carregamento
        const submitBtn = this.querySelector('button[type="submit"]');
        const originalText = submitBtn.textContent;
        submitBtn.textContent = 'Salvando...';
        submitBtn.disabled = true;
        
        const response = await fetch('/api/chamados', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(chamadoData)
        });
        
        const result = await response.json();
        
        if (response.ok && result.success) {
            showNotification('Chamado criado com sucesso!', 'success');
            closeNovoChamadoModal();
            
            // Opcional: redirecionar para lista de chamados
            setTimeout(() => {
                navigateTo('/chamados/abertos');
            }, 2000);
        } else {
            throw new Error(result.error || 'Erro ao criar chamado');
        }
        
    } catch (error) {
        console.error('Erro ao criar chamado:', error);
        showNotification(error.message || 'Erro ao criar chamado', 'error');
    } finally {
        // Restaurar botão
        const submitBtn = this.querySelector('button[type="submit"]');
        submitBtn.textContent = originalText;
        submitBtn.disabled = false;
    }
});

// Função para mostrar notificações
function showNotification(message, type = 'info') {
    // Remover notificação existente
    const existingNotification = document.querySelector('.notification');
    if (existingNotification) {
        existingNotification.remove();
    }
    
    // Criar nova notificação
    const notification = document.createElement('div');
    notification.className = `notification notification-${type}`;
    notification.style.cssText = `
        position: fixed;
        top: 20px;
        right: 20px;
        padding: 16px 24px;
        border-radius: 8px;
        color: white;
        font-weight: 500;
        z-index: 10000;
        max-width: 400px;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.2);
        animation: slideIn 0.3s ease-out;
    `;
    
    // Definir cor baseada no tipo
    const colors = {
        success: '#28a745',
        error: '#dc3545',
        warning: '#ffc107',
        info: '#17a2b8'
    };
    
    notification.style.backgroundColor = colors[type] || colors.info;
    notification.textContent = message;
    
    // Adicionar ao DOM
    document.body.appendChild(notification);
    
    // Remover após 5 segundos
    setTimeout(() => {
        if (notification.parentNode) {
            notification.style.animation = 'slideOut 0.3s ease-in';
            setTimeout(() => {
                if (notification.parentNode) {
                    notification.remove();
                }
            }, 300);
        }
    }, 5000);
}

// Adicionar estilos de animação
const style = document.createElement('style');
style.textContent = `
    @keyframes slideIn {
        from {
            transform: translateX(100%);
            opacity: 0;
        }
        to {
            transform: translateX(0);
            opacity: 1;
        }
    }
    
    @keyframes slideOut {
        from {
            transform: translateX(0);
            opacity: 1;
        }
        to {
            transform: translateX(100%);
            opacity: 0;
        }
    }
    
    .modal-backdrop {
        position: fixed;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        background: rgba(0, 0, 0, 0.5);
        display: flex;
        justify-content: center;
        align-items: center;
        z-index: 1000;
    }
    
    .modal {
        background: white;
        border-radius: 12px;
        padding: 0;
        max-width: 90%;
        max-height: 90%;
        overflow-y: auto;
        box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
    }
    
    .modal-header {
        padding: 24px 24px 0 24px;
        border-bottom: 1px solid #eee;
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 24px;
    }
    
    .modal-title {
        margin: 0;
        font-size: 24px;
        font-weight: 600;
        color: #333;
    }
    
    .modal-close {
        background: none;
        border: none;
        font-size: 24px;
        cursor: pointer;
        color: #999;
        padding: 0;
        width: 32px;
        height: 32px;
        display: flex;
        align-items: center;
        justify-content: center;
        border-radius: 50%;
        transition: all 0.2s ease;
    }
    
    .modal-close:hover {
        background: #f5f5f5;
        color: #333;
    }
    
    .modal-body {
        padding: 0 24px 24px 24px;
    }
`;
document.head.appendChild(style);

window.openNovoChamadoForm = openNovoChamadoForm;
window.closeNovoChamadoModal = closeNovoChamadoModal;
window.carregarSetores = carregarSetores;
window.carregarEquipamentos = carregarEquipamentos;
