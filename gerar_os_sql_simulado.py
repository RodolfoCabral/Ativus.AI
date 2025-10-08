#!/usr/bin/env python3
"""
Script para gerar comandos SQL que criariam as OS necessárias
Simula a geração baseada nos dados das PMPs
"""

from datetime import datetime, date, timedelta
from dateutil.relativedelta import relativedelta

def normalizar_frequencia(frequencia):
    """Normaliza frequência para padrão"""
    if not frequencia:
        return 'semanal'
    
    freq_lower = frequencia.lower().strip()
    
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
        return data_base + timedelta(weeks=1)

def gerar_cronograma(data_inicio, frequencia, data_fim=None):
    """Gera cronograma de datas baseado na frequência"""
    if not data_inicio:
        return []
    
    cronograma = []
    data_atual = data_inicio
    hoje = date.today()
    
    # Gerar datas até hoje
    while data_atual <= hoje:
        cronograma.append(data_atual)
        data_atual = calcular_proxima_data(data_atual, frequencia)
        
        # Proteção contra loop infinito
        if len(cronograma) > 1000:
            break
    
    return cronograma

def gerar_sql_os():
    """Gera comandos SQL para criar as OS necessárias"""
    
    # Dados das PMPs que precisam de OS
    pmps_dados = [
        {
            'id': 133,
            'codigo': 'PMP-01-BBN01',
            'descricao': 'PREVENTIVA MENSAL - MECANICA',
            'equipamento_id': 232,
            'frequencia': 'mensal',
            'data_inicio_plano': date(2025, 9, 4),
            'oficina': 'mecanica',
            'usuarios_responsaveis': '[67]'
        },
        {
            'id': 134,
            'codigo': 'PMP-02-BBN01',
            'descricao': 'PREVENTIVA SEMANAL - MECANICA',
            'equipamento_id': 232,
            'frequencia': 'semanal',
            'data_inicio_plano': date(2025, 9, 5),
            'oficina': 'mecanica',
            'usuarios_responsaveis': '[67]'
        },
        {
            'id': 135,
            'codigo': 'PMP-03-BBN01',
            'descricao': 'PREVENTIVA SEMANAL - ELETRICA',
            'equipamento_id': 232,
            'frequencia': 'semanal',
            'data_inicio_plano': date(2025, 9, 8),
            'oficina': 'eletrica',
            'usuarios_responsaveis': None
        },
        {
            'id': 137,
            'codigo': 'PMP-05-BBN01',
            'descricao': 'PREVENTIVA DIARIO - CIVIL',
            'equipamento_id': 232,
            'frequencia': 'diario',
            'data_inicio_plano': date(2025, 9, 5),
            'oficina': 'civil',
            'usuarios_responsaveis': None
        },
        {
            'id': 167,
            'codigo': 'PMP-01-MTD01',
            'descricao': 'PREVENTIVA DIARIO - MECANICA',
            'equipamento_id': 233,
            'frequencia': 'diario',
            'data_inicio_plano': date(2025, 9, 8),
            'oficina': 'mecanica',
            'usuarios_responsaveis': None
        }
    ]
    
    print("-- SQL PARA GERAR OS BASEADAS EM PMPs")
    print("-- Gerado em:", datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
    print("-- Total de PMPs processadas:", len(pmps_dados))
    print()
    
    total_os = 0
    os_id_counter = 1000  # Começar com ID alto para evitar conflitos
    
    for pmp in pmps_dados:
        print(f"-- PMP: {pmp['codigo']} - {pmp['descricao']}")
        print(f"-- Frequência: {pmp['frequencia']}, Data início: {pmp['data_inicio_plano']}")
        
        # Gerar cronograma
        cronograma = gerar_cronograma(pmp['data_inicio_plano'], pmp['frequencia'])
        
        print(f"-- OS necessárias: {len(cronograma)}")
        print()
        
        for i, data_os in enumerate(cronograma, 1):
            os_id_counter += 1
            sequencia = f"#{i:03d}"
            
            # Descrição da OS
            descricao = f"PMP: {pmp['descricao']} - Sequência {sequencia}"
            
            # Usuários responsáveis
            usuarios = pmp['usuarios_responsaveis'] if pmp['usuarios_responsaveis'] else 'NULL'
            if usuarios != 'NULL':
                usuarios = f"'{usuarios}'"
            
            # SQL INSERT
            sql = f"""INSERT INTO ordens_servico (
    id, descricao, equipamento_id, tipo, oficina, status, prioridade,
    data_programada, data_criacao, criado_por, pmp_id, pmp_codigo,
    usuarios_responsaveis, origem
) VALUES (
    {os_id_counter}, 
    '{descricao}', 
    {pmp['equipamento_id']}, 
    'preventiva-periodica', 
    '{pmp['oficina']}', 
    'programada', 
    'media',
    '{data_os}', 
    NOW(), 
    1, 
    {pmp['id']}, 
    '{pmp['codigo']}',
    {usuarios},
    'pmp_automatica'
);"""
            
            print(sql)
            print()
            
            total_os += 1
        
        print(f"-- Fim das OS para {pmp['codigo']}")
        print("-- " + "="*60)
        print()
    
    print(f"-- RESUMO FINAL:")
    print(f"-- Total de OS geradas: {total_os}")
    print(f"-- PMPs processadas: {len(pmps_dados)}")
    print("-- ")
    print("-- Para executar estes comandos:")
    print("-- 1. Conecte-se ao banco de dados PostgreSQL")
    print("-- 2. Execute os comandos INSERT acima")
    print("-- 3. Verifique se as OS aparecem na tela de programação")
    print()
    
    return total_os

def gerar_exemplo_pmp_03():
    """Gera exemplo específico da PMP-03-BBN01"""
    print("-- EXEMPLO ESPECÍFICO: PMP-03-BBN01")
    print("-- " + "="*60)
    
    data_inicio = date(2025, 9, 8)
    frequencia = 'semanal'
    cronograma = gerar_cronograma(data_inicio, frequencia)
    
    print(f"-- PMP-03-BBN01: PREVENTIVA SEMANAL - ELETRICA")
    print(f"-- Data início: {data_inicio}")
    print(f"-- Frequência: {frequencia}")
    print(f"-- OS necessárias: {len(cronograma)}")
    print()
    
    for i, data_os in enumerate(cronograma, 1):
        sequencia = f"#{i:03d}"
        descricao = f"PMP: PREVENTIVA SEMANAL - ELETRICA - Sequência {sequencia}"
        
        print(f"-- OS {i}: {data_os} ({data_os.strftime('%A')})")
        sql = f"""INSERT INTO ordens_servico (
    descricao, equipamento_id, tipo, oficina, status, prioridade,
    data_programada, data_criacao, criado_por, pmp_id, pmp_codigo, origem
) VALUES (
    '{descricao}', 
    232, 
    'preventiva-periodica', 
    'eletrica', 
    'programada', 
    'media',
    '{data_os}', 
    NOW(), 
    1, 
    135, 
    'PMP-03-BBN01',
    'pmp_automatica'
);"""
        print(sql)
        print()
    
    print(f"-- Total de OS para PMP-03-BBN01: {len(cronograma)}")
    print("-- Estas são exatamente as OS mencionadas na especificação:")
    for i, data_os in enumerate(cronograma[:5], 1):
        print(f"--   {i}. {data_os}")
    print()

if __name__ == "__main__":
    print("🔧 GERADOR DE SQL PARA OS BASEADAS EM PMPs")
    print(f"Data/Hora: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # Gerar exemplo específico primeiro
    gerar_exemplo_pmp_03()
    
    print("\n" + "="*80)
    print()
    
    # Gerar SQL completo
    total = gerar_sql_os()
    
    print("="*80)
    print("💡 INSTRUÇÕES PARA EXECUÇÃO:")
    print()
    print("1. Copie os comandos SQL gerados acima")
    print("2. Conecte-se ao banco de dados PostgreSQL do Heroku")
    print("3. Execute os comandos INSERT")
    print("4. Verifique a tela de programação para ver as novas OS")
    print()
    print(f"Isso criará {total} OS baseadas nas PMPs com data de início.")
    print("As OS seguirão exatamente os cronogramas calculados.")
    print("="*80)
