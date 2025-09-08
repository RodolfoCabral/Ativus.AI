#!/usr/bin/env python3
"""
DEBUG REAL DA PROGRAMAÇÃO - Descobrir por que OS não aparecem
Execute com: heroku run python debug_programacao_real.py -a ativusai
"""

import sys
import os
from datetime import datetime, date

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def debug_programacao_real():
    """Debug específico da programação"""
    
    print("🔍 DEBUG REAL DA PROGRAMAÇÃO")
    print("=" * 50)
    
    try:
        from models import db
        from app import create_app
        
        app = create_app()
        
        with app.app_context():
            print("1️⃣ TESTANDO API REAL DA PROGRAMAÇÃO...")
            
            # Testar endpoint que a programação realmente usa
            result = db.session.execute(db.text("""
                SELECT id, descricao, status, prioridade, pmp_id, usuario_responsavel,
                       tipo_manutencao, oficina, qtd_pessoas, horas, hh,
                       filial_id, setor_id, equipamento_id, empresa,
                       data_criacao, data_programada
                FROM ordens_servico 
                WHERE empresa = 'Sistema'
                AND status IN ('aberta', 'programada')
                ORDER BY data_criacao DESC
            """))
            
            os_list = result.fetchall()
            
            print(f"📊 Total de OS encontradas: {len(os_list)}")
            
            for os_row in os_list:
                print(f"\n🔍 OS {os_row[0]}:")
                print(f"   📝 Descrição: {os_row[1][:50]}...")
                print(f"   📊 Status: {os_row[2]} | Prioridade: {os_row[3]}")
                print(f"   🔧 PMP ID: {os_row[4]} | Usuário: {os_row[5]}")
                print(f"   🏭 Tipo: {os_row[6]} | Oficina: {os_row[7]}")
                print(f"   ⏰ Tempo: {os_row[10]}h ({os_row[8]}p × {os_row[9]}h)")
                print(f"   🏢 Empresa: {os_row[14]}")
                
                # Verificar se deveria aparecer na seção preventiva
                is_pmp = os_row[4] is not None
                is_preventiva = os_row[3] == 'preventiva'
                is_aberta = os_row[2] == 'aberta'
                sem_usuario = os_row[5] is None or os_row[5] == ''
                
                deveria_aparecer = (is_preventiva and is_aberta and sem_usuario) or (is_pmp and is_aberta)
                
                print(f"   ✅ Deveria aparecer na preventiva: {deveria_aparecer}")
                if deveria_aparecer:
                    print(f"      - É PMP: {is_pmp}")
                    print(f"      - É preventiva: {is_preventiva}")
                    print(f"      - Está aberta: {is_aberta}")
                    print(f"      - Sem usuário: {sem_usuario}")
            
            print("\n2️⃣ SIMULANDO RESPOSTA DA API...")
            
            # Simular exatamente o que a API retorna
            api_response = []
            for os_row in os_list:
                os_dict = {
                    'id': os_row[0],
                    'descricao': os_row[1],
                    'status': os_row[2],
                    'prioridade': os_row[3],
                    'pmp_id': os_row[4],
                    'usuario_responsavel': os_row[5],
                    'tipo_manutencao': os_row[6],
                    'oficina': os_row[7],
                    'qtd_pessoas': os_row[8],
                    'horas': os_row[9],
                    'hh': os_row[10],
                    'filial_id': os_row[11],
                    'setor_id': os_row[12],
                    'equipamento_id': os_row[13],
                    'empresa': os_row[14],
                    'data_criacao': os_row[15].isoformat() if os_row[15] else None,
                    'data_programada': os_row[16].isoformat() if os_row[16] else None
                }
                api_response.append(os_dict)
            
            print(f"📡 API retornaria {len(api_response)} OS")
            
            # Simular filtro JavaScript para preventivas
            preventivas = []
            for os in api_response:
                # Condição 1: Preventivas sem usuário
                condicao1 = (os['prioridade'] == 'preventiva' and 
                           os['status'] == 'aberta' and 
                           (not os['usuario_responsavel'] or os['usuario_responsavel'] == ''))
                
                # Condição 2: OS de PMP
                condicao2 = os['pmp_id'] is not None and os['status'] == 'aberta'
                
                if condicao1 or condicao2:
                    preventivas.append(os['id'])
            
            print(f"🔧 Filtro JS - Preventivas: {preventivas}")
            
            print("\n3️⃣ TESTANDO ENDPOINT REAL...")
            
            # Testar endpoint real com Flask test client
            from flask import Flask
            from routes.ordens_servico import ordens_servico_bp
            
            test_app = Flask(__name__)
            test_app.config['SQLALCHEMY_DATABASE_URI'] = app.config['SQLALCHEMY_DATABASE_URI']
            test_app.config['SECRET_KEY'] = 'test'
            
            # Registrar blueprint
            test_app.register_blueprint(ordens_servico_bp)
            
            # Inicializar banco
            db.init_app(test_app)
            
            with test_app.test_client() as client:
                with test_app.app_context():
                    # Simular sessão
                    with client.session_transaction() as sess:
                        sess['user_company'] = 'Sistema'
                        sess['user_name'] = 'Sistema'
                    
                    # Testar endpoint
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
                            
                            # Mostrar primeiras OS
                            for i, os in enumerate(data['ordens_servico'][:3]):
                                print(f"   OS {os['id']}: {os['descricao'][:30]}... | PMP: {os.get('pmp_id')} | Status: {os['status']}")
                        else:
                            print("❌ API não retornou dados válidos")
                            print(f"Resposta: {data}")
                    else:
                        print(f"❌ API retornou erro: {response.status_code}")
                        print(f"Resposta: {response.get_data(as_text=True)}")
            
            print("\n4️⃣ DIAGNÓSTICO FINAL...")
            
            total_os = len(os_list)
            total_preventivas = len(preventivas)
            
            if total_os == 0:
                print("❌ PROBLEMA: Nenhuma OS encontrada no banco")
                print("💡 SOLUÇÃO: Executar script de geração de OS")
            elif total_preventivas == 0:
                print("❌ PROBLEMA: Nenhuma OS passa no filtro de preventivas")
                print("💡 SOLUÇÃO: Verificar lógica de filtro no JavaScript")
            else:
                print(f"✅ DADOS OK: {total_os} OS no banco, {total_preventivas} deveriam aparecer")
                print("💡 PROBLEMA: Pode ser no carregamento do JavaScript ou cache")
            
            print(f"\n🎯 RESUMO FINAL:")
            print(f"   📊 OS no banco: {total_os}")
            print(f"   🔧 OS de PMP: {sum(1 for os in os_list if os[4] is not None)}")
            print(f"   📋 Deveriam aparecer: {total_preventivas}")
            
    except Exception as e:
        print(f"❌ ERRO CRÍTICO: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    debug_programacao_real()

