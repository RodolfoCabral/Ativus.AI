#!/usr/bin/env python3
"""
Script para simular geração de OS baseado nos dados da tabela PMP
Calcula quantas OS deveriam existir para cada PMP
"""

from datetime import datetime, date, timedelta
from dateutil.relativedelta import relativedelta

def normalizar_frequencia(frequencia):
    """Normaliza frequência para padrão"""
    if not frequencia:
        return 'semanal'
    
    freq_lower = frequencia.lower().strip()
    
    # Mapeamento de frequências
    mapeamento = {
        'diario': 'diaria',
        'diária': 'diaria',
        'daily': 'diaria',
        'semanal': 'semanal',
        'weekly': 'semanal',
        'quinzenal': 'quinzenal',
        'biweekly': 'quinzenal',
        'mensal': 'mensal',
        'monthly': 'mensal',
        'mês': 'mensal',
        'bimestral': 'bimestral',
        'trimestral': 'trimestral',
        'quarterly': 'trimestral',
        'semestral': 'semestral',
        'anual': 'anual',
        'yearly': 'anual',
        'ano': 'anual'
    }
    
    return mapeamento.get(freq_lower, 'semanal')

def calcular_proxima_data(data_base, frequencia):
    """Calcula próxima data baseada na frequência"""
    freq_normalizada = normalizar_frequencia(frequencia)
    
    if freq_normalizada == 'diaria':
        return data_base + timedelta(days=1)
    elif freq_normalizada == 'semanal':
        return data_base + timedelta(weeks=1)
    elif freq_normalizada == 'quinzenal':
        return data_base + timedelta(weeks=2)
    elif freq_normalizada == 'mensal':
        return data_base + relativedelta(months=1)
    elif freq_normalizada == 'bimestral':
        return data_base + relativedelta(months=2)
    elif freq_normalizada == 'trimestral':
        return data_base + relativedelta(months=3)
    elif freq_normalizada == 'semestral':
        return data_base + relativedelta(months=6)
    elif freq_normalizada == 'anual':
        return data_base + relativedelta(years=1)
    else:
        return data_base + timedelta(weeks=1)  # Padrão semanal

def gerar_cronograma(data_inicio, frequencia, data_fim=None, limite_dias=365):
    """Gera cronograma de datas baseado na frequência"""
    if not data_inicio:
        return []
    
    cronograma = []
    data_atual = data_inicio
    hoje = date.today()
    data_limite = hoje + timedelta(days=limite_dias)
    
    # Se há data fim, usar a menor entre data_fim e data_limite
    if data_fim:
        data_limite = min(data_fim, data_limite)
    
    # Gerar datas até o limite
    while data_atual <= data_limite:
        cronograma.append(data_atual)
        data_atual = calcular_proxima_data(data_atual, frequencia)
        
        # Proteção contra loop infinito
        if len(cronograma) > 1000:
            break
    
    return cronograma

def analisar_pmps():
    """Analisa as PMPs da tabela e calcula OS necessárias"""
    
    # Dados da tabela PMP fornecida
    pmps_dados = [
        {
            'id': 84,
            'codigo': 'PMP-01-MNTR01',
            'descricao': 'PREVENTIVA ANUAL - INSTRUMENTACAO',
            'frequencia': 'anual',
            'status': 'ativo',
            'data_inicio_plano': None,  # Sem data de início
            'data_fim_plano': None
        },
        {
            'id': 133,
            'codigo': 'PMP-01-BBN01',
            'descricao': 'PREVENTIVA MENSAL - MECANICA',
            'frequencia': 'mensal',
            'status': 'ativo',
            'data_inicio_plano': date(2025, 9, 4),
            'data_fim_plano': None
        },
        {
            'id': 134,
            'codigo': 'PMP-02-BBN01',
            'descricao': 'PREVENTIVA SEMANAL - MECANICA',
            'frequencia': 'semanal',
            'status': 'ativo',
            'data_inicio_plano': date(2025, 9, 5),
            'data_fim_plano': None
        },
        {
            'id': 135,
            'codigo': 'PMP-03-BBN01',
            'descricao': 'PREVENTIVA SEMANAL - ELETRICA',
            'frequencia': 'semanal',
            'status': 'ativo',
            'data_inicio_plano': date(2025, 9, 8),
            'data_fim_plano': None
        },
        {
            'id': 136,
            'codigo': 'PMP-04-BBN01',
            'descricao': 'PREVENTIVA SEMESTRAL - ELETRICA',
            'frequencia': 'semestral',
            'status': 'ativo',
            'data_inicio_plano': None,  # Sem data de início
            'data_fim_plano': None
        },
        {
            'id': 137,
            'codigo': 'PMP-05-BBN01',
            'descricao': 'PREVENTIVA DIARIO - CIVIL',
            'frequencia': 'diario',
            'status': 'ativo',
            'data_inicio_plano': date(2025, 9, 5),
            'data_fim_plano': None
        },
        {
            'id': 167,
            'codigo': 'PMP-01-MTD01',
            'descricao': 'PREVENTIVA DIARIO - MECANICA',
            'frequencia': 'diario',
            'status': 'ativo',
            'data_inicio_plano': date(2025, 9, 8),
            'data_fim_plano': None
        },
        {
            'id': 168,
            'codigo': 'PMP-01-PNC01',
            'descricao': 'PREVENTIVA DIARIO - MECANICA',
            'frequencia': 'diario',
            'status': 'ativo',
            'data_inicio_plano': None,  # Sem data de início
            'data_fim_plano': None
        },
        {
            'id': 199,
            'codigo': 'PMP-06-BBN01',
            'descricao': 'PREVENTIVA QUINZENAL - MECANICA',
            'frequencia': 'quinzenal',
            'status': 'ativo',
            'data_inicio_plano': None,  # Sem data de início
            'data_fim_plano': None
        }
    ]
    
    print("📊 ANÁLISE DE PMPs E OS NECESSÁRIAS")
    print("="*80)
    print(f"Data de referência: {date.today()}")
    print()
    
    total_os_necessarias = 0
    pmps_com_pendencias = 0
    
    for pmp in pmps_dados:
        print(f"📋 {pmp['codigo']}: {pmp['descricao']}")
        print(f"   Frequência: {pmp['frequencia']}")
        print(f"   Data início: {pmp['data_inicio_plano']}")
        print(f"   Status: {pmp['status']}")
        
        # Verificar se pode gerar OS
        if pmp['status'] != 'ativo':
            print("   ❌ PMP não está ativa")
            print()
            continue
            
        if not pmp['data_inicio_plano']:
            print("   ⚠️ Sem data de início - não pode gerar OS")
            print()
            continue
            
        if pmp['data_inicio_plano'] > date.today():
            print("   ⚠️ Data de início é futura - aguardando")
            print()
            continue
        
        # Gerar cronograma
        cronograma = gerar_cronograma(
            pmp['data_inicio_plano'],
            pmp['frequencia'],
            pmp['data_fim_plano'],
            limite_dias=60  # Próximos 60 dias
        )
        
        # Filtrar apenas datas até hoje
        cronograma_ate_hoje = [data for data in cronograma if data <= date.today()]
        
        print(f"   📅 Cronograma até hoje: {len(cronograma_ate_hoje)} OS necessárias")
        
        if cronograma_ate_hoje:
            print("   📆 Datas das OS:")
            for i, data in enumerate(cronograma_ate_hoje[:10], 1):  # Mostrar até 10
                print(f"      {i:2d}. {data} ({data.strftime('%A')})")
            
            if len(cronograma_ate_hoje) > 10:
                print(f"      ... e mais {len(cronograma_ate_hoje) - 10} datas")
            
            total_os_necessarias += len(cronograma_ate_hoje)
            pmps_com_pendencias += 1
            
            print(f"   🎯 RESULTADO: {len(cronograma_ate_hoje)} OS deveriam existir")
        else:
            print("   ✅ Nenhuma OS necessária ainda")
        
        print()
    
    print("="*80)
    print("📊 RESUMO GERAL:")
    print(f"   • PMPs analisadas: {len(pmps_dados)}")
    print(f"   • PMPs com data de início: {sum(1 for p in pmps_dados if p['data_inicio_plano'])}")
    print(f"   • PMPs que precisam de OS: {pmps_com_pendencias}")
    print(f"   • Total de OS necessárias: {total_os_necessarias}")
    print()
    
    if total_os_necessarias > 0:
        print("🚨 AÇÃO NECESSÁRIA:")
        print(f"   O sistema automático deve gerar {total_os_necessarias} OS")
        print("   para colocar as PMPs em dia com seus cronogramas.")
    else:
        print("✅ SISTEMA EM DIA:")
        print("   Todas as PMPs estão com suas OS em dia.")
    
    return total_os_necessarias

def gerar_exemplo_pmp_03_bbn01():
    """Gera exemplo específico da PMP-03-BBN01"""
    print("\n" + "="*80)
    print("🎯 EXEMPLO ESPECÍFICO: PMP-03-BBN01")
    print("="*80)
    
    data_inicio = date(2025, 9, 8)  # 08/09/2025
    frequencia = 'semanal'
    
    print(f"Código: PMP-03-BBN01")
    print(f"Descrição: PREVENTIVA SEMANAL - ELETRICA")
    print(f"Data início: {data_inicio}")
    print(f"Frequência: {frequencia}")
    print()
    
    cronograma = gerar_cronograma(data_inicio, frequencia, limite_dias=60)
    cronograma_ate_hoje = [data for data in cronograma if data <= date.today()]
    
    print(f"📅 Cronograma completo (próximos 60 dias): {len(cronograma)} datas")
    print(f"📅 OS necessárias até hoje: {len(cronograma_ate_hoje)} datas")
    print()
    
    print("📆 Datas das OS que deveriam existir:")
    for i, data in enumerate(cronograma_ate_hoje, 1):
        dias_passados = (date.today() - data).days
        status = "✅ Deveria existir" if dias_passados >= 0 else "⏳ Futura"
        print(f"   {i:2d}. {data} ({data.strftime('%A')}) - {status}")
    
    print()
    print(f"🎯 RESULTADO FINAL:")
    print(f"   A PMP-03-BBN01 deveria ter {len(cronograma_ate_hoje)} OS criadas até hoje.")
    print(f"   Cada OS representa uma execução semanal da manutenção preventiva.")

if __name__ == "__main__":
    print("🔍 SIMULAÇÃO DE GERAÇÃO DE OS BASEADA EM PMPs")
    print(f"Data/Hora: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # Analisar todas as PMPs
    total_necessarias = analisar_pmps()
    
    # Exemplo específico da PMP-03-BBN01
    gerar_exemplo_pmp_03_bbn01()
    
    print("\n" + "="*80)
    print("💡 CONCLUSÃO:")
    if total_necessarias > 0:
        print(f"   O sistema automático deve ser executado para gerar {total_necessarias} OS.")
        print("   Essas OS colocarão todas as PMPs em dia com seus cronogramas.")
    else:
        print("   Todas as PMPs estão em dia. Nenhuma OS adicional necessária.")
    print("="*80)
