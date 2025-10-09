#!/usr/bin/env python3
"""
Script para verificar usuários responsáveis nas PMPs
"""

import sys
import os
import json

# Adicionar o diretório atual ao path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def verificar_usuarios_pmps():
    """Verifica usuários responsáveis nas PMPs"""
    print("🔍 VERIFICANDO USUÁRIOS RESPONSÁVEIS NAS PMPS")
    print("="*60)
    
    try:
        from models.pmp_limpo import PMP
        
        # Buscar PMPs ativas com data de início
        pmps = PMP.query.filter(
            PMP.status == 'ativo',
            PMP.data_inicio_plano.isnot(None)
        ).all()
        
        print(f"📊 Total de PMPs ativas com data de início: {len(pmps)}")
        print()
        
        for pmp in pmps:
            print(f"🔧 PMP: {pmp.codigo} - {pmp.descricao}")
            print(f"   📅 Data início: {pmp.data_inicio_plano}")
            print(f"   🔄 Frequência: {pmp.frequencia}")
            print(f"   👥 Usuários responsáveis (raw): {pmp.usuarios_responsaveis}")
            
            # Tentar fazer parse dos usuários
            usuarios_responsaveis = []
            if pmp.usuarios_responsaveis:
                try:
                    usuarios_responsaveis = json.loads(pmp.usuarios_responsaveis)
                    print(f"   ✅ Usuários (parsed): {usuarios_responsaveis}")
                except Exception as e:
                    print(f"   ❌ Erro ao fazer parse: {e}")
            else:
                print(f"   ⚪ Sem usuários responsáveis")
            
            # Determinar como a OS seria criada
            if usuarios_responsaveis and len(usuarios_responsaveis) > 0:
                print(f"   🎯 OS seria criada: STATUS=programada, USUÁRIO={usuarios_responsaveis[0]}")
            else:
                print(f"   🎯 OS seria criada: STATUS=aberta, USUÁRIO=None")
            
            print()
        
        return pmps
        
    except Exception as e:
        print(f"❌ Erro: {e}")
        import traceback
        traceback.print_exc()
        return []

def simular_criacao_os():
    """Simula criação de OS baseada nas PMPs"""
    print("\n🎯 SIMULANDO CRIAÇÃO DE OS")
    print("="*60)
    
    pmps = verificar_usuarios_pmps()
    
    os_abertas = 0
    os_programadas = 0
    
    for pmp in pmps:
        # Simular lógica de usuários
        usuarios_responsaveis = []
        if pmp.usuarios_responsaveis:
            try:
                usuarios_responsaveis = json.loads(pmp.usuarios_responsaveis)
            except:
                usuarios_responsaveis = []
        
        if usuarios_responsaveis and len(usuarios_responsaveis) > 0:
            os_programadas += 1
            print(f"📋 {pmp.codigo}: OS PROGRAMADA para usuário {usuarios_responsaveis[0]}")
        else:
            os_abertas += 1
            print(f"📋 {pmp.codigo}: OS ABERTA (vai para linha preventiva)")
    
    print(f"\n📊 RESUMO DA SIMULAÇÃO:")
    print(f"   🟢 OS Abertas (linha preventiva): {os_abertas}")
    print(f"   🔵 OS Programadas (container usuário): {os_programadas}")
    print(f"   📈 Total: {os_abertas + os_programadas}")

if __name__ == "__main__":
    print("🔍 DIAGNÓSTICO DE USUÁRIOS RESPONSÁVEIS NAS PMPS")
    print()
    
    # Verificar usuários
    simular_criacao_os()
    
    print("\n" + "="*60)
    print("📊 ANÁLISE CONCLUÍDA")
    print("="*60)
