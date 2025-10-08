#!/usr/bin/env python3
"""
Script para forçar re-registro das blueprints PMP
"""

import sys
import os
from datetime import datetime

# Adicionar o diretório atual ao path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def force_register_pmp_blueprints():
    """Força o registro das blueprints PMP"""
    print("🔧 FORÇANDO REGISTRO DAS BLUEPRINTS PMP")
    print("="*60)
    
    try:
        print("1. Criando app Flask...")
        from app import create_app
        app = create_app()
        print("   ✅ App criado")
        
        print("\n2. Verificando blueprints PMP registradas...")
        with app.app_context():
            pmp_blueprints = {}
            for name, blueprint in app.blueprints.items():
                if 'pmp' in name.lower():
                    pmp_blueprints[name] = blueprint
            
            print(f"   📋 {len(pmp_blueprints)} blueprints PMP encontradas:")
            for name in pmp_blueprints.keys():
                print(f"      • {name}")
        
        print("\n3. Verificando rotas PMP específicas...")
        target_routes = [
            '/api/pmp/os/verificar-pendencias',
            '/api/pmp/os/gerar-todas',
            '/api/pmp/os/executar-automatico',
            '/api/pmp/auto/status'
        ]
        
        with app.app_context():
            for target in target_routes:
                found = False
                for rule in app.url_map.iter_rules():
                    if rule.rule == target:
                        print(f"   ✅ {target} - {list(rule.methods)}")
                        found = True
                        break
                
                if not found:
                    print(f"   ❌ {target} - NÃO ENCONTRADA")
        
        print("\n4. Testando importações diretas...")
        
        # Testar importação direta das blueprints
        try:
            from routes.pmp_os_api import pmp_os_api_bp
            print("   ✅ pmp_os_api_bp importada")
        except Exception as e:
            print(f"   ❌ pmp_os_api_bp: {e}")
        
        try:
            from routes.pmp_auto_status import pmp_auto_status_bp
            print("   ✅ pmp_auto_status_bp importada")
        except Exception as e:
            print(f"   ❌ pmp_auto_status_bp: {e}")
        
        return True
        
    except Exception as e:
        print(f"   ❌ Erro: {e}")
        import traceback
        traceback.print_exc()
        return False

def create_manual_registration():
    """Cria código para registro manual das blueprints"""
    print("\n📝 CÓDIGO PARA REGISTRO MANUAL")
    print("="*60)
    
    manual_code = '''
# Adicionar no app.py após outras blueprints
print("🔧 Forçando registro manual das blueprints PMP...")

# Registro forçado da blueprint pmp_os_api
try:
    from routes.pmp_os_api import pmp_os_api_bp
    if 'pmp_os_api' not in app.blueprints:
        app.register_blueprint(pmp_os_api_bp)
        print("✅ pmp_os_api_bp registrada manualmente")
    else:
        print("⚠️ pmp_os_api_bp já estava registrada")
except Exception as e:
    print(f"❌ Erro ao registrar pmp_os_api_bp: {e}")

# Registro forçado da blueprint pmp_auto_status
try:
    from routes.pmp_auto_status import pmp_auto_status_bp
    if 'pmp_auto_status' not in app.blueprints:
        app.register_blueprint(pmp_auto_status_bp)
        print("✅ pmp_auto_status_bp registrada manualmente")
    else:
        print("⚠️ pmp_auto_status_bp já estava registrada")
except Exception as e:
    print(f"❌ Erro ao registrar pmp_auto_status_bp: {e}")

# Verificar rotas após registro manual
pmp_routes = [r.rule for r in app.url_map.iter_rules() if '/api/pmp/' in r.rule]
print(f"📊 Total de rotas PMP registradas: {len(pmp_routes)}")
'''
    
    print(manual_code)
    
    # Salvar código em arquivo
    with open('manual_blueprint_registration.py', 'w') as f:
        f.write(manual_code)
    
    print("💾 Código salvo em 'manual_blueprint_registration.py'")

def create_heroku_test_commands():
    """Cria comandos para testar no Heroku"""
    print("\n🚀 COMANDOS PARA TESTAR NO HEROKU")
    print("="*60)
    
    commands = [
        "# 1. Verificar se arquivos existem",
        "heroku run ls routes/pmp* --app ativusai-af6f1462097d",
        "",
        "# 2. Testar importação das blueprints",
        'heroku run python -c "from routes.pmp_os_api import pmp_os_api_bp; print(\'pmp_os_api OK\')" --app ativusai-af6f1462097d',
        'heroku run python -c "from routes.pmp_auto_status import pmp_auto_status_bp; print(\'pmp_auto_status OK\')" --app ativusai-af6f1462097d',
        "",
        "# 3. Verificar rotas registradas",
        'heroku run python -c "from app import create_app; app=create_app(); print([r.rule for r in app.url_map.iter_rules() if \'/api/pmp/os/\' in r.rule])" --app ativusai-af6f1462097d',
        "",
        "# 4. Testar endpoint de debug",
        "curl https://ativusai-af6f1462097d.herokuapp.com/debug/pmp-status",
        "",
        "# 5. Verificar logs durante inicialização",
        "heroku logs --tail --app ativusai-af6f1462097d | grep -i blueprint"
    ]
    
    for cmd in commands:
        print(cmd)
    
    # Salvar comandos em arquivo
    with open('heroku_test_commands.txt', 'w') as f:
        f.write('\n'.join(commands))
    
    print("\n💾 Comandos salvos em 'heroku_test_commands.txt'")

if __name__ == "__main__":
    print("🔧 SCRIPT PARA FORÇAR REGISTRO DE BLUEPRINTS PMP")
    print(f"Data/Hora: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # Executar verificações
    sucesso = force_register_pmp_blueprints()
    
    # Criar código manual
    create_manual_registration()
    
    # Criar comandos de teste
    create_heroku_test_commands()
    
    print("\n" + "="*60)
    print("📊 RESUMO:")
    if sucesso:
        print("✅ Blueprints funcionam localmente")
        print("🔧 Use os comandos do Heroku para diagnosticar o problema em produção")
        print("📝 Use o código manual se necessário")
    else:
        print("❌ Problemas nas blueprints localmente")
        print("🔧 Corrija os erros antes de fazer deploy")
    
    print("\n🎯 PRÓXIMOS PASSOS:")
    print("1. Faça deploy com as correções")
    print("2. Teste: curl https://ativusai-af6f1462097d.herokuapp.com/debug/pmp-status")
    print("3. Execute os comandos do Heroku para diagnosticar")
    print("4. Se necessário, adicione o código manual no app.py")
    print("="*60)
