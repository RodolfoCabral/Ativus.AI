document.addEventListener('DOMContentLoaded', function() {
    // Verificar se estamos na página de redefinição de senha
    const resetPasswordForm = document.getElementById('reset-password-form');
    if (!resetPasswordForm) return;

    resetPasswordForm.addEventListener('submit', function(e) {
        e.preventDefault();
        
        const currentPassword = document.getElementById('current-password').value;
        const newPassword = document.getElementById('new-password').value;
        const confirmPassword = document.getElementById('confirm-password').value;
        const messageContainer = document.getElementById('message-container');
        
        // Validações
        if (!currentPassword || !newPassword || !confirmPassword) {
            showMessage('Por favor, preencha todos os campos.', 'error');
            return;
        }
        
        if (newPassword !== confirmPassword) {
            showMessage('A nova senha e a confirmação não coincidem.', 'error');
            return;
        }
        
        if (newPassword.length < 6) {
            showMessage('A nova senha deve ter pelo menos 6 caracteres.', 'error');
            return;
        }
        
        // Enviar dados para o servidor
        fetch('/api/reset-password', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                current_password: currentPassword,
                new_password: newPassword
            }),
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                showMessage('Senha alterada com sucesso!', 'success');
                resetPasswordForm.reset();
            } else {
                showMessage(data.message || 'Erro ao alterar senha', 'error');
            }
        })
        .catch(error => {
            console.error('Erro:', error);
            showMessage('Erro de conexão. Tente novamente mais tarde.', 'error');
        });
    });
    
    // Função para exibir mensagens
    function showMessage(text, type) {
        const messageContainer = document.getElementById('message-container');
        if (!messageContainer) return;
        
        messageContainer.textContent = text;
        messageContainer.className = `message ${type}`;
        messageContainer.style.display = 'block';
        
        // Ocultar mensagem após alguns segundos
        setTimeout(() => {
            messageContainer.style.display = 'none';
        }, 5000);
    }
});

