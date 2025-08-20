#!/usr/bin/env python3
"""
Script para investigar a estrutura do banco de dados
"""

import sys
import os

# Adicionar o diretório atual ao path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def debug_database_structure():
    """Investigar estrutura do banco de dados"""
    
    print("🔍 INVESTIGANDO ESTRUTURA DO BANCO DE DADOS")
    print("=" * 60)
    
    try:
        # Importar aplicação
        from app import create_app
        from models import db
        
        app = create_app()
        
        with app.app_context():
            print("📋 Listando todas as tabelas existentes:")
            
            from sqlalchemy import text
            
            # Listar todas as tabelas
            result = db.engine.execute(text("""
                SELECT table_name 
                FROM information_schema.tables 
                WHERE table_schema = 'public'
                ORDER BY table_name
            """))
            
            tabelas = []
            for row in result:
                tabelas.append(row[0])
                print(f"  📋 {row[0]}")
            
            print(f"\n📊 Total de tabelas: {len(tabelas)}")
            
            # Verificar se existe tabela de usuários
            print("\n🔍 Procurando tabela de usuários:")
            tabelas_usuarios = [t for t in tabelas if 'user' in t.lower()]
            
            if tabelas_usuarios:
                for tabela in tabelas_usuarios:
                    print(f"  ✅ Encontrada: {tabela}")
                    
                    # Mostrar estrutura da tabela
                    result = db.engine.execute(text(f"""
                        SELECT column_name, data_type, is_nullable
                        FROM information_schema.columns 
                        WHERE table_name = '{tabela}'
                        ORDER BY ordinal_position
                    """))
                    
                    print(f"    📋 Estrutura da tabela {tabela}:")
                    for row in result:
                        nullable = "NULL" if row[2] == "YES" else "NOT NULL"
                        print(f"      • {row[0]} | {row[1]} | {nullable}")
            else:
                print("  ❌ Nenhuma tabela de usuários encontrada")
            
            # Verificar tabelas relacionadas a equipamentos
            print("\n🔍 Tabelas relacionadas a equipamentos:")
            tabelas_equipamentos = [t for t in tabelas if any(palavra in t.lower() for palavra in ['equip', 'ativo', 'asset'])]
            
            for tabela in tabelas_equipamentos:
                print(f"  📋 {tabela}")
            
            # Verificar tabelas de plano mestre
            print("\n🔍 Tabelas relacionadas a plano mestre:")
            tabelas_plano = [t for t in tabelas if any(palavra in t.lower() for palavra in ['plano', 'atividade', 'mestre'])]
            
            for tabela in tabelas_plano:
                print(f"  📋 {tabela}")
            
            # Tentar importar modelos existentes
            print("\n🔍 Testando importação de modelos:")
            
            try:
                from models.user import User
                print("  ✅ models.user.User importado com sucesso")
                print(f"    Tabela: {User.__tablename__}")
            except Exception as e:
                print(f"  ❌ Erro ao importar models.user.User: {e}")
            
            try:
                from assets_models import Equipamento
                print("  ✅ assets_models.Equipamento importado com sucesso")
                print(f"    Tabela: {Equipamento.__tablename__}")
            except Exception as e:
                print(f"  ❌ Erro ao importar assets_models.Equipamento: {e}")
            
            try:
                from models.plano_mestre import AtividadePlanoMestre
                print("  ✅ models.plano_mestre.AtividadePlanoMestre importado com sucesso")
                print(f"    Tabela: {AtividadePlanoMestre.__tablename__}")
            except Exception as e:
                print(f"  ❌ Erro ao importar models.plano_mestre.AtividadePlanoMestre: {e}")
            
            print("\n✅ INVESTIGAÇÃO CONCLUÍDA")
            
            return tabelas
            
    except Exception as e:
        print(f"❌ Erro: {e}")
        import traceback
        traceback.print_exc()
        return []

if __name__ == '__main__':
    tabelas = debug_database_structure()
    if not tabelas:
        sys.exit(1)

