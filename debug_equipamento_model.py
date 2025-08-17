#!/usr/bin/env python3
"""
Script de diagnóstico para verificar o modelo Equipamento
"""

import sys
import os

# Adicionar o diretório atual ao path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def debug_equipamento_model():
    """Diagnosticar o modelo Equipamento"""
    
    print("🔍 DIAGNÓSTICO DO MODELO EQUIPAMENTO")
    print("=" * 50)
    
    try:
        # Verificar importação da aplicação
        print("📦 Importando aplicação...")
        from app import create_app
        print("✅ App importado com sucesso")
        
        # Verificar importação dos modelos
        print("📦 Importando modelos...")
        from models import db
        print("✅ DB importado com sucesso")
        
        # Tentar importar modelo de assets
        try:
            from models.assets import Equipamento
            print("✅ Modelo Equipamento importado de models.assets")
            equipamento_source = "models.assets"
        except ImportError:
            try:
                from assets_models import Equipamento
                print("✅ Modelo Equipamento importado de assets_models")
                equipamento_source = "assets_models"
            except ImportError:
                print("❌ Erro: Não foi possível importar modelo Equipamento")
                return False
        
        # Criar contexto da aplicação
        app = create_app()
        with app.app_context():
            
            # Verificar colunas do modelo
            print(f"\n📋 Analisando modelo Equipamento de {equipamento_source}:")
            
            # Verificar atributos da classe
            print("🔍 Atributos da classe Equipamento:")
            for attr_name in dir(Equipamento):
                if not attr_name.startswith('_') and hasattr(getattr(Equipamento, attr_name), 'type'):
                    attr = getattr(Equipamento, attr_name)
                    print(f"  • {attr_name}: {type(attr.type).__name__}")
            
            # Verificar se campo foto existe
            if hasattr(Equipamento, 'foto'):
                print("✅ Campo 'foto' encontrado no modelo")
                foto_attr = getattr(Equipamento, 'foto')
                print(f"  Tipo: {type(foto_attr.type).__name__}")
                print(f"  Nullable: {foto_attr.nullable}")
            else:
                print("❌ Campo 'foto' NÃO encontrado no modelo")
            
            # Verificar tabela no banco
            print("\n🗄️ Verificando tabela no banco de dados:")
            try:
                from sqlalchemy import text
                result = db.engine.execute(text("""
                    SELECT column_name, data_type, is_nullable
                    FROM information_schema.columns 
                    WHERE table_name = 'equipamentos'
                    ORDER BY ordinal_position
                """))
                
                print("📋 Colunas na tabela equipamentos:")
                foto_exists_in_db = False
                for row in result:
                    nullable = "NULL" if row[2] == "YES" else "NOT NULL"
                    print(f"  • {row[0]} | {row[1]} | {nullable}")
                    if row[0] == 'foto':
                        foto_exists_in_db = True
                
                if foto_exists_in_db:
                    print("✅ Coluna 'foto' existe no banco de dados")
                else:
                    print("❌ Coluna 'foto' NÃO existe no banco de dados")
                
            except Exception as e:
                print(f"❌ Erro ao verificar banco: {e}")
            
            # Tentar criar instância de teste
            print("\n🧪 Testando criação de instância:")
            try:
                # Teste sem foto
                test_eq = Equipamento(
                    tag="TEST001",
                    descricao="Teste",
                    setor_id=1,
                    empresa="Teste",
                    usuario_criacao="teste@teste.com"
                )
                print("✅ Instância criada sem foto")
                
                # Teste com foto
                test_eq_foto = Equipamento(
                    tag="TEST002",
                    descricao="Teste com foto",
                    setor_id=1,
                    foto="/test/path.jpg",
                    empresa="Teste",
                    usuario_criacao="teste@teste.com"
                )
                print("✅ Instância criada com foto")
                
            except Exception as e:
                print(f"❌ Erro ao criar instância: {e}")
                print(f"Tipo do erro: {type(e).__name__}")
            
            # Verificar método to_dict
            print("\n📄 Verificando método to_dict:")
            try:
                test_dict = test_eq.to_dict()
                if 'foto' in test_dict:
                    print("✅ Campo 'foto' incluído no to_dict")
                else:
                    print("❌ Campo 'foto' NÃO incluído no to_dict")
            except Exception as e:
                print(f"❌ Erro no to_dict: {e}")
        
        print("\n✅ DIAGNÓSTICO CONCLUÍDO")
        return True
        
    except Exception as e:
        print(f"❌ Erro geral: {e}")
        print(f"Tipo do erro: {type(e).__name__}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == '__main__':
    success = debug_equipamento_model()
    if not success:
        sys.exit(1)

