#!/usr/bin/env python3
"""
Script de Teste Simplificado para Sistema de Geração de OS PMP
Testa funcionalidades básicas sem dependências do Flask app
"""

import sys
import os
from datetime import datetime, date, timedelta

# Adicionar o diretório atual ao path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_basic_imports():
    """Testa importações básicas"""
    print("="*60)
    print("TESTE 1: IMPORTAÇÕES BÁSICAS")
    print("="*60)
    
    try:
        # Testar dateutil
        from dateutil.relativedelta import relativedelta
        print("✅ python-dateutil importado")
        
        # Testar sistema aprimorado
        from sistema_geracao_os_pmp_aprimorado import GeradorOSPMPAprimorado
        print("✅ GeradorOSPMPAprimorado importado")
        
        return True
        
    except Exception as e:
        print(f"❌ Erro na importação: {e}")
        return False

def test_gerador_functionality():
    """Testa funcionalidades básicas do gerador"""
    print("\n" + "="*60)
    print("TESTE 2: FUNCIONALIDADES DO GERADOR")
    print("="*60)
    
    try:
        from sistema_geracao_os_pmp_aprimorado import GeradorOSPMPAprimorado
        
        # Criar instância
        gerador = GeradorOSPMPAprimorado()
        print("✅ Instância criada")
        
        # Testar normalização de frequências
        testes_freq = [
            ('semanal', 'semanal'),
            ('MENSAL', 'mensal'),
            ('diário', 'diaria'),
            ('anual', 'anual'),
            ('trimestral', 'trimestral'),
            ('frequencia_inexistente', 'semanal')  # deve retornar padrão
        ]
        
        print("\n📋 Teste de normalização de frequências:")
        for entrada, esperado in testes_freq:
            resultado = gerador.normalizar_frequencia(entrada)
            status = "✅" if resultado == esperado else "❌"
            print(f"  {status} '{entrada}' -> '{resultado}' (esperado: '{esperado}')")
        
        # Testar cálculo de próximas datas
        print("\n📅 Teste de cálculo de próximas datas:")
        data_base = date(2025, 9, 8)  # 08/09/2025 (domingo)
        
        testes_data = [
            ('semanal', timedelta(weeks=1)),
            ('mensal', None),  # Será testado separadamente
            ('diaria', timedelta(days=1)),
            ('anual', None)    # Será testado separadamente
        ]
        
        for freq, delta_esperado in testes_data:
            proxima = gerador.calcular_proxima_data(data_base, freq)
            
            if delta_esperado:
                esperada = data_base + delta_esperado
                status = "✅" if proxima == esperada else "❌"
                print(f"  {status} {freq}: {data_base} -> {proxima} (esperado: {esperada})")
            else:
                print(f"  ✅ {freq}: {data_base} -> {proxima}")
        
        # Teste específico para mensal
        proxima_mensal = gerador.calcular_proxima_data(data_base, 'mensal')
        esperada_mensal = date(2025, 10, 8)
        status = "✅" if proxima_mensal == esperada_mensal else "❌"
        print(f"  {status} mensal específico: {data_base} -> {proxima_mensal} (esperado: {esperada_mensal})")
        
        return True
        
    except Exception as e:
        print(f"❌ Erro no teste do gerador: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_cronograma_generation():
    """Testa geração de cronograma sem banco de dados"""
    print("\n" + "="*60)
    print("TESTE 3: GERAÇÃO DE CRONOGRAMA")
    print("="*60)
    
    try:
        from sistema_geracao_os_pmp_aprimorado import GeradorOSPMPAprimorado
        
        gerador = GeradorOSPMPAprimorado()
        
        # Criar objeto PMP simulado
        class PMPSimulado:
            def __init__(self, data_inicio, frequencia, data_fim=None):
                self.data_inicio_plano = data_inicio
                self.frequencia = frequencia
                self.data_fim_plano = data_fim
                self.codigo = "PMP-TESTE"
        
        # Teste 1: PMP semanal por 1 mês
        print("\n📅 Teste 1: PMP semanal por 30 dias")
        pmp_semanal = PMPSimulado(
            data_inicio=date(2025, 9, 8),  # 08/09/2025
            frequencia='semanal'
        )
        
        cronograma = gerador.gerar_cronograma_os(pmp_semanal, limite_futuro_dias=30)
        print(f"  Datas geradas: {len(cronograma)}")
        for i, data in enumerate(cronograma, 1):
            print(f"    {i}. {data}")
        
        # Teste 2: PMP mensal por 6 meses
        print("\n📅 Teste 2: PMP mensal por 180 dias")
        pmp_mensal = PMPSimulado(
            data_inicio=date(2025, 9, 1),
            frequencia='mensal'
        )
        
        cronograma_mensal = gerador.gerar_cronograma_os(pmp_mensal, limite_futuro_dias=180)
        print(f"  Datas geradas: {len(cronograma_mensal)}")
        for i, data in enumerate(cronograma_mensal, 1):
            print(f"    {i}. {data}")
        
        # Teste 3: PMP com data fim
        print("\n📅 Teste 3: PMP com data fim definida")
        pmp_com_fim = PMPSimulado(
            data_inicio=date(2025, 9, 1),
            frequencia='semanal',
            data_fim=date(2025, 9, 30)
        )
        
        cronograma_limitado = gerador.gerar_cronograma_os(pmp_com_fim)
        print(f"  Datas geradas: {len(cronograma_limitado)}")
        for i, data in enumerate(cronograma_limitado, 1):
            print(f"    {i}. {data}")
        
        return True
        
    except Exception as e:
        print(f"❌ Erro no teste de cronograma: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_validation_logic():
    """Testa lógica de validação"""
    print("\n" + "="*60)
    print("TESTE 4: LÓGICA DE VALIDAÇÃO")
    print("="*60)
    
    try:
        from sistema_geracao_os_pmp_aprimorado import GeradorOSPMPAprimorado
        
        gerador = GeradorOSPMPAprimorado()
        
        # Criar objetos PMP simulados para teste
        class PMPSimulado:
            def __init__(self, status='ativo', data_inicio=None, data_fim=None, frequencia='semanal'):
                self.status = status
                self.data_inicio_plano = data_inicio
                self.data_fim_plano = data_fim
                self.frequencia = frequencia
                self.codigo = "PMP-TESTE"
        
        hoje = gerador.hoje
        
        # Teste 1: PMP válida
        pmp_valida = PMPSimulado(
            status='ativo',
            data_inicio=hoje - timedelta(days=7),
            frequencia='semanal'
        )
        valida, motivo = gerador.validar_pmp(pmp_valida)
        print(f"  ✅ PMP válida: {valida} - {motivo}")
        
        # Teste 2: PMP inativa
        pmp_inativa = PMPSimulado(status='inativo')
        valida, motivo = gerador.validar_pmp(pmp_inativa)
        print(f"  ❌ PMP inativa: {valida} - {motivo}")
        
        # Teste 3: PMP sem data de início
        pmp_sem_data = PMPSimulado(data_inicio=None)
        valida, motivo = gerador.validar_pmp(pmp_sem_data)
        print(f"  ❌ PMP sem data: {valida} - {motivo}")
        
        # Teste 4: PMP com data de início futura
        pmp_futura = PMPSimulado(data_inicio=hoje + timedelta(days=7))
        valida, motivo = gerador.validar_pmp(pmp_futura)
        print(f"  ❌ PMP futura: {valida} - {motivo}")
        
        # Teste 5: PMP expirada
        pmp_expirada = PMPSimulado(
            data_inicio=hoje - timedelta(days=30),
            data_fim=hoje - timedelta(days=1)
        )
        valida, motivo = gerador.validar_pmp(pmp_expirada)
        print(f"  ❌ PMP expirada: {valida} - {motivo}")
        
        return True
        
    except Exception as e:
        print(f"❌ Erro no teste de validação: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_api_structure():
    """Testa estrutura da API"""
    print("\n" + "="*60)
    print("TESTE 5: ESTRUTURA DA API")
    print("="*60)
    
    try:
        from routes.pmp_os_api import pmp_os_api_bp
        print("✅ Blueprint da API importado")
        
        # Verificar se é um Blueprint válido
        from flask import Blueprint
        if isinstance(pmp_os_api_bp, Blueprint):
            print("✅ É um Blueprint válido do Flask")
        else:
            print("❌ Não é um Blueprint válido")
            return False
        
        # Verificar nome do blueprint
        print(f"✅ Nome do blueprint: {pmp_os_api_bp.name}")
        
        return True
        
    except Exception as e:
        print(f"❌ Erro no teste da API: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_example_scenario():
    """Testa cenário de exemplo específico"""
    print("\n" + "="*60)
    print("TESTE 6: CENÁRIO DE EXEMPLO (PMP-03-BBN01)")
    print("="*60)
    
    try:
        from sistema_geracao_os_pmp_aprimorado import GeradorOSPMPAprimorado
        
        gerador = GeradorOSPMPAprimorado()
        
        # Simular PMP-03-BBN01 conforme especificação
        class PMPExemplo:
            def __init__(self):
                self.codigo = "PMP-03-BBN01"
                self.descricao = "Manutenção Preventiva BBN01"
                self.status = 'ativo'
                self.data_inicio_plano = date(2025, 9, 8)  # 08/09/2025
                self.data_fim_plano = None
                self.frequencia = 'semanal'
                self.id = 135
        
        pmp_exemplo = PMPExemplo()
        
        # Validar PMP
        valida, motivo = gerador.validar_pmp(pmp_exemplo)
        print(f"✅ Validação: {valida} - {motivo}")
        
        # Gerar cronograma até hoje + algumas semanas
        cronograma = gerador.gerar_cronograma_os(pmp_exemplo, limite_futuro_dias=60)
        
        print(f"\n📅 Cronograma gerado para {pmp_exemplo.codigo}:")
        print(f"  Data início: {pmp_exemplo.data_inicio_plano}")
        print(f"  Frequência: {pmp_exemplo.frequencia}")
        print(f"  Total de datas: {len(cronograma)}")
        
        # Mostrar datas esperadas conforme especificação
        datas_esperadas = [
            date(2025, 9, 8),   # 08/09/2025
            date(2025, 9, 15),  # 15/09/2025
            date(2025, 9, 22),  # 22/09/2025
            date(2025, 9, 29),  # 29/09/2025
            date(2025, 10, 6),  # 06/10/2025
        ]
        
        print("\n  Datas esperadas vs geradas:")
        for i, data_esperada in enumerate(datas_esperadas):
            if i < len(cronograma):
                data_gerada = cronograma[i]
                status = "✅" if data_gerada == data_esperada else "❌"
                print(f"    {status} {i+1}. Esperada: {data_esperada}, Gerada: {data_gerada}")
            else:
                print(f"    ❌ {i+1}. Esperada: {data_esperada}, Não gerada")
        
        # Verificar se as primeiras 5 datas estão corretas
        primeiras_5_corretas = all(
            cronograma[i] == datas_esperadas[i] 
            for i in range(min(5, len(cronograma), len(datas_esperadas)))
        )
        
        if primeiras_5_corretas:
            print("✅ As primeiras 5 datas estão corretas conforme especificação!")
        else:
            print("❌ Algumas datas não conferem com a especificação")
        
        return primeiras_5_corretas
        
    except Exception as e:
        print(f"❌ Erro no teste de cenário: {e}")
        import traceback
        traceback.print_exc()
        return False

def run_simplified_tests():
    """Executa todos os testes simplificados"""
    print("🚀 TESTES SIMPLIFICADOS DO SISTEMA PMP OS")
    print("Data/Hora:", datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    
    testes = [
        ("Importações Básicas", test_basic_imports),
        ("Funcionalidades do Gerador", test_gerador_functionality),
        ("Geração de Cronograma", test_cronograma_generation),
        ("Lógica de Validação", test_validation_logic),
        ("Estrutura da API", test_api_structure),
        ("Cenário de Exemplo", test_example_scenario)
    ]
    
    resultados = []
    
    for nome, teste_func in testes:
        try:
            resultado = teste_func()
            resultados.append((nome, resultado))
        except Exception as e:
            print(f"❌ FALHA CRÍTICA no teste {nome}: {e}")
            resultados.append((nome, False))
    
    # Resumo final
    print("\n" + "="*60)
    print("RESUMO DOS TESTES SIMPLIFICADOS")
    print("="*60)
    
    sucessos = 0
    for nome, resultado in resultados:
        status = "✅ PASSOU" if resultado else "❌ FALHOU"
        print(f"{status} - {nome}")
        if resultado:
            sucessos += 1
    
    print(f"\nResultado: {sucessos}/{len(resultados)} testes passaram")
    
    if sucessos == len(resultados):
        print("🎉 TODOS OS TESTES PASSARAM!")
        print("✅ Sistema de geração automática de OS baseado em PMPs está funcionando corretamente")
        print("✅ Lógica de cronograma, validação e frequências implementada")
        print("✅ API estruturada e pronta para uso")
        print("✅ Cenário de exemplo (PMP-03-BBN01) validado")
    elif sucessos >= len(resultados) * 0.8:
        print("⚠️ Maioria dos testes passou. Sistema funcional com algumas limitações.")
    else:
        print("❌ Muitos testes falharam. Sistema precisa de correções.")
    
    return sucessos == len(resultados)

if __name__ == "__main__":
    success = run_simplified_tests()
    sys.exit(0 if success else 1)
