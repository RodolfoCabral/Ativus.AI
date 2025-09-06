"""
Script CORRIGIDO para migração do banco de dados
Versão que verifica se colunas existem antes de criar e trata transações adequadamente
"""

import os
import sys
from sqlalchemy import text, inspect

# Adicionar o diretório atual ao path para importar os modelos
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

try:
    from models import db
    from app import create_app
    print("✅ Modelos importados com sucesso")
except ImportError as e:
    print(f"❌ Erro ao importar modelos: {e}")
    sys.exit(1)

def verificar_coluna_existe(tabela, coluna):
    """Verifica se uma coluna existe na tabela"""
    try:
        inspector = inspect(db.engine)
        columns = inspector.get_columns(tabela)
        column_names = [col['name'] for col in columns]
        return coluna in column_names
    except Exception as e:
        print(f"❌ Erro ao verificar coluna {coluna} na tabela {tabela}: {e}")
        return False

def executar_comando_seguro(comando, descricao):
    """Executa um comando SQL de forma segura com commit individual"""
    try:
        # Usar uma nova transação para cada comando
        with db.engine.begin() as conn:
            conn.execute(text(comando))
        print(f"✅ {descricao}")
        return True
    except Exception as e:
        error_msg = str(e).lower()
        if "already exists" in error_msg or "duplicate" in error_msg:
            print(f"⚠️ {descricao} - já existe")
            return True
        else:
            print(f"❌ Erro em {descricao}: {e}")
            return False

def verificar_indice_existe(nome_indice):
    """Verifica se um índice existe"""
    try:
        with db.engine.begin() as conn:
            result = conn.execute(text("""
                SELECT indexname FROM pg_indexes 
                WHERE indexname = :index_name
            """), {'index_name': nome_indice})
            return result.fetchone() is not None
    except Exception:
        return False

def migrar_banco_dados():
    """Executa a migração completa do banco de dados"""
    
    print("\n🚀 INICIANDO MIGRAÇÃO CORRIGIDA DO BANCO DE DADOS")
    print("Sistema PMP → OS - Verificação e adição de campos")
    print("=" * 60)
    
    # Verificar se as tabelas existem
    print("\n🔍 VERIFICANDO TABELAS NECESSÁRIAS")
    print("=" * 60)
    
    try:
        inspector = inspect(db.engine)
        tabelas = inspector.get_table_names()
        
        tabelas_necessarias = ['ordens_servico', 'pmps', 'user']
        for tabela in tabelas_necessarias:
            if tabela in tabelas:
                print(f"✅ Tabela {tabela} existe")
            else:
                print(f"❌ Tabela {tabela} não encontrada")
                return False
                
    except Exception as e:
        print(f"❌ Erro ao verificar tabelas: {e}")
        return False
    
    # Migrar tabela ordens_servico
    print("\n🔧 VERIFICANDO/ADICIONANDO COLUNAS À TABELA ORDENS_SERVICO")
    print("=" * 60)
    
    colunas_os = [
        ("pmp_id", "INTEGER", "FK para tabela pmps"),
        ("data_proxima_geracao", "DATE", "Controle de frequência"),
        ("frequencia_origem", "VARCHAR(20)", "Tipo de frequência"),
        ("numero_sequencia", "INTEGER DEFAULT 1", "Contador de OS")
    ]
    
    sucesso_os = 0
    for coluna, tipo, descricao in colunas_os:
        if verificar_coluna_existe('ordens_servico', coluna):
            print(f"⚠️ Coluna {coluna} já existe - {descricao}")
            sucesso_os += 1
        else:
            comando = f"ALTER TABLE ordens_servico ADD COLUMN {coluna} {tipo}"
            if executar_comando_seguro(comando, f"Coluna {coluna} - {descricao}"):
                sucesso_os += 1
    
    # Migrar tabela pmps
    print("\n🔧 VERIFICANDO/ADICIONANDO COLUNAS À TABELA PMPS")
    print("=" * 60)
    
    colunas_pmps = [
        ("hora_homem", "DECIMAL(10,2)", "Horas-homem calculadas"),
        ("materiais", "TEXT", "Lista de materiais em JSON"),
        ("usuarios_responsaveis", "TEXT", "Lista de usuários em JSON"),
        ("data_inicio_plano", "DATE", "Data de início do plano"),
        ("data_fim_plano", "DATE", "Data de fim do plano"),
        ("os_geradas_count", "INTEGER DEFAULT 0", "Contador de OS geradas")
    ]
    
    sucesso_pmps = 0
    for coluna, tipo, descricao in colunas_pmps:
        if verificar_coluna_existe('pmps', coluna):
            print(f"⚠️ Coluna {coluna} já existe - {descricao}")
            sucesso_pmps += 1
        else:
            comando = f"ALTER TABLE pmps ADD COLUMN {coluna} {tipo}"
            if executar_comando_seguro(comando, f"Coluna {coluna} - {descricao}"):
                sucesso_pmps += 1
    
    # Criar índices para performance
    print("\n🔧 VERIFICANDO/CRIANDO ÍNDICES PARA PERFORMANCE")
    print("=" * 60)
    
    indices = [
        ("idx_ordens_servico_pmp_id", "CREATE INDEX idx_ordens_servico_pmp_id ON ordens_servico (pmp_id)", "Índice para FK pmp_id"),
        ("idx_ordens_servico_data_programada", "CREATE INDEX idx_ordens_servico_data_programada ON ordens_servico (data_programada)", "Índice para data_programada"),
        ("idx_pmps_data_inicio", "CREATE INDEX idx_pmps_data_inicio ON pmps (data_inicio_plano)", "Índice para data_inicio_plano")
    ]
    
    sucesso_indices = 0
    for nome_indice, comando, descricao in indices:
        if verificar_indice_existe(nome_indice):
            print(f"⚠️ Índice {nome_indice} já existe - {descricao}")
            sucesso_indices += 1
        else:
            if executar_comando_seguro(comando, f"Índice {nome_indice} - {descricao}"):
                sucesso_indices += 1
    
    # Resumo final
    print("\n🎉 RESUMO DA MIGRAÇÃO")
    print("=" * 60)
    print(f"📊 Colunas ordens_servico: {sucesso_os}/{len(colunas_os)} processadas")
    print(f"📊 Colunas pmps: {sucesso_pmps}/{len(colunas_pmps)} processadas")
    print(f"📊 Índices: {sucesso_indices}/{len(indices)} processados")
    
    total_operacoes = len(colunas_os) + len(colunas_pmps) + len(indices)
    total_sucesso = sucesso_os + sucesso_pmps + sucesso_indices
    
    if total_sucesso == total_operacoes:
        print("\n✅ MIGRAÇÃO CONCLUÍDA COM SUCESSO!")
        print("✅ Todas as colunas e índices estão disponíveis")
        print("✅ Sistema PMP → OS está pronto para uso")
        return True
    else:
        print(f"\n⚠️ MIGRAÇÃO PARCIAL: {total_sucesso}/{total_operacoes} operações bem-sucedidas")
        print("⚠️ Algumas operações falharam, mas o sistema pode funcionar")
        return False

def verificar_estrutura_final():
    """Verifica a estrutura final das tabelas"""
    print("\n🔍 VERIFICAÇÃO FINAL DA ESTRUTURA")
    print("=" * 60)
    
    try:
        inspector = inspect(db.engine)
        
        # Verificar ordens_servico
        print("\n📋 Estrutura da tabela ordens_servico:")
        columns_os = inspector.get_columns('ordens_servico')
        colunas_pmp = ['pmp_id', 'data_proxima_geracao', 'frequencia_origem', 'numero_sequencia']
        
        for coluna in colunas_pmp:
            encontrada = any(col['name'] == coluna for col in columns_os)
            status = "✅" if encontrada else "❌"
            print(f"  {status} {coluna}")
        
        # Verificar pmps
        print("\n📋 Estrutura da tabela pmps:")
        columns_pmps = inspector.get_columns('pmps')
        colunas_novas = ['hora_homem', 'materiais', 'usuarios_responsaveis', 'data_inicio_plano', 'data_fim_plano', 'os_geradas_count']
        
        for coluna in colunas_novas:
            encontrada = any(col['name'] == coluna for col in columns_pmps)
            status = "✅" if encontrada else "❌"
            print(f"  {status} {coluna}")
            
        return True
        
    except Exception as e:
        print(f"❌ Erro na verificação final: {e}")
        return False

if __name__ == "__main__":
    # Criar contexto da aplicação
    app = create_app()
    
    with app.app_context():
        try:
            # Executar migração
            sucesso_migracao = migrar_banco_dados()
            
            # Verificar estrutura final
            verificar_estrutura_final()
            
            if sucesso_migracao:
                print("\n🎉 MIGRAÇÃO FINALIZADA COM SUCESSO!")
                print("🚀 O sistema PMP → OS está pronto para uso")
            else:
                print("\n⚠️ MIGRAÇÃO FINALIZADA COM AVISOS")
                print("⚠️ Verifique os logs acima para detalhes")
                
        except Exception as e:
            print(f"\n❌ ERRO CRÍTICO NA MIGRAÇÃO: {e}")
            import traceback
            traceback.print_exc()
            sys.exit(1)

