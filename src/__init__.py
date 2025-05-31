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
    
    # Configuração do banco de dados - Heroku Postgres
    database_url = os.getenv('HEROKU_POSTGRESQL_NAVY_URL')
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
    
    # Configuração do Flask-Mail
    app.config['MAIL_SERVER'] = 'smtp.outlook.com'
    app.config['MAIL_PORT'] = 587
    app.config['MAIL_USE_TLS'] = True
    app.config['MAIL_USERNAME'] = os.getenv('MAIL_USERNAME', '')
    app.config['MAIL_PASSWORD'] = os.getenv('MAIL_PASSWORD', '')
    app.config['MAIL_DEFAULT_SENDER'] = os.getenv('MAIL_DEFAULT_SENDER', '')
    mail.init_app(app)
    
    # Rota de teste simples
    @app.route('/')
    def hello():
        return "Aplicação funcionando! Banco de dados e email configurados."
    
    # Rota de informações
    @app.route('/info')
    def info():
        return {
            "status": "online",
            "version": "1.0.0",
            "app": "OS Management System",
            "database_url": "Configurado" if database_url else "Não configurado",
            "mail_username": os.getenv('MAIL_USERNAME', 'Não configurado'),
            "environment": os.environ.get('ENVIRONMENT', 'production')
        }
    
    return app
