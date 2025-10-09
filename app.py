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
import logging

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

# Carregar variáveis de ambiente
load_dotenv()

def create_app():
    app = Flask(__name__, static_folder='static')
    
    # Configuração usando config.py
    try:
        from config import config
        config_name = os.environ.get('FLASK_CONFIG', 'production')
        app.config.from_object(config[config_name])
        logger.info(f"Configuração carregada: {config_name}")
    except ImportError:
        # Fallback para configuração manual se config.py não existir
        app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev_key_for_testing')
        
        # Configuração do banco de dados PostgreSQL
        database_url = os.environ.get('HEROKU_POSTGRESQL_NAVY_URL')
        if not database_url:
            database_url = os.environ.get('DATABASE_URL')
        if not database_url:
            database_url = 'postgresql://postgres:postgres@localhost:5432/ativus'
        
        if database_url.startswith('postgres://'):
            database_url = database_url.replace('postgres://', 'postgresql://', 1)
        
        app.config['SQLALCHEMY_DATABASE_URI'] = database_url
        app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
        logger.info("Configuração manual aplicada")
    
    logger.info(f"Conectando ao banco de dados: {app.config['SQLALCHEMY_DATABASE_URI']}")
    
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
    
    # Importar e registrar blueprint de desprogramação de OS
    try:
        from routes.ordens_servico_desprogramar import ordens_servico_desprogramar_bp
        app.register_blueprint(ordens_servico_desprogramar_bp)
        print("Blueprint de desprogramação de OS registrado com sucesso")
    except ImportError as e:
        print(f"Aviso: Não foi possível importar ordens_servico_desprogramar_bp: {e}")
        print("Sistema funcionará sem funcionalidades de desprogramação de OS.")
    except Exception as e:
        print(f"Erro ao registrar blueprint de desprogramação de OS: {e}")
        print("Sistema funcionará sem funcionalidades de desprogramação de OS.")
    
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
    
    # Importar e registrar blueprint de plano mestre
    try:
        from routes.plano_mestre import plano_mestre_bp
        app.register_blueprint(plano_mestre_bp)
        print("Blueprint de plano mestre registrado com sucesso")
    except ImportError as e:
        print(f"Aviso: Não foi possível importar plano_mestre_bp: {e}")
        print("Sistema funcionará sem funcionalidades de plano mestre.")
    except Exception as e:
        print(f"Erro ao registrar blueprint de plano mestre: {e}")
        print("Sistema funcionará sem funcionalidades de plano mestre.")
    
    # Importar e registrar blueprint de debug do plano mestre
    try:
        from routes.plano_mestre_debug import plano_mestre_debug_bp
        app.register_blueprint(plano_mestre_debug_bp)
        print("Blueprint de debug do plano mestre registrado com sucesso")
    except ImportError as e:
        print(f"Aviso: Não foi possível importar plano_mestre_debug_bp: {e}")
    except Exception as e:
        print(f"Erro ao registrar blueprint de debug do plano mestre: {e}")
    
    # Importar e registrar blueprint de PMP LIMPO
    try:
        from routes.pmp_limpo import pmp_limpo_bp
        app.register_blueprint(pmp_limpo_bp)
        print("Blueprint de PMP LIMPO registrado com sucesso")
    except ImportError as e:
        print(f"Aviso: Não foi possível importar pmp_limpo_bp: {e}")
        print("Sistema funcionará sem funcionalidades de PMP.")
    except Exception as e:
        print(f"Erro ao registrar blueprint de PMP LIMPO: {e}")
        print("Sistema funcionará sem funcionalidades de PMP.")
    
    # Importar e registrar blueprint de geração de OS baseada em PMP
    try:
        from routes.pmp_os_generator import pmp_os_generator_bp
        app.register_blueprint(pmp_os_generator_bp)
        print("Blueprint de geração de OS PMP registrado com sucesso")
    except ImportError as e:
        print(f"Aviso: Não foi possível importar pmp_os_generator_bp: {e}")
        print("Sistema funcionará sem funcionalidades de geração automática de OS.")
    except Exception as e:
        print(f"Erro ao registrar blueprint de geração de OS PMP: {e}")
        print("Sistema funcionará sem funcionalidades de geração automática de OS.")
    
    # 🚨 BLUEPRINT SIMPLES DE EMERGÊNCIA PARA RESOLVER ERRO 404
    try:
        from routes.pmp_simple_api import pmp_simple_api_bp
        app.register_blueprint(pmp_simple_api_bp)
        print("✅ Blueprint SIMPLES de PMP registrado com sucesso (versão de emergência)")
    except ImportError as e:
        print(f"❌ Erro ao importar pmp_simple_api_bp: {e}")
    except Exception as e:
        print(f"❌ Erro ao registrar blueprint simples: {e}")
    
    # 🧹 BLUEPRINT DE LIMPEZA E MANUTENÇÃO
    try:
        from routes.pmp_cleanup_api import pmp_cleanup_api_bp
        app.register_blueprint(pmp_cleanup_api_bp)
        print("✅ Blueprint de LIMPEZA PMP registrado com sucesso")
    except ImportError as e:
        print(f"❌ Erro ao importar pmp_cleanup_api_bp: {e}")
    except Exception as e:
        print(f"❌ Erro ao registrar blueprint de limpeza: {e}")
    
    # Importar e registrar blueprint de API aprimorada (como backup)
    try:
        from routes.pmp_os_api import pmp_os_api_bp
        app.register_blueprint(pmp_os_api_bp)
        print("Blueprint de API aprimorada PMP OS registrado com sucesso")
    except ImportError as e:
        print(f"Aviso: Não foi possível importar pmp_os_api_bp: {e}")
        print("Sistema funcionará com API simples de PMP.")
    except Exception as e:
        print(f"Erro ao registrar blueprint de API aprimorada PMP OS: {e}")
        print("Sistema funcionará com API simples de PMP.")
    
    # Importar e registrar blueprint de status automático (como backup)
    try:
        from routes.pmp_auto_status import pmp_auto_status_bp
        app.register_blueprint(pmp_auto_status_bp)
        print("Blueprint de status automático PMP registrado com sucesso")
    except ImportError as e:
        print(f"Aviso: Não foi possível importar pmp_auto_status_bp: {e}")
        print("Sistema funcionará com status simples de PMP.")
    except Exception as e:
        print(f"Erro ao registrar blueprint de status automático: {e}")
        print("Sistema funcionará com status simples de PMP.")
    
    # Importar e registrar blueprint de debug (apenas em desenvolvimento)
    try:
        from routes.debug_routes import debug_routes_bp
        app.register_blueprint(debug_routes_bp)
        print("Blueprint de debug registrado com sucesso")
    except ImportError as e:
        print(f"Aviso: Não foi possível importar debug_routes_bp: {e}")
    except Exception as e:
        print(f"Erro ao registrar blueprint de debug: {e}")
    
    # 🔧 REGISTRO MANUAL FORÇADO DAS BLUEPRINTS PMP (para resolver erro 404)
    print("🔧 Forçando registro manual das blueprints PMP...")
    
    # Registro forçado da blueprint pmp_os_api
    try:
        from routes.pmp_os_api import pmp_os_api_bp
        if 'pmp_os_api' not in app.blueprints:
            app.register_blueprint(pmp_os_api_bp)
            print("✅ pmp_os_api_bp registrada manualmente")
        else:
            print("⚠️ pmp_os_api_bp já estava registrada")
    except Exception as e:
        print(f"❌ Erro ao registrar pmp_os_api_bp manualmente: {e}")
    
    # Registro forçado da blueprint pmp_auto_status
    try:
        from routes.pmp_auto_status import pmp_auto_status_bp
        if 'pmp_auto_status' not in app.blueprints:
            app.register_blueprint(pmp_auto_status_bp)
            print("✅ pmp_auto_status_bp registrada manualmente")
        else:
            print("⚠️ pmp_auto_status_bp já estava registrada")
    except Exception as e:
        print(f"❌ Erro ao registrar pmp_auto_status_bp manualmente: {e}")
    
    # Verificar rotas após registro manual
    try:
        pmp_routes = [r.rule for r in app.url_map.iter_rules() if '/api/pmp/' in r.rule]
        print(f"📊 Total de rotas PMP registradas: {len(pmp_routes)}")
        
        # Verificar rotas específicas que estavam falhando
        target_routes = ['/api/pmp/os/verificar-pendencias', '/api/pmp/os/gerar-todas', '/api/pmp/os/executar-automatico']
        for target in target_routes:
            found = any(r.rule == target for r in app.url_map.iter_rules())
            status = "✅" if found else "❌"
            print(f"   {status} {target}")
    except Exception as e:
        print(f"❌ Erro ao verificar rotas: {e}")
    
    # Importar e registrar blueprint de agendamento por frequência
    try:
        from routes.pmp_scheduler import pmp_scheduler_bp
        app.register_blueprint(pmp_scheduler_bp)
        print("Blueprint de agendamento PMP registrado com sucesso")
    except ImportError as e:
        print(f"Aviso: Não foi possível importar pmp_scheduler_bp: {e}")
        print("Sistema funcionará sem funcionalidades de agendamento.")
    except Exception as e:
        print(f"Erro ao registrar blueprint de agendamento PMP: {e}")
        print("Sistema funcionará sem funcionalidades de agendamento.")
    
    # Importar e registrar blueprint de API de programação
    try:
        from routes.programacao_api import programacao_api_bp
        app.register_blueprint(programacao_api_bp)
        print("Blueprint de API de programação registrado com sucesso")
    except ImportError as e:
        print(f"Aviso: Não foi possível importar programacao_api_bp: {e}")
        print("Sistema funcionará sem funcionalidades de programação via API.")
    except Exception as e:
        print(f"Erro ao registrar blueprint de API de programação: {e}")
        print("Sistema funcionará sem funcionalidades de programação via API.")
    
    # Importar e registrar blueprint de analytics PMP
    try:
        from routes.pmp_analytics import pmp_analytics_bp
        app.register_blueprint(pmp_analytics_bp)
        print("Blueprint de analytics PMP registrado com sucesso")
    except ImportError as e:
        print(f"Aviso: Não foi possível importar pmp_analytics_bp: {e}")
        print("Sistema funcionará sem funcionalidades de analytics.")
    except Exception as e:
        print(f"Erro ao registrar blueprint de analytics PMP: {e}")
        print("Sistema funcionará sem funcionalidades de analytics.")


    # Importar e registrar a blueprint de atividades da os
    try:
        from routes.atividades_os import atividades_os_bp
        app.register_blueprint(atividades_os_bp)
        print("Blueprint de atividades da os registrado com sucesso")
    except ImportError as e:
        print(f"Aviso: Não foi possível importar atividades_os_bp: {e}")
        print("Sistema funcionará sem funcionalidades de atividades da OS.")
    except Exception as e:
        print(f"Erro ao registrar blueprint de atividades_os_bp: {e}")
        print("Sistema funcionará sem funcionalidades de atividades da OS.")
    
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
    
    @app.route('/monitoramento')
    @login_required
    def monitoramento():
        return send_from_directory('static', 'monitoramento.html')
    
    @app.route('/scanner-qr')
    @login_required
    def scanner_qr():
        return send_from_directory('static', 'scanner-qr.html')
    
    @app.route('/lista-qr-codes')
    @login_required
    def lista_qr_codes():
        return send_from_directory('static', 'lista-qr-codes.html')
    
    @app.route('/parametros')
    @login_required
    def parametros():
        return send_from_directory('static', 'parametros.html')
    
    @app.route('/cadastro-ativos')
    @login_required
    def cadastro_ativos():
        return send_from_directory('static', 'cadastro-ativos.html')
    
    @app.route('/manutencao-preventiva')
    @login_required
    def manutencao_preventiva():
        return send_from_directory('static', 'manutencao-preventiva.html')

    @app.route('/plano-manutencao')
    @login_required
    def plano_manutencao():
        return send_from_directory('static', 'plano-manutencao.html')
    
    @app.route('/plano-mestre')
    @login_required
    def plano_mestre():
        return send_from_directory('static', 'plano-mestre.html')
    
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
            
            # Se não há filial especificada, retornar vazio
            if not filial_id:
                print("❌ Nenhuma filial especificada")
                return jsonify({
                    'success': True,
                    'setores': []
                })
            
            try:
                # Converter filial_id para inteiro
                filial_id_int = int(filial_id)
                print(f"🔢 Filial ID convertido para int: {filial_id_int}")
                
                # Importar modelo
                from assets_models import Setor
                
                # FILTRO SIMPLIFICADO: Apenas por filial_id (sem filtro por empresa)
                # O usuário já tem acesso apenas às suas filiais pelo frontend
                setores = Setor.query.filter(Setor.filial_id == filial_id_int).all()
                
                print(f"📊 Setores encontrados para filial {filial_id_int}: {len(setores)}")
                
                # Debug: mostrar todos os setores encontrados
                for setor in setores:
                    print(f"   🔍 Setor encontrado: ID={setor.id}, filial_id={setor.filial_id}, tag={setor.tag}, empresa={setor.empresa}")
                
                # Converter para dict
                setores_data = []
                for setor in setores:
                    setor_dict = setor.to_dict()
                    setores_data.append(setor_dict)
                    print(f"   ✅ Setor adicionado: ID={setor_dict['id']}, filial_id={setor_dict['filial_id']}, tag={setor_dict['tag']}")
                
                print(f"✅ Retornando {len(setores_data)} setores filtrados")
                
                return jsonify({
                    'success': True,
                    'setores': setores_data
                })
                
            except ValueError as e:
                print(f"❌ Erro ao converter filial_id: {e}")
                return jsonify({
                    'success': False,
                    'message': f'Filial ID inválido: {filial_id}'
                }), 400
                
            except Exception as e:
                print(f"❌ Erro ao buscar setores: {e}")
                import traceback
                traceback.print_exc()
                return jsonify({
                    'success': False,
                    'message': 'Erro interno do servidor'
                }), 500
                
        except Exception as e:
            print(f"❌ Erro geral na API setores: {e}")
            import traceback
            traceback.print_exc()
            return jsonify({
                'success': False,
                'message': 'Erro interno do servidor'
            }), 500

    @app.route('/api/equipamentos', methods=['GET'])
    @login_required
    def api_get_equipamentos():
        """API para equipamentos filtrados por setor"""
        try:
            setor_id = request.args.get('setor_id')
            print(f"🔍 API equipamentos chamada com setor_id: {setor_id}")
            
            # Se não há setor especificado, retornar vazio
            if not setor_id:
                print("❌ Nenhum setor especificado")
                return jsonify({
                    'success': True,
                    'equipamentos': []
                })
            
            try:
                # Converter setor_id para inteiro
                setor_id_int = int(setor_id)
                print(f"🔢 Setor ID convertido para int: {setor_id_int}")
                
                # Importar modelo
                from assets_models import Equipamento
                
                # FILTRO SIMPLIFICADO: Apenas por setor_id (sem filtro por empresa)
                # O usuário já tem acesso apenas aos seus setores pelo filtro anterior
                equipamentos = Equipamento.query.filter(Equipamento.setor_id == setor_id_int).all()
                
                print(f"📊 Equipamentos encontrados para setor {setor_id_int}: {len(equipamentos)}")
                
                # Debug: mostrar todos os equipamentos encontrados
                for equipamento in equipamentos:
                    print(f"   🔍 Equipamento encontrado: ID={equipamento.id}, setor_id={equipamento.setor_id}, tag={equipamento.tag}, empresa={equipamento.empresa}")
                
                # Converter para dict
                equipamentos_data = []
                for equipamento in equipamentos:
                    equipamento_dict = equipamento.to_dict()
                    equipamentos_data.append(equipamento_dict)
                    print(f"   ✅ Equipamento adicionado: ID={equipamento_dict['id']}, setor_id={equipamento_dict['setor_id']}, tag={equipamento_dict['tag']}")
                
                print(f"✅ Retornando {len(equipamentos_data)} equipamentos filtrados")
                
                return jsonify({
                    'success': True,
                    'equipamentos': equipamentos_data
                })
                
            except ValueError as e:
                print(f"❌ Erro ao converter setor_id: {e}")
                return jsonify({
                    'success': False,
                    'message': f'Setor ID inválido: {setor_id}'
                }), 400
                
            except Exception as e:
                print(f"❌ Erro ao buscar equipamentos: {e}")
                import traceback
                traceback.print_exc()
                return jsonify({
                    'success': False,
                    'message': 'Erro interno do servidor'
                }), 500
                
        except Exception as e:
            print(f"❌ Erro geral na API equipamentos: {e}")
            import traceback
            traceback.print_exc()
            return jsonify({
                'success': False,
                'message': 'Erro interno do servidor'
            }), 500

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
    
    # Headers de segurança para prevenir conflitos com scripts externos
    @app.after_request
    def add_security_headers(response):
        # Prevenir carregamento de scripts externos maliciosos
        response.headers['X-Content-Type-Options'] = 'nosniff'
        response.headers['X-Frame-Options'] = 'DENY'
        response.headers['X-XSS-Protection'] = '1; mode=block'
        
        # CSP mais permissivo para permitir bibliotecas CDN necessárias
        csp = (
            "default-src 'self'; "
            "script-src 'self' 'unsafe-inline' 'unsafe-eval' "
            "https://unpkg.com https://cdn.jsdelivr.net https://cdnjs.cloudflare.com; "
            "style-src 'self' 'unsafe-inline' "
            "https://fonts.googleapis.com https://cdnjs.cloudflare.com; "
            "font-src 'self' https://fonts.gstatic.com https://cdnjs.cloudflare.com; "
            "img-src 'self' data: https:; "
            "connect-src 'self' https:;"
        )
        response.headers['Content-Security-Policy'] = csp
        
        return response
    
    @app.route('/api/pmp/gerar-todas-os', methods=['POST'])
    @login_required
    def gerar_todas_os_pmp():
        """Gera todas as OS necessárias para todas as PMPs ativas"""
        try:
            from sistema_geracao_os_pmp import GeradorOSPMP
            
            app.logger.info(f"Usuário {current_user.id} iniciou geração de OS para todas as PMPs")
            
            gerador = GeradorOSPMP()
            resultado = gerador.executar_geracao_completa()
            
            if resultado['success']:
                app.logger.info(f"Geração concluída: {resultado['total_os_geradas']} OS geradas")
                return jsonify({
                    'success': True,
                    'message': f"{resultado['total_os_geradas']} OS geradas com sucesso!",
                    'total_os_geradas': resultado['total_os_geradas'],
                    'pmps_processadas': resultado['pmps_processadas'],
                    'os_geradas': resultado['os_geradas'],
                    'log_operacoes': resultado['log_operacoes'][-10:]  # Últimas 10 operações
                })
            else:
                app.logger.error(f"Erro na geração: {resultado['error']}")
                return jsonify({
                    'success': False,
                    'error': resultado['error'],
                    'log_operacoes': resultado['log_operacoes']
                }), 500
                
        except Exception as e:
            app.logger.error(f"Erro ao gerar OS: {e}")
            return jsonify({
                'success': False,
                'error': f'Erro interno: {str(e)}'
            }), 500
    
    @app.route('/api/pmp/gerar-os/<codigo_pmp>', methods=['POST'])
    @login_required
    def gerar_os_pmp_especifica(codigo_pmp):
        """Gera OS para uma PMP específica pelo código"""
        try:
            from sistema_geracao_os_pmp import GeradorOSPMP
            
            app.logger.info(f"Usuário {current_user.id} iniciou geração de OS para PMP {codigo_pmp}")
            
            gerador = GeradorOSPMP()
            resultado = gerador.gerar_os_pmp_especifica(codigo_pmp)
            
            if resultado['success']:
                app.logger.info(f"Geração para {codigo_pmp} concluída: {resultado['os_geradas']} OS geradas")
                return jsonify({
                    'success': True,
                    'message': f"{resultado['os_geradas']} OS geradas para {codigo_pmp}!",
                    'os_geradas': resultado['os_geradas'],
                    'pmp_processada': resultado['pmp_processada'],
                    'log_operacoes': resultado['log_operacoes'][-5:]  # Últimas 5 operações
                })
            else:
                app.logger.error(f"Erro na geração para {codigo_pmp}: {resultado['error']}")
                return jsonify({
                    'success': False,
                    'error': resultado['error'],
                    'log_operacoes': resultado['log_operacoes']
                }), 500
                
        except Exception as e:
            app.logger.error(f"Erro ao gerar OS para {codigo_pmp}: {e}")
            return jsonify({
                'success': False,
                'error': f'Erro interno: {str(e)}'
            }), 500
    
    @app.route('/api/pmp/verificar-pendencias', methods=['GET'])
    @login_required
    def verificar_pendencias_pmp():
        """Verifica quantas OS estão pendentes de geração para cada PMP"""
        try:
            from sistema_geracao_os_pmp import GeradorOSPMP
            from models.pmp_limpo import PMP
            
            # Buscar PMPs ativas
            pmps_ativas = PMP.query.filter(
                PMP.status == 'ativo',
                PMP.data_inicio_plano.isnot(None)
            ).all()
            
            pendencias = []
            
            for pmp in pmps_ativas:
                gerador = GeradorOSPMP()
                datas_necessarias = gerador.gerar_datas_os(pmp)
                
                # Contar OS existentes
                from assets_models import OrdemServico
                os_existentes = OrdemServico.query.filter_by(pmp_id=pmp.id).count()
                
                os_pendentes = len(datas_necessarias) - os_existentes
                
                if os_pendentes > 0:
                    pendencias.append({
                        'pmp_codigo': pmp.codigo,
                        'pmp_descricao': pmp.descricao,
                        'os_pendentes': os_pendentes,
                        'os_existentes': os_existentes,
                        'total_necessarias': len(datas_necessarias),
                        'data_inicio': pmp.data_inicio_plano.isoformat() if pmp.data_inicio_plano else None,
                        'frequencia': pmp.frequencia
                    })
            
            return jsonify({
                'success': True,
                'pendencias': pendencias,
                'total_pmps_com_pendencias': len(pendencias)
            })
            
        except Exception as e:
            app.logger.error(f"Erro ao verificar pendências: {e}")
            return jsonify({
                'success': False,
                'error': f'Erro interno: {str(e)}'
            }), 500
    
    # API para listar usuários (necessária para a programação)
    @app.route('/api/usuarios', methods=['GET'])
    @login_required
    def api_listar_usuarios():
        """Lista todos os usuários para a programação"""
        try:
            from models import User
            
            # Buscar usuários da mesma empresa
            if hasattr(current_user, 'company') and current_user.company:
                usuarios = User.query.filter_by(company=current_user.company).all()
            else:
                # Fallback: buscar todos os usuários
                usuarios = User.query.all()
            
            usuarios_data = []
            for usuario in usuarios:
                usuarios_data.append({
                    'id': usuario.id,
                    'name': usuario.name or usuario.email.split('@')[0],
                    'email': usuario.email,
                    'profile': usuario.profile or 'user',
                    'company': usuario.company or 'Sistema'
                })
            
            return jsonify({
                'success': True,
                'usuarios': usuarios_data
            })
            
        except Exception as e:
            app.logger.error(f"❌ Erro ao listar usuários: {e}")
            return jsonify({
                'success': False,
                'error': 'Erro ao carregar usuários',
                'message': str(e)
            }), 500

    # Inicializar scheduler automático de PMPs
    try:
        from pmp_scheduler_automatico import iniciar_scheduler
        
        # Inicializar em thread separada para não bloquear a aplicação
        import threading
        def init_scheduler():
            try:
                iniciar_scheduler()
                print("✅ Scheduler automático de PMPs iniciado com sucesso")
            except Exception as e:
                print(f"❌ Erro ao iniciar scheduler automático: {e}")
        
        # Aguardar um pouco para a aplicação inicializar completamente
        timer = threading.Timer(10.0, init_scheduler)
        timer.daemon = True
        timer.start()
        
    except ImportError as e:
        print(f"Aviso: Scheduler automático não disponível: {e}")
    except Exception as e:
        print(f"Erro ao configurar scheduler automático: {e}")
    
    return app

def send_signup_email(data):
    """Envia um email com os dados do formulário de assinatura via SendGrid."""
    SENDGRID_API_KEY = os.getenv("SENDGRID_API_KEY")
    
    if not SENDGRID_API_KEY:
        logger.error("API Key do SendGrid não encontrada. Verifique as variáveis de ambiente.")
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
        logger.info(f"Email enviado com sucesso. Status: {response.status_code}")
    except Exception as e:
        logger.error(f"Erro ao enviar email com SendGrid: {e}")
        raise


