#!/usr/bin/env python3
"""
Script para diagnosticar e corrigir o problema da PMP-02-BBN01
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from datetime import datetime, date, timedelta
from models import db
from app import create_app

def calcular_datas_esperadas(data_inicio, frequencia):
    """Calcula as datas esperadas baseado na frequência"""
    datas = []
    data_atual = data_inicio
    hoje = date.today()
    
    # Primeira data sempre é a data de início
    datas.append(data_atual)
    
    # Calcular próximas datas até hoje
    while data_atual < hoje:
        if frequencia == 'semanal':
            data_atual += timedelta(weeks=1)
        elif frequencia == 'mensal':
            if data_atual.month == 12:
                data_atual = data_atual.replace(year=data_atual.year + 1, month=1)
            else:
                try:
                    data_atual = data_atual.replace(month=data_atual.month + 1)
                except ValueError:
                    # Dia não existe no próximo mês
                    next_month = data_atual.replace(month=data_atual.month + 1, day=1)
                    last_day = (next_month.replace(month=next_month.month + 1) - timedelta(days=1)).day
                    data_atual = next_month.replace(day=min(data_atual.day, last_day))
        else:
            # Default semanal
            data_atual += timedelta(weeks=1)
        
        if data_atual <= hoje:
            datas.append(data_atual)
    
    return datas

def diagnosticar_pmp():
    """Diagnostica o problema da PMP-02-BBN01"""
    try:
        print("🔍 DIAGNÓSTICO DA PMP-02-BBN01")
        print("=" * 50)
        
        # Buscar PMP-02-BBN01
        from models.pmp_limpo import PMP
        pmp = db.session.execute(
            "SELECT * FROM pmps WHERE codigo LIKE '%PMP-02%' OR codigo LIKE '%BBN01%' OR atividade LIKE '%BBN01%'"
        ).fetchone()
        
        if not pmp:
            print("❌ PMP-02-BBN01 não encontrada no banco")
            # Buscar todas as PMPs para debug
            pmps = db.session.execute("SELECT id, codigo, atividade, frequencia, data_inicio_plano FROM pmps LIMIT 10").fetchall()
            print("\n📋 PMPs encontradas:")
            for p in pmps:
                print(f"  ID: {p[0]}, Código: {p[1]}, Atividade: {p[2]}, Freq: {p[3]}, Início: {p[4]}")
            return
        
        print(f"✅ PMP encontrada:")
        print(f"  ID: {pmp[0]}")
        print(f"  Código: {pmp[1]}")
        print(f"  Atividade: {pmp[2]}")
        print(f"  Frequência: {pmp[3]}")
        print(f"  Data Início: {pmp[4] if len(pmp) > 4 else 'N/A'}")
        
        # Verificar se tem data de início
        data_inicio_plano = None
        if len(pmp) > 4 and pmp[4]:
            if isinstance(pmp[4], str):
                data_inicio_plano = datetime.strptime(pmp[4], '%Y-%m-%d').date()
            else:
                data_inicio_plano = pmp[4]
        
        if not data_inicio_plano:
            print("❌ PMP não possui data de início definida")
            return
        
        print(f"📅 Data de início do plano: {data_inicio_plano}")
        
        # Calcular datas esperadas
        frequencia = pmp[3] or 'semanal'
        datas_esperadas = calcular_datas_esperadas(data_inicio_plano, frequencia)
        
        print(f"\n📊 ANÁLISE DE DATAS (Frequência: {frequencia})")
        print(f"  Data início: 05/09/2025")
        print(f"  Datas esperadas até hoje:")
        for i, data in enumerate(datas_esperadas, 1):
            print(f"    {i}. {data.strftime('%d/%m/%Y')} ({data.strftime('%A')})")
        
        # Buscar OS existentes
        from assets_models import OrdemServico
        os_existentes = db.session.execute(
            f"SELECT id, descricao, data_programada, status, pmp_id FROM ordens_servico WHERE pmp_id = {pmp[0]}"
        ).fetchall()
        
        print(f"\n📋 OS EXISTENTES ({len(os_existentes)} encontradas):")
        os_por_data = {}
        for os in os_existentes:
            data_prog = os[2]
            if isinstance(data_prog, str):
                data_prog = datetime.strptime(data_prog, '%Y-%m-%d').date()
            os_por_data[data_prog] = os
            print(f"  OS #{os[0]}: {data_prog.strftime('%d/%m/%Y')} - Status: {os[3]}")
        
        # Identificar OS faltantes
        print(f"\n❌ OS FALTANTES:")
        os_faltantes = []
        for i, data_esperada in enumerate(datas_esperadas, 1):
            if data_esperada not in os_por_data:
                os_faltantes.append((i, data_esperada))
                print(f"  Sequência #{i}: {data_esperada.strftime('%d/%m/%Y')} - FALTANTE")
        
        print(f"\n📈 RESUMO:")
        print(f"  Total esperado: {len(datas_esperadas)} OS")
        print(f"  Total existente: {len(os_existentes)} OS")
        print(f"  Total faltante: {len(os_faltantes)} OS")
        
        return {
            'pmp_id': pmp[0],
            'pmp_codigo': pmp[1],
            'pmp_atividade': pmp[2],
            'frequencia': frequencia,
            'data_inicio': data_inicio_plano,
            'datas_esperadas': datas_esperadas,
            'os_existentes': os_existentes,
            'os_faltantes': os_faltantes
        }
        
    except Exception as e:
        print(f"❌ Erro no diagnóstico: {e}")
        import traceback
        traceback.print_exc()
        return None

def gerar_os_faltantes(diagnostico):
    """Gera as OS faltantes"""
    try:
        print("\n🚀 GERANDO OS FALTANTES")
        print("=" * 30)
        
        if not diagnostico or not diagnostico['os_faltantes']:
            print("✅ Nenhuma OS faltante para gerar")
            return
        
        from assets_models import OrdemServico
        
        os_geradas = []
        
        for sequencia, data_faltante in diagnostico['os_faltantes']:
            try:
                # Criar nova OS
                nova_os = OrdemServico(
                    descricao=f"PMP: PREVENTIVA SEMANAL - MECANICA - BBN01 - Sequência #{sequencia}",
                    data_programada=data_faltante,
                    status='aberta',
                    prioridade='preventiva',
                    tipo_manutencao='Preventiva',
                    oficina='Mecânica',
                    equipamento='BBN01',
                    pmp_id=diagnostico['pmp_id'],
                    sequencia_pmp=sequencia,
                    criado_por=1,  # ID do usuário admin
                    criado_em=datetime.now()
                )
                
                db.session.add(nova_os)
                db.session.flush()  # Para obter o ID
                
                os_geradas.append({
                    'id': nova_os.id,
                    'sequencia': sequencia,
                    'data': data_faltante,
                    'descricao': nova_os.descricao
                })
                
                print(f"✅ OS #{nova_os.id} criada para {data_faltante.strftime('%d/%m/%Y')} (Seq #{sequencia})")
                
            except Exception as e:
                print(f"❌ Erro ao criar OS para {data_faltante}: {e}")
        
        # Commit das mudanças
        db.session.commit()
        
        print(f"\n🎉 RESULTADO:")
        print(f"  {len(os_geradas)} OS geradas com sucesso")
        
        return os_geradas
        
    except Exception as e:
        print(f"❌ Erro ao gerar OS: {e}")
        db.session.rollback()
        import traceback
        traceback.print_exc()
        return []

def verificar_programacao_preventivas():
    """Verifica por que as OS não aparecem na linha de preventivas"""
    try:
        print("\n🔍 VERIFICANDO LINHA DE PREVENTIVAS")
        print("=" * 40)
        
        # Buscar OS com prioridade preventiva
        os_preventivas = db.session.execute("""
            SELECT id, descricao, data_programada, status, prioridade, pmp_id 
            FROM ordens_servico 
            WHERE prioridade = 'preventiva' OR prioridade LIKE '%prevent%'
            ORDER BY data_programada DESC
            LIMIT 10
        """).fetchall()
        
        print(f"📋 OS com prioridade preventiva ({len(os_preventivas)} encontradas):")
        for os in os_preventivas:
            print(f"  OS #{os[0]}: {os[1][:50]}... - {os[2]} - Status: {os[3]} - Prioridade: {os[4]}")
        
        # Verificar se há OS da PMP-02-BBN01 nas preventivas
        os_pmp_preventivas = db.session.execute("""
            SELECT id, descricao, data_programada, status, prioridade 
            FROM ordens_servico 
            WHERE pmp_id IS NOT NULL AND (prioridade = 'preventiva' OR descricao LIKE '%BBN01%')
            ORDER BY data_programada DESC
        """).fetchall()
        
        print(f"\n📋 OS de PMP com prioridade preventiva ({len(os_pmp_preventivas)} encontradas):")
        for os in os_pmp_preventivas:
            print(f"  OS #{os[0]}: {os[1][:50]}... - {os[2]} - Status: {os[3]} - Prioridade: {os[4]}")
        
        # Verificar valores únicos de prioridade
        prioridades = db.session.execute("""
            SELECT DISTINCT prioridade, COUNT(*) 
            FROM ordens_servico 
            GROUP BY prioridade 
            ORDER BY COUNT(*) DESC
        """).fetchall()
        
        print(f"\n📊 PRIORIDADES NO SISTEMA:")
        for prio, count in prioridades:
            print(f"  '{prio}': {count} OS")
        
    except Exception as e:
        print(f"❌ Erro ao verificar preventivas: {e}")
        import traceback
        traceback.print_exc()

def main():
    """Função principal"""
    app = create_app()
    
    with app.app_context():
        print("🔧 DIAGNÓSTICO E CORREÇÃO DA PMP-02-BBN01")
        print("=" * 60)
        
        # 1. Diagnosticar problema
        diagnostico = diagnosticar_pmp()
        
        if diagnostico:
            # 2. Gerar OS faltantes
            os_geradas = gerar_os_faltantes(diagnostico)
            
            # 3. Verificar linha de preventivas
            verificar_programacao_preventivas()
            
            print("\n" + "=" * 60)
            print("✅ DIAGNÓSTICO E CORREÇÃO CONCLUÍDOS")
            
            if os_geradas:
                print(f"🎉 {len(os_geradas)} OS foram geradas para corrigir o problema")
                print("\nPróximos passos:")
                print("1. Verifique se as OS aparecem na tela 'Chamados em Aberto'")
                print("2. Confirme se estão na linha 'PREVENTIVAS (PMP)'")
                print("3. Teste a programação das OS geradas")
        else:
            print("❌ Não foi possível diagnosticar o problema")

if __name__ == "__main__":
    main()
