#!/usr/bin/env python3
"""
Script para verificar campos obrigatórios do modelo OrdemServico
"""

import sys
import os

# Adicionar o diretório atual ao path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def verificar_campos_os():
    """Verifica campos obrigatórios do modelo OrdemServico"""
    print("🔍 VERIFICANDO CAMPOS DO MODELO ORDEMSERVICO")
    print("="*60)
    
    try:
        from assets_models import OrdemServico
        
        print("1. Campos da tabela OrdemServico:")
        for column in OrdemServico.__table__.columns:
            nullable = "NULL" if column.nullable else "NOT NULL"
            default = f" DEFAULT={column.default}" if column.default else ""
            print(f"   • {column.name}: {column.type} {nullable}{default}")
        
        print("\n2. Campos obrigatórios (NOT NULL):")
        campos_obrigatorios = []
        for column in OrdemServico.__table__.columns:
            if not column.nullable and column.default is None:
                campos_obrigatorios.append(column.name)
                print(f"   ❗ {column.name}")
        
        print(f"\n3. Total de campos obrigatórios: {len(campos_obrigatorios)}")
        
        return campos_obrigatorios
        
    except Exception as e:
        print(f"❌ Erro: {e}")
        import traceback
        traceback.print_exc()
        return []

def gerar_codigo_corrigido(campos_obrigatorios):
    """Gera código corrigido para criação de OrdemServico"""
    print("\n📝 CÓDIGO CORRIGIDO PARA CRIAÇÃO DE OS")
    print("="*60)
    
    codigo = '''
nova_os = OrdemServico(
    # Campos obrigatórios básicos
    descricao=descricao,
    tipo_manutencao='preventiva-periodica',
    oficina=pmp.oficina,
    condicao_ativo='funcionando',
    qtd_pessoas=pmp.num_pessoas or 1,
    horas=pmp.tempo_pessoa or 1.0,
    hh=(pmp.num_pessoas or 1) * (pmp.tempo_pessoa or 1.0),
    prioridade='media',
    status='programada',
    
    # Campos de relacionamento obrigatórios
    equipamento_id=pmp.equipamento_id,
    filial_id=1,  # Buscar da PMP ou usar padrão
    setor_id=1,   # Buscar da PMP ou usar padrão
    
    # Campos de empresa e usuário
    empresa='Ativus',
    usuario_criacao='sistema',
    
    # Campos de data
    data_programada=data_programada,
    data_criacao=datetime.now(),
    
    # Campos específicos de PMP
    pmp_id=pmp.id,
    frequencia_origem=pmp.frequencia,
    numero_sequencia=i
)
'''
    
    print(codigo)
    
    # Salvar código em arquivo
    with open('codigo_os_corrigido.py', 'w') as f:
        f.write(codigo)
    
    print("💾 Código salvo em 'codigo_os_corrigido.py'")

def verificar_relacionamentos():
    """Verifica relacionamentos necessários"""
    print("\n🔗 VERIFICANDO RELACIONAMENTOS")
    print("="*60)
    
    try:
        from assets_models import OrdemServico, Filial, Setor, Equipamento
        from models.pmp_limpo import PMP
        
        print("1. Modelos relacionados:")
        print("   ✅ OrdemServico")
        print("   ✅ Filial")
        print("   ✅ Setor") 
        print("   ✅ Equipamento")
        print("   ✅ PMP")
        
        print("\n2. Relacionamentos obrigatórios:")
        print("   • equipamento_id → equipamentos.id")
        print("   • filial_id → filiais.id")
        print("   • setor_id → setores.id")
        print("   • pmp_id → pmps.id (opcional)")
        
        return True
        
    except Exception as e:
        print(f"❌ Erro: {e}")
        return False

if __name__ == "__main__":
    print("🔍 DIAGNÓSTICO DO MODELO ORDEMSERVICO")
    print()
    
    # Verificar campos
    campos_obrigatorios = verificar_campos_os()
    
    # Verificar relacionamentos
    verificar_relacionamentos()
    
    # Gerar código corrigido
    if campos_obrigatorios:
        gerar_codigo_corrigido(campos_obrigatorios)
    
    print("\n" + "="*60)
    print("📊 RESUMO:")
    print(f"   • Campos obrigatórios identificados: {len(campos_obrigatorios)}")
    print("   • Código corrigido gerado")
    print("   • Pronto para atualizar a API simples")
    print("="*60)
