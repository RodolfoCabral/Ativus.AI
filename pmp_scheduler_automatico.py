#!/usr/bin/env python3
"""
Sistema de Scheduler Automático para Geração de OS baseado em PMPs
Executa em background para gerar OS automaticamente sem intervenção manual
"""

import os
import sys
import time
import logging
import schedule
from datetime import datetime, timedelta
from threading import Thread

# Adicionar o diretório atual ao path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('pmp_scheduler.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger('pmp_scheduler')

class PMPSchedulerAutomatico:
    """Scheduler automático para geração de OS baseado em PMPs"""
    
    def __init__(self):
        self.running = False
        self.thread = None
        self.last_execution = None
        self.execution_count = 0
        
    def executar_geracao_automatica(self):
        """Executa geração automática de OS"""
        try:
            logger.info("🤖 Iniciando execução automática de geração de OS")
            
            # Importar dentro da função para evitar problemas de contexto
            from app import create_app
            from sistema_geracao_os_pmp_aprimorado import gerar_todas_os_pmp
            
            # Criar contexto da aplicação
            app = create_app()
            
            with app.app_context():
                # Executar geração
                resultado = gerar_todas_os_pmp()
                
                if resultado['success']:
                    stats = resultado['estatisticas']
                    os_geradas = stats['os_geradas']
                    pmps_processadas = stats['pmps_processadas']
                    
                    logger.info(f"✅ Execução concluída: {os_geradas} OS geradas de {pmps_processadas} PMPs processadas")
                    
                    # Log detalhado se OS foram geradas
                    if os_geradas > 0:
                        logger.info(f"📋 Detalhes: {stats['os_ja_existentes']} OS já existiam, {stats['erros']} erros")
                        
                        # Log das OS geradas (primeiras 5)
                        if 'os_geradas' in resultado and resultado['os_geradas']:
                            logger.info("🆕 Novas OS geradas:")
                            for i, os in enumerate(resultado['os_geradas'][:5], 1):
                                logger.info(f"  {i}. OS #{os['id']}: {os['descricao']}")
                            
                            if len(resultado['os_geradas']) > 5:
                                logger.info(f"  ... e mais {len(resultado['os_geradas']) - 5} OS")
                    
                    self.last_execution = datetime.now()
                    self.execution_count += 1
                    
                else:
                    logger.error(f"❌ Erro na execução automática: {resultado['error']}")
                    
        except Exception as e:
            logger.error(f"❌ Erro crítico na execução automática: {e}")
            import traceback
            logger.error(traceback.format_exc())
    
    def verificar_sistema(self):
        """Verifica status do sistema"""
        try:
            logger.info("🔍 Verificando status do sistema PMP")
            
            from app import create_app
            from sistema_geracao_os_pmp_aprimorado import verificar_pendencias_os_pmp
            
            app = create_app()
            
            with app.app_context():
                resultado = verificar_pendencias_os_pmp()
                
                if resultado['success']:
                    total_pendencias = resultado['total_pmps_com_pendencias']
                    total_os_pendentes = resultado['total_os_pendentes']
                    
                    if total_pendencias > 0:
                        logger.info(f"⚠️ Sistema tem {total_pendencias} PMPs com {total_os_pendentes} OS pendentes")
                    else:
                        logger.info("✅ Sistema em dia - nenhuma pendência encontrada")
                else:
                    logger.warning(f"⚠️ Erro ao verificar pendências: {resultado['error']}")
                    
        except Exception as e:
            logger.error(f"❌ Erro ao verificar sistema: {e}")
    
    def configurar_agendamentos(self):
        """Configura os agendamentos automáticos"""
        logger.info("📅 Configurando agendamentos automáticos")
        
        # Execução principal: todos os dias às 6h da manhã
        schedule.every().day.at("06:00").do(self.executar_geracao_automatica)
        logger.info("  ⏰ Geração automática agendada para 06:00 diariamente")
        
        # Execução adicional: todos os dias às 18h
        schedule.every().day.at("18:00").do(self.executar_geracao_automatica)
        logger.info("  ⏰ Geração automática agendada para 18:00 diariamente")
        
        # Verificação de sistema: a cada 2 horas durante horário comercial
        for hora in [8, 10, 12, 14, 16]:
            schedule.every().day.at(f"{hora:02d}:00").do(self.verificar_sistema)
        logger.info("  🔍 Verificações de sistema agendadas para horário comercial")
        
        # Execução de emergência: a cada 30 minutos durante horário comercial
        # (apenas se houver pendências críticas)
        schedule.every(30).minutes.do(self.verificar_e_executar_se_necessario)
        logger.info("  🚨 Verificação de emergência a cada 30 minutos")
    
    def verificar_e_executar_se_necessario(self):
        """Verifica se há pendências críticas e executa se necessário"""
        try:
            # Só executar durante horário comercial (7h às 19h)
            agora = datetime.now()
            if not (7 <= agora.hour <= 19):
                return
            
            from app import create_app
            from sistema_geracao_os_pmp_aprimorado import verificar_pendencias_os_pmp
            
            app = create_app()
            
            with app.app_context():
                resultado = verificar_pendencias_os_pmp()
                
                if resultado['success']:
                    total_os_pendentes = resultado['total_os_pendentes']
                    
                    # Executar se há mais de 5 OS pendentes
                    if total_os_pendentes > 5:
                        logger.warning(f"🚨 Execução de emergência: {total_os_pendentes} OS pendentes")
                        self.executar_geracao_automatica()
                        
        except Exception as e:
            logger.error(f"❌ Erro na verificação de emergência: {e}")
    
    def executar_loop(self):
        """Loop principal do scheduler"""
        logger.info("🚀 Iniciando loop do scheduler automático")
        
        while self.running:
            try:
                schedule.run_pending()
                time.sleep(60)  # Verificar a cada minuto
                
            except KeyboardInterrupt:
                logger.info("⏹️ Interrupção manual recebida")
                break
            except Exception as e:
                logger.error(f"❌ Erro no loop do scheduler: {e}")
                time.sleep(60)  # Aguardar antes de tentar novamente
        
        logger.info("🛑 Loop do scheduler finalizado")
    
    def iniciar(self):
        """Inicia o scheduler em thread separada"""
        if self.running:
            logger.warning("⚠️ Scheduler já está executando")
            return
        
        logger.info("🎬 Iniciando scheduler automático de PMPs")
        
        self.running = True
        self.configurar_agendamentos()
        
        # Executar primeira verificação imediatamente
        logger.info("🔄 Executando verificação inicial")
        self.verificar_sistema()
        
        # Iniciar thread do loop
        self.thread = Thread(target=self.executar_loop, daemon=True)
        self.thread.start()
        
        logger.info("✅ Scheduler automático iniciado com sucesso")
    
    def parar(self):
        """Para o scheduler"""
        logger.info("🛑 Parando scheduler automático")
        
        self.running = False
        
        if self.thread and self.thread.is_alive():
            self.thread.join(timeout=5)
        
        logger.info("✅ Scheduler automático parado")
    
    def status(self):
        """Retorna status do scheduler"""
        return {
            'running': self.running,
            'last_execution': self.last_execution.isoformat() if self.last_execution else None,
            'execution_count': self.execution_count,
            'next_runs': [str(job.next_run) for job in schedule.jobs[:3]]
        }

# Instância global do scheduler
scheduler_instance = None

def iniciar_scheduler():
    """Inicia o scheduler global"""
    global scheduler_instance
    
    if scheduler_instance is None:
        scheduler_instance = PMPSchedulerAutomatico()
    
    scheduler_instance.iniciar()
    return scheduler_instance

def parar_scheduler():
    """Para o scheduler global"""
    global scheduler_instance
    
    if scheduler_instance:
        scheduler_instance.parar()

def status_scheduler():
    """Retorna status do scheduler global"""
    global scheduler_instance
    
    if scheduler_instance:
        return scheduler_instance.status()
    else:
        return {'running': False, 'message': 'Scheduler não inicializado'}

if __name__ == "__main__":
    # Execução direta do script
    import signal
    
    def signal_handler(sig, frame):
        logger.info("🛑 Sinal de interrupção recebido")
        if scheduler_instance:
            scheduler_instance.parar()
        sys.exit(0)
    
    # Configurar handler para SIGINT (Ctrl+C)
    signal.signal(signal.SIGINT, signal_handler)
    
    try:
        # Iniciar scheduler
        scheduler = iniciar_scheduler()
        
        logger.info("🎯 Scheduler automático de PMPs em execução")
        logger.info("   Pressione Ctrl+C para parar")
        
        # Manter o processo vivo
        while scheduler.running:
            time.sleep(1)
            
    except Exception as e:
        logger.error(f"❌ Erro fatal: {e}")
        sys.exit(1)
