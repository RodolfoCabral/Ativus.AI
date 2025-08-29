#!/usr/bin/env python3
"""
Script para adicionar as novas colunas na tabela pmps para suportar os novos campos:
- data_inicio_plano (DATE)
- data_fim_plano (DATE) 
- usuarios_responsaveis (TEXT - JSON)
- materiais (TEXT - JSON)
"""

import os
import sys
import psycopg2
from urllib.parse import urlparse

def conectar_banco():
    """Conecta ao banco PostgreSQL do Heroku"""
    try:
        # Tentar diferentes variáveis de ambiente
        database_url = os.environ.get('HEROKU_POSTGRESQL_NAVY_URL')
        if not database_url:
            database_url = os.environ.get('DATABASE_URL')
        if not database_url:
            database_url = 'postgresql://postgres:postgres@localhost:5432/ativus'
        
        # Corrigir URL se necessário
        if database_url.startswith('postgres://'):
            database_url = database_url.replace('postgres://', 'postgresql://', 1)
        
        print(f"🔗 Conectando ao banco: {database_url[:50]}...")
        
        # Conectar ao banco
        conn = psycopg2.connect(database_url)
        conn.autocommit = True
        
        print("✅ Conexão estabelecida com sucesso!")
        return conn
        
    except Exception as e:
        print(f"❌ Erro ao conectar ao banco: {e}")
        return None

def verificar_colunas_existentes(conn):
    """Verifica quais colunas já existem na tabela pmps"""
    try:
        cursor = conn.cursor()
        
        # Verificar colunas existentes
        cursor.execute("""
            SELECT column_name, data_type 
            FROM information_schema.columns 
            WHERE table_name = 'pmps' 
            AND column_name IN ('data_inicio_plano', 'data_fim_plano', 'usuarios_responsaveis', 'materiais')
            ORDER BY column_name;
        """)
        
        colunas_existentes = cursor.fetchall()
        
        print("🔍 VERIFICANDO COLUNAS EXISTENTES:")
        if colunas_existentes:
            for coluna, tipo in colunas_existentes:
                print(f"   ✅ {coluna} ({tipo}) - JÁ EXISTE")
        else:
            print("   ❌ Nenhuma das novas colunas existe ainda")
        
        cursor.close()
        return [coluna[0] for coluna in colunas_existentes]
        
    except Exception as e:
        print(f"❌ Erro ao verificar colunas: {e}")
        return []

def adicionar_colunas(conn):
    """Adiciona as novas colunas na tabela pmps"""
    try:
        cursor = conn.cursor()
        
        # Verificar colunas existentes
        colunas_existentes = verificar_colunas_existentes(conn)
        
        print("\n🔧 ADICIONANDO NOVAS COLUNAS:")
        
        # Lista de colunas para adicionar
        novas_colunas = [
            ('data_inicio_plano', 'DATE', 'Data de início do plano PMP'),
            ('data_fim_plano', 'DATE', 'Data de fim do plano PMP'),
            ('usuarios_responsaveis', 'TEXT', 'JSON com IDs dos usuários responsáveis'),
            ('materiais', 'TEXT', 'JSON com materiais e valores')
        ]
        
        colunas_adicionadas = []
        
        for nome_coluna, tipo_coluna, descricao in novas_colunas:
            if nome_coluna not in colunas_existentes:
                try:
                    sql = f"ALTER TABLE pmps ADD COLUMN {nome_coluna} {tipo_coluna};"
                    print(f"   🔄 Adicionando coluna {nome_coluna}...")
                    cursor.execute(sql)
                    print(f"   ✅ Coluna {nome_coluna} adicionada com sucesso!")
                    colunas_adicionadas.append(nome_coluna)
                except Exception as e:
                    print(f"   ❌ Erro ao adicionar coluna {nome_coluna}: {e}")
            else:
                print(f"   ⏭️ Coluna {nome_coluna} já existe, pulando...")
        
        cursor.close()
        
        if colunas_adicionadas:
            print(f"\n✅ {len(colunas_adicionadas)} COLUNAS ADICIONADAS COM SUCESSO!")
            print("📋 Colunas adicionadas:")
            for coluna in colunas_adicionadas:
                print(f"   - {coluna}")
        else:
            print("\n⏭️ NENHUMA COLUNA NOVA FOI ADICIONADA (todas já existiam)")
        
        return True
        
    except Exception as e:
        print(f"❌ Erro ao adicionar colunas: {e}")
        return False

def verificar_estrutura_final(conn):
    """Verifica a estrutura final da tabela pmps"""
    try:
        cursor = conn.cursor()
        
        # Buscar todas as colunas da tabela pmps
        cursor.execute("""
            SELECT column_name, data_type, is_nullable, column_default
            FROM information_schema.columns 
            WHERE table_name = 'pmps' 
            ORDER BY ordinal_position;
        """)
        
        colunas = cursor.fetchall()
        
        print("\n📋 ESTRUTURA FINAL DA TABELA PMPS:")
        print("-" * 80)
        print(f"{'COLUNA':<25} {'TIPO':<15} {'NULO':<8} {'PADRÃO':<20}")
        print("-" * 80)
        
        for coluna, tipo, nulo, padrao in colunas:
            padrao_str = str(padrao)[:18] if padrao else ''
            print(f"{coluna:<25} {tipo:<15} {nulo:<8} {padrao_str:<20}")
        
        print("-" * 80)
        print(f"Total de colunas: {len(colunas)}")
        
        cursor.close()
        return True
        
    except Exception as e:
        print(f"❌ Erro ao verificar estrutura: {e}")
        return False

def main():
    """Função principal"""
    print("🚀 ADICIONANDO NOVAS COLUNAS NA TABELA PMPS")
    print("=" * 60)
    
    # Conectar ao banco
    conn = conectar_banco()
    if not conn:
        print("❌ Não foi possível conectar ao banco. Abortando.")
        sys.exit(1)
    
    try:
        # Adicionar colunas
        if adicionar_colunas(conn):
            # Verificar estrutura final
            verificar_estrutura_final(conn)
            print("\n🎉 PROCESSO CONCLUÍDO COM SUCESSO!")
        else:
            print("\n❌ PROCESSO FALHOU!")
            sys.exit(1)
    
    finally:
        # Fechar conexão
        conn.close()
        print("\n🔌 Conexão com banco fechada.")

if __name__ == "__main__":
    main()

