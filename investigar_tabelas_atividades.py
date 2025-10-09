#!/usr/bin/env python3
"""
Script para investigar a estrutura das tabelas de atividades
"""

import sys
import os

# Adicionar o diretório atual ao path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def investigar_tabelas():
    """Investiga as tabelas de atividades"""
    print("🔍 INVESTIGANDO TABELAS DE ATIVIDADES")
    print("="*60)
    
    try:
        from app import create_app
        app = create_app()
        
        with app.app_context():
            from models import db
            
            # Listar todas as tabelas
            print("📋 TABELAS NO BANCO:")
            result = db.engine.execute("SELECT table_name FROM information_schema.tables WHERE table_schema = 'public'")
            tabelas = [row[0] for row in result]
            
            tabelas_atividades = [t for t in tabelas if 'atividade' in t.lower()]
            print(f"   Tabelas relacionadas a atividades: {tabelas_atividades}")
            
            # Verificar estrutura de cada tabela de atividades
            for tabela in tabelas_atividades:
                print(f"\n📊 ESTRUTURA DA TABELA '{tabela}':")
                try:
                    result = db.engine.execute(f"SELECT column_name, data_type, is_nullable FROM information_schema.columns WHERE table_name = '{tabela}' ORDER BY ordinal_position")
                    colunas = list(result)
                    
                    for coluna in colunas:
                        print(f"   {coluna[0]} ({coluna[1]}) {'NULL' if coluna[2] == 'YES' else 'NOT NULL'}")
                    
                    # Contar registros
                    result = db.engine.execute(f"SELECT COUNT(*) FROM {tabela}")
                    count = result.fetchone()[0]
                    print(f"   📊 Total de registros: {count}")
                    
                    # Mostrar alguns registros se houver
                    if count > 0:
                        print(f"   📋 Primeiros 3 registros:")
                        result = db.engine.execute(f"SELECT * FROM {tabela} LIMIT 3")
                        registros = list(result)
                        
                        for i, registro in enumerate(registros):
                            print(f"      {i+1}. {dict(registro)}")
                    
                except Exception as e:
                    print(f"   ❌ Erro ao analisar tabela {tabela}: {e}")
            
            # Verificar especificamente a OS 862
            print(f"\n🔍 INVESTIGANDO OS 862:")
            
            # Verificar se a OS existe
            result = db.engine.execute("SELECT id, descricao, pmp_id FROM ordens_servico WHERE id = 862")
            os_data = result.fetchone()
            
            if os_data:
                print(f"   ✅ OS 862 encontrada: {os_data[1]}")
                print(f"   🔗 PMP ID: {os_data[2]}")
                
                # Buscar atividades em todas as tabelas possíveis
                for tabela in tabelas_atividades:
                    try:
                        # Tentar diferentes colunas que podem referenciar a OS
                        colunas_possíveis = ['os_id', 'ordem_servico_id', 'id_os', 'ordem_id']
                        
                        for coluna in colunas_possíveis:
                            try:
                                result = db.engine.execute(f"SELECT COUNT(*) FROM {tabela} WHERE {coluna} = 862")
                                count = result.fetchone()[0]
                                if count > 0:
                                    print(f"   ✅ {tabela}.{coluna}: {count} atividades encontradas")
                                    
                                    # Mostrar as atividades
                                    result = db.engine.execute(f"SELECT * FROM {tabela} WHERE {coluna} = 862 LIMIT 5")
                                    atividades = list(result)
                                    for atividade in atividades:
                                        print(f"      - {dict(atividade)}")
                                else:
                                    print(f"   ⚪ {tabela}.{coluna}: 0 atividades")
                            except Exception:
                                # Coluna não existe nesta tabela
                                pass
                    except Exception as e:
                        print(f"   ❌ Erro ao verificar {tabela}: {e}")
                
                # Verificar se a PMP tem atividades
                if os_data[2]:
                    print(f"\n🔍 INVESTIGANDO PMP {os_data[2]}:")
                    
                    for tabela in tabelas_atividades:
                        try:
                            colunas_pmp = ['pmp_id', 'plano_id', 'id_pmp']
                            
                            for coluna in colunas_pmp:
                                try:
                                    result = db.engine.execute(f"SELECT COUNT(*) FROM {tabela} WHERE {coluna} = {os_data[2]}")
                                    count = result.fetchone()[0]
                                    if count > 0:
                                        print(f"   ✅ {tabela}.{coluna}: {count} atividades da PMP")
                                        
                                        # Mostrar as atividades da PMP
                                        result = db.engine.execute(f"SELECT * FROM {tabela} WHERE {coluna} = {os_data[2]} LIMIT 3")
                                        atividades = list(result)
                                        for atividade in atividades:
                                            print(f"      - {dict(atividade)}")
                                    else:
                                        print(f"   ⚪ {tabela}.{coluna}: 0 atividades da PMP")
                                except Exception:
                                    pass
                        except Exception as e:
                            print(f"   ❌ Erro ao verificar PMP em {tabela}: {e}")
            else:
                print(f"   ❌ OS 862 não encontrada")
        
        return True
        
    except Exception as e:
        print(f"❌ Erro geral: {e}")
        import traceback
        traceback.print_exc()
        return False

def verificar_modelos():
    """Verifica os modelos Python"""
    print(f"\n🔍 VERIFICANDO MODELOS PYTHON:")
    print("="*40)
    
    try:
        from app import create_app
        app = create_app()
        
        with app.app_context():
            # Verificar modelo AtividadeOS
            try:
                from models.atividade_os import AtividadeOS
                print(f"   ✅ AtividadeOS importado com sucesso")
                print(f"   📋 Tabela: {AtividadeOS.__tablename__}")
                
                # Verificar colunas do modelo
                colunas = [c.name for c in AtividadeOS.__table__.columns]
                print(f"   📊 Colunas: {colunas}")
                
                # Contar registros usando o modelo
                count = AtividadeOS.query.count()
                print(f"   📊 Total via modelo: {count}")
                
                # Buscar atividades da OS 862 usando o modelo
                atividades_862 = AtividadeOS.query.filter_by(os_id=862).all()
                print(f"   🔍 Atividades OS 862 via modelo: {len(atividades_862)}")
                
                for atividade in atividades_862[:3]:
                    print(f"      - ID: {atividade.id}, Desc: {atividade.descricao}")
                
            except Exception as e:
                print(f"   ❌ Erro com AtividadeOS: {e}")
            
            # Verificar outros modelos possíveis
            try:
                from assets_models import OrdemServico
                os = OrdemServico.query.get(862)
                if os:
                    print(f"   ✅ OS 862 via modelo: {os.descricao}")
                    print(f"   🔗 PMP ID: {os.pmp_id}")
                else:
                    print(f"   ❌ OS 862 não encontrada via modelo")
            except Exception as e:
                print(f"   ❌ Erro com OrdemServico: {e}")
        
    except Exception as e:
        print(f"❌ Erro nos modelos: {e}")

if __name__ == "__main__":
    print("🔍 INVESTIGAÇÃO COMPLETA DE ATIVIDADES")
    print()
    
    # Investigar tabelas
    investigar_tabelas()
    
    # Verificar modelos
    verificar_modelos()
    
    print("\n" + "="*60)
    print("📊 INVESTIGAÇÃO CONCLUÍDA")
    print("="*60)
