// Função global para carregar informações do usuário logado
function loadCurrentUserInfo() {
    fetch('/api/user')
        .then(response => response.json())
        .then(data => {
            if (data.success && data.user) {
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
                console.error('Erro ao carregar informações do usuário:', data.message || 'Resposta inválida');
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
document.addEventListener('DOMContentLoaded', function() {
    loadCurrentUserInfo();
});

