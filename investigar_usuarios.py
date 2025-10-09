#!/usr/bin/env python3
"""
Script para investigar a estrutura da tabela de usuários
"""

import sys
import os

# Adicionar o diretório atual ao path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def investigar_modelo_user():
    """Investiga o modelo User para entender sua estrutura"""
    print("🔍 INVESTIGANDO MODELO USER")
    print("="*60)
    
    try:
        from app import create_app
        app = create_app()
        
        with app.app_context():
            # Tentar importar o modelo User
            try:
                from assets_models import User
                print("✅ Modelo User importado com sucesso de assets_models")
                
                # Verificar estrutura do modelo
                print("\n📋 ESTRUTURA DO MODELO USER:")
                
                # Listar atributos do modelo
                atributos = [attr for attr in dir(User) if not attr.startswith('_')]
                print(f"   Atributos disponíveis: {atributos}")
                
                # Verificar colunas da tabela
                if hasattr(User, '__table__'):
                    colunas = [col.name for col in User.__table__.columns]
                    print(f"   Colunas da tabela: {colunas}")
                
                # Tentar buscar alguns usuários
                print("\n👥 USUÁRIOS NO BANCO:")
                usuarios = User.query.limit(10).all()
                
                if usuarios:
                    for usuario in usuarios:
                        print(f"\n   Usuário ID {usuario.id}:")
                        
                        # Verificar todos os atributos possíveis
                        atributos_teste = ['name', 'username', 'nome', 'login', 'user_name', 'email', 'first_name', 'last_name']
                        
                        for attr in atributos_teste:
                            if hasattr(usuario, attr):
                                valor = getattr(usuario, attr)
                                print(f"      {attr}: {valor}")
                        
                        # Verificar se ID 67 existe
                        if usuario.id == 67:
                            print(f"      ⭐ ESTE É O USUÁRIO 67!")
                            
                else:
                    print("   ⚠️ Nenhum usuário encontrado")
                
                # Buscar especificamente o usuário 67
                print("\n🎯 BUSCANDO USUÁRIO ID 67:")
                usuario_67 = User.query.get(67)
                
                if usuario_67:
                    print(f"   ✅ Usuário 67 encontrado!")
                    
                    # Mostrar todos os campos
                    for attr in dir(usuario_67):
                        if not attr.startswith('_') and not callable(getattr(usuario_67, attr)):
                            try:
                                valor = getattr(usuario_67, attr)
                                if valor is not None:
                                    print(f"      {attr}: {valor}")
                            except:
                                pass
                else:
                    print("   ❌ Usuário 67 NÃO encontrado")
                
            except ImportError as e:
                print(f"❌ Erro ao importar User de assets_models: {e}")
                
                # Tentar outras importações
                try:
                    from models import User
                    print("✅ Modelo User importado de models")
                except ImportError:
                    print("❌ Modelo User não encontrado em models")
                    
                try:
                    from app import User
                    print("✅ Modelo User importado de app")
                except ImportError:
                    print("❌ Modelo User não encontrado em app")
        
        return True
        
    except Exception as e:
        print(f"❌ Erro: {e}")
        import traceback
        traceback.print_exc()
        return False

def testar_busca_manual():
    """Testa busca manual usando SQL direto"""
    print("\n🔧 TESTANDO BUSCA MANUAL COM SQL")
    print("="*60)
    
    try:
        from app import create_app
        app = create_app()
        
        with app.app_context():
            from models import db
            
            # Executar SQL direto para ver a estrutura
            result = db.session.execute("SELECT * FROM users WHERE id = 67 LIMIT 1")
            row = result.fetchone()
            
            if row:
                print("✅ Usuário 67 encontrado via SQL:")
                
                # Mostrar todas as colunas
                columns = result.keys()
                for i, column in enumerate(columns):
                    print(f"   {column}: {row[i]}")
            else:
                print("❌ Usuário 67 não encontrado via SQL")
                
                # Listar alguns usuários para ver a estrutura
                result = db.session.execute("SELECT * FROM users LIMIT 5")
                rows = result.fetchall()
                
                if rows:
                    print("\n📋 Primeiros 5 usuários:")
                    columns = result.keys()
                    
                    for row in rows:
                        print(f"\n   ID {row[0]}:")
                        for i, column in enumerate(columns):
                            if row[i] is not None:
                                print(f"      {column}: {row[i]}")
        
        return True
        
    except Exception as e:
        print(f"❌ Erro no SQL: {e}")
        return False

if __name__ == "__main__":
    print("🔍 INVESTIGAÇÃO DE USUÁRIOS")
    print()
    
    # Investigar modelo
    investigar_modelo_user()
    
    # Testar SQL direto
    testar_busca_manual()
    
    print("\n" + "="*60)
    print("📊 INVESTIGAÇÃO CONCLUÍDA")
    print("="*60)
