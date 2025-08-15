#!/usr/bin/env python3
"""
Script para adicionar a coluna 'foto' à tabela equipamentos
Usa a configuração existente da aplicação Flask
"""

import sys
import os

# Adicionar o diretório atual ao path para importar módulos
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    from app import create_app
    from models import db
    from sqlalchemy import text
    
    def add_foto_column():
        """Adicionar coluna foto à tabela equipamentos"""
        try:
            # Criar app Flask
            app = create_app()
            
            with app.app_context():
                print("🔧 ADICIONANDO COLUNA FOTO À TABELA EQUIPAMENTOS")
                print("=" * 50)
                
                # Verificar se a coluna já existe
                print("📋 Verificando se coluna 'foto' já existe...")
                result = db.engine.execute(text("""
                    SELECT column_name 
                    FROM information_schema.columns 
                    WHERE table_name = 'equipamentos' 
                    AND column_name = 'foto'
                """))
                
                if result.fetchone():
                    print("✅ Coluna 'foto' já existe na tabela equipamentos")
                    return True
                
                # Verificar se tabela equipamentos existe
                print("📋 Verificando se tabela equipamentos existe...")
                result = db.engine.execute(text("""
                    SELECT table_name 
                    FROM information_schema.tables 
                    WHERE table_name = 'equipamentos'
                """))
                
                if not result.fetchone():
                    print("❌ Erro: Tabela 'equipamentos' não encontrada")
                    return False
                
                # Adicionar a coluna
                print("📝 Adicionando coluna 'foto' à tabela equipamentos...")
                db.engine.execute(text("""
                    ALTER TABLE equipamentos 
                    ADD COLUMN foto VARCHAR(255)
                """))
                
                print("✅ Coluna 'foto' adicionada com sucesso!")
                
                # Verificar se foi adicionada
                print("🔍 Verificando se coluna foi criada...")
                result = db.engine.execute(text("""
                    SELECT column_name, data_type, is_nullable
                    FROM information_schema.columns 
                    WHERE table_name = 'equipamentos' 
                    AND column_name = 'foto'
                """))
                
                row = result.fetchone()
                if row:
                    print(f"✅ Verificação: {row[0]} | {row[1]} | nullable: {row[2]}")
                    
                    # Mostrar estrutura final da tabela
                    print("\n📋 Estrutura final da tabela equipamentos:")
                    result = db.engine.execute(text("""
                        SELECT column_name, data_type, is_nullable
                        FROM information_schema.columns 
                        WHERE table_name = 'equipamentos'
                        ORDER BY ordinal_position
                    """))
                    
                    for row in result:
                        nullable = "NULL" if row[2] == "YES" else "NOT NULL"
                        print(f"  • {row[0]} | {row[1]} | {nullable}")
                    
                    print("\n✅ MIGRAÇÃO CONCLUÍDA COM SUCESSO!")
                    return True
                else:
                    print("❌ Erro: Coluna não foi criada corretamente")
                    return False
                    
        except Exception as e:
            print(f"❌ Erro ao adicionar coluna: {str(e)}")
            print(f"Detalhes do erro: {type(e).__name__}")
            return False
    
    if __name__ == '__main__':
        success = add_foto_column()
        if not success:
            sys.exit(1)
            
except ImportError as e:
    print(f"❌ Erro ao importar módulos: {e}")
    print("Certifique-se de que está executando no diretório correto da aplicação")
    sys.exit(1)
except Exception as e:
    print(f"❌ Erro geral: {e}")
    sys.exit(1)

