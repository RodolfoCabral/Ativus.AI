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
        if hasattr(current_user, 'company') and current_user.company:
            if os.empresa != current_user.company:
                logger.warning(f"Usuário da empresa {current_user.company} tentando acessar OS da empresa {os.empresa}")
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
        logger.info(f"Tentando avaliar atividade {atividade_id}")
        
        # Buscar a atividade diretamente (sem JOIN complexo)
        atividade = AtividadeOS.query.filter_by(id=atividade_id).first()
        
        if not atividade:
            logger.error(f"Atividade {atividade_id} não encontrada")
            return jsonify({'error': 'Atividade não encontrada'}), 404
        
        logger.info(f"Atividade {atividade_id} encontrada, OS: {atividade.os_id}")
        
        # Verificar se a OS pertence ao usuário (se empresa estiver definida)
        if hasattr(current_user, 'company') and current_user.company:
            os = OrdemServico.query.filter_by(id=atividade.os_id).first()
            if os and os.empresa != current_user.company:
                logger.warning(f"Usuário da empresa {current_user.company} tentando avaliar atividade da empresa {os.empresa}")
                return jsonify({'error': 'Acesso negado'}), 403
        
        # Obter dados da requisição
        dados = request.json or {}
        logger.info(f"Dados recebidos: {dados}")
        
        # Atualizar status se fornecido
        if 'status' in dados:
            status_validos = ['pendente', 'conforme', 'nao_conforme', 'nao_aplicavel']
            if dados['status'] not in status_validos:
                logger.error(f"Status inválido: {dados['status']}")
                return jsonify({'error': 'Status inválido'}), 400
            
            logger.info(f"Atualizando status de {atividade.status} para {dados['status']}")
            atividade.status = dados['status']
        
        # Atualizar observação se fornecida
        if 'observacao' in dados:
            logger.info(f"Atualizando observação: {dados['observacao']}")
            atividade.observacao = dados['observacao']
        
        # Salvar no banco
        db.session.commit()
        logger.info(f"Atividade {atividade_id} salva com sucesso")
        
        return jsonify({
            'success': True,
            'atividade': atividade.to_dict()
        })
    
    except Exception as e:
        db.session.rollback()
        logger.error(f"Erro ao avaliar atividade {atividade_id}: {str(e)}")
        logger.error(f"Tipo do erro: {type(e)}")
        import traceback
        logger.error(f"Traceback: {traceback.format_exc()}")
        return jsonify({'error': f'Erro interno: {str(e)}'}), 500
