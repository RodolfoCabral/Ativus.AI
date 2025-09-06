#!/usr/bin/env python3
"""
DEBUG DEFINITIVO - Investigar por que OS de PMP não aparecem na programação
Execute com: heroku run python debug_os_programacao.py -a ativusai
"""

import sys
import os
from datetime import datetime, date

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def debug_os_programacao():
    """Debug completo das OS na programação"""
    
    print("🔍 DEBUG DEFINITIVO - OS NA PROGRAMAÇÃO")
    print("=" * 60)
    
    try:
        from models import db
        from app import create_app
        
        app = create_app()
        
        with app.app_context():
            print("1️⃣ VERIFICANDO OS CRIADAS HOJE...")
            
            # Buscar todas as OS criadas hoje
            hoje = datetime.now().date()
            result = db.session.execute(db.text("""
                SELECT id, descricao, status, prioridade, pmp_id, usuario_responsavel,
                       data_criacao, data_programada, empresa
                FROM ordens_servico 
                WHERE DATE(data_criacao) = :hoje
                ORDER BY id DESC
            """), {'hoje': hoje})
            
            os_hoje = result.fetchall()
            
            if not os_hoje:
                print("❌ NENHUMA OS criada hoje encontrada!")
                print("💡 Execute primeiro: heroku run python solucao_definitiva_os.py -a ativusai")
                return
            
            print(f"✅ Encontradas {len(os_hoje)} OS criadas hoje:")
            for os_row in os_hoje:
                print(f"   - OS {os_row[0]}: {os_row[1][:40]}...")
                print(f"     Status: {os_row[2]} | Prioridade: {os_row[3]} | PMP: {os_row[4]}")
                print(f"     Usuário: {os_row[5]} | Empresa: {os_row[8]}")
                print()
            
            print("2️⃣ TESTANDO API DE ORDENS DE SERVIÇO...")
            
            # Simular chamada da API que a programação usa
            from routes.ordens_servico import get_current_user
            
            # Buscar empresa do usuário (simular sessão)
            empresa_usuario = os_hoje[0][8]  # Pegar empresa da primeira OS
            print(f"🏢 Empresa do usuário: {empresa_usuario}")
            
            # Testar query da API para status 'abertas'
            result_api = db.session.execute(db.text("""
                SELECT id, descricao, status, prioridade, pmp_id, usuario_responsavel,
                       tipo_manutencao, oficina, qtd_pessoas, horas, hh,
                       filial_id, setor_id, equipamento_id, empresa
                FROM ordens_servico 
                WHERE empresa = :empresa 
                AND status IN ('aberta', 'programada')
                ORDER BY data_criacao DESC
            """), {'empresa': empresa_usuario})
            
            os_api = result_api.fetchall()
            
            print(f"📡 API retornaria {len(os_api)} OS:")
            for os_row in os_api:
                print(f"   - OS {os_row[0]}: Status={os_row[2]} | Prioridade={os_row[3]} | PMP={os_row[4]}")
            
            print("\n3️⃣ VERIFICANDO FILTROS DA PROGRAMAÇÃO...")
            
            # Simular filtros do JavaScript
            os_preventivas_sem_usuario = []
            os_pmp = []
            
            for os_row in os_api:
                os_id, descricao, status, prioridade, pmp_id, usuario_resp = os_row[:6]
                
                # Filtro 1: Preventivas sem usuário
                if (prioridade == 'preventiva' and 
                    status == 'aberta' and 
                    (not usuario_resp or usuario_resp == '' or usuario_resp == 'None')):
                    os_preventivas_sem_usuario.append(os_id)
                
                # Filtro 2: OS de PMP
                if pmp_id and pmp_id != 'None' and status == 'aberta':
                    os_pmp.append(os_id)
            
            print(f"🔍 Filtro JS - Preventivas sem usuário: {os_preventivas_sem_usuario}")
            print(f"🔍 Filtro JS - OS de PMP: {os_pmp}")
            
            total_preventivas = len(set(os_preventivas_sem_usuario + os_pmp))
            print(f"📊 Total que deveria aparecer na seção Preventiva: {total_preventivas}")
            
            print("\n4️⃣ VERIFICANDO DADOS COMPLETOS DAS OS...")
            
            # Verificar se OS têm todos os dados necessários para renderização
            for os_row in os_api:
                if os_row[4]:  # Se tem pmp_id
                    os_id = os_row[0]
                    print(f"\n🔍 OS {os_id} (PMP):")
                    
                    # Buscar dados completos com JOINs
                    result_completo = db.session.execute(db.text("""
                        SELECT os.id, os.descricao, os.status, os.prioridade, os.pmp_id,
                               os.tipo_manutencao, os.oficina, os.qtd_pessoas, os.horas, os.hh,
                               f.tag as filial_tag, s.tag as setor_tag, e.tag as equipamento_tag,
                               os.data_proxima_geracao, os.frequencia_origem, os.numero_sequencia
                        FROM ordens_servico os
                        LEFT JOIN filiais f ON os.filial_id = f.id
                        LEFT JOIN setores s ON os.setor_id = s.id
                        LEFT JOIN equipamentos e ON os.equipamento_id = e.id
                        WHERE os.id = :os_id
                    """), {'os_id': os_id})
                    
                    os_completa = result_completo.fetchone()
                    if os_completa:
                        print(f"   ✅ Dados completos disponíveis")
                        print(f"   📍 Localização: {os_completa[10]} - {os_completa[11]} - {os_completa[12]}")
                        print(f"   🔧 Tipo: {os_completa[5]} | Oficina: {os_completa[6]}")
                        print(f"   ⏰ Tempo: {os_completa[9]}h ({os_completa[7]}p × {os_completa[8]}h)")
                        print(f"   📅 Próxima: {os_completa[13]} | Freq: {os_completa[14]} | Seq: {os_completa[15]}")
                    else:
                        print(f"   ❌ Erro ao buscar dados completos")
            
            print("\n5️⃣ TESTANDO ENDPOINT REAL DA API...")
            
            # Testar endpoint real
            try:
                from flask import Flask
                from routes.ordens_servico import ordens_servico_bp
                
                test_app = Flask(__name__)
                test_app.register_blueprint(ordens_servico_bp)
                
                with test_app.test_client() as client:
                    # Simular request
                    response = client.get('/api/ordens-servico?status=abertas')
                    print(f"📡 Status da API: {response.status_code}")
                    
                    if response.status_code == 200:
                        data = response.get_json()
                        if data and 'ordens_servico' in data:
                            os_count = len(data['ordens_servico'])
                            print(f"📊 API retornou {os_count} OS")
                            
                            # Verificar se tem OS de PMP
                            pmp_count = sum(1 for os in data['ordens_servico'] if os.get('pmp_id'))
                            print(f"🔧 OS de PMP na API: {pmp_count}")
                        else:
                            print("❌ API não retornou dados válidos")
                    else:
                        print(f"❌ API retornou erro: {response.status_code}")
                        
            except Exception as e:
                print(f"⚠️ Não foi possível testar endpoint: {e}")
            
            print("\n6️⃣ DIAGNÓSTICO FINAL...")
            
            if not os_hoje:
                print("❌ PROBLEMA: Nenhuma OS foi criada hoje")
                print("💡 SOLUÇÃO: Execute o script de geração de OS")
            elif not os_api:
                print("❌ PROBLEMA: API não retorna OS para a empresa")
                print("💡 SOLUÇÃO: Verificar filtro de empresa na API")
            elif total_preventivas == 0:
                print("❌ PROBLEMA: Filtros JS não capturam as OS")
                print("💡 SOLUÇÃO: Ajustar lógica de filtro no frontend")
            else:
                print("✅ TUDO PARECE OK - Problema pode ser no frontend")
                print("💡 SOLUÇÃO: Verificar console do navegador e cache")
            
            print(f"\n🎯 RESUMO:")
            print(f"   📊 OS criadas hoje: {len(os_hoje)}")
            print(f"   📡 OS na API: {len(os_api)}")
            print(f"   🔧 OS de PMP: {len([os for os in os_api if os[4]])}")
            print(f"   📋 Deveria aparecer: {total_preventivas}")
            
    except Exception as e:
        print(f"❌ ERRO CRÍTICO: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    debug_os_programacao()

