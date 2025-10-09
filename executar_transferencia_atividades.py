#!/usr/bin/env python3
"""
Script para executar transferência de atividades para OS que não têm atividades
"""

import sys
import os

# Adicionar o diretório atual ao path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def executar_transferencia():
    """Executa transferência de atividades para OS sem atividades"""
    print("🔧 EXECUTANDO TRANSFERÊNCIA DE ATIVIDADES")
    print("="*60)
    
    try:
        from app import create_app
        app = create_app()
        
        with app.app_context():
            # Importar modelos
            from assets_models import OrdemServico
            from models.atividade_os import AtividadeOS
            from models.pmp_limpo import PMP, AtividadePMP
            from models import db
            
            print("📋 BUSCANDO OS DE PMP SEM ATIVIDADES...")
            
            # Buscar OS de PMP
            os_pmp = OrdemServico.query.filter(OrdemServico.pmp_id.isnot(None)).all()
            print(f"   Encontradas {len(os_pmp)} OS de PMP")
            
            transferencias = 0
            erros = 0
            
            for os in os_pmp:
                try:
                    # Verificar se já tem atividades
                    atividades_existentes = AtividadeOS.query.filter_by(os_id=os.id).count()
                    
                    if atividades_existentes > 0:
                        print(f"   ✅ OS {os.id}: já tem {atividades_existentes} atividades")
                        continue
                    
                    # Buscar PMP
                    pmp = PMP.query.get(os.pmp_id)
                    if not pmp:
                        print(f"   ⚠️ OS {os.id}: PMP {os.pmp_id} não encontrada")
                        continue
                    
                    # Buscar atividades da PMP
                    atividades_pmp = AtividadePMP.query.filter_by(pmp_id=os.pmp_id).order_by(AtividadePMP.ordem).all()
                    
                    if not atividades_pmp:
                        print(f"   ⚠️ OS {os.id}: PMP {pmp.codigo} não tem atividades")
                        continue
                    
                    print(f"   🔧 OS {os.id}: Transferindo {len(atividades_pmp)} atividades da PMP {pmp.codigo}")
                    
                    # Transferir atividades
                    atividades_criadas = 0
                    for atividade_pmp in atividades_pmp:
                        nova_atividade_os = AtividadeOS(
                            os_id=os.id,
                            atividade_pmp_id=atividade_pmp.id,
                            descricao=atividade_pmp.descricao,
                            ordem=atividade_pmp.ordem,
                            status='pendente'
                        )
                        db.session.add(nova_atividade_os)
                        atividades_criadas += 1
                    
                    db.session.commit()
                    transferencias += 1
                    
                    print(f"   ✅ OS {os.id}: {atividades_criadas} atividades transferidas com sucesso!")
                    
                    # Mostrar algumas atividades transferidas
                    for i, atividade_pmp in enumerate(atividades_pmp[:3]):
                        print(f"      {i+1}. {atividade_pmp.descricao}")
                    if len(atividades_pmp) > 3:
                        print(f"      ... e mais {len(atividades_pmp) - 3} atividades")
                    
                except Exception as e:
                    db.session.rollback()
                    erros += 1
                    print(f"   ❌ OS {os.id}: Erro - {e}")
            
            print("\n" + "="*60)
            print(f"📊 RESULTADO FINAL:")
            print(f"   ✅ Transferências realizadas: {transferencias}")
            print(f"   ❌ Erros: {erros}")
            print(f"   📋 Total de OS verificadas: {len(os_pmp)}")
            print("="*60)
            
            return transferencias > 0
        
    except Exception as e:
        print(f"❌ Erro geral: {e}")
        import traceback
        traceback.print_exc()
        return False

def verificar_os_especifica(os_id):
    """Verifica uma OS específica"""
    print(f"\n🔍 VERIFICANDO OS {os_id}")
    print("="*40)
    
    try:
        from app import create_app
        app = create_app()
        
        with app.app_context():
            from assets_models import OrdemServico
            from models.atividade_os import AtividadeOS
            from models.pmp_limpo import PMP, AtividadePMP
            
            # Buscar a OS
            os = OrdemServico.query.get(os_id)
            
            if not os:
                print(f"   ❌ OS {os_id} não encontrada")
                return False
            
            print(f"   📋 OS {os_id}: {os.descricao}")
            print(f"   🏷️ Status: {os.status}")
            print(f"   🔗 PMP ID: {os.pmp_id}")
            
            # Verificar atividades da OS
            atividades_os = AtividadeOS.query.filter_by(os_id=os_id).count()
            print(f"   📊 Atividades na OS: {atividades_os}")
            
            if os.pmp_id:
                # Verificar PMP
                pmp = PMP.query.get(os.pmp_id)
                if pmp:
                    print(f"   📋 PMP: {pmp.codigo} - {pmp.descricao}")
                    
                    # Verificar atividades da PMP
                    atividades_pmp = AtividadePMP.query.filter_by(pmp_id=os.pmp_id).count()
                    print(f"   📊 Atividades na PMP: {atividades_pmp}")
                    
                    if atividades_pmp > 0 and atividades_os == 0:
                        print(f"   ⚠️ PROBLEMA: PMP tem {atividades_pmp} atividades, mas OS tem 0")
                        return True
                else:
                    print(f"   ❌ PMP {os.pmp_id} não encontrada")
            
            return False
        
    except Exception as e:
        print(f"❌ Erro: {e}")
        return False

if __name__ == "__main__":
    print("🔧 TRANSFERÊNCIA DE ATIVIDADES PARA OS")
    print()
    
    # Verificar OS específica se fornecida
    if len(sys.argv) > 1:
        os_id = int(sys.argv[1])
        verificar_os_especifica(os_id)
    
    # Executar transferência geral
    sucesso = executar_transferencia()
    
    if sucesso:
        print("\n✅ TRANSFERÊNCIA CONCLUÍDA COM SUCESSO!")
        print("   As atividades agora devem aparecer na interface.")
    else:
        print("\n⚠️ NENHUMA TRANSFERÊNCIA NECESSÁRIA")
        print("   Todas as OS já têm atividades ou não há OS de PMP.")
    
    print("\n" + "="*60)
    print("📊 VERIFICAÇÃO CONCLUÍDA")
    print("="*60)
