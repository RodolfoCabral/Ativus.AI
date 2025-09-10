from flask import Blueprint, request, jsonify, session
from flask_login import current_user, login_required
from models import db
from datetime import datetime, date

# Importação segura dos modelos
try:
    from assets_models import OrdemServico, Chamado
    OS_AVAILABLE = True
except ImportError as e:
    print(f"Erro ao importar modelos de OS: {e}")
    OS_AVAILABLE = False

ordens_servico_desprogramar_bp = Blueprint('ordens_servico_desprogramar', __name__)

def get_current_user():
    """Obtém informações do usuário atual da sessão"""
    if current_user.is_authenticated:
        return {
            'name': current_user.name or current_user.email.split('@')[0],
            'company': current_user.company or 'Empresa',
            'profile': current_user.profile or 'user'
        }
    else:
        return {
            'name': session.get('user_name', 'Usuário'),
            'company': session.get('user_company', 'Empresa'),
            'profile': session.get('user_profile', 'user')
        }

@ordens_servico_desprogramar_bp.route('/api/ordens-servico/<int:os_id>/desprogramar', methods=['PUT'])
def desprogramar_ordem_servico(os_id):
    """Desprogramar uma ordem de serviço"""
    if not OS_AVAILABLE:
        return jsonify({'error': 'Funcionalidade de OS não disponível'}), 503

    try:
        # Obter informações do usuário atual
        try:
            user_info = get_current_user()
        except:
            # Fallback para sessão
            user_info = {
                'name': session.get('user_name', 'Sistema'),
                'company': session.get('user_company', 'Sistema')
            }

        # Buscar a ordem de serviço
        ordem_servico = OrdemServico.query.filter_by(id=os_id).first()
        if not ordem_servico:
            return jsonify({'error': 'Ordem de Serviço não encontrada'}), 404

        # Verificar se a OS pertence à empresa do usuário
        if ordem_servico.empresa != user_info['company']:
            return jsonify({'error': 'Acesso negado a esta Ordem de Serviço'}), 403

        # Verificar se a OS está em um estado que permite desprogramação
        if ordem_servico.status not in ['programada', 'aberta']:
            return jsonify({'error': f'Não é possível desprogramar OS no estado {ordem_servico.status}'}), 400

        # Desprogramar a OS
        ordem_servico.data_programada = None
        ordem_servico.usuario_responsavel = None
        ordem_servico.status = 'aberta'
        ordem_servico.data_atualizacao = datetime.utcnow()

        # Atualizar status do chamado, se houver
        if ordem_servico.chamado_id:
            chamado = Chamado.query.filter_by(id=ordem_servico.chamado_id).first()
            if chamado:
                chamado.status = 'os_criada'  # Voltar para o status anterior à programação

        # Salvar alterações
        db.session.commit()

        return jsonify({
            'success': True,
            'message': 'Ordem de Serviço desprogramada com sucesso',
            'ordem_servico': ordem_servico.to_dict()
        })

    except Exception as e:
        db.session.rollback()
        print(f"Erro ao desprogramar OS: {e}")
        return jsonify({'error': f'Erro interno do servidor: {str(e)}'}), 500

