#!/usr/bin/env python3
"""
Script para executar geração imediata de todas as OS pendentes
Analisa as PMPs com data de início e gera as OS que deveriam existir
"""

import sys
import os
from datetime import datetime, date

# Adicionar o diretório atual ao path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def executar_geracao_pendentes():
    """Executa geração de todas as OS pendentes"""
    print("🚀 EXECUTANDO GERAÇÃO DE OS PENDENTES")
    print("="*60)
    
    try:
        # Importar sistema
        from app import create_app
        from sistema_geracao_os_pmp_aprimorado import gerar_todas_os_pmp
        
        # Criar contexto da aplicação
        app = create_app()
        
        with app.app_context():
            print("📊 Analisando PMPs com data de início...")
            
            # Importar modelos
            from models.pmp_limpo import PMP
            
            # Buscar PMPs ativas com data de início
            pmps_com_data = PMP.query.filter(
                PMP.status == 'ativo',
                PMP.data_inicio_plano.isnot(None)
            ).all()
            
            print(f"📋 Encontradas {len(pmps_com_data)} PMPs ativas com data de início:")
            
            for pmp in pmps_com_data:
                print(f"  • {pmp.codigo}: {pmp.descricao}")
                print(f"    Data início: {pmp.data_inicio_plano}")
                print(f"    Frequência: {pmp.frequencia}")
                print()
            
            print("🔄 Executando geração automática...")
            
            # Executar geração
            resultado = gerar_todas_os_pmp()
            
            if resultado['success']:
                stats = resultado['estatisticas']
                os_geradas = stats['os_geradas']
                pmps_processadas = stats['pmps_processadas']
                os_ja_existentes = stats['os_ja_existentes']
                erros = stats['erros']
                
                print("✅ GERAÇÃO CONCLUÍDA COM SUCESSO!")
                print("="*60)
                print(f"📊 ESTATÍSTICAS:")
                print(f"  • PMPs processadas: {pmps_processadas}")
                print(f"  • OS geradas: {os_geradas}")
                print(f"  • OS já existentes: {os_ja_existentes}")
                print(f"  • Erros: {erros}")
                print()
                
                # Mostrar OS geradas
                if 'os_geradas' in resultado and resultado['os_geradas']:
                    print(f"🆕 NOVAS OS GERADAS ({len(resultado['os_geradas'])}):")
                    for i, os in enumerate(resultado['os_geradas'], 1):
                        print(f"  {i:2d}. OS #{os['id']}: {os['descricao']}")
                        if 'data_programada' in os:
                            print(f"      Data: {os['data_programada']}")
                        print()
                
                # Mostrar detalhes por PMP
                if 'detalhes_pmps' in resultado:
                    print("📋 DETALHES POR PMP:")
                    for detalhe in resultado['detalhes_pmps']:
                        if detalhe['processada']:
                            print(f"  • {detalhe['pmp_codigo']}: {detalhe['os_geradas']} OS geradas")
                        else:
                            print(f"  • {detalhe['pmp_codigo']}: {detalhe['motivo']}")
                
                if os_geradas > 0:
                    print(f"\n🎉 SUCESSO! {os_geradas} OS foram geradas automaticamente!")
                    print("   As OS agora aparecem na tela de programação.")
                else:
                    print("\n✅ Sistema em dia! Todas as OS necessárias já existem.")
                    
            else:
                print("❌ ERRO NA GERAÇÃO:")
                print(f"   {resultado['error']}")
                return False
                
        return True
        
    except Exception as e:
        print(f"❌ ERRO CRÍTICO: {e}")
        import traceback
        traceback.print_exc()
        return False

def verificar_pmps_especificas():
    """Verifica PMPs específicas mencionadas"""
    print("\n🔍 VERIFICAÇÃO ESPECÍFICA DAS PMPs MENCIONADAS")
    print("="*60)
    
    try:
        from app import create_app
        from sistema_geracao_os_pmp_aprimorado import GeradorOSPMPAprimorado
        
        app = create_app()
        
        with app.app_context():
            from models.pmp_limpo import PMP
            from assets_models import OrdemServico
            
            gerador = GeradorOSPMPAprimorado()
            
            # PMPs específicas para verificar
            codigos_verificar = [
                'PMP-01-BBN01',  # mensal, início 2025-09-04
                'PMP-02-BBN01',  # semanal, início 2025-09-05  
                'PMP-03-BBN01',  # semanal, início 2025-09-08
                'PMP-05-BBN01',  # diário, início 2025-09-05
                'PMP-01-MTD01',  # diário, início 2025-09-08
            ]
            
            for codigo in codigos_verificar:
                pmp = PMP.query.filter_by(codigo=codigo).first()
                
                if pmp:
                    print(f"\n📋 {codigo}:")
                    print(f"   Descrição: {pmp.descricao}")
                    print(f"   Data início: {pmp.data_inicio_plano}")
                    print(f"   Frequência: {pmp.frequencia}")
                    print(f"   Status: {pmp.status}")
                    
                    # Verificar se é válida
                    valida, motivo = gerador.validar_pmp(pmp)
                    print(f"   Válida: {valida} - {motivo}")
                    
                    if valida:
                        # Gerar cronograma
                        cronograma = gerador.gerar_cronograma_os(pmp, limite_futuro_dias=60)
                        print(f"   Cronograma: {len(cronograma)} datas")
                        
                        # Mostrar primeiras datas
                        for i, data in enumerate(cronograma[:5], 1):
                            print(f"     {i}. {data}")
                        
                        if len(cronograma) > 5:
                            print(f"     ... e mais {len(cronograma) - 5} datas")
                        
                        # Verificar OS existentes
                        os_existentes = OrdemServico.query.filter_by(
                            pmp_codigo=pmp.codigo
                        ).count()
                        print(f"   OS existentes: {os_existentes}")
                        
                        if os_existentes < len(cronograma):
                            print(f"   ⚠️ PENDENTE: {len(cronograma) - os_existentes} OS faltando")
                        else:
                            print(f"   ✅ EM DIA: Todas as OS existem")
                else:
                    print(f"\n❌ {codigo}: PMP não encontrada")
                    
    except Exception as e:
        print(f"❌ Erro na verificação: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    print("🎯 SCRIPT DE GERAÇÃO DE OS PENDENTES")
    print(f"Data/Hora: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # Verificar PMPs específicas primeiro
    verificar_pmps_especificas()
    
    # Executar geração
    print("\n" + "="*60)
    sucesso = executar_geracao_pendentes()
    
    if sucesso:
        print("\n🎉 PROCESSO CONCLUÍDO COM SUCESSO!")
        print("   Verifique a tela de programação para ver as novas OS.")
    else:
        print("\n❌ PROCESSO FALHOU!")
        print("   Verifique os logs para mais detalhes.")
    
    sys.exit(0 if sucesso else 1)
