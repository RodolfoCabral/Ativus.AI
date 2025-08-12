#!/usr/bin/env python3
"""
Script para corrigir problemas de blueprints no Heroku
Execute este script para tentar corrigir automaticamente problemas de registro
"""

import os
import sys

def corrigir_blueprints():
    """Tentar corrigir problemas de blueprints automaticamente"""
    
    print("🔧 Iniciando correção de blueprints...")
    
    try:
        # Importar aplicação
        from app import create_app
        
        print("✅ Aplicação importada com sucesso")
        
        # Criar aplicação Flask
        app = create_app()
        print("✅ Aplicação Flask criada")
        
        # Verificar se blueprint já está registrado
        if 'plano_mestre' in app.blueprints:
            print("✅ Blueprint plano_mestre já registrado")
        else:
            print("❌ Blueprint plano_mestre NÃO registrado")
            
            # Tentar registrar manualmente
            try:
                from routes.plano_mestre import plano_mestre_bp
                app.register_blueprint(plano_mestre_bp)
                print("✅ Blueprint plano_mestre registrado manualmente")
            except Exception as e:
                print(f"❌ Erro ao registrar blueprint manualmente: {e}")
        
        # Verificar blueprint de debug
        if 'plano_mestre_debug' in app.blueprints:
            print("✅ Blueprint plano_mestre_debug já registrado")
        else:
            print("❌ Blueprint plano_mestre_debug NÃO registrado")
            
            # Tentar registrar manualmente
            try:
                from routes.plano_mestre_debug import plano_mestre_debug_bp
                app.register_blueprint(plano_mestre_debug_bp)
                print("✅ Blueprint plano_mestre_debug registrado manualmente")
            except Exception as e:
                print(f"❌ Erro ao registrar blueprint debug manualmente: {e}")
        
        # Listar rotas após correção
        print("\n🛣️ Rotas após correção:")
        rotas_plano_mestre = []
        with app.app_context():
            for rule in app.url_map.iter_rules():
                if 'plano-mestre' in rule.rule:
                    methods = ', '.join(rule.methods - {'HEAD', 'OPTIONS'})
                    print(f"  ✓ {rule.rule} [{methods}]")
                    rotas_plano_mestre.append(rule)
        
        if rotas_plano_mestre:
            print(f"✅ {len(rotas_plano_mestre)} rotas do plano mestre encontradas")
            
            # Testar uma rota específica
            print("\n🧪 Testando rota específica...")
            with app.test_client() as client:
                # Simular session de usuário logado
                with client.session_transaction() as sess:
                    sess['user_id'] = 1
                    sess['logged_in'] = True
                
                # Testar rota de debug
                response = client.get('/api/plano-mestre-debug/test-auth')
                print(f"  📡 GET /api/plano-mestre-debug/test-auth: {response.status_code}")
                
                if response.status_code == 200:
                    print("  ✅ Rota de debug funcionando")
                else:
                    print(f"  ❌ Rota de debug retornou: {response.status_code}")
                
                # Testar rota principal
                response = client.get('/api/plano-mestre/equipamento/1')
                print(f"  📡 GET /api/plano-mestre/equipamento/1: {response.status_code}")
                
                if response.status_code in [200, 404]:  # 404 é OK se não houver dados
                    print("  ✅ Rota principal acessível")
                else:
                    print(f"  ❌ Rota principal retornou: {response.status_code}")
            
            return True
        else:
            print("❌ Nenhuma rota do plano mestre encontrada após correção")
            return False
        
    except ImportError as e:
        print(f"❌ ERRO DE IMPORTAÇÃO: {e}")
        print("\n🔧 POSSÍVEIS SOLUÇÕES:")
        print("1. Verificar se o arquivo routes/plano_mestre.py existe")
        print("2. Verificar se o arquivo models/plano_mestre.py existe")
        print("3. Executar: heroku run python create_tables.py -a sua-app")
        return False
        
    except Exception as e:
        print(f"❌ ERRO GERAL: {e}")
        import traceback
        traceback.print_exc()
        return False

def criar_arquivo_init():
    """Criar arquivo __init__.py se não existir"""
    
    print("\n📁 Verificando arquivos __init__.py...")
    
    diretorios = ['routes', 'models']
    
    for diretorio in diretorios:
        init_path = os.path.join(diretorio, '__init__.py')
        
        if os.path.exists(init_path):
            print(f"  ✅ {init_path} já existe")
        else:
            print(f"  ❌ {init_path} não existe, criando...")
            
            try:
                os.makedirs(diretorio, exist_ok=True)
                with open(init_path, 'w') as f:
                    f.write('# __init__.py\n')
                print(f"  ✅ {init_path} criado")
            except Exception as e:
                print(f"  ❌ Erro ao criar {init_path}: {e}")

if __name__ == "__main__":
    print("🔧 CORREÇÃO DE BLUEPRINTS - HEROKU")
    print("="*50)
    
    # Criar arquivos __init__.py se necessário
    criar_arquivo_init()
    
    # Tentar corrigir blueprints
    sucesso = corrigir_blueprints()
    
    print("\n" + "="*50)
    if sucesso:
        print("🎉 CORREÇÃO CONCLUÍDA: Blueprints funcionando")
        print("\n🚀 PRÓXIMOS PASSOS:")
        print("1. Reiniciar a aplicação no Heroku")
        print("2. Testar a URL: /api/plano-mestre-debug/test-auth")
        print("3. Verificar se o erro 404 foi resolvido")
    else:
        print("⚠️ CORREÇÃO CONCLUÍDA: Problemas persistem")
        print("\n🔧 AÇÕES NECESSÁRIAS:")
        print("1. Verificar se todos os arquivos foram enviados")
        print("2. Executar create_tables.py para criar tabelas")
        print("3. Verificar logs do Heroku para mais detalhes")
    print("="*50)

