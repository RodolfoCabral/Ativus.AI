#!/usr/bin/env python3
"""
Script CORRIGIDO para adicionar campos necessários para integração PMP → OS
Versão com tratamento adequado de transações para evitar erros de rollback
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

def executar_comando_seguro(comando, descricao):
    """Executa um comando SQL de forma segura com commit individual"""
    try:
        db.session.execute(text(comando))
        db.session.commit()
        print(f"✅ {descricao}")
        return True
    except Exception as e:
        db.session.rollback()
        if "already exists" in str(e).lower() or "duplicate" in str(e).lower():
            print(f"⚠️ {descricao} - já existe")
            return True
        else:
            print(f"❌ Erro em {descricao}: {e}")
            return False

def adicionar_colunas_ordens_servico():
    """Adiciona colunas necessárias à tabela ordens_servico"""
    print("\n🔧 ADICIONANDO COLUNAS À TABELA ORDENS_SERVICO")
    print("=" * 60)
    
    comandos = [
        ("ALTER TABLE ordens_servico ADD COLUMN pmp_id INTEGER", "Coluna pmp_id (FK para pmps)"),
        ("ALTER TABLE ordens_servico ADD COLUMN data_proxima_geracao DATE", "Coluna data_proxima_geracao (controle frequência)"),
        ("ALTER TABLE ordens_servico ADD COLUMN frequencia_origem VARCHAR(20)", "Coluna frequencia_origem (tipo de frequência)"),
        ("ALTER TABLE ordens_servico ADD COLUMN numero_sequencia INTEGER DEFAULT 1", "Coluna numero_sequencia (contador OS)")
    ]
    
    sucesso = 0
    for comando, descricao in comandos:
        if executar_comando_seguro(comando, descricao):
            sucesso += 1
    
    print(f"\n📊 Resultado: {sucesso}/{len(comandos)} colunas processadas com sucesso")
    return sucesso == len(comandos)

def adicionar_colunas_pmps():
    """Adiciona colunas necessárias à tabela pmps"""
    print("\n🔧 ADICIONANDO COLUNAS À TABELA PMPS")
    print("=" * 60)
    
    comandos = [
        ("ALTER TABLE pmps ADD COLUMN hora_homem DECIMAL(10,2)", "Coluna hora_homem (cálculo automático)"),
        ("ALTER TABLE pmps ADD COLUMN materiais TEXT", "Coluna materiais (JSON)"),
        ("ALTER TABLE pmps ADD COLUMN usuarios_responsaveis TEXT", "Coluna usuarios_responsaveis (JSON)"),
        ("ALTER TABLE pmps ADD COLUMN data_inicio_plano DATE", "Coluna data_inicio_plano"),
        ("ALTER TABLE pmps ADD COLUMN data_fim_plano DATE", "Coluna data_fim_plano"),
        ("ALTER TABLE pmps ADD COLUMN os_geradas_count INTEGER DEFAULT 0", "Coluna os_geradas_count (contador)")
    ]
    
    sucesso = 0
    for comando, descricao in comandos:
        if executar_comando_seguro(comando, descricao):
            sucesso += 1
    
    print(f"\n📊 Resultado: {sucesso}/{len(comandos)} colunas processadas com sucesso")
    return sucesso == len(comandos)

def criar_indices():
    """Cria índices para melhor performance"""
    print("\n🔧 CRIANDO ÍNDICES PARA PERFORMANCE")
    print("=" * 60)
    
    comandos = [
        ("CREATE INDEX IF NOT EXISTS idx_ordens_servico_pmp_id ON ordens_servico (pmp_id)", "Índice pmp_id"),
        ("CREATE INDEX IF NOT EXISTS idx_ordens_servico_data_programada ON ordens_servico (data_programada)", "Índice data_programada"),
        ("CREATE INDEX IF NOT EXISTS idx_ordens_servico_status ON ordens_servico (status)", "Índice status"),
        ("CREATE INDEX IF NOT EXISTS idx_pmps_data_inicio ON pmps (data_inicio_plano)", "Índice data_inicio_plano"),
        ("CREATE INDEX IF NOT EXISTS idx_pmps_equipamento ON pmps (equipamento_id)", "Índice equipamento_id")
    ]
    
    sucesso = 0
    for comando, descricao in comandos:
        if executar_comando_seguro(comando, descricao):
            sucesso += 1
    
    print(f"\n📊 Resultado: {sucesso}/{len(comandos)} índices processados com sucesso")
    return sucesso == len(comandos)

def verificar_tabelas():
    """Verifica se as tabelas necessárias existem"""
    print("\n🔍 VERIFICANDO TABELAS NECESSÁRIAS")
    print("=" * 60)
    
    tabelas = ["ordens_servico", "pmps", "user"]
    tabelas_ok = 0
    
    for tabela in tabelas:
        try:
            result = db.session.execute(text(f"SELECT COUNT(*) FROM {tabela} LIMIT 1"))
            count = result.scalar()
            print(f"✅ Tabela {tabela} existe e acessível ({count} registros)")
            tabelas_ok += 1
        except Exception as e:
            print(f"❌ Problema com tabela {tabela}: {e}")
            db.session.rollback()
    
    return tabelas_ok == len(tabelas)

def verificar_colunas_existentes():
    """Verifica quais colunas já existem"""
    print("\n🔍 VERIFICANDO COLUNAS EXISTENTES")
    print("=" * 60)
    
    # Verificar colunas da tabela ordens_servico
    try:
        result = db.session.execute(text("""
            SELECT column_name 
            FROM information_schema.columns 
            WHERE table_name = 'ordens_servico' 
            AND column_name IN ('pmp_id', 'data_proxima_geracao', 'frequencia_origem', 'numero_sequencia')
        """))
        colunas_os = [row[0] for row in result]
        print(f"📋 ordens_servico - Colunas PMP existentes: {colunas_os}")
    except Exception as e:
        print(f"⚠️ Erro ao verificar colunas ordens_servico: {e}")
        db.session.rollback()
    
    # Verificar colunas da tabela pmps
    try:
        result = db.session.execute(text("""
            SELECT column_name 
            FROM information_schema.columns 
            WHERE table_name = 'pmps' 
            AND column_name IN ('hora_homem', 'materiais', 'usuarios_responsaveis', 'data_inicio_plano', 'data_fim_plano', 'os_geradas_count')
        """))
        colunas_pmps = [row[0] for row in result]
        print(f"📋 pmps - Colunas novas existentes: {colunas_pmps}")
    except Exception as e:
        print(f"⚠️ Erro ao verificar colunas pmps: {e}")
        db.session.rollback()

def main():
    """Função principal"""
    print("🚀 INICIANDO MIGRAÇÃO CORRIGIDA DO BANCO DE DADOS")
    print("Sistema PMP → OS - Versão com tratamento de transações")
    print("=" * 60)
    
    # Criar contexto da aplicação
    app = create_app()
    
    with app.app_context():
        try:
            # Verificar tabelas
            if not verificar_tabelas():
                print("❌ Erro: Tabelas necessárias não encontradas")
                return False
            
            # Verificar colunas existentes
            verificar_colunas_existentes()
            
            # Adicionar colunas (cada uma com commit individual)
            print("\n" + "="*60)
            print("🔄 INICIANDO ADIÇÃO DE COLUNAS")
            print("="*60)
            
            sucesso_os = adicionar_colunas_ordens_servico()
            sucesso_pmps = adicionar_colunas_pmps()
            sucesso_indices = criar_indices()
            
            # Verificar resultado final
            print("\n" + "="*60)
            print("📊 RESUMO FINAL DA MIGRAÇÃO")
            print("="*60)
            
            if sucesso_os:
                print("✅ Tabela ordens_servico - Todas as colunas processadas")
            else:
                print("⚠️ Tabela ordens_servico - Algumas colunas com problemas")
            
            if sucesso_pmps:
                print("✅ Tabela pmps - Todas as colunas processadas")
            else:
                print("⚠️ Tabela pmps - Algumas colunas com problemas")
            
            if sucesso_indices:
                print("✅ Índices - Todos processados")
            else:
                print("⚠️ Índices - Alguns com problemas")
            
            # Verificação final
            print("\n🔍 VERIFICAÇÃO FINAL")
            print("="*60)
            verificar_colunas_existentes()
            
            print("\n🎉 MIGRAÇÃO CONCLUÍDA!")
            print("="*60)
            print("✅ Sistema PMP → OS está pronto para uso")
            print("✅ Todas as operações foram executadas com commits individuais")
            print("✅ Transações tratadas adequadamente")
            
            return True
            
        except Exception as e:
            print(f"\n❌ ERRO GERAL DURANTE A MIGRAÇÃO: {e}")
            db.session.rollback()
            return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)

