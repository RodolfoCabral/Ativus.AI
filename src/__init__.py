from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_mail import Mail
import os
import sys

# Configuração do caminho para importações
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

# Inicialização das extensões
'''
db = SQLAlchemy()
'''
login_manager = LoginManager()
mail = Mail()

def create_app():
    app = Flask(__name__)
    '''
    # Configuração do banco de dados
    postgres_url = os.getenv('DATABASE_URL', 'postgresql://postgres:101002Rm101002Rm#@db.dsmhjzhhjzycqihcgeah.supabase.co:5432/postgres')
    app.config['SQLALCHEMY_DATABASE_URI'] = postgres_url
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    '''
    
    # Configuração da chave secreta
    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'desenvolvimento-secreto-chave')
    
    # Configuração do Flask-Mail
    app.config['MAIL_SERVER'] = 'smtp.gmail.com'
    app.config['MAIL_PORT'] = 587
    app.config['MAIL_USE_TLS'] = True
    app.config['MAIL_USERNAME'] = os.getenv('MAIL_USERNAME', '')
    app.config['MAIL_PASSWORD'] = os.getenv('MAIL_PASSWORD', '')
    app.config['MAIL_DEFAULT_SENDER'] = os.getenv('MAIL_DEFAULT_SENDER', '')
    
    # Inicialização das extensões com o app
    '''
    db.init_app(app)
    '''
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'
    login_manager.login_message = 'Por favor, faça login para acessar esta página.'
    mail.init_app(app)
    
    # Importação e registro dos blueprints
    from src.routes.auth import auth_bp
    from src.routes.main import main_bp
    from src.routes.admin import admin_bp
    
    app.register_blueprint(auth_bp)
    app.register_blueprint(main_bp)
    app.register_blueprint(admin_bp)
    
    # Configuração do carregador de usuário para o Flask-Login
    from src.models.user import User
    
    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))
    
    # Criação das tabelas do banco de dados
    with app.app_context():
        '''
        db.create_all()
        '''
        
        # Criação do usuário administrador se não existir
        admin_user = User.query.filter_by(email='rodolfocabral@outlook.com.br').first()
        if not admin_user:
            admin_user = User(
                name='Administrador',
                email='rodolfocabral@outlook.com.br',
                is_admin=True
            )
            admin_user.set_password('101002Rm#')
            '''
            db.session.add(admin_user)
            db.session.commit()
            '''
    
    return app
