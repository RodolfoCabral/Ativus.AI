#!/usr/bin/env python3
"""
Script para adicionar colunas faltantes na tabela atividades_pmp
"""

import sys
import os

# Adicionar o diretório do projeto ao path
sys.path.insert(0, '/home/ubuntu/SaaS Ativus')

def adicionar_colunas_faltantes():
    """Adicionar colunas faltantes na tabela atividades_pmp"""
    print("🔧 ADICIONANDO COLUNAS FALTANTES NA TABELA ATIVIDADES_PMP")
    print("=" * 65)
    
    try:
        from app import create_app
        from models import db
        from sqlalchemy import text
        
        app = create_app()
        
        with app.app_context():
            print("1️⃣ VERIFICANDO COLUNAS EXISTENTES...")
            
            try:
                # Verificar colunas existentes
                result = db.session.execute(text("""
                    SELECT column_name
                    FROM information_schema.columns 
                    WHERE table_name = 'atividades_pmp'
                    ORDER BY ordinal_position;
                """))
                
                colunas_existentes = [row[0] for row in result.fetchall()]
                print(f"  📋 Colunas existentes: {', '.join(colunas_existentes)}")
                
            except Exception as e:
                print(f"  ❌ Erro ao verificar colunas: {e}")
                return False
            
            print("\n2️⃣ DEFININDO COLUNAS NECESSÁRIAS...")
            
            # Colunas que o modelo AtividadePMP precisa
            colunas_necessarias = {
                'descricao': 'TEXT NOT NULL DEFAULT \'\'',
                'oficina': 'VARCHAR(100)',
                'frequencia': 'VARCHAR(100)',
                'tipo_manutencao': 'VARCHAR(100)',
                'conjunto': 'VARCHAR(100)',
                'ponto_controle': 'VARCHAR(100)',
                'valor_frequencia': 'INTEGER',
                'condicao': 'VARCHAR(50)',
                'ordem': 'INTEGER DEFAULT 1',
                'status': 'VARCHAR(20) DEFAULT \'ativo\'',
                'criado_em': 'TIMESTAMP DEFAULT CURRENT_TIMESTAMP'
            }
            
            # Identificar colunas faltando
            colunas_faltando = {}
            for coluna, definicao in colunas_necessarias.items():
                if coluna not in colunas_existentes:
                    colunas_faltando[coluna] = definicao
                    print(f"  ❌ {coluna} - FALTANDO")
                else:
                    print(f"  ✅ {coluna} - OK")
            
            if not colunas_faltando:
                print("\n✅ TODAS AS COLUNAS JÁ EXISTEM!")
                return True
            
            print(f"\n3️⃣ ADICIONANDO {len(colunas_faltando)} COLUNAS FALTANTES...")
            
            # Executar comandos ALTER TABLE
            for coluna, definicao in colunas_faltando.items():
                try:
                    comando = f"ALTER TABLE atividades_pmp ADD COLUMN {coluna} {definicao};"
                    print(f"  🔧 Executando: {comando}")
                    
                    db.session.execute(text(comando))
                    print(f"  ✅ Coluna {coluna} adicionada com sucesso!")
                    
                except Exception as e:
                    print(f"  ❌ Erro ao adicionar coluna {coluna}: {e}")
                    # Continuar com as outras colunas
                    continue
            
            # Commit das alterações
            try:
                db.session.commit()
                print("\n✅ TODAS AS ALTERAÇÕES FORAM SALVAS!")
            except Exception as e:
                print(f"\n❌ Erro ao salvar alterações: {e}")
                db.session.rollback()
                return False
            
            print("\n4️⃣ VERIFICAÇÃO FINAL...")
            
            # Verificar estrutura final
            try:
                result = db.session.execute(text("""
                    SELECT column_name, data_type, is_nullable, column_default
                    FROM information_schema.columns 
                    WHERE table_name = 'atividades_pmp'
                    ORDER BY ordinal_position;
                """))
                
                colunas_finais = result.fetchall()
                print(f"  📋 Tabela agora tem {len(colunas_finais)} colunas:")
                print("     COLUNA                | TIPO           | NULL | DEFAULT")
                print("     " + "-" * 60)
                
                for coluna in colunas_finais:
                    nome, tipo, nullable, default = coluna
                    null_str = "YES" if nullable == "YES" else "NO"
                    default_str = str(default) if default else "-"
                    print(f"     {nome:<20} | {tipo:<14} | {null_str:<4} | {default_str}")
                
                return True
                
            except Exception as e:
                print(f"  ❌ Erro na verificação final: {e}")
                return False
                
    except Exception as e:
        print(f"❌ Erro geral: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Função principal"""
    print("🚀 SCRIPT DE CORREÇÃO DA TABELA ATIVIDADES_PMP")
    print("Este script adiciona as colunas faltantes na tabela atividades_pmp")
    print("para corrigir o erro: column 'descricao' does not exist")
    print()
    
    success = adicionar_colunas_faltantes()
    
    if success:
        print("\n🎉 CORREÇÃO CONCLUÍDA COM SUCESSO!")
        print("   A tabela atividades_pmp agora tem todas as colunas necessárias.")
        print("   Você pode testar a geração de PMPs novamente.")
    else:
        print("\n❌ CORREÇÃO FALHOU!")
        print("   Verifique os erros acima e tente novamente.")
    
    return success

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)

