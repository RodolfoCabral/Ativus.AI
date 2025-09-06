#!/usr/bin/env python3
"""
Script para forçar geração de OS preventivas
Execute com: heroku run python forcar_geracao_os.py -a ativusai
"""

import sys
import os
from datetime import datetime, date, timedelta

# Adicionar o diretório atual ao path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def forcar_geracao_os():
    """Força a geração de OS para PMPs que deveriam ter gerado"""
    
    print("🚀 FORÇANDO GERAÇÃO DE OS PREVENTIVAS")
    print("=" * 50)
    
    try:
        from models import db
        from app import create_app
        
        app = create_app()
        
        with app.app_context():
            # Verificar se as tabelas e colunas existem
            print("🔍 Verificando estrutura do banco...")
            
            try:
                # Verificar se coluna pmp_id existe
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
            
            # Buscar PMPs que deveriam gerar OS
            hoje = date.today()
            
            print(f"\n📅 Buscando PMPs para gerar OS até {hoje}...")
            
            try:
                result = db.session.execute(db.text("""
                    SELECT id, atividade, data_inicio_plano, frequencia, equipamento_id,
                           usuarios_responsaveis, num_pessoas, tempo_pessoa
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
            
            # Processar cada PMP
            os_geradas = 0
            os_existentes = 0
            erros = 0
            
            for pmp in pmps_para_gerar:
                pmp_id, atividade, data_inicio, frequencia, equipamento_id, usuarios_resp, num_pessoas, tempo_pessoa = pmp
                
                print(f"\n🔄 Processando PMP {pmp_id}: {atividade}")
                
                try:
                    # Verificar se já existe OS para esta PMP na data de início
                    result = db.session.execute(db.text("""
                        SELECT id FROM ordens_servico 
                        WHERE pmp_id = :pmp_id AND data_programada = :data_inicio
                    """), {'pmp_id': pmp_id, 'data_inicio': data_inicio})
                    
                    if result.fetchone():
                        print(f"  ⚠️ OS já existe para data {data_inicio}")
                        os_existentes += 1
                        continue
                    
                    # Buscar dados do equipamento
                    result = db.session.execute(db.text("""
                        SELECT e.tag, e.setor_id, s.filial_id 
                        FROM equipamentos e
                        LEFT JOIN setores s ON e.setor_id = s.id
                        WHERE e.id = :equip_id
                    """), {'equip_id': equipamento_id})
                    
                    equip_data = result.fetchone()
                    if not equip_data:
                        print(f"  ❌ Equipamento {equipamento_id} não encontrado")
                        erros += 1
                        continue
                    
                    equip_tag, setor_id, filial_id = equip_data
                    
                    # Determinar status e usuário responsável
                    usuarios_responsaveis = usuarios_resp or '[]'
                    
                    # Tentar fazer parse do JSON
                    import json
                    try:
                        usuarios_list = json.loads(usuarios_responsaveis) if usuarios_responsaveis != '[]' else []
                    except:
                        usuarios_list = []
                    
                    if usuarios_list and len(usuarios_list) > 0:
                        # Tem usuário responsável - vai para carteira
                        usuario_responsavel = usuarios_list[0].get('nome', '') if isinstance(usuarios_list[0], dict) else str(usuarios_list[0])
                        status = 'programada'
                        destino = 'carteira do técnico'
                    else:
                        # Sem usuário - vai para chamados
                        usuario_responsavel = None
                        status = 'aberta'
                        destino = 'chamados preventivos'
                    
                    # Calcular próxima data
                    freq = frequencia or 'semanal'
                    if freq == 'diaria':
                        proxima_data = data_inicio + timedelta(days=1)
                    elif freq == 'semanal':
                        proxima_data = data_inicio + timedelta(days=7)
                    elif freq == 'quinzenal':
                        proxima_data = data_inicio + timedelta(days=14)
                    elif freq == 'mensal':
                        proxima_data = data_inicio + timedelta(days=30)
                    else:
                        proxima_data = data_inicio + timedelta(days=7)  # Default semanal
                    
                    # Criar OS
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
                        'descricao': f'PMP: {atividade} - Sequência #1',
                        'status': status,
                        'equipamento_id': equipamento_id,
                        'filial_id': filial_id or 1,
                        'setor_id': setor_id or 1,
                        'qtd_pessoas': num_pessoas or 1,
                        'horas': tempo_pessoa or 1.0,
                        'data_programada': data_inicio,
                        'data_criacao': datetime.now(),
                        'data_proxima_geracao': proxima_data,
                        'frequencia_origem': freq,
                        'usuario_responsavel': usuario_responsavel
                    })
                    
                    db.session.commit()
                    
                    print(f"  ✅ OS criada com sucesso - {destino}")
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
                print("💡 Verifique na tela de programação")
            
    except Exception as e:
        print(f"❌ ERRO CRÍTICO: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    forcar_geracao_os()

