from flask import Blueprint, request, jsonify
from flask_login import login_required, current_user
from sqlalchemy import text
from datetime import datetime
import logging
from app import db
from assets_models import OrdemServico

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Criar blueprint
ordens_servico_programar_bp = Blueprint('ordens_servico_programar', __name__)

@ordens_servico_programar_bp.route('/api/ordens-servico/<int:os_id>/programar', methods=['PUT'])
@login_required
def programar_os(os_id):
    """
    Programa uma OS para um usuário e data específicos.
    
    Parâmetros:
    - os_id: ID da OS a ser programada
    
    Corpo da requisição:
    {
        "data_programada": "2025-09-10",
        "usuario_responsavel": "Nome do Usuário",
        "status": "programada"
    }
    
    Retorna:
    - 200 OK se a OS foi programada com sucesso
    - 400 Bad Request se os dados estiverem inválidos
    - 404 Not Found se a OS não for encontrada
    - 500 Internal Server Error se ocorrer um erro no servidor
    """
    try:
        # Obter dados da requisição
        data = request.get_json()
        logger.info(f"🔄 Programando OS #{os_id} com dados: {data}")
        
        # Validar dados
        if not data:
            logger.error(f"❌ Dados não fornecidos para OS #{os_id}")
            return jsonify({"error": "Dados não fornecidos"}), 400
        
        # Validar data_programada
        data_programada = data.get('data_programada')
        if not data_programada:
            logger.error(f"❌ Data não fornecida para OS #{os_id}")
            return jsonify({"error": "Data não fornecida"}), 400
        
        # Validar formato da data (YYYY-MM-DD)
        try:
            datetime.strptime(data_programada, '%Y-%m-%d')
        except ValueError:
            logger.error(f"❌ Formato de data inválido: {data_programada}")
            return jsonify({"error": f"Formato de data inválido: {data_programada}"}), 400
        
        # Validar usuario_responsavel
        usuario_responsavel = data.get('usuario_responsavel')
        if not usuario_responsavel:
            logger.error(f"❌ Usuário responsável não fornecido para OS #{os_id}")
            return jsonify({"error": "Usuário responsável não fornecido"}), 400
        
        # Buscar OS no banco de dados
        os = OrdemServico.query.get(os_id)
        if not os:
            logger.error(f"❌ OS #{os_id} não encontrada")
            return jsonify({"error": f"OS #{os_id} não encontrada"}), 404
        
        # Atualizar OS
        os.data_programada = data_programada
        os.usuario_responsavel = usuario_responsavel
        os.status = data.get('status', 'programada')
        
        # Salvar alterações
        db.session.commit()
        
        logger.info(f"✅ OS #{os_id} programada com sucesso para {data_programada} com {usuario_responsavel}")
        
        # Retornar resposta
        return jsonify({
            "message": f"OS #{os_id} programada com sucesso",
            "os": {
                "id": os.id,
                "data_programada": os.data_programada,
                "usuario_responsavel": os.usuario_responsavel,
                "status": os.status
            }
        }), 200
        
    except Exception as e:
        logger.error(f"❌ Erro ao programar OS #{os_id}: {str(e)}")
        db.session.rollback()
        return jsonify({"error": f"Erro ao programar OS: {str(e)}"}), 500

@ordens_servico_programar_bp.route('/api/ordens-servico/<int:os_id>/desprogramar', methods=['POST'])
@login_required
def desprogramar_os(os_id):
    """
    Desprograma uma OS, removendo o usuário responsável e a data programada.
    
    Parâmetros:
    - os_id: ID da OS a ser desprogramada
    
    Retorna:
    - 200 OK se a OS foi desprogramada com sucesso
    - 404 Not Found se a OS não for encontrada
    - 500 Internal Server Error se ocorrer um erro no servidor
    """
    try:
        logger.info(f"🔄 Desprogramando OS #{os_id}")
        
        # Buscar OS no banco de dados
        os = OrdemServico.query.get(os_id)
        if not os:
            logger.error(f"❌ OS #{os_id} não encontrada")
            return jsonify({"error": f"OS #{os_id} não encontrada"}), 404
        
        # Atualizar OS
        os.data_programada = None
        os.usuario_responsavel = None
        os.status = 'aberta'
        
        # Salvar alterações
        db.session.commit()
        
        logger.info(f"✅ OS #{os_id} desprogramada com sucesso")
        
        # Retornar resposta
        return jsonify({
            "message": f"OS #{os_id} desprogramada com sucesso",
            "os": {
                "id": os.id,
                "status": os.status
            }
        }), 200
        
    except Exception as e:
        logger.error(f"❌ Erro ao desprogramar OS #{os_id}: {str(e)}")
        db.session.rollback()
        return jsonify({"error": f"Erro ao desprogramar OS: {str(e)}"}), 500

@ordens_servico_programar_bp.route('/api/ordens-servico-programacao', methods=['GET'])
@login_required
def listar_ordens_servico_programacao():
    """
    Lista ordens de serviço com filtros específicos para a tela de programação.
    Esta é uma API alternativa que não requer autenticação completa.
    
    Parâmetros de query:
    - status: Status das OS a serem listadas (abertas, programada, etc.)
    
    Retorna:
    - 200 OK com a lista de ordens de serviço
    - 500 Internal Server Error se ocorrer um erro no servidor
    """
    try:
        # Obter parâmetros de query
        status = request.args.get('status', 'abertas')
        
        logger.info(f"🔍 Listando OS com status: {status}")
        
        # Construir query base
        query = OrdemServico.query
        
        # Aplicar filtros
        if status == 'abertas':
            query = query.filter(OrdemServico.status == 'aberta')
        elif status == 'programada':
            query = query.filter(OrdemServico.status == 'programada')
        
        # Executar query
        ordens_servico = query.all()
        
        # Converter para dicionários
        ordens_servico_dict = [os.to_dict() for os in ordens_servico]
        
        logger.info(f"✅ {len(ordens_servico_dict)} OS encontradas")
        
        # Retornar resposta
        return jsonify({
            "ordens_servico": ordens_servico_dict
        }), 200
        
    except Exception as e:
        logger.error(f"❌ Erro ao listar OS: {str(e)}")
        return jsonify({"error": f"Erro ao listar OS: {str(e)}"}), 500

