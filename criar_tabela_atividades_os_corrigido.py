#!/usr/bin/env python3
"""
Script para criar a tabela 'atividades_os' no banco de dados do Heroku.
Versão corrigida para SQLAlchemy 2.x

Execute este comando no terminal:
heroku run python criar_tabela_atividades_os_corrigido.py --app seu-app-name
"""

import os
import sys
import logging
from datetime import datetime
from sqlalchemy import text

# Configurar logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def criar_tabela_atividades_os():
    """Cria a tabela atividades_os no banco de dados"""
    try:
        # Importar Flask e configurações
        from flask import Flask
        from models import db
        from config import config
        
        # Criar app Flask
        app = Flask(__name__)
        
        # Configurar app
        config_name = os.environ.get('FLASK_CONFIG', 'production')
        app.config.from_object(config[config_name])
        
        # Inicializar banco
        db.init_app(app)
        
        with app.app_context():
            logger.info("🔗 Conectando ao banco de dados...")
            
            # Verificar se a tabela já existe
            inspector = db.inspect(db.engine)
            tabelas_existentes = inspector.get_table_names()
            
            if 'atividades_os' in tabelas_existentes:
                logger.info("✅ Tabela 'atividades_os' já existe!")
                return True
            
            logger.info("📝 Criando tabela 'atividades_os'...")
            
            # SQL para criar a tabela
            sql_create_table = text("""
            CREATE TABLE atividades_os (
                id SERIAL PRIMARY KEY,
                os_id INTEGER NOT NULL,
                atividade_pmp_id INTEGER,
                descricao TEXT NOT NULL,
                instrucao TEXT,
                ordem INTEGER DEFAULT 1,
                status VARCHAR(20) DEFAULT 'pendente' NOT NULL,
                observacao TEXT,
                data_criacao TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                data_atualizacao TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                
                CONSTRAINT fk_atividades_os_os_id 
                    FOREIGN KEY (os_id) REFERENCES ordens_servico (id) ON DELETE CASCADE,
                    
                CONSTRAINT fk_atividades_os_atividade_pmp_id 
                    FOREIGN KEY (atividade_pmp_id) REFERENCES atividades_pmp (id) ON DELETE SET NULL,
                    
                CONSTRAINT ck_atividades_os_status 
                    CHECK (status IN ('pendente', 'conforme', 'nao_conforme', 'nao_aplicavel'))
            )
            """)
            
            # Executar o SQL usando a nova sintaxe
            with db.engine.connect() as connection:
                connection.execute(sql_create_table)
                connection.commit()
            
            logger.info("✅ Tabela 'atividades_os' criada com sucesso!")
            
            # Criar índices para melhor performance
            indices = [
                "CREATE INDEX idx_atividades_os_os_id ON atividades_os (os_id)",
                "CREATE INDEX idx_atividades_os_atividade_pmp_id ON atividades_os (atividade_pmp_id)",
                "CREATE INDEX idx_atividades_os_status ON atividades_os (status)",
                "CREATE INDEX idx_atividades_os_ordem ON atividades_os (os_id, ordem)"
            ]
            
            with db.engine.connect() as connection:
                for sql_index in indices:
                    try:
                        connection.execute(text(sql_index))
                        logger.info(f"✅ Índice criado: {sql_index.split()[2]}")
                    except Exception as e:
                        logger.warning(f"⚠️ Erro ao criar índice: {e}")
                connection.commit()
            
            logger.info("📊 Estrutura da tabela:")
            logger.info("   - id: Chave primária")
            logger.info("   - os_id: ID da Ordem de Serviço (FK)")
            logger.info("   - atividade_pmp_id: ID da Atividade PMP original (FK, opcional)")
            logger.info("   - descricao: Descrição da atividade")
            logger.info("   - instrucao: Instruções para execução")
            logger.info("   - ordem: Ordem de execução")
            logger.info("   - status: pendente, conforme, nao_conforme, nao_aplicavel")
            logger.info("   - observacao: Observações do executor")
            logger.info("   - data_criacao: Data de criação")
            logger.info("   - data_atualizacao: Data da última atualização")
            
            return True
            
    except ImportError as e:
        logger.error(f"❌ Erro de importação: {e}")
        logger.error("Certifique-se de que todos os módulos estão instalados")
        return False
        
    except Exception as e:
        logger.error(f"❌ Erro ao criar tabela: {e}")
        return False

def verificar_tabela():
    """Verifica se a tabela foi criada corretamente"""
    try:
        from flask import Flask
        from models import db
        from config import config
        
        app = Flask(__name__)
        config_name = os.environ.get('FLASK_CONFIG', 'production')
        app.config.from_object(config[config_name])
        db.init_app(app)
        
        with app.app_context():
            inspector = db.inspect(db.engine)
            
            if 'atividades_os' not in inspector.get_table_names():
                logger.error("❌ Tabela 'atividades_os' não foi encontrada!")
                return False
            
            # Verificar colunas
            colunas = inspector.get_columns('atividades_os')
            nomes_colunas = [col['name'] for col in colunas]
            
            colunas_esperadas = [
                'id', 'os_id', 'atividade_pmp_id', 'descricao', 'instrucao',
                'ordem', 'status', 'observacao', 'data_criacao', 'data_atualizacao'
            ]
            
            for coluna in colunas_esperadas:
                if coluna in nomes_colunas:
                    logger.info(f"✅ Coluna '{coluna}' encontrada")
                else:
                    logger.error(f"❌ Coluna '{coluna}' não encontrada")
                    return False
            
            logger.info("✅ Tabela 'atividades_os' verificada com sucesso!")
            return True
            
    except Exception as e:
        logger.error(f"❌ Erro ao verificar tabela: {e}")
        return False

def popular_atividades_exemplo():
    """Popula algumas atividades de exemplo se houver OS com PMP"""
    try:
        from flask import Flask
        from models import db
        from config import config
        from models.assets_models import OrdemServico
        from models.pmp_limpo import AtividadePMP
        
        app = Flask(__name__)
        config_name = os.environ.get('FLASK_CONFIG', 'production')
        app.config.from_object(config[config_name])
        db.init_app(app)
        
        with app.app_context():
            # Buscar OS que têm PMP mas não têm atividades
            sql_buscar_os = text("""
                SELECT os.id, os.pmp_id, os.descricao
                FROM ordens_servico os
                WHERE os.pmp_id IS NOT NULL
                AND NOT EXISTS (
                    SELECT 1 FROM atividades_os ao WHERE ao.os_id = os.id
                )
                LIMIT 5
            """)
            
            with db.engine.connect() as connection:
                result = connection.execute(sql_buscar_os)
                os_sem_atividades = result.fetchall()
            
            if not os_sem_atividades:
                logger.info("ℹ️ Não há OS com PMP sem atividades para popular")
                return True
            
            logger.info(f"📝 Encontradas {len(os_sem_atividades)} OS com PMP sem atividades")
            
            for os_row in os_sem_atividades:
                os_id, pmp_id, os_descricao = os_row
                
                # Buscar atividades do PMP
                atividades_pmp = AtividadePMP.query.filter_by(pmp_id=pmp_id).order_by(AtividadePMP.ordem).all()
                
                if atividades_pmp:
                    logger.info(f"📋 Copiando {len(atividades_pmp)} atividades para OS #{os_id}")
                    
                    for atividade_pmp in atividades_pmp:
                        sql_inserir = text("""
                            INSERT INTO atividades_os (os_id, atividade_pmp_id, descricao, instrucao, ordem, status)
                            VALUES (:os_id, :atividade_pmp_id, :descricao, :instrucao, :ordem, 'pendente')
                        """)
                        
                        with db.engine.connect() as connection:
                            connection.execute(sql_inserir, {
                                'os_id': os_id,
                                'atividade_pmp_id': atividade_pmp.id,
                                'descricao': atividade_pmp.descricao,
                                'instrucao': getattr(atividade_pmp, 'instrucao', None),
                                'ordem': atividade_pmp.ordem
                            })
                            connection.commit()
                    
                    logger.info(f"✅ Atividades copiadas para OS #{os_id}")
            
            return True
            
    except Exception as e:
        logger.error(f"❌ Erro ao popular atividades de exemplo: {e}")
        return False

if __name__ == "__main__":
    logger.info("🚀 Iniciando criação da tabela 'atividades_os'...")
    
    if criar_tabela_atividades_os():
        logger.info("🔍 Verificando tabela criada...")
        if verificar_tabela():
            logger.info("📝 Populando atividades de exemplo...")
            popular_atividades_exemplo()
            
            logger.info("🎉 Processo concluído com sucesso!")
            logger.info("")
            logger.info("📋 Próximos passos:")
            logger.info("1. Verificar se os blueprints foram registrados no app.py")
            logger.info("2. Incluir o JavaScript na página de programação")
            logger.info("3. Testar a funcionalidade")
            logger.info("")
            logger.info("🧪 Para testar:")
            logger.info("- Acesse a página de programação")
            logger.info("- Procure por OS com badge 'PMP'")
            logger.info("- Clique no botão de lista para ver as atividades")
        else:
            logger.error("❌ Falha na verificação da tabela")
            sys.exit(1)
    else:
        logger.error("❌ Falha ao criar a tabela")
        sys.exit(1)
