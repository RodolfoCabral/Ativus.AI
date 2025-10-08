#!/usr/bin/env python3
"""
Script para verificar se as blueprints estão sendo registradas corretamente
"""

import sys
import os
from datetime import datetime

# Adicionar o diretório atual ao path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def verificar_blueprints():
    """Verifica se as blueprints podem ser importadas e registradas"""
    print("🔍 VERIFICANDO BLUEPRINTS")
    print("="*50)
    
    try:
        print("1. Testando importação da blueprint pmp_os_api...")
        from routes.pmp_os_api import pmp_os_api_bp
        print(f"   ✅ Blueprint importada: {pmp_os_api_bp.name}")
        
        # Verificar rotas da blueprint
        print("   📍 Rotas registradas:")
        for rule in pmp_os_api_bp.url_map.iter_rules():
            print(f"      {rule.methods} {rule.rule}")
        
        print("\n2. Testando importação da blueprint pmp_auto_status...")
        from routes.pmp_auto_status import pmp_auto_status_bp
        print(f"   ✅ Blueprint importada: {pmp_auto_status_bp.name}")
        
        # Verificar rotas da blueprint
        print("   📍 Rotas registradas:")
        for rule in pmp_auto_status_bp.url_map.iter_rules():
            print(f"      {rule.methods} {rule.rule}")
        
        return True
        
    except Exception as e:
        print(f"   ❌ Erro na importação: {e}")
        import traceback
        traceback.print_exc()
        return False

def testar_app_completo():
    """Testa se o app consegue ser criado com todas as blueprints"""
    print("\n🚀 TESTANDO CRIAÇÃO DO APP COMPLETO")
    print("="*50)
    
    try:
        print("1. Importando create_app...")
        from app import create_app
        print("   ✅ Função create_app importada")
        
        print("2. Criando app...")
        app = create_app()
        print("   ✅ App criado com sucesso")
        
        print("3. Verificando rotas registradas...")
        with app.app_context():
            rotas_pmp = []
            for rule in app.url_map.iter_rules():
                if '/api/pmp/' in rule.rule:
                    rotas_pmp.append(f"{list(rule.methods)} {rule.rule}")
            
            if rotas_pmp:
                print("   📍 Rotas PMP encontradas:")
                for rota in rotas_pmp:
                    print(f"      {rota}")
            else:
                print("   ❌ Nenhuma rota PMP encontrada!")
        
        return True
        
    except Exception as e:
        print(f"   ❌ Erro na criação do app: {e}")
        import traceback
        traceback.print_exc()
        return False

def verificar_dependencias():
    """Verifica se todas as dependências estão disponíveis"""
    print("\n📦 VERIFICANDO DEPENDÊNCIAS")
    print("="*50)
    
    dependencias = [
        'flask',
        'flask_login',
        'sqlalchemy',
        'dateutil',
        'models',
        'assets_models',
        'sistema_geracao_os_pmp_aprimorado'
    ]
    
    for dep in dependencias:
        try:
            __import__(dep)
            print(f"   ✅ {dep}")
        except ImportError as e:
            print(f"   ❌ {dep}: {e}")

def gerar_solucoes():
    """Gera soluções para problemas identificados"""
    print("\n🔧 SOLUÇÕES PARA PROBLEMAS 404")
    print("="*50)
    
    print("1. Verificar se as blueprints estão sendo registradas:")
    print("   • Verificar logs do Heroku durante deploy")
    print("   • Procurar por mensagens de erro de importação")
    
    print("\n2. Verificar se os arquivos estão no Heroku:")
    print("   • heroku run ls routes/ --app ativusai-af6f1462097d")
    print("   • heroku run python -c \"from routes.pmp_os_api import pmp_os_api_bp; print('OK')\" --app ativusai-af6f1462097d")
    
    print("\n3. Verificar se as rotas estão registradas:")
    print("   • heroku run python -c \"from app import create_app; app=create_app(); print([r.rule for r in app.url_map.iter_rules() if '/api/pmp/' in r.rule])\" --app ativusai-af6f1462097d")
    
    print("\n4. Forçar re-registro das blueprints:")
    print("   • Adicionar logs de debug no app.py")
    print("   • Verificar se há conflitos de nomes")

if __name__ == "__main__":
    print("🔍 DIAGNÓSTICO DE BLUEPRINTS - ERRO 404")
    print(f"Data/Hora: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # Executar verificações
    sucesso_blueprints = verificar_blueprints()
    verificar_dependencias()
    sucesso_app = testar_app_completo()
    
    # Gerar soluções
    gerar_solucoes()
    
    print("\n" + "="*50)
    print("📊 RESUMO DO DIAGNÓSTICO:")
    print(f"   • Blueprints: {'✅' if sucesso_blueprints else '❌'}")
    print(f"   • App completo: {'✅' if sucesso_app else '❌'}")
    
    if sucesso_blueprints and sucesso_app:
        print("\n🎉 DIAGNÓSTICO: Blueprints funcionam localmente")
        print("   O problema está no deploy/registro no Heroku")
        print("   Verifique os logs do Heroku para erros de importação")
    else:
        print("\n⚠️ DIAGNÓSTICO: Problemas nas blueprints localmente")
        print("   Corrija os erros antes de fazer deploy")
    
    print("="*50)
