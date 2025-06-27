document.addEventListener('DOMContentLoaded', function() {
    // Variáveis globais
    let currentUserProfile = '';
    let currentUserCompany = '';
    let usersList = [];
    
    // Toggle sidebar
    const sidebarToggle = document.getElementById('sidebar-toggle');
    const dashboardContainer = document.querySelector('.dashboard-container');
    const sidebar = document.querySelector('.sidebar');
    const sidebarOverlay = document.getElementById('sidebar-overlay');
    
    if (sidebarToggle) {
        sidebarToggle.addEventListener('click', function() {
            if (window.innerWidth <= 768) {
                // Em mobile, usar classe mobile-open e mostrar overlay
                sidebar.classList.toggle('mobile-open');
                if (sidebarOverlay) {
                    sidebarOverlay.classList.toggle('show');
                }
            } else {
                // Em desktop, usar classe sidebar-collapsed
                dashboardContainer.classList.toggle('sidebar-collapsed');
            }
        });
    }
    
    // Fechar sidebar em mobile quando clicar no overlay
    if (sidebarOverlay) {
        sidebarOverlay.addEventListener('click', function() {
            sidebar.classList.remove('mobile-open');
            sidebarOverlay.classList.remove('show');
        });
    }
    
    // Fechar sidebar em mobile quando clicar fora
    document.addEventListener('click', function(e) {
        if (window.innerWidth <= 768) {
            if (!e.target.closest('.sidebar') && !e.target.closest('.sidebar-toggle')) {
                sidebar.classList.remove('mobile-open');
                if (sidebarOverlay) {
                    sidebarOverlay.classList.remove('show');
                }
            }
        }
    });
    
    // Ajustar comportamento ao redimensionar janela
    window.addEventListener('resize', function() {
        if (window.innerWidth > 768) {
            sidebar.classList.remove('mobile-open');
            if (sidebarOverlay) {
                sidebarOverlay.classList.remove('show');
            }
        } else {
            dashboardContainer.classList.remove('sidebar-collapsed');
        }
    });
    
    // Verificar o perfil do usuário atual
    function checkCurrentUserProfile() {
        fetch('/api/user')
            .then(response => response.json())
            .then(data => {
                if (data.success && data.user) {
                    currentUserProfile = data.user.profile;
                    currentUserCompany = data.user.company;
                    loadUsers();
                } else {
                    console.error('Erro ao obter perfil do usuário:', data.message);
                    showMessage('Erro ao carregar informações do usuário. Tente novamente mais tarde.', 'error');
                }
            })
            .catch(error => {
                console.error('Erro ao obter perfil do usuário:', error);
                showMessage('Erro ao carregar informações do usuário. Tente novamente mais tarde.', 'error');
            });
    }
    
    // Carregar lista de usuários
    function loadUsers() {
        fetch('/api/users')
            .then(response => {
                if (!response.ok) {
                    throw new Error('Erro ao carregar usuários');
                }
                return response.json();
            })
            .then(data => {
                if (data.success) {
                    usersList = data.users;
                    renderUsersTable();
                } else {
                    showMessage(data.message || 'Erro ao carregar usuários', 'error');
                }
            })
            .catch(error => {
                console.error('Erro:', error);
                showMessage('Erro ao carregar usuários. Tente novamente mais tarde.', 'error');
            });
    }
    
    // Renderizar tabela de usuários
    function renderUsersTable() {
        const tableBody = document.getElementById('users-table-body');
        if (!tableBody) return;
        
        tableBody.innerHTML = '';
        
        usersList.forEach(user => {
            const row = document.createElement('tr');
            
            // Células da tabela com data-labels para responsividade
            row.innerHTML = `
                <td data-label="Nome">${user.name || ''}</td>
                <td data-label="Email">${user.email}</td>
                <td data-label="Empresa">${user.company || ''}</td>
                <td data-label="Perfil">${user.profile}</td>
                <td data-label="Status"><span class="status-badge ${user.status === 'active' ? 'status-active' : 'status-inactive'}">${user.status === 'active' ? 'Liberado' : 'Bloqueado'}</span></td>
                <td data-label="Ações">
                    <div class="action-buttons">
                        <button class="btn-action btn-edit" data-id="${user.id}" title="Editar"><i class="fas fa-edit"></i></button>
                        <button class="btn-action btn-delete" data-id="${user.id}" title="Excluir" ${user.profile === 'master' ? 'disabled' : ''}><i class="fas fa-trash"></i></button>
                    </div>
                </td>
            `;
            
            tableBody.appendChild(row);
        });
        
        // Adicionar event listeners para os botões de ação
        addActionButtonListeners();
        
        // Mostrar ou ocultar botão de adicionar usuário com base no perfil
        const addUserBtn = document.getElementById('add-user-btn');
        if (addUserBtn) {
            if (currentUserProfile === 'master' || currentUserProfile === 'admin') {
                addUserBtn.style.display = 'inline-block';
            } else {
                addUserBtn.style.display = 'none';
            }
        }
    }
    
    // Adicionar event listeners para os botões de ação
    function addActionButtonListeners() {
        // Botões de editar
        document.querySelectorAll('.btn-edit').forEach(button => {
            button.addEventListener('click', function() {
                if (currentUserProfile !== 'master' && currentUserProfile !== 'admin') {
                    showMessage('Apenas usuários com perfil master ou admin podem editar usuários', 'error');
                    return;
                }
                
                const userId = this.getAttribute('data-id');
                const user = usersList.find(u => u.id == userId);
                if (user) {
                    // Admin só pode editar usuários da mesma empresa
                    if (currentUserProfile === 'admin' && user.company !== currentUserCompany) {
                        showMessage('Você só pode editar usuários da sua empresa', 'error');
                        return;
                    }
                    
                    // Admin não pode editar usuários master
                    if (currentUserProfile === 'admin' && user.profile === 'master') {
                        showMessage('Administradores não podem editar usuários master', 'error');
                        return;
                    }
                    
                    openUserModal('edit', user);
                }
            });
        });
        
        // Botões de excluir
        document.querySelectorAll('.btn-delete').forEach(button => {
            button.addEventListener('click', function() {
                if (currentUserProfile !== 'master' && currentUserProfile !== 'admin') {
                    showMessage('Apenas usuários com perfil master ou admin podem excluir usuários', 'error');
                    return;
                }
                
                const userId = this.getAttribute('data-id');
                const user = usersList.find(u => u.id == userId);
                if (user) {
                    // Admin só pode excluir usuários da mesma empresa
                    if (currentUserProfile === 'admin' && user.company !== currentUserCompany) {
                        showMessage('Você só pode excluir usuários da sua empresa', 'error');
                        return;
                    }
                    
                    // Admin não pode excluir usuários master
                    if (currentUserProfile === 'admin' && user.profile === 'master') {
                        showMessage('Administradores não podem excluir usuários master', 'error');
                        return;
                    }
                    
                    if (user.profile === 'master') {
                        showMessage('Não é possível excluir usuários com perfil master', 'error');
                        return;
                    }
                    
                    if (confirm(`Tem certeza que deseja excluir o usuário ${user.name || user.email}?`)) {
                        deleteUser(userId);
                    }
                }
            });
        });
    }
    
    // Abrir modal de usuário (criar/editar)
    function openUserModal(mode, user = null) {
        const modal = document.getElementById('user-modal');
        const modalTitle = document.querySelector('.modal-title');
        const form = document.getElementById('user-form');
        
        if (!modal || !modalTitle || !form) {
            console.error('Erro: Elementos do modal não encontrados');
            showMessage('Erro interno: Elementos do modal não encontrados', 'error');
            return;
        }
        
        // Configurar título do modal
        modalTitle.textContent = mode === 'create' ? 'Cadastrar Novo Usuário' : 'Editar Usuário';
        
        // Preencher formulário se estiver editando
        if (mode === 'edit' && user) {
            const userIdElement = document.getElementById('user-id');
            const nameElement = document.getElementById('user-name');
            const emailElement = document.getElementById('user-email');
            const companyElement = document.getElementById('user-company');
            const profileElement = document.getElementById('user-profile');
            const statusElement = document.getElementById('user-status');
            const passwordLabel = document.querySelector('label[for="user-password"]');
            const passwordElement = document.getElementById('user-password');
            
            if (userIdElement) userIdElement.value = user.id;
            if (nameElement) nameElement.value = user.name || '';
            if (emailElement) {
                emailElement.value = user.email;
                emailElement.disabled = true;
            }
            if (companyElement) {
                companyElement.value = user.company || '';
                // Admin não pode alterar empresa
                if (currentUserProfile === 'admin') {
                    companyElement.disabled = true;
                }
            }
            if (profileElement) {
                profileElement.value = user.profile;
                // Admin não pode editar perfil master
                if (currentUserProfile === 'admin' && user.profile === 'master') {
                    profileElement.disabled = true;
                }
            }
            if (statusElement) statusElement.value = user.status;
            
            // Mostrar campo de senha como opcional
            if (passwordLabel) passwordLabel.textContent = 'Senha (deixe em branco para manter a atual)';
            if (passwordElement) passwordElement.required = false;
        } else {
            // Resetar formulário para criação
            form.reset();
            const userIdElement = document.getElementById('user-id');
            const emailElement = document.getElementById('user-email');
            const companyElement = document.getElementById('user-company');
            const profileElement = document.getElementById('user-profile');
            const passwordLabel = document.querySelector('label[for="user-password"]');
            const passwordElement = document.getElementById('user-password');
            
            if (userIdElement) userIdElement.value = '';
            if (emailElement) emailElement.disabled = false;
            if (passwordLabel) passwordLabel.textContent = 'Senha';
            if (passwordElement) passwordElement.required = true;
            
            // Configurar campo empresa baseado no perfil do usuário atual
            if (companyElement) {
                if (currentUserProfile === 'admin') {
                    // Admin: pré-preencher com sua empresa e desabilitar
                    companyElement.value = currentUserCompany;
                    companyElement.disabled = true;
                } else {
                    // Master: pode definir qualquer empresa
                    companyElement.value = '';
                    companyElement.disabled = false;
                }
            }
            
            // Configurar opções de perfil baseado no usuário atual
            if (profileElement) {
                // Limpar opções existentes
                profileElement.innerHTML = '<option value="">Selecione um perfil</option>';
                
                if (currentUserProfile === 'master') {
                    // Master pode criar qualquer perfil
                    profileElement.innerHTML += '<option value="user">Usuário</option>';
                    profileElement.innerHTML += '<option value="admin">Administrador</option>';
                    profileElement.innerHTML += '<option value="master">Master</option>';
                } else if (currentUserProfile === 'admin') {
                    // Admin só pode criar usuários comuns e outros admins
                    profileElement.innerHTML += '<option value="user">Usuário</option>';
                    profileElement.innerHTML += '<option value="admin">Administrador</option>';
                }
            }
        }
        
        // Exibir modal
        modal.classList.add('show');
        
        // Configurar formulário para envio
        form.onsubmit = function(e) {
            e.preventDefault();
            console.log('Formulário submetido, iniciando processamento...');
            
            // Validação direta sem função separada
            const name = form.querySelector('#user-name')?.value?.trim() || '';
            const email = form.querySelector('#user-email')?.value?.trim() || '';
            const company = form.querySelector('#user-company')?.value?.trim() || '';
            const password = form.querySelector('#user-password')?.value || '';
            const profile = form.querySelector('#user-profile')?.value || '';
            const status = form.querySelector('#user-status')?.value || '';
            const userId = form.querySelector('#user-id')?.value || '';
            
            console.log("Dados do formulário:", { name, email, company, profile, status, userId });
            
            // Validação inline
            if (!name) {
                showMessage('Por favor, preencha o campo Nome', 'error');
                return;
            }
            
            if (!email) {
                showMessage('Por favor, preencha o campo Email', 'error');
                return;
            }
            
            // Para admin, empresa é automática; para master, é obrigatória
            if (currentUserProfile === 'master' && !company) {
                showMessage('Por favor, preencha o campo Empresa', 'error');
                return;
            }
            
            if (!profile) {
                showMessage('Por favor, selecione um Perfil', 'error');
                return;
            }
            
            if (!status) {
                showMessage('Por favor, selecione um Status', 'error');
                return;
            }
            
            // Validar email
            const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
            if (!emailRegex.test(email)) {
                showMessage('Por favor, insira um email válido', 'error');
                return;
            }
            
            // Senha obrigatória apenas para novos usuários
            if (!userId && !password) {
                showMessage('Por favor, defina uma senha para o novo usuário', 'error');
                return;
            }
            
            console.log('Validação concluída, processando...');
            
            // Processar baseado no modo
            if (mode === 'create') {
                createUser();
            } else {
                updateUser();
            }
        };
    }
    
    // Validar formulário
    function validateForm() {
        console.log('Iniciando validação do formulário...');
        
        // Aguardar um momento para garantir que o DOM esteja pronto
        setTimeout(() => {
            // Usar querySelector como alternativa mais robusta
            const form = document.getElementById('user-form');
            if (!form) {
                console.error('Formulário não encontrado');
                showMessage('Erro interno: Formulário não encontrado', 'error');
                return false;
            }
            
            // Usar FormData para acessar os valores do formulário
            const formData = new FormData(form);
            const name = form.querySelector('#user-name')?.value?.trim() || '';
            const email = form.querySelector('#user-email')?.value?.trim() || '';
            const company = form.querySelector('#user-company')?.value?.trim() || '';
            const password = form.querySelector('#user-password')?.value || '';
            const profile = form.querySelector('#user-profile')?.value || '';
            const status = form.querySelector('#user-status')?.value || '';
            const userId = form.querySelector('#user-id')?.value || '';
            
            console.log("Valores do formulário:", { name, email, company, profile, status, userId });
            
            // Validação básica
            if (!name) {
                showMessage('Por favor, preencha o campo Nome', 'error');
                return false;
            }
            
            if (!email) {
                showMessage('Por favor, preencha o campo Email', 'error');
                return false;
            }
            
            if (!company) {
                showMessage('Por favor, preencha o campo Empresa', 'error');
                return false;
            }
            
            if (!profile) {
                showMessage('Por favor, selecione um Perfil', 'error');
                return false;
            }
            
            if (!status) {
                showMessage('Por favor, selecione um Status', 'error');
                return false;
            }
            
            // Validar email
            if (!isValidEmail(email)) {
                showMessage('Por favor, insira um email válido', 'error');
                return false;
            }
            
            // Senha obrigatória apenas para novos usuários
            if (!userId && !password) {
                showMessage('Por favor, defina uma senha para o novo usuário', 'error');
                return false;
            }
            
            console.log('Validação concluída com sucesso');
            return true;
        }, 100);
        
        return true; // Retorna true temporariamente para permitir o processamento
    }
    
    // Validar formato de email
    function isValidEmail(email) {
        const re = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        return re.test(email);
    }
    
    // Criar novo usuário
    function createUser() {
        console.log('Função createUser chamada');
        
        const form = document.getElementById('user-form');
        if (!form) {
            console.error('Formulário não encontrado na função createUser');
            showMessage('Erro interno: Formulário não encontrado', 'error');
            return;
        }
        
        const userData = {
            name: form.querySelector('#user-name')?.value?.trim() || '',
            email: form.querySelector('#user-email')?.value?.trim() || '',
            company: form.querySelector('#user-company')?.value?.trim() || '',
            password: form.querySelector('#user-password')?.value || '',
            profile: form.querySelector('#user-profile')?.value || '',
            status: form.querySelector('#user-status')?.value || ''
        };
        
        console.log('Enviando dados do usuário:', userData);
        
        fetch('/api/users', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(userData),
        })
        .then(response => {
            console.log('Resposta recebida:', response);
            return response.json();
        })
        .then(data => {
            console.log('Dados da resposta:', data);
            if (data.success) {
                showMessage('Usuário criado com sucesso!', 'success');
                closeUserModal();
                // Garantir que a lista seja atualizada imediatamente
                setTimeout(() => {
                    loadUsers();
                }, 500);
            } else {
                showMessage(data.message || 'Erro ao criar usuário', 'error');
            }
        })
        .catch(error => {
            console.error('Erro:', error);
            showMessage('Erro ao criar usuário. Tente novamente mais tarde.', 'error');
        });
    }
    
    // Atualizar usuário existente
    function updateUser() {
        console.log('Função updateUser chamada');
        
        const form = document.getElementById('user-form');
        if (!form) {
            console.error('Formulário não encontrado na função updateUser');
            showMessage('Erro interno: Formulário não encontrado', 'error');
            return;
        }
        
        const userId = form.querySelector('#user-id')?.value || '';
        const userData = {
            name: form.querySelector('#user-name')?.value?.trim() || '',
            company: form.querySelector('#user-company')?.value?.trim() || '',
            profile: form.querySelector('#user-profile')?.value || '',
            status: form.querySelector('#user-status')?.value || ''
        };
        
        // Incluir senha apenas se foi fornecida
        const password = form.querySelector('#user-password')?.value || '';
        if (password) {
            userData.password = password;
        }
        
        console.log('Atualizando usuário:', userId, userData);
        
        fetch(`/api/users/${userId}`, {
            method: 'PUT',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(userData),
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                showMessage('Usuário atualizado com sucesso!', 'success');
                closeUserModal();
                loadUsers();
            } else {
                showMessage(data.message || 'Erro ao atualizar usuário', 'error');
            }
        })
        .catch(error => {
            console.error('Erro:', error);
            showMessage('Erro ao atualizar usuário. Tente novamente mais tarde.', 'error');
        });
    }
    
    // Excluir usuário
    function deleteUser(userId) {
        fetch(`/api/users/${userId}`, {
            method: 'DELETE',
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                showMessage('Usuário excluído com sucesso!', 'success');
                loadUsers();
            } else {
                showMessage(data.message || 'Erro ao excluir usuário', 'error');
            }
        })
        .catch(error => {
            console.error('Erro:', error);
            showMessage('Erro ao excluir usuário. Tente novamente mais tarde.', 'error');
        });
    }
    
    // Fechar modal de usuário
    function closeUserModal() {
        const modal = document.getElementById('user-modal');
        modal.classList.remove('show');
    }
    
    // Exibir mensagem
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
    
    // Inicializar página
    function init() {
        // Verificar se estamos na página de usuários
        const usersTable = document.getElementById('users-table-body');
        if (!usersTable) return;
        
        // Verificar perfil do usuário atual
        checkCurrentUserProfile();
        
        // Configurar botão de adicionar usuário
        const addUserBtn = document.getElementById('add-user-btn');
        if (addUserBtn) {
            addUserBtn.addEventListener('click', function() {
                if (currentUserProfile !== 'master' && currentUserProfile !== 'admin') {
                    showMessage('Apenas usuários com perfil master ou admin podem adicionar usuários', 'error');
                    return;
                }
                openUserModal('create');
            });
        }
        
        // Configurar botões para fechar modal
        document.querySelectorAll('.modal-close, .modal-close-btn').forEach(button => {
            button.addEventListener('click', closeUserModal);
        });
    }
    
    // Inicializar quando o DOM estiver pronto
    init();
});
