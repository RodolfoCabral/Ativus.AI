// ADICIONE ESTE CÓDIGO NO FINAL DO ARQUIVO static/js/executar-os.js

console.log('🔧 Iniciando correção do layout da página executar-os');

// Função para corrigir o layout da página
function corrigirLayoutExecutarOS() {
    console.log('🎨 Aplicando correções de layout...');
    
    // Adicionar classe ao body para identificar a página
    document.body.classList.add('executar-os-page');
    
    // Verificar se existe sidebar
    const sidebar = document.querySelector('.sidebar, .menu-lateral, .side-menu');
    const mainContent = document.querySelector('.main-content, .content, .container-fluid');
    
    if (sidebar && mainContent) {
        console.log('📐 Sidebar e conteúdo principal encontrados');
        
        // Verificar se a sidebar está visível
        const sidebarVisible = window.getComputedStyle(sidebar).display !== 'none' && 
                              window.getComputedStyle(sidebar).visibility !== 'hidden';
        
        if (sidebarVisible) {
            console.log('👁️ Sidebar visível - ajustando layout');
            
            // Aplicar margem ao conteúdo principal
            if (window.innerWidth > 768) {
                mainContent.style.marginLeft = '250px';
                mainContent.style.width = 'calc(100% - 250px)';
                mainContent.style.transition = 'all 0.3s ease';
            }
        }
    }
    
    // Corrigir z-index dos elementos
    corrigirZIndex();
    
    // Adicionar estilos inline se necessário
    adicionarEstilosInline();
    
    console.log('✅ Layout corrigido!');
}

// Função para corrigir z-index
function corrigirZIndex() {
    const sidebar = document.querySelector('.sidebar, .menu-lateral, .side-menu');
    const header = document.querySelector('.header, .top-header, .navbar');
    const mainContent = document.querySelector('.main-content, .content, .container-fluid');
    
    if (sidebar) {
        sidebar.style.zIndex = '1000';
        sidebar.style.position = 'fixed';
    }
    
    if (header) {
        header.style.zIndex = '1001';
        header.style.position = 'relative';
    }
    
    if (mainContent) {
        mainContent.style.zIndex = '1';
        mainContent.style.position = 'relative';
    }
}

// Função para adicionar estilos inline
function adicionarEstilosInline() {
    // Criar elemento style se não existir
    let styleElement = document.getElementById('executar-os-layout-fix');
    
    if (!styleElement) {
        styleElement = document.createElement('style');
        styleElement.id = 'executar-os-layout-fix';
        document.head.appendChild(styleElement);
    }
    
    // CSS para correção do layout
    const css = `
        /* Correção específica para página executar-os */
        .executar-os-page .main-content {
            margin-left: 0;
            width: 100%;
            transition: all 0.3s ease;
        }
        
        @media (min-width: 769px) {
            .executar-os-page .main-content {
                margin-left: 250px;
                width: calc(100% - 250px);
            }
        }
        
        .executar-os-page .sidebar {
            position: fixed !important;
            z-index: 1000 !important;
        }
        
        .executar-os-page .container-fluid,
        .executar-os-page .container {
            max-width: none;
            padding-left: 15px;
            padding-right: 15px;
        }
        
        /* Garantir que cards não fiquem atrás do menu */
        .executar-os-page .card,
        .executar-os-page .os-card {
            position: relative;
            z-index: 1;
            margin-bottom: 20px;
        }
        
        /* Ajustar largura dos elementos */
        .executar-os-page .row {
            margin-left: 0;
            margin-right: 0;
        }
        
        .executar-os-page .col-12,
        .executar-os-page .col-md-12 {
            padding-left: 15px;
            padding-right: 15px;
        }
        
        /* Responsividade para mobile */
        @media (max-width: 768px) {
            .executar-os-page .main-content {
                margin-left: 0 !important;
                width: 100% !important;
            }
            
            .executar-os-page .sidebar {
                transform: translateX(-100%);
                transition: transform 0.3s ease;
            }
            
            .executar-os-page .sidebar.show {
                transform: translateX(0);
            }
        }
        
        /* Botão do menu para mobile */
        .menu-toggle-btn {
            position: fixed;
            top: 20px;
            left: 20px;
            z-index: 1002;
            background: #007bff;
            color: white;
            border: none;
            padding: 10px 12px;
            border-radius: 4px;
            cursor: pointer;
            display: none;
        }
        
        @media (max-width: 768px) {
            .menu-toggle-btn {
                display: block;
            }
        }
        
        .menu-toggle-btn:hover {
            background: #0056b3;
        }
    `;
    
    styleElement.textContent = css;
}

// Função para adicionar botão de toggle do menu (mobile)
function adicionarBotaoToggleMenu() {
    // Verificar se já existe
    if (document.querySelector('.menu-toggle-btn')) {
        return;
    }
    
    const toggleBtn = document.createElement('button');
    toggleBtn.className = 'menu-toggle-btn';
    toggleBtn.innerHTML = '<i class="fas fa-bars"></i>';
    toggleBtn.title = 'Toggle Menu';
    
    toggleBtn.addEventListener('click', function() {
        const sidebar = document.querySelector('.sidebar, .menu-lateral, .side-menu');
        if (sidebar) {
            sidebar.classList.toggle('show');
        }
    });
    
    document.body.appendChild(toggleBtn);
}

// Função para detectar mudanças no tamanho da tela
function adicionarListenerResize() {
    window.addEventListener('resize', function() {
        setTimeout(corrigirLayoutExecutarOS, 100);
    });
}

// Função para detectar mudanças na sidebar
function detectarMudancasSidebar() {
    const sidebar = document.querySelector('.sidebar, .menu-lateral, .side-menu');
    
    if (sidebar) {
        // Observer para mudanças na sidebar
        const observer = new MutationObserver(function(mutations) {
            mutations.forEach(function(mutation) {
                if (mutation.type === 'attributes' && 
                    (mutation.attributeName === 'class' || mutation.attributeName === 'style')) {
                    setTimeout(corrigirLayoutExecutarOS, 100);
                }
            });
        });
        
        observer.observe(sidebar, {
            attributes: true,
            attributeFilter: ['class', 'style']
        });
    }
}

// EXECUÇÃO AUTOMÁTICA
console.log('⚡ Iniciando correção automática do layout...');

// Executar correções múltiplas vezes
setTimeout(corrigirLayoutExecutarOS, 100);
setTimeout(corrigirLayoutExecutarOS, 500);
setTimeout(corrigirLayoutExecutarOS, 1000);
setTimeout(corrigirLayoutExecutarOS, 2000);

// Adicionar funcionalidades
setTimeout(adicionarBotaoToggleMenu, 1000);
setTimeout(adicionarListenerResize, 1000);
setTimeout(detectarMudancasSidebar, 1000);

// Event listeners
document.addEventListener('DOMContentLoaded', function() {
    console.log('🚀 DOM carregado - aplicando correções de layout');
    setTimeout(corrigirLayoutExecutarOS, 100);
});

window.addEventListener('load', function() {
    console.log('🌐 Window carregada - aplicando correções de layout');
    setTimeout(corrigirLayoutExecutarOS, 100);
});

console.log('✅ Script de correção de layout carregado!');
