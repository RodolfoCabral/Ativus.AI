"""
Sistema de transferência automática de atividades após login
"""

from flask import current_app
from models import db
import threading
import time
from datetime import datetime, timedelta


class AutoTransferirAtividades:
    def __init__(self):
        self.ultima_execucao = None
        self.executando = False
        self.intervalo_minimo = 300  # 5 minutos entre execuções
    
    def deve_executar(self):
        """Verifica se deve executar a transferência"""
        if self.executando:
            return False
        
        if self.ultima_execucao is None:
            return True
        
        agora = datetime.now()
        if (agora - self.ultima_execucao).seconds > self.intervalo_minimo:
            return True
        
        return False

    def executar_transferencia(self, app):
        """Executa a transferência de atividades (dentro do contexto Flask)"""
        with app.app_context():
            if not self.deve_executar():
                app.logger.info("🔄 Transferência de atividades: muito recente, pulando")
                return

            self.executando = True
            self.ultima_execucao = datetime.now()

            try:
                app.logger.info("🚀 Iniciando transferência automática de atividades")
                
                # Verificar quantas OS precisam de transferência
                result = db.engine.execute('''
                    SELECT COUNT(*) 
                    FROM ordens_servico os 
                    WHERE os.pmp_id IS NOT NULL 
                    AND os.id NOT IN (SELECT DISTINCT os_id FROM atividades_os WHERE os_id IS NOT NULL)
                ''')
                total_pendentes = result.fetchone()[0]
                
                if total_pendentes == 0:
                    app.logger.info("✅ Todas as OS já têm atividades - nada para transferir")
                    return
                
                app.logger.info(f"📊 Encontradas {total_pendentes} OS que precisam de atividades")
                
                # Executar transferência
                db.engine.execute('''
                    INSERT INTO atividades_os (os_id, atividade_pmp_id, descricao, ordem, status, data_criacao, data_atualizacao)
                    SELECT 
                        os.id as os_id,
                        ap.id as atividade_pmp_id,
                        ap.descricao,
                        ap.ordem,
                        'pendente' as status,
                        NOW() as data_criacao,
                        NOW() as data_atualizacao
                    FROM ordens_servico os
                    INNER JOIN atividades_pmp ap ON os.pmp_id = ap.pmp_id
                    WHERE os.pmp_id IS NOT NULL
                    AND os.id NOT IN (SELECT DISTINCT os_id FROM atividades_os WHERE os_id IS NOT NULL)
                ''')
                
                db.session.commit()
                
                result = db.engine.execute('SELECT COUNT(*) FROM atividades_os')
                total_atividades = result.fetchone()[0]
                
                app.logger.info(f"✅ Transferência concluída! Total de atividades_os: {total_atividades}")
            
            except Exception as e:
                app.logger.error(f"❌ Erro na transferência automática: {e}")
                db.session.rollback()
            finally:
                self.executando = False

    def executar_em_background(self, app):
        """Executa a transferência em thread separada"""
        thread = threading.Thread(target=self.executar_transferencia, args=(app,))
        thread.daemon = True
        thread.start()


# Instância global
auto_transferir = AutoTransferirAtividades()


def executar_apos_login():
    """Função para ser chamada após login bem-sucedido"""
    try:
        app = current_app._get_current_object()
        app.logger.info("🔄 Login detectado - verificando necessidade de transferência de atividades")
        auto_transferir.executar_em_background(app)
    except Exception as e:
        current_app.logger.error(f"❌ Erro ao iniciar transferência automática: {e}")


def executar_na_inicializacao():
    """Função para ser chamada na inicialização do app"""
    try:
        app = current_app._get_current_object()
        app.logger.info("🚀 Inicialização do app - verificando atividades pendentes")

        def delayed_execution():
            time.sleep(5)
            auto_transferir.executar_transferencia(app)
        
        thread = threading.Thread(target=delayed_execution)
        thread.daemon = True
        thread.start()
        
    except Exception as e:
        current_app.logger.error(f"❌ Erro na inicialização automática: {e}")


def verificar_status():
    """Retorna status da transferência automática"""
    return {
        'ultima_execucao': auto_transferir.ultima_execucao.isoformat() if auto_transferir.ultima_execucao else None,
        'executando': auto_transferir.executando,
        'intervalo_minimo': auto_transferir.intervalo_minimo
    }
