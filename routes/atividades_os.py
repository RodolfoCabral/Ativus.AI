from flask import Blueprint, jsonify, request
from flask_login import login_required, current_user
from models import db
from models.atividade_os import AtividadeOS
from assets_models import OrdemServico
import logging

logger = logging.getLogger(__name__)

atividades_os_bp = Blueprint('atividades_os', __name__)

@atividades_os_bp.route('/api/os/<int:os_id>/atividades', methods=['GET'])
@login_required
def listar_atividades_os(os_id):
    """Lista todas as atividades de uma OS específica"""
    try:
        # Buscar a OS primeiro (sem filtro de empresa para debug)
        os = OrdemServico.query.filter_by(id=os_id).first()
        
        if not os:
            logger.error(f"OS {os_id} não encontrada no banco de dados")
            return jsonify({'error': 'OS não encontrada'}), 404
        
        logger.info(f"OS {os_id} encontrada: {os.descricao}")
        
        # Verificar se o usuário tem acesso (se tiver empresa definida)
        if hasattr(current_user, 'empresa') and current_user.empresa:
            if os.empresa != current_user.empresa:
                logger.warning(f"Usuário da empresa {current_user.empresa} tentando acessar OS da empresa {os.empresa}")
                return jsonify({'error': 'Acesso negado à OS'}), 403
        
        # Buscar atividades
        atividades = AtividadeOS.query.filter_by(os_id=os_id).order_by(AtividadeOS.ordem).all()
        logger.info(f"Encontradas {len(atividades)} atividades para OS {os_id}")
        
        # Converter para dicionário
        atividades_dict = [atividade.to_dict() for atividade in atividades]
        
        return jsonify({
            'os_id': os_id,
            'os_descricao': os.descricao,
            'os_tipo': os.tipo_manutencao,
            'os_status': os.status,
            'atividades': atividades_dict
        })
    
    except Exception as e:
        logger.error(f"Erro ao listar atividades da OS {os_id}: {str(e)}")
        return jsonify({'error': str(e)}), 500

@atividades_os_bp.route('/api/os/atividades/<int:atividade_id>/avaliar', methods=['PUT'])
@login_required
def avaliar_atividade_os(atividade_id):
    """Atualiza o status de conformidade e observação de uma atividade"""
    try:
        # Verificar se a atividade existe e pertence à empresa do usuário
        atividade = db.session.query(AtividadeOS).join(OrdemServico).filter(
            AtividadeOS.id == atividade_id,
            OrdemServico.empresa == current_user.empresa
        ).first()
        
        if not atividade:
            return jsonify({'error': 'Atividade não encontrada'}), 404
        
        # Obter dados da requisição
        dados = request.json
        
        # Atualizar status se fornecido
        if 'status' in dados:
            status_validos = ['pendente', 'conforme', 'nao_conforme', 'nao_aplicavel']
            if dados['status'] not in status_validos:
                return jsonify({'error': 'Status inválido'}), 400
            atividade.status = dados['status']
        
        # Atualizar observação se fornecida
        if 'observacao' in dados:
            atividade.observacao = dados['observacao']
        
        # Salvar no banco
        db.session.commit()
        
        return jsonify(atividade.to_dict())
    
    except Exception as e:
        db.session.rollback()
        logger.error(f"Erro ao avaliar atividade {atividade_id}: {str(e)}")
        return jsonify({'error': str(e)}), 500
