#!/usr/bin/env python3
"""
Script final para criar tabelas do sistema PMP
Versão corrigida para SQLAlchemy 2.x
"""

import sys
import os

# Adicionar o diretório do projeto ao path
sys.path.insert(0, '/home/ubuntu/SaaS Ativus')

def create_pmp_tables():
    """Criar todas as tabelas do sistema PMP"""
    print("🔧 CRIANDO TABELAS DO SISTEMA PMP")
    print("=" * 50)
    
    try:
        # Importar aplicação
        from app import create_app
        from models import db
        from models.pmp import PMP, AtividadePMP, HistoricoExecucaoPMP
        
        # Criar aplicação
        app = create_app()
        
        with app.app_context():
            print("📦 Criando tabelas...")
            
            # Criar todas as tabelas
            db.create_all()
            print("✅ Tabelas criadas com sucesso!")
            
            # Verificar se as tabelas foram criadas
            print("\n📋 Verificando tabelas criadas:")
            
            from sqlalchemy import text
            
            tabelas_pmp = ['pmps', 'atividades_pmp', 'historico_execucao_pmp']
            
            for tabela in tabelas_pmp:
                try:
                    # Usar SQLAlchemy 2.x syntax
                    result = db.session.execute(text(f"SELECT COUNT(*) FROM {tabela}"))
                    count = result.fetchone()[0]
                    print(f"  ✅ {tabela} - {count} registros")
                except Exception as e:
                    print(f"  ❌ {tabela} - Erro: {str(e)}")
            
            # Mostrar estrutura das tabelas
            print("\n🎯 ESTRUTURA DAS TABELAS:")
            for tabela in tabelas_pmp:
                try:
                    result = db.session.execute(text(f"""
                        SELECT column_name, data_type, is_nullable 
                        FROM information_schema.columns 
                        WHERE table_name = '{tabela}'
                        ORDER BY ordinal_position
                    """))
                    
                    print(f"\n📋 Tabela: {tabela}")
                    for row in result:
                        nullable = "NULL" if row[2] == "YES" else "NOT NULL"
                        print(f"  • {row[0]} | {row[1]} | {nullable}")
                        
                except Exception as e:
                    print(f"  ❌ Erro ao verificar {tabela}: {str(e)}")
            
            print("\n✅ SISTEMA PMP CONFIGURADO COM SUCESSO!")
            
    except Exception as e:
        print(f"❌ Erro ao criar tabelas: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    return True

if __name__ == "__main__":
    success = create_pmp_tables()
    sys.exit(0 if success else 1)

