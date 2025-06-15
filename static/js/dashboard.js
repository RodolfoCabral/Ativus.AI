document.addEventListener('DOMContentLoaded', function() {
    // Toggle submenu
    const menuItems = document.querySelectorAll('.has-submenu');
    menuItems.forEach(item => {
        item.addEventListener('click', function(e) {
            if (e.target.closest('.submenu')) return;
            e.preventDefault();
            
            // Em mobile, fechar outros submenus abertos
            if (window.innerWidth <= 768) {
                menuItems.forEach(otherItem => {
                    if (otherItem !== this) {
                        otherItem.classList.remove('active');
                    }
                });
            }
            
            this.classList.toggle('active');
        });
    });

    // Toggle sidebar
    const sidebarToggle = document.getElementById('sidebar-toggle');
    const dashboardContainer = document.querySelector('.dashboard-container');
    const sidebar = document.querySelector('.sidebar');
    const sidebarOverlay = document.getElementById('sidebar-overlay');
    
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

    // User dropdown
    const userDropdownBtn = document.querySelector('.user-dropdown-btn');
    const userDropdownContent = document.querySelector('.user-dropdown-content');
    
    userDropdownBtn.addEventListener('click', function(e) {
        e.preventDefault();
        userDropdownContent.classList.toggle('show');
    });

    // Close dropdown when clicking outside
    document.addEventListener('click', function(e) {
        if (!e.target.closest('.user-dropdown')) {
            if (userDropdownContent.classList.contains('show')) {
                userDropdownContent.classList.remove('show');
            }
        }
    });

    // Logout functionality
    const logoutBtn = document.getElementById('logout-btn');
    if (logoutBtn) {
        logoutBtn.addEventListener('click', function(e) {
            e.preventDefault();
            
            fetch('/api/logout')
                .then(response => response.json())
                .then(data => {
                    if (data.success) {
                        window.location.href = '/';
                    } else {
                        alert('Erro ao fazer logout. Tente novamente.');
                    }
                })
                .catch(error => {
                    console.error('Erro:', error);
                    alert('Erro de conexão. Tente novamente mais tarde.');
                });
        });
    }

    // Load content based on menu selection
    const menuLinks = document.querySelectorAll('.menu-link, .submenu-link');
    const dynamicContent = document.getElementById('dynamic-content');
    
    menuLinks.forEach(link => {
        link.addEventListener('click', function(e) {
            if (this.classList.contains('has-submenu') || this.closest('.submenu')) return;
            e.preventDefault();
            
            // Get the text content of the clicked link
            const menuText = this.querySelector('span') ? this.querySelector('span').textContent : this.textContent;
            
            // Handle specific menu items
            if (menuText === 'Permissões') {
                loadPermissionsContent();
            } else {
                // For other menu items, just show a placeholder
                dynamicContent.innerHTML = `
                    <div class="content-panel">
                        <h2>${menuText}</h2>
                        <p>Conteúdo para ${menuText} será implementado em breve.</p>
                    </div>
                `;
            }
            
            // Show the dynamic content and hide welcome panel
            document.querySelector('.welcome-panel').style.display = 'none';
            dynamicContent.style.display = 'block';
        });
    });

    // Function to load permissions content
    function loadPermissionsContent() {
        dynamicContent.innerHTML = `
            <div class="user-management">
                <h2>Gerenciamento de Permissões</h2>
                
                <table class="user-table">
                    <thead>
                        <tr>
                            <th>Nome</th>
                            <th>Email</th>
                            <th>Empresa</th>
                            <th>Perfil</th>
                            <th>Status</th>
                            <th>Ações</th>
                        </tr>
                    </thead>
                    <tbody>
                        <tr>
                            <td>Rodolfo Cabral</td>
                            <td>rodolfocabral@outlook.com.br</td>
                            <td>Melvin</td>
                            <td>Master</td>
                            <td><span class="status-badge status-active">Liberado</span></td>
                            <td>
                                <div class="action-buttons">
                                    <button class="btn-action btn-edit" title="Editar"><i class="fas fa-edit"></i></button>
                                </div>
                            </td>
                        </tr>
                    </tbody>
                </table>
                
                <button id="add-user-btn" class="btn btn-primary">
                    <i class="fas fa-user-plus"></i> Cadastrar Usuário
                </button>
            </div>
            
            <!-- Modal de Cadastro de Usuário -->
            <div id="user-modal" class="modal-backdrop">
                <div class="modal">
                    <div class="modal-header">
                        <h3 class="modal-title">Cadastrar Novo Usuário</h3>
                        <button class="modal-close">&times;</button>
                    </div>
                    <div class="modal-body">
                        <form id="user-form">
                            <div class="form-group">
                                <label for="user-name">Nome Completo</label>
                                <input type="text" id="user-name" class="form-control" required>
                            </div>
                            <div class="form-group">
                                <label for="user-email">Email</label>
                                <input type="email" id="user-email" class="form-control" required>
                            </div>
                            <div class="form-group">
                                <label for="user-company">Empresa</label>
                                <input type="text" id="user-company" class="form-control" required>
                            </div>
                            <div class="form-group">
                                <label for="user-password">Senha</label>
                                <input type="password" id="user-password" class="form-control" required>
                            </div>
                            <div class="form-group">
                                <label for="user-profile">Perfil</label>
                                <select id="user-profile" class="form-select" required>
                                    <option value="">Selecione um perfil</option>
                                    <option value="user">Usuário</option>
                                    <option value="admin">Administrador</option>
                                    <option value="master">Master</option>
                                </select>
                            </div>
                            <div class="form-group">
                                <label for="user-status">Status</label>
                                <select id="user-status" class="form-select" required>
                                    <option value="active">Liberado</option>
                                    <option value="inactive">Bloqueado</option>
                                </select>
                            </div>
                        </form>
                    </div>
                    <div class="modal-footer">
                        <button class="btn btn-secondary modal-close-btn">Cancelar</button>
                        <button id="save-user-btn" class="btn btn-primary">Salvar</button>
                    </div>
                </div>
            </div>
        `;
        
        // Add event listeners for the modal
        const addUserBtn = document.getElementById('add-user-btn');
        const userModal = document.getElementById('user-modal');
        const modalCloseBtn = document.querySelector('.modal-close');
        const modalCloseBtnFooter = document.querySelector('.modal-close-btn');
        const saveUserBtn = document.getElementById('save-user-btn');
        
        addUserBtn.addEventListener('click', function() {
            userModal.classList.add('show');
        });
        
        modalCloseBtn.addEventListener('click', function() {
            userModal.classList.remove('show');
        });
        
        modalCloseBtnFooter.addEventListener('click', function() {
            userModal.classList.remove('show');
        });
        
        saveUserBtn.addEventListener('click', function() {
            // Get form values
            const name = document.getElementById('user-name').value;
            const email = document.getElementById('user-email').value;
            const company = document.getElementById('user-company').value;
            const password = document.getElementById('user-password').value;
            const profile = document.getElementById('user-profile').value;
            const status = document.getElementById('user-status').value;
            
            // Validate form
            if (!name || !email || !company || !password || !profile || !status) {
                alert('Por favor, preencha todos os campos.');
                return;
            }
            
            // Here you would normally send this data to the server
            // For now, we'll just show a success message and close the modal
            alert(`Usuário ${name} cadastrado com sucesso!`);
            userModal.classList.remove('show');
            
            // Reset form
            document.getElementById('user-form').reset();
            
            // Add the new user to the table (in a real app, this would come from the server)
            const userTable = document.querySelector('.user-table tbody');
            const newRow = document.createElement('tr');
            newRow.innerHTML = `
                <td>${name}</td>
                <td>${email}</td>
                <td>${company}</td>
                <td>${profile}</td>
                <td><span class="status-badge ${status === 'active' ? 'status-active' : 'status-inactive'}">${status === 'active' ? 'Liberado' : 'Bloqueado'}</span></td>
                <td>
                    <div class="action-buttons">
                        <button class="btn-action btn-edit" title="Editar"><i class="fas fa-edit"></i></button>
                        <button class="btn-action btn-delete" title="Excluir"><i class="fas fa-trash"></i></button>
                    </div>
                </td>
            `;
            userTable.appendChild(newRow);
        });
    }

    // Check if we need to load permissions content by default
    const urlParams = new URLSearchParams(window.location.search);
    if (urlParams.get('section') === 'permissions') {
        loadPermissionsContent();
        document.querySelector('.welcome-panel').style.display = 'none';
        dynamicContent.style.display = 'block';
    }
});
