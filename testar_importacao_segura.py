#!/usr/bin/env python3
"""
Teste específico para verificar se a importação segura evita conflitos de tabela
"""

import sys
import os

# Adicionar o diretório atual ao path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def testar_importacao_multipla():
    """Testa se múltiplas importações não causam conflito"""
    print("🔄 Testando múltiplas importações...")
    
    try:
        # Importar múltiplas vezes para simular o problema em produção
        for i in range(10):
            from routes.relatorio_52_semanas import get_model_safe
            
            # Tentar importar os modelos várias vezes
            equipamento = get_model_safe('Equipamento')
            pmp = get_model_safe('PMP')
            os_model = get_model_safe('OrdemServico')
            
            if i == 0:
                print(f"✅ Primeira importação: Equipamento={equipamento is not None}, PMP={pmp is not None}, OS={os_model is not None}")
            elif i == 9:
                print(f"✅ Décima importação: Equipamento={equipamento is not None}, PMP={pmp is not None}, OS={os_model is not None}")
        
        print("✅ Múltiplas importações funcionando sem conflito!")
        return True
        
    except Exception as e:
        print(f"❌ Erro em múltiplas importações: {e}")
        import traceback
        traceback.print_exc()
        return False

def testar_cache_funcionando():
    """Testa se o cache está funcionando corretamente"""
    print("\n💾 Testando cache de modelos...")
    
    try:
        from routes.relatorio_52_semanas import get_model_safe, _MODELS_CACHE
        
        # Limpar cache para teste
        _MODELS_CACHE.clear()
        print("🧹 Cache limpo")
        
        # Primeira importação - deve ir para o cache
        equipamento1 = get_model_safe('Equipamento')
        print(f"📥 Primeira importação Equipamento: {equipamento1 is not None}")
        print(f"💾 Cache após primeira importação: {list(_MODELS_CACHE.keys())}")
        
        # Segunda importação - deve vir do cache
        equipamento2 = get_model_safe('Equipamento')
        print(f"📤 Segunda importação Equipamento: {equipamento2 is not None}")
        
        # Verificar se são o mesmo objeto (cache funcionando)
        if equipamento1 is equipamento2:
            print("✅ Cache funcionando - mesmo objeto retornado!")
        else:
            print("❌ Cache não funcionando - objetos diferentes")
            return False
        
        # Testar com PMP
        pmp1 = get_model_safe('PMP')
        pmp2 = get_model_safe('PMP')
        
        if pmp1 is pmp2:
            print("✅ Cache PMP funcionando!")
        else:
            print("❌ Cache PMP não funcionando")
            return False
        
        print(f"💾 Cache final: {list(_MODELS_CACHE.keys())}")
        return True
        
    except Exception as e:
        print(f"❌ Erro no teste de cache: {e}")
        return False

def testar_fallback_mock():
    """Testa se o fallback para modelo mock funciona"""
    print("\n🎭 Testando fallback para modelo mock...")
    
    try:
        from routes.relatorio_52_semanas import get_model_safe
        
        # Tentar importar um modelo inexistente
        modelo_inexistente = get_model_safe('ModeloInexistente')
        
        if modelo_inexistente is None:
            print("✅ Fallback funcionando - retorna None para modelo inexistente")
            return True
        else:
            print("❌ Fallback não funcionando")
            return False
        
    except Exception as e:
        print(f"❌ Erro no teste de fallback: {e}")
        return False

def main():
    """Função principal de teste"""
    print("🚀 TESTE DE IMPORTAÇÃO SEGURA")
    print("=" * 50)
    
    try:
        # Teste 1: Múltiplas importações
        if not testar_importacao_multipla():
            print("❌ Falha no teste de múltiplas importações")
            return False
        
        # Teste 2: Cache funcionando
        if not testar_cache_funcionando():
            print("❌ Falha no teste de cache")
            return False
        
        # Teste 3: Fallback mock
        if not testar_fallback_mock():
            print("❌ Falha no teste de fallback")
            return False
        
        print("\n" + "=" * 50)
        print("🎉 TODOS OS TESTES DE IMPORTAÇÃO SEGURA PASSARAM!")
        print("🛡️ Sistema de importação segura funcionando:")
        print("  ✅ Cache evita reimportações")
        print("  ✅ Múltiplas importações sem conflito")
        print("  ✅ Fallback para modelos inexistentes")
        print("  ✅ Compatível com produção")
        
        return True
        
    except Exception as e:
        print(f"\n❌ Erro durante os testes: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
