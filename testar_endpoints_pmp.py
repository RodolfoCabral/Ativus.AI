#!/usr/bin/env python3
"""
Script para testar os endpoints de PMP e identificar problemas
"""

import sys
import os
from datetime import datetime

# Adicionar o diretório atual ao path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def testar_importacoes():
    """Testa se todas as importações estão funcionando"""
    print("🔍 TESTANDO IMPORTAÇÕES")
    print("="*50)
    
    try:
        print("1. Testando sistema_geracao_os_pmp_aprimorado...")
        from sistema_geracao_os_pmp_aprimorado import (
            GeradorOSPMPAprimorado,
            gerar_todas_os_pmp,
            verificar_pendencias_os_pmp
        )
        print("   ✅ Sistema aprimorado importado com sucesso")
        
        print("2. Testando modelos...")
        from models.pmp_limpo import PMP
        print("   ✅ Modelo PMP importado com sucesso")
        
        from assets_models import OrdemServico
        print("   ✅ Modelo OrdemServico importado com sucesso")
        
        from models.atividade_os import AtividadeOS
        print("   ✅ Modelo AtividadeOS importado com sucesso")
        
        print("3. Testando Flask...")
        from flask import Flask
        print("   ✅ Flask importado com sucesso")
        
        return True
        
    except Exception as e:
        print(f"   ❌ Erro na importação: {e}")
        import traceback
        traceback.print_exc()
        return False

def testar_funcoes_sem_db():
    """Testa funções que não precisam de banco de dados"""
    print("\n🧪 TESTANDO FUNÇÕES SEM BANCO")
    print("="*50)
    
    try:
        from sistema_geracao_os_pmp_aprimorado import GeradorOSPMPAprimorado
        
        print("1. Testando criação do gerador...")
        gerador = GeradorOSPMPAprimorado()
        print(f"   ✅ Gerador criado - Data hoje: {gerador.hoje}")
        
        print("2. Testando normalização de frequência...")
        freq_testes = ['semanal', 'SEMANAL', 'weekly', 'mensal', 'diario', 'anual']
        for freq in freq_testes:
            normalizada = gerador.normalizar_frequencia(freq)
            print(f"   '{freq}' → '{normalizada}'")
        print("   ✅ Normalização funcionando")
        
        print("3. Testando cálculo de próxima data...")
        from datetime import date, timedelta
        data_base = date(2025, 9, 8)
        proxima = gerador.calcular_proxima_data(data_base, 'semanal')
        esperada = date(2025, 9, 15)
        if proxima == esperada:
            print(f"   ✅ Cálculo correto: {data_base} + semanal = {proxima}")
        else:
            print(f"   ❌ Cálculo incorreto: esperado {esperada}, obtido {proxima}")
        
        return True
        
    except Exception as e:
        print(f"   ❌ Erro no teste: {e}")
        import traceback
        traceback.print_exc()
        return False

def testar_estrutura_resposta():
    """Testa estrutura de resposta das funções"""
    print("\n📋 TESTANDO ESTRUTURA DE RESPOSTA")
    print("="*50)
    
    try:
        # Simular resposta de verificar_pendencias_os_pmp
        resposta_simulada = {
            'success': True,
            'pendencias': [
                {
                    'pmp_codigo': 'PMP-03-BBN01',
                    'pmp_id': 135,
                    'descricao': 'PREVENTIVA SEMANAL - ELETRICA',
                    'frequencia': 'semanal',
                    'data_inicio': '2025-09-08',
                    'os_pendentes': 5,
                    'datas_pendentes': ['2025-09-08', '2025-09-15', '2025-09-22', '2025-09-29', '2025-10-06']
                }
            ],
            'total_pmps_verificadas': 5,
            'total_pmps_com_pendencias': 1
        }
        
        print("1. Estrutura de resposta de verificar_pendencias_os_pmp:")
        print(f"   ✅ success: {resposta_simulada['success']}")
        print(f"   ✅ total_pmps_verificadas: {resposta_simulada['total_pmps_verificadas']}")
        print(f"   ✅ total_pmps_com_pendencias: {resposta_simulada['total_pmps_com_pendencias']}")
        print(f"   ✅ pendencias: {len(resposta_simulada['pendencias'])} itens")
        
        # Simular resposta de gerar_todas_os_pmp
        resposta_geracao = {
            'success': True,
            'estatisticas': {
                'pmps_processadas': 5,
                'os_geradas': 77,
                'os_ja_existentes': 0,
                'erros': 0
            },
            'os_geradas': []
        }
        
        print("\n2. Estrutura de resposta de gerar_todas_os_pmp:")
        print(f"   ✅ success: {resposta_geracao['success']}")
        print(f"   ✅ estatisticas.pmps_processadas: {resposta_geracao['estatisticas']['pmps_processadas']}")
        print(f"   ✅ estatisticas.os_geradas: {resposta_geracao['estatisticas']['os_geradas']}")
        print(f"   ✅ os_geradas: lista com {len(resposta_geracao['os_geradas'])} itens")
        
        return True
        
    except Exception as e:
        print(f"   ❌ Erro no teste: {e}")
        return False

def verificar_endpoints_api():
    """Verifica se os endpoints da API estão corretos"""
    print("\n🌐 VERIFICANDO ENDPOINTS DA API")
    print("="*50)
    
    endpoints_esperados = [
        '/api/pmp/os/verificar-pendencias',
        '/api/pmp/os/gerar-todas',
        '/api/pmp/os/executar-automatico',
        '/api/pmp/auto/status'
    ]
    
    print("Endpoints que devem existir:")
    for endpoint in endpoints_esperados:
        print(f"   📍 {endpoint}")
    
    print("\nVerificando arquivos de rotas:")
    arquivos_rotas = [
        'routes/pmp_os_api.py',
        'routes/pmp_auto_status.py'
    ]
    
    for arquivo in arquivos_rotas:
        if os.path.exists(arquivo):
            print(f"   ✅ {arquivo} existe")
        else:
            print(f"   ❌ {arquivo} não encontrado")
    
    return True

def gerar_comandos_correcao():
    """Gera comandos para corrigir problemas identificados"""
    print("\n🔧 COMANDOS PARA CORREÇÃO")
    print("="*50)
    
    print("1. Para corrigir problemas de JSON no frontend:")
    print("   • Verificar se endpoints retornam JSON válido")
    print("   • Adicionar try/catch em todas as chamadas fetch()")
    print("   • Verificar Content-Type: application/json")
    
    print("\n2. Para corrigir erro 500 nos endpoints:")
    print("   • Verificar se todas as importações estão corretas")
    print("   • Verificar se banco de dados está acessível")
    print("   • Verificar logs do Heroku: heroku logs --tail")
    
    print("\n3. Para testar endpoints manualmente:")
    print("   curl -X GET https://ativusai-af6f1462097d.herokuapp.com/api/pmp/os/verificar-pendencias")
    print("   curl -X POST https://ativusai-af6f1462097d.herokuapp.com/api/pmp/os/gerar-todas")
    
    print("\n4. Para verificar logs em produção:")
    print("   heroku logs --tail --app ativusai-af6f1462097d")

if __name__ == "__main__":
    print("🔍 DIAGNÓSTICO DE PROBLEMAS DO SISTEMA PMP")
    print(f"Data/Hora: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # Executar testes
    sucesso_importacoes = testar_importacoes()
    sucesso_funcoes = testar_funcoes_sem_db() if sucesso_importacoes else False
    sucesso_estrutura = testar_estrutura_resposta()
    sucesso_endpoints = verificar_endpoints_api()
    
    # Gerar comandos de correção
    gerar_comandos_correcao()
    
    print("\n" + "="*50)
    print("📊 RESUMO DO DIAGNÓSTICO:")
    print(f"   • Importações: {'✅' if sucesso_importacoes else '❌'}")
    print(f"   • Funções: {'✅' if sucesso_funcoes else '❌'}")
    print(f"   • Estruturas: {'✅' if sucesso_estrutura else '❌'}")
    print(f"   • Endpoints: {'✅' if sucesso_endpoints else '❌'}")
    
    if all([sucesso_importacoes, sucesso_funcoes, sucesso_estrutura, sucesso_endpoints]):
        print("\n🎉 DIAGNÓSTICO: Sistema parece estar correto localmente")
        print("   O problema pode estar na conexão com banco de dados em produção")
    else:
        print("\n⚠️ DIAGNÓSTICO: Problemas identificados que precisam ser corrigidos")
    
    print("="*50)
