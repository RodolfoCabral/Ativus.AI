#!/usr/bin/env python3
"""
Teste para verificar se o campo company do User está correto
"""

import sys
import os

# Adicionar o diretório atual ao path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def testar_modelo_user():
    """Testa se o modelo User tem o campo company"""
    print("🧪 Testando modelo User...")
    
    try:
        from models import User
        
        # Verificar se o modelo tem o campo company
        if hasattr(User, 'company'):
            print("✅ Campo 'company' encontrado no modelo User")
        else:
            print("❌ Campo 'company' NÃO encontrado no modelo User")
            return False
        
        # Verificar se o modelo tem o campo empresa (não deveria ter)
        if hasattr(User, 'empresa'):
            print("⚠️ Campo 'empresa' encontrado no modelo User (inesperado)")
        else:
            print("✅ Campo 'empresa' não encontrado (correto)")
        
        # Listar todos os campos do modelo
        print("\n📋 Campos disponíveis no modelo User:")
        for attr in dir(User):
            if not attr.startswith('_') and not callable(getattr(User, attr)):
                print(f"  - {attr}")
        
        return True
        
    except Exception as e:
        print(f"❌ Erro ao testar modelo User: {e}")
        return False

def testar_importacao_relatorio():
    """Testa se o relatório pode ser importado sem erro"""
    print("\n🧪 Testando importação do relatório...")
    
    try:
        from routes.relatorio_52_semanas import relatorio_52_semanas_bp
        print("✅ Relatório importado com sucesso")
        return True
        
    except Exception as e:
        print(f"❌ Erro ao importar relatório: {e}")
        return False

def main():
    """Função principal de teste"""
    print("🚀 Testando correção do campo User.company")
    print("=" * 50)
    
    try:
        # Teste 1: Modelo User
        if not testar_modelo_user():
            print("❌ Falha no teste do modelo User")
            return False
        
        # Teste 2: Importação do relatório
        if not testar_importacao_relatorio():
            print("❌ Falha no teste de importação")
            return False
        
        print("\n" + "=" * 50)
        print("✅ Todos os testes passaram!")
        print("🎯 A correção do campo company está funcionando")
        
        return True
        
    except Exception as e:
        print(f"\n❌ Erro durante os testes: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
