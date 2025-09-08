#!/usr/bin/env python3
"""
FORÇAR EXIBIÇÃO DAS OS NA PROGRAMAÇÃO
Este script força as OS a aparecerem na programação
Execute com: heroku run python forcar_exibicao_os.py -a ativusai
"""

import sys
import os
from datetime import datetime, date

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def forcar_exibicao_os():
    """Força as OS a aparecerem na programação"""
    
    print("🚀 FORÇANDO EXIBIÇÃO DAS OS NA PROGRAMAÇÃO")
    print("=" * 50)
    
    try:
        from models import db
        from app import create_app
        
        app = create_app()
        
        with app.app_context():
            print("1️⃣ VERIFICANDO OS EXISTENTES...")
            
            # Buscar todas as OS de PMP
            result = db.session.execute(db.text("""
                SELECT id, descricao, status, prioridade, pmp_id, usuario_responsavel
                FROM ordens_servico 
                WHERE pmp_id IS NOT NULL
                ORDER BY data_criacao DESC
            """))
            
            os_pmp = result.fetchall()
            
            print(f"📊 Encontradas {len(os_pmp)} OS de PMP:")
            for os_row in os_pmp:
                print(f"   - OS {os_row[0]}: Status={os_row[2]} | Prioridade={os_row[3]} | Usuário={os_row[5]}")
            
            print("\n2️⃣ FORÇANDO CONFIGURAÇÃO PARA APARECER NA PROGRAMAÇÃO...")
            
            # Atualizar OS de PMP para garantir que apareçam
            updates_realizados = 0
            
            for os_row in os_pmp:
                os_id = os_row[0]
                status_atual = os_row[2]
                prioridade_atual = os_row[3]
                usuario_atual = os_row[5]
                
                # Configurar para aparecer na seção preventiva
                novo_status = 'aberta'
                nova_prioridade = 'preventiva'
                novo_usuario = None  # Sem usuário para aparecer na seção preventiva
                
                # Só atualizar se necessário
                if (status_atual != novo_status or 
                    prioridade_atual != nova_prioridade or 
                    usuario_atual is not None):
                    
                    db.session.execute(db.text("""
                        UPDATE ordens_servico 
                        SET status = :status, 
                            prioridade = :prioridade, 
                            usuario_responsavel = NULL
                        WHERE id = :os_id
                    """), {
                        'status': novo_status,
                        'prioridade': nova_prioridade,
                        'os_id': os_id
                    })
                    
                    updates_realizados += 1
                    print(f"   ✅ OS {os_id}: Status={novo_status} | Prioridade={nova_prioridade} | Usuário=NULL")
                else:
                    print(f"   ⏭️ OS {os_id}: Já configurada corretamente")
            
            if updates_realizados > 0:
                db.session.commit()
                print(f"\n✅ {updates_realizados} OS atualizadas com sucesso!")
            else:
                print(f"\n⏭️ Todas as OS já estavam configuradas corretamente")
            
            print("\n3️⃣ VERIFICANDO RESULTADO...")
            
            # Verificar se agora aparecem no filtro
            result_final = db.session.execute(db.text("""
                SELECT id, descricao, status, prioridade, pmp_id, usuario_responsavel
                FROM ordens_servico 
                WHERE (
                    (prioridade = 'preventiva' AND status = 'aberta' AND usuario_responsavel IS NULL)
                    OR 
                    (pmp_id IS NOT NULL AND status = 'aberta')
                )
                ORDER BY data_criacao DESC
            """))
            
            os_visiveis = result_final.fetchall()
            
            print(f"📊 OS que DEVEM aparecer na seção Preventiva: {len(os_visiveis)}")
            for os_row in os_visiveis:
                print(f"   ✅ OS {os_row[0]}: {os_row[1][:40]}... | PMP: {os_row[4]}")
            
            print("\n4️⃣ TESTANDO API APÓS CORREÇÃO...")
            
            # Testar se API retorna as OS corretamente
            from flask import Flask
            from routes.ordens_servico import ordens_servico_bp
            
            test_app = Flask(__name__)
            test_app.config['SQLALCHEMY_DATABASE_URI'] = app.config['SQLALCHEMY_DATABASE_URI']
            test_app.config['SECRET_KEY'] = 'test'
            
            test_app.register_blueprint(ordens_servico_bp)
            db.init_app(test_app)
            
            with test_app.test_client() as client:
                with test_app.app_context():
                    # Simular sessão
                    with client.session_transaction() as sess:
                        sess['user_company'] = 'Sistema'
                        sess['user_name'] = 'Sistema'
                    
                    # Testar endpoint
                    response = client.get('/api/ordens-servico?status=abertas')
                    
                    if response.status_code == 200:
                        data = response.get_json()
                        if data and 'ordens_servico' in data:
                            api_os = data['ordens_servico']
                            print(f"📡 API retorna {len(api_os)} OS")
                            
                            # Contar OS de PMP
                            pmp_count = sum(1 for os in api_os if os.get('pmp_id'))
                            print(f"🔧 OS de PMP na API: {pmp_count}")
                            
                            # Simular filtro JavaScript
                            preventivas_js = []
                            for os in api_os:
                                condicao1 = (os['prioridade'] == 'preventiva' and 
                                           os['status'] == 'aberta' and 
                                           not os.get('usuario_responsavel'))
                                
                                condicao2 = os.get('pmp_id') and os['status'] == 'aberta'
                                
                                if condicao1 or condicao2:
                                    preventivas_js.append(os['id'])
                            
                            print(f"🎯 JavaScript mostraria: {len(preventivas_js)} OS")
                            print(f"📋 IDs: {preventivas_js}")
                        else:
                            print("❌ API não retornou dados válidos")
                    else:
                        print(f"❌ API falhou: {response.status_code}")
            
            print("\n🎯 RESULTADO FINAL:")
            print(f"   📊 OS de PMP configuradas: {len(os_pmp)}")
            print(f"   ✅ Updates realizados: {updates_realizados}")
            print(f"   📋 Devem aparecer na programação: {len(os_visiveis)}")
            
            if len(os_visiveis) > 0:
                print("\n🎉 SUCESSO! As OS agora devem aparecer na programação!")
                print("💡 Acesse: https://ativusai-af6f1462097d.herokuapp.com/programacao")
                print("💡 Abra o console (F12) para ver os logs de debug")
            else:
                print("\n❌ PROBLEMA: Ainda não há OS para mostrar")
                print("💡 Execute primeiro: heroku run python solucao_definitiva_os.py -a ativusai")
            
    except Exception as e:
        print(f"❌ ERRO CRÍTICO: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    forcar_exibicao_os()

