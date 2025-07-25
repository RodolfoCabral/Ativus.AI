document.addEventListener('DOMContentLoaded', function() {
    console.log('🚀 Dashboard JavaScript carregado');
    
    // Toggle sidebar
    const sidebarToggle = document.querySelector('.sidebar-toggle');
    const dashboardContainer = document.querySelector('.dashboard-container');
    const sidebar = document.querySelector('.sidebar');
    const sidebarOverlay = document.querySelector('.sidebar-overlay');
    
    if (sidebarToggle) {
        sidebarToggle.addEventListener('click', function() {
            console.log('🖱️ Clique no toggle da sidebar');
            
            if (window.innerWidth <= 768) {
                // Em mobile, usar classe mobile-open e mostrar overlay
                sidebar.classList.toggle('mobile-open');
                if (sidebarOverlay) {
                    sidebarOverlay.classList.toggle('show');
                }
                console.log('📱 Sidebar mobile toggled');
            } else {
                // Em desktop, usar classe sidebar-collapsed
                dashboardContainer.classList.toggle('sidebar-collapsed');
                console.log('💻 Sidebar desktop toggled');
            }
        });
    }
    
    // Fechar sidebar em mobile quando clicar no overlay
    if (sidebarOverlay) {
        sidebarOverlay.addEventListener('click', function() {
            sidebar.classList.remove('mobile-open');
            sidebarOverlay.classList.remove('show');
            console.log('📁 Sidebar fechada via overlay');
        });
    }
    
    // Fechar sidebar em mobile quando clicar fora
    document.addEventListener('click', function(e) {
        if (window.innerWidth <= 768) {
            if (!e.target.closest('.sidebar') && !e.target.closest('.sidebar-toggle')) {
                if (sidebar && sidebar.classList.contains('mobile-open')) {
                    sidebar.classList.remove('mobile-open');
                    if (sidebarOverlay) {
                        sidebarOverlay.classList.remove('show');
                    }
                    console.log('📁 Sidebar fechada (clique fora)');
                }
            }
        }
    });
    
    // Ajustar comportamento ao redimensionar janela
    window.addEventListener('resize', function() {
        if (window.innerWidth > 768) {
            if (sidebar) sidebar.classList.remove('mobile-open');
            if (sidebarOverlay) sidebarOverlay.classList.remove('show');
        } else {
            if (dashboardContainer) dashboardContainer.classList.remove('sidebar-collapsed');
        }
    });

    console.log('✅ Dashboard funcionalidades inicializadas');
});

// Função para navegar entre páginas
function navigateTo(url) {
    console.log('🔗 Navegando para:', url);
    window.location.href = url;
}

// Exportar função para uso global
window.navigateTo = navigateTo;

