#!/usr/bin/env python3
"""
Script para verificar se os blueprints estão registrados corretamente no Heroku
Execute este script para diagnosticar problemas de rotas 404
"""

import os
import sys

def verificar_blueprints():
    """Verificar todos os blueprints registrados na aplicação"""
    
    print("🔍 Verificando blueprints registrados...")
    
    try:
        # Importar aplicação
        from app import create_app
        
        print("✅ Aplicação importada com sucesso")
        
        # Criar aplicação Flask
        app = create_app()
        print("✅ Aplicação Flask criada")
        
        # Listar todos os blueprints registrados
        print("\n📋 Blueprints registrados:")
        if app.blueprints:
            for nome, blueprint in app.blueprints.items():
                print(f"  ✓ {nome} - {blueprint.url_prefix or '/'}")
        else:
            print("  ❌ Nenhum blueprint registrado!")
        
        # Verificar blueprint específico do plano mestre
        plano_mestre_registrado = 'plano_mestre' in app.blueprints
        debug_registrado = 'plano_mestre_debug' in app.blueprints
        
        print(f"\n🔍 Blueprint plano_mestre: {'✅ REGISTRADO' if plano_mestre_registrado else '❌ NÃO REGISTRADO'}")
        print(f"🔍 Blueprint plano_mestre_debug: {'✅ REGISTRADO' if debug_registrado else '❌ NÃO REGISTRADO'}")
        
        # Listar todas as rotas da aplicação
        print("\n🛣️ Todas as rotas registradas:")
        with app.app_context():
            for rule in app.url_map.iter_rules():
                methods = ', '.join(rule.methods - {'HEAD', 'OPTIONS'})
                print(f"  {rule.rule} [{methods}] -> {rule.endpoint}")
        
        # Verificar rotas específicas do plano mestre
        rotas_plano_mestre = [rule for rule in app.url_map.iter_rules() if 'plano-mestre' in rule.rule]
        
        print(f"\n🎯 Rotas do plano mestre encontradas: {len(rotas_plano_mestre)}")
        for rota in rotas_plano_mestre:
            methods = ', '.join(rota.methods - {'HEAD', 'OPTIONS'})
            print(f"  ✓ {rota.rule} [{methods}]")
        
        if not rotas_plano_mestre:
            print("  ❌ NENHUMA ROTA DO PLANO MESTRE ENCONTRADA!")
            print("  🔧 Isso explica o erro 404")
        
        # Verificar se os arquivos existem
        print("\n📁 Verificando arquivos:")
        arquivos_necessarios = [
            'routes/plano_mestre.py',
            'routes/plano_mestre_debug.py',
            'models/plano_mestre.py'
        ]
        
        for arquivo in arquivos_necessarios:
            if os.path.exists(arquivo):
                print(f"  ✅ {arquivo} - EXISTE")
            else:
                print(f"  ❌ {arquivo} - NÃO ENCONTRADO")
        
        # Tentar importar os módulos diretamente
        print("\n🔧 Testando imports:")
        try:
            from routes.plano_mestre import plano_mestre_bp
            print("  ✅ routes.plano_mestre importado com sucesso")
            print(f"  📍 URL prefix: {plano_mestre_bp.url_prefix}")
        except ImportError as e:
            print(f"  ❌ Erro ao importar routes.plano_mestre: {e}")
        except Exception as e:
            print(f"  ❌ Erro geral ao importar routes.plano_mestre: {e}")
        
        try:
            from routes.plano_mestre_debug import plano_mestre_debug_bp
            print("  ✅ routes.plano_mestre_debug importado com sucesso")
            print(f"  📍 URL prefix: {plano_mestre_debug_bp.url_prefix}")
        except ImportError as e:
            print(f"  ❌ Erro ao importar routes.plano_mestre_debug: {e}")
        except Exception as e:
            print(f"  ❌ Erro geral ao importar routes.plano_mestre_debug: {e}")
        
        try:
            from models.plano_mestre import PlanoMestre, AtividadePlanoMestre
            print("  ✅ models.plano_mestre importado com sucesso")
        except ImportError as e:
            print(f"  ❌ Erro ao importar models.plano_mestre: {e}")
        except Exception as e:
            print(f"  ❌ Erro geral ao importar models.plano_mestre: {e}")
        
        # Verificar variáveis de ambiente
        print("\n🌍 Variáveis de ambiente:")
        env_vars = ['DATABASE_URL', 'SECRET_KEY', 'FLASK_ENV']
        for var in env_vars:
            valor = os.environ.get(var)
            if valor:
                # Mascarar valores sensíveis
                if 'SECRET' in var or 'PASSWORD' in var or 'DATABASE' in var:
                    valor_mostrar = valor[:10] + '...' if len(valor) > 10 else '***'
                else:
                    valor_mostrar = valor
                print(f"  ✅ {var}: {valor_mostrar}")
            else:
                print(f"  ❌ {var}: NÃO DEFINIDA")
        
        print("\n" + "="*60)
        print("DIAGNÓSTICO COMPLETO")
        print("="*60)
        
        if plano_mestre_registrado and rotas_plano_mestre:
            print("✅ TUDO OK: Blueprint registrado e rotas disponíveis")
        elif not plano_mestre_registrado:
            print("❌ PROBLEMA: Blueprint não registrado")
            print("🔧 SOLUÇÃO: Verificar imports no app.py")
        elif not rotas_plano_mestre:
            print("❌ PROBLEMA: Blueprint registrado mas sem rotas")
            print("🔧 SOLUÇÃO: Verificar definição das rotas no blueprint")
        
        return plano_mestre_registrado and len(rotas_plano_mestre) > 0
        
    except ImportError as e:
        print(f"❌ ERRO DE IMPORTAÇÃO: {e}")
        print("🔧 Verifique se todos os arquivos foram enviados para o Heroku")
        return False
        
    except Exception as e:
        print(f"❌ ERRO GERAL: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("🔍 VERIFICAÇÃO DE BLUEPRINTS - HEROKU")
    print("="*50)
    
    sucesso = verificar_blueprints()
    
    print("\n" + "="*50)
    if sucesso:
        print("🎉 VERIFICAÇÃO CONCLUÍDA: Sistema OK")
    else:
        print("⚠️ VERIFICAÇÃO CONCLUÍDA: Problemas encontrados")
    print("="*50)

