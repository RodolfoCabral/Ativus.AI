#!/usr/bin/env python3
"""
Script CORRIGIDO para forçar geração de OS preventivas
Usa apenas colunas que existem na tabela pmps
Execute com: heroku run python forcar_geracao_os_corrigido.py -a ativusai
"""

import sys
import os
from datetime import datetime, date, timedelta

# Adicionar o diretório atual ao path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def forcar_geracao_os_corrigido():
    """Força a geração de OS usando apenas colunas existentes"""
    
    print("🚀 FORÇANDO GERAÇÃO DE OS PREVENTIVAS (VERSÃO CORRIGIDA)")
    print("=" * 60)
    
    try:
        from models import db
        from app import create_app
        
        app = create_app()
        
        with app.app_context():
            # Primeiro, verificar quais colunas existem
            print("🔍 Verificando colunas disponíveis...")
            
            try:
                result = db.session.execute(db.text("""
                    SELECT column_name 
                    FROM information_schema.columns 
                    WHERE table_name = 'pmps'
                """))
                
                colunas_disponiveis = [row[0] for row in result]
                print(f"✅ Colunas encontradas: {', '.join(colunas_disponiveis)}")
                
                # Verificar se coluna pmp_id existe em ordens_servico
                result = db.session.execute(db.text("""
                    SELECT column_name 
                    FROM information_schema.columns 
                    WHERE table_name = 'ordens_servico' AND column_name = 'pmp_id'
                """))
                
                if not result.fetchone():
                    print("❌ ERRO: Coluna pmp_id não existe em ordens_servico")
                    print("💡 Execute primeiro: heroku run python migrar_banco_simples.py -a ativusai")
                    return
                
            except Exception as e:
                print(f"❌ Erro ao verificar colunas: {e}")
                return
            
            # Construir query baseada nas colunas disponíveis
            colunas_select = ['id', 'equipamento_id']
            
            # Adicionar colunas opcionais se existirem
            colunas_opcionais = {
                'data_inicio_plano': 'data_inicio_plano',
                'frequencia': 'frequencia', 
                'usuarios_responsaveis': 'usuarios_responsaveis',
                'num_pessoas': 'num_pessoas',
                'tempo_pessoa': 'tempo_pessoa',
                'atividade': 'atividade',
                'descricao': 'descricao',
                'nome': 'nome'
            }
            
            for coluna, alias in colunas_opcionais.items():
                if coluna in colunas_disponiveis:
                    colunas_select.append(f"{coluna} as {alias}")
            
            # Se não tem data_inicio_plano, não pode continuar
            if 'data_inicio_plano' not in colunas_disponiveis:
                print("❌ ERRO: Coluna data_inicio_plano não existe na tabela pmps")
                print("💡 Execute primeiro a migração do banco")
                return
            
            query = f"""
                SELECT {', '.join(colunas_select)}
                FROM pmps 
                WHERE data_inicio_plano IS NOT NULL 
                AND data_inicio_plano <= :hoje
                ORDER BY data_inicio_plano
            """
            
            hoje = date.today()
            print(f"\n📅 Buscando PMPs para gerar OS até {hoje}...")
            
            try:
                result = db.session.execute(db.text(query), {'hoje': hoje})
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
            
            for pmp_data in pmps_para_gerar:
                # Converter resultado em dicionário
                pmp = dict(zip([desc[0] for desc in result.description], pmp_data))
                
                pmp_id = pmp['id']
                equipamento_id = pmp['equipamento_id']
                data_inicio = pmp.get('data_inicio_plano')
                frequencia = pmp.get('frequencia', 'semanal')
                usuarios_resp = pmp.get('usuarios_responsaveis', '[]')
                num_pessoas = pmp.get('num_pessoas', 1)
                tempo_pessoa = pmp.get('tempo_pessoa', 1.0)
                
                # Tentar obter descrição da PMP
                descricao_pmp = (pmp.get('atividade') or 
                               pmp.get('descricao') or 
                               pmp.get('nome') or 
                               f'PMP ID {pmp_id}')
                
                print(f"\n🔄 Processando PMP {pmp_id}: {descricao_pmp}")
                
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
                        SELECT e.tag, e.setor_id, s.filial_id 
                        FROM equipamentos e
                        LEFT JOIN setores s ON e.setor_id = s.id
                        WHERE e.id = :equip_id
                    """), {'equip_id': equipamento_id})
                    
                    equip_data = result_equip.fetchone()
                    if not equip_data:
                        print(f"  ❌ Equipamento {equipamento_id} não encontrado")
                        erros += 1
                        continue
                    
                    equip_tag, setor_id, filial_id = equip_data
                    
                    # Determinar status e usuário responsável
                    import json
                    try:
                        usuarios_list = json.loads(usuarios_resp) if usuarios_resp and usuarios_resp != '[]' else []
                    except:
                        usuarios_list = []
                    
                    if usuarios_list and len(usuarios_list) > 0:
                        # Tem usuário responsável - vai para carteira
                        if isinstance(usuarios_list[0], dict):
                            usuario_responsavel = usuarios_list[0].get('nome', str(usuarios_list[0]))
                        else:
                            usuario_responsavel = str(usuarios_list[0])
                        status = 'programada'
                        destino = 'carteira do técnico'
                    else:
                        # Sem usuário - vai para chamados
                        usuario_responsavel = None
                        status = 'aberta'
                        destino = 'chamados preventivos'
                    
                    # Calcular próxima data baseada na frequência
                    freq_map = {
                        'diaria': 1,
                        'semanal': 7,
                        'quinzenal': 14,
                        'mensal': 30,
                        'bimestral': 60,
                        'trimestral': 90,
                        'semestral': 180,
                        'anual': 365
                    }
                    
                    dias_adicionar = freq_map.get(frequencia, 7)  # Default semanal
                    proxima_data = data_inicio + timedelta(days=dias_adicionar)
                    
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
                        'descricao': f'PMP: {descricao_pmp} - Sequência #1',
                        'status': status,
                        'equipamento_id': equipamento_id,
                        'filial_id': filial_id or 1,
                        'setor_id': setor_id or 1,
                        'qtd_pessoas': num_pessoas or 1,
                        'horas': float(tempo_pessoa or 1.0),
                        'data_programada': data_inicio,
                        'data_criacao': datetime.now(),
                        'data_proxima_geracao': proxima_data,
                        'frequencia_origem': frequencia,
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
            print("=" * 60)
            print(f"✅ OS geradas: {os_geradas}")
            print(f"⚠️ OS já existentes: {os_existentes}")
            print(f"❌ Erros: {erros}")
            print(f"📊 Total processado: {len(pmps_para_gerar)}")
            
            if os_geradas > 0:
                print(f"\n🎯 {os_geradas} OS preventivas foram criadas!")
                print("💡 Verifique na tela de programação:")
                print("   - Seção 'Preventiva' (OS sem usuário responsável)")
                print("   - Carteira dos técnicos (OS com usuário responsável)")
            elif os_existentes > 0:
                print(f"\n⚠️ Todas as OS já existem para as datas de início")
                print("💡 Para gerar novas OS, aguarde as próximas datas baseadas na frequência")
            else:
                print(f"\n❌ Nenhuma OS foi gerada")
                print("💡 Verifique se as PMPs têm data de início definida")
            
    except Exception as e:
        print(f"❌ ERRO CRÍTICO: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    forcar_geracao_os_corrigido()

