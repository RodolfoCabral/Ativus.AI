#!/usr/bin/env python3
"""
SOLUÇÃO DEFINITIVA - GERAÇÃO DE OS PREVENTIVAS
Esta versão analisa a estrutura REAL da tabela e se adapta automaticamente
Execute com: heroku run python solucao_definitiva_os.py -a ativusai
"""

import sys
import os
from datetime import datetime, date, timedelta

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def solucao_definitiva_os():
    """Solução que se adapta à estrutura real da tabela"""
    
    print("🚀 SOLUÇÃO DEFINITIVA - GERAÇÃO DE OS PREVENTIVAS")
    print("=" * 60)
    
    try:
        from models import db
        from app import create_app
        
        app = create_app()
        
        with app.app_context():
            print("🔍 ANALISANDO ESTRUTURA REAL DA TABELA...")
            
            # 1. DESCOBRIR ESTRUTURA REAL DA TABELA ordens_servico
            try:
                result = db.session.execute(db.text("""
                    SELECT column_name, data_type, is_nullable, column_default
                    FROM information_schema.columns 
                    WHERE table_name = 'ordens_servico'
                    ORDER BY ordinal_position
                """))
                
                colunas_info = result.fetchall()
                colunas_obrigatorias = []
                colunas_opcionais = []
                
                print("📊 ESTRUTURA DA TABELA ordens_servico:")
                for col in colunas_info:
                    nome, tipo, nullable, default = col
                    if nullable == 'NO' and nome != 'id':  # Obrigatória (exceto ID que é auto)
                        colunas_obrigatorias.append(nome)
                        print(f"   ✅ {nome} ({tipo}) - OBRIGATÓRIO")
                    else:
                        colunas_opcionais.append(nome)
                        print(f"   ⚪ {nome} ({tipo}) - opcional")
                
                print(f"\n📋 RESUMO: {len(colunas_obrigatorias)} obrigatórias, {len(colunas_opcionais)} opcionais")
                
            except Exception as e:
                print(f"❌ Erro ao analisar estrutura: {e}")
                return
            
            # 2. VERIFICAR SE MIGRAÇÃO FOI FEITA
            if 'pmp_id' not in colunas_obrigatorias and 'pmp_id' not in colunas_opcionais:
                print("❌ ERRO: Coluna pmp_id não existe!")
                print("💡 Execute primeiro: heroku run python migrar_banco_simples.py -a ativusai")
                return
            
            # 3. BUSCAR PMPs PARA PROCESSAR
            hoje = date.today()
            print(f"\n📅 Buscando PMPs para gerar OS até {hoje}...")
            
            try:
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
            
            # 4. PROCESSAR CADA PMP
            os_geradas = 0
            os_existentes = 0
            erros = 0
            
            for pmp_row in pmps_para_gerar:
                pmp_id = pmp_row[0]
                equipamento_id = pmp_row[1]
                data_inicio = pmp_row[2]
                frequencia = pmp_row[3]
                usuarios_resp = pmp_row[4]
                num_pessoas = pmp_row[5]
                tempo_pessoa = pmp_row[6]
                
                print(f"\n🔄 Processando PMP {pmp_id}")
                
                try:
                    # Verificar se já existe OS
                    result_check = db.session.execute(db.text("""
                        SELECT id FROM ordens_servico 
                        WHERE pmp_id = :pmp_id AND data_programada = :data_inicio
                    """), {'pmp_id': pmp_id, 'data_inicio': data_inicio})
                    
                    if result_check.fetchone():
                        print(f"  ⚠️ OS já existe para data {data_inicio}")
                        os_existentes += 1
                        continue
                    
                    # Buscar dados do equipamento
                    try:
                        result_equip = db.session.execute(db.text("""
                            SELECT COALESCE(e.tag, :default_tag) as tag, 
                                   COALESCE(e.setor_id, 1) as setor_id
                            FROM equipamentos e
                            WHERE e.id = :equip_id
                        """), {'equip_id': equipamento_id, 'default_tag': f'Equipamento {equipamento_id}'})
                        
                        equip_data = result_equip.fetchone()
                        if equip_data:
                            equip_tag = equip_data[0]
                            setor_id = equip_data[1]
                        else:
                            equip_tag = f'Equipamento {equipamento_id}'
                            setor_id = 1
                    except:
                        equip_tag = f'Equipamento {equipamento_id}'
                        setor_id = 1
                    
                    # Buscar filial
                    try:
                        result_setor = db.session.execute(db.text("""
                            SELECT COALESCE(filial_id, 1) as filial_id
                            FROM setores WHERE id = :setor_id
                        """), {'setor_id': setor_id})
                        setor_data = result_setor.fetchone()
                        filial_id = setor_data[0] if setor_data else 1
                    except:
                        filial_id = 1
                    
                    # Determinar usuário responsável
                    import json
                    try:
                        if usuarios_resp and usuarios_resp != '[]':
                            usuarios_list = json.loads(usuarios_resp)
                            if usuarios_list and len(usuarios_list) > 0:
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
                        usuario_responsavel = None
                        status = 'aberta'
                        destino = 'chamados preventivos'
                    
                    # Calcular próxima data
                    freq_dias = {
                        'diaria': 1, 'diario': 1,
                        'semanal': 7, 'quinzenal': 14, 'mensal': 30,
                        'bimestral': 60, 'trimestral': 90, 'semestral': 180, 'anual': 365
                    }
                    dias_adicionar = freq_dias.get(frequencia, 7)
                    proxima_data = data_inicio + timedelta(days=dias_adicionar)
                    
                    # 5. MONTAR INSERT DINAMICAMENTE BASEADO NA ESTRUTURA REAL
                    valores = {
                        'pmp_id': pmp_id,
                        'descricao': f'PMP: Manutenção Preventiva - {equip_tag} - Sequência #1',
                        'equipamento_id': equipamento_id,
                        'data_programada': data_inicio,
                        'data_criacao': datetime.now(),
                        'status': status,
                        'usuario_responsavel': usuario_responsavel
                    }
                    
                    # Adicionar campos baseado no que existe na tabela
                    if 'tipo_manutencao' in colunas_obrigatorias or 'tipo_manutencao' in colunas_opcionais:
                        valores['tipo_manutencao'] = 'preventiva'
                    
                    if 'prioridade' in colunas_obrigatorias or 'prioridade' in colunas_opcionais:
                        valores['prioridade'] = 'preventiva'
                    
                    if 'filial_id' in colunas_obrigatorias or 'filial_id' in colunas_opcionais:
                        valores['filial_id'] = filial_id
                    
                    if 'setor_id' in colunas_obrigatorias or 'setor_id' in colunas_opcionais:
                        valores['setor_id'] = setor_id
                    
                    if 'oficina' in colunas_obrigatorias or 'oficina' in colunas_opcionais:
                        valores['oficina'] = 'Oficina Manutenção'
                    
                    if 'qtd_pessoas' in colunas_obrigatorias or 'qtd_pessoas' in colunas_opcionais:
                        valores['qtd_pessoas'] = int(num_pessoas)
                    
                    if 'horas' in colunas_obrigatorias or 'horas' in colunas_opcionais:
                        valores['horas'] = float(tempo_pessoa)
                    
                    if 'hh' in colunas_obrigatorias or 'hh' in colunas_opcionais:
                        valores['hh'] = float(tempo_pessoa) * int(num_pessoas)
                    
                    if 'empresa' in colunas_obrigatorias or 'empresa' in colunas_opcionais:
                        valores['empresa'] = 'Sistema'
                    
                    if 'usuario_criacao' in colunas_obrigatorias or 'usuario_criacao' in colunas_opcionais:
                        valores['usuario_criacao'] = 'Sistema PMP'
                    
                    if 'condicao_ativo' in colunas_obrigatorias or 'condicao_ativo' in colunas_opcionais:
                        valores['condicao_ativo'] = 'Operacional'
                    
                    if 'data_proxima_geracao' in colunas_obrigatorias or 'data_proxima_geracao' in colunas_opcionais:
                        valores['data_proxima_geracao'] = proxima_data
                    
                    if 'frequencia_origem' in colunas_obrigatorias or 'frequencia_origem' in colunas_opcionais:
                        valores['frequencia_origem'] = frequencia
                    
                    if 'numero_sequencia' in colunas_obrigatorias or 'numero_sequencia' in colunas_opcionais:
                        valores['numero_sequencia'] = 1
                    
                    # Montar SQL dinamicamente
                    colunas = ', '.join(valores.keys())
                    placeholders = ', '.join([f':{k}' for k in valores.keys()])
                    
                    sql = f"""
                        INSERT INTO ordens_servico ({colunas})
                        VALUES ({placeholders})
                    """
                    
                    # Executar INSERT
                    db.session.execute(db.text(sql), valores)
                    db.session.commit()
                    
                    print(f"  ✅ OS criada com sucesso - {destino}")
                    print(f"     Equipamento: {equip_tag}")
                    print(f"     Data: {data_inicio} | Próxima: {proxima_data}")
                    print(f"     Campos incluídos: {len(valores)}")
                    os_geradas += 1
                    
                except Exception as e:
                    print(f"  ❌ Erro ao criar OS: {e}")
                    db.session.rollback()
                    erros += 1
            
            # 6. RESUMO FINAL
            print(f"\n🎉 PROCESSAMENTO CONCLUÍDO")
            print("=" * 60)
            print(f"✅ OS geradas: {os_geradas}")
            print(f"⚠️ OS já existentes: {os_existentes}")
            print(f"❌ Erros: {erros}")
            print(f"📊 Total processado: {len(pmps_para_gerar)}")
            
            if os_geradas > 0:
                print(f"\n🎯 {os_geradas} OS preventivas criadas com SUCESSO!")
                print("💡 Acesse a tela de programação para ver as OS")
                print("   - Seção 'Preventiva' (sem usuário responsável)")
                print("   - Carteira dos técnicos (com usuário responsável)")
                
                # Listar OS criadas
                try:
                    result_os = db.session.execute(db.text("""
                        SELECT id, descricao, status, data_programada
                        FROM ordens_servico 
                        WHERE pmp_id IS NOT NULL
                        AND DATE(data_criacao) = :hoje
                        ORDER BY id DESC
                        LIMIT 5
                    """), {'hoje': datetime.now().date()})
                    
                    print(f"\n📋 OS criadas hoje:")
                    for os_row in result_os:
                        print(f"   - OS {os_row[0]}: {os_row[2]} | {os_row[3]}")
                        
                except Exception:
                    pass
                    
            print(f"\n🎉 SOLUÇÃO DEFINITIVA EXECUTADA!")
            print("=" * 60)
            
    except Exception as e:
        print(f"❌ ERRO CRÍTICO: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    solucao_definitiva_os()

