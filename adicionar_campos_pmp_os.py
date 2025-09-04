#!/usr/bin/env python3
"""
Script para adicionar campos necessários para integração PMP → OS
Execute este script após fazer deploy do código atualizado
"""

import os
import sys
from sqlalchemy import text

# Adicionar o diretório atual ao path para importar os modelos
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

try:
    from models import db
    from app import create_app
    print("✅ Modelos importados com sucesso")
except ImportError as e:
    print(f"❌ Erro ao importar modelos: {e}")
    sys.exit(1)

def adicionar_colunas_ordens_servico():
    """Adiciona colunas necessárias à tabela ordens_servico"""
    print("\n🔧 ADICIONANDO COLUNAS À TABELA ORDENS_SERVICO")
    print("=" * 60)
    
    colunas = [
        ("pmp_id", "INTEGER", "FK para tabela pmps"),
        ("data_proxima_geracao", "DATE", "Controle de frequência"),
        ("frequencia_origem", "VARCHAR(20)", "Tipo de frequência"),
        ("numero_sequencia", "INTEGER DEFAULT 1", "Contador de OS geradas pela PMP")
    ]
    
    for nome, tipo, descricao in colunas:
        try:
            query = f"ALTER TABLE ordens_servico ADD COLUMN {nome} {tipo}"
            db.session.execute(text(query))
            print(f"✅ Coluna {nome} adicionada - {descricao}")
        except Exception as e:
            if "already exists" in str(e).lower() or "duplicate column" in str(e).lower():
                print(f"⚠️ Coluna {nome} já existe - {descricao}")
            else:
                print(f"❌ Erro ao adicionar coluna {nome}: {e}")

def adicionar_colunas_pmps():
    """Adiciona colunas necessárias à tabela pmps"""
    print("\n🔧 ADICIONANDO COLUNAS À TABELA PMPS")
    print("=" * 60)
    
    colunas = [
        ("hora_homem", "DECIMAL(10,2)", "Calculado automaticamente (pessoas × tempo)"),
        ("materiais", "TEXT", "Lista de materiais em JSON"),
        ("usuarios_responsaveis", "TEXT", "Lista de usuários responsáveis em JSON"),
        ("data_inicio_plano", "DATE", "Data de início do plano PMP"),
        ("data_fim_plano", "DATE", "Data de fim do plano (opcional)"),
        ("os_geradas_count", "INTEGER DEFAULT 0", "Contador de OS geradas")
    ]
    
    for nome, tipo, descricao in colunas:
        try:
            query = f"ALTER TABLE pmps ADD COLUMN {nome} {tipo}"
            db.session.execute(text(query))
            print(f"✅ Coluna {nome} adicionada - {descricao}")
        except Exception as e:
            if "already exists" in str(e).lower() or "duplicate column" in str(e).lower():
                print(f"⚠️ Coluna {nome} já existe - {descricao}")
            else:
                print(f"❌ Erro ao adicionar coluna {nome}: {e}")

def criar_indices():
    """Cria índices para melhor performance"""
    print("\n🔧 CRIANDO ÍNDICES PARA PERFORMANCE")
    print("=" * 60)
    
    indices = [
        ("idx_ordens_servico_pmp_id", "ordens_servico", "pmp_id", "Índice para FK pmp_id"),
        ("idx_ordens_servico_data_programada", "ordens_servico", "data_programada", "Índice para data programada"),
        ("idx_pmps_data_inicio", "pmps", "data_inicio_plano", "Índice para data de início")
    ]
    
    for nome_indice, tabela, coluna, descricao in indices:
        try:
            query = f"CREATE INDEX {nome_indice} ON {tabela} ({coluna})"
            db.session.execute(text(query))
            print(f"✅ Índice {nome_indice} criado - {descricao}")
        except Exception as e:
            if "already exists" in str(e).lower() or "duplicate" in str(e).lower():
                print(f"⚠️ Índice {nome_indice} já existe - {descricao}")
            else:
                print(f"❌ Erro ao criar índice {nome_indice}: {e}")

def verificar_tabelas():
    """Verifica se as tabelas necessárias existem"""
    print("\n🔍 VERIFICANDO TABELAS NECESSÁRIAS")
    print("=" * 60)
    
    tabelas = ["ordens_servico", "pmps", "user"]
    
    for tabela in tabelas:
        try:
            result = db.session.execute(text(f"SELECT COUNT(*) FROM {tabela} LIMIT 1"))
            count = result.scalar()
            print(f"✅ Tabela {tabela} existe e acessível")
        except Exception as e:
            print(f"❌ Problema com tabela {tabela}: {e}")
            return False
    
    return True

def main():
    """Função principal"""
    print("🚀 INICIANDO MIGRAÇÃO DO BANCO DE DADOS")
    print("Sistema PMP → OS - Adição de campos necessários")
    print("=" * 60)
    
    # Criar contexto da aplicação
    app = create_app()
    
    with app.app_context():
        try:
            # Verificar tabelas
            if not verificar_tabelas():
                print("❌ Erro: Tabelas necessárias não encontradas")
                return False
            
            # Adicionar colunas
            adicionar_colunas_ordens_servico()
            adicionar_colunas_pmps()
            
            # Criar índices
            criar_indices()
            
            # Commit das alterações
            db.session.commit()
            
            print("\n🎉 MIGRAÇÃO CONCLUÍDA COM SUCESSO!")
            print("=" * 60)
            print("✅ Todas as colunas foram adicionadas")
            print("✅ Índices criados para performance")
            print("✅ Sistema PMP → OS está pronto para uso")
            
            return True
            
        except Exception as e:
            print(f"\n❌ ERRO DURANTE A MIGRAÇÃO: {e}")
            db.session.rollback()
            return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)

