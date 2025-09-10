#!/usr/bin/env python3
"""
Script para corrigir o problema do atributo 'atividade' que não existe no objeto PMP
"""

import os
import sys
import logging
from datetime import datetime, date

# Configurar logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Adicionar diretório atual ao path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    # Importar Flask e criar app
    from flask import Flask
    app = Flask(__name__)
    
    # Configurar banco de dados
    from models import db
    
    # Obter URL do banco de dados
    database_url = os.environ.get('DATABASE_URL')
    if database_url and database_url.startswith('postgres://'):
        database_url = database_url.replace('postgres://', 'postgresql://', 1)
    
    app.config['SQLALCHEMY_DATABASE_URI'] = database_url or 'postgresql://postgres:postgres@localhost:5432/ativus'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    # Inicializar banco de dados
    with app.app_context():
        db.init_app(app)
        
        # Importar modelos
        from models.pmp_limpo import PMP
        from assets_models import OrdemServico
        
        logger.info("🔍 Verificando estrutura da tabela PMP")
        
        # Verificar se a coluna 'atividade' existe
        from sqlalchemy import inspect
        inspector = inspect(db.engine)
        colunas_pmp = [c['name'] for c in inspector.get_columns('pmps')]
        
        logger.info(f"📋 Colunas encontradas na tabela PMP: {colunas_pmp}")
        
        # Verificar qual coluna usar como descrição
        coluna_descricao = None
        for candidato in ['atividade', 'descricao', 'nome', 'titulo', 'description']:
            if candidato in colunas_pmp:
                coluna_descricao = candidato
                logger.info(f"✅ Coluna de descrição encontrada: {coluna_descricao}")
                break
        
        if not coluna_descricao:
            logger.error("❌ Nenhuma coluna de descrição encontrada na tabela PMP")
            sys.exit(1)
        
        # Corrigir código que usa o atributo 'atividade'
        logger.info("🔧 Corrigindo arquivos que usam o atributo 'atividade'")
        
        # 1. Corrigir pmp_os_generator.py
        try:
            with open('routes/pmp_os_generator.py', 'r') as f:
                conteudo = f.read()
            
            # Substituir todas as ocorrências de pmp.atividade
            conteudo_corrigido = conteudo.replace('pmp.atividade', f'getattr(pmp, "{coluna_descricao}", "PMP")')
            
            with open('routes/pmp_os_generator.py', 'w') as f:
                f.write(conteudo_corrigido)
            
            logger.info("✅ Arquivo pmp_os_generator.py corrigido")
        except Exception as e:
            logger.error(f"❌ Erro ao corrigir pmp_os_generator.py: {e}")
        
        # 2. Corrigir pmp_scheduler.py
        try:
            with open('routes/pmp_scheduler.py', 'r') as f:
                conteudo = f.read()
            
            # Substituir todas as ocorrências de pmp.atividade
            conteudo_corrigido = conteudo.replace('pmp.atividade', f'getattr(pmp, "{coluna_descricao}", "PMP")')
            # Substituir todas as ocorrências de pmp_atividade
            conteudo_corrigido = conteudo_corrigido.replace("'pmp_atividade': pmp.atividade", f"'pmp_atividade': getattr(pmp, '{coluna_descricao}', 'PMP')")
            
            with open('routes/pmp_scheduler.py', 'w') as f:
                f.write(conteudo_corrigido)
            
            logger.info("✅ Arquivo pmp_scheduler.py corrigido")
        except Exception as e:
            logger.error(f"❌ Erro ao corrigir pmp_scheduler.py: {e}")
        
        # 3. Corrigir pmp_analytics.py se existir
        try:
            if os.path.exists('routes/pmp_analytics.py'):
                with open('routes/pmp_analytics.py', 'r') as f:
                    conteudo = f.read()
                
                # Substituir todas as ocorrências de pmp.atividade
                conteudo_corrigido = conteudo.replace('pmp.atividade', f'getattr(pmp, "{coluna_descricao}", "PMP")')
                
                with open('routes/pmp_analytics.py', 'w') as f:
                    f.write(conteudo_corrigido)
                
                logger.info("✅ Arquivo pmp_analytics.py corrigido")
        except Exception as e:
            logger.error(f"❌ Erro ao corrigir pmp_analytics.py: {e}")
        
        logger.info("✅ Correção concluída com sucesso!")

except Exception as e:
    logger.error(f"❌ Erro geral: {e}")
    sys.exit(1)

