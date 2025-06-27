#!/usr/bin/env python3
"""
Script para inicializar as tabelas de ativos no banco de dados
"""

import os
import sys
from app import create_app, db
from models.assets import Filial, Setor, Equipamento, Categoria

def init_assets_tables():
    """Inicializar tabelas de ativos"""
    app = create_app()
    
    with app.app_context():
        try:
            # Criar tabelas de ativos
            print("Criando tabelas de ativos...")
            
            # Importar modelos para garantir que sejam registrados
            from models.assets import Filial, Setor, Equipamento, Categoria
            
            # Criar todas as tabelas
            db.create_all()
            
            print("✅ Tabelas de ativos criadas com sucesso!")
            print("Tabelas criadas:")
            print("- filiais")
            print("- setores") 
            print("- equipamentos")
            print("- categorias")
            
        except Exception as e:
            print(f"❌ Erro ao criar tabelas: {e}")
            return False
    
    return True

if __name__ == '__main__':
    print("🚀 Inicializando tabelas de ativos...")
    success = init_assets_tables()
    
    if success:
        print("\n🎉 Inicialização concluída com sucesso!")
    else:
        print("\n💥 Falha na inicialização!")
        sys.exit(1)

