#!/usr/bin/env python3
"""
Script para debugar sistema de login
"""

import sys
import os

# Adicionar o diretório atual ao path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def debug_login_system():
    """Debugar sistema de login"""
    
    print("🔐 DEBUGANDO SISTEMA DE LOGIN")
    print("=" * 50)
    
    try:
        # Importar aplicação
        from app import create_app
        from models import db
        
        app = create_app()
        
        with app.app_context():
            print("🔍 Verificando configuração do Flask-Login:")
            
            # Verificar se Flask-Login está configurado
            try:
                from flask_login import LoginManager
                print("  ✅ Flask-Login importado com sucesso")
            except Exception as e:
                print(f"  ❌ Erro ao importar Flask-Login: {e}")
                return False
            
            # Verificar modelo de usuário
            print("\n🔍 Verificando modelo de usuário:")
            
            try:
                from models.user import User
                print("  ✅ models.user.User importado com sucesso")
                
                # Verificar se a tabela existe
                from sqlalchemy import text
                result = db.engine.execute(text("SELECT COUNT(*) FROM information_schema.tables WHERE table_name = 'users'"))
                count = result.fetchone()[0]
                
                if count > 0:
                    print("  ✅ Tabela 'users' existe no banco")
                    
                    # Verificar usuários existentes
                    usuarios = User.query.all()
                    print(f"  📊 Total de usuários: {len(usuarios)}")
                    
                    for user in usuarios[:3]:  # Mostrar apenas os primeiros 3
                        print(f"    👤 ID: {user.id}, Email: {user.email}, Status: {getattr(user, 'status', 'N/A')}")
                        
                else:
                    print("  ❌ Tabela 'users' não existe no banco")
                    
            except Exception as e:
                print(f"  ❌ Erro ao verificar modelo User: {e}")
            
            # Verificar configuração de autenticação no app
            print("\n🔍 Verificando configuração de autenticação:")
            
            try:
                # Verificar se login_manager está configurado
                if hasattr(app, 'login_manager'):
                    print("  ✅ LoginManager configurado no app")
                    print(f"    Login view: {app.login_manager.login_view}")
                else:
                    print("  ❌ LoginManager não configurado no app")
                
            except Exception as e:
                print(f"  ❌ Erro ao verificar LoginManager: {e}")
            
            # Testar função de verificação de senha
            print("\n🔍 Testando sistema de hash de senha:")
            
            try:
                from werkzeug.security import generate_password_hash, check_password_hash
                
                # Testar hash
                senha_teste = "123456"
                hash_teste = generate_password_hash(senha_teste)
                verificacao = check_password_hash(hash_teste, senha_teste)
                
                print(f"  ✅ Hash gerado: {hash_teste[:50]}...")
                print(f"  ✅ Verificação: {verificacao}")
                
            except Exception as e:
                print(f"  ❌ Erro ao testar hash de senha: {e}")
            
            # Verificar rotas de autenticação
            print("\n🔍 Verificando rotas de autenticação:")
            
            try:
                # Listar rotas relacionadas a login
                for rule in app.url_map.iter_rules():
                    if any(palavra in rule.rule.lower() for palavra in ['login', 'auth', 'signup']):
                        print(f"  📍 {rule.rule} -> {rule.endpoint}")
                        
            except Exception as e:
                print(f"  ❌ Erro ao verificar rotas: {e}")
            
            print("\n✅ DEBUG DE LOGIN CONCLUÍDO")
            
            return True
            
    except Exception as e:
        print(f"❌ Erro: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == '__main__':
    success = debug_login_system()
    if not success:
        sys.exit(1)

