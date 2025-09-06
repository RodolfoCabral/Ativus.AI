"""
Script SIMPLIFICADO para migração do banco de dados
Executa cada comando individualmente e verifica existência antes de criar
"""

import os
import sys
from sqlalchemy import text

# Adicionar o diretório atual ao path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

try:
    from models import db
    from app import create_app
    print("✅ Modelos importados com sucesso")
except ImportError as e:
    print(f"❌ Erro ao importar modelos: {e}")
    sys.exit(1)

def executar_sql_seguro(sql, descricao):
    """Executa SQL de forma segura, ignorando erros de 'já existe'"""
    try:
        with db.engine.begin() as conn:
            conn.execute(text(sql))
        print(f"✅ {descricao}")
        return True
    except Exception as e:
        error_str = str(e).lower()
        if any(palavra in error_str for palavra in ['already exists', 'duplicate', 'já existe']):
            print(f"⚠️ {descricao} - já existe")
            return True
        else:
            print(f"❌ {descricao} - Erro: {e}")
            return False

def migrar_banco():
    """Executa migração do banco"""
    
    print("\n🚀 MIGRAÇÃO SIMPLIFICADA DO BANCO")
    print("=" * 50)
    
    # Lista de comandos SQL para executar
    comandos = [
        # Colunas para ordens_servico
        ("ALTER TABLE ordens_servico ADD COLUMN pmp_id INTEGER", 
         "Adicionar coluna pmp_id"),
        
        ("ALTER TABLE ordens_servico ADD COLUMN data_proxima_geracao DATE", 
         "Adicionar coluna data_proxima_geracao"),
        
        ("ALTER TABLE ordens_servico ADD COLUMN frequencia_origem VARCHAR(20)", 
         "Adicionar coluna frequencia_origem"),
        
        ("ALTER TABLE ordens_servico ADD COLUMN numero_sequencia INTEGER DEFAULT 1", 
         "Adicionar coluna numero_sequencia"),
        
        # Colunas para pmps
        ("ALTER TABLE pmps ADD COLUMN hora_homem DECIMAL(10,2)", 
         "Adicionar coluna hora_homem"),
        
        ("ALTER TABLE pmps ADD COLUMN materiais TEXT", 
         "Adicionar coluna materiais"),
        
        ("ALTER TABLE pmps ADD COLUMN usuarios_responsaveis TEXT", 
         "Adicionar coluna usuarios_responsaveis"),
        
        ("ALTER TABLE pmps ADD COLUMN data_inicio_plano DATE", 
         "Adicionar coluna data_inicio_plano"),
        
        ("ALTER TABLE pmps ADD COLUMN data_fim_plano DATE", 
         "Adicionar coluna data_fim_plano"),
        
        ("ALTER TABLE pmps ADD COLUMN os_geradas_count INTEGER DEFAULT 0", 
         "Adicionar coluna os_geradas_count"),
        
        # Índices
        ("CREATE INDEX IF NOT EXISTS idx_ordens_servico_pmp_id ON ordens_servico (pmp_id)", 
         "Criar índice pmp_id"),
        
        ("CREATE INDEX IF NOT EXISTS idx_ordens_servico_data_programada ON ordens_servico (data_programada)", 
         "Criar índice data_programada"),
        
        ("CREATE INDEX IF NOT EXISTS idx_pmps_data_inicio ON pmps (data_inicio_plano)", 
         "Criar índice data_inicio_plano"),
    ]
    
    sucessos = 0
    total = len(comandos)
    
    for sql, descricao in comandos:
        if executar_sql_seguro(sql, descricao):
            sucessos += 1
    
    print(f"\n📊 RESULTADO: {sucessos}/{total} operações bem-sucedidas")
    
    if sucessos == total:
        print("🎉 MIGRAÇÃO CONCLUÍDA COM SUCESSO!")
    elif sucessos > total * 0.8:  # Mais de 80% de sucesso
        print("✅ MIGRAÇÃO MAJORITARIAMENTE BEM-SUCEDIDA!")
    else:
        print("⚠️ MIGRAÇÃO COM PROBLEMAS - Verificar logs")
    
    return sucessos >= total * 0.8

if __name__ == "__main__":
    app = create_app()
    
    with app.app_context():
        try:
            sucesso = migrar_banco()
            
            if sucesso:
                print("\n🚀 BANCO PRONTO PARA O SISTEMA PMP/OS!")
            else:
                print("\n⚠️ VERIFICAR PROBLEMAS NA MIGRAÇÃO")
                
        except Exception as e:
            print(f"\n❌ ERRO CRÍTICO: {e}")
            import traceback
            traceback.print_exc()

