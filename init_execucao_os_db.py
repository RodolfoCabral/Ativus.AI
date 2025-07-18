#!/usr/bin/env python3
"""
Script para inicializar as tabelas de execução de OS no banco de dados
"""

import os
import sys
from datetime import datetime
from sqlalchemy import inspect

# Adicionar o diretório atual ao path para importar os módulos
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def init_execucao_tables():
    """Inicializar tabelas de execução de OS"""
    
    print("🚀 Inicializando tabelas de execução de OS...")
    print("=" * 50)
    
    try:
        # Importar app e modelos
        from app import create_app
        from assets_models import db, ExecucaoOS, MaterialUtilizado, MaterialEstoque
        
        # Criar aplicação
        app = create_app()
        
        with app.app_context():
            # Obter informações do banco
            database_url = app.config.get('DATABASE_URL', 'sqlite:///instance/ativus.db')
            print(f"Conectando ao banco de dados: {database_url}")
            
            # Verificar conexão
            try:
                inspector = inspect(db.engine)
                print("✅ Conexão com banco de dados estabelecida")
            except Exception as e:
                print(f"❌ Erro ao conectar com banco de dados: {e}")
                return False
            
            # Verificar e criar tabelas
            tabelas_criadas = []
            
            # Tabela de materiais de estoque
            if not inspector.has_table('materiais_estoque'):
                print("📦 Criando tabela 'materiais_estoque'...")
                try:
                    MaterialEstoque.__table__.create(db.engine)
                    tabelas_criadas.append('materiais_estoque')
                    print("✅ Tabela 'materiais_estoque' criada com sucesso!")
                except Exception as e:
                    print(f"❌ Erro ao criar tabela 'materiais_estoque': {e}")
                    return False
            else:
                print("ℹ️  Tabela 'materiais_estoque' já existe")
            
            # Tabela de execuções de OS
            if not inspector.has_table('execucoes_os'):
                print("⚙️  Criando tabela 'execucoes_os'...")
                try:
                    ExecucaoOS.__table__.create(db.engine)
                    tabelas_criadas.append('execucoes_os')
                    print("✅ Tabela 'execucoes_os' criada com sucesso!")
                except Exception as e:
                    print(f"❌ Erro ao criar tabela 'execucoes_os': {e}")
                    return False
            else:
                print("ℹ️  Tabela 'execucoes_os' já existe")
            
            # Tabela de materiais utilizados
            if not inspector.has_table('materiais_utilizados'):
                print("🔧 Criando tabela 'materiais_utilizados'...")
                try:
                    MaterialUtilizado.__table__.create(db.engine)
                    tabelas_criadas.append('materiais_utilizados')
                    print("✅ Tabela 'materiais_utilizados' criada com sucesso!")
                except Exception as e:
                    print(f"❌ Erro ao criar tabela 'materiais_utilizados': {e}")
                    return False
            else:
                print("ℹ️  Tabela 'materiais_utilizados' já existe")
            
            # Verificar se as tabelas foram criadas corretamente
            print("\n🔍 Verificando tabelas criadas...")
            inspector = inspect(db.engine)
            
            tabelas_verificadas = []
            for tabela in ['materiais_estoque', 'execucoes_os', 'materiais_utilizados']:
                if inspector.has_table(tabela):
                    tabelas_verificadas.append(tabela)
                    print(f"✅ Verificação: Tabela '{tabela}' existe")
                else:
                    print(f"❌ Verificação: Tabela '{tabela}' não encontrada")
            
            # Criar alguns materiais de estoque de exemplo (opcional)
            if 'materiais_estoque' in tabelas_criadas:
                print("\n📦 Criando materiais de estoque de exemplo...")
                try:
                    # Verificar se já existem materiais
                    count = MaterialEstoque.query.count()
                    if count == 0:
                        materiais_exemplo = [
                            MaterialEstoque(
                                nome="Óleo Lubrificante SAE 40",
                                codigo="OL-SAE40",
                                descricao="Óleo lubrificante para equipamentos industriais",
                                unidade="L",
                                valor_unitario=25.50,
                                quantidade_estoque=100.0,
                                estoque_minimo=20.0,
                                categoria="Lubrificantes",
                                fornecedor="Petrobras",
                                empresa="Empresa Exemplo",
                                usuario_criacao="admin"
                            ),
                            MaterialEstoque(
                                nome="Rolamento 6205",
                                codigo="ROL-6205",
                                descricao="Rolamento rígido de esferas",
                                unidade="UN",
                                valor_unitario=45.00,
                                quantidade_estoque=50.0,
                                estoque_minimo=10.0,
                                categoria="Rolamentos",
                                fornecedor="SKF",
                                empresa="Empresa Exemplo",
                                usuario_criacao="admin"
                            ),
                            MaterialEstoque(
                                nome="Parafuso M8x20",
                                codigo="PAR-M8X20",
                                descricao="Parafuso sextavado M8 x 20mm",
                                unidade="UN",
                                valor_unitario=2.50,
                                quantidade_estoque=200.0,
                                estoque_minimo=50.0,
                                categoria="Parafusos",
                                fornecedor="Fixadores ABC",
                                empresa="Empresa Exemplo",
                                usuario_criacao="admin"
                            ),
                            MaterialEstoque(
                                nome="Graxa Multiuso",
                                codigo="GRX-MULTI",
                                descricao="Graxa multiuso para rolamentos",
                                unidade="KG",
                                valor_unitario=18.00,
                                quantidade_estoque=25.0,
                                estoque_minimo=5.0,
                                categoria="Lubrificantes",
                                fornecedor="Shell",
                                empresa="Empresa Exemplo",
                                usuario_criacao="admin"
                            )
                        ]
                        
                        for material in materiais_exemplo:
                            db.session.add(material)
                        
                        db.session.commit()
                        print(f"✅ {len(materiais_exemplo)} materiais de exemplo criados!")
                    else:
                        print(f"ℹ️  Já existem {count} materiais no estoque")
                        
                except Exception as e:
                    print(f"⚠️  Erro ao criar materiais de exemplo: {e}")
                    db.session.rollback()
            
            print("\n" + "=" * 50)
            if tabelas_criadas:
                print(f"🎉 Inicialização concluída! {len(tabelas_criadas)} tabelas criadas:")
                for tabela in tabelas_criadas:
                    print(f"   ✅ {tabela}")
            else:
                print("ℹ️  Todas as tabelas já existiam - nenhuma criação necessária")
            
            print(f"🎯 Total de tabelas verificadas: {len(tabelas_verificadas)}/3")
            print("=" * 50)
            
            return True
            
    except ImportError as e:
        print(f"❌ Erro de importação: {e}")
        print("Certifique-se de que todos os módulos estão instalados")
        return False
    except Exception as e:
        print(f"❌ Erro inesperado: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == '__main__':
    try:
        success = init_execucao_tables()
        if success:
            print("✅ Script executado com sucesso!")
            sys.exit(0)
        else:
            print("❌ Script falhou!")
            sys.exit(1)
    except KeyboardInterrupt:
        print("\n⚠️  Script interrompido pelo usuário")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Erro fatal: {e}")
        sys.exit(1)

