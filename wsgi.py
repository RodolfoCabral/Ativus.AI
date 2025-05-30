import os
import sys

# Adiciona o diretório atual ao path do Python
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Importa a aplicação
from src.main import app

if __name__ == '__main__':
    app.run()
