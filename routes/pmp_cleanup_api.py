"""
API para Limpeza e Manutenção de OS PMP
"""

from flask import Blueprint, request, jsonify, current_app
from flask_login import login_required, current_user
from datetime import datetime, date, timedelta
from models import db

# Importações dos modelos
try:
    from assets_models import OrdemServico
    from models.pmp_limpo import PMP
    from routes.verificador_duplicatas_os import contar_os_existentes_pmp, limpar_os_duplicadas_pmp
    MODELS_AVAILABLE = True
except ImportError as e:
    current_app.logger.error(f"Erro ao importar modelos: {e}")
    MODELS_AVAILABLE = False

pmp_cleanup_api_bp = Blueprint('pmp_cleanup_api', __name__)

@pmp_cleanup_api_bp.route('/api/pmp/os/contar-duplicatas', methods=['GET'])
@login_required
def api_contar_duplicatas():
    """Conta OS duplicadas por PMP"""
    try:
        current_app.logger.info("🔍 Contando OS duplicadas por PMP")
        
        if not MODELS_AVAILABLE:
            return jsonify({
                'success': False,
                'error': 'Modelos não disponíveis'
            }), 500
        
        # Buscar PMPs ativas
        pmps = PMP.query.filter(PMP.status == 'ativo').all()
        
        resultado = []
        total_duplicatas = 0
        
        for pmp in pmps:
            # Contar OS existentes
            count_os = contar_os_existentes_pmp(pmp.id, OrdemServico)
            
            # Buscar duplicatas por sequência
            todas_os = OrdemServico.query.filter_by(pmp_id=pmp.id).all()
            sequencias_vistas = set()
            duplicatas = 0
            
            for os in todas_os:
                if os.numero_sequencia in sequencias_vistas:
                    duplicatas += 1
                else:
                    sequencias_vistas.add(os.numero_sequencia)
            
            if count_os > 0 or duplicatas > 0:
                resultado.append({
                    'pmp_id': pmp.id,
                    'pmp_codigo': pmp.codigo,
                    'total_os': count_os,
                    'duplicatas': duplicatas,
                    'sequencias_unicas': len(sequencias_vistas)
                })
                total_duplicatas += duplicatas
        
        return jsonify({
            'success': True,
            'pmps': resultado,
            'total_duplicatas': total_duplicatas,
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        current_app.logger.error(f"❌ Erro ao contar duplicatas: {e}")
        return jsonify({
            'success': False,
            'error': f'Erro interno: {str(e)}'
        }), 500

@pmp_cleanup_api_bp.route('/api/pmp/os/limpar-duplicatas', methods=['POST'])
@login_required
def api_limpar_duplicatas():
    """Remove OS duplicadas (usar com cuidado)"""
    try:
        current_app.logger.info("🧹 Iniciando limpeza de OS duplicadas")
        
        if not MODELS_AVAILABLE:
            return jsonify({
                'success': False,
                'error': 'Modelos não disponíveis'
            }), 500
        
        data = request.get_json() or {}
        pmp_id = data.get('pmp_id')
        confirmar = data.get('confirmar', False)
        
        if not confirmar:
            return jsonify({
                'success': False,
                'error': 'Confirmação necessária para limpeza'
            }), 400
        
        if pmp_id:
            # Limpar duplicatas de uma PMP específica
            removidas = limpar_os_duplicadas_pmp(pmp_id, OrdemServico, db)
            
            return jsonify({
                'success': True,
                'message': f'{removidas} OS duplicadas removidas da PMP {pmp_id}',
                'os_removidas': removidas,
                'timestamp': datetime.now().isoformat()
            })
        else:
            # Limpar duplicatas de todas as PMPs
            pmps = PMP.query.filter(PMP.status == 'ativo').all()
            total_removidas = 0
            
            for pmp in pmps:
                removidas = limpar_os_duplicadas_pmp(pmp.id, OrdemServico, db)
                total_removidas += removidas
            
            return jsonify({
                'success': True,
                'message': f'{total_removidas} OS duplicadas removidas de {len(pmps)} PMPs',
                'os_removidas': total_removidas,
                'pmps_processadas': len(pmps),
                'timestamp': datetime.now().isoformat()
            })
        
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"❌ Erro na limpeza: {e}")
        return jsonify({
            'success': False,
            'error': f'Erro interno: {str(e)}'
        }), 500

@pmp_cleanup_api_bp.route('/api/pmp/os/status-sistema', methods=['GET'])
def api_status_sistema():
    """Status geral do sistema PMP"""
    try:
        if not MODELS_AVAILABLE:
            return jsonify({
                'success': False,
                'error': 'Modelos não disponíveis'
            }), 500
        
        # Estatísticas gerais
        total_pmps = PMP.query.filter(PMP.status == 'ativo').count()
        total_os = OrdemServico.query.filter(OrdemServico.pmp_id.isnot(None)).count()
        os_abertas = OrdemServico.query.filter(
            OrdemServico.pmp_id.isnot(None),
            OrdemServico.status == 'aberta'
        ).count()
        os_programadas = OrdemServico.query.filter(
            OrdemServico.pmp_id.isnot(None),
            OrdemServico.status == 'programada'
        ).count()
        
        return jsonify({
            'success': True,
            'estatisticas': {
                'total_pmps_ativas': total_pmps,
                'total_os_pmp': total_os,
                'os_abertas': os_abertas,
                'os_programadas': os_programadas,
                'sistema_funcionando': True
            },
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        current_app.logger.error(f"❌ Erro no status: {e}")
        return jsonify({
            'success': False,
            'error': f'Erro interno: {str(e)}'
        }), 500
