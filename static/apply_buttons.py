import re
import os

# Definir os botões para cada página
buttons_config = {
    'relatorios.html': [
        {'icon': 'fa-list', 'text': 'Lista de Ativos', 'url': '/relatorios/lista-ativos'},
        {'icon': 'fa-clipboard-list', 'text': 'Ordens de Serviço', 'url': '/relatorios/ordens-servico'},
        {'icon': 'fa-ticket-alt', 'text': 'Solicitações de Serviço', 'url': '/relatorios/solicitacoes'}
    ],
    'kpis.html': [
        {'icon': 'fa-chart-line', 'text': 'Desempenho', 'url': '/kpis/desempenho'},
        {'icon': 'fa-tools', 'text': 'Manutenção', 'url': '/kpis/manutencao'},
        {'icon': 'fa-dollar-sign', 'text': 'Custo', 'url': '/kpis/custo'}
    ],
    'cadastro-ativos.html': [
        {'icon': 'fa-plus', 'text': 'Cadastrar Ativo', 'url': '/ativos/cadastrar'},
        {'icon': 'fa-list', 'text': 'Listar Ativos', 'url': '/ativos/listar'},
        {'icon': 'fa-tags', 'text': 'Categorias', 'url': '/ativos/categorias'}
    ],
    'plano-manutencao.html': [
        {'icon': 'fa-calendar-plus', 'text': 'Cadastrar Preventiva', 'url': '/manutencao/preventiva'},
        {'icon': 'fa-wrench', 'text': 'Criar OS Corretiva', 'url': '/manutencao/corretiva'}
    ],
    'abrir-chamado.html': [
        {'icon': 'fa-plus-circle', 'text': 'Novo Chamado', 'url': '/chamados/novo'},
        {'icon': 'fa-folder-open', 'text': 'Em Aberto', 'url': '/chamados/abertos'},
        {'icon': 'fa-history', 'text': 'Histórico', 'url': '/chamados/historico'}
    ],
    'materiais.html': [
        {'icon': 'fa-plus', 'text': 'Cadastrar Material', 'url': '/materiais/cadastrar'},
        {'icon': 'fa-clipboard-list', 'text': 'Solicitações', 'url': '/materiais/solicitacoes'},
        {'icon': 'fa-truck', 'text': 'Fornecedores', 'url': '/materiais/fornecedores'},
        {'icon': 'fa-warehouse', 'text': 'Inventário', 'url': '/materiais/inventario'}
    ]
}

def create_button_html(icon, text, url):
    return f'''                    <button onclick="navigateTo('{url}')" style="
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
                        <i class="fas {icon}" style="font-size: 24px;"></i>
                        {text}
                    </button>'''

for filename, buttons in buttons_config.items():
    if os.path.exists(filename):
        with open(filename, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Criar HTML dos botões
        buttons_html = '\n'.join([create_button_html(btn['icon'], btn['text'], btn['url']) for btn in buttons])
        
        # Criar container dos botões
        buttons_container = f'''                <div class="buttons-container" style="display: flex; flex-wrap: wrap; gap: 20px; justify-content: center; padding: 40px 20px; max-width: 800px; margin: 0 auto;">
                    
{buttons_html}
                    
                </div>'''
        
        # Substituir área de cards por botões
        # Procurar por diferentes padrões de cards
        patterns = [
            r'<div class="cards-container".*?</div>\s*</div>',
            r'<div class="cards-container".*?</div>\s*</div>\s*</div>',
            r'<p>.*?será implementado em breve.*?</p>'
        ]
        
        replaced = False
        for pattern in patterns:
            if re.search(pattern, content, re.DOTALL):
                content = re.sub(pattern, buttons_container, content, flags=re.DOTALL)
                replaced = True
                break
        
        # Se não encontrou padrão, adicionar após section-header
        if not replaced:
            content = re.sub(
                r'(<div class="section-header">.*?</div>)',
                r'\1\n' + buttons_container,
                content,
                flags=re.DOTALL
            )
        
        # Adicionar função navigateTo se não existir
        if 'function navigateTo' not in content:
            content = content.replace('</body>', '''    <script>
        function navigateTo(url) {
            window.location.href = url;
        }
    </script>
</body>''')
        
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(content)
        
        print(f'Botões aplicados em {filename}')

print('Todos os botões foram aplicados!')
