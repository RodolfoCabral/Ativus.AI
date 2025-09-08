#!/usr/bin/env python3
"""
DEBUG DO USUÁRIO LOGADO
Verifica informações do usuário logado e da sessão
Execute com: heroku run python debug_usuario_logado.py -a ativusai
"""

import sys
import os
from datetime import datetime
import json

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def debug_usuario_logado():
    """Debug do usuário logado e sessão"""
    
    print("🔍 DEBUG DO USUÁRIO LOGADO E SESSÃO")
    print("=" * 50)
    
    try:
        from flask import Flask, session
        from flask_login import LoginManager, current_user
        from models import db, User
        from app import create_app
        
        app = create_app()
        
        with app.test_request_context():
            print("1️⃣ VERIFICANDO USUÁRIO LOGADO...")
            
            # Verificar se há usuário logado
            if hasattr(current_user, 'is_authenticated') and current_user.is_authenticated:
                print(f"✅ Usuário autenticado: {current_user.username}")
                print(f"   ID: {current_user.id}")
                print(f"   Email: {current_user.email}")
                
                # Verificar atributos adicionais
                for attr in ['company', 'role', 'first_name', 'last_name']:
                    if hasattr(current_user, attr):
                        print(f"   {attr}: {getattr(current_user, attr)}")
            else:
                print("❌ Nenhum usuário autenticado no contexto atual")
            
            print("\n2️⃣ VERIFICANDO SESSÃO...")
            
            # Verificar dados na sessão
            if session:
                print(f"✅ Sessão encontrada com {len(session)} itens:")
                for key in session:
                    print(f"   {key}: {session[key]}")
            else:
                print("❌ Nenhum dado na sessão")
            
            print("\n3️⃣ VERIFICANDO USUÁRIOS NO BANCO...")
            
            # Verificar usuários no banco
            with app.app_context():
                users = User.query.limit(5).all()
                
                if users:
                    print(f"✅ Encontrados {len(users)} usuários:")
                    for user in users:
                        print(f"   ID: {user.id} | Username: {user.username} | Email: {user.email}")
                        
                        # Verificar atributos adicionais
                        for attr in ['company', 'role', 'first_name', 'last_name']:
                            if hasattr(user, attr):
                                print(f"      {attr}: {getattr(user, attr)}")
                else:
                    print("❌ Nenhum usuário encontrado no banco")
            
            print("\n4️⃣ VERIFICANDO MODELO DE USUÁRIO...")
            
            # Verificar estrutura do modelo User
            print(f"✅ Atributos do modelo User:")
            user_attrs = [attr for attr in dir(User) if not attr.startswith('_') and attr not in ['metadata', 'query', 'query_class']]
            for attr in user_attrs:
                print(f"   {attr}")
            
            print("\n5️⃣ VERIFICANDO ROTAS DE AUTENTICAÇÃO...")
            
            # Verificar rotas registradas
            print(f"✅ Rotas registradas:")
            for rule in app.url_map.iter_rules():
                if 'auth' in rule.endpoint or 'login' in rule.endpoint or 'logout' in rule.endpoint:
                    print(f"   {rule.rule} -> {rule.endpoint}")
            
            print("\n6️⃣ DIAGNÓSTICO FINAL...")
            
            # Diagnóstico final
            if hasattr(current_user, 'is_authenticated') and current_user.is_authenticated:
                print("✅ Sistema de autenticação funcionando corretamente")
                print(f"   Usuário: {current_user.username}")
                if hasattr(current_user, 'company'):
                    print(f"   Empresa: {current_user.company}")
                else:
                    print("⚠️ Usuário não tem atributo 'company'")
            else:
                print("⚠️ Nenhum usuário autenticado no contexto atual")
                print("   Recomendação: Verificar se o login está sendo feito corretamente")
                print("   Alternativa: Usar dados da sessão para obter informações do usuário")
            
    except Exception as e:
        import traceback
        print(f"❌ ERRO: {e}")
        traceback.print_exc()

if __name__ == "__main__":
    debug_usuario_logado()

