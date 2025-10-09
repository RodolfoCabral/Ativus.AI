"""
API para monitorar status da transferência automática de atividades
"""

from flask import Blueprint, jsonify, current_app
from flask_login import login_required, current_user

auto_transfer_status_bp = Blueprint('auto_transfer_status', __name__)

@auto_transfer_status_bp.route('/api/auto-transfer/status', methods=['GET'])
@login_required
def get_auto_transfer_status():
    """Retorna status da transferência automática"""
    try:
        from auto_transferir_atividades import verificar_status
        status = verificar_status()
        
        return jsonify({
            'success': True,
            'status': status,
            'message': 'Status da transferência automática'
        })
        
    except Exception as e:
        current_app.logger.error(f"❌ Erro ao obter status: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@auto_transfer_status_bp.route('/api/auto-transfer/force', methods=['POST'])
@login_required
def force_auto_transfer():
    """Força execução da transferência automática"""
    try:
        # Só admins podem forçar
        if current_user.profile not in ['master', 'admin']:
            return jsonify({
                'success': False,
                'message': 'Permissão negada'
            }), 403
        
        from auto_transferir_atividades import auto_transferir
        
        # Resetar controle para permitir execução
        auto_transferir.ultima_execucao = None
        auto_transferir.executar_em_background()
        
        return jsonify({
            'success': True,
            'message': 'Transferência forçada iniciada em background'
        })
        
    except Exception as e:
        current_app.logger.error(f"❌ Erro ao forçar transferência: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@auto_transfer_status_bp.route('/api/auto-transfer/stats', methods=['GET'])
@login_required
def get_transfer_stats():
    """Retorna estatísticas das atividades"""
    try:
        from models import db
        
        # Contar OS sem atividades
        result = db.engine.execute('''
            SELECT COUNT(*) 
            FROM ordens_servico os 
            WHERE os.pmp_id IS NOT NULL 
            AND os.id NOT IN (SELECT DISTINCT os_id FROM atividades_os WHERE os_id IS NOT NULL)
        ''')
        os_sem_atividades = result.fetchone()[0]
        
        # Contar total de atividades_os
        result = db.engine.execute('SELECT COUNT(*) FROM atividades_os')
        total_atividades_os = result.fetchone()[0]
        
        # Contar total de OS com PMP
        result = db.engine.execute('SELECT COUNT(*) FROM ordens_servico WHERE pmp_id IS NOT NULL')
        total_os_pmp = result.fetchone()[0]
        
        return jsonify({
            'success': True,
            'stats': {
                'os_sem_atividades': os_sem_atividades,
                'total_atividades_os': total_atividades_os,
                'total_os_pmp': total_os_pmp,
                'percentual_completo': round((total_os_pmp - os_sem_atividades) / max(total_os_pmp, 1) * 100, 2)
            }
        })
        
    except Exception as e:
        current_app.logger.error(f"❌ Erro ao obter estatísticas: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500
