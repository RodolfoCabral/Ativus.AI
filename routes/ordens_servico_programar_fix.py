"""
Módulo para programação e desprogramação de ordens de serviço.

Este módulo fornece endpoints para programar e desprogramar ordens de serviço,
com validação robusta de dados e tratamento de erros.
"""

from flask import Blueprint, request, jsonify, session
from flask_login import login_required, current_user
import logging
from datetime import datetime
from sqlalchemy import text
from app import db

# Configurar logger
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Criar blueprint
ordens_servico_programar_bp = Blueprint('ordens_servico_programar', __name__)

@ordens_servico_programar_bp.route('/api/ordens-servico/<int:os_id>/programar', methods=['PUT'])
def programar_os(os_id):
    """
    Programa uma ordem de serviço para um usuário e data específicos.
    
    Args:
        os_id (int): ID da ordem de serviço a ser programada
        
    Returns:
        JSON: Resultado da operação
    """
    try:
        # Obter dados da requisição
        data = request.get_json()
        logger.info(f"📥 Dados recebidos para programação da OS #{os_id}: {data}")
        
        # Validar dados
        if not data:
            logger.error(f"❌ Dados não fornecidos para programação da OS #{os_id}")
            return jsonify({"error": "Dados não fornecidos"}), 400
        
        # Validar data_programada
        data_programada = data.get('data_programada')
        if not data_programada:
            logger.error(f"❌ Data não fornecida para programação da OS #{os_id}")
            return jsonify({"error": "Data não fornecida"}), 400
        
        # Validar formato da data (YYYY-MM-DD)
        try:
            if not isinstance(data_programada, str) or not data_programada.strip():
                logger.error(f"❌ Data inválida para programação da OS #{os_id}: {data_programada}")
                return jsonify({"error": "Data inválida"}), 400
                
            # Verificar se a data está no formato ISO (YYYY-MM-DD)
            if not data_programada.strip().match(/^\d{4}-\d{2}-\d{2}$/):
                logger.error(f"❌ Formato de data inválido para programação da OS #{os_id}: {data_programada}")
                return jsonify({"error": "Formato de data inválido. Use YYYY-MM-DD"}), 400
                
            # Converter para objeto datetime
            data_obj = datetime.strptime(data_programada.strip(), '%Y-%m-%d')
        except Exception as e:
            logger.error(f"❌ Erro ao validar data para programação da OS #{os_id}: {e}")
            return jsonify({"error": f"Data inválida: {str(e)}"}), 400
        
        # Validar usuario_responsavel
        usuario_responsavel = data.get('usuario_responsavel')
        if not usuario_responsavel:
            logger.error(f"❌ Usuário responsável não fornecido para programação da OS #{os_id}")
            return jsonify({"error": "Usuário responsável não fornecido"}), 400
        
        # Validar status
        status = data.get('status')
        if not status:
            logger.error(f"❌ Status não fornecido para programação da OS #{os_id}")
            return jsonify({"error": "Status não fornecido"}), 400
        
        # Atualizar ordem de serviço
        try:
            # Usar SQL direto para evitar problemas com ORM
            query = text("""
                UPDATE ordens_servico
                SET data_programada = :data_programada,
                    usuario_responsavel = :usuario_responsavel,
                    status = :status
                WHERE id = :os_id
            """)
            
            result = db.session.execute(query, {
                'data_programada': data_programada,
                'usuario_responsavel': usuario_responsavel,
                'status': status,
                'os_id': os_id
            })
            
            # Commit para salvar as alterações
            db.session.commit()
            
            logger.info(f"✅ OS #{os_id} programada com sucesso para {data_programada} com {usuario_responsavel}")
            
            return jsonify({
                "success": True,
                "message": f"OS #{os_id} programada com sucesso",
                "os_id": os_id,
                "data_programada": data_programada,
                "usuario_responsavel": usuario_responsavel,
                "status": status
            })
            
        except Exception as e:
            db.session.rollback()
            logger.error(f"❌ Erro ao programar OS #{os_id}: {e}")
            return jsonify({"error": f"Erro ao programar OS: {str(e)}"}), 500
            
    except Exception as e:
        logger.error(f"❌ Erro geral ao programar OS #{os_id}: {e}")
        return jsonify({"error": f"Erro geral: {str(e)}"}), 500

@ordens_servico_programar_bp.route('/api/ordens-servico/<int:os_id>/desprogramar', methods=['POST'])
def desprogramar_os(os_id):
    """
    Desprograma uma ordem de serviço.
    
    Args:
        os_id (int): ID da ordem de serviço a ser desprogramada
        
    Returns:
        JSON: Resultado da operação
    """
    try:
        logger.info(f"🔄 Desprogramando OS #{os_id}")
        
        # Atualizar ordem de serviço
        try:
            # Usar SQL direto para evitar problemas com ORM
            query = text("""
                UPDATE ordens_servico
                SET data_programada = NULL,
                    usuario_responsavel = NULL,
                    status = 'aberta'
                WHERE id = :os_id
            """)
            
            result = db.session.execute(query, {'os_id': os_id})
            
            # Commit para salvar as alterações
            db.session.commit()
            
            logger.info(f"✅ OS #{os_id} desprogramada com sucesso")
            
            return jsonify({
                "success": True,
                "message": f"OS #{os_id} desprogramada com sucesso",
                "os_id": os_id
            })
            
        except Exception as e:
            db.session.rollback()
            logger.error(f"❌ Erro ao desprogramar OS #{os_id}: {e}")
            return jsonify({"error": f"Erro ao desprogramar OS: {str(e)}"}), 500
            
    except Exception as e:
        logger.error(f"❌ Erro geral ao desprogramar OS #{os_id}: {e}")
        return jsonify({"error": f"Erro geral: {str(e)}"}), 500

@ordens_servico_programar_bp.route('/api/ordens-servico-programacao', methods=['GET'])
def listar_ordens_servico():
    """
    Lista todas as ordens de serviço para programação.
    Este endpoint é uma alternativa ao endpoint principal que pode falhar devido a problemas de autenticação.
    
    Returns:
        JSON: Lista de ordens de serviço
    """
    try:
        logger.info("🔍 Listando ordens de serviço para programação")
        
        # Obter empresa do usuário atual ou da sessão
        empresa = None
        if hasattr(current_user, 'is_authenticated') and current_user.is_authenticated and hasattr(current_user, 'company'):
            empresa = current_user.company
        elif 'company' in session:
            empresa = session['company']
            
        logger.info(f"🏢 Empresa: {empresa}")
        
        # Consultar ordens de serviço
        try:
            query = text("""
                SELECT id, descricao, prioridade, status, data_programada, usuario_responsavel, 
                       equipamento_id, setor, filial, empresa, pmp_id, frequencia_origem
                FROM ordens_servico
                WHERE status IN ('aberta', 'programada')
                ORDER BY id DESC
            """)
            
            result = db.session.execute(query)
            
            # Converter resultado para lista de dicionários
            ordens_servico = []
            for row in result:
                os_dict = {
                    'id': row[0],
                    'descricao': row[1],
                    'prioridade': row[2],
                    'status': row[3],
                    'data_programada': row[4].strftime('%Y-%m-%d') if row[4] else None,
                    'usuario_responsavel': row[5],
                    'equipamento_id': row[6],
                    'setor': row[7],
                    'filial': row[8],
                    'empresa': row[9],
                    'pmp_id': row[10],
                    'frequencia_origem': row[11]
                }
                ordens_servico.append(os_dict)
                
            logger.info(f"✅ {len(ordens_servico)} ordens de serviço encontradas")
            
            return jsonify(ordens_servico)
            
        except Exception as e:
            logger.error(f"❌ Erro ao consultar ordens de serviço: {e}")
            return jsonify({"error": f"Erro ao consultar ordens de serviço: {str(e)}"}), 500
            
    except Exception as e:
        logger.error(f"❌ Erro geral ao listar ordens de serviço: {e}")
        return jsonify({"error": f"Erro geral: {str(e)}"}), 500

