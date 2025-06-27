import os

# Template base para as páginas
template = '''<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Ativus.AI - {title}</title>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap" rel="stylesheet">
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
    <link rel="stylesheet" href="/static/css/dashboard.css">
</head>
<body>
    <div class="dashboard-container">
        <!-- Overlay para mobile -->
        <div class="sidebar-overlay"></div>
        
        <!-- Menu Lateral -->
        <div class="sidebar">
            <div class="sidebar-header">
                <img src="/static/images/Ativus.png" alt="Ativus.AI Logo" class="logo">
                <span class="logo-text">Ativus.AI</span>
            </div>
            
            <nav class="sidebar-nav">
                <ul class="menu">
                    <li class="menu-item">
                        <a href="/dashboard" class="menu-link">
                            <i class="fas fa-tachometer-alt"></i>
                            <span>Dashboard</span>
                        </a>
                    </li>
                    
                    <li class="menu-item{active_relatorios}">
                        <a href="/relatorios" class="menu-link">
                            <i class="fas fa-chart-bar"></i>
                            <span>Relatórios</span>
                        </a>
                    </li>
                    
                    <li class="menu-item{active_kpis}">
                        <a href="/kpis" class="menu-link">
                            <i class="fas fa-chart-line"></i>
                            <span>KPIs</span>
                        </a>
                    </li>
                    
                    <li class="menu-item{active_ativos}">
                        <a href="/cadastro-ativos" class="menu-link">
                            <i class="fas fa-boxes"></i>
                            <span>Cadastro de Ativos</span>
                        </a>
                    </li>
                    
                    <li class="menu-item{active_manutencao}">
                        <a href="/plano-manutencao" class="menu-link">
                            <i class="fas fa-tools"></i>
                            <span>Plano de Manutenção</span>
                        </a>
                    </li>
                    
                    <li class="menu-item{active_chamado}">
                        <a href="/abrir-chamado" class="menu-link">
                            <i class="fas fa-headset"></i>
                            <span>Abrir Chamado</span>
                        </a>
                    </li>
                    
                    <li class="menu-item{active_materiais}">
                        <a href="/materiais" class="menu-link">
                            <i class="fas fa-boxes"></i>
                            <span>Materiais</span>
                        </a>
                    </li>
                    
                    <li class="menu-item{active_parametros}">
                        <a href="/parametros" class="menu-link">
                            <i class="fas fa-cog"></i>
                            <span>Parâmetros</span>
                        </a>
                    </li>
                </ul>
            </nav>
        </div>
        
        <!-- Conteúdo Principal -->
        <div class="main-content">
            <header class="top-bar">
                <div class="top-bar-left">
                    <button class="sidebar-toggle">
                        <i class="fas fa-bars"></i>
                    </button>
                </div>
                
                <div class="top-bar-right">
                    <div class="user-info">
                        <span id="user-name">Carregando...</span>
                        <span id="user-company">Carregando...</span>
                    </div>
                    <div class="user-avatar">
                        <i class="fas fa-user"></i>
                        <i class="fas fa-chevron-down"></i>
                    </div>
                </div>
            </header>
            
            <!-- Área de Conteúdo -->
            <div class="content">
                <div class="section-header">
                    <h1><i class="{icon}"></i> {title}</h1>
                    <p>{description}</p>
                </div>
                
                <div class="buttons-container" style="display: flex; flex-wrap: wrap; gap: 20px; justify-content: center; padding: 40px 20px; max-width: 800px; margin: 0 auto;">
                    {buttons}
                </div>
            </div>
        </div>
    </div>
    
    <script src="/static/js/user_info.js"></script>
    <script src="/static/js/dashboard.js"></script>
    <script>
        function navigateTo(url) {{
            window.location.href = url;
        }}
    </script>
</body>
</html>'''

def create_button(icon, text, url):
    return f'''
                    <button onclick="navigateTo('{url}')" style="
                        background: linear-gradient(135deg, #9956a8, #bb8fba);
                        color: white;
                        border: none;
                        padding: 20px 30px;
                        border-radius: 12px;
                        font-size: 18px;
                        font-weight: 600;
                        cursor: pointer;
                        min-width: 200px;
                        min-height: 80px;
                        display: flex;
                        align-items: center;
                        justify-content: center;
                        gap: 12px;
                        box-shadow: 0 4px 15px rgba(153, 86, 152, 0.3);
                        transition: all 0.3s ease;
                        text-decoration: none;
                    " onmouseover="this.style.transform='translateY(-2px)'; this.style.boxShadow='0 6px 20px rgba(153, 86, 152, 0.4)'" onmouseout="this.style.transform='translateY(0)'; this.style.boxShadow='0 4px 15px rgba(153, 86, 152, 0.3)'">
                        <i class="{icon}" style="font-size: 24px;"></i>
                        {text}
                    </button>'''

# Configuração das páginas
pages = {
    'kpis.html': {
        'title': 'KPIs',
        'icon': 'fas fa-chart-line',
        'description': 'Indicadores de performance e métricas',
        'active': 'active_kpis',
        'buttons': [
            ('fas fa-chart-line', 'Desempenho', '/kpis/desempenho'),
            ('fas fa-tools', 'Manutenção', '/kpis/manutencao'),
            ('fas fa-dollar-sign', 'Custo', '/kpis/custo')
        ]
    },
    'cadastro-ativos.html': {
        'title': 'Cadastro de Ativos',
        'icon': 'fas fa-boxes',
        'description': 'Gerenciamento de ativos e equipamentos',
        'active': 'active_ativos',
        'buttons': [
            ('fas fa-plus', 'Cadastrar Ativo', '/ativos/cadastrar'),
            ('fas fa-list', 'Listar Ativos', '/ativos/listar'),
            ('fas fa-tags', 'Categorias', '/ativos/categorias')
        ]
    },
    'plano-manutencao.html': {
        'title': 'Plano de Manutenção',
        'icon': 'fas fa-tools',
        'description': 'Planejamento e controle de manutenções',
        'active': 'active_manutencao',
        'buttons': [
            ('fas fa-calendar-plus', 'Cadastrar Preventiva', '/manutencao/preventiva'),
            ('fas fa-wrench', 'Criar OS Corretiva', '/manutencao/corretiva')
        ]
    },
    'abrir-chamado.html': {
        'title': 'Abrir Chamado',
        'icon': 'fas fa-headset',
        'description': 'Gestão de chamados e solicitações',
        'active': 'active_chamado',
        'buttons': [
            ('fas fa-plus-circle', 'Novo Chamado', '/chamados/novo'),
            ('fas fa-folder-open', 'Em Aberto', '/chamados/abertos'),
            ('fas fa-history', 'Histórico', '/chamados/historico')
        ]
    },
    'materiais.html': {
        'title': 'Materiais',
        'icon': 'fas fa-boxes',
        'description': 'Controle de materiais e estoque',
        'active': 'active_materiais',
        'buttons': [
            ('fas fa-plus', 'Cadastrar Material', '/materiais/cadastrar'),
            ('fas fa-clipboard-list', 'Solicitações', '/materiais/solicitacoes'),
            ('fas fa-truck', 'Fornecedores', '/materiais/fornecedores'),
            ('fas fa-warehouse', 'Inventário', '/materiais/inventario')
        ]
    }
}

# Criar as páginas
for filename, config in pages.items():
    # Criar botões
    buttons_html = ''.join([create_button(icon, text, url) for icon, text, url in config['buttons']])
    
    # Definir classes ativas
    active_classes = {
        'active_relatorios': '',
        'active_kpis': '',
        'active_ativos': '',
        'active_manutencao': '',
        'active_chamado': '',
        'active_materiais': '',
        'active_parametros': ''
    }
    active_classes[config['active']] = ' active'
    
    # Gerar HTML
    html_content = template.format(
        title=config['title'],
        icon=config['icon'],
        description=config['description'],
        buttons=buttons_html,
        **active_classes
    )
    
    # Salvar arquivo
    with open(filename, 'w', encoding='utf-8') as f:
        f.write(html_content)
    
    print(f'Página {filename} criada com sucesso!')

print('Todas as páginas foram criadas!')
