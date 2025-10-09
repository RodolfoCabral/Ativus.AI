"""
API de Debug para verificar OS e suas atividades
"""

from flask import Blueprint, jsonify, current_app
from flask_login import login_required

debug_os_atividades_bp = Blueprint('debug_os_atividades', __name__)

@debug_os_atividades_bp.route('/api/debug/os-sem-atividades', methods=['GET'])
@login_required
def api_debug_os_sem_atividades():
    """Debug de OS que não têm atividades"""
    try:
        current_app.logger.info("🔍 Debug de OS sem atividades")
        
        # Importar modelos
        from assets_models import OrdemServico
        from models.atividade_os import AtividadeOS
        
        # Buscar OS de PMP
        os_pmp = OrdemServico.query.filter(OrdemServico.pmp_id.isnot(None)).limit(20).all()
        
        resultado = []
        
        for os in os_pmp:
            try:
                # Contar atividades da OS
                atividades_count = AtividadeOS.query.filter_by(os_id=os.id).count()
                
                resultado.append({
                    'os_id': os.id,
                    'os_descricao': os.descricao,
                    'pmp_id': os.pmp_id,
                    'pmp_codigo': getattr(os, 'pmp_codigo', 'N/A'),
                    'status': os.status,
                    'tipo_manutencao': getattr(os, 'tipo_manutencao', 'N/A'),
                    'total_atividades': atividades_count,
                    'tem_atividades': atividades_count > 0
                })
                
            except Exception as e:
                resultado.append({
                    'os_id': os.id,
                    'erro': str(e)
                })
        
        # Separar OS com e sem atividades
        com_atividades = [os for os in resultado if os.get('tem_atividades', False)]
        sem_atividades = [os for os in resultado if not os.get('tem_atividades', True)]
        
        return jsonify({
            'success': True,
            'total_os_pmp': len(resultado),
            'com_atividades': len(com_atividades),
            'sem_atividades': len(sem_atividades),
            'os_sem_atividades': sem_atividades,
            'os_com_atividades': com_atividades[:5]  # Apenas primeiras 5
        })
        
    except Exception as e:
        current_app.logger.error(f"❌ Erro no debug de OS: {e}")
        return jsonify({
            'success': False,
            'error': f'Erro interno: {str(e)}'
        }), 500

@debug_os_atividades_bp.route('/api/debug/os/<int:os_id>/detalhes', methods=['GET'])
@login_required
def api_debug_os_detalhes(os_id):
    """Debug detalhado de uma OS específica"""
    try:
        current_app.logger.info(f"🔍 Debug detalhado da OS {os_id}")
        
        # Importar modelos
        from assets_models import OrdemServico
        from models.atividade_os import AtividadeOS
        from models.pmp_limpo import PMP, AtividadePMP
        
        # Buscar a OS
        os = OrdemServico.query.get(os_id)
        
        if not os:
            return jsonify({
                'success': False,
                'error': f'OS {os_id} não encontrada'
            }), 404
        
        # Buscar atividades da OS
        atividades_os = AtividadeOS.query.filter_by(os_id=os_id).order_by(AtividadeOS.ordem).all()
        
        # Buscar PMP se existir
        pmp_info = None
        atividades_pmp = []
        
        if os.pmp_id:
            pmp = PMP.query.get(os.pmp_id)
            if pmp:
                pmp_info = {
                    'id': pmp.id,
                    'codigo': pmp.codigo,
                    'descricao': pmp.descricao,
                    'status': pmp.status
                }
                
                # Buscar atividades da PMP
                atividades_pmp = AtividadePMP.query.filter_by(pmp_id=pmp.id).order_by(AtividadePMP.ordem).all()
        
        # Preparar dados das atividades da OS
        atividades_os_info = []
        for atividade in atividades_os:
            atividades_os_info.append({
                'id': atividade.id,
                'descricao': atividade.descricao,
                'ordem': atividade.ordem,
                'status': str(atividade.status),
                'atividade_pmp_id': getattr(atividade, 'atividade_pmp_id', None)
            })
        
        # Preparar dados das atividades da PMP
        atividades_pmp_info = []
        for atividade in atividades_pmp:
            atividades_pmp_info.append({
                'id': atividade.id,
                'descricao': atividade.descricao,
                'ordem': atividade.ordem,
                'oficina': atividade.oficina
            })
        
        return jsonify({
            'success': True,
            'os': {
                'id': os.id,
                'descricao': os.descricao,
                'status': os.status,
                'tipo_manutencao': getattr(os, 'tipo_manutencao', 'N/A'),
                'pmp_id': os.pmp_id,
                'pmp_codigo': getattr(os, 'pmp_codigo', 'N/A')
            },
            'pmp': pmp_info,
            'atividades_os': {
                'total': len(atividades_os),
                'lista': atividades_os_info
            },
            'atividades_pmp': {
                'total': len(atividades_pmp),
                'lista': atividades_pmp_info
            },
            'diagnostico': {
                'os_tem_atividades': len(atividades_os) > 0,
                'pmp_tem_atividades': len(atividades_pmp) > 0,
                'atividades_transferidas': len(atividades_os) == len(atividades_pmp) if atividades_pmp else False
            }
        })
        
    except Exception as e:
        current_app.logger.error(f"❌ Erro no debug da OS: {e}")
        return jsonify({
            'success': False,
            'error': f'Erro interno: {str(e)}'
        }), 500

@debug_os_atividades_bp.route('/api/debug/transferir-atividades-faltantes', methods=['POST'])
@login_required
def api_debug_transferir_atividades_faltantes():
    """Transfere atividades para OS que não têm atividades mas deveriam ter"""
    try:
        current_app.logger.info("🔧 Transferindo atividades faltantes")
        
        # Importar modelos
        from assets_models import OrdemServico
        from models.atividade_os import AtividadeOS, StatusConformidade
        from models.pmp_limpo import PMP, AtividadePMP
        from models import db
        
        # Buscar OS de PMP sem atividades
        os_pmp = OrdemServico.query.filter(OrdemServico.pmp_id.isnot(None)).all()
        
        transferencias = []
        erros = []
        
        for os in os_pmp:
            try:
                # Verificar se já tem atividades
                atividades_existentes = AtividadeOS.query.filter_by(os_id=os.id).count()
                
                if atividades_existentes > 0:
                    continue  # Já tem atividades
                
                # Buscar atividades da PMP
                atividades_pmp = AtividadePMP.query.filter_by(pmp_id=os.pmp_id).all()
                
                if not atividades_pmp:
                    continue  # PMP não tem atividades
                
                # Transferir atividades
                atividades_criadas = 0
                for atividade_pmp in atividades_pmp:
                    nova_atividade_os = AtividadeOS(
                        os_id=os.id,
                        atividade_pmp_id=atividade_pmp.id,
                        descricao=atividade_pmp.descricao,
                        ordem=atividade_pmp.ordem,
                        status=StatusConformidade.PENDENTE
                    )
                    db.session.add(nova_atividade_os)
                    atividades_criadas += 1
                
                db.session.commit()
                
                transferencias.append({
                    'os_id': os.id,
                    'pmp_id': os.pmp_id,
                    'atividades_transferidas': atividades_criadas
                })
                
                current_app.logger.info(f"✅ OS {os.id}: {atividades_criadas} atividades transferidas")
                
            except Exception as e:
                db.session.rollback()
                erros.append({
                    'os_id': os.id,
                    'erro': str(e)
                })
                current_app.logger.error(f"❌ Erro na OS {os.id}: {e}")
        
        return jsonify({
            'success': True,
            'transferencias_realizadas': len(transferencias),
            'erros': len(erros),
            'detalhes': {
                'transferencias': transferencias,
                'erros': erros
            }
        })
        
    except Exception as e:
        current_app.logger.error(f"❌ Erro na transferência em lote: {e}")
        return jsonify({
            'success': False,
            'error': f'Erro interno: {str(e)}'
        }), 500
