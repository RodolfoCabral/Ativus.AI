"""
API de Debug para Atividades de PMP
"""

from flask import Blueprint, jsonify, current_app
from flask_login import login_required

debug_atividades_api_bp = Blueprint('debug_atividades_api', __name__)

@debug_atividades_api_bp.route('/api/debug/pmp/atividades', methods=['GET'])
@login_required
def api_debug_atividades_pmp():
    """Debug das atividades das PMPs"""
    try:
        current_app.logger.info("🔍 Debug de atividades das PMPs")
        
        # Importar modelos
        from models.pmp_limpo import PMP, AtividadePMP
        
        pmps = PMP.query.filter(PMP.status == 'ativo').all()
        
        resultado = []
        
        for pmp in pmps:
            try:
                # Buscar atividades da PMP
                atividades = AtividadePMP.query.filter_by(pmp_id=pmp.id).order_by(AtividadePMP.ordem).all()
                
                atividades_info = []
                for atividade in atividades:
                    atividades_info.append({
                        'id': atividade.id,
                        'descricao': atividade.descricao,
                        'ordem': atividade.ordem,
                        'oficina': atividade.oficina,
                        'tipo_manutencao': atividade.tipo_manutencao
                    })
                
                resultado.append({
                    'pmp_id': pmp.id,
                    'pmp_codigo': pmp.codigo,
                    'pmp_descricao': pmp.descricao,
                    'total_atividades': len(atividades),
                    'atividades': atividades_info
                })
                
            except Exception as e:
                resultado.append({
                    'pmp_id': pmp.id,
                    'pmp_codigo': pmp.codigo,
                    'erro': str(e)
                })
        
        return jsonify({
            'success': True,
            'pmps': resultado,
            'total_pmps': len(resultado)
        })
        
    except Exception as e:
        current_app.logger.error(f"❌ Erro no debug de atividades: {e}")
        return jsonify({
            'success': False,
            'error': f'Erro interno: {str(e)}'
        }), 500

@debug_atividades_api_bp.route('/api/debug/os/atividades/<int:os_id>', methods=['GET'])
@login_required
def api_debug_atividades_os(os_id):
    """Debug das atividades de uma OS específica"""
    try:
        current_app.logger.info(f"🔍 Debug de atividades da OS {os_id}")
        
        # Importar modelos
        from assets_models import OrdemServico
        from models.atividade_os import AtividadeOS
        
        # Buscar a OS
        os = OrdemServico.query.get(os_id)
        
        if not os:
            return jsonify({
                'success': False,
                'error': f'OS {os_id} não encontrada'
            }), 404
        
        # Buscar atividades da OS
        atividades = AtividadeOS.query.filter_by(os_id=os_id).order_by(AtividadeOS.ordem).all()
        
        atividades_info = []
        for atividade in atividades:
            atividades_info.append({
                'id': atividade.id,
                'descricao': atividade.descricao,
                'ordem': atividade.ordem,
                'status': atividade.status.value if hasattr(atividade.status, 'value') else str(atividade.status),
                'atividade_pmp_id': atividade.atividade_pmp_id
            })
        
        return jsonify({
            'success': True,
            'os_id': os_id,
            'os_descricao': os.descricao,
            'pmp_id': os.pmp_id,
            'total_atividades': len(atividades),
            'atividades': atividades_info
        })
        
    except Exception as e:
        current_app.logger.error(f"❌ Erro no debug de atividades da OS: {e}")
        return jsonify({
            'success': False,
            'error': f'Erro interno: {str(e)}'
        }), 500

@debug_atividades_api_bp.route('/api/debug/pmp/<int:pmp_id>/atividades', methods=['GET'])
@login_required
def api_debug_atividades_pmp_especifica(pmp_id):
    """Debug das atividades de uma PMP específica"""
    try:
        current_app.logger.info(f"🔍 Debug de atividades da PMP {pmp_id}")
        
        # Importar modelos
        from models.pmp_limpo import PMP, AtividadePMP
        
        # Buscar a PMP
        pmp = PMP.query.get(pmp_id)
        
        if not pmp:
            return jsonify({
                'success': False,
                'error': f'PMP {pmp_id} não encontrada'
            }), 404
        
        # Buscar atividades da PMP
        atividades = AtividadePMP.query.filter_by(pmp_id=pmp_id).order_by(AtividadePMP.ordem).all()
        
        atividades_info = []
        for atividade in atividades:
            atividades_info.append({
                'id': atividade.id,
                'descricao': atividade.descricao,
                'ordem': atividade.ordem,
                'oficina': atividade.oficina,
                'tipo_manutencao': atividade.tipo_manutencao,
                'conjunto': atividade.conjunto,
                'ponto_controle': atividade.ponto_controle
            })
        
        return jsonify({
            'success': True,
            'pmp_id': pmp_id,
            'pmp_codigo': pmp.codigo,
            'pmp_descricao': pmp.descricao,
            'total_atividades': len(atividades),
            'atividades': atividades_info
        })
        
    except Exception as e:
        current_app.logger.error(f"❌ Erro no debug de atividades da PMP: {e}")
        return jsonify({
            'success': False,
            'error': f'Erro interno: {str(e)}'
        }), 500

@debug_atividades_api_bp.route('/api/debug/transferir-atividades/<int:pmp_id>/<int:os_id>', methods=['POST'])
@login_required
def api_debug_transferir_atividades(pmp_id, os_id):
    """Força transferência de atividades de uma PMP para uma OS (para debug)"""
    try:
        current_app.logger.info(f"🔧 Forçando transferência de atividades PMP {pmp_id} → OS {os_id}")
        
        # Importar modelos
        from models.pmp_limpo import PMP, AtividadePMP
        from models.atividade_os import AtividadeOS, StatusConformidade
        from assets_models import OrdemServico
        from models import db
        
        # Verificar se PMP e OS existem
        pmp = PMP.query.get(pmp_id)
        os = OrdemServico.query.get(os_id)
        
        if not pmp:
            return jsonify({'success': False, 'error': f'PMP {pmp_id} não encontrada'}), 404
        
        if not os:
            return jsonify({'success': False, 'error': f'OS {os_id} não encontrada'}), 404
        
        # Buscar atividades da PMP
        atividades_pmp = AtividadePMP.query.filter_by(pmp_id=pmp_id).order_by(AtividadePMP.ordem).all()
        
        if not atividades_pmp:
            return jsonify({
                'success': False,
                'error': f'PMP {pmp_id} não possui atividades'
            }), 400
        
        # Remover atividades existentes da OS (se houver)
        AtividadeOS.query.filter_by(os_id=os_id).delete()
        
        # Transferir atividades
        atividades_criadas = 0
        for atividade_pmp in atividades_pmp:
            nova_atividade_os = AtividadeOS(
                os_id=os_id,
                atividade_pmp_id=atividade_pmp.id,
                descricao=atividade_pmp.descricao,
                ordem=atividade_pmp.ordem,
                status=StatusConformidade.PENDENTE
            )
            db.session.add(nova_atividade_os)
            atividades_criadas += 1
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': f'{atividades_criadas} atividades transferidas com sucesso',
            'pmp_id': pmp_id,
            'os_id': os_id,
            'atividades_transferidas': atividades_criadas
        })
        
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"❌ Erro na transferência forçada: {e}")
        return jsonify({
            'success': False,
            'error': f'Erro interno: {str(e)}'
        }), 500
