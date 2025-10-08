#!/usr/bin/env python3
"""
Demonstração da Lógica de Geração de OS por Data
Mostra como o sistema gera apenas OS até hoje e futuras no dia correto
"""

from datetime import datetime, date, timedelta
from dateutil.relativedelta import relativedelta

def demonstrar_logica_geracao():
    """Demonstra a lógica de geração de OS por data"""
    
    print("🎯 DEMONSTRAÇÃO DA LÓGICA DE GERAÇÃO DE OS")
    print("="*70)
    print(f"Data de hoje: {date.today()}")
    print()
    
    # Exemplo com PMP-03-BBN01
    print("📋 EXEMPLO: PMP-03-BBN01")
    print("   Descrição: PREVENTIVA SEMANAL - ELETRICA")
    print("   Data início: 08/09/2025")
    print("   Frequência: semanal")
    print()
    
    # Gerar cronograma completo
    data_inicio = date(2025, 9, 8)
    hoje = date.today()
    
    print("📅 CRONOGRAMA COMPLETO (próximas 8 semanas):")
    cronograma_completo = []
    data_atual = data_inicio
    
    for i in range(8):
        cronograma_completo.append(data_atual)
        data_atual = data_atual + timedelta(weeks=1)
    
    for i, data in enumerate(cronograma_completo, 1):
        status_data = "PASSADA" if data < hoje else ("HOJE" if data == hoje else "FUTURA")
        print(f"   {i}. {data} ({data.strftime('%A')}) - {status_data}")
    
    print()
    print("🤖 LÓGICA DO SISTEMA AUTOMÁTICO:")
    print()
    
    # Separar datas
    datas_passadas = [d for d in cronograma_completo if d < hoje]
    data_hoje = [d for d in cronograma_completo if d == hoje]
    datas_futuras = [d for d in cronograma_completo if d > hoje]
    
    print(f"📊 ANÁLISE DAS DATAS:")
    print(f"   • Datas passadas: {len(datas_passadas)}")
    print(f"   • Data de hoje: {len(data_hoje)}")
    print(f"   • Datas futuras: {len(datas_futuras)}")
    print()
    
    print("✅ COMPORTAMENTO DO SISTEMA:")
    print()
    
    print("1️⃣ NO DEPLOY INICIAL:")
    print("   O sistema gera IMEDIATAMENTE as OS das datas passadas:")
    for i, data in enumerate(datas_passadas, 1):
        print(f"      ✅ OS #{i:03d} para {data} - CRIADA IMEDIATAMENTE")
    
    if data_hoje:
        print(f"      ✅ OS #{len(datas_passadas)+1:03d} para {data_hoje[0]} - CRIADA IMEDIATAMENTE (é hoje)")
    
    print()
    print("2️⃣ PARA DATAS FUTURAS:")
    print("   O sistema aguarda o dia correto para gerar:")
    for i, data in enumerate(datas_futuras, 1):
        dias_restantes = (data - hoje).days
        print(f"      ⏳ OS #{len(datas_passadas)+len(data_hoje)+i:03d} para {data} - será criada em {dias_restantes} dias")
    
    print()
    print("🔄 EXECUÇÃO DIÁRIA DO SISTEMA:")
    print("   • 06:00 - Verifica se há novas OS para criar hoje")
    print("   • 18:00 - Segunda verificação diária")
    print("   • A cada 30min - Verificação de emergência")
    print()
    
    print("📝 CÓDIGO RESPONSÁVEL:")
    print("   Linha 396-398 em sistema_geracao_os_pmp_aprimorado.py:")
    print("   ```python")
    print("   # Só processar datas até hoje (não gerar OS futuras automaticamente)")
    print("   if data_programada > self.hoje:")
    print("       continue")
    print("   ```")
    print()
    
    print("🎯 RESULTADO PRÁTICO:")
    print()
    print("   ANTES DO DEPLOY:")
    print("   • 0 OS existem para PMP-03-BBN01")
    print()
    print("   IMEDIATAMENTE APÓS DEPLOY:")
    datas_imediatas = [d for d in cronograma_completo if d <= hoje]
    print(f"   • {len(datas_imediatas)} OS criadas automaticamente:")
    for i, data in enumerate(datas_imediatas, 1):
        print(f"     - OS #{i:03d}: {data}")
    print()
    print("   NOS PRÓXIMOS DIAS:")
    for data in datas_futuras[:3]:  # Mostrar próximas 3
        print(f"   • {data}: Nova OS será criada automaticamente às 06:00")
    
    return len(datas_imediatas), len(datas_futuras)

def demonstrar_outras_pmps():
    """Demonstra a lógica para outras PMPs"""
    
    print("\n" + "="*70)
    print("📋 OUTRAS PMPs - COMPORTAMENTO SIMILAR")
    print("="*70)
    
    pmps_exemplo = [
        {
            'codigo': 'PMP-01-BBN01',
            'frequencia': 'mensal',
            'data_inicio': date(2025, 9, 4),
            'descricao': 'PREVENTIVA MENSAL - MECANICA'
        },
        {
            'codigo': 'PMP-02-BBN01', 
            'frequencia': 'semanal',
            'data_inicio': date(2025, 9, 5),
            'descricao': 'PREVENTIVA SEMANAL - MECANICA'
        }
    ]
    
    hoje = date.today()
    
    for pmp in pmps_exemplo:
        print(f"\n📋 {pmp['codigo']}: {pmp['descricao']}")
        print(f"   Data início: {pmp['data_inicio']}")
        print(f"   Frequência: {pmp['frequencia']}")
        
        # Calcular datas até hoje
        datas = []
        data_atual = pmp['data_inicio']
        
        while data_atual <= hoje:
            datas.append(data_atual)
            if pmp['frequencia'] == 'semanal':
                data_atual = data_atual + timedelta(weeks=1)
            elif pmp['frequencia'] == 'mensal':
                data_atual = data_atual + relativedelta(months=1)
        
        print(f"   📅 OS criadas no deploy: {len(datas)}")
        for i, data in enumerate(datas, 1):
            print(f"      {i}. {data}")
        
        # Próxima data
        if pmp['frequencia'] == 'semanal':
            proxima = datas[-1] + timedelta(weeks=1) if datas else pmp['data_inicio']
        elif pmp['frequencia'] == 'mensal':
            proxima = datas[-1] + relativedelta(months=1) if datas else pmp['data_inicio']
        
        if proxima > hoje:
            dias_restantes = (proxima - hoje).days
            print(f"   ⏳ Próxima OS: {proxima} (em {dias_restantes} dias)")

if __name__ == "__main__":
    print("🔍 DEMONSTRAÇÃO DA LÓGICA DE GERAÇÃO DE OS POR DATA")
    print(f"Executado em: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # Demonstrar lógica principal
    imediatas, futuras = demonstrar_logica_geracao()
    
    # Demonstrar outras PMPs
    demonstrar_outras_pmps()
    
    print("\n" + "="*70)
    print("💡 RESUMO DA LÓGICA:")
    print("="*70)
    print("✅ CORRETO: Datas passadas são criadas IMEDIATAMENTE no deploy")
    print("✅ CORRETO: Datas futuras são criadas APENAS no dia correto")
    print("✅ CORRETO: Sistema executa automaticamente todos os dias")
    print("✅ CORRETO: Não há geração antecipada de OS futuras")
    print()
    print("🎯 COMPORTAMENTO EXATO CONFORME SOLICITADO:")
    print("   • Deploy → OS passadas aparecem de imediato")
    print("   • Futuras → Só aparecem no dia correto")
    print("   • Automático → Sem intervenção manual")
    print("="*70)
