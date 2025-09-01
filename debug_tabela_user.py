#!/usr/bin/env python3
"""
Script para verificar a estrutura da tabela user e dados reais
"""

import os
import sys

# Adicionar o diretório do projeto ao path
sys.path.append('/home/ubuntu/SaaS Ativus')

try:
    from models import db
    from sqlalchemy import text, inspect
    import json
    
    def verificar_tabela_user():
        """Verifica a estrutura e dados da tabela user"""
        
        print("🔍 VERIFICANDO TABELA USER")
        print("=" * 50)
        
        try:
            # Verificar se a tabela existe
            inspector = inspect(db.engine)
            tabelas = inspector.get_table_names()
            
            print(f"📋 Tabelas encontradas: {len(tabelas)}")
            for tabela in sorted(tabelas):
                print(f"  - {tabela}")
            
            # Verificar variações do nome da tabela
            tabelas_user = [t for t in tabelas if 'user' in t.lower()]
            print(f"\n👤 Tabelas relacionadas a usuários: {tabelas_user}")
            
            # Tentar diferentes nomes de tabela
            nomes_possiveis = ['user', 'users', 'User', 'Users', 'usuario', 'usuarios']
            
            for nome_tabela in nomes_possiveis:
                if nome_tabela in tabelas:
                    print(f"\n✅ TABELA ENCONTRADA: {nome_tabela}")
                    
                    # Verificar colunas
                    colunas = inspector.get_columns(nome_tabela)
                    print(f"📊 Colunas da tabela {nome_tabela}:")
                    for coluna in colunas:
                        print(f"  - {coluna['name']} ({coluna['type']})")
                    
                    # Verificar dados
                    query = text(f'SELECT * FROM "{nome_tabela}" LIMIT 5')
                    result = db.session.execute(query)
                    rows = result.fetchall()
                    
                    print(f"\n📄 Primeiros 5 registros:")
                    for i, row in enumerate(rows, 1):
                        print(f"  {i}. {dict(row._mapping)}")
                    
                    # Verificar se tem coluna company
                    colunas_nomes = [c['name'] for c in colunas]
                    if 'company' in colunas_nomes:
                        print(f"\n🏢 COLUNA 'company' ENCONTRADA!")
                        
                        # Verificar empresas distintas
                        query_empresas = text(f'SELECT DISTINCT company FROM "{nome_tabela}" WHERE company IS NOT NULL')
                        result_empresas = db.session.execute(query_empresas)
                        empresas = [row[0] for row in result_empresas.fetchall()]
                        print(f"🏢 Empresas encontradas: {empresas}")
                        
                        # Verificar usuários por empresa
                        for empresa_id in empresas[:3]:  # Primeiras 3 empresas
                            query_usuarios = text(f'''
                                SELECT id, name, email, cargo, status 
                                FROM "{nome_tabela}" 
                                WHERE company = :company_id 
                                LIMIT 5
                            ''')
                            result_usuarios = db.session.execute(query_usuarios, {'company_id': empresa_id})
                            usuarios = result_usuarios.fetchall()
                            
                            print(f"\n👥 Usuários da empresa {empresa_id}:")
                            for usuario in usuarios:
                                print(f"  - {dict(usuario._mapping)}")
                    else:
                        print(f"\n❌ Coluna 'company' NÃO encontrada")
                        print(f"💡 Colunas disponíveis: {colunas_nomes}")
                    
                    return nome_tabela
            
            print("\n❌ NENHUMA TABELA DE USUÁRIOS ENCONTRADA")
            return None
            
        except Exception as e:
            print(f"❌ Erro ao verificar tabela: {e}")
            return None
    
    def testar_query_usuarios():
        """Testa a query específica da API"""
        
        print("\n🧪 TESTANDO QUERY DA API")
        print("=" * 30)
        
        try:
            # Tentar a query exata da API
            query_usuario = text('''
                SELECT company 
                FROM "user" 
                WHERE id = :user_id
            ''')
            
            result_usuario = db.session.execute(query_usuario, {'user_id': 1})
            usuario_row = result_usuario.fetchone()
            
            if usuario_row:
                company_id = usuario_row.company
                print(f"✅ Usuário ID 1 encontrado, empresa: {company_id}")
                
                # Buscar usuários da mesma empresa
                query_usuarios = text('''
                    SELECT id, name, email, cargo, status
                    FROM "user" 
                    WHERE company = :company_id 
                    AND status = 'ativo'
                    AND id != :user_id
                    ORDER BY name
                ''')
                
                result_usuarios = db.session.execute(query_usuarios, {
                    'company_id': company_id,
                    'user_id': 1
                })
                usuarios = result_usuarios.fetchall()
                
                print(f"👥 Usuários da empresa {company_id}:")
                for usuario in usuarios:
                    print(f"  - {dict(usuario._mapping)}")
                
                return True
            else:
                print("❌ Usuário ID 1 não encontrado")
                return False
                
        except Exception as e:
            print(f"❌ Erro na query da API: {e}")
            return False
    
    if __name__ == "__main__":
        # Verificar estrutura da tabela
        nome_tabela = verificar_tabela_user()
        
        # Testar query da API
        if nome_tabela:
            testar_query_usuarios()
        
        print("\n🏁 VERIFICAÇÃO CONCLUÍDA")

except ImportError as e:
    print(f"❌ Erro de import: {e}")
    print("💡 Execute este script no diretório do projeto Flask")
except Exception as e:
    print(f"❌ Erro inesperado: {e}")

