#!/usr/bin/env python3
"""
API para programação de OS via drag and drop
Atualiza usuário responsável e data programada
"""

from flask import Blueprint, request, jsonify, current_app
from datetime import datetime, date
from sqlalchemy import text
from models import db

# Importações dos modelos
try:
    from assets_models import OrdemServico
    OS_AVAILABLE = True
except ImportError as e:
    current_app.logger.error(f"Erro ao importar modelo OrdemServico: {e}")
    OS_AVAILABLE = False

programacao_api_bp = Blueprint('programacao_api', __name__)

@programacao_api_bp.route('/api/ordens-servico/<int:os_id>/programar', methods=['POST'])
def programar_os(os_id):
    """
    Programa uma OS para um usuário em uma data específica
    Usado pelo drag and drop da tela de programação
    """
    if not OS_AVAILABLE:
        return jsonify({'error': 'Funcionalidade de OS não disponível'}), 503
    
    try:
        current_app.logger.info(f"📅 Programando OS {os_id}")
        
        data = request.get_json()
        usuario_responsavel = data.get('usuario_responsavel')
        data_programada = data.get('data_programada')
        
        if not usuario_responsavel or not data_programada:
            return jsonify({'error': 'Usuário responsável e data são obrigatórios'}), 400
        
        # Buscar OS
        os = OrdemServico.query.get(os_id)
        if not os:
            return jsonify({'error': 'OS não encontrada'}), 404
        
        current_app.logger.info(f"📋 OS encontrada: {os.descricao}")
        
        # Converter data
        if isinstance(data_programada, str):
            try:
                data_programada = datetime.strptime(data_programada, '%Y-%m-%d').date()
            except ValueError:
                return jsonify({'error': 'Formato de data inválido. Use YYYY-MM-DD'}), 400
        
        # Atualizar OS
        os.usuario_responsavel = usuario_responsavel
        os.data_programada = data_programada
        os.status = 'programada'  # Mudar status para programada
        
        # Salvar no banco
        db.session.commit()
        
        current_app.logger.info(f"✅ OS {os_id} programada para {usuario_responsavel} em {data_programada}")
        
        return jsonify({
            'success': True,
            'message': f'OS #{os_id} programada com sucesso',
            'os': {
                'id': os.id,
                'usuario_responsavel': os.usuario_responsavel,
                'data_programada': os.data_programada.isoformat() if os.data_programada else None,
                'status': os.status
            }
        }), 200
        
    except Exception as e:
        current_app.logger.error(f"❌ Erro ao programar OS: {e}", exc_info=True)
        db.session.rollback()
        return jsonify({'error': f'Erro interno: {str(e)}'}), 500

@programacao_api_bp.route('/api/ordens-servico/<int:os_id>/desprogramar', methods=['POST'])
def desprogramar_os(os_id):
    """
    Remove programação de uma OS, voltando para chamados por prioridade
    """
    if not OS_AVAILABLE:
        return jsonify({'error': 'Funcionalidade de OS não disponível'}), 503
    
    try:
        current_app.logger.info(f"🔄 Desprogramando OS {os_id}")
        
        # Buscar OS
        os = OrdemServico.query.get(os_id)
        if not os:
            return jsonify({'error': 'OS não encontrada'}), 404
        
        # Remover programação
        os.usuario_responsavel = None
        os.data_programada = None
        os.status = 'aberta'  # Voltar para status aberta
        
        # Salvar no banco
        db.session.commit()
        
        current_app.logger.info(f"✅ OS {os_id} desprogramada")
        
        return jsonify({
            'success': True,
            'message': f'OS #{os_id} desprogramada com sucesso',
            'os': {
                'id': os.id,
                'usuario_responsavel': os.usuario_responsavel,
                'data_programada': os.data_programada,
                'status': os.status
            }
        }), 200
        
    except Exception as e:
        current_app.logger.error(f"❌ Erro ao desprogramar OS: {e}", exc_info=True)
        db.session.rollback()
        return jsonify({'error': f'Erro interno: {str(e)}'}), 500

@programacao_api_bp.route('/api/ordens-servico/<int:os_id>/mover-prioridade', methods=['POST'])
def mover_prioridade_os(os_id):
    """
    Move uma OS entre diferentes prioridades
    """
    if not OS_AVAILABLE:
        return jsonify({'error': 'Funcionalidade de OS não disponível'}), 503
    
    try:
        current_app.logger.info(f"🔄 Movendo prioridade da OS {os_id}")
        
        data = request.get_json()
        nova_prioridade = data.get('prioridade')
        
        if not nova_prioridade:
            return jsonify({'error': 'Nova prioridade é obrigatória'}), 400
        
        # Validar prioridade
        prioridades_validas = ['baixa', 'media', 'alta', 'seguranca', 'preventiva']
        if nova_prioridade not in prioridades_validas:
            return jsonify({'error': f'Prioridade inválida. Use: {", ".join(prioridades_validas)}'}), 400
        
        # Buscar OS
        os = OrdemServico.query.get(os_id)
        if not os:
            return jsonify({'error': 'OS não encontrada'}), 404
        
        prioridade_anterior = os.prioridade
        
        # Atualizar prioridade
        os.prioridade = nova_prioridade
        
        # Se mover para preventiva e não tem usuário, garantir que status seja 'aberta'
        if nova_prioridade == 'preventiva' and not os.usuario_responsavel:
            os.status = 'aberta'
        
        # Salvar no banco
        db.session.commit()
        
        current_app.logger.info(f"✅ OS {os_id} movida de {prioridade_anterior} para {nova_prioridade}")
        
        return jsonify({
            'success': True,
            'message': f'OS #{os_id} movida para prioridade {nova_prioridade}',
            'os': {
                'id': os.id,
                'prioridade_anterior': prioridade_anterior,
                'prioridade_nova': os.prioridade,
                'status': os.status
            }
        }), 200
        
    except Exception as e:
        current_app.logger.error(f"❌ Erro ao mover prioridade: {e}", exc_info=True)
        db.session.rollback()
        return jsonify({'error': f'Erro interno: {str(e)}'}), 500

@programacao_api_bp.route('/api/programacao/estatisticas', methods=['GET'])
def obter_estatisticas_programacao():
    """
    Obtém estatísticas da programação atual
    """
    if not OS_AVAILABLE:
        return jsonify({'error': 'Funcionalidade de OS não disponível'}), 503
    
    try:
        current_app.logger.info("📊 Obtendo estatísticas de programação")
        
        hoje = date.today()
        
        # Contar OS por status
        query_status = text("""
            SELECT 
                status,
                COUNT(*) as total
            FROM ordens_servico 
            WHERE status IN ('aberta', 'programada', 'em_execucao', 'concluida')
            GROUP BY status
        """)
        
        result_status = db.session.execute(query_status)
        stats_status = {row[0]: row[1] for row in result_status}
        
        # Contar OS por prioridade (apenas abertas)
        query_prioridade = text("""
            SELECT 
                prioridade,
                COUNT(*) as total
            FROM ordens_servico 
            WHERE status = 'aberta'
            GROUP BY prioridade
        """)
        
        result_prioridade = db.session.execute(query_prioridade)
        stats_prioridade = {row[0]: row[1] for row in result_prioridade}
        
        # Contar OS programadas por usuário
        query_usuarios = text("""
            SELECT 
                usuario_responsavel,
                COUNT(*) as total
            FROM ordens_servico 
            WHERE status = 'programada' 
            AND usuario_responsavel IS NOT NULL
            GROUP BY usuario_responsavel
            ORDER BY total DESC
        """)
        
        result_usuarios = db.session.execute(query_usuarios)
        stats_usuarios = [{'usuario': row[0], 'total_os': row[1]} for row in result_usuarios]
        
        # Contar OS de PMP
        query_pmp = text("""
            SELECT 
                COUNT(*) as total_pmp,
                COUNT(CASE WHEN status = 'aberta' THEN 1 END) as pmp_abertas,
                COUNT(CASE WHEN status = 'programada' THEN 1 END) as pmp_programadas
            FROM ordens_servico 
            WHERE pmp_id IS NOT NULL
        """)
        
        result_pmp = db.session.execute(query_pmp)
        pmp_row = result_pmp.fetchone()
        stats_pmp = {
            'total': pmp_row[0] if pmp_row else 0,
            'abertas': pmp_row[1] if pmp_row else 0,
            'programadas': pmp_row[2] if pmp_row else 0
        }
        
        return jsonify({
            'success': True,
            'data_calculo': hoje.isoformat(),
            'estatisticas': {
                'por_status': stats_status,
                'por_prioridade': stats_prioridade,
                'por_usuario': stats_usuarios,
                'pmp': stats_pmp
            },
            'resumo': {
                'total_os': sum(stats_status.values()),
                'abertas': stats_status.get('aberta', 0),
                'programadas': stats_status.get('programada', 0),
                'em_execucao': stats_status.get('em_execucao', 0),
                'concluidas': stats_status.get('concluida', 0)
            }
        }), 200
        
    except Exception as e:
        current_app.logger.error(f"❌ Erro ao obter estatísticas: {e}", exc_info=True)
        return jsonify({'error': f'Erro interno: {str(e)}'}), 500

