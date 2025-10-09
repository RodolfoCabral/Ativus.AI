"""
API de Debug para descobrir estrutura da tabela users
"""

from flask import Blueprint, jsonify, current_app
from flask_login import login_required

debug_users_api_bp = Blueprint('debug_users_api', __name__)

@debug_users_api_bp.route('/api/debug/users/estrutura', methods=['GET'])
@login_required
def api_debug_estrutura_users():
    """Descobre a estrutura da tabela users"""
    try:
        current_app.logger.info("🔍 Investigando estrutura da tabela users")
        
        from models import db
        
        # Método 1: Tentar DESCRIBE ou PRAGMA
        estrutura = []
        try:
            # Para PostgreSQL
            result = db.session.execute("""
                SELECT column_name, data_type, is_nullable 
                FROM information_schema.columns 
                WHERE table_name = 'users'
                ORDER BY ordinal_position
            """)
            
            for row in result:
                estrutura.append({
                    'coluna': row[0],
                    'tipo': row[1],
                    'nullable': row[2]
                })
                
        except Exception as e:
            current_app.logger.warning(f"Método PostgreSQL falhou: {e}")
            
            # Para SQLite
            try:
                result = db.session.execute("PRAGMA table_info(users)")
                for row in result:
                    estrutura.append({
                        'coluna': row[1],
                        'tipo': row[2],
                        'nullable': not row[3]
                    })
            except Exception as e2:
                current_app.logger.warning(f"Método SQLite falhou: {e2}")
        
        # Método 2: Buscar alguns registros para ver dados reais
        usuarios_exemplo = []
        try:
            result = db.session.execute("SELECT * FROM users LIMIT 3")
            columns = result.keys()
            
            for row in result:
                usuario = {}
                for i, col in enumerate(columns):
                    usuario[col] = row[i]
                usuarios_exemplo.append(usuario)
                
        except Exception as e:
            current_app.logger.warning(f"Erro ao buscar exemplos: {e}")
        
        # Método 3: Buscar especificamente o usuário 67
        usuario_67 = None
        try:
            result = db.session.execute("SELECT * FROM users WHERE id = 67")
            row = result.fetchone()
            
            if row:
                columns = result.keys()
                usuario_67 = {}
                for i, col in enumerate(columns):
                    usuario_67[col] = row[i]
                    
        except Exception as e:
            current_app.logger.warning(f"Erro ao buscar usuário 67: {e}")
        
        return jsonify({
            'success': True,
            'estrutura_tabela': estrutura,
            'usuarios_exemplo': usuarios_exemplo,
            'usuario_67': usuario_67,
            'total_colunas': len(estrutura) if estrutura else 0
        })
        
    except Exception as e:
        current_app.logger.error(f"❌ Erro no debug: {e}")
        return jsonify({
            'success': False,
            'error': f'Erro interno: {str(e)}'
        }), 500

@debug_users_api_bp.route('/api/debug/users/buscar-67', methods=['GET'])
@login_required
def api_debug_buscar_67():
    """Busca específica do usuário 67 com todos os métodos"""
    try:
        current_app.logger.info("🎯 Buscando usuário 67 com todos os métodos")
        
        resultado = {
            'user_id': 67,
            'metodos': {}
        }
        
        # Método 1: ORM
        try:
            from assets_models import User
            usuario = User.query.get(67)
            
            if usuario:
                dados_orm = {}
                for attr in dir(usuario):
                    if not attr.startswith('_') and not callable(getattr(usuario, attr)):
                        try:
                            valor = getattr(usuario, attr)
                            if valor is not None:
                                dados_orm[attr] = valor
                        except:
                            pass
                
                resultado['metodos']['orm'] = {
                    'sucesso': True,
                    'dados': dados_orm
                }
            else:
                resultado['metodos']['orm'] = {
                    'sucesso': False,
                    'erro': 'Usuário não encontrado'
                }
                
        except Exception as e:
            resultado['metodos']['orm'] = {
                'sucesso': False,
                'erro': str(e)
            }
        
        # Método 2: SQL direto
        try:
            from models import db
            result = db.session.execute("SELECT * FROM users WHERE id = 67")
            row = result.fetchone()
            
            if row:
                columns = result.keys()
                dados_sql = {}
                for i, col in enumerate(columns):
                    dados_sql[col] = row[i]
                
                resultado['metodos']['sql'] = {
                    'sucesso': True,
                    'dados': dados_sql
                }
            else:
                resultado['metodos']['sql'] = {
                    'sucesso': False,
                    'erro': 'Usuário não encontrado'
                }
                
        except Exception as e:
            resultado['metodos']['sql'] = {
                'sucesso': False,
                'erro': str(e)
            }
        
        # Método 3: Testar função helper
        try:
            from routes.usuario_helper import buscar_nome_usuario_por_id
            nome = buscar_nome_usuario_por_id(67)
            
            resultado['metodos']['helper'] = {
                'sucesso': True,
                'nome_encontrado': nome
            }
            
        except Exception as e:
            resultado['metodos']['helper'] = {
                'sucesso': False,
                'erro': str(e)
            }
        
        return jsonify({
            'success': True,
            'resultado': resultado
        })
        
    except Exception as e:
        current_app.logger.error(f"❌ Erro no debug 67: {e}")
        return jsonify({
            'success': False,
            'error': f'Erro interno: {str(e)}'
        }), 500

@debug_users_api_bp.route('/api/debug/users/testar-queries', methods=['GET'])
@login_required
def api_debug_testar_queries():
    """Testa diferentes queries SQL para encontrar usuários"""
    try:
        current_app.logger.info("🧪 Testando diferentes queries SQL")
        
        from models import db
        
        queries_teste = [
            "SELECT id, name FROM users WHERE id = 67",
            "SELECT id, username FROM users WHERE id = 67", 
            "SELECT id, nome FROM users WHERE id = 67",
            "SELECT id, login FROM users WHERE id = 67",
            "SELECT id, user_name FROM users WHERE id = 67",
            "SELECT id, first_name FROM users WHERE id = 67",
            "SELECT id, last_name FROM users WHERE id = 67",
            "SELECT id, email FROM users WHERE id = 67",
            "SELECT * FROM users WHERE id = 67"
        ]
        
        resultados = []
        
        for query in queries_teste:
            try:
                result = db.session.execute(query)
                row = result.fetchone()
                
                if row:
                    columns = result.keys()
                    dados = {}
                    for i, col in enumerate(columns):
                        dados[col] = row[i]
                    
                    resultados.append({
                        'query': query,
                        'sucesso': True,
                        'dados': dados
                    })
                else:
                    resultados.append({
                        'query': query,
                        'sucesso': False,
                        'erro': 'Nenhum resultado'
                    })
                    
            except Exception as e:
                resultados.append({
                    'query': query,
                    'sucesso': False,
                    'erro': str(e)
                })
        
        return jsonify({
            'success': True,
            'queries_testadas': len(queries_teste),
            'resultados': resultados
        })
        
    except Exception as e:
        current_app.logger.error(f"❌ Erro no teste de queries: {e}")
        return jsonify({
            'success': False,
            'error': f'Erro interno: {str(e)}'
        }), 500
