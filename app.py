import os
from flask import Flask, render_template, request, jsonify, redirect, url_for, send_from_directory
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from models import db, User
from auth import auth_bp
from datetime import datetime
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail
from dotenv import load_dotenv
import ssl

import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

SENDGRID_API_KEY = os.getenv("SENDGRID_API_KEY")

def create_app():
    app = Flask(__name__, static_folder='static')
    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev_key_for_testing')
    
    # Configuração do banco de dados PostgreSQL
    # Priorizar a variável HEROKU_POSTGRESQL_NAVY_URL fornecida pelo usuário
    database_url = os.environ.get('HEROKU_POSTGRESQL_NAVY_URL')
    
    # Fallback para DATABASE_URL se HEROKU_POSTGRESQL_NAVY_URL não estiver disponível
    if not database_url:
        database_url = os.environ.get('DATABASE_URL')
    
    # Valor padrão para desenvolvimento local
    if not database_url:
        database_url = 'postgresql://postgres:postgres@localhost:5432/ativus'
    
    # Corrigir prefixo da URL se necessário (Heroku usa postgres://, SQLAlchemy requer postgresql://)
    if database_url.startswith('postgres://'):
        database_url = database_url.replace('postgres://', 'postgresql://', 1)
    
    # Usar sempre PostgreSQL, sem fallback para SQLite
    app.config['SQLALCHEMY_DATABASE_URI'] = database_url
    print(f"Conectando ao banco de dados: {database_url}")
    
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    # Inicialização do banco de dados
    db.init_app(app)
    
    # Configuração do login
    login_manager = LoginManager()
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'
    
    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))
    
    # Registro de blueprints
    app.register_blueprint(auth_bp)
    
    # Importar e registrar blueprint de ativos após inicialização do app
    try:
        from routes.assets import assets_bp
        app.register_blueprint(assets_bp)
    except ImportError as e:
        print(f"Aviso: Não foi possível importar assets_bp: {e}")
        print("Sistema funcionará sem funcionalidades de ativos.")
    
    # Rotas para arquivos estáticos
    @app.route('/')
    def index():
        return send_from_directory('static', 'index.html')
    
    @app.route('/signup')
    def signup():
        return send_from_directory('static', 'signup.html')
    
    @app.route('/dashboard')
    @login_required
    def dashboard():
        return send_from_directory('static', 'dashboard.html')
    
    @app.route('/users')
    @login_required
    def users():
        return send_from_directory('static', 'users.html')
    
    @app.route('/reset-password')
    @login_required
    def reset_password():
        return send_from_directory('static', 'reset_password.html')
    
    # Rotas para páginas com botões centralizados
    @app.route('/relatorios')
    @login_required
    def relatorios():
        return send_from_directory('static', 'relatorios.html')
    
    @app.route('/kpis')
    @login_required
    def kpis():
        return send_from_directory('static', 'kpis.html')
    
    @app.route('/parametros')
    @login_required
    def parametros():
        return send_from_directory('static', 'parametros.html')
    
    @app.route('/cadastro-ativos')
    @login_required
    def cadastro_ativos():
        return send_from_directory('static', 'cadastro-ativos.html')
    
    @app.route('/plano-manutencao')
    @login_required
    def plano_manutencao():
        return send_from_directory('static', 'plano-manutencao.html')
    
    @app.route('/abrir-chamado')
    @login_required
    def abrir_chamado():
        return send_from_directory('static', 'abrir-chamado.html')
    
    @app.route('/materiais')
    @login_required
    def materiais():
        return send_from_directory('static', 'materiais.html')
    
    @app.route('/static/<path:path>')
    def serve_static(path):
        return send_from_directory('static', path)
    
    # API para o formulário de assinatura
    @app.route('/api/signup', methods=['POST'])
    def api_signup():
        data = request.json
        
        # Validação básica
        if not data or not all(k in data for k in ('source', 'fullname', 'company', 'phone')):
            return jsonify({'success': False, 'message': 'Dados incompletos'})
        
        try:
            # Enviar email com os dados do formulário via SendGrid
            send_signup_email(data)
            
            return jsonify({'success': True, 'message': 'Cadastro realizado com sucesso!'})
        except Exception as e:
            print(f"Erro ao processar cadastro: {str(e)}")
            return jsonify({'success': False, 'message': 'Erro ao processar cadastro'})
    
    @app.route('/ativos/arvore')
    @login_required
    def arvore_ativos():
        return send_from_directory('static', 'arvore-ativos.html')
    
    @app.route('/ativos/categorias')
    @login_required
    def categorias_ativos():
        return send_from_directory('static', 'categorias-ativos.html')
    
    return app

def send_signup_email(data):
    """Envia um email com os dados do formulário de assinatura via SendGrid."""
    SENDGRID_API_KEY = os.getenv("SENDGRID_API_KEY")
    
    if not SENDGRID_API_KEY:
        print("API Key do SendGrid não encontrada. Verifique seu .env.txt.")
        raise Exception("API Key do SendGrid ausente")
    
    html_content = f"""
    <html>
    <body>
        <h2>Novo cadastro de assinatura - Ativus.AI</h2>
        <p>Um novo cliente se cadastrou para assinar o plano:</p>
        <table border="1" cellpadding="5" cellspacing="0">
            <tr><td><strong>Origem:</strong></td><td>{data.get('source')}</td></tr>
            <tr><td><strong>Nome:</strong></td><td>{data.get('fullname')}</td></tr>
            <tr><td><strong>Empresa:</strong></td><td>{data.get('company')}</td></tr>
            <tr><td><strong>Telefone:</strong></td><td>{data.get('phone')}</td></tr>
            <tr><td><strong>Data/Hora:</strong></td><td>{datetime.now().strftime('%d/%m/%Y %H:%M:%S')}</td></tr>
        </table>
        <p>Atenciosamente,<br>Sistema Ativus.AI</p>
    </body>
    </html>
    """
    
    message = Mail(
        from_email='rodolfocabral94@outlook.com',
        to_emails='rodolfocabral02@gmail.com',
        subject='Novo cadastro de assinatura - Ativus.AI',
        html_content=html_content
    )
    
    try:
        ssl._create_default_https_context = ssl._create_unverified_context
        sg = SendGridAPIClient(SENDGRID_API_KEY)
        response = sg.send(message)
        print(f"Email enviado com sucesso. Status: {response.status_code}")
    except Exception as e:
        print(f"Erro ao enviar email com SendGrid: {e}")
        raise

