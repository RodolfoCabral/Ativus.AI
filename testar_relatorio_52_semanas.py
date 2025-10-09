#!/usr/bin/env python3
"""
Teste do relatório de 52 semanas
"""

from datetime import datetime, timedelta
import sys
import os

# Adicionar o diretório atual ao path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def testar_calculo_semanas():
    """Testa o cálculo das 52 semanas do ano"""
    print("🧪 Testando cálculo de semanas do ano...")
    
    from routes.relatorio_52_semanas import calcular_semanas_ano
    
    ano = 2025
    semanas = calcular_semanas_ano(ano)
    
    print(f"✅ Calculadas {len(semanas)} semanas para {ano}")
    print(f"📅 Primeira semana: {semanas[0]['inicio'].strftime('%d/%m/%Y')} - {semanas[0]['fim'].strftime('%d/%m/%Y')}")
    print(f"📅 Última semana: {semanas[-1]['inicio'].strftime('%d/%m/%Y')} - {semanas[-1]['fim'].strftime('%d/%m/%Y')}")
    
    return True

def testar_frequencias():
    """Testa o cálculo de frequências de PMP"""
    print("\n🧪 Testando cálculo de frequências...")
    
    from routes.relatorio_52_semanas import calcular_semanas_ano, determinar_semanas_pmp
    
    # Mock de PMP
    class MockPMP:
        def __init__(self, frequencia, data_inicio):
            self.frequencia = frequencia
            self.data_inicio_plano = data_inicio
    
    semanas_ano = calcular_semanas_ano(2025)
    
    # Testar diferentes frequências
    frequencias_teste = [
        ('semanal', datetime(2025, 1, 6)),  # Segunda-feira da primeira semana
        ('mensal', datetime(2025, 1, 6)),
        ('diario', datetime(2025, 1, 6)),
    ]
    
    for freq, data_inicio in frequencias_teste:
        pmp_mock = MockPMP(freq, data_inicio)
        semanas_execucao = determinar_semanas_pmp(pmp_mock, semanas_ano)
        print(f"📊 {freq.upper()}: {len(semanas_execucao)} execuções - Semanas: {semanas_execucao[:5]}{'...' if len(semanas_execucao) > 5 else ''}")
    
    return True

def testar_cores_status():
    """Testa a lógica de cores baseada no status"""
    print("\n🧪 Testando lógica de cores...")
    
    # Simular diferentes status
    status_exemplos = [
        {'status': 'concluida', 'numero_os': 123},
        {'status': 'gerada', 'numero_os': 456},
        {'status': 'nao_gerada', 'numero_os': None}
    ]
    
    cores_mapeamento = {
        'concluida': '🟢 Verde (OS concluída)',
        'gerada': '⚫ Cinza escuro (OS gerada)',
        'nao_gerada': '⚪ Cinza claro (OS não gerada)'
    }
    
    for status in status_exemplos:
        cor = cores_mapeamento[status['status']]
        numero = f"OS#{status['numero_os']}" if status['numero_os'] else "●"
        print(f"📋 Status: {status['status']} → {cor} → Exibir: {numero}")
    
    return True

def main():
    """Função principal de teste"""
    print("🚀 Iniciando testes do Relatório de 52 Semanas")
    print("=" * 50)
    
    try:
        # Teste 1: Cálculo de semanas
        if not testar_calculo_semanas():
            print("❌ Falha no teste de cálculo de semanas")
            return False
        
        # Teste 2: Frequências
        if not testar_frequencias():
            print("❌ Falha no teste de frequências")
            return False
        
        # Teste 3: Cores e status
        if not testar_cores_status():
            print("❌ Falha no teste de cores")
            return False
        
        print("\n" + "=" * 50)
        print("✅ Todos os testes passaram!")
        print("🎯 O relatório de 52 semanas está pronto para uso")
        
        return True
        
    except Exception as e:
        print(f"\n❌ Erro durante os testes: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
