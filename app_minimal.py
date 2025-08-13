#!/usr/bin/env python3
"""
Aplicação Flask mínima para testar se o Heroku consegue executar Flask básico
Use esta versão se a aplicação principal não estiver iniciando
"""

from flask import Flask, jsonify, render_template_string
import os

def create_minimal_app():
    """Criar aplicação Flask mínima"""
    app = Flask(__name__)
    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-key-minimal-123')
    
    @app.route('/')
    def home():
        """Página inicial mínima"""
        html = '''
        <!DOCTYPE html>
        <html>
        <head>
            <title>SaaS Ativus - Modo Mínimo</title>
            <style>
                body { font-family: Arial, sans-serif; margin: 40px; background: #f5f5f5; }
                .container { max-width: 800px; margin: 0 auto; background: white; padding: 30px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
                .status { padding: 15px; background: #d4edda; border: 1px solid #c3e6cb; border-radius: 5px; color: #155724; margin: 20px 0; }
                .warning { padding: 15px; background: #fff3cd; border: 1px solid #ffeaa7; border-radius: 5px; color: #856404; margin: 20px 0; }
                .btn { display: inline-block; padding: 10px 20px; background: #007bff; color: white; text-decoration: none; border-radius: 5px; margin: 5px; }
                .btn:hover { background: #0056b3; }
            </style>
        </head>
        <body>
            <div class="container">
                <h1>🔧 SaaS Ativus - Modo Diagnóstico</h1>
                
                <div class="status">
                    ✅ <strong>Aplicação Flask funcionando!</strong><br>
                    O Heroku consegue executar Flask básico.
                </div>
                
                <div class="warning">
                    ⚠️ <strong>Modo Mínimo Ativo</strong><br>
                    A aplicação principal não conseguiu iniciar. Esta é uma versão simplificada para diagnóstico.
                </div>
                
                <h3>🔍 Informações do Sistema:</h3>
                <ul>
                    <li><strong>Status:</strong> Aplicação mínima funcionando</li>
                    <li><strong>Porta:</strong> {{ port }}</li>
                    <li><strong>Ambiente:</strong> {{ env }}</li>
                    <li><strong>Python:</strong> {{ python_version }}</li>
                </ul>
                
                <h3>🧪 Testes Disponíveis:</h3>
                <a href="/health" class="btn">🏥 Health Check</a>
                <a href="/test-imports" class="btn">📦 Testar Imports</a>
                <a href="/test-database" class="btn">🗄️ Testar Banco</a>
                <a href="/debug-full" class="btn">🔍 Debug Completo</a>
                
                <h3>🔧 Próximos Passos:</h3>
                <ol>
                    <li>Execute os testes acima para identificar problemas</li>
                    <li>Verifique os logs do Heroku: <code>heroku logs --tail</code></li>
                    <li>Execute o debug no servidor: <code>heroku run python debug_startup.py</code></li>
                    <li>Corrija os problemas identificados</li>
                    <li>Volte para a aplicação principal</li>
                </ol>
            </div>
        </body>
        </html>
        '''
        
        import sys
        return render_template_string(html, 
            port=os.environ.get('PORT', '5000'),
            env=os.environ.get('FLASK_ENV', 'production'),
            python_version=sys.version
        )
    
    @app.route('/health')
    def health():
        """Health check endpoint"""
        return jsonify({
            'status': 'healthy',
            'message': 'Aplicação mínima funcionando',
            'port': os.environ.get('PORT'),
            'env': os.environ.get('FLASK_ENV', 'production')
        })
    
    @app.route('/test-imports')
    def test_imports():
        """Testar imports problemáticos"""
        results = {}
        
        imports_to_test = [
            ('flask', 'Flask'),
            ('flask_sqlalchemy', 'SQLAlchemy'),
            ('models', None),
            ('routes.plano_mestre', 'plano_mestre_bp'),
            ('models.plano_mestre', 'PlanoMestre'),
        ]
        
        for module, item in imports_to_test:
            try:
                if item:
                    exec(f"from {module} import {item}")
                else:
                    exec(f"import {module}")
                results[f"{module}.{item if item else ''}"] = "✅ OK"
            except Exception as e:
                results[f"{module}.{item if item else ''}"] = f"❌ {str(e)}"
        
        return jsonify({
            'status': 'completed',
            'results': results
        })
    
    @app.route('/test-database')
    def test_database():
        """Testar conexão com banco de dados"""
        try:
            database_url = os.environ.get('DATABASE_URL')
            if not database_url:
                return jsonify({
                    'status': 'error',
                    'message': 'DATABASE_URL não configurada'
                })
            
            # Tentar importar SQLAlchemy
            from flask_sqlalchemy import SQLAlchemy
            
            # Criar app temporária para testar DB
            test_app = Flask(__name__)
            test_app.config['SQLALCHEMY_DATABASE_URI'] = database_url
            test_app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
            
            db = SQLAlchemy(test_app)
            
            with test_app.app_context():
                # Testar conexão
                db.engine.execute('SELECT 1')
            
            return jsonify({
                'status': 'success',
                'message': 'Conexão com banco de dados OK',
                'database_url': database_url[:30] + '...'
            })
            
        except Exception as e:
            return jsonify({
                'status': 'error',
                'message': f'Erro no banco de dados: {str(e)}'
            })
    
    @app.route('/debug-full')
    def debug_full():
        """Debug completo do sistema"""
        try:
            # Executar script de debug
            import subprocess
            result = subprocess.run(['python', 'debug_startup.py'], 
                                  capture_output=True, text=True, timeout=30)
            
            return jsonify({
                'status': 'completed',
                'stdout': result.stdout,
                'stderr': result.stderr,
                'returncode': result.returncode
            })
            
        except subprocess.TimeoutExpired:
            return jsonify({
                'status': 'timeout',
                'message': 'Debug demorou mais de 30 segundos'
            })
        except Exception as e:
            return jsonify({
                'status': 'error',
                'message': f'Erro ao executar debug: {str(e)}'
            })
    
    return app

# Criar aplicação
app = create_minimal_app()

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)

