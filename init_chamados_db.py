#!/usr/bin/env python3
"""
Script para inicializar a tabela de chamados no banco de dados
"""

import os
import sys
from app import create_app, db
from models.assets import Chamado

def init_chamados_table():
    """Inicializa a tabela de chamados no banco de dados"""
    
    app = create_app()
    
    with app.app_context():
        try:
            print("Iniciando criação da tabela de chamados...")
            
            # Criar apenas a tabela de chamados se não existir
            db.create_all()
            
            print("✅ Tabela de chamados criada com sucesso!")
            
            # Verificar se a tabela foi criada
            inspector = db.inspect(db.engine)
            tables = inspector.get_table_names()
            
            if 'chamados' in tables:
                print("✅ Tabela 'chamados' confirmada no banco de dados")
                
                # Mostrar estrutura da tabela
                columns = inspector.get_columns('chamados')
                print("\n📋 Estrutura da tabela 'chamados':")
                for column in columns:
                    print(f"  - {column['name']}: {column['type']}")
            else:
                print("❌ Tabela 'chamados' não foi encontrada")
                return False
            
            return True
            
        except Exception as e:
            print(f"❌ Erro ao criar tabela de chamados: {str(e)}")
            return False

def verify_chamados_table():
    """Verifica se a tabela de chamados existe e está correta"""
    
    app = create_app()
    
    with app.app_context():
        try:
            # Tentar fazer uma consulta simples
            count = Chamado.query.count()
            print(f"✅ Tabela de chamados está funcionando. Total de registros: {count}")
            return True
            
        except Exception as e:
            print(f"❌ Erro ao verificar tabela de chamados: {str(e)}")
            return False

if __name__ == '__main__':
    print("🚀 Inicializando sistema de chamados...")
    print("=" * 50)
    
    # Verificar se a tabela já existe
    if verify_chamados_table():
        print("ℹ️  Tabela de chamados já existe e está funcionando")
    else:
        print("📝 Criando tabela de chamados...")
        if init_chamados_table():
            print("\n🎉 Sistema de chamados inicializado com sucesso!")
        else:
            print("\n💥 Falha ao inicializar sistema de chamados")
            sys.exit(1)
    
    print("=" * 50)
    print("✅ Processo concluído!")

