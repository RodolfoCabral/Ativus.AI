"""
API de atividades com fallback para buscar diretamente na atividades_pmp
"""

from flask import Blueprint, jsonify, request, current_app
from flask_login import login_required, current_user
from models import db
from models.atividade_os import AtividadeOS
from assets_models import OrdemServico
import logging

logger = logging.getLogger(__name__)

atividades_os_fallback_bp = Blueprint('atividades_os_fallback', __name__)

@atividades_os_fallback_bp.route('/api/os/<int:os_id>/atividades-fallback', methods=['GET'])
@login_required
def listar_atividades_os_com_fallback(os_id):
    """Lista atividades de uma OS com fallback para atividades_pmp"""
    try:
        current_app.logger.info(f"🔍 Buscando atividades para OS {os_id} (com fallback)")
        
        # Buscar a OS primeiro
        os = OrdemServico.query.filter_by(id=os_id).first()
        
        if not os:
            current_app.logger.error(f"❌ OS {os_id} não encontrada")
            return jsonify({'error': 'OS não encontrada'}), 404
        
        current_app.logger.info(f"✅ OS {os_id} encontrada: {os.descricao}")
        
        # MÉTODO 1: Buscar em atividades_os (método normal)
        atividades_os = AtividadeOS.query.filter_by(os_id=os_id).order_by(AtividadeOS.ordem).all()
        current_app.logger.info(f"📋 Método 1 - atividades_os: {len(atividades_os)} atividades")
        
        if atividades_os:
            # Encontrou atividades na tabela atividades_os
            atividades_dict = []
            for atividade in atividades_os:
                try:
                    atividade_dict = atividade.to_dict()
                    atividades_dict.append(atividade_dict)
                except Exception as e:
                    current_app.logger.error(f"❌ Erro ao converter atividade {atividade.id}: {e}")
                    # Fallback manual
                    atividades_dict.append({
                        'id': atividade.id,
                        'descricao': atividade.descricao,
                        'ordem': atividade.ordem,
                        'status': atividade.status,
                        'observacao': getattr(atividade, 'observacao', ''),
                        'instrucao': getattr(atividade, 'instrucao', '')
                    })
            
            current_app.logger.info(f"✅ Retornando {len(atividades_dict)} atividades da tabela atividades_os")
            return jsonify({
                'os_id': os_id,
                'os_descricao': os.descricao,
                'os_tipo': getattr(os, 'tipo_manutencao', 'N/A'),
                'os_status': getattr(os, 'status', 'N/A'),
                'atividades': atividades_dict,
                'fonte': 'atividades_os',
                'total': len(atividades_dict)
            })
        
        # MÉTODO 2: Fallback - Buscar diretamente na atividades_pmp
        current_app.logger.info(f"🔄 Método 2 - Fallback: buscando na atividades_pmp")
        
        if not os.pmp_id:
            current_app.logger.warning(f"⚠️ OS {os_id} não tem PMP associada")
            return jsonify({
                'os_id': os_id,
                'os_descricao': os.descricao,
                'os_tipo': getattr(os, 'tipo_manutencao', 'N/A'),
                'os_status': getattr(os, 'status', 'N/A'),
                'atividades': [],
                'message': 'OS não tem PMP associada',
                'fonte': 'nenhuma'
            })
        
        # Buscar atividades da PMP diretamente
        try:
            from models.pmp_limpo import AtividadePMP
            atividades_pmp = AtividadePMP.query.filter_by(pmp_id=os.pmp_id).order_by(AtividadePMP.ordem).all()
            current_app.logger.info(f"📋 Método 2 - atividades_pmp: {len(atividades_pmp)} atividades")
            
            if atividades_pmp:
                # Converter atividades da PMP para formato da OS
                atividades_dict = []
                for i, atividade_pmp in enumerate(atividades_pmp):
                    atividade_dict = {
                        'id': f"pmp_{atividade_pmp.id}",  # ID temporário
                        'descricao': atividade_pmp.descricao,
                        'ordem': atividade_pmp.ordem or (i + 1),
                        'status': 'pendente',
                        'observacao': '',
                        'instrucao': getattr(atividade_pmp, 'instrucao', ''),
                        'oficina': getattr(atividade_pmp, 'oficina', ''),
                        'fonte_original': 'atividades_pmp'
                    }
                    atividades_dict.append(atividade_dict)
                
                current_app.logger.info(f"✅ Retornando {len(atividades_dict)} atividades da PMP (fallback)")
                return jsonify({
                    'os_id': os_id,
                    'os_descricao': os.descricao,
                    'os_tipo': getattr(os, 'tipo_manutencao', 'N/A'),
                    'os_status': getattr(os, 'status', 'N/A'),
                    'atividades': atividades_dict,
                    'fonte': 'atividades_pmp_fallback',
                    'total': len(atividades_dict),
                    'pmp_id': os.pmp_id,
                    'message': 'Atividades carregadas diretamente da PMP (fallback)'
                })
            
        except Exception as e:
            current_app.logger.error(f"❌ Erro ao buscar atividades da PMP: {e}")
        
        # MÉTODO 3: Último recurso - busca via SQL direto
        current_app.logger.info(f"🔄 Método 3 - SQL direto na atividades_pmp")
        
        try:
            sql_query = """
                SELECT id, descricao, ordem, oficina 
                FROM atividades_pmp 
                WHERE pmp_id = :pmp_id 
                ORDER BY ordem
            """
            result = db.engine.execute(sql_query, pmp_id=os.pmp_id)
            atividades_sql = list(result)
            
            current_app.logger.info(f"📋 Método 3 - SQL direto: {len(atividades_sql)} atividades")
            
            if atividades_sql:
                atividades_dict = []
                for i, atividade in enumerate(atividades_sql):
                    atividade_dict = {
                        'id': f"sql_{atividade[0]}",
                        'descricao': atividade[1],
                        'ordem': atividade[2] or (i + 1),
                        'status': 'pendente',
                        'observacao': '',
                        'instrucao': '',
                        'oficina': atividade[3] if len(atividade) > 3 else '',
                        'fonte_original': 'sql_direto'
                    }
                    atividades_dict.append(atividade_dict)
                
                current_app.logger.info(f"✅ Retornando {len(atividades_dict)} atividades via SQL direto")
                return jsonify({
                    'os_id': os_id,
                    'os_descricao': os.descricao,
                    'os_tipo': getattr(os, 'tipo_manutencao', 'N/A'),
                    'os_status': getattr(os, 'status', 'N/A'),
                    'atividades': atividades_dict,
                    'fonte': 'sql_direto',
                    'total': len(atividades_dict),
                    'pmp_id': os.pmp_id,
                    'message': 'Atividades carregadas via SQL direto da PMP'
                })
        
        except Exception as e:
            current_app.logger.error(f"❌ Erro no SQL direto: {e}")
        
        # Nenhum método funcionou
        current_app.logger.warning(f"⚠️ Nenhum método encontrou atividades para OS {os_id}")
        return jsonify({
            'os_id': os_id,
            'os_descricao': os.descricao,
            'os_tipo': getattr(os, 'tipo_manutencao', 'N/A'),
            'os_status': getattr(os, 'status', 'N/A'),
            'atividades': [],
            'message': 'Nenhuma atividade encontrada em nenhuma fonte',
            'fonte': 'nenhuma',
            'pmp_id': os.pmp_id,
            'debug': {
                'atividades_os_count': len(atividades_os),
                'pmp_id': os.pmp_id,
                'metodos_testados': ['atividades_os', 'atividades_pmp', 'sql_direto']
            }
        })
        
    except Exception as e:
        current_app.logger.error(f"❌ Erro geral na API: {e}")
        return jsonify({
            'error': f'Erro interno: {str(e)}',
            'os_id': os_id
        }), 500

@atividades_os_fallback_bp.route('/api/debug/os/<int:os_id>/fontes-atividades', methods=['GET'])
@login_required
def debug_fontes_atividades(os_id):
    """Debug para mostrar todas as fontes possíveis de atividades"""
    try:
        current_app.logger.info(f"🔍 Debug de fontes de atividades para OS {os_id}")
        
        # Buscar OS
        os = OrdemServico.query.filter_by(id=os_id).first()
        if not os:
            return jsonify({'error': 'OS não encontrada'}), 404
        
        resultado = {
            'os_id': os_id,
            'os_descricao': os.descricao,
            'pmp_id': os.pmp_id,
            'fontes': {}
        }
        
        # Fonte 1: atividades_os
        try:
            atividades_os = AtividadeOS.query.filter_by(os_id=os_id).all()
            resultado['fontes']['atividades_os'] = {
                'count': len(atividades_os),
                'atividades': [{'id': a.id, 'descricao': a.descricao} for a in atividades_os[:3]]
            }
        except Exception as e:
            resultado['fontes']['atividades_os'] = {'erro': str(e)}
        
        # Fonte 2: atividades_pmp (se tem PMP)
        if os.pmp_id:
            try:
                from models.pmp_limpo import AtividadePMP
                atividades_pmp = AtividadePMP.query.filter_by(pmp_id=os.pmp_id).all()
                resultado['fontes']['atividades_pmp'] = {
                    'count': len(atividades_pmp),
                    'atividades': [{'id': a.id, 'descricao': a.descricao} for a in atividades_pmp[:3]]
                }
            except Exception as e:
                resultado['fontes']['atividades_pmp'] = {'erro': str(e)}
        
        # Fonte 3: SQL direto
        try:
            sql_result = db.engine.execute(f"SELECT COUNT(*) FROM atividades_pmp WHERE pmp_id = {os.pmp_id}")
            count_sql = sql_result.fetchone()[0]
            resultado['fontes']['sql_direto'] = {'count': count_sql}
        except Exception as e:
            resultado['fontes']['sql_direto'] = {'erro': str(e)}
        
        return jsonify(resultado)
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500
