#!/usr/bin/env python3
"""
Script para criar tabelas do Plano Mestre no banco de dados do Heroku
Execute este script no console do Heroku para criar as tabelas necessárias
"""

import os
import sys

def criar_tabelas_plano_mestre():
    """Criar todas as tabelas necessárias para o Plano Mestre"""
    
    print("🔧 Iniciando criação das tabelas do Plano Mestre...")
    
    try:
        # Importar aplicação e modelos
        from app import create_app
        from models import db
        
        # Importar modelos específicos do plano mestre
        from models.plano_mestre import PlanoMestre, AtividadePlanoMestre, HistoricoExecucaoPlano
        
        print("✅ Modelos importados com sucesso")
        
        # Criar aplicação Flask
        app = create_app()
        print("✅ Aplicação Flask criada")
        
        # Criar contexto da aplicação
        with app.app_context():
            print("🗄️ Criando tabelas no banco de dados...")
            
            # Criar todas as tabelas
            db.create_all()
            
            print("✅ Comando db.create_all() executado")
            
            # Verificar se as tabelas foram criadas
            inspector = db.inspect(db.engine)
            tabelas_existentes = inspector.get_table_names()
            
            print("\n📋 Tabelas existentes no banco de dados:")
            for tabela in sorted(tabelas_existentes):
                print(f"  ✓ {tabela}")
            
            # Verificar tabelas específicas do plano mestre
            tabelas_plano_mestre = [
                'planos_mestre',
                'atividades_plano_mestre', 
                'historico_execucao_plano'
            ]
            
            print("\n🔍 Verificando tabelas do Plano Mestre:")
            tabelas_criadas = []
            for tabela in tabelas_plano_mestre:
                if tabela in tabelas_existentes:
                    print(f"  ✅ {tabela} - CRIADA")
                    tabelas_criadas.append(tabela)
                else:
                    print(f"  ❌ {tabela} - NÃO ENCONTRADA")
            
            if len(tabelas_criadas) == len(tabelas_plano_mestre):
                print("\n🎉 SUCESSO! Todas as tabelas do Plano Mestre foram criadas!")
                
                # Testar inserção básica
                print("\n🧪 Testando inserção de dados...")
                
                # Criar um plano mestre de teste
                plano_teste = PlanoMestre(
                    equipamento_id=999999,  # ID de teste
                    nome="Plano Teste - Criação de Tabelas",
                    descricao="Plano criado para testar a estrutura do banco",
                    criado_por=1
                )
                
                db.session.add(plano_teste)
                db.session.commit()
                
                print("✅ Inserção de teste realizada com sucesso")
                
                # Remover dados de teste
                db.session.delete(plano_teste)
                db.session.commit()
                
                print("✅ Dados de teste removidos")
                print("\n🎯 BANCO DE DADOS PRONTO PARA USO!")
                
            else:
                print(f"\n⚠️ ATENÇÃO: Apenas {len(tabelas_criadas)} de {len(tabelas_plano_mestre)} tabelas foram criadas")
                print("Verifique se há erros nos modelos ou no banco de dados")
                
    except ImportError as e:
        print(f"❌ ERRO DE IMPORTAÇÃO: {e}")
        print("Verifique se todos os arquivos foram enviados para o Heroku:")
        print("  - models/plano_mestre.py")
        print("  - routes/plano_mestre.py") 
        print("  - app.py (atualizado)")
        
    except Exception as e:
        print(f"❌ ERRO GERAL: {e}")
        print("Detalhes do erro:")
        import traceback
        traceback.print_exc()
        
    print("\n" + "="*50)
    print("Script de criação de tabelas finalizado")
    print("="*50)

if __name__ == "__main__":
    criar_tabelas_plano_mestre()

