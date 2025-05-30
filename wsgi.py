import os
import sys

# Adiciona o diretório atual ao path do Python
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src import create_app

app = create_app()

if __name__ == '__main__':
    app.run()
