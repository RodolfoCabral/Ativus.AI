#!/usr/bin/env python3
"""
Script para inicializar a tabela de ordens de serviço no banco de dados
"""

import os
import sys
from app import create_app, db

# Importação segura dos modelos
try:
    from assets_models import OrdemServico
    OS_AVAILABLE = True
except ImportError as e:
    print(f"Erro ao importar modelo OrdemServico: {e}")
    OS_AVAILABLE = False

def init_os_table():
    """Inicializa a tabela de ordens de serviço no banco de dados"""
    
    if not OS_AVAILABLE:
        print("❌ Modelo OrdemServico não disponível. Verifique o arquivo assets_models.py")
        return False
    
    app = create_app()
    
    with app.app_context():
        try:
            # Verificar se a tabela já existe
            if db.engine.dialect.has_table(db.engine, 'ordens_servico'):
                print("ℹ️  Tabela 'ordens_servico' já existe")
                
                # Verificar se há registros
                count = OrdemServico.query.count()
                print(f"📊 Total de ordens de serviço existentes: {count}")
                
            else:
                print("🔨 Criando tabela 'ordens_servico'...")
                
                # Criar tabela
                db.create_all()
                
                print("✅ Tabela 'ordens_servico' criada com sucesso!")
                
                # Verificar se foi criada corretamente
                if db.engine.dialect.has_table(db.engine, 'ordens_servico'):
                    print("✅ Verificação: Tabela criada corretamente")
                else:
                    print("❌ Erro: Tabela não foi criada")
                    return False
            
            # Mostrar estrutura da tabela
            print("\n📋 Estrutura da tabela 'ordens_servico':")
            print("   - id (Integer, Primary Key)")
            print("   - chamado_id (Integer, Foreign Key)")
            print("   - descricao (Text)")
            print("   - tipo_manutencao (String)")
            print("   - oficina (String)")
            print("   - condicao_ativo (String)")
            print("   - qtd_pessoas (Integer)")
            print("   - horas (Float)")
            print("   - hh (Float)")
            print("   - prioridade (String)")
            print("   - status (String)")
            print("   - filial_id (Integer, Foreign Key)")
            print("   - setor_id (Integer, Foreign Key)")
            print("   - equipamento_id (Integer, Foreign Key)")
            print("   - empresa (String)")
            print("   - usuario_criacao (String)")
            print("   - usuario_responsavel (String)")
            print("   - data_criacao (DateTime)")
            print("   - data_programada (Date)")
            print("   - data_inicio (DateTime)")
            print("   - data_conclusao (DateTime)")
            print("   - data_atualizacao (DateTime)")
            
            print("\n🎉 Inicialização da tabela de ordens de serviço concluída!")
            return True
            
        except Exception as e:
            print(f"❌ Erro ao inicializar tabela de ordens de serviço: {e}")
            return False

if __name__ == '__main__':
    print("🚀 Inicializando tabela de ordens de serviço...")
    print("=" * 50)
    
    success = init_os_table()
    
    print("=" * 50)
    if success:
        print("✅ Script executado com sucesso!")
        sys.exit(0)
    else:
        print("❌ Script falhou!")
        sys.exit(1)

