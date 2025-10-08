"""
Endpoints para monitoramento do sistema automático de PMPs
"""

from flask import Blueprint, jsonify, current_app
from datetime import datetime
import logging

pmp_auto_status_bp = Blueprint('pmp_auto_status', __name__)

@pmp_auto_status_bp.route('/api/pmp/auto/status', methods=['GET'])
def status_sistema_automatico():
    """Retorna status do sistema automático de PMPs"""
    try:
        # Importar scheduler
        from pmp_scheduler_automatico import status_scheduler
        
        # Obter status do scheduler
        scheduler_status = status_scheduler()
        
        # Informações adicionais do sistema
        sistema_info = {
            'timestamp': datetime.now().isoformat(),
            'sistema_ativo': True,
            'modo_automatico': scheduler_status.get('running', False),
            'scheduler': scheduler_status
        }
        
        return jsonify({
            'success': True,
            'status': sistema_info
        })
        
    except Exception as e:
        current_app.logger.error(f"Erro ao obter status do sistema automático: {e}")
        return jsonify({
            'success': False,
            'error': str(e),
            'status': {
                'timestamp': datetime.now().isoformat(),
                'sistema_ativo': False,
                'modo_automatico': False,
                'scheduler': {'running': False, 'error': str(e)}
            }
        }), 500

@pmp_auto_status_bp.route('/api/pmp/auto/heartbeat', methods=['GET'])
def heartbeat_sistema():
    """Endpoint simples para verificar se o sistema está respondendo"""
    return jsonify({
        'success': True,
        'timestamp': datetime.now().isoformat(),
        'message': 'Sistema automático de PMPs ativo'
    })

@pmp_auto_status_bp.route('/api/pmp/auto/logs', methods=['GET'])
def logs_sistema():
    """Retorna logs recentes do sistema (se disponível)"""
    try:
        import os
        log_file = 'pmp_scheduler.log'
        
        if os.path.exists(log_file):
            # Ler últimas 50 linhas do log
            with open(log_file, 'r', encoding='utf-8') as f:
                lines = f.readlines()
                recent_lines = lines[-50:] if len(lines) > 50 else lines
            
            return jsonify({
                'success': True,
                'logs': [line.strip() for line in recent_lines],
                'total_lines': len(recent_lines)
            })
        else:
            return jsonify({
                'success': True,
                'logs': ['Log file not found'],
                'total_lines': 0
            })
            
    except Exception as e:
        current_app.logger.error(f"Erro ao obter logs: {e}")
        return jsonify({
            'success': False,
            'error': str(e),
            'logs': [],
            'total_lines': 0
        }), 500
