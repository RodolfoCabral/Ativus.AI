#!/usr/bin/env python3
"""
Sistema Aprimorado de Geração Automática de OS baseado em PMPs
Versão melhorada com validações, logs detalhados e controle de frequências
"""

from datetime import datetime, timedelta, date
from dateutil.relativedelta import relativedelta
import json
import logging
from models import db
from models.pmp_limpo import PMP, AtividadePMP
from assets_models import OrdemServico
from models.atividade_os import AtividadeOS

# Configurar logging específico para o sistema
logger = logging.getLogger('pmp_os_generator')
logger.setLevel(logging.INFO)

class GeradorOSPMPAprimorado:
    """Classe aprimorada para geração automática de OS baseada em PMPs"""
    
    def __init__(self):
        self.hoje = date.today()
        self.os_geradas = []
        self.log_operacoes = []
        self.estatisticas = {
            'pmps_processadas': 0,
            'os_geradas': 0,
            'os_ja_existentes': 0,
            'erros': 0,
            'pmps_inativas': 0,
            'pmps_sem_data_inicio': 0,
            'pmps_com_data_fim_passada': 0
        }
    
    def log(self, mensagem, nivel='info'):
        """Adiciona mensagem ao log de operações com timestamp"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_entry = f"[{timestamp}] {mensagem}"
        self.log_operacoes.append(log_entry)
        
        # Log no sistema também
        if nivel == 'error':
            logger.error(log_entry)
        elif nivel == 'warning':
            logger.warning(log_entry)
        else:
            logger.info(log_entry)
        
        print(log_entry)
    
    def validar_pmp(self, pmp):
        """
        Valida se uma PMP está apta para gerar OS
        
        Args:
            pmp (PMP): Objeto PMP a ser validado
        
        Returns:
            tuple: (bool, str) - (é_válida, motivo_se_inválida)
        """
        # Verificar se PMP está ativa
        if pmp.status != 'ativo':
            self.estatisticas['pmps_inativas'] += 1
            return False, f"PMP não está ativa (status: {pmp.status})"
        
        # Verificar se tem data de início
        if not pmp.data_inicio_plano:
            self.estatisticas['pmps_sem_data_inicio'] += 1
            return False, "PMP não tem data de início definida"
        
        # Verificar se data de início já passou
        if pmp.data_inicio_plano > self.hoje:
            return False, f"Data de início ainda não chegou ({pmp.data_inicio_plano})"
        
        # Verificar se PMP não expirou
        if pmp.data_fim_plano and pmp.data_fim_plano <= self.hoje:
            self.estatisticas['pmps_com_data_fim_passada'] += 1
            return False, f"PMP expirou em {pmp.data_fim_plano}"
        
        # Verificar se tem frequência definida
        if not pmp.frequencia:
            return False, "PMP não tem frequência definida"
        
        return True, "PMP válida"
    
    def normalizar_frequencia(self, frequencia):
        """
        Normaliza a frequência para um formato padrão
        
        Args:
            frequencia (str): Frequência original
        
        Returns:
            str: Frequência normalizada
        """
        if not frequencia:
            return 'semanal'
        
        freq_lower = frequencia.lower().strip()
        
        # Mapeamento de frequências
        mapeamento = {
            'diaria': 'diaria',
            'diário': 'diaria',
            'diario': 'diaria',
            'daily': 'diaria',
            
            'semanal': 'semanal',
            'semana': 'semanal',
            'weekly': 'semanal',
            
            'quinzenal': 'quinzenal',
            'quinzena': 'quinzenal',
            'biweekly': 'quinzenal',
            
            'mensal': 'mensal',
            'mês': 'mensal',
            'mes': 'mensal',
            'monthly': 'mensal',
            
            'bimestral': 'bimestral',
            'bimestre': 'bimestral',
            'bimonthly': 'bimestral',
            
            'trimestral': 'trimestral',
            'trimestre': 'trimestral',
            'quarterly': 'trimestral',
            
            'semestral': 'semestral',
            'semestre': 'semestral',
            'semiannual': 'semestral',
            
            'anual': 'anual',
            'ano': 'anual',
            'yearly': 'anual',
            'annual': 'anual'
        }
        
        # Buscar correspondência exata
        if freq_lower in mapeamento:
            return mapeamento[freq_lower]
        
        # Buscar por palavras-chave
        for palavra, freq_normalizada in mapeamento.items():
            if palavra in freq_lower:
                return freq_normalizada
        
        # Padrão se não encontrar
        self.log(f"⚠️ Frequência não reconhecida: '{frequencia}'. Usando padrão 'semanal'", 'warning')
        return 'semanal'
    
    def calcular_proxima_data(self, data_base, frequencia):
        """
        Calcula a próxima data baseada na frequência normalizada
        
        Args:
            data_base (date): Data base para cálculo
            frequencia (str): Frequência normalizada
        
        Returns:
            date: Próxima data calculada
        """
        try:
            freq_normalizada = self.normalizar_frequencia(frequencia)
            
            if freq_normalizada == 'diaria':
                return data_base + timedelta(days=1)
            elif freq_normalizada == 'semanal':
                return data_base + timedelta(weeks=1)
            elif freq_normalizada == 'quinzenal':
                return data_base + timedelta(weeks=2)
            elif freq_normalizada == 'mensal':
                return data_base + relativedelta(months=1)
            elif freq_normalizada == 'bimestral':
                return data_base + relativedelta(months=2)
            elif freq_normalizada == 'trimestral':
                return data_base + relativedelta(months=3)
            elif freq_normalizada == 'semestral':
                return data_base + relativedelta(months=6)
            elif freq_normalizada == 'anual':
                return data_base + relativedelta(years=1)
            else:
                # Fallback para semanal
                return data_base + timedelta(weeks=1)
                
        except Exception as e:
            self.log(f"❌ Erro ao calcular próxima data: {e}", 'error')
            return data_base + timedelta(weeks=1)  # Fallback seguro
    
    def gerar_cronograma_os(self, pmp, limite_futuro_dias=365):
        """
        Gera cronograma completo de OS para uma PMP
        
        Args:
            pmp (PMP): Objeto PMP
            limite_futuro_dias (int): Limite de dias no futuro para gerar OS
        
        Returns:
            list: Lista de datas que deveriam ter OS
        """
        if not pmp.data_inicio_plano:
            return []
        
        datas = []
        data_atual = pmp.data_inicio_plano
        data_limite = self.hoje + timedelta(days=limite_futuro_dias)
        
        # Se há data fim definida, usar a menor entre data_fim e limite_futuro
        if pmp.data_fim_plano:
            data_limite = min(data_limite, pmp.data_fim_plano)
        
        contador = 0
        max_iteracoes = 1000  # Proteção contra loop infinito
        
        while data_atual <= data_limite and contador < max_iteracoes:
            datas.append(data_atual)
            data_atual = self.calcular_proxima_data(data_atual, pmp.frequencia)
            contador += 1
        
        if contador >= max_iteracoes:
            self.log(f"⚠️ Limite de iterações atingido para PMP {pmp.codigo}", 'warning')
        
        return datas
    
    def verificar_os_existente(self, pmp_id, data_programada):
        """
        Verifica se já existe uma OS para a PMP na data específica
        
        Args:
            pmp_id (int): ID da PMP
            data_programada (date): Data programada da OS
        
        Returns:
            OrdemServico or None: OS existente ou None
        """
        try:
            return OrdemServico.query.filter_by(
                pmp_id=pmp_id,
                data_programada=data_programada
            ).first()
        except Exception as e:
            self.log(f"❌ Erro ao verificar OS existente: {e}", 'error')
            return None
    
    def obter_proximo_numero_sequencia(self, pmp_id):
        """
        Obtém o próximo número de sequência para uma PMP
        
        Args:
            pmp_id (int): ID da PMP
        
        Returns:
            int: Próximo número de sequência
        """
        try:
            ultima_os = OrdemServico.query.filter_by(pmp_id=pmp_id)\
                                         .order_by(OrdemServico.numero_sequencia.desc())\
                                         .first()
            
            if ultima_os and ultima_os.numero_sequencia:
                return ultima_os.numero_sequencia + 1
            else:
                # Contar total de OS para esta PMP como fallback
                count = OrdemServico.query.filter_by(pmp_id=pmp_id).count()
                return count + 1
                
        except Exception as e:
            self.log(f"❌ Erro ao obter número de sequência: {e}", 'error')
            return 1
    
    def criar_os_para_pmp(self, pmp, data_programada, numero_sequencia):
        """
        Cria uma nova OS para a PMP na data especificada
        
        Args:
            pmp (PMP): Objeto PMP
            data_programada (date): Data programada da OS
            numero_sequencia (int): Número da sequência da OS
        
        Returns:
            OrdemServico: OS criada
        """
        try:
            # Criar descrição da OS
            descricao = f"{pmp.descricao} - Sequência #{numero_sequencia:03d}"
            
            # Determinar próxima data de geração
            proxima_data = self.calcular_proxima_data(data_programada, pmp.frequencia)
            
            # Criar a OS
            nova_os = OrdemServico(
                descricao=descricao,
                equipamento_id=pmp.equipamento_id,
                tipo_manutencao=pmp.tipo or 'Preventiva',
                prioridade='preventiva',
                status='aberta',
                data_programada=data_programada,
                pmp_id=pmp.id,
                oficina=pmp.oficina or 'mecanica',
                criado_por=pmp.criado_por,
                empresa='Ativus',
                numero_sequencia=numero_sequencia,
                data_proxima_geracao=proxima_data,
                frequencia_origem=pmp.frequencia,
                qtd_pessoas=pmp.num_pessoas or 1,
                horas=pmp.tempo_pessoa or 1.0
            )
            
            # Calcular HH se método existir
            if hasattr(nova_os, 'calcular_hh'):
                nova_os.calcular_hh()
            
            db.session.add(nova_os)
            db.session.flush()  # Para obter o ID
            
            # Criar atividades da OS
            atividades_criadas = self.criar_atividades_os(nova_os, pmp)
            
            self.log(f"✅ OS criada: #{nova_os.id} - {descricao} para {data_programada} ({atividades_criadas} atividades)")
            return nova_os
            
        except Exception as e:
            self.log(f"❌ Erro ao criar OS: {e}", 'error')
            raise
    
    def criar_atividades_os(self, os, pmp):
        """
        Cria as atividades da OS baseadas nas atividades da PMP
        
        Args:
            os (OrdemServico): Ordem de serviço
            pmp (PMP): PMP de origem
        
        Returns:
            int: Número de atividades criadas
        """
        try:
            # Buscar atividades da PMP
            atividades_pmp = AtividadePMP.query.filter_by(
                pmp_id=pmp.id,
                status='ativo'
            ).order_by(AtividadePMP.ordem).all()
            
            atividades_criadas = 0
            
            for atividade_pmp in atividades_pmp:
                atividade_os = AtividadeOS(
                    os_id=os.id,
                    descricao=atividade_pmp.descricao,
                    ordem=atividade_pmp.ordem,
                    status='pendente'
                )
                db.session.add(atividade_os)
                atividades_criadas += 1
            
            return atividades_criadas
            
        except Exception as e:
            self.log(f"❌ Erro ao criar atividades da OS: {e}", 'error')
            return 0
    
    def processar_pmp(self, pmp):
        """
        Processa uma PMP específica, gerando as OS necessárias
        
        Args:
            pmp (PMP): PMP a ser processada
        
        Returns:
            dict: Resultado do processamento
        """
        self.log(f"🔍 Processando PMP: {pmp.codigo} - {pmp.descricao}")
        self.estatisticas['pmps_processadas'] += 1
        
        # Validar PMP
        valida, motivo = self.validar_pmp(pmp)
        if not valida:
            self.log(f"⏸️ PMP {pmp.codigo} ignorada: {motivo}")
            return {
                'pmp_codigo': pmp.codigo,
                'processada': False,
                'motivo': motivo,
                'os_geradas': 0
            }
        
        # Gerar cronograma de datas
        datas_necessarias = self.gerar_cronograma_os(pmp)
        self.log(f"📅 {len(datas_necessarias)} datas identificadas para PMP {pmp.codigo}")
        
        os_geradas_pmp = 0
        os_ja_existentes = 0
        
        for data_programada in datas_necessarias:
            # Só processar datas até hoje (não gerar OS futuras automaticamente)
            if data_programada > self.hoje:
                continue
                
            # Verificar se já existe OS para esta data
            os_existente = self.verificar_os_existente(pmp.id, data_programada)
            
            if os_existente:
                os_ja_existentes += 1
                continue
            
            # Obter próximo número de sequência
            numero_sequencia = self.obter_proximo_numero_sequencia(pmp.id)
            
            # Criar nova OS
            try:
                nova_os = self.criar_os_para_pmp(pmp, data_programada, numero_sequencia)
                self.os_geradas.append(nova_os)
                os_geradas_pmp += 1
                self.estatisticas['os_geradas'] += 1
                
            except Exception as e:
                self.log(f"❌ Erro ao criar OS para {data_programada}: {str(e)}", 'error')
                self.estatisticas['erros'] += 1
                db.session.rollback()
                continue
        
        self.estatisticas['os_ja_existentes'] += os_ja_existentes
        
        resultado = {
            'pmp_codigo': pmp.codigo,
            'processada': True,
            'os_geradas': os_geradas_pmp,
            'os_ja_existentes': os_ja_existentes,
            'total_datas': len(datas_necessarias)
        }
        
        self.log(f"✅ PMP {pmp.codigo}: {os_geradas_pmp} novas OS geradas, {os_ja_existentes} já existiam")
        return resultado
    
    def executar_geracao_completa(self, apenas_pmps_com_pendencias=False):
        """
        Executa a geração completa de OS para todas as PMPs ativas
        
        Args:
            apenas_pmps_com_pendencias (bool): Se True, processa apenas PMPs com OS pendentes
        
        Returns:
            dict: Resultado da operação
        """
        self.log("🚀 Iniciando geração automática de OS baseada em PMPs")
        
        try:
            # Buscar PMPs ativas com data de início
            query = PMP.query.filter(
                PMP.status == 'ativo',
                PMP.data_inicio_plano.isnot(None)
            )
            
            # Se solicitado, filtrar apenas PMPs com pendências
            if apenas_pmps_com_pendencias:
                # Aqui poderia adicionar lógica para identificar PMPs com pendências
                pass
            
            pmps_ativas = query.all()
            
            self.log(f"📊 {len(pmps_ativas)} PMPs ativas encontradas com data de início")
            
            resultados_pmps = []
            
            for pmp in pmps_ativas:
                resultado_pmp = self.processar_pmp(pmp)
                resultados_pmps.append(resultado_pmp)
            
            # Commit das alterações se houver OS geradas
            if self.estatisticas['os_geradas'] > 0:
                db.session.commit()
                self.log(f"💾 {self.estatisticas['os_geradas']} OS salvas no banco de dados")
            else:
                self.log("ℹ️ Nenhuma OS nova foi necessária")
            
            return {
                'success': True,
                'estatisticas': self.estatisticas,
                'resultados_pmps': resultados_pmps,
                'os_geradas': [os.to_dict() for os in self.os_geradas],
                'log_operacoes': self.log_operacoes,
                'data_processamento': self.hoje.isoformat()
            }
            
        except Exception as e:
            db.session.rollback()
            self.log(f"❌ Erro durante geração: {str(e)}", 'error')
            self.estatisticas['erros'] += 1
            return {
                'success': False,
                'error': str(e),
                'estatisticas': self.estatisticas,
                'log_operacoes': self.log_operacoes
            }
    
    def gerar_os_pmp_especifica(self, pmp_codigo):
        """
        Gera OS para uma PMP específica pelo código
        
        Args:
            pmp_codigo (str): Código da PMP
        
        Returns:
            dict: Resultado da operação
        """
        self.log(f"🎯 Gerando OS para PMP específica: {pmp_codigo}")
        
        try:
            pmp = PMP.query.filter_by(codigo=pmp_codigo).first()
            
            if not pmp:
                return {
                    'success': False,
                    'error': f'PMP {pmp_codigo} não encontrada'
                }
            
            resultado_pmp = self.processar_pmp(pmp)
            
            if resultado_pmp['os_geradas'] > 0:
                db.session.commit()
                self.log(f"💾 {resultado_pmp['os_geradas']} OS salvas para PMP {pmp_codigo}")
            
            return {
                'success': True,
                'resultado_pmp': resultado_pmp,
                'estatisticas': self.estatisticas,
                'log_operacoes': self.log_operacoes
            }
            
        except Exception as e:
            db.session.rollback()
            self.log(f"❌ Erro ao gerar OS para PMP {pmp_codigo}: {str(e)}", 'error')
            return {
                'success': False,
                'error': str(e),
                'log_operacoes': self.log_operacoes
            }
    
    def verificar_pendencias_pmp(self):
        """
        Verifica quais PMPs têm OS pendentes de geração
        
        Returns:
            dict: Relatório de pendências
        """
        self.log("🔍 Verificando pendências de OS para PMPs")
        
        try:
            pmps_ativas = PMP.query.filter(
                PMP.status == 'ativo',
                PMP.data_inicio_plano.isnot(None)
            ).all()
            
            pendencias = []
            
            for pmp in pmps_ativas:
                # Validar PMP
                valida, motivo = self.validar_pmp(pmp)
                if not valida:
                    continue
                
                # Gerar cronograma até hoje
                datas_necessarias = [d for d in self.gerar_cronograma_os(pmp) if d <= self.hoje]
                
                # Contar OS existentes
                os_existentes = OrdemServico.query.filter_by(pmp_id=pmp.id).count()
                
                os_pendentes = len(datas_necessarias) - os_existentes
                
                if os_pendentes > 0:
                    pendencias.append({
                        'pmp_codigo': pmp.codigo,
                        'pmp_descricao': pmp.descricao,
                        'os_pendentes': os_pendentes,
                        'os_existentes': os_existentes,
                        'total_necessarias': len(datas_necessarias),
                        'data_inicio': pmp.data_inicio_plano.isoformat(),
                        'frequencia': pmp.frequencia,
                        'proxima_data': datas_necessarias[-1].isoformat() if datas_necessarias else None
                    })
            
            return {
                'success': True,
                'pendencias': pendencias,
                'total_pmps_verificadas': len(pmps_ativas),
                'total_pmps_com_pendencias': len(pendencias)
            }
            
        except Exception as e:
            self.log(f"❌ Erro ao verificar pendências: {str(e)}", 'error')
            return {
                'success': False,
                'error': str(e)
            }

# Funções de conveniência para uso direto
def gerar_todas_os_pmp():
    """Gera todas as OS necessárias para todas as PMPs ativas"""
    gerador = GeradorOSPMPAprimorado()
    return gerador.executar_geracao_completa()

def gerar_os_pmp_codigo(codigo):
    """Gera OS para uma PMP específica pelo código"""
    gerador = GeradorOSPMPAprimorado()
    return gerador.gerar_os_pmp_especifica(codigo)

def verificar_pendencias_os_pmp():
    """Verifica pendências de OS para PMPs"""
    gerador = GeradorOSPMPAprimorado()
    return gerador.verificar_pendencias_pmp()

if __name__ == "__main__":
    # Teste direto
    print("="*60)
    print("SISTEMA DE GERAÇÃO AUTOMÁTICA DE OS - TESTE")
    print("="*60)
    
    # Verificar pendências primeiro
    print("\n1. Verificando pendências...")
    pendencias = verificar_pendencias_os_pmp()
    print(f"Pendências encontradas: {pendencias.get('total_pmps_com_pendencias', 0)}")
    
    # Executar geração
    print("\n2. Executando geração...")
    resultado = gerar_todas_os_pmp()
    
    print("\n" + "="*60)
    print("RESULTADO FINAL:")
    print(f"Sucesso: {resultado['success']}")
    if resultado['success']:
        stats = resultado['estatisticas']
        print(f"PMPs processadas: {stats['pmps_processadas']}")
        print(f"OS geradas: {stats['os_geradas']}")
        print(f"OS já existentes: {stats['os_ja_existentes']}")
        print(f"Erros: {stats['erros']}")
    else:
        print(f"Erro: {resultado['error']}")
    print("="*60)
