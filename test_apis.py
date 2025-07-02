#!/usr/bin/env python3
"""
Script para testar as APIs de ativos
"""
import requests
import json

def test_apis():
    base_url = "https://ativusai-af6f1462097d.herokuapp.com"
    
    # URLs das APIs
    apis = [
        "/api/filiais",
        "/api/setores", 
        "/api/equipamentos"
    ]
    
    print("🔍 Testando APIs de ativos...")
    print("=" * 50)
    
    for api in apis:
        url = base_url + api
        print(f"\n📡 Testando: {url}")
        
        try:
            response = requests.get(url, timeout=10)
            print(f"Status: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                print(f"✅ Sucesso: {json.dumps(data, indent=2)}")
            else:
                print(f"❌ Erro: {response.text}")
                
        except Exception as e:
            print(f"❌ Exceção: {str(e)}")
    
    print("\n" + "=" * 50)
    print("🏁 Teste concluído!")

if __name__ == "__main__":
    test_apis()

