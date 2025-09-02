#!/usr/bin/env python3
"""
Script para verificar distribuição de usuários por empresa
"""

import os
import sys
import psycopg2
from urllib.parse import urlparse

def verificar_usuarios_por_empresa():
    """Verifica quantos usuários existem por empresa"""
    
    print("🏢 VERIFICANDO USUÁRIOS POR EMPRESA")
    print("=" * 50)
    
    # Tentar pegar URL do banco das variáveis de ambiente
    database_url = os.environ.get('DATABASE_URL')
    
    if not database_url:
        print("❌ DATABASE_URL não encontrada")
        return False
    
    try:
        # Parse da URL do banco
        url = urlparse(database_url)
        
        # Conectar ao banco
        conn = psycopg2.connect(
            host=url.hostname,
            database=url.path[1:],
            user=url.username,
            password=url.password,
            port=url.port or 5432
        )
        
        cursor = conn.cursor()
        
        print("✅ CONEXÃO ESTABELECIDA!")
        
        # Verificar total de usuários
        cursor.execute('SELECT COUNT(*) FROM "user"')
        total = cursor.fetchone()[0]
        print(f"📊 Total de usuários na tabela: {total}")
        
        # Verificar distribuição por empresa
        cursor.execute('''
            SELECT company, COUNT(*) as total
            FROM "user" 
            GROUP BY company
            ORDER BY total DESC
        ''')
        
        empresas = cursor.fetchall()
        print(f"\n🏢 DISTRIBUIÇÃO POR EMPRESA:")
        
        for empresa, count in empresas:
            print(f"  - {empresa}: {count} usuários")
        
        # Verificar usuários específicos
        cursor.execute('''
            SELECT id, name, email, company
            FROM "user" 
            ORDER BY company, name
        ''')
        
        usuarios = cursor.fetchall()
        print(f"\n👥 TODOS OS USUÁRIOS:")
        
        empresa_atual = None
        for user_id, name, email, company in usuarios:
            if company != empresa_atual:
                print(f"\n🏢 EMPRESA: {company}")
                empresa_atual = company
            print(f"  {user_id}. {name} ({email})")
        
        # Simular busca para usuário ID 1
        print(f"\n🧪 SIMULANDO BUSCA PARA USUÁRIO ID 1:")
        
        cursor.execute('SELECT name, company FROM "user" WHERE id = 1')
        usuario_1 = cursor.fetchone()
        
        if usuario_1:
            nome, empresa = usuario_1
            print(f"👤 Usuário 1: {nome} - Empresa: {empresa}")
            
            # Buscar colegas
            cursor.execute('''
                SELECT id, name, email 
                FROM "user" 
                WHERE company = %s AND id != 1
                ORDER BY name
            ''', (empresa,))
            
            colegas = cursor.fetchall()
            print(f"👥 Colegas da empresa '{empresa}': {len(colegas)}")
            
            for colega_id, colega_nome, colega_email in colegas:
                print(f"  - {colega_nome} ({colega_email})")
        else:
            print("❌ Usuário ID 1 não encontrado")
        
        cursor.close()
        conn.close()
        
        return True
        
    except Exception as e:
        print(f"❌ Erro: {e}")
        return False

if __name__ == "__main__":
    verificar_usuarios_por_empresa()

