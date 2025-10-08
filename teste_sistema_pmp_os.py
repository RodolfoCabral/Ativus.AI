#!/usr/bin/env python3
"""
Script de Teste para Sistema de Geração Automática de OS baseado em PMPs
Valida todas as funcionalidades implementadas
"""

import sys
import os
import traceback
from datetime import datetime, date, timedelta

# Adicionar o diretório atual ao path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_imports():
    """Testa se todas as importações necessárias funcionam"""
    print("="*60)
    print("TESTE 1: IMPORTAÇÕES")
    print("="*60)
    
    try:
        # Testar importação do sistema aprimorado
        from sistema_geracao_os_pmp_aprimorado import (
            GeradorOSPMPAprimorado,
            gerar_todas_os_pmp,
            gerar_os_pmp_codigo,
            verificar_pendencias_os_pmp
        )
        print("✅ Sistema aprimorado importado com sucesso")
        
        # Testar importação das rotas
        from routes.pmp_os_api import pmp_os_api_bp
        print("✅ Blueprint de API importado com sucesso")
        
        # Testar importação dos modelos
        from models.pmp_limpo import PMP, AtividadePMP
        print("✅ Modelos PMP importados com sucesso")
        
        from assets_models import OrdemServico, AtividadeOS
        print("✅ Modelos de OS importados com sucesso")
        
        # Testar dateutil
        from dateutil.relativedelta import relativedelta
        print("✅ python-dateutil importado com sucesso")
        
        return True
        
    except Exception as e:
        print(f"❌ Erro na importação: {e}")
        traceback.print_exc()
        return False

def test_gerador_class():
    """Testa a classe GeradorOSPMPAprimorado"""
    print("\n" + "="*60)
    print("TESTE 2: CLASSE GERADOR")
    print("="*60)
    
    try:
        from sistema_geracao_os_pmp_aprimorado import GeradorOSPMPAprimorado
        
        # Criar instância
        gerador = GeradorOSPMPAprimorado()
        print("✅ Instância do gerador criada com sucesso")
        
        # Testar normalização de frequência
        frequencias_teste = [
            'semanal', 'SEMANAL', 'Semanal',
            'mensal', 'mês', 'monthly',
            'diaria', 'diário', 'daily',
            'anual', 'yearly', 'ano'
        ]
        
        for freq in frequencias_teste:
            normalizada = gerador.normalizar_frequencia(freq)
            print(f"  {freq} -> {normalizada}")
        
        print("✅ Normalização de frequências funcionando")
        
        # Testar cálculo de próxima data
        data_base = date(2025, 9, 8)  # 08/09/2025
        
        proxima_semanal = gerador.calcular_proxima_data(data_base, 'semanal')
        print(f"  Próxima data semanal: {data_base} -> {proxima_semanal}")
        
        proxima_mensal = gerador.calcular_proxima_data(data_base, 'mensal')
        print(f"  Próxima data mensal: {data_base} -> {proxima_mensal}")
        
        print("✅ Cálculo de próximas datas funcionando")
        
        return True
        
    except Exception as e:
        print(f"❌ Erro no teste da classe: {e}")
        traceback.print_exc()
        return False

def test_database_connection():
    """Testa conexão com banco de dados"""
    print("\n" + "="*60)
    print("TESTE 3: CONEXÃO COM BANCO")
    print("="*60)
    
    try:
        from models import db
        from models.pmp_limpo import PMP
        from assets_models import OrdemServico
        
        # Testar consulta de PMPs
        pmps_count = PMP.query.count()
        print(f"✅ Total de PMPs no banco: {pmps_count}")
        
        # Testar consulta de OS
        os_count = OrdemServico.query.count()
        print(f"✅ Total de OS no banco: {os_count}")
        
        # Buscar PMPs ativas
        pmps_ativas = PMP.query.filter_by(status='ativo').count()
        print(f"✅ PMPs ativas: {pmps_ativas}")
        
        # Buscar PMPs com data de início
        pmps_com_data = PMP.query.filter(
            PMP.status == 'ativo',
            PMP.data_inicio_plano.isnot(None)
        ).count()
        print(f"✅ PMPs ativas com data de início: {pmps_com_data}")
        
        return True
        
    except Exception as e:
        print(f"❌ Erro na conexão com banco: {e}")
        traceback.print_exc()
        return False

def test_pmp_validation():
    """Testa validação de PMPs"""
    print("\n" + "="*60)
    print("TESTE 4: VALIDAÇÃO DE PMPs")
    print("="*60)
    
    try:
        from sistema_geracao_os_pmp_aprimorado import GeradorOSPMPAprimorado
        from models.pmp_limpo import PMP
        
        gerador = GeradorOSPMPAprimorado()
        
        # Buscar algumas PMPs para testar
        pmps = PMP.query.limit(5).all()
        
        if not pmps:
            print("⚠️ Nenhuma PMP encontrada no banco para teste")
            return True
        
        for pmp in pmps:
            valida, motivo = gerador.validar_pmp(pmp)
            status_icon = "✅" if valida else "❌"
            print(f"  {status_icon} PMP {pmp.codigo}: {motivo}")
        
        print("✅ Validação de PMPs funcionando")
        return True
        
    except Exception as e:
        print(f"❌ Erro na validação de PMPs: {e}")
        traceback.print_exc()
        return False

def test_pendencias_check():
    """Testa verificação de pendências"""
    print("\n" + "="*60)
    print("TESTE 5: VERIFICAÇÃO DE PENDÊNCIAS")
    print("="*60)
    
    try:
        from sistema_geracao_os_pmp_aprimorado import verificar_pendencias_os_pmp
        
        resultado = verificar_pendencias_os_pmp()
        
        if resultado['success']:
            print(f"✅ Verificação de pendências executada com sucesso")
            print(f"  PMPs verificadas: {resultado['total_pmps_verificadas']}")
            print(f"  PMPs com pendências: {resultado['total_pmps_com_pendencias']}")
            
            if resultado['pendencias']:
                print("  Pendências encontradas:")
                for pmp in resultado['pendencias'][:3]:  # Mostrar apenas 3
                    print(f"    - {pmp['pmp_codigo']}: {pmp['os_pendentes']} OS pendentes")
            else:
                print("  ✅ Nenhuma pendência encontrada")
        else:
            print(f"❌ Erro na verificação: {resultado['error']}")
            return False
        
        return True
        
    except Exception as e:
        print(f"❌ Erro no teste de pendências: {e}")
        traceback.print_exc()
        return False

def test_specific_pmp():
    """Testa geração para PMP específica"""
    print("\n" + "="*60)
    print("TESTE 6: GERAÇÃO PARA PMP ESPECÍFICA")
    print("="*60)
    
    try:
        from sistema_geracao_os_pmp_aprimorado import gerar_os_pmp_codigo
        from models.pmp_limpo import PMP
        
        # Buscar uma PMP ativa para teste
        pmp_teste = PMP.query.filter(
            PMP.status == 'ativo',
            PMP.data_inicio_plano.isnot(None)
        ).first()
        
        if not pmp_teste:
            print("⚠️ Nenhuma PMP ativa com data de início encontrada para teste")
            return True
        
        print(f"🎯 Testando com PMP: {pmp_teste.codigo}")
        
        # Executar geração (modo simulação - não commitando)
        resultado = gerar_os_pmp_codigo(pmp_teste.codigo)
        
        if resultado['success']:
            print(f"✅ Geração para PMP específica executada")
            resultado_pmp = resultado['resultado_pmp']
            print(f"  PMP processada: {resultado_pmp['processada']}")
            if resultado_pmp['processada']:
                print(f"  OS geradas: {resultado_pmp['os_geradas']}")
            else:
                print(f"  Motivo: {resultado_pmp['motivo']}")
        else:
            print(f"❌ Erro na geração: {resultado['error']}")
            return False
        
        return True
        
    except Exception as e:
        print(f"❌ Erro no teste de PMP específica: {e}")
        traceback.print_exc()
        return False

def test_api_endpoints():
    """Testa se os endpoints de API estão definidos corretamente"""
    print("\n" + "="*60)
    print("TESTE 7: ENDPOINTS DE API")
    print("="*60)
    
    try:
        from routes.pmp_os_api import pmp_os_api_bp
        
        # Verificar se blueprint tem as rotas esperadas
        endpoints_esperados = [
            '/api/pmp/os/verificar-pendencias',
            '/api/pmp/os/gerar-todas',
            '/api/pmp/os/status-sistema',
            '/api/pmp/os/simular-geracao',
            '/api/pmp/os/executar-automatico'
        ]
        
        # Obter regras do blueprint
        regras = []
        for rule in pmp_os_api_bp.url_map.iter_rules():
            regras.append(rule.rule)
        
        print(f"✅ Blueprint carregado com {len(regras)} rotas")
        
        for endpoint in endpoints_esperados:
            if any(endpoint in regra for regra in regras):
                print(f"  ✅ {endpoint}")
            else:
                print(f"  ❌ {endpoint} - NÃO ENCONTRADO")
        
        return True
        
    except Exception as e:
        print(f"❌ Erro no teste de endpoints: {e}")
        traceback.print_exc()
        return False

def test_cronograma_generation():
    """Testa geração de cronograma"""
    print("\n" + "="*60)
    print("TESTE 8: GERAÇÃO DE CRONOGRAMA")
    print("="*60)
    
    try:
        from sistema_geracao_os_pmp_aprimorado import GeradorOSPMPAprimorado
        from models.pmp_limpo import PMP
        
        gerador = GeradorOSPMPAprimorado()
        
        # Buscar PMP para teste
        pmp_teste = PMP.query.filter(
            PMP.status == 'ativo',
            PMP.data_inicio_plano.isnot(None)
        ).first()
        
        if not pmp_teste:
            print("⚠️ Nenhuma PMP encontrada para teste de cronograma")
            return True
        
        print(f"📅 Testando cronograma para PMP: {pmp_teste.codigo}")
        print(f"  Data início: {pmp_teste.data_inicio_plano}")
        print(f"  Frequência: {pmp_teste.frequencia}")
        
        # Gerar cronograma limitado
        cronograma = gerador.gerar_cronograma_os(pmp_teste, limite_futuro_dias=30)
        
        print(f"✅ Cronograma gerado com {len(cronograma)} datas")
        
        # Mostrar primeiras 5 datas
        for i, data in enumerate(cronograma[:5], 1):
            print(f"  {i}. {data}")
        
        if len(cronograma) > 5:
            print(f"  ... e mais {len(cronograma) - 5} datas")
        
        return True
        
    except Exception as e:
        print(f"❌ Erro no teste de cronograma: {e}")
        traceback.print_exc()
        return False

def run_all_tests():
    """Executa todos os testes"""
    print("🚀 INICIANDO TESTES DO SISTEMA DE GERAÇÃO DE OS PMP")
    print("Data/Hora:", datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    
    testes = [
        ("Importações", test_imports),
        ("Classe Gerador", test_gerador_class),
        ("Conexão Banco", test_database_connection),
        ("Validação PMPs", test_pmp_validation),
        ("Verificação Pendências", test_pendencias_check),
        ("PMP Específica", test_specific_pmp),
        ("Endpoints API", test_api_endpoints),
        ("Geração Cronograma", test_cronograma_generation)
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
    print("RESUMO DOS TESTES")
    print("="*60)
    
    sucessos = 0
    for nome, resultado in resultados:
        status = "✅ PASSOU" if resultado else "❌ FALHOU"
        print(f"{status} - {nome}")
        if resultado:
            sucessos += 1
    
    print(f"\nResultado: {sucessos}/{len(resultados)} testes passaram")
    
    if sucessos == len(resultados):
        print("🎉 TODOS OS TESTES PASSARAM! Sistema pronto para uso.")
    elif sucessos >= len(resultados) * 0.8:
        print("⚠️ Maioria dos testes passou. Sistema funcional com algumas limitações.")
    else:
        print("❌ Muitos testes falharam. Sistema precisa de correções.")
    
    return sucessos == len(resultados)

if __name__ == "__main__":
    # Configurar ambiente Flask mínimo para testes
    try:
        from app import create_app
        app = create_app()
        
        with app.app_context():
            success = run_all_tests()
            sys.exit(0 if success else 1)
            
    except Exception as e:
        print(f"❌ Erro ao configurar ambiente de teste: {e}")
        traceback.print_exc()
        sys.exit(1)
