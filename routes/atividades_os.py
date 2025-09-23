from flask import Blueprint, jsonify, request
from models import db
from models.atividade_os import AtividadeOS
from models.assets_models import OrdemServico
import logging

logger = logging.getLogger(__name__)

atividades_os_bp = Blueprint('atividades_os', __name__)

@atividades_os_bp.route('/api/os/<int:os_id>/atividades', methods=['GET'])
def listar_atividades_os(os_id):
    """Lista todas as atividades de uma OS específica"""
    try:
        # Verificar se a OS existe
        os = OrdemServico.query.get(os_id)
        if not os:
            return jsonify({'error': 'OS não encontrada'}), 404
        
        # Buscar atividades
        atividades = AtividadeOS.query.filter_by(os_id=os_id).order_by(AtividadeOS.ordem).all()
        
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
def avaliar_atividade_os(atividade_id):
    """Atualiza o status de conformidade e observação de uma atividade"""
    try:
        # Verificar se a atividade existe
        atividade = AtividadeOS.query.get(atividade_id)
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
