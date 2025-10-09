#!/usr/bin/env python3
"""
Script para testar transferência de atividades de PMP para OS
"""

import sys
import os

# Adicionar o diretório atual ao path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def testar_atividades_pmp():
    """Testa a transferência de atividades"""
    print("🔧 TESTANDO ATIVIDADES DE PMP")
    print("="*60)
    
    try:
        from app import create_app
        app = create_app()
        
        with app.app_context():
            # Importar modelos
            from models.pmp_limpo import PMP, AtividadePMP
            from assets_models import OrdemServico
            from models.atividade_os import AtividadeOS
            
            # Listar PMPs ativas
            print("📋 PMPS ATIVAS:")
            pmps = PMP.query.filter(PMP.status == 'ativo').limit(5).all()
            
            for pmp in pmps:
                # Contar atividades da PMP
                atividades_count = AtividadePMP.query.filter_by(pmp_id=pmp.id).count()
                print(f"   PMP {pmp.codigo}: {atividades_count} atividades")
                
                if atividades_count > 0:
                    # Mostrar algumas atividades
                    atividades = AtividadePMP.query.filter_by(pmp_id=pmp.id).limit(3).all()
                    for atividade in atividades:
                        print(f"      - {atividade.descricao}")
            
            # Listar OS de PMP
            print("\n📋 OS DE PMP:")
            os_pmp = OrdemServico.query.filter(OrdemServico.pmp_id.isnot(None)).limit(5).all()
            
            for os in os_pmp:
                # Contar atividades da OS
                atividades_count = AtividadeOS.query.filter_by(os_id=os.id).count()
                print(f"   OS {os.id} (PMP {os.pmp_id}): {atividades_count} atividades")
                
                if atividades_count > 0:
                    # Mostrar algumas atividades
                    atividades = AtividadeOS.query.filter_by(os_id=os.id).limit(3).all()
                    for atividade in atividades:
                        print(f"      - {atividade.descricao}")
                else:
                    print(f"      ⚠️ OS sem atividades!")
            
            # Verificar se há OS de PMP sem atividades
            print("\n⚠️ OS DE PMP SEM ATIVIDADES:")
            os_sem_atividades = []
            
            for os in os_pmp:
                atividades_count = AtividadeOS.query.filter_by(os_id=os.id).count()
                if atividades_count == 0:
                    os_sem_atividades.append(os)
            
            if os_sem_atividades:
                for os in os_sem_atividades:
                    pmp = PMP.query.get(os.pmp_id)
                    pmp_atividades = AtividadePMP.query.filter_by(pmp_id=os.pmp_id).count()
                    print(f"   OS {os.id} → PMP {os.pmp_id} ({pmp.codigo if pmp else 'N/A'}) tem {pmp_atividades} atividades")
            else:
                print("   ✅ Todas as OS de PMP têm atividades")
        
        return True
        
    except Exception as e:
        print(f"❌ Erro: {e}")
        import traceback
        traceback.print_exc()
        return False

def testar_transferencia_manual():
    """Testa transferência manual de atividades"""
    print("\n🔧 TESTANDO TRANSFERÊNCIA MANUAL")
    print("="*60)
    
    try:
        from app import create_app
        app = create_app()
        
        with app.app_context():
            from models.pmp_limpo import PMP, AtividadePMP
            from assets_models import OrdemServico
            from models.atividade_os import AtividadeOS, StatusConformidade
            from models import db
            
            # Buscar uma OS de PMP sem atividades
            os_pmp = OrdemServico.query.filter(OrdemServico.pmp_id.isnot(None)).first()
            
            if not os_pmp:
                print("   ⚠️ Nenhuma OS de PMP encontrada")
                return False
            
            # Verificar se já tem atividades
            atividades_existentes = AtividadeOS.query.filter_by(os_id=os_pmp.id).count()
            print(f"   OS {os_pmp.id}: {atividades_existentes} atividades existentes")
            
            # Buscar atividades da PMP
            atividades_pmp = AtividadePMP.query.filter_by(pmp_id=os_pmp.pmp_id).all()
            print(f"   PMP {os_pmp.pmp_id}: {len(atividades_pmp)} atividades disponíveis")
            
            if atividades_pmp and atividades_existentes == 0:
                print(f"   🔧 Transferindo {len(atividades_pmp)} atividades...")
                
                for atividade_pmp in atividades_pmp:
                    nova_atividade_os = AtividadeOS(
                        os_id=os_pmp.id,
                        atividade_pmp_id=atividade_pmp.id,
                        descricao=atividade_pmp.descricao,
                        ordem=atividade_pmp.ordem,
                        status=StatusConformidade.PENDENTE
                    )
                    db.session.add(nova_atividade_os)
                
                db.session.commit()
                print(f"   ✅ Transferência concluída!")
                
                # Verificar resultado
                novas_atividades = AtividadeOS.query.filter_by(os_id=os_pmp.id).count()
                print(f"   📊 OS {os_pmp.id} agora tem {novas_atividades} atividades")
            
        return True
        
    except Exception as e:
        print(f"❌ Erro na transferência: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("🔧 TESTE DE ATIVIDADES PMP")
    print()
    
    # Testar atividades
    testar_atividades_pmp()
    
    # Testar transferência manual
    testar_transferencia_manual()
    
    print("\n" + "="*60)
    print("📊 TESTE CONCLUÍDO")
    print("="*60)
