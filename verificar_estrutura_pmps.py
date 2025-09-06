#!/usr/bin/env python3
"""
Script para verificar a estrutura real da tabela pmps
Execute com: heroku run python verificar_estrutura_pmps.py -a ativusai
"""

import sys
import os

# Adicionar o diretório atual ao path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def verificar_estrutura_pmps():
    """Verifica a estrutura real da tabela pmps"""
    
    print("🔍 VERIFICANDO ESTRUTURA DA TABELA PMPS")
    print("=" * 50)
    
    try:
        from models import db
        from app import create_app
        
        app = create_app()
        
        with app.app_context():
            # Verificar colunas da tabela pmps
            print("📊 Colunas da tabela pmps:")
            print("-" * 30)
            
            result = db.session.execute(db.text("""
                SELECT column_name, data_type, is_nullable
                FROM information_schema.columns 
                WHERE table_name = 'pmps'
                ORDER BY ordinal_position
            """))
            
            colunas = result.fetchall()
            
            if not colunas:
                print("❌ Tabela pmps não encontrada!")
                return
            
            for coluna in colunas:
                nome, tipo, nullable = coluna
                print(f"  - {nome} ({tipo}) {'NULL' if nullable == 'YES' else 'NOT NULL'}")
            
            # Verificar alguns dados de exemplo
            print(f"\n📋 Dados de exemplo (primeiros 3 registros):")
            print("-" * 30)
            
            # Usar apenas colunas que sabemos que existem
            result = db.session.execute(db.text("""
                SELECT id, equipamento_id, data_inicio_plano, frequencia
                FROM pmps 
                LIMIT 3
            """))
            
            registros = result.fetchall()
            
            for registro in registros:
                print(f"  ID: {registro[0]}, Equipamento: {registro[1]}, Data Início: {registro[2]}, Frequência: {registro[3]}")
            
            # Verificar quantos registros têm data de início
            print(f"\n📊 Estatísticas:")
            print("-" * 30)
            
            result = db.session.execute(db.text("SELECT COUNT(*) FROM pmps"))
            total = result.scalar()
            print(f"  Total de PMPs: {total}")
            
            result = db.session.execute(db.text("""
                SELECT COUNT(*) FROM pmps 
                WHERE data_inicio_plano IS NOT NULL
            """))
            com_data = result.scalar()
            print(f"  PMPs com data de início: {com_data}")
            
            # Verificar se existe coluna de descrição/nome
            nomes_possiveis = ['atividade', 'descricao', 'nome', 'title', 'description']
            coluna_nome = None
            
            for nome in nomes_possiveis:
                try:
                    result = db.session.execute(db.text(f"SELECT {nome} FROM pmps LIMIT 1"))
                    result.fetchone()
                    coluna_nome = nome
                    print(f"  ✅ Coluna de descrição encontrada: {nome}")
                    break
                except:
                    continue
            
            if not coluna_nome:
                print("  ⚠️ Nenhuma coluna de descrição encontrada")
                print("  💡 Usando apenas ID para identificação")
            
            print(f"\n🎯 INFORMAÇÕES PARA CORREÇÃO:")
            print("-" * 30)
            print(f"  Coluna de identificação: {coluna_nome or 'id'}")
            print(f"  Total de PMPs: {total}")
            print(f"  PMPs com data de início: {com_data}")
            
    except Exception as e:
        print(f"❌ ERRO: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    verificar_estrutura_pmps()

