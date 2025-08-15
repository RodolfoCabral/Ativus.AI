#!/usr/bin/env python3
"""
Script simples para adicionar coluna foto usando SQL direto
"""

import os
import psycopg2
from urllib.parse import urlparse

def get_database_url():
    """Obter URL do banco de dados"""
    # Tentar diferentes variáveis de ambiente
    database_url = (
        os.environ.get('DATABASE_URL') or 
        os.environ.get('HEROKU_POSTGRESQL_BRONZE_URL') or
        os.environ.get('HEROKU_POSTGRESQL_COPPER_URL') or
        os.environ.get('HEROKU_POSTGRESQL_CRIMSON_URL') or
        os.environ.get('HEROKU_POSTGRESQL_GOLD_URL') or
        os.environ.get('HEROKU_POSTGRESQL_GRAY_URL') or
        os.environ.get('HEROKU_POSTGRESQL_GREEN_URL') or
        os.environ.get('HEROKU_POSTGRESQL_JADE_URL') or
        os.environ.get('HEROKU_POSTGRESQL_LIME_URL') or
        os.environ.get('HEROKU_POSTGRESQL_MAGENTA_URL') or
        os.environ.get('HEROKU_POSTGRESQL_MAROON_URL') or
        os.environ.get('HEROKU_POSTGRESQL_NAVY_URL') or
        os.environ.get('HEROKU_POSTGRESQL_OLIVE_URL') or
        os.environ.get('HEROKU_POSTGRESQL_ORANGE_URL') or
        os.environ.get('HEROKU_POSTGRESQL_PINK_URL') or
        os.environ.get('HEROKU_POSTGRESQL_PURPLE_URL') or
        os.environ.get('HEROKU_POSTGRESQL_RED_URL') or
        os.environ.get('HEROKU_POSTGRESQL_SILVER_URL') or
        os.environ.get('HEROKU_POSTGRESQL_TEAL_URL') or
        os.environ.get('HEROKU_POSTGRESQL_VIOLET_URL') or
        os.environ.get('HEROKU_POSTGRESQL_WHITE_URL') or
        os.environ.get('HEROKU_POSTGRESQL_YELLOW_URL')
    )
    
    return database_url

def add_foto_column():
    """Adicionar coluna foto à tabela equipamentos"""
    
    print("🔧 SCRIPT DE MIGRAÇÃO - COLUNA FOTO")
    print("=" * 40)
    
    # Obter URL do banco
    database_url = get_database_url()
    
    if not database_url:
        print("❌ Nenhuma URL de banco de dados encontrada")
        print("Variáveis de ambiente disponíveis:")
        for key in os.environ:
            if 'POSTGRES' in key or 'DATABASE' in key:
                print(f"  • {key}")
        return False
    
    print(f"✅ URL do banco encontrada: {database_url[:50]}...")
    
    # Corrigir URL se necessário
    if database_url.startswith('postgres://'):
        database_url = database_url.replace('postgres://', 'postgresql://', 1)
    
    try:
        # Conectar ao banco
        print("📡 Conectando ao banco de dados...")
        conn = psycopg2.connect(database_url)
        cursor = conn.cursor()
        
        # Verificar se coluna já existe
        print("🔍 Verificando se coluna 'foto' já existe...")
        cursor.execute("""
            SELECT column_name 
            FROM information_schema.columns 
            WHERE table_name = 'equipamentos' 
            AND column_name = 'foto'
        """)
        
        if cursor.fetchone():
            print("✅ Coluna 'foto' já existe na tabela equipamentos")
            cursor.close()
            conn.close()
            return True
        
        # Verificar se tabela existe
        print("🔍 Verificando se tabela 'equipamentos' existe...")
        cursor.execute("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_name = 'equipamentos'
        """)
        
        if not cursor.fetchone():
            print("❌ Tabela 'equipamentos' não encontrada")
            cursor.close()
            conn.close()
            return False
        
        # Adicionar coluna
        print("📝 Adicionando coluna 'foto'...")
        cursor.execute("""
            ALTER TABLE equipamentos 
            ADD COLUMN foto VARCHAR(255)
        """)
        
        # Confirmar transação
        conn.commit()
        print("✅ Coluna adicionada com sucesso!")
        
        # Verificar resultado
        print("🔍 Verificando resultado...")
        cursor.execute("""
            SELECT column_name, data_type, is_nullable
            FROM information_schema.columns 
            WHERE table_name = 'equipamentos' 
            AND column_name = 'foto'
        """)
        
        row = cursor.fetchone()
        if row:
            print(f"✅ Coluna criada: {row[0]} | {row[1]} | nullable: {row[2]}")
        
        # Mostrar estrutura da tabela
        print("\n📋 Estrutura atual da tabela equipamentos:")
        cursor.execute("""
            SELECT column_name, data_type, is_nullable
            FROM information_schema.columns 
            WHERE table_name = 'equipamentos'
            ORDER BY ordinal_position
        """)
        
        for row in cursor.fetchall():
            nullable = "NULL" if row[2] else "NOT NULL"
            print(f"  • {row[0]} | {row[1]} | {nullable}")
        
        cursor.close()
        conn.close()
        
        print("\n✅ MIGRAÇÃO CONCLUÍDA COM SUCESSO!")
        return True
        
    except Exception as e:
        print(f"❌ Erro: {str(e)}")
        return False

if __name__ == '__main__':
    import sys
    success = add_foto_column()
    if not success:
        sys.exit(1)

