from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_mail import Mail
import os
import sys

# Configuração do caminho para importações
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

# Inicialização das extensões
db = SQLAlchemy()
login_manager = LoginManager()
mail = Mail()

def create_app():
    app = Flask(__name__)
    
    # Configuração da chave secreta
    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'desenvolvimento-secreto-chave')
    
    # Rota de teste simples
    @app.route('/')
    def hello():
        return "Aplicação funcionando sem banco de dados! Teste bem-sucedido."
    
    @app.route('/info')
    def info():
        return {
            "status": "online",
            "version": "1.0.0",
            "app": "OS Management System",
            "message": "Conexão com banco de dados temporariamente desativada para testes"
        }
    
    return app
