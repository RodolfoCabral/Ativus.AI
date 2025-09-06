#!/usr/bin/env python3
"""
Script FINAL CORRIGIDO para forçar geração de OS preventivas
Versão simplificada que funciona com qualquer estrutura de tabela
Execute com: heroku run python forcar_geracao_os_final.py -a ativusai
"""

import sys
import os
from datetime import datetime, date, timedelta

# Adicionar o diretório atual ao path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def forcar_geracao_os_final():
    """Versão final e simplificada da geração de OS"""
    
    print("🚀 GERAÇÃO DE OS PREVENTIVAS - VERSÃO FINAL")
    print("=" * 50)
    
    try:
        from models import db
        from app import create_app
        
        app = create_app()
        
        with app.app_context():
            # Verificar se coluna pmp_id existe em ordens_servico
            print("🔍 Verificando estrutura necessária...")
            
            try:
                result = db.session.execute(db.text("""
                    SELECT column_name 
                    FROM information_schema.columns 
                    WHERE table_name = 'ordens_servico' AND column_name = 'pmp_id'
                """))
                
                if not result.fetchone():
                    print("❌ ERRO: Coluna pmp_id não existe em ordens_servico")
                    print("💡 Execute primeiro: heroku run python migrar_banco_simples.py -a ativusai")
                    return
                
                print("✅ Estrutura do banco OK")
                
            except Exception as e:
                print(f"❌ Erro ao verificar estrutura: {e}")
                return
            
            # Buscar PMPs de forma simples
            hoje = date.today()
            print(f"\n📅 Buscando PMPs para gerar OS até {hoje}...")
            
            try:
                # Query simples usando apenas colunas básicas
                result = db.session.execute(db.text("""
                    SELECT id, equipamento_id, data_inicio_plano, 
                           COALESCE(frequencia, 'semanal') as frequencia,
                           COALESCE(usuarios_responsaveis, '[]') as usuarios_responsaveis,
                           COALESCE(num_pessoas, 1) as num_pessoas,
                           COALESCE(tempo_pessoa, 1.0) as tempo_pessoa
                    FROM pmps 
                    WHERE data_inicio_plano IS NOT NULL 
                    AND data_inicio_plano <= :hoje
                    ORDER BY data_inicio_plano
                """), {'hoje': hoje})
                
                pmps_para_gerar = result.fetchall()
                
                if not pmps_para_gerar:
                    print("❌ Nenhuma PMP encontrada com data de início <= hoje")
                    print("💡 Defina data de início nas PMPs no plano mestre")
                    return
                
                print(f"✅ Encontradas {len(pmps_para_gerar)} PMPs para processar")
                
            except Exception as e:
                print(f"❌ Erro ao buscar PMPs: {e}")
                return
            
            # Processar cada PMP de forma simples
            os_geradas = 0
            os_existentes = 0
            erros = 0
            
            for pmp_row in pmps_para_gerar:
                # Acessar dados por índice (mais simples e confiável)
                pmp_id = pmp_row[0]
                equipamento_id = pmp_row[1]
                data_inicio = pmp_row[2]
                frequencia = pmp_row[3]
                usuarios_resp = pmp_row[4]
                num_pessoas = pmp_row[5]
                tempo_pessoa = pmp_row[6]
                
                print(f"\n🔄 Processando PMP {pmp_id}")
                
                try:
                    # Verificar se já existe OS para esta PMP na data de início
                    result_check = db.session.execute(db.text("""
                        SELECT id FROM ordens_servico 
                        WHERE pmp_id = :pmp_id AND data_programada = :data_inicio
                    """), {'pmp_id': pmp_id, 'data_inicio': data_inicio})
                    
                    if result_check.fetchone():
                        print(f"  ⚠️ OS já existe para data {data_inicio}")
                        os_existentes += 1
                        continue
                    
                    # Buscar dados do equipamento
                    result_equip = db.session.execute(db.text("""
                        SELECT COALESCE(e.tag, 'Equipamento') as tag, 
                               COALESCE(e.setor_id, 1) as setor_id, 
                               COALESCE(s.filial_id, 1) as filial_id 
                        FROM equipamentos e
                        LEFT JOIN setores s ON e.setor_id = s.id
                        WHERE e.id = :equip_id
                    """), {'equip_id': equipamento_id})
                    
                    equip_data = result_equip.fetchone()
                    if not equip_data:
                        print(f"  ❌ Equipamento {equipamento_id} não encontrado")
                        erros += 1
                        continue
                    
                    equip_tag = equip_data[0]
                    setor_id = equip_data[1]
                    filial_id = equip_data[2]
                    
                    # Determinar status e usuário responsável de forma simples
                    import json
                    try:
                        if usuarios_resp and usuarios_resp != '[]':
                            usuarios_list = json.loads(usuarios_resp)
                            if usuarios_list and len(usuarios_list) > 0:
                                # Tem usuário responsável
                                if isinstance(usuarios_list[0], dict):
                                    usuario_responsavel = usuarios_list[0].get('nome', 'Técnico')
                                else:
                                    usuario_responsavel = str(usuarios_list[0])
                                status = 'programada'
                                destino = 'carteira do técnico'
                            else:
                                usuario_responsavel = None
                                status = 'aberta'
                                destino = 'chamados preventivos'
                        else:
                            usuario_responsavel = None
                            status = 'aberta'
                            destino = 'chamados preventivos'
                    except:
                        # Se der erro no JSON, assume sem usuário
                        usuario_responsavel = None
                        status = 'aberta'
                        destino = 'chamados preventivos'
                    
                    # Calcular próxima data baseada na frequência
                    freq_dias = {
                        'diaria': 1,
                        'semanal': 7,
                        'quinzenal': 14,
                        'mensal': 30,
                        'bimestral': 60,
                        'trimestral': 90,
                        'semestral': 180,
                        'anual': 365
                    }
                    
                    dias_adicionar = freq_dias.get(frequencia, 7)  # Default semanal
                    proxima_data = data_inicio + timedelta(days=dias_adicionar)
                    
                    # Criar OS com dados mínimos necessários
                    db.session.execute(db.text("""
                        INSERT INTO ordens_servico (
                            pmp_id, descricao, tipo_manutencao, prioridade, status,
                            equipamento_id, filial_id, setor_id,
                            qtd_pessoas, horas, data_programada, data_criacao,
                            data_proxima_geracao, frequencia_origem, numero_sequencia,
                            usuario_responsavel, empresa, usuario_criacao
                        ) VALUES (
                            :pmp_id, :descricao, 'preventiva', 'preventiva', :status,
                            :equipamento_id, :filial_id, :setor_id,
                            :qtd_pessoas, :horas, :data_programada, :data_criacao,
                            :data_proxima_geracao, :frequencia_origem, 1,
                            :usuario_responsavel, 'Sistema', 'Sistema PMP'
                        )
                    """), {
                        'pmp_id': pmp_id,
                        'descricao': f'PMP: Manutenção Preventiva - Equipamento {equip_tag} - Sequência #1',
                        'status': status,
                        'equipamento_id': equipamento_id,
                        'filial_id': filial_id,
                        'setor_id': setor_id,
                        'qtd_pessoas': int(num_pessoas),
                        'horas': float(tempo_pessoa),
                        'data_programada': data_inicio,
                        'data_criacao': datetime.now(),
                        'data_proxima_geracao': proxima_data,
                        'frequencia_origem': frequencia,
                        'usuario_responsavel': usuario_responsavel
                    })
                    
                    db.session.commit()
                    
                    print(f"  ✅ OS criada com sucesso - {destino}")
                    print(f"     Equipamento: {equip_tag}")
                    print(f"     Data programada: {data_inicio}")
                    print(f"     Próxima geração: {proxima_data}")
                    os_geradas += 1
                    
                except Exception as e:
                    print(f"  ❌ Erro ao criar OS: {e}")
                    db.session.rollback()
                    erros += 1
            
            # Resumo final
            print(f"\n🎉 PROCESSAMENTO CONCLUÍDO")
            print("=" * 50)
            print(f"✅ OS geradas: {os_geradas}")
            print(f"⚠️ OS já existentes: {os_existentes}")
            print(f"❌ Erros: {erros}")
            print(f"📊 Total processado: {len(pmps_para_gerar)}")
            
            if os_geradas > 0:
                print(f"\n🎯 {os_geradas} OS preventivas foram criadas!")
                print("💡 Verifique na tela de programação:")
                print("   - Seção 'Preventiva' (OS sem usuário responsável)")
                print("   - Carteira dos técnicos (OS com usuário responsável)")
                print("   - OS devem ter badge 'PMP' e informação de frequência")
            elif os_existentes > 0:
                print(f"\n⚠️ Todas as OS já existem para as datas de início")
                print("💡 Para gerar novas OS:")
                print("   - Aguarde as próximas datas baseadas na frequência")
                print("   - Ou use o botão 'Gerar OS Pendentes' na programação")
            else:
                print(f"\n❌ Nenhuma OS foi gerada")
                print("💡 Possíveis causas:")
                print("   - PMPs não têm data de início definida")
                print("   - Equipamentos não encontrados")
                print("   - Problemas na estrutura do banco")
            
    except Exception as e:
        print(f"❌ ERRO CRÍTICO: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    forcar_geracao_os_final()

