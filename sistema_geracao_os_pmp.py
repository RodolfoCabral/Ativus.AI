#!/usr/bin/env python3
"""
Sistema Completo de Geração Automática de OS baseado em PMPs
Gera OS automaticamente baseado na data de início e frequência das PMPs
"""

from datetime import datetime, timedelta, date
from dateutil.relativedelta import relativedelta
import json
from models import db
from models.pmp_limpo import PMP
from assets_models import OrdemServico, AtividadeOS

class GeradorOSPMP:
    """Classe responsável pela geração automática de OS baseada em PMPs"""
    
    def __init__(self):
        self.hoje = date.today()
        self.os_geradas = []
        self.log_operacoes = []
    
    def log(self, mensagem):
        """Adiciona mensagem ao log de operações"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_entry = f"[{timestamp}] {mensagem}"
        self.log_operacoes.append(log_entry)
        print(log_entry)
    
    def calcular_proxima_data(self, data_base, frequencia):
        """
        Calcula a próxima data baseada na frequência
        
        Args:
            data_base (date): Data base para cálculo
            frequencia (str): Frequência da PMP (semanal, mensal, etc.)
        
        Returns:
            date: Próxima data calculada
        """
        frequencia_lower = frequencia.lower()
        
        if 'semanal' in frequencia_lower or 'semana' in frequencia_lower:
            return data_base + timedelta(weeks=1)
        elif 'mensal' in frequencia_lower or 'mês' in frequencia_lower or 'mes' in frequencia_lower:
            return data_base + relativedelta(months=1)
        elif 'bimestral' in frequencia_lower:
            return data_base + relativedelta(months=2)
        elif 'trimestral' in frequencia_lower:
            return data_base + relativedelta(months=3)
        elif 'semestral' in frequencia_lower:
            return data_base + relativedelta(months=6)
        elif 'anual' in frequencia_lower or 'ano' in frequencia_lower:
            return data_base + relativedelta(years=1)
        elif 'diaria' in frequencia_lower or 'diário' in frequencia_lower:
            return data_base + timedelta(days=1)
        elif 'quinzenal' in frequencia_lower:
            return data_base + timedelta(weeks=2)
        else:
            # Padrão: semanal
            self.log(f"⚠️ Frequência não reconhecida: {frequencia}. Usando padrão semanal.")
            return data_base + timedelta(weeks=1)
    
    def gerar_datas_os(self, pmp):
        """
        Gera todas as datas de OS que deveriam existir para uma PMP
        
        Args:
            pmp (PMP): Objeto PMP
        
        Returns:
            list: Lista de datas que deveriam ter OS
        """
        if not pmp.data_inicio_plano:
            return []
        
        datas = []
        data_atual = pmp.data_inicio_plano
        
        # Verificar se deve parar pela data fim
        data_limite = self.hoje
        if pmp.data_fim_plano and pmp.data_fim_plano <= self.hoje:
            self.log(f"📅 PMP {pmp.codigo}: Data fim ({pmp.data_fim_plano}) já passou. Não gerando novas OS.")
            data_limite = pmp.data_fim_plano
        
        # Gerar datas até hoje (ou data fim se aplicável)
        while data_atual <= data_limite:
            datas.append(data_atual)
            data_atual = self.calcular_proxima_data(data_atual, pmp.frequencia)
        
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
        return OrdemServico.query.filter_by(
            pmp_id=pmp_id,
            data_programada=data_programada
        ).first()
    
    def criar_os_para_pmp(self, pmp, data_programada, sequencia):
        """
        Cria uma nova OS para a PMP na data especificada
        
        Args:
            pmp (PMP): Objeto PMP
            data_programada (date): Data programada da OS
            sequencia (int): Número da sequência da OS
        
        Returns:
            OrdemServico: OS criada
        """
        # Criar descrição da OS
        descricao = f"{pmp.descricao} - Sequência #{sequencia}"
        
        # Criar a OS
        nova_os = OrdemServico(
            descricao=descricao,
            equipamento_id=pmp.equipamento_id,
            tipo_manutencao=pmp.tipo or 'Preventiva',
            prioridade='preventiva',
            status='aberta',
            data_programada=data_programada,
            pmp_id=pmp.id,
            oficina=pmp.oficina,
            criado_por=pmp.criado_por,
            empresa='Ativus'  # Ajustar conforme necessário
        )
        
        db.session.add(nova_os)
        db.session.flush()  # Para obter o ID
        
        # Criar atividades da OS baseadas nas atividades da PMP
        self.criar_atividades_os(nova_os, pmp)
        
        self.log(f"✅ OS criada: {nova_os.id} - {descricao} para {data_programada}")
        return nova_os
    
    def criar_atividades_os(self, os, pmp):
        """
        Cria as atividades da OS baseadas nas atividades da PMP
        
        Args:
            os (OrdemServico): Ordem de serviço
            pmp (PMP): PMP de origem
        """
        # Buscar atividades da PMP
        from models.pmp_limpo import AtividadePMP
        atividades_pmp = AtividadePMP.query.filter_by(
            pmp_id=pmp.id,
            status='ativo'
        ).order_by(AtividadePMP.ordem).all()
        
        for atividade_pmp in atividades_pmp:
            atividade_os = AtividadeOS(
                os_id=os.id,
                descricao=atividade_pmp.descricao,
                ordem=atividade_pmp.ordem,
                status='pendente'
            )
            db.session.add(atividade_os)
        
        self.log(f"📋 {len(atividades_pmp)} atividades criadas para OS {os.id}")
    
    def processar_pmp(self, pmp):
        """
        Processa uma PMP específica, gerando as OS necessárias
        
        Args:
            pmp (PMP): PMP a ser processada
        
        Returns:
            int: Número de OS geradas
        """
        self.log(f"🔍 Processando PMP: {pmp.codigo} - {pmp.descricao}")
        
        # Verificar se PMP está ativa
        if pmp.status != 'ativo':
            self.log(f"⏸️ PMP {pmp.codigo} não está ativa. Status: {pmp.status}")
            return 0
        
        # Verificar se tem data de início
        if not pmp.data_inicio_plano:
            self.log(f"⚠️ PMP {pmp.codigo} não tem data de início definida.")
            return 0
        
        # Gerar datas que deveriam ter OS
        datas_necessarias = self.gerar_datas_os(pmp)
        self.log(f"📅 {len(datas_necessarias)} datas identificadas para PMP {pmp.codigo}")
        
        os_geradas_pmp = 0
        
        for i, data_programada in enumerate(datas_necessarias, 1):
            # Verificar se já existe OS para esta data
            os_existente = self.verificar_os_existente(pmp.id, data_programada)
            
            if os_existente:
                self.log(f"📋 OS já existe para {data_programada}: OS #{os_existente.id}")
                continue
            
            # Criar nova OS
            try:
                nova_os = self.criar_os_para_pmp(pmp, data_programada, i)
                self.os_geradas.append(nova_os)
                os_geradas_pmp += 1
                
            except Exception as e:
                self.log(f"❌ Erro ao criar OS para {data_programada}: {str(e)}")
                db.session.rollback()
                continue
        
        self.log(f"✅ PMP {pmp.codigo}: {os_geradas_pmp} novas OS geradas")
        return os_geradas_pmp
    
    def executar_geracao_completa(self):
        """
        Executa a geração completa de OS para todas as PMPs ativas
        
        Returns:
            dict: Resultado da operação
        """
        self.log("🚀 Iniciando geração automática de OS baseada em PMPs")
        
        try:
            # Buscar todas as PMPs ativas com data de início
            pmps_ativas = PMP.query.filter(
                PMP.status == 'ativo',
                PMP.data_inicio_plano.isnot(None)
            ).all()
            
            self.log(f"📊 {len(pmps_ativas)} PMPs ativas encontradas com data de início")
            
            total_os_geradas = 0
            
            for pmp in pmps_ativas:
                os_geradas_pmp = self.processar_pmp(pmp)
                total_os_geradas += os_geradas_pmp
            
            # Commit das alterações
            if total_os_geradas > 0:
                db.session.commit()
                self.log(f"💾 {total_os_geradas} OS salvas no banco de dados")
            else:
                self.log("ℹ️ Nenhuma OS nova foi necessária")
            
            return {
                'success': True,
                'total_os_geradas': total_os_geradas,
                'pmps_processadas': len(pmps_ativas),
                'os_geradas': [os.to_dict() for os in self.os_geradas],
                'log_operacoes': self.log_operacoes
            }
            
        except Exception as e:
            db.session.rollback()
            self.log(f"❌ Erro durante geração: {str(e)}")
            return {
                'success': False,
                'error': str(e),
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
            
            os_geradas = self.processar_pmp(pmp)
            
            if os_geradas > 0:
                db.session.commit()
                self.log(f"💾 {os_geradas} OS salvas para PMP {pmp_codigo}")
            
            return {
                'success': True,
                'os_geradas': os_geradas,
                'pmp_processada': pmp.to_dict(),
                'log_operacoes': self.log_operacoes
            }
            
        except Exception as e:
            db.session.rollback()
            self.log(f"❌ Erro ao gerar OS para PMP {pmp_codigo}: {str(e)}")
            return {
                'success': False,
                'error': str(e),
                'log_operacoes': self.log_operacoes
            }

# Função de conveniência para uso direto
def gerar_todas_os_pmp():
    """Gera todas as OS necessárias para todas as PMPs ativas"""
    gerador = GeradorOSPMP()
    return gerador.executar_geracao_completa()

def gerar_os_pmp_codigo(codigo):
    """Gera OS para uma PMP específica pelo código"""
    gerador = GeradorOSPMP()
    return gerador.gerar_os_pmp_especifica(codigo)

if __name__ == "__main__":
    # Teste direto
    resultado = gerar_todas_os_pmp()
    print("\n" + "="*50)
    print("RESULTADO FINAL:")
    print(f"Sucesso: {resultado['success']}")
    if resultado['success']:
        print(f"OS geradas: {resultado['total_os_geradas']}")
        print(f"PMPs processadas: {resultado['pmps_processadas']}")
    else:
        print(f"Erro: {resultado['error']}")
