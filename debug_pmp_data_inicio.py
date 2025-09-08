#!/usr/bin/env python3
"""
DEBUG DA GERAÇÃO AUTOMÁTICA DE OS AO DEFINIR DATA DE INÍCIO
Execute com: heroku run python debug_pmp_data_inicio.py -a ativusai
"""

import sys
import os
from datetime import datetime, date, timedelta
import json
import traceback

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def debug_pmp_data_inicio():
    """Debug da geração automática de OS ao definir data de início"""
    
    print("🔍 DEBUG DA GERAÇÃO AUTOMÁTICA DE OS")
    print("=" * 50)
    
    try:
        from models import db
        from app import create_app
        
        app = create_app()
        
        with app.app_context():
            print("1️⃣ VERIFICANDO ESTRUTURA DA TABELA ORDENS_SERVICO...")
            
            # Verificar estrutura da tabela
            result = db.session.execute(db.text("""
                SELECT column_name, data_type, is_nullable, column_default
                FROM information_schema.columns 
                WHERE table_name = 'ordens_servico' 
                ORDER BY ordinal_position
            """))
            
            colunas = result.fetchall()
            print(f"📊 Tabela tem {len(colunas)} colunas:")
            
            campos_obrigatorios = []
            for col in colunas:
                nullable = "NULL" if col[2] == 'YES' else "NOT NULL"
                default = f" DEFAULT {col[3]}" if col[3] else ""
                print(f"   - {col[0]}: {col[1]} {nullable}{default}")
                
                if col[2] == 'NO' and col[0] != 'id':  # NOT NULL exceto ID (auto-increment)
                    campos_obrigatorios.append(col[0])
            
            print(f"\n🔒 Campos obrigatórios: {campos_obrigatorios}")
            
            print("\n2️⃣ VERIFICANDO PMPS EXISTENTES...")
            
            # Buscar PMPs com data de início
            result = db.session.execute(db.text("""
                SELECT id, descricao, equipamento_id, frequencia, data_inicio_plano
                FROM pmps 
                WHERE data_inicio_plano IS NOT NULL
                ORDER BY id DESC
                LIMIT 5
            """))
            
            pmps_com_data = result.fetchall()
            
            print(f"📋 Encontradas {len(pmps_com_data)} PMPs com data de início:")
            for pmp in pmps_com_data:
                print(f"   - PMP {pmp[0]}: {pmp[1][:40]}... | Data: {pmp[4]}")
            
            print("\n3️⃣ VERIFICANDO OS GERADAS DE PMP...")
            
            # Buscar OS de PMP
            result = db.session.execute(db.text("""
                SELECT id, descricao, pmp_id, data_criacao, status
                FROM ordens_servico 
                WHERE pmp_id IS NOT NULL
                ORDER BY id DESC
                LIMIT 10
            """))
            
            os_pmp = result.fetchall()
            
            print(f"📊 Encontradas {len(os_pmp)} OS de PMP:")
            for os in os_pmp:
                print(f"   - OS {os[0]}: PMP {os[2]} | {os[1][:40]}... | {os[4]} | {os[3]}")
            
            print("\n4️⃣ TESTANDO GERAÇÃO MANUAL DE OS...")
            
            # Selecionar uma PMP para teste
            pmp_id_teste = None
            
            # Buscar PMPs sem OS
            result = db.session.execute(db.text("""
                SELECT p.id, p.descricao, p.equipamento_id, p.frequencia, p.data_inicio_plano
                FROM pmps p
                LEFT JOIN ordens_servico os ON os.pmp_id = p.id
                WHERE p.data_inicio_plano IS NOT NULL
                AND os.id IS NULL
                ORDER BY p.id DESC
                LIMIT 1
            """))
            
            pmp_sem_os = result.fetchone()
            
            if pmp_sem_os:
                pmp_id_teste = pmp_sem_os[0]
                print(f"✅ Encontrada PMP {pmp_id_teste} sem OS para teste")
            else:
                # Se não encontrar, usar a primeira PMP com data
                if pmps_com_data:
                    pmp_id_teste = pmps_com_data[0][0]
                    print(f"⚠️ Usando PMP {pmp_id_teste} que já pode ter OS")
                else:
                    # Buscar qualquer PMP
                    result = db.session.execute(db.text("SELECT id FROM pmps LIMIT 1"))
                    pmp_qualquer = result.fetchone()
                    if pmp_qualquer:
                        pmp_id_teste = pmp_qualquer[0]
                        print(f"⚠️ Usando PMP {pmp_id_teste} sem data de início")
                    else:
                        print("❌ Nenhuma PMP encontrada para teste")
                        return
            
            if pmp_id_teste:
                print(f"\n5️⃣ TESTANDO GERAÇÃO MANUAL PARA PMP {pmp_id_teste}...")
                
                # Buscar dados completos da PMP
                result = db.session.execute(db.text("""
                    SELECT id, descricao, equipamento_id, frequencia, num_pessoas, tempo_pessoa, data_inicio_plano
                    FROM pmps 
                    WHERE id = :pmp_id
                """), {'pmp_id': pmp_id_teste})
                
                pmp_data = result.fetchone()
                
                if not pmp_data:
                    print(f"❌ PMP {pmp_id_teste} não encontrada")
                    return
                
                print(f"📋 Dados da PMP {pmp_id_teste}:")
                print(f"   - Descrição: {pmp_data[1]}")
                print(f"   - Equipamento: {pmp_data[2]}")
                print(f"   - Frequência: {pmp_data[3]}")
                print(f"   - Pessoas: {pmp_data[4]}")
                print(f"   - Tempo: {pmp_data[5]}")
                print(f"   - Data início: {pmp_data[6]}")
                
                # Buscar dados do equipamento
                from assets_models import Equipamento, Setor, Filial
                equipamento = Equipamento.query.get(pmp_data[2])
                
                if not equipamento:
                    print(f"❌ Equipamento {pmp_data[2]} não encontrado")
                    return
                
                print(f"📋 Dados do equipamento {equipamento.id}:")
                print(f"   - Tag: {equipamento.tag}")
                print(f"   - Descrição: {equipamento.descricao}")
                print(f"   - Setor: {equipamento.setor_id}")
                
                setor = Setor.query.get(equipamento.setor_id) if equipamento.setor_id else None
                filial = Filial.query.get(setor.filial_id) if setor and setor.filial_id else None
                
                # Calcular próxima data baseada na frequência
                data_inicio = pmp_data[6] or date.today()
                frequencia = pmp_data[3] or 'mensal'
                
                if frequencia == 'diario':
                    proxima_data = data_inicio + timedelta(days=1)
                elif frequencia == 'semanal':
                    proxima_data = data_inicio + timedelta(weeks=1)
                elif frequencia == 'mensal':
                    proxima_data = data_inicio + timedelta(days=30)
                elif frequencia == 'trimestral':
                    proxima_data = data_inicio + timedelta(days=90)
                elif frequencia == 'semestral':
                    proxima_data = data_inicio + timedelta(days=180)
                elif frequencia == 'anual':
                    proxima_data = data_inicio + timedelta(days=365)
                else:
                    proxima_data = data_inicio + timedelta(days=30)
                
                print(f"📅 Próxima data calculada: {proxima_data}")
                
                # Criar OS manualmente
                try:
                    from assets_models import OrdemServico
                    
                    nova_os = OrdemServico(
                        chamado_id=None,
                        descricao=f"PMP: {pmp_data[1] or 'Manutenção Preventiva'} - {equipamento.tag} - Sequência #1",
                        tipo_manutencao='preventiva',
                        oficina='Oficina Manutenção',
                        condicao_ativo='Operacional',
                        qtd_pessoas=int(pmp_data[4] or 1),
                        horas=float(pmp_data[5] or 1.0),
                        hh=float(pmp_data[4] or 1) * float(pmp_data[5] or 1.0),
                        prioridade='preventiva',
                        status='aberta',
                        filial_id=filial.id if filial else 166,
                        setor_id=setor.id if setor else 166,
                        equipamento_id=equipamento.id,
                        empresa='Sistema',
                        usuario_criacao='Sistema PMP',
                        usuario_responsavel=None,
                        data_criacao=datetime.now(),
                        data_programada=data_inicio,
                        data_inicio=None,
                        data_conclusao=None,
                        data_atualizacao=None,
                        pmp_id=pmp_id_teste,
                        data_proxima_geracao=proxima_data,
                        frequencia_origem=frequencia,
                        numero_sequencia=1
                    )
                    
                    print("\n🔍 Verificando campos da OS antes de salvar:")
                    for campo in dir(nova_os):
                        if not campo.startswith('_') and campo not in ['metadata', 'query', 'query_class']:
                            valor = getattr(nova_os, campo)
                            if not callable(valor):
                                print(f"   - {campo}: {valor}")
                    
                    print("\n💾 Tentando salvar OS...")
                    db.session.add(nova_os)
                    db.session.flush()
                    
                    print(f"✅ OS #{nova_os.id} criada com sucesso!")
                    
                    # Verificar se a OS foi realmente salva
                    db.session.commit()
                    print("✅ Commit realizado com sucesso!")
                    
                    # Verificar se a OS existe no banco
                    os_verificacao = OrdemServico.query.get(nova_os.id)
                    if os_verificacao:
                        print(f"✅ OS #{nova_os.id} verificada no banco")
                        print(f"   - Descrição: {os_verificacao.descricao}")
                        print(f"   - PMP: {os_verificacao.pmp_id}")
                        print(f"   - Status: {os_verificacao.status}")
                    else:
                        print(f"❌ OS #{nova_os.id} não encontrada no banco após commit")
                    
                except Exception as e:
                    print(f"❌ ERRO AO CRIAR OS: {e}")
                    traceback.print_exc()
                    db.session.rollback()
            
            print("\n6️⃣ VERIFICANDO FUNÇÃO DE ATUALIZAÇÃO DE PMP...")
            
            # Buscar PMP sem data de início
            result = db.session.execute(db.text("""
                SELECT id, descricao, equipamento_id
                FROM pmps 
                WHERE data_inicio_plano IS NULL
                ORDER BY id DESC
                LIMIT 1
            """))
            
            pmp_sem_data = result.fetchone()
            
            if not pmp_sem_data:
                print("❌ Nenhuma PMP sem data de início encontrada para teste")
                return
            
            pmp_id_teste = pmp_sem_data[0]
            print(f"📋 Usando PMP {pmp_id_teste} para teste de atualização")
            
            # Simular atualização via API
            import json
            from flask import Flask
            from routes.pmp_limpo import pmp_limpo_bp
            
            test_app = Flask(__name__)
            test_app.config['SQLALCHEMY_DATABASE_URI'] = app.config['SQLALCHEMY_DATABASE_URI']
            test_app.config['SECRET_KEY'] = 'test'
            
            test_app.register_blueprint(pmp_limpo_bp)
            db.init_app(test_app)
            
            with test_app.test_client() as client:
                with test_app.app_context():
                    # Dados para atualização - definindo data de início como hoje
                    data_atualizacao = {
                        'data_inicio_plano': date.today().strftime('%Y-%m-%d')
                    }
                    
                    print(f"📅 Definindo data de início como: {data_atualizacao['data_inicio_plano']}")
                    
                    # Fazer requisição PUT para atualizar PMP
                    response = client.put(
                        f'/api/pmp/{pmp_id_teste}/atualizar',
                        data=json.dumps(data_atualizacao),
                        content_type='application/json'
                    )
                    
                    print(f"📡 Status da resposta: {response.status_code}")
                    
                    if response.status_code == 200:
                        resultado = response.get_json()
                        print(f"✅ Atualização bem-sucedida!")
                        
                        if resultado.get('campos_atualizados'):
                            print(f"📝 Campos atualizados:")
                            for campo in resultado['campos_atualizados']:
                                print(f"   - {campo}")
                                
                                # Verificar se OS foi gerada
                                if 'OS #' in campo and 'gerada automaticamente' in campo:
                                    os_id = campo.split('OS #')[1].split(' ')[0]
                                    print(f"🎉 OS #{os_id} foi gerada automaticamente!")
                                    
                                    # Verificar se a OS realmente existe
                                    os_result = db.session.execute(db.text("""
                                        SELECT id, descricao, status, prioridade, pmp_id, data_programada
                                        FROM ordens_servico 
                                        WHERE id = :os_id
                                    """), {'os_id': os_id})
                                    
                                    os_data = os_result.fetchone()
                                    
                                    if os_data:
                                        print(f"✅ OS #{os_id} confirmada no banco:")
                                        print(f"   📝 Descrição: {os_data[1]}")
                                        print(f"   📊 Status: {os_data[2]} | Prioridade: {os_data[3]}")
                                        print(f"   🔗 PMP ID: {os_data[4]}")
                                        print(f"   📅 Data programada: {os_data[5]}")
                                    else:
                                        print(f"❌ OS #{os_id} não encontrada no banco")
                        
                        if not any('OS #' in campo for campo in resultado.get('campos_atualizados', [])):
                            print(f"⚠️ Nenhuma OS foi gerada automaticamente")
                    
                    else:
                        error_text = response.get_data(as_text=True)
                        print(f"❌ Erro na atualização: {error_text}")
            
            print("\n7️⃣ DIAGNÓSTICO FINAL...")
            
            # Verificar se a data de início foi realmente salva
            result = db.session.execute(db.text("""
                SELECT data_inicio_plano
                FROM pmps 
                WHERE id = :pmp_id
            """), {'pmp_id': pmp_id_teste})
            
            data_salva = result.fetchone()
            
            if data_salva and data_salva[0]:
                print(f"✅ Data de início salva com sucesso: {data_salva[0]}")
            else:
                print(f"❌ Data de início NÃO foi salva!")
            
            # Verificar se alguma OS foi gerada para esta PMP
            result = db.session.execute(db.text("""
                SELECT COUNT(*)
                FROM ordens_servico 
                WHERE pmp_id = :pmp_id
            """), {'pmp_id': pmp_id_teste})
            
            count_os = result.fetchone()[0]
            
            if count_os > 0:
                print(f"✅ {count_os} OS geradas para a PMP {pmp_id_teste}")
            else:
                print(f"❌ Nenhuma OS gerada para a PMP {pmp_id_teste}")
            
            print("\n🎯 RESUMO DO DIAGNÓSTICO:")
            if data_salva and data_salva[0] and count_os > 0:
                print("✅ SISTEMA FUNCIONANDO CORRETAMENTE!")
                print("   - Data de início está sendo salva")
                print("   - OS está sendo gerada automaticamente")
            elif data_salva and data_salva[0]:
                print("⚠️ PROBLEMA PARCIAL:")
                print("   - Data de início está sendo salva")
                print("   - OS NÃO está sendo gerada automaticamente")
            else:
                print("❌ PROBLEMA CRÍTICO:")
                print("   - Data de início NÃO está sendo salva")
                print("   - OS NÃO está sendo gerada automaticamente")
            
    except Exception as e:
        print(f"❌ ERRO CRÍTICO: {e}")
        traceback.print_exc()

if __name__ == "__main__":
    debug_pmp_data_inicio()

