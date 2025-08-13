#!/usr/bin/env python3
"""
Script para debugar problemas de inicialização da aplicação
Execute este script para identificar erros que impedem o Flask de iniciar
"""

import sys
import traceback

def debug_imports():
    """Testar todos os imports necessários"""
    print("🔍 Testando imports...")
    
    imports_to_test = [
        ('flask', 'Flask'),
        ('flask', 'Blueprint'),
        ('flask', 'request'),
        ('flask', 'jsonify'),
        ('flask', 'session'),
        ('flask_sqlalchemy', 'SQLAlchemy'),
        ('models', None),
        ('routes.plano_mestre', 'plano_mestre_bp'),
        ('routes.plano_mestre_debug', 'plano_mestre_debug_bp'),
        ('models.plano_mestre', 'PlanoMestre'),
    ]
    
    failed_imports = []
    
    for module, item in imports_to_test:
        try:
            if item:
                exec(f"from {module} import {item}")
                print(f"  ✅ {module}.{item}")
            else:
                exec(f"import {module}")
                print(f"  ✅ {module}")
        except ImportError as e:
            print(f"  ❌ {module}.{item if item else ''}: {e}")
            failed_imports.append((module, item, str(e)))
        except Exception as e:
            print(f"  ⚠️ {module}.{item if item else ''}: {e}")
            failed_imports.append((module, item, str(e)))
    
    return failed_imports

def debug_app_creation():
    """Testar criação da aplicação Flask"""
    print("\n🔍 Testando criação da aplicação...")
    
    try:
        from app import create_app
        print("  ✅ Função create_app importada")
        
        app = create_app()
        print("  ✅ Aplicação Flask criada")
        
        print(f"  📍 Blueprints registrados: {len(app.blueprints)}")
        for name, bp in app.blueprints.items():
            print(f"    - {name}: {bp.url_prefix or '/'}")
        
        return True, app
        
    except Exception as e:
        print(f"  ❌ Erro ao criar aplicação: {e}")
        traceback.print_exc()
        return False, None

def debug_database():
    """Testar conexão com banco de dados"""
    print("\n🔍 Testando banco de dados...")
    
    try:
        from models import db
        print("  ✅ SQLAlchemy importado")
        
        # Verificar variáveis de ambiente
        import os
        database_url = os.environ.get('DATABASE_URL')
        if database_url:
            print(f"  ✅ DATABASE_URL configurada: {database_url[:30]}...")
        else:
            print("  ❌ DATABASE_URL não configurada")
            return False
        
        return True
        
    except Exception as e:
        print(f"  ❌ Erro no banco de dados: {e}")
        traceback.print_exc()
        return False

def debug_routes():
    """Testar definição de rotas"""
    print("\n🔍 Testando rotas...")
    
    try:
        success, app = debug_app_creation()
        if not success:
            return False
        
        with app.app_context():
            routes = list(app.url_map.iter_rules())
            print(f"  ✅ {len(routes)} rotas definidas")
            
            # Mostrar algumas rotas importantes
            important_routes = [r for r in routes if any(keyword in r.rule for keyword in ['api', 'plano-mestre', 'login'])]
            
            if important_routes:
                print("  📍 Rotas importantes:")
                for route in important_routes[:10]:  # Mostrar apenas as primeiras 10
                    methods = ', '.join(route.methods - {'HEAD', 'OPTIONS'})
                    print(f"    - {route.rule} [{methods}]")
            
            return True
            
    except Exception as e:
        print(f"  ❌ Erro ao testar rotas: {e}")
        traceback.print_exc()
        return False

def debug_startup_complete():
    """Teste completo de inicialização"""
    print("\n🔍 Teste completo de inicialização...")
    
    try:
        success, app = debug_app_creation()
        if not success:
            return False
        
        # Testar se a aplicação pode ser executada
        with app.test_client() as client:
            # Testar rota básica
            response = client.get('/')
            print(f"  ✅ Rota raiz acessível: {response.status_code}")
            
            # Testar rota de API se existir
            try:
                response = client.get('/api/user')
                print(f"  ✅ API user acessível: {response.status_code}")
            except:
                print("  ⚠️ API user não acessível (normal se não logado)")
        
        print("  ✅ Aplicação pode ser executada com sucesso")
        return True
        
    except Exception as e:
        print(f"  ❌ Erro no teste completo: {e}")
        traceback.print_exc()
        return False

def create_minimal_app():
    """Criar versão mínima da aplicação para teste"""
    print("\n🔧 Criando aplicação mínima para teste...")
    
    minimal_app_code = '''
from flask import Flask, jsonify
import os

def create_minimal_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-key-123')
    
    @app.route('/')
    def home():
        return jsonify({'status': 'ok', 'message': 'Aplicação mínima funcionando'})
    
    @app.route('/health')
    def health():
        return jsonify({'status': 'healthy'})
    
    return app

if __name__ == '__main__':
    app = create_minimal_app()
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
'''
    
    try:
        with open('app_minimal.py', 'w') as f:
            f.write(minimal_app_code)
        print("  ✅ app_minimal.py criado")
        
        # Testar aplicação mínima
        exec(minimal_app_code.replace("if __name__ == '__main__':", "if False:"))
        app = create_minimal_app()
        
        with app.test_client() as client:
            response = client.get('/')
            print(f"  ✅ Aplicação mínima testada: {response.status_code}")
            
        return True
        
    except Exception as e:
        print(f"  ❌ Erro ao criar aplicação mínima: {e}")
        traceback.print_exc()
        return False

def main():
    print("🚨 DEBUG DE INICIALIZAÇÃO - HEROKU H27")
    print("="*60)
    
    # Testar imports
    failed_imports = debug_imports()
    
    # Testar banco de dados
    db_ok = debug_database()
    
    # Testar criação da aplicação
    app_ok, app = debug_app_creation()
    
    # Testar rotas
    routes_ok = debug_routes()
    
    # Teste completo
    startup_ok = debug_startup_complete()
    
    # Criar aplicação mínima
    minimal_ok = create_minimal_app()
    
    print("\n" + "="*60)
    print("RESUMO DO DIAGNÓSTICO")
    print("="*60)
    
    print(f"📦 Imports: {'✅ OK' if not failed_imports else f'❌ {len(failed_imports)} falhas'}")
    print(f"🗄️ Banco de dados: {'✅ OK' if db_ok else '❌ PROBLEMA'}")
    print(f"🔧 Criação da app: {'✅ OK' if app_ok else '❌ PROBLEMA'}")
    print(f"🛣️ Rotas: {'✅ OK' if routes_ok else '❌ PROBLEMA'}")
    print(f"🚀 Inicialização: {'✅ OK' if startup_ok else '❌ PROBLEMA'}")
    print(f"🔬 App mínima: {'✅ OK' if minimal_ok else '❌ PROBLEMA'}")
    
    if failed_imports:
        print(f"\n❌ IMPORTS COM PROBLEMA:")
        for module, item, error in failed_imports:
            print(f"  - {module}.{item if item else ''}: {error}")
    
    if not app_ok:
        print(f"\n🔧 RECOMENDAÇÕES:")
        print("1. Verificar se todos os arquivos foram enviados")
        print("2. Verificar sintaxe dos arquivos Python")
        print("3. Usar app_minimal.py temporariamente")
        print("4. Verificar logs detalhados do Heroku")
    
    if minimal_ok and not app_ok:
        print(f"\n💡 SOLUÇÃO TEMPORÁRIA:")
        print("Use app_minimal.py como Procfile temporário:")
        print("web: python app_minimal.py")
    
    print("="*60)

if __name__ == "__main__":
    main()

