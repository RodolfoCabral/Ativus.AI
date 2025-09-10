#!/usr/bin/env python3
"""
Script para corrigir o problema do atributo 'atividade' que não existe no objeto PMP
Versão para Heroku que usa a variável DATABASE_URL corretamente
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
    
    # Obter URL do banco de dados do Heroku
    database_url = os.environ.get('DATABASE_URL')
    logger.info(f"🔌 DATABASE_URL: {database_url}")
    
    if not database_url:
        logger.error("❌ DATABASE_URL não encontrada no ambiente")
        database_url = os.environ.get('HEROKU_POSTGRESQL_NAVY_URL')
        logger.info(f"🔌 Tentando HEROKU_POSTGRESQL_NAVY_URL: {database_url}")
    
    if not database_url:
        logger.error("❌ Nenhuma URL de banco de dados encontrada no ambiente")
        sys.exit(1)
    
    # Converter postgres:// para postgresql://
    if database_url.startswith('postgres://'):
        database_url = database_url.replace('postgres://', 'postgresql://', 1)
        logger.info(f"🔄 URL convertida: {database_url}")
    
    app.config['SQLALCHEMY_DATABASE_URI'] = database_url
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    logger.info(f"🔌 Conectando ao banco de dados: {database_url}")
    
    # Inicializar banco de dados
    with app.app_context():
        db.init_app(app)
        
        # Verificar conexão
        try:
            db.engine.execute("SELECT 1")
            logger.info("✅ Conexão com o banco de dados estabelecida com sucesso")
        except Exception as e:
            logger.error(f"❌ Erro ao conectar ao banco de dados: {e}")
            sys.exit(1)
        
        # Importar modelos
        try:
            from models.pmp_limpo import PMP
            from assets_models import OrdemServico
            logger.info("✅ Modelos importados com sucesso")
        except Exception as e:
            logger.error(f"❌ Erro ao importar modelos: {e}")
            sys.exit(1)
        
        logger.info("🔍 Verificando estrutura da tabela PMP")
        
        # Verificar se a tabela existe
        from sqlalchemy import inspect
        inspector = inspect(db.engine)
        if 'pmps' not in inspector.get_table_names():
            logger.error("❌ Tabela 'pmps' não encontrada no banco de dados")
            sys.exit(1)
        
        # Verificar se a coluna 'atividade' existe
        colunas_pmp = [c['name'] for c in inspector.get_columns('pmps')]
        
        logger.info(f"📋 Colunas encontradas na tabela PMP: {colunas_pmp}")
        
        # Verificar qual coluna usar como descrição
        coluna_descricao = None
        for candidato in ['atividade', 'descricao', 'nome', 'titulo', 'description', 'tag']:
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

