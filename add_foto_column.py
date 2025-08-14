#!/usr/bin/env python3
"""
Script para adicionar a coluna 'foto' à tabela equipamentos
"""

import os
import sys
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import text

# Configurar Flask app
app = Flask(__name__)

# Configurar banco de dados
DATABASE_URL = os.environ.get('DATABASE_URL')
if not DATABASE_URL:
    print("❌ Erro: DATABASE_URL não encontrada nas variáveis de ambiente")
    sys.exit(1)

# Corrigir URL do PostgreSQL se necessário
if DATABASE_URL.startswith('postgres://'):
    DATABASE_URL = DATABASE_URL.replace('postgres://', 'postgresql://', 1)

app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE_URL
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Inicializar SQLAlchemy
db = SQLAlchemy(app)

def add_foto_column():
    """Adicionar coluna foto à tabela equipamentos"""
    try:
        with app.app_context():
            # Verificar se a coluna já existe
            result = db.engine.execute(text("""
                SELECT column_name 
                FROM information_schema.columns 
                WHERE table_name = 'equipamentos' 
                AND column_name = 'foto'
            """))
            
            if result.fetchone():
                print("✅ Coluna 'foto' já existe na tabela equipamentos")
                return True
            
            # Adicionar a coluna
            print("📝 Adicionando coluna 'foto' à tabela equipamentos...")
            db.engine.execute(text("""
                ALTER TABLE equipamentos 
                ADD COLUMN foto VARCHAR(255)
            """))
            
            print("✅ Coluna 'foto' adicionada com sucesso!")
            
            # Verificar se foi adicionada
            result = db.engine.execute(text("""
                SELECT column_name, data_type, is_nullable
                FROM information_schema.columns 
                WHERE table_name = 'equipamentos' 
                AND column_name = 'foto'
            """))
            
            row = result.fetchone()
            if row:
                print(f"✅ Verificação: {row[0]} | {row[1]} | nullable: {row[2]}")
                return True
            else:
                print("❌ Erro: Coluna não foi criada corretamente")
                return False
                
    except Exception as e:
        print(f"❌ Erro ao adicionar coluna: {str(e)}")
        return False

def verify_table_structure():
    """Verificar estrutura atual da tabela equipamentos"""
    try:
        with app.app_context():
            print("\n📋 Estrutura atual da tabela equipamentos:")
            result = db.engine.execute(text("""
                SELECT column_name, data_type, is_nullable, column_default
                FROM information_schema.columns 
                WHERE table_name = 'equipamentos'
                ORDER BY ordinal_position
            """))
            
            for row in result:
                nullable = "NULL" if row[2] == "YES" else "NOT NULL"
                default = f" DEFAULT {row[3]}" if row[3] else ""
                print(f"  • {row[0]} | {row[1]} | {nullable}{default}")
            
            return True
    except Exception as e:
        print(f"❌ Erro ao verificar estrutura: {str(e)}")
        return False

if __name__ == '__main__':
    print("🔧 ADICIONANDO COLUNA FOTO À TABELA EQUIPAMENTOS")
    print("=" * 50)
    
    # Verificar estrutura atual
    verify_table_structure()
    
    # Adicionar coluna
    if add_foto_column():
        print("\n✅ MIGRAÇÃO CONCLUÍDA COM SUCESSO!")
        
        # Verificar estrutura final
        verify_table_structure()
    else:
        print("\n❌ FALHA NA MIGRAÇÃO!")
        sys.exit(1)

