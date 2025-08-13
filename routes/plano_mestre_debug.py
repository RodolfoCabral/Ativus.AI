# Rotas para Plano Mestre - Versão Debug
from flask import Blueprint, request, jsonify, session
from flask_login import login_required, current_user
from models import db
from models.plano_mestre import PlanoMestre, AtividadePlanoMestre, HistoricoExecucaoPlano
from datetime import datetime
import logging

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

plano_mestre_debug_bp = Blueprint('plano_mestre_debug', __name__, url_prefix='/api/plano-mestre-debug')

@plano_mestre_debug_bp.route('/test-auth', methods=['GET'])
def test_auth():
    """Endpoint para testar autenticação"""
    try:
        logger.info("=== TESTE DE AUTENTICAÇÃO ===")
        
        # Verificar session
        session_info = {
            'session_keys': list(session.keys()),
            'session_data': dict(session),
            'has_user_id': 'user_id' in session,
            'has_logged_in': 'logged_in' in session
        }
        
        logger.info(f"Session info: {session_info}")
        
        # Verificar Flask-Login
        try:
            user_info = {
                'is_authenticated': current_user.is_authenticated,
                'user_id': current_user.id if current_user.is_authenticated else None,
                'user_email': current_user.email if current_user.is_authenticated else None
            }
            logger.info(f"Flask-Login info: {user_info}")
        except Exception as e:
            user_info = {'error': str(e)}
            logger.error(f"Erro ao verificar Flask-Login: {e}")
        
        # Verificar Flask-Login
        flask_login_info = {}
        try:
            from flask_login import current_user
            flask_login_info = {
                'current_user_exists': True,
                'is_authenticated': hasattr(current_user, 'is_authenticated') and current_user.is_authenticated,
                'user_id': getattr(current_user, 'id', None) if hasattr(current_user, 'id') else None
            }
        except ImportError:
            flask_login_info = {'current_user_exists': False, 'error': 'Flask-Login não importado'}
        
        logger.info(f"Flask-Login info: {flask_login_info}")
        
        # Verificar headers
        headers_info = {
            'user_agent': request.headers.get('User-Agent'),
            'referer': request.headers.get('Referer'),
            'cookie': request.headers.get('Cookie', 'Nenhum cookie')[:100] + '...' if request.headers.get('Cookie') else 'Nenhum cookie'
        }
        
        logger.info(f"Headers info: {headers_info}")
        
        return jsonify({
            'status': 'success',
            'message': 'Teste de autenticação executado',
            'session': session_info,
            'flask_login': flask_login_info,
            'headers': headers_info,
            'timestamp': datetime.utcnow().isoformat()
        }), 200
        
    except Exception as e:
        logger.error(f"Erro no teste de autenticação: {str(e)}")
        return jsonify({'error': str(e)}), 500

@plano_mestre_debug_bp.route('/equipamento/<int:equipamento_id>/sem-auth', methods=['GET'])
def obter_plano_mestre_sem_auth(equipamento_id):
    """Obter plano mestre SEM verificação de autenticação (apenas para debug)"""
    try:
        logger.info(f"=== DEBUG: Buscando plano mestre para equipamento {equipamento_id} SEM AUTH ===")
        
        # Forçar user_id para teste
        user_id_teste = 1
        
        plano = PlanoMestre.query.filter_by(equipamento_id=equipamento_id).first()
        
        if not plano:
            # Se não existe plano mestre, criar um novo
            plano = PlanoMestre(
                equipamento_id=equipamento_id,
                nome=f"Plano Mestre - Equipamento {equipamento_id}",
                descricao="Plano mestre criado automaticamente (DEBUG)",
                criado_por=user_id_teste
            )
            db.session.add(plano)
            db.session.commit()
            logger.info(f"Novo plano mestre criado para equipamento {equipamento_id}")
        
        # Buscar atividades do plano
        atividades = AtividadePlanoMestre.query.filter_by(
            plano_mestre_id=plano.id
        ).order_by(AtividadePlanoMestre.ordem, AtividadePlanoMestre.criado_em).all()
        
        resultado = {
            'plano_mestre': plano.to_dict(),
            'atividades': [atividade.to_dict() for atividade in atividades],
            'debug_info': {
                'equipamento_id': equipamento_id,
                'user_id_usado': user_id_teste,
                'total_atividades': len(atividades),
                'plano_id': plano.id
            }
        }
        
        logger.info(f"Plano mestre retornado com {len(atividades)} atividades")
        return jsonify(resultado), 200
        
    except Exception as e:
        logger.error(f"Erro ao obter plano mestre (debug): {str(e)}")
        return jsonify({'error': 'Erro interno do servidor', 'details': str(e)}), 500

@plano_mestre_debug_bp.route('/equipamento/<int:equipamento_id>/atividades/sem-auth', methods=['POST'])
def criar_atividade_sem_auth(equipamento_id):
    """Criar nova atividade SEM verificação de autenticação (apenas para debug)"""
    try:
        data = request.get_json()
        logger.info(f"=== DEBUG: Criando atividade para equipamento {equipamento_id} SEM AUTH ===")
        logger.info(f"Dados recebidos: {data}")
        
        # Forçar user_id para teste
        user_id_teste = 1
        
        # Validar dados obrigatórios
        if not data.get('descricao'):
            return jsonify({'error': 'Descrição é obrigatória'}), 400
        
        # Buscar ou criar plano mestre
        plano = PlanoMestre.query.filter_by(equipamento_id=equipamento_id).first()
        if not plano:
            plano = PlanoMestre(
                equipamento_id=equipamento_id,
                nome=f"Plano Mestre - Equipamento {equipamento_id}",
                descricao="Plano mestre criado automaticamente (DEBUG)",
                criado_por=user_id_teste
            )
            db.session.add(plano)
            db.session.flush()  # Para obter o ID
        
        # Determinar próxima ordem
        ultima_ordem = db.session.query(db.func.max(AtividadePlanoMestre.ordem)).filter_by(
            plano_mestre_id=plano.id
        ).scalar() or 0
        
        # Criar nova atividade
        atividade = AtividadePlanoMestre(
            plano_mestre_id=plano.id,
            descricao=data['descricao'],
            oficina=data.get('oficina'),
            tipo_manutencao=data.get('tipo_manutencao'),
            frequencia=data.get('frequencia'),
            conjunto=data.get('conjunto'),
            ponto_controle=data.get('ponto_controle'),
            valor_frequencia=data.get('valor_frequencia'),
            condicao=data.get('condicao'),
            status_ativo=data.get('status_ativo', True),
            criado_por=user_id_teste,
            ordem=ultima_ordem + 1
        )
        
        db.session.add(atividade)
        db.session.commit()
        
        logger.info(f"Atividade criada com sucesso: ID {atividade.id}")
        return jsonify(atividade.to_dict()), 201
        
    except Exception as e:
        db.session.rollback()
        logger.error(f"Erro ao criar atividade (debug): {str(e)}")
        return jsonify({'error': 'Erro interno do servidor', 'details': str(e)}), 500

