#!/usr/bin/env python3
"""
Script para testar busca de usuários
"""

import sys
import os

# Adicionar o diretório atual ao path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def testar_busca_usuarios():
    """Testa a busca de usuários"""
    print("🔍 TESTANDO BUSCA DE USUÁRIOS")
    print("="*60)
    
    try:
        from app import create_app
        app = create_app()
        
        with app.app_context():
            from routes.usuario_helper import (
                buscar_nome_usuario_por_id,
                listar_usuarios_ativos,
                validar_usuario_existe
            )
            
            # Listar todos os usuários
            print("📋 LISTANDO USUÁRIOS ATIVOS:")
            usuarios = listar_usuarios_ativos()
            
            if usuarios:
                for usuario in usuarios:
                    print(f"   ID: {usuario['id']} → Nome: {usuario['nome']}")
                
                print(f"\n📊 Total de usuários: {len(usuarios)}")
                
                # Testar busca individual
                print("\n🔍 TESTANDO BUSCA INDIVIDUAL:")
                for usuario in usuarios[:3]:  # Testar primeiros 3
                    user_id = usuario['id']
                    nome = buscar_nome_usuario_por_id(user_id)
                    existe = validar_usuario_existe(user_id)
                    
                    print(f"   ID {user_id}: Nome='{nome}', Existe={existe}")
                
                # Testar IDs que não existem
                print("\n⚠️ TESTANDO IDs INEXISTENTES:")
                for test_id in [999, 1000, "abc"]:
                    nome = buscar_nome_usuario_por_id(test_id)
                    existe = validar_usuario_existe(test_id)
                    print(f"   ID {test_id}: Nome='{nome}', Existe={existe}")
                
            else:
                print("   ⚠️ Nenhum usuário encontrado")
            
            # Testar PMPs com usuários
            print("\n🔧 TESTANDO PMPs COM USUÁRIOS:")
            from models.pmp_limpo import PMP
            import json
            
            pmps_com_usuarios = PMP.query.filter(
                PMP.status == 'ativo',
                PMP.usuarios_responsaveis.isnot(None)
            ).all()
            
            if pmps_com_usuarios:
                for pmp in pmps_com_usuarios:
                    print(f"   PMP {pmp.codigo}: usuarios_responsaveis = {pmp.usuarios_responsaveis}")
                    
                    try:
                        usuarios_ids = json.loads(pmp.usuarios_responsaveis)
                        for user_id in usuarios_ids:
                            nome = buscar_nome_usuario_por_id(user_id)
                            print(f"      ID {user_id} → Nome: {nome}")
                    except Exception as e:
                        print(f"      ❌ Erro ao fazer parse: {e}")
            else:
                print("   ⚠️ Nenhuma PMP com usuários responsáveis encontrada")
        
        return True
        
    except Exception as e:
        print(f"❌ Erro: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("🔍 TESTE DE BUSCA DE USUÁRIOS")
    print()
    
    sucesso = testar_busca_usuarios()
    
    print("\n" + "="*60)
    if sucesso:
        print("✅ TESTE CONCLUÍDO COM SUCESSO")
    else:
        print("❌ TESTE FALHOU")
    print("="*60)
