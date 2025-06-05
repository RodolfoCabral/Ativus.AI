document.addEventListener('DOMContentLoaded', function() {
    // Variáveis globais
    let currentUserProfile = '';
    let usersList = [];
    
    // Verificar o perfil do usuário atual
    function checkCurrentUserProfile() {
        fetch('/api/user')
            .then(response => response.json())
            .then(data => {
                currentUserProfile = data.profile;
                loadUsers();
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
            
            // Células da tabela
            row.innerHTML = `
                <td>${user.name || ''}</td>
                <td>${user.email}</td>
                <td>${user.company || ''}</td>
                <td>${user.profile}</td>
                <td><span class="status-badge ${user.status === 'active' ? 'status-active' : 'status-inactive'}">${user.status === 'active' ? 'Liberado' : 'Bloqueado'}</span></td>
                <td>
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
            if (currentUserProfile === 'master') {
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
                if (currentUserProfile !== 'master') {
                    showMessage('Apenas usuários com perfil master podem editar usuários', 'error');
                    return;
                }
                
                const userId = this.getAttribute('data-id');
                const user = usersList.find(u => u.id == userId);
                if (user) {
                    openUserModal('edit', user);
                }
            });
        });
        
        // Botões de excluir
        document.querySelectorAll('.btn-delete').forEach(button => {
            button.addEventListener('click', function() {
                if (currentUserProfile !== 'master') {
                    showMessage('Apenas usuários com perfil master podem excluir usuários', 'error');
                    return;
                }
                
                const userId = this.getAttribute('data-id');
                const user = usersList.find(u => u.id == userId);
                if (user) {
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
        
        // Configurar título do modal
        modalTitle.textContent = mode === 'create' ? 'Cadastrar Novo Usuário' : 'Editar Usuário';
        
        // Preencher formulário se estiver editando
        if (mode === 'edit' && user) {
            document.getElementById('user-id').value = user.id;
            document.getElementById('user-name').value = user.name || '';
            document.getElementById('user-email').value = user.email;
            document.getElementById('user-company').value = user.company || '';
            document.getElementById('user-profile').value = user.profile;
            document.getElementById('user-status').value = user.status;
            
            // Campo de email desabilitado na edição
            document.getElementById('user-email').disabled = true;
            
            // Mostrar campo de senha como opcional
            document.querySelector('label[for="user-password"]').textContent = 'Senha (deixe em branco para manter a atual)';
        } else {
            // Resetar formulário para criação
            form.reset();
            document.getElementById('user-id').value = '';
            document.getElementById('user-email').disabled = false;
            document.querySelector('label[for="user-password"]').textContent = 'Senha';
        }
        
        // Exibir modal
        modal.classList.add('show');
        
        // Configurar botão de salvar
        const saveBtn = document.getElementById('save-user-btn');
        saveBtn.onclick = function() {
            if (validateForm()) {
                if (mode === 'create') {
                    createUser();
                } else {
                    updateUser();
                }
            }
        };
    }
    
    // Validar formulário
    function validateForm() {
        const userId = document.getElementById('user-id').value;
        const name = document.getElementById('user-name').value;
        const email = document.getElementById('user-email').value;
        const company = document.getElementById('user-company').value;
        const password = document.getElementById('user-password').value;
        const profile = document.getElementById('user-profile').value;
        const status = document.getElementById('user-status').value;
        
        // Validação básica
        if (!name || !email || !company || !profile || !status) {
            showMessage('Por favor, preencha todos os campos obrigatórios', 'error');
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
        
        return true;
    }
    
    // Validar formato de email
    function isValidEmail(email) {
        const re = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        return re.test(email);
    }
    
    // Criar novo usuário
    function createUser() {
        const userData = {
            name: document.getElementById('user-name').value,
            email: document.getElementById('user-email').value,
            company: document.getElementById('user-company').value,
            password: document.getElementById('user-password').value,
            profile: document.getElementById('user-profile').value,
            status: document.getElementById('user-status').value
        };
        
        fetch('/api/users', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(userData),
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                showMessage('Usuário criado com sucesso!', 'success');
                closeUserModal();
                loadUsers();
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
        const userId = document.getElementById('user-id').value;
        const userData = {
            name: document.getElementById('user-name').value,
            company: document.getElementById('user-company').value,
            profile: document.getElementById('user-profile').value,
            status: document.getElementById('user-status').value
        };
        
        // Incluir senha apenas se foi fornecida
        const password = document.getElementById('user-password').value;
        if (password) {
            userData.password = password;
        }
        
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
                if (currentUserProfile !== 'master') {
                    showMessage('Apenas usuários com perfil master podem adicionar usuários', 'error');
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
