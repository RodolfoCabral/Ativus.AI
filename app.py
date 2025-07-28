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
    
    # Importar e registrar blueprint de chamados
    try:
        from routes.chamados import chamados_bp
        app.register_blueprint(chamados_bp)
        print("Blueprint de chamados registrado com sucesso")
    except ImportError as e:
        print(f"Aviso: Não foi possível importar chamados_bp: {e}")
        print("Sistema funcionará sem funcionalidades de chamados.")
    except Exception as e:
        print(f"Erro ao registrar blueprint de chamados: {e}")
        print("Sistema funcionará sem funcionalidades de chamados.")
    
    # Importar e registrar blueprint de ordens de serviço
    try:
        from routes.ordens_servico import ordens_servico_bp
        app.register_blueprint(ordens_servico_bp)
        print("Blueprint de ordens de serviço registrado com sucesso")
    except ImportError as e:
        print(f"Aviso: Não foi possível importar ordens_servico_bp: {e}")
        print("Sistema funcionará sem funcionalidades de OS.")
    except Exception as e:
        print(f"Erro ao registrar blueprint de ordens de serviço: {e}")
        print("Sistema funcionará sem funcionalidades de OS.")
    
    # Importar e registrar blueprint de execução de OS
    try:
        from routes.execucao_os import execucao_bp
        app.register_blueprint(execucao_bp)
        print("Blueprint de execução de OS registrado com sucesso")
    except ImportError as e:
        print(f"Aviso: Não foi possível importar execucao_bp: {e}")
        print("Sistema funcionará sem funcionalidades de execução de OS.")
    except Exception as e:
        print(f"Erro ao registrar blueprint de execução de OS: {e}")
        print("Sistema funcionará sem funcionalidades de execução de OS.")
    
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
    
    @app.route('/chamados/abertos')
    @login_required
    def chamados_abertos():
        return send_from_directory('static', 'chamados-abertos.html')
    
    @app.route('/chamados/historico')
    @login_required
    def chamados_historico():
        return send_from_directory('static', 'chamados-historico.html')
    
    @app.route('/programacao')
    @login_required
    def programacao():
        return send_from_directory('static', 'programacao.html')
    
    @app.route('/executar-os')
    @login_required
    def executar_os():
        return send_from_directory('static', 'executar-os.html')
    
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
    
    # APIs simplificadas para ativos com filtros sequenciais
    @app.route('/api/filiais', methods=['GET'])
    @login_required
    def api_get_filiais():
        """API para filiais do usuário"""
        try:
            # Tentar usar dados reais se disponível
            try:
                from assets_models import Filial
                filiais = Filial.query.filter_by(empresa=current_user.company).all()
                filiais_data = [filial.to_dict() for filial in filiais]
            except:
                # Fallback para dados mock se não houver tabela
                filiais_data = [
                    {
                        'id': 1,
                        'tag': 'F01',
                        'descricao': 'Unidade Olinda',
                        'endereco': 'Rua Principal, 123',
                        'cidade': 'Olinda',
                        'estado': 'PE',
                        'email': 'filial@empresa.com',
                        'telefone': '(81) 99999-9999',
                        'cnpj': '12.345.678/0001-90',
                        'empresa': current_user.company,
                        'data_criacao': '2024-06-26T10:00:00',
                        'usuario_criacao': current_user.email
                    },
                    {
                        'id': 2,
                        'tag': 'F02',
                        'descricao': 'Unidade Recife',
                        'endereco': 'Av. Boa Viagem, 456',
                        'cidade': 'Recife',
                        'estado': 'PE',
                        'email': 'recife@empresa.com',
                        'telefone': '(81) 88888-8888',
                        'cnpj': '12.345.678/0002-71',
                        'empresa': current_user.company,
                        'data_criacao': '2024-06-26T10:00:00',
                        'usuario_criacao': current_user.email
                    }
                ]
            
            return jsonify({
                'success': True,
                'filiais': filiais_data
            })
        except Exception as e:
            return jsonify({'success': False, 'message': str(e)}), 500

    @app.route('/api/setores', methods=['GET'])
    @login_required
    def api_get_setores():
        """API para setores filtrados por filial"""
        try:
            filial_id = request.args.get('filial_id')
            print(f"🔍 API setores chamada com filial_id: {filial_id}")
            
            # Tentar usar dados reais se disponível
            try:
                from assets_models import Setor
                if filial_id:
                    setores = Setor.query.filter_by(filial_id=filial_id).all()
                    print(f"📊 Encontrados {len(setores)} setores reais para filial {filial_id}")
                else:
                    setores = Setor.query.all()
                    print(f"📊 Encontrados {len(setores)} setores reais (todos)")
                setores_data = [setor.to_dict() for setor in setores]
            except Exception as e:
                print(f"⚠️ Usando dados mock para setores: {e}")
                # Fallback para dados mock se não houver tabela
                setores_mock = [
                    {
                        'id': 1,
                        'tag': 'PM',
                        'descricao': 'Pré-moldagem',
                        'filial_id': 1,
                        'empresa': current_user.company,
                        'data_criacao': '2024-06-26T10:00:00',
                        'usuario_criacao': current_user.email
                    },
                    {
                        'id': 2,
                        'tag': 'MT',
                        'descricao': 'Manutenção',
                        'filial_id': 1,
                        'empresa': current_user.company,
                        'data_criacao': '2024-06-26T10:00:00',
                        'usuario_criacao': current_user.email
                    },
                    {
                        'id': 3,
                        'tag': 'AD',
                        'descricao': 'Administrativo',
                        'filial_id': 2,
                        'empresa': current_user.company,
                        'data_criacao': '2024-06-26T10:00:00',
                        'usuario_criacao': current_user.email
                    }
                ]
                
                # Filtrar por filial se especificado
                if filial_id:
                    setores_data = [s for s in setores_mock if s['filial_id'] == int(filial_id)]
                    print(f"📊 Filtrados {len(setores_data)} setores mock para filial {filial_id}")
                else:
                    setores_data = setores_mock
                    print(f"📊 Retornando {len(setores_data)} setores mock (todos)")
            
            print(f"✅ Retornando {len(setores_data)} setores")
            return jsonify({
                'success': True,
                'setores': setores_data
            })
        except Exception as e:
            print(f"❌ Erro na API setores: {e}")
            return jsonify({'success': False, 'message': str(e)}), 500

    @app.route('/api/equipamentos', methods=['GET'])
    @login_required
    def api_get_equipamentos():
        """API para equipamentos filtrados por setor"""
        try:
            setor_id = request.args.get('setor_id')
            print(f"🔍 API equipamentos chamada com setor_id: {setor_id}")
            
            # Tentar usar dados reais se disponível
            try:
                from assets_models import Equipamento
                if setor_id:
                    equipamentos = Equipamento.query.filter_by(setor_id=setor_id).all()
                    print(f"📊 Encontrados {len(equipamentos)} equipamentos reais para setor {setor_id}")
                else:
                    equipamentos = Equipamento.query.all()
                    print(f"📊 Encontrados {len(equipamentos)} equipamentos reais (todos)")
                equipamentos_data = [equipamento.to_dict() for equipamento in equipamentos]
            except Exception as e:
                print(f"⚠️ Usando dados mock para equipamentos: {e}")
                # Fallback para dados mock se não houver tabela
                equipamentos_mock = [
                    {
                        'id': 1,
                        'tag': 'EQP001',
                        'descricao': 'Máquina de Corte',
                        'setor_id': 1,
                        'empresa': current_user.company,
                        'data_criacao': '2024-06-26T10:00:00',
                        'usuario_criacao': current_user.email
                    },
                    {
                        'id': 2,
                        'tag': 'EQP002',
                        'descricao': 'Prensa Hidráulica',
                        'setor_id': 1,
                        'empresa': current_user.company,
                        'data_criacao': '2024-06-26T10:00:00',
                        'usuario_criacao': current_user.email
                    },
                    {
                        'id': 3,
                        'tag': 'EQP003',
                        'descricao': 'Soldadora',
                        'setor_id': 2,
                        'empresa': current_user.company,
                        'data_criacao': '2024-06-26T10:00:00',
                        'usuario_criacao': current_user.email
                    },
                    {
                        'id': 4,
                        'tag': 'EQP004',
                        'descricao': 'Computador',
                        'setor_id': 3,
                        'empresa': current_user.company,
                        'data_criacao': '2024-06-26T10:00:00',
                        'usuario_criacao': current_user.email
                    }
                ]
                
                # Filtrar por setor se especificado
                if setor_id:
                    equipamentos_data = [e for e in equipamentos_mock if e['setor_id'] == int(setor_id)]
                    print(f"📊 Filtrados {len(equipamentos_data)} equipamentos mock para setor {setor_id}")
                else:
                    equipamentos_data = equipamentos_mock
                    print(f"📊 Retornando {len(equipamentos_data)} equipamentos mock (todos)")
            
            print(f"✅ Retornando {len(equipamentos_data)} equipamentos")
            return jsonify({
                'success': True,
                'equipamentos': equipamentos_data
            })
        except Exception as e:
            print(f"❌ Erro na API equipamentos: {e}")
            return jsonify({'success': False, 'message': str(e)}), 500

    # API para informações do usuário
    @app.route('/api/user', methods=['GET'])
    @login_required
    def api_get_user():
        """Retorna informações do usuário logado"""
        try:
            return jsonify({
                'success': True,
                'user': {
                    'id': current_user.id,
                    'name': current_user.name or current_user.email.split('@')[0],
                    'email': current_user.email,
                    'company': current_user.company or 'Empresa',
                    'profile': current_user.profile or 'user'
                }
            })
        except Exception as e:
            return jsonify({'success': False, 'message': str(e)}), 500

    # API para logout
    @app.route('/api/logout', methods=['POST'])
    @login_required
    def api_logout():
        """Realiza logout do usuário"""
        try:
            logout_user()
            return jsonify({
                'success': True,
                'message': 'Logout realizado com sucesso'
            })
        except Exception as e:
            return jsonify({'success': False, 'message': str(e)}), 500
    
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

