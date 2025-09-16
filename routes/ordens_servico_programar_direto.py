"""
Endpoint para programação de ordens de serviço.
"""

from flask import Blueprint, request, jsonify
from sqlalchemy import text
from app import db
import logging
from datetime import datetime

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Criar blueprint
ordens_servico_programar_bp = Blueprint('ordens_servico_programar', __name__)

@ordens_servico_programar_bp.route('/api/ordens-servico/<int:os_id>/programar', methods=['PUT'])
def programar_os(os_id):
    """
    Programar uma ordem de serviço.
    """
    try:
        # Obter dados da requisição
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'Dados inválidos'}), 400
        
        # Validar dados
        data_programada = data.get('data_programada')
        usuario_responsavel = data.get('usuario_responsavel')
        status = data.get('status', 'programada')
        
        if not data_programada or not usuario_responsavel:
            return jsonify({'error': 'Dados incompletos'}), 400
        
        # Validar formato da data
        try:
            # Tentar converter para data
            datetime.strptime(data_programada, '%Y-%m-%d')
        except ValueError:
            logger.error(f"❌ Formato de data inválido: {data_programada}")
            return jsonify({'error': 'Formato de data inválido'}), 400
        
        # Atualizar ordem de serviço
        query = text("""
            UPDATE ordens_servico
            SET data_programada = :data_programada,
                usuario_responsavel = :usuario_responsavel,
                status = :status
            WHERE id = :os_id
        """)
        
        # Executar query
        with db.engine.connect() as connection:
            connection.execute(query, {
                'data_programada': data_programada,
                'usuario_responsavel': usuario_responsavel,
                'status': status,
                'os_id': os_id
            })
            connection.commit()
        
        logger.info(f"✅ OS {os_id} programada para {data_programada} com {usuario_responsavel}")
        
        return jsonify({
            'message': 'OS programada com sucesso',
            'os_id': os_id,
            'data_programada': data_programada,
            'usuario_responsavel': usuario_responsavel,
            'status': status
        }), 200
    
    except Exception as e:
        logger.error(f"❌ Erro ao programar OS {os_id}: {str(e)}")
        return jsonify({'error': f'Erro ao programar OS: {str(e)}'}), 500

@ordens_servico_programar_bp.route('/api/ordens-servico/<int:os_id>/desprogramar', methods=['POST'])
def desprogramar_os(os_id):
    """
    Desprogramar uma ordem de serviço.
    """
    try:
        # Atualizar ordem de serviço
        query = text("""
            UPDATE ordens_servico
            SET data_programada = NULL,
                usuario_responsavel = NULL,
                status = 'aberta'
            WHERE id = :os_id
        """)
        
        # Executar query
        with db.engine.connect() as connection:
            connection.execute(query, {'os_id': os_id})
            connection.commit()
        
        logger.info(f"✅ OS {os_id} desprogramada")
        
        return jsonify({
            'message': 'OS desprogramada com sucesso',
            'os_id': os_id
        }), 200
    
    except Exception as e:
        logger.error(f"❌ Erro ao desprogramar OS {os_id}: {str(e)}")
        return jsonify({'error': f'Erro ao desprogramar OS: {str(e)}'}), 500

@ordens_servico_programar_bp.route('/api/ordens-servico-programacao', methods=['GET'])
def listar_ordens_servico_programacao():
    """
    Listar todas as ordens de serviço para programação.
    """
    try:
        # Consultar ordens de serviço
        query = text("""
            SELECT id, descricao, prioridade, status, data_programada, 
                   usuario_responsavel, equipamento_id, setor, filial,
                   pmp_id, frequencia_origem
            FROM ordens_servico
            WHERE status IN ('aberta', 'programada')
        """)
        
        # Executar query
        with db.engine.connect() as connection:
            result = connection.execute(query)
            ordens_servico = [dict(row) for row in result]
        
        logger.info(f"✅ {len(ordens_servico)} ordens de serviço encontradas")
        
        return jsonify(ordens_servico), 200
    
    except Exception as e:
        logger.error(f"❌ Erro ao listar ordens de serviço: {str(e)}")
        return jsonify({'error': f'Erro ao listar ordens de serviço: {str(e)}'}), 500

