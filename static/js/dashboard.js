document.addEventListener('DOMContentLoaded', function() {
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
});
