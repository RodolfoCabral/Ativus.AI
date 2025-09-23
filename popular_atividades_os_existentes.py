#!/usr/bin/env python3
"""
Script para popular atividades nas OS existentes que foram geradas a partir de PMPs.
Execute este comando no Heroku:

heroku run python popular_atividades_os_existentes.py --app seu-app-name
"""

import os
import sys
import logging
from datetime import datetime
from sqlalchemy import text

# Configurar logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def popular_atividades_os():
    """Popula atividades nas OS que foram geradas a partir de PMPs"""
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
            
            # Buscar OS que têm PMP mas não têm atividades
            sql_buscar_os = text("""
                SELECT os.id, os.pmp_id, os.descricao
                FROM ordens_servico os
                WHERE os.pmp_id IS NOT NULL
                AND NOT EXISTS (
                    SELECT 1 FROM atividades_os ao WHERE ao.os_id = os.id
                )
                ORDER BY os.id
            """)
            
            with db.engine.connect() as connection:
                result = connection.execute(sql_buscar_os)
                os_sem_atividades = result.fetchall()
            
            if not os_sem_atividades:
                logger.info("ℹ️ Não há OS com PMP sem atividades para popular")
                return True
            
            logger.info(f"📝 Encontradas {len(os_sem_atividades)} OS com PMP sem atividades")
            
            total_atividades_criadas = 0
            
            for os_row in os_sem_atividades:
                os_id, pmp_id, os_descricao = os_row
                logger.info(f"📋 Processando OS #{os_id} (PMP #{pmp_id})")
                
                # Buscar atividades do PMP
                sql_buscar_atividades_pmp = text("""
                    SELECT id, descricao, ordem
                    FROM atividades_pmp
                    WHERE pmp_id = :pmp_id
                    ORDER BY ordem
                """)
                
                with db.engine.connect() as connection:
                    result = connection.execute(sql_buscar_atividades_pmp, {'pmp_id': pmp_id})
                    atividades_pmp = result.fetchall()
                
                if not atividades_pmp:
                    logger.warning(f"⚠️ PMP #{pmp_id} não tem atividades cadastradas")
                    continue
                
                logger.info(f"   📝 Copiando {len(atividades_pmp)} atividades...")
                
                # Inserir atividades na OS
                for atividade_pmp in atividades_pmp:
                    atividade_pmp_id, descricao, ordem = atividade_pmp
                    
                    sql_inserir = text("""
                        INSERT INTO atividades_os (
                            os_id, 
                            atividade_pmp_id, 
                            descricao, 
                            ordem, 
                            status,
                            data_criacao,
                            data_atualizacao
                        ) VALUES (
                            :os_id, 
                            :atividade_pmp_id, 
                            :descricao, 
                            :ordem, 
                            'pendente',
                            CURRENT_TIMESTAMP,
                            CURRENT_TIMESTAMP
                        )
                    """)
                    
                    with db.engine.connect() as connection:
                        connection.execute(sql_inserir, {
                            'os_id': os_id,
                            'atividade_pmp_id': atividade_pmp_id,
                            'descricao': descricao,
                            'ordem': ordem
                        })
                        connection.commit()
                    
                    total_atividades_criadas += 1
                
                logger.info(f"   ✅ {len(atividades_pmp)} atividades copiadas para OS #{os_id}")
            
            logger.info(f"🎉 Processo concluído!")
            logger.info(f"   📊 Total de OS processadas: {len(os_sem_atividades)}")
            logger.info(f"   📊 Total de atividades criadas: {total_atividades_criadas}")
            
            return True
            
    except Exception as e:
        logger.error(f"❌ Erro ao popular atividades: {e}")
        return False

def verificar_resultado():
    """Verifica o resultado da população de atividades"""
    try:
        from flask import Flask
        from models import db
        from config import config
        
        app = Flask(__name__)
        config_name = os.environ.get('FLASK_CONFIG', 'production')
        app.config.from_object(config[config_name])
        db.init_app(app)
        
        with app.app_context():
            # Contar OS com PMP e suas atividades
            sql_verificar = text("""
                SELECT 
                    COUNT(DISTINCT os.id) as total_os_pmp,
                    COUNT(ao.id) as total_atividades,
                    AVG(atividades_por_os.qtd) as media_atividades_por_os
                FROM ordens_servico os
                LEFT JOIN atividades_os ao ON os.id = ao.os_id
                LEFT JOIN (
                    SELECT os_id, COUNT(*) as qtd
                    FROM atividades_os
                    GROUP BY os_id
                ) atividades_por_os ON os.id = atividades_por_os.os_id
                WHERE os.pmp_id IS NOT NULL
            """)
            
            with db.engine.connect() as connection:
                result = connection.execute(sql_verificar)
                stats = result.fetchone()
            
            total_os_pmp, total_atividades, media_atividades = stats
            
            logger.info("📊 Estatísticas finais:")
            logger.info(f"   • OS com PMP: {total_os_pmp}")
            logger.info(f"   • Total de atividades: {total_atividades}")
            logger.info(f"   • Média de atividades por OS: {media_atividades:.1f}" if media_atividades else "   • Média de atividades por OS: 0")
            
            # Mostrar algumas OS com atividades
            sql_exemplos = text("""
                SELECT os.id, os.descricao, COUNT(ao.id) as qtd_atividades
                FROM ordens_servico os
                LEFT JOIN atividades_os ao ON os.id = ao.os_id
                WHERE os.pmp_id IS NOT NULL
                GROUP BY os.id, os.descricao
                ORDER BY os.id
                LIMIT 5
            """)
            
            with db.engine.connect() as connection:
                result = connection.execute(sql_exemplos)
                exemplos = result.fetchall()
            
            if exemplos:
                logger.info("📋 Exemplos de OS com atividades:")
                for os_id, descricao, qtd_atividades in exemplos:
                    logger.info(f"   • OS #{os_id}: {qtd_atividades} atividades - {descricao[:50]}...")
            
            return True
            
    except Exception as e:
        logger.error(f"❌ Erro ao verificar resultado: {e}")
        return False

if __name__ == "__main__":
    logger.info("🚀 Iniciando população de atividades nas OS existentes...")
    
    if popular_atividades_os():
        logger.info("🔍 Verificando resultado...")
        verificar_resultado()
        
        logger.info("")
        logger.info("✅ Processo concluído com sucesso!")
        logger.info("")
        logger.info("📋 Próximos passos:")
        logger.info("1. Adicionar o código JavaScript à página de execução de OS")
        logger.info("2. Testar abrindo uma OS que foi gerada a partir de PMP")
        logger.info("3. Verificar se as atividades aparecem na Lista de Execução")
        
    else:
        logger.error("❌ Falha ao popular atividades")
        sys.exit(1)
