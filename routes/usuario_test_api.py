"""
API de Teste para Usuários - Debug e Validação
"""

from flask import Blueprint, request, jsonify, current_app
from flask_login import login_required
from routes.usuario_helper import (
    buscar_nome_usuario_por_id, 
    buscar_usuarios_por_ids, 
    validar_usuario_existe,
    listar_usuarios_ativos
)

usuario_test_api_bp = Blueprint('usuario_test_api', __name__)

@usuario_test_api_bp.route('/api/usuarios/listar', methods=['GET'])
@login_required
def api_listar_usuarios():
    """Lista todos os usuários do sistema"""
    try:
        current_app.logger.info("📋 Listando usuários do sistema")
        
        usuarios = listar_usuarios_ativos()
        
        return jsonify({
            'success': True,
            'usuarios': usuarios,
            'total': len(usuarios)
        })
        
    except Exception as e:
        current_app.logger.error(f"❌ Erro ao listar usuários: {e}")
        return jsonify({
            'success': False,
            'error': f'Erro interno: {str(e)}'
        }), 500

@usuario_test_api_bp.route('/api/usuarios/buscar/<user_id>', methods=['GET'])
@login_required
def api_buscar_usuario(user_id):
    """Busca um usuário específico pelo ID"""
    try:
        current_app.logger.info(f"🔍 Buscando usuário ID: {user_id}")
        
        nome = buscar_nome_usuario_por_id(user_id)
        existe = validar_usuario_existe(user_id)
        
        return jsonify({
            'success': True,
            'user_id': user_id,
            'nome': nome,
            'existe': existe
        })
        
    except Exception as e:
        current_app.logger.error(f"❌ Erro ao buscar usuário {user_id}: {e}")
        return jsonify({
            'success': False,
            'error': f'Erro interno: {str(e)}'
        }), 500

@usuario_test_api_bp.route('/api/usuarios/buscar-multiplos', methods=['POST'])
@login_required
def api_buscar_usuarios_multiplos():
    """Busca múltiplos usuários pelos IDs"""
    try:
        data = request.get_json() or {}
        user_ids = data.get('user_ids', [])
        
        current_app.logger.info(f"🔍 Buscando múltiplos usuários: {user_ids}")
        
        nomes = buscar_usuarios_por_ids(user_ids)
        
        resultado = []
        for i, user_id in enumerate(user_ids):
            nome = nomes[i] if i < len(nomes) else None
            resultado.append({
                'user_id': user_id,
                'nome': nome,
                'existe': validar_usuario_existe(user_id)
            })
        
        return jsonify({
            'success': True,
            'usuarios': resultado,
            'total': len(resultado)
        })
        
    except Exception as e:
        current_app.logger.error(f"❌ Erro ao buscar usuários: {e}")
        return jsonify({
            'success': False,
            'error': f'Erro interno: {str(e)}'
        }), 500

@usuario_test_api_bp.route('/api/usuarios/debug-pmps', methods=['GET'])
@login_required
def api_debug_usuarios_pmps():
    """Debug dos usuários responsáveis nas PMPs"""
    try:
        current_app.logger.info("🔍 Debug de usuários responsáveis nas PMPs")
        
        # Importar modelos
        from models.pmp_limpo import PMP
        import json
        
        pmps = PMP.query.filter(
            PMP.status == 'ativo',
            PMP.usuarios_responsaveis.isnot(None)
        ).all()
        
        resultado = []
        
        for pmp in pmps:
            try:
                usuarios_responsaveis = json.loads(pmp.usuarios_responsaveis)
                
                usuarios_info = []
                for user_id in usuarios_responsaveis:
                    nome = buscar_nome_usuario_por_id(user_id)
                    existe = validar_usuario_existe(user_id)
                    
                    usuarios_info.append({
                        'user_id': user_id,
                        'nome': nome,
                        'existe': existe
                    })
                
                resultado.append({
                    'pmp_id': pmp.id,
                    'pmp_codigo': pmp.codigo,
                    'usuarios_raw': pmp.usuarios_responsaveis,
                    'usuarios_parsed': usuarios_responsaveis,
                    'usuarios_info': usuarios_info
                })
                
            except Exception as e:
                resultado.append({
                    'pmp_id': pmp.id,
                    'pmp_codigo': pmp.codigo,
                    'usuarios_raw': pmp.usuarios_responsaveis,
                    'erro': str(e)
                })
        
        return jsonify({
            'success': True,
            'pmps_com_usuarios': resultado,
            'total': len(resultado)
        })
        
    except Exception as e:
        current_app.logger.error(f"❌ Erro no debug: {e}")
        return jsonify({
            'success': False,
            'error': f'Erro interno: {str(e)}'
        }), 500
