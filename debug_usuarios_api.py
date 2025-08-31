#!/usr/bin/env python3
"""
Script para testar a API de usuários da empresa
"""

import requests
import json

def testar_api_usuarios():
    """Testa a API de usuários da empresa"""
    
    print("🧪 TESTANDO API DE USUÁRIOS DA EMPRESA")
    print("=" * 50)
    
    # URL da API (ajustar conforme necessário)
    url = "http://localhost:5000/api/usuarios/empresa"
    
    try:
        print(f"🔗 Fazendo requisição para: {url}")
        
        # Fazer requisição GET
        response = requests.get(url, timeout=10)
        
        print(f"📡 Status Code: {response.status_code}")
        print(f"📡 Headers: {dict(response.headers)}")
        
        if response.status_code == 200:
            data = response.json()
            print("✅ RESPOSTA RECEBIDA:")
            print(json.dumps(data, indent=2, ensure_ascii=False))
            
            if data.get('success'):
                usuarios = data.get('usuarios', [])
                print(f"\n👥 USUÁRIOS ENCONTRADOS: {len(usuarios)}")
                
                for i, usuario in enumerate(usuarios, 1):
                    print(f"  {i}. {usuario.get('nome')} ({usuario.get('email')}) - {usuario.get('cargo')}")
                
                if data.get('mock'):
                    print("\n⚠️ ATENÇÃO: Dados são MOCK (não vieram do banco)")
                else:
                    print(f"\n✅ Dados REAIS da empresa {data.get('empresa_id')}")
            else:
                print("❌ API retornou success=false")
        else:
            print(f"❌ Erro HTTP: {response.status_code}")
            print(f"📄 Resposta: {response.text}")
            
    except requests.exceptions.ConnectionError:
        print("❌ ERRO: Não foi possível conectar ao servidor")
        print("💡 Verifique se o Flask está rodando em localhost:5000")
        
    except requests.exceptions.Timeout:
        print("❌ ERRO: Timeout na requisição")
        
    except Exception as e:
        print(f"❌ ERRO INESPERADO: {e}")

def testar_com_heroku():
    """Testa com URL do Heroku"""
    
    print("\n🌐 TESTANDO COM HEROKU")
    print("=" * 30)
    
    # URL do Heroku (ajustar conforme necessário)
    url = "https://ativusai.herokuapp.com/api/usuarios/empresa"
    
    try:
        print(f"🔗 Fazendo requisição para: {url}")
        
        response = requests.get(url, timeout=15)
        
        print(f"📡 Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print("✅ RESPOSTA DO HEROKU:")
            print(json.dumps(data, indent=2, ensure_ascii=False))
        else:
            print(f"❌ Erro: {response.status_code}")
            print(f"📄 Resposta: {response.text}")
            
    except Exception as e:
        print(f"❌ Erro ao testar Heroku: {e}")

if __name__ == "__main__":
    # Testar localmente
    testar_api_usuarios()
    
    # Testar no Heroku
    testar_com_heroku()
    
    print("\n🏁 TESTE CONCLUÍDO")

