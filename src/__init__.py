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
    
    # Configuração do banco de dados
    database_url = os.getenv('DATABASE_URL')
    if database_url and database_url.startswith("postgres://"):
        database_url = database_url.replace("postgres://", "postgresql://", 1)
    app.config['SQLALCHEMY_DATABASE_URI'] = database_url
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    # Configuração da chave secreta
    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'desenvolvimento-secreto-chave')
    
    # Inicialização do banco de dados
    db.init_app(app)
    
    # Rota de teste simples
    @app.route('/')
    def hello():
        return "Aplicação funcionando com banco de dados configurado! Teste de conexão em andamento."
    
    @app.route('/test-db')
    def test_db():
        try:
            # Tenta executar uma consulta simples
            db.session.execute("SELECT 1")
            return "Conexão com o banco de dados estabelecida com sucesso!"
        except Exception as e:
            return f"Erro ao conectar ao banco de dados: {str(e)}"
    
    # Inicialização do Flask-Login
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'
    login_manager.login_message = 'Por favor, faça login para acessar esta página.'
    
    # Inicialização do Flask-Mail
    app.config['MAIL_SERVER'] = 'smtp.gmail.com'
    app.config['MAIL_PORT'] = 587
    app.config['MAIL_USE_TLS'] = True
    app.config['MAIL_USERNAME'] = os.getenv('MAIL_USERNAME', '')
    app.config['MAIL_PASSWORD'] = os.getenv('MAIL_PASSWORD', '')
    app.config['MAIL_DEFAULT_SENDER'] = os.getenv('MAIL_DEFAULT_SENDER', '')
    mail.init_app(app)
    
    # Criação das tabelas do banco de dados
    with app.app_context():
        db.create_all()
    
    return app
