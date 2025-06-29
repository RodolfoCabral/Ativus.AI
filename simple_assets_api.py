#!/usr/bin/env python3
"""
Script simples para testar as APIs de ativos
"""

import requests
import json

# Configuração
BASE_URL = "http://localhost:5000"  # Para teste local
# BASE_URL = "https://ativusai-af6f1462097d.herokuapp.com"  # Para teste no Heroku

def test_stats_api():
    """Testa a API de estatísticas"""
    print("🔍 Testando API de estatísticas...")
    try:
        response = requests.get(f"{BASE_URL}/api/test/assets-stats")
        print(f"Status: {response.status_code}")
        print(f"Resposta: {json.dumps(response.json(), indent=2)}")
    except Exception as e:
        print(f"Erro: {e}")

def test_populate_api():
    """Testa a API de popular dados"""
    print("\n📝 Testando API de popular dados...")
    try:
        response = requests.post(f"{BASE_URL}/api/test/populate-sample-data")
        print(f"Status: {response.status_code}")
        print(f"Resposta: {json.dumps(response.json(), indent=2)}")
    except Exception as e:
        print(f"Erro: {e}")

def test_clear_company_api():
    """Testa a API de limpar dados da empresa"""
    print("\n🗑️ Testando API de limpar dados da empresa...")
    try:
        response = requests.post(f"{BASE_URL}/api/test/clear-company-assets")
        print(f"Status: {response.status_code}")
        print(f"Resposta: {json.dumps(response.json(), indent=2)}")
    except Exception as e:
        print(f"Erro: {e}")

def test_clear_all_api():
    """Testa a API de limpar todos os dados"""
    print("\n💥 Testando API de limpar todos os dados...")
    try:
        response = requests.post(f"{BASE_URL}/api/test/clear-all-assets")
        print(f"Status: {response.status_code}")
        print(f"Resposta: {json.dumps(response.json(), indent=2)}")
    except Exception as e:
        print(f"Erro: {e}")

if __name__ == "__main__":
    print("🧪 TESTE DAS APIs DE ATIVOS")
    print("=" * 50)
    
    # Testar APIs
    test_stats_api()
    test_populate_api()
    test_stats_api()  # Verificar se os dados foram criados
    test_clear_company_api()
    test_stats_api()  # Verificar se os dados foram removidos
    
    print("\n✅ Testes concluídos!")

