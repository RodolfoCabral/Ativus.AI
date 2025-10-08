"""
Endpoint de debug para verificar rotas registradas
"""

from flask import Blueprint, jsonify, current_app

debug_routes_bp = Blueprint('debug_routes', __name__)

@debug_routes_bp.route('/debug/routes', methods=['GET'])
def debug_routes():
    """Lista todas as rotas registradas no app"""
    try:
        routes = []
        for rule in current_app.url_map.iter_rules():
            routes.append({
                'endpoint': rule.endpoint,
                'methods': list(rule.methods),
                'rule': rule.rule
            })
        
        # Filtrar rotas PMP
        pmp_routes = [r for r in routes if '/api/pmp/' in r['rule']]
        
        return jsonify({
            'success': True,
            'total_routes': len(routes),
            'pmp_routes': len(pmp_routes),
            'pmp_routes_list': pmp_routes,
            'all_routes': routes
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@debug_routes_bp.route('/debug/blueprints', methods=['GET'])
def debug_blueprints():
    """Lista todas as blueprints registradas"""
    try:
        blueprints = []
        for name, blueprint in current_app.blueprints.items():
            blueprints.append({
                'name': name,
                'url_prefix': blueprint.url_prefix,
                'static_folder': blueprint.static_folder,
                'template_folder': blueprint.template_folder
            })
        
        return jsonify({
            'success': True,
            'total_blueprints': len(blueprints),
            'blueprints': blueprints
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@debug_routes_bp.route('/debug/pmp-status', methods=['GET'])
def debug_pmp_status():
    """Verifica status específico das rotas PMP"""
    try:
        # Verificar se blueprints PMP estão registradas
        pmp_blueprints = {}
        for name, blueprint in current_app.blueprints.items():
            if 'pmp' in name.lower():
                pmp_blueprints[name] = {
                    'registered': True,
                    'url_prefix': blueprint.url_prefix
                }
        
        # Verificar rotas específicas que estão falhando
        target_routes = [
            '/api/pmp/os/verificar-pendencias',
            '/api/pmp/os/gerar-todas',
            '/api/pmp/os/executar-automatico',
            '/api/pmp/auto/status'
        ]
        
        route_status = {}
        for target in target_routes:
            found = False
            for rule in current_app.url_map.iter_rules():
                if rule.rule == target:
                    route_status[target] = {
                        'found': True,
                        'methods': list(rule.methods),
                        'endpoint': rule.endpoint
                    }
                    found = True
                    break
            
            if not found:
                route_status[target] = {'found': False}
        
        return jsonify({
            'success': True,
            'pmp_blueprints': pmp_blueprints,
            'target_routes_status': route_status,
            'app_name': current_app.name,
            'debug_mode': current_app.debug
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500
