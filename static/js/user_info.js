// Função global para carregar informações do usuário logado
function loadCurrentUserInfo() {
    console.log('🔄 Carregando informações do usuário...');
    
    fetch('/api/user', {
        method: 'GET',
        credentials: 'include',
        headers: {
            'Content-Type': 'application/json'
        }
    })
    .then(response => {
        console.log('📡 Resposta da API user:', response.status);
        return response.json();
    })
    .then(data => {
        console.log('📊 Dados recebidos:', data);
        
        if (data.success && data.user) {
            // Atualizar nome e empresa do usuário na interface
            const userNameElement = document.getElementById('user-name');
            const userCompanyElement = document.getElementById('user-company');
            
            if (userNameElement && data.user.name) {
                userNameElement.textContent = data.user.name;
                console.log('✅ Nome do usuário atualizado:', data.user.name);
            }
            
            if (userCompanyElement && data.user.company) {
                userCompanyElement.textContent = data.user.company;
                console.log('✅ Empresa atualizada:', data.user.company);
            }
            
            console.log('✅ Informações do usuário carregadas com sucesso!');
        } else {
            console.warn('⚠️ Resposta da API inválida:', data.message || 'Dados não encontrados');
            setDefaultUserInfo();
        }
    })
    .catch(error => {
        console.error('❌ Erro ao buscar informações do usuário:', error);
        setDefaultUserInfo();
    });
}

// Função para definir informações padrão do usuário
function setDefaultUserInfo() {
    console.log('🔄 Definindo informações padrão do usuário...');
    
    const userNameElement = document.getElementById('user-name');
    const userCompanyElement = document.getElementById('user-company');
    
    if (userNameElement) {
        userNameElement.textContent = 'Usuário Logado';
        console.log('📝 Nome padrão definido: Usuário Logado');
    }
    
    if (userCompanyElement) {
        userCompanyElement.textContent = 'Empresa Ativa';
        console.log('📝 Empresa padrão definida: Empresa Ativa');
    }
}

// Função para inicializar o menu de usuário
function initializeUserMenu() {
    console.log('🔄 Inicializando menu de usuário...');
    
    // User dropdown functionality
    const userDropdownBtn = document.querySelector('.user-dropdown-btn');
    const userDropdownContent = document.querySelector('.user-dropdown-content');
    
    if (userDropdownBtn && userDropdownContent) {
        console.log('✅ Elementos do menu encontrados');
        
        // Toggle dropdown on click
        userDropdownBtn.addEventListener('click', function(e) {
            e.preventDefault();
            e.stopPropagation();
            
            const isVisible = userDropdownContent.classList.contains('show');
            console.log('🖱️ Clique no menu de usuário. Visível:', isVisible);
            
            userDropdownContent.classList.toggle('show');
            
            if (!isVisible) {
                console.log('📂 Menu aberto');
            } else {
                console.log('📁 Menu fechado');
            }
        });

        // Close dropdown when clicking outside
        document.addEventListener('click', function(e) {
            if (!e.target.closest('.user-dropdown')) {
                if (userDropdownContent.classList.contains('show')) {
                    userDropdownContent.classList.remove('show');
                    console.log('📁 Menu fechado (clique fora)');
                }
            }
        });
        
        console.log('✅ Menu de usuário inicializado com sucesso!');
    } else {
        console.warn('⚠️ Elementos do menu de usuário não encontrados');
        console.log('🔍 userDropdownBtn:', userDropdownBtn);
        console.log('🔍 userDropdownContent:', userDropdownContent);
    }

    // Logout functionality
    const logoutBtn = document.getElementById('logout-btn');
    if (logoutBtn) {
        logoutBtn.addEventListener('click', function(e) {
            e.preventDefault();
            console.log('🚪 Tentativa de logout...');
            
            fetch('/api/logout', {
                method: 'POST',
                credentials: 'include',
                headers: {
                    'Content-Type': 'application/json'
                }
            })
            .then(response => response.json())
            .then(data => {
                console.log('📡 Resposta do logout:', data);
                if (data.success) {
                    console.log('✅ Logout realizado com sucesso');
                    window.location.href = '/';
                } else {
                    console.error('❌ Erro no logout:', data.message);
                    alert('Erro ao fazer logout. Tente novamente.');
                }
            })
            .catch(error => {
                console.error('❌ Erro de conexão no logout:', error);
                alert('Erro de conexão. Tente novamente mais tarde.');
            });
        });
        
        console.log('✅ Funcionalidade de logout configurada');
    } else {
        console.warn('⚠️ Botão de logout não encontrado');
    }
}

// Carregar informações do usuário quando a página carregar
document.addEventListener('DOMContentLoaded', function() {
    console.log('🚀 DOM carregado - Inicializando sistema de usuário...');
    
    // Aguardar um pouco para garantir que todos os elementos estejam prontos
    setTimeout(() => {
        loadCurrentUserInfo();
        initializeUserMenu();
    }, 100);
});

// Função para recarregar informações do usuário (pode ser chamada externamente)
function reloadUserInfo() {
    console.log('🔄 Recarregando informações do usuário...');
    loadCurrentUserInfo();
}

// Exportar funções para uso global
window.loadCurrentUserInfo = loadCurrentUserInfo;
window.reloadUserInfo = reloadUserInfo;

