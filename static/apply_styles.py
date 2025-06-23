import re
import os

# Estilo inline para container
container_style = 'style="display: grid !important; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)) !important; gap: 25px !important; padding: 30px !important; max-width: 1200px !important; margin: 0 auto !important;"'

# Estilo inline para card-item
card_style = 'style="background: #ffffff !important; border-radius: 15px !important; padding: 35px 30px !important; text-align: center !important; box-shadow: 0 6px 20px rgba(0, 0, 0, 0.15) !important; border: 2px solid #e0e0e0 !important; position: relative !important; min-height: 250px !important; display: flex !important; flex-direction: column !important; justify-content: space-between !important;"'

# Estilo inline para card-icon
icon_style = 'style="width: 80px !important; height: 80px !important; background: linear-gradient(135deg, rgb(153, 86, 152), rgb(187, 143, 186)) !important; border-radius: 50% !important; display: flex !important; align-items: center !important; justify-content: center !important; margin: 0 auto 25px !important;"'

# Estilo inline para ícones
icon_i_style = 'style="font-size: 32px !important; color: #ffffff !important;"'

# Estilo inline para h3
h3_style = 'style="color: #333333 !important; font-size: 22px !important; font-weight: 600 !important; margin: 0 0 15px 0 !important;"'

# Estilo inline para p
p_style = 'style="color: #666666 !important; font-size: 15px !important; line-height: 1.6 !important; margin: 0 0 30px 0 !important;"'

# Estilo inline para botão
btn_style = 'style="background: linear-gradient(135deg, rgb(153, 86, 152), rgb(187, 143, 186)) !important; color: #ffffff !important; border: none !important; padding: 14px 28px !important; border-radius: 30px !important; font-size: 15px !important; cursor: pointer !important; display: inline-flex !important; align-items: center !important; gap: 10px !important; min-width: 140px !important; justify-content: center !important;"'

# Estilo inline para ícone da seta
arrow_style = 'style="font-size: 14px !important;"'

files = ['kpis.html', 'cadastro-ativos.html', 'plano-manutencao.html', 'abrir-chamado.html', 'materiais.html']

for filename in files:
    if os.path.exists(filename):
        with open(filename, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Aplicar estilos
        content = re.sub(r'<div class="cards-container">', f'<div class="cards-container" {container_style}>', content)
        content = re.sub(r'<div class="card-item">', f'<div class="card-item" {card_style}>', content)
        content = re.sub(r'<div class="card-icon">', f'<div class="card-icon" {icon_style}>', content)
        content = re.sub(r'<i class="fas ([^"]*)">', lambda m: f'<i class="fas {m.group(1)}" {icon_i_style}>', content)
        content = re.sub(r'<h3>([^<]*)</h3>', lambda m: f'<h3 {h3_style}>{m.group(1)}</h3>', content)
        content = re.sub(r'<p>([^<]*)</p>', lambda m: f'<p {p_style}>{m.group(1)}</p>', content)
        content = re.sub(r'<button class="card-btn"([^>]*)>', lambda m: f'<button class="card-btn"{m.group(1)} {btn_style}>', content)
        content = re.sub(r'<i class="fas fa-arrow-right"></i>', f'<i class="fas fa-arrow-right" {arrow_style}></i>', content)
        
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
        
        print(f'Estilos aplicados em {filename}')

print('Todos os estilos foram aplicados!')
