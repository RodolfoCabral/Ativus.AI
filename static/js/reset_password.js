document.addEventListener('DOMContentLoaded', function() {
    const resetPasswordForm = document.getElementById('reset-password-form');
    const messageContainer = document.getElementById('message-container');
    
    if (resetPasswordForm) {
        resetPasswordForm.addEventListener('submit', function(e) {
            e.preventDefault();
            
            const currentPassword = document.getElementById('current-password').value;
            const newPassword = document.getElementById('new-password').value;
            const confirmPassword = document.getElementById('confirm-password').value;
            
            // Limpar mensagens anteriores
            messageContainer.textContent = '';
            messageContainer.className = 'message';
            messageContainer.style.display = 'none';
            
            // Validar senhas
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
            
            // Enviar requisição para a API de redefinição de senha
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
                    showMessage(data.message || 'Erro ao alterar senha. Verifique se a senha atual está correta.', 'error');
                }
            })
            .catch(error => {
                console.error('Erro:', error);
                showMessage('Erro de conexão. Tente novamente mais tarde.', 'error');
            });
        });
    }
    
    // Exibir mensagem
    function showMessage(text, type) {
        messageContainer.textContent = text;
        messageContainer.className = `message ${type}`;
        messageContainer.style.display = 'block';
        
        // Rolar para o topo para garantir que a mensagem seja vista
        window.scrollTo(0, 0);
        
        // Se for uma mensagem de sucesso, redirecionar após alguns segundos
        if (type === 'success') {
            setTimeout(() => {
                window.location.href = '/dashboard';
            }, 3000);
        }
    }
});

    // Carregar informações do usuário logado
    function loadCurrentUserInfo() {
        fetch('/api/user')
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    // Atualizar nome e empresa do usuário na interface
                    const userNameElement = document.getElementById('user-name');
                    const userCompanyElement = document.getElementById('user-company');
                    
                    if (userNameElement && data.user.name) {
                        userNameElement.textContent = data.user.name;
                    }
                    
                    if (userCompanyElement && data.user.company) {
                        userCompanyElement.textContent = data.user.company;
                    }
                    
                    console.log('Informações do usuário carregadas:', data.user);
                } else {
                    console.error('Erro ao carregar informações do usuário:', data.message);
                    // Manter valores padrão se houver erro
                    const userNameElement = document.getElementById('user-name');
                    const userCompanyElement = document.getElementById('user-company');
                    
                    if (userNameElement) userNameElement.textContent = 'Usuário';
                    if (userCompanyElement) userCompanyElement.textContent = 'Empresa';
                }
            })
            .catch(error => {
                console.error('Erro ao buscar informações do usuário:', error);
                // Manter valores padrão se houver erro
                const userNameElement = document.getElementById('user-name');
                const userCompanyElement = document.getElementById('user-company');
                
                if (userNameElement) userNameElement.textContent = 'Usuário';
                if (userCompanyElement) userCompanyElement.textContent = 'Empresa';
            });
    }

    // Carregar informações do usuário quando a página carregar
    loadCurrentUserInfo();

