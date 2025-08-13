#!/usr/bin/env python3
"""
Script para inicializar o banco de dados da aplicação SaaS Ativus.
Este script deve ser executado após o deploy no Heroku.
"""

import os
import sys
import logging
from datetime import datetime

# Configurar logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def init_database():
    """Inicializa o banco de dados criando todas as tabelas necessárias"""
    try:
        logger.info("🗄️ Iniciando configuração do banco de dados...")
        
        # Importar a aplicação
        from app import create_app
        from models import db
        
        # Tentar importar modelos específicos
        try:
            from models.plano_mestre import PlanoMestre, AtividadePlanoMestre, HistoricoExecucaoPlano
            logger.info("✅ Modelos do plano mestre importados com sucesso")
        except ImportError as e:
            logger.warning(f"⚠️ Não foi possível importar modelos do plano mestre: {e}")
        
        # Criar aplicação
        app = create_app()
        
        with app.app_context():
            logger.info("🔧 Criando todas as tabelas...")
            
            # Criar todas as tabelas
            db.create_all()
            
            # Verificar se as tabelas foram criadas
            inspector = db.inspect(db.engine)
            tabelas = inspector.get_table_names()
            
            logger.info("📋 Tabelas criadas no banco de dados:")
            for tabela in sorted(tabelas):
                logger.info(f"  ✅ {tabela}")
            
            # Verificar tabelas específicas do plano mestre
            tabelas_plano_mestre = [t for t in tabelas if 'plano' in t.lower()]
            if tabelas_plano_mestre:
                logger.info("🎯 Tabelas do plano mestre encontradas:")
                for tabela in tabelas_plano_mestre:
                    logger.info(f"  ✅ {tabela}")
            else:
                logger.warning("⚠️ Nenhuma tabela do plano mestre foi encontrada")
            
            logger.info("🎉 Banco de dados inicializado com sucesso!")
            return True
            
    except Exception as e:
        logger.error(f"❌ Erro ao inicializar banco de dados: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_database_connection():
    """Testa a conexão com o banco de dados"""
    try:
        logger.info("🔍 Testando conexão com o banco de dados...")
        
        from app import create_app
        from models import db
        
        app = create_app()
        
        with app.app_context():
            # Tentar executar uma query simples
            result = db.engine.execute("SELECT 1 as test")
            test_value = result.fetchone()[0]
            
            if test_value == 1:
                logger.info("✅ Conexão com o banco de dados OK")
                return True
            else:
                logger.error("❌ Teste de conexão falhou")
                return False
                
    except Exception as e:
        logger.error(f"❌ Erro ao testar conexão: {e}")
        return False

def main():
    """Função principal"""
    logger.info("🚀 Iniciando script de configuração do banco de dados")
    logger.info(f"📅 Data/Hora: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Verificar variáveis de ambiente
    database_url = os.environ.get('DATABASE_URL') or os.environ.get('HEROKU_POSTGRESQL_NAVY_URL')
    if database_url:
        logger.info(f"🔗 URL do banco encontrada: {database_url[:50]}...")
    else:
        logger.warning("⚠️ URL do banco de dados não encontrada nas variáveis de ambiente")
    
    # Testar conexão
    if not test_database_connection():
        logger.error("❌ Falha na conexão com o banco. Abortando.")
        sys.exit(1)
    
    # Inicializar banco
    if init_database():
        logger.info("🎉 Configuração concluída com sucesso!")
        sys.exit(0)
    else:
        logger.error("❌ Falha na configuração do banco de dados")
        sys.exit(1)

if __name__ == "__main__":
    main()

