// Funções principais do JavaScript
document.addEventListener('DOMContentLoaded', function() {
    // Toggle submenu
    const menuToggles = document.querySelectorAll('.menu-toggle');
    menuToggles.forEach(toggle => {
        toggle.addEventListener('click', function(e) {
            e.preventDefault();
            const target = this.getAttribute('data-target');
            document.getElementById(target).classList.toggle('active');
            this.querySelector('.fa-chevron-down')?.classList.toggle('fa-chevron-up');
        });
    });
    
    // Toggle user dropdown
    const dropdownToggle = document.querySelector('.dropdown-toggle');
    if (dropdownToggle) {
        dropdownToggle.addEventListener('click', function() {
            document.querySelector('.dropdown-menu').classList.toggle('show');
        });
    }
    
    // Close dropdown when clicking outside
    document.addEventListener('click', function(e) {
        if (!e.target.closest('.dropdown')) {
            const dropdownMenu = document.querySelector('.dropdown-menu');
            if (dropdownMenu && dropdownMenu.classList.contains('show')) {
                dropdownMenu.classList.remove('show');
            }
        }
    });
    
    // Mobile menu toggle
    const menuToggleMobile = document.querySelector('.menu-toggle-mobile');
    if (menuToggleMobile) {
        menuToggleMobile.addEventListener('click', function() {
            document.querySelector('.sidebar').classList.toggle('active');
        });
    }
    
    // Flash messages auto-hide
    const flashMessages = document.querySelectorAll('.flash-message');
    flashMessages.forEach(message => {
        setTimeout(() => {
            message.style.opacity = '0';
            setTimeout(() => {
                message.style.display = 'none';
            }, 500);
        }, 5000);
    });
});
