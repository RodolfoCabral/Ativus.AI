#!/usr/bin/env python3
"""
Script de debug para executar no Heroku e investigar problema de geração de OS
Execute com: heroku run python debug_os_heroku.py -a ativusai
"""

import sys
import os
from datetime import datetime, date, timedelta

# Adicionar o diretório atual ao path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def debug_sistema_completo():
    """Debug completo do sistema no Heroku"""
    
    print("🔍 DEBUG SISTEMA PMP/OS - HEROKU")
    print("=" * 50)
    
    try:
        from models import db
        from app import create_app
        
        print("✅ Módulos básicos importados")
        
        # Criar app
        app = create_app()
        print("✅ App criado com sucesso")
        
        with app.app_context():
            # Testar conexão com banco
            try:
                result = db.session.execute(db.text("SELECT 1"))
                print("✅ Conexão com banco OK")
            except Exception as e:
                print(f"❌ Erro de conexão: {e}")
                return
            
            # Verificar se tabelas existem
            print("\n📊 VERIFICANDO TABELAS")
            print("-" * 30)
            
            tabelas = ['pmps', 'ordens_servico', 'user']
            for tabela in tabelas:
                try:
                    result = db.session.execute(db.text(f"SELECT COUNT(*) FROM {tabela}"))
                    count = result.scalar()
                    print(f"✅ {tabela}: {count} registros")
                except Exception as e:
                    print(f"❌ {tabela}: Erro - {e}")
            
            # Verificar colunas específicas
            print("\n🔧 VERIFICANDO COLUNAS NECESSÁRIAS")
            print("-" * 30)
            
            # Verificar colunas em ordens_servico
            try:
                result = db.session.execute(db.text("""
                    SELECT column_name 
                    FROM information_schema.columns 
                    WHERE table_name = 'ordens_servico'
                    AND column_name IN ('pmp_id', 'data_proxima_geracao', 'frequencia_origem', 'numero_sequencia')
                """))
                colunas_os = [row[0] for row in result]
                
                colunas_necessarias = ['pmp_id', 'data_proxima_geracao', 'frequencia_origem', 'numero_sequencia']
                for coluna in colunas_necessarias:
                    status = "✅" if coluna in colunas_os else "❌"
                    print(f"  {status} ordens_servico.{coluna}")
                    
            except Exception as e:
                print(f"❌ Erro ao verificar colunas ordens_servico: {e}")
            
            # Verificar colunas em pmps
            try:
                result = db.session.execute(db.text("""
                    SELECT column_name 
                    FROM information_schema.columns 
                    WHERE table_name = 'pmps'
                    AND column_name IN ('data_inicio_plano', 'usuarios_responsaveis', 'frequencia')
                """))
                colunas_pmps = [row[0] for row in result]
                
                colunas_pmp_necessarias = ['data_inicio_plano', 'usuarios_responsaveis', 'frequencia']
                for coluna in colunas_pmp_necessarias:
                    status = "✅" if coluna in colunas_pmps else "❌"
                    print(f"  {status} pmps.{coluna}")
                    
            except Exception as e:
                print(f"❌ Erro ao verificar colunas pmps: {e}")
            
            # Verificar PMPs com data de início
            print("\n📅 VERIFICANDO PMPs COM DATA DE INÍCIO")
            print("-" * 30)
            
            try:
                # Contar PMPs total
                result = db.session.execute(db.text("SELECT COUNT(*) FROM pmps"))
                total_pmps = result.scalar()
                print(f"📋 Total de PMPs: {total_pmps}")
                
                # Contar PMPs com data de início
                result = db.session.execute(db.text("""
                    SELECT COUNT(*) FROM pmps 
                    WHERE data_inicio_plano IS NOT NULL
                """))
                pmps_com_data = result.scalar()
                print(f"📅 PMPs com data de início: {pmps_com_data}")
                
                if pmps_com_data == 0:
                    print("❌ PROBLEMA: Nenhuma PMP tem data de início!")
                    print("💡 SOLUÇÃO: Definir data de início nas PMPs")
                    
                    # Mostrar algumas PMPs
                    result = db.session.execute(db.text("""
                        SELECT id, atividade, equipamento_id 
                        FROM pmps 
                        WHERE data_inicio_plano IS NULL 
                        LIMIT 5
                    """))
                    
                    print("\n📋 PMPs sem data de início:")
                    for row in result:
                        print(f"  - ID {row[0]}: {row[1]} (Equip: {row[2]})")
                
                else:
                    # Verificar PMPs que deveriam gerar OS
                    hoje = date.today()
                    result = db.session.execute(db.text("""
                        SELECT COUNT(*) FROM pmps 
                        WHERE data_inicio_plano IS NOT NULL 
                        AND data_inicio_plano <= :hoje
                    """), {'hoje': hoje})
                    
                    pmps_para_gerar = result.scalar()
                    print(f"🎯 PMPs que deveriam gerar OS até hoje: {pmps_para_gerar}")
                    
                    if pmps_para_gerar > 0:
                        # Mostrar algumas PMPs
                        result = db.session.execute(db.text("""
                            SELECT id, atividade, data_inicio_plano, frequencia
                            FROM pmps 
                            WHERE data_inicio_plano IS NOT NULL 
                            AND data_inicio_plano <= :hoje
                            LIMIT 5
                        """), {'hoje': hoje})
                        
                        print("\n📋 PMPs prontas para gerar OS:")
                        for row in result:
                            print(f"  - ID {row[0]}: {row[1]}")
                            print(f"    Data início: {row[2]}")
                            print(f"    Frequência: {row[3] or 'semanal'}")
                    
            except Exception as e:
                print(f"❌ Erro ao verificar PMPs: {e}")
            
            # Verificar OS já geradas
            print("\n📊 VERIFICANDO OS GERADAS")
            print("-" * 30)
            
            try:
                # Total de OS
                result = db.session.execute(db.text("SELECT COUNT(*) FROM ordens_servico"))
                total_os = result.scalar()
                print(f"📋 Total de OS: {total_os}")
                
                # OS geradas por PMP
                result = db.session.execute(db.text("""
                    SELECT COUNT(*) FROM ordens_servico 
                    WHERE pmp_id IS NOT NULL
                """))
                os_pmp = result.scalar()
                print(f"🔗 OS geradas por PMP: {os_pmp}")
                
                if os_pmp == 0:
                    print("❌ PROBLEMA: Nenhuma OS foi gerada por PMP!")
                    print("💡 POSSÍVEL CAUSA: Sistema não está gerando automaticamente")
                
                # OS por status
                result = db.session.execute(db.text("""
                    SELECT status, COUNT(*) 
                    FROM ordens_servico 
                    WHERE pmp_id IS NOT NULL
                    GROUP BY status
                """))
                
                print("\n📊 OS por status:")
                for row in result:
                    print(f"  - {row[0]}: {row[1]}")
                    
            except Exception as e:
                print(f"❌ Erro ao verificar OS: {e}")
            
            # Testar importação dos módulos de geração
            print("\n🧪 TESTANDO MÓDULOS DE GERAÇÃO")
            print("-" * 30)
            
            try:
                from routes.pmp_os_generator import pmp_os_generator_bp
                print("✅ pmp_os_generator importado")
            except Exception as e:
                print(f"❌ Erro ao importar pmp_os_generator: {e}")
            
            try:
                from routes.pmp_scheduler import pmp_scheduler_bp
                print("✅ pmp_scheduler importado")
            except Exception as e:
                print(f"❌ Erro ao importar pmp_scheduler: {e}")
            
            try:
                from routes.programacao_api import programacao_api_bp
                print("✅ programacao_api importado")
            except Exception as e:
                print(f"❌ Erro ao importar programacao_api: {e}")
            
            print("\n🎉 DEBUG CONCLUÍDO")
            print("=" * 50)
            
    except Exception as e:
        print(f"❌ ERRO CRÍTICO NO DEBUG: {e}")
        import traceback
        traceback.print_exc()

def sugerir_acoes():
    """Sugere ações baseadas no debug"""
    
    print("\n💡 AÇÕES RECOMENDADAS:")
    print("=" * 50)
    
    print("1. 📅 SE NÃO HÁ PMPs COM DATA DE INÍCIO:")
    print("   - Acesse o plano mestre no sistema")
    print("   - Edite cada PMP")
    print("   - Defina 'Data de Início do Plano'")
    print("   - Use data de hoje ou no passado")
    print("   - Salve as alterações")
    
    print("\n2. 🗄️ SE FALTAM COLUNAS NO BANCO:")
    print("   - Execute: heroku run python migrar_banco_simples.py -a ativusai")
    print("   - Aguarde conclusão da migração")
    print("   - Execute este debug novamente")
    
    print("\n3. 🔄 SE PMPs EXISTEM MAS NÃO GERAM OS:")
    print("   - Acesse a tela de programação")
    print("   - Clique em 'Verificar Pendências'")
    print("   - Clique em 'Gerar OS Pendentes'")
    print("   - Verifique se OS aparecem")
    
    print("\n4. 🧪 TESTE MANUAL VIA API:")
    print("   - POST /api/pmp/gerar-os")
    print("   - Body: {\"pmp_id\": [ID_DA_PMP], \"data_inicio_plano\": \"2025-09-05\"}")
    
    print("\n5. 📊 VERIFICAR LOGS:")
    print("   - heroku logs --tail -a ativusai")
    print("   - Procurar erros relacionados a PMP/OS")

if __name__ == "__main__":
    debug_sistema_completo()
    sugerir_acoes()

