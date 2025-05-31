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
    
    # Configuração do banco de dados - APENAS Heroku Postgres
    database_url = os.getenv('DATABASE_URL')
    if database_url:
        # Corrigir URL do PostgreSQL para SQLAlchemy 1.4+
        if database_url.startswith("postgres://"):
            database_url = database_url.replace("postgres://", "postgresql://", 1)
        app.config['SQLALCHEMY_DATABASE_URI'] = database_url
        app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
        
        # Inicialização do banco de dados
        db.init_app(app)
        
        # Rota de teste para o banco de dados
        @app.route('/test-db')
        def test_db():
            try:
                # Tenta executar uma consulta simples
                db.session.execute("SELECT 1")
                return "Conexão com o banco de dados estabelecida com sucesso!"
            except Exception as e:
                return f"Erro ao conectar ao banco de dados: {str(e)}"
    
    # Configuração da chave secreta
    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'desenvolvimento-secreto-chave')
    
    # Rota de teste simples
    @app.route('/')
    def hello():
        return "Aplicação funcionando! Banco de dados configurado para Heroku Postgres."
    
    # Rota de informações
    @app.route('/info')
    def info():
        return {
            "status": "online",
            "version": "1.0.0",
            "app": "OS Management System",
            "database_url": "Configurado" if os.getenv('DATABASE_URL') else "Não configurado",
            "environment": os.environ.get('ENVIRONMENT', 'production')
        }
    
    return app
