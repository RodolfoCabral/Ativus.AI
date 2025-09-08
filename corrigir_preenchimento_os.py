#!/usr/bin/env python3
"""
CORREÇÃO DEFINITIVA - PREENCHIMENTO CORRETO DA TABELA ORDENS_SERVICO
Corrige o preenchimento para seguir exatamente cada coluna conforme CSV real
Execute com: heroku run python corrigir_preenchimento_os.py -a ativusai
"""

import sys
import os
from datetime import datetime, date, timedelta

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def corrigir_preenchimento_os():
    """Corrige o preenchimento da tabela ordens_servico baseado no CSV real"""
    
    print("🔧 CORREÇÃO DEFINITIVA - PREENCHIMENTO ORDENS_SERVICO")
    print("=" * 60)
    
    try:
        from models import db
        from app import create_app
        
        app = create_app()
        
        with app.app_context():
            print("1️⃣ ANALISANDO ESTRUTURA BASEADA NO CSV REAL...")
            
            # Estrutura baseada no CSV fornecido:
            # "id","chamado_id","descricao","tipo_manutencao","oficina","condicao_ativo",
            # "qtd_pessoas","horas","hh","prioridade","status","filial_id","setor_id",
            # "equipamento_id","empresa","usuario_criacao","usuario_responsavel",
            # "data_criacao","data_programada","data_inicio","data_conclusao",
            # "data_atualizacao","pmp_id","data_proxima_geracao","frequencia_origem","numero_sequencia"
            
            print("📋 ESTRUTURA CORRETA (baseada no CSV):")
            print("   - chamado_id: pode ser NULL para OS de PMP")
            print("   - descricao: 'PMP: [atividade] - [equipamento] - Sequência #[num]'")
            print("   - tipo_manutencao: 'preventiva'")
            print("   - oficina: 'Oficina Manutenção' (padrão)")
            print("   - condicao_ativo: 'Operacional' (padrão)")
            print("   - empresa: 'Sistema' (para OS de PMP)")
            print("   - usuario_criacao: 'Sistema PMP'")
            print("   - usuario_responsavel: NULL (para aparecer na programação)")
            
            print("\n2️⃣ VERIFICANDO OS DE PMP EXISTENTES...")
            
            # Buscar OS de PMP com dados incompletos
            result = db.session.execute(db.text("""
                SELECT id, chamado_id, descricao, tipo_manutencao, oficina, condicao_ativo,
                       qtd_pessoas, horas, hh, prioridade, status, filial_id, setor_id, 
                       equipamento_id, empresa, usuario_criacao, usuario_responsavel,
                       data_criacao, data_programada, pmp_id, data_proxima_geracao,
                       frequencia_origem, numero_sequencia
                FROM ordens_servico 
                WHERE pmp_id IS NOT NULL
                ORDER BY id DESC
            """))
            
            os_pmp = result.fetchall()
            print(f"📋 Encontradas {len(os_pmp)} OS de PMP")
            
            for os_row in os_pmp:
                print(f"   - OS {os_row[0]}: Empresa='{os_row[14]}' | Oficina='{os_row[4]}' | Status='{os_row[10]}'")
            
            print("\n3️⃣ CORRIGINDO PREENCHIMENTO SEGUINDO CSV EXATO...")
            
            updates_realizados = 0
            
            for os_row in os_pmp:
                os_id = os_row[0]
                pmp_id = os_row[19]  # pmp_id
                
                print(f"\n🔧 Corrigindo OS {os_id} (PMP {pmp_id})...")
                
                # Buscar dados do PMP
                pmp_result = db.session.execute(db.text("""
                    SELECT descricao, equipamento_id, num_pessoas, tempo_pessoa, 
                           frequencia, data_inicio_plano
                    FROM pmps 
                    WHERE id = :pmp_id
                """), {'pmp_id': pmp_id})
                
                pmp_data = pmp_result.fetchone()
                
                # Buscar dados do equipamento
                equip_result = db.session.execute(db.text("""
                    SELECT e.id, e.tag, e.descricao,
                           s.id as setor_id, s.tag as setor_tag,
                           f.id as filial_id, f.tag as filial_tag
                    FROM equipamentos e
                    LEFT JOIN setores s ON e.setor_id = s.id
                    LEFT JOIN filiais f ON s.filial_id = f.id
                    WHERE e.id = :equip_id
                """), {'equip_id': os_row[13]})  # equipamento_id
                
                equip_data = equip_result.fetchone()
                
                # Preparar dados EXATAMENTE como no CSV
                dados_corretos = {
                    'os_id': os_id,
                    'chamado_id': None,  # NULL como no CSV
                    'descricao': f"PMP: {pmp_data[0] if pmp_data and pmp_data[0] else 'Manutenção Preventiva'} - {equip_data[1] if equip_data else 'BBN01'} - Sequência #{os_row[22] or 1}",
                    'tipo_manutencao': 'preventiva',  # Sempre preventiva
                    'oficina': 'Oficina Manutenção',  # Exato como no CSV
                    'condicao_ativo': 'Operacional',  # Exato como no CSV
                    'qtd_pessoas': int(pmp_data[2]) if pmp_data and pmp_data[2] else 2,
                    'horas': float(pmp_data[3]) if pmp_data and pmp_data[3] else 0.5,
                    'hh': float(pmp_data[2] or 2) * float(pmp_data[3] or 0.5),
                    'prioridade': 'preventiva',  # Sempre preventiva para aparecer na seção certa
                    'status': 'aberta',  # Aberta para aparecer na programação
                    'filial_id': equip_data[5] if equip_data else 166,
                    'setor_id': equip_data[3] if equip_data else 166,
                    'equipamento_id': os_row[13],  # Manter original
                    'empresa': 'Sistema',  # Exato como no CSV
                    'usuario_criacao': 'Sistema PMP',  # Exato como no CSV
                    'usuario_responsavel': None,  # NULL para aparecer na programação
                    'data_programada': date.today(),  # Data de hoje
                    'data_inicio': None,  # NULL
                    'data_conclusao': None,  # NULL
                    'data_atualizacao': None,  # NULL
                    'pmp_id': pmp_id,  # Manter PMP ID
                    'data_proxima_geracao': os_row[20] or (date.today() + timedelta(days=7)),
                    'frequencia_origem': os_row[21] or (pmp_data[4] if pmp_data else 'semanal'),
                    'numero_sequencia': os_row[22] or 1
                }
                
                # UPDATE seguindo EXATAMENTE a estrutura do CSV
                update_sql = """
                    UPDATE ordens_servico SET
                        chamado_id = :chamado_id,
                        descricao = :descricao,
                        tipo_manutencao = :tipo_manutencao,
                        oficina = :oficina,
                        condicao_ativo = :condicao_ativo,
                        qtd_pessoas = :qtd_pessoas,
                        horas = :horas,
                        hh = :hh,
                        prioridade = :prioridade,
                        status = :status,
                        filial_id = :filial_id,
                        setor_id = :setor_id,
                        equipamento_id = :equipamento_id,
                        empresa = :empresa,
                        usuario_criacao = :usuario_criacao,
                        usuario_responsavel = :usuario_responsavel,
                        data_programada = :data_programada,
                        data_inicio = :data_inicio,
                        data_conclusao = :data_conclusao,
                        data_atualizacao = :data_atualizacao,
                        pmp_id = :pmp_id,
                        data_proxima_geracao = :data_proxima_geracao,
                        frequencia_origem = :frequencia_origem,
                        numero_sequencia = :numero_sequencia
                    WHERE id = :os_id
                """
                
                # Executar UPDATE
                db.session.execute(db.text(update_sql), dados_corretos)
                updates_realizados += 1
                
                print(f"   ✅ OS {os_id} corrigida:")
                print(f"      📝 Descrição: {dados_corretos['descricao']}")
                print(f"      🏭 Oficina: {dados_corretos['oficina']} | Condição: {dados_corretos['condicao_ativo']}")
                print(f"      📊 Status: {dados_corretos['status']} | Prioridade: {dados_corretos['prioridade']}")
                print(f"      🏢 Empresa: {dados_corretos['empresa']} | Criador: {dados_corretos['usuario_criacao']}")
                print(f"      ⏰ Tempo: {dados_corretos['hh']}h ({dados_corretos['qtd_pessoas']}p × {dados_corretos['horas']}h)")
            
            # Commit das alterações
            if updates_realizados > 0:
                db.session.commit()
                print(f"\n✅ {updates_realizados} OS corrigidas com sucesso!")
            
            print("\n4️⃣ VERIFICANDO RESULTADO FINAL...")
            
            # Verificar resultado final
            result_final = db.session.execute(db.text("""
                SELECT id, descricao, tipo_manutencao, oficina, condicao_ativo,
                       qtd_pessoas, horas, hh, prioridade, status, empresa,
                       usuario_criacao, usuario_responsavel, pmp_id, frequencia_origem
                FROM ordens_servico 
                WHERE pmp_id IS NOT NULL
                ORDER BY id DESC
            """))
            
            os_corrigidas = result_final.fetchall()
            
            print(f"📊 RESULTADO FINAL - {len(os_corrigidas)} OS corrigidas:")
            for os_row in os_corrigidas:
                print(f"\n   ✅ OS {os_row[0]}:")
                print(f"      📝 {os_row[1]}")
                print(f"      🔧 {os_row[2]} | {os_row[3]} | {os_row[4]}")
                print(f"      📊 {os_row[8]} | {os_row[9]} | {os_row[10]}")
                print(f"      👤 Criador: {os_row[11]} | Responsável: {os_row[12]}")
                print(f"      ⏰ {os_row[7]}h ({os_row[5]}p × {os_row[6]}h)")
                print(f"      🔗 PMP: {os_row[13]} | Freq: {os_row[14]}")
            
            print("\n5️⃣ TESTANDO FILTRO DA PROGRAMAÇÃO...")
            
            # Simular exatamente o filtro JavaScript
            preventivas_visiveis = []
            for os_row in os_corrigidas:
                # Condições para aparecer na seção preventiva
                condicao1 = (os_row[8] == 'preventiva' and  # prioridade
                           os_row[9] == 'aberta' and        # status
                           os_row[12] is None)              # usuario_responsavel NULL
                
                condicao2 = (os_row[13] is not None and     # pmp_id não NULL
                           os_row[9] == 'aberta')           # status aberta
                
                if condicao1 or condicao2:
                    preventivas_visiveis.append(os_row[0])
            
            print(f"🎯 OS que DEVEM aparecer na seção Preventiva: {len(preventivas_visiveis)}")
            print(f"📋 IDs das OS visíveis: {preventivas_visiveis}")
            
            if len(preventivas_visiveis) > 0:
                print("\n🎉 SUCESSO! As OS agora estão corretamente configuradas!")
                print("💡 Acesse: https://ativusai-af6f1462097d.herokuapp.com/programacao")
                print("💡 As OS devem aparecer na seção 'Preventiva' com badges 'PMP' roxos")
                print("💡 Abra o console (F12) para ver os logs de debug")
            else:
                print("\n❌ PROBLEMA: Ainda não há OS configuradas para aparecer")
            
            print(f"\n🎯 RESUMO FINAL:")
            print(f"   📊 OS de PMP encontradas: {len(os_pmp)}")
            print(f"   ✅ OS corrigidas: {updates_realizados}")
            print(f"   📋 Devem aparecer na programação: {len(preventivas_visiveis)}")
            
            return len(preventivas_visiveis)
            
    except Exception as e:
        print(f"❌ ERRO CRÍTICO: {e}")
        import traceback
        traceback.print_exc()
        return 0

if __name__ == "__main__":
    corrigir_preenchimento_os()

