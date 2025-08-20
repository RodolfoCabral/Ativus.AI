#!/usr/bin/env python3
"""
Script para criar tabelas do sistema PMP
"""

import sys
import os

# Adicionar o diretório atual ao path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def create_pmp_tables():
    """Criar tabelas do sistema PMP"""
    
    print("🔧 CRIANDO TABELAS DO SISTEMA PMP")
    print("=" * 50)
    
    try:
        # Importar aplicação e modelos
        from app import create_app
        from models import db
        from models.pmp import PMP, AtividadePMP, HistoricoExecucaoPMP
        
        app = create_app()
        
        with app.app_context():
            print("📦 Criando tabelas...")
            
            # Criar tabelas
            db.create_all()
            
            print("✅ Tabelas criadas com sucesso!")
            
            # Verificar se as tabelas foram criadas
            from sqlalchemy import text
            
            tabelas_pmp = ['pmps', 'atividades_pmp', 'historico_execucao_pmp']
            
            print("\n📋 Verificando tabelas criadas:")
            
            for tabela in tabelas_pmp:
                try:
                    result = db.session.execute(text(f"SELECT COUNT(*) FROM {tabela}"))
                    count = result.fetchone()[0]
                    print(f"  ✅ {tabela} - {count} registros")
                except Exception as e:
                    print(f"  ❌ {tabela} - Erro: {str(e)}")
            
            print("\n🎯 ESTRUTURA DAS TABELAS:")
            
            # Mostrar estrutura das tabelas
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
                    print(f"  ❌ Erro ao verificar {tabela}: {e}")
            
            print("\n✅ SISTEMA PMP CONFIGURADO COM SUCESSO!")
            
            return True
            
    except Exception as e:
        print(f"❌ Erro: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == '__main__':
    success = create_pmp_tables()
    if not success:
        sys.exit(1)

