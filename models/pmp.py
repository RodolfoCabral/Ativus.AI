from models import db
from datetime import datetime
import json

class PMP(db.Model):
    """Modelo para Procedimento de Manutenção Preventiva"""
    __tablename__ = 'pmps'
    
    id = db.Column(db.Integer, primary_key=True)
    codigo = db.Column(db.String(50), nullable=False, unique=True)
    descricao = db.Column(db.Text, nullable=False)
    equipamento_id = db.Column(db.Integer, nullable=False)  # Removido FK temporariamente
    
    # Dados de agrupamento
    tipo = db.Column(db.String(100))
    oficina = db.Column(db.String(100))
    frequencia = db.Column(db.String(100))
    condicao = db.Column(db.String(50))
    
    # Configurações da PMP
    num_pessoas = db.Column(db.Integer, default=1)
    dias_antecipacao = db.Column(db.Integer, default=0)
    tempo_pessoa = db.Column(db.Float, default=0.5)
    forma_impressao = db.Column(db.String(50), default='comum')
    dias_semana = db.Column(db.Text)  # JSON array
    
    # Metadados
    status = db.Column(db.String(20), default='ativo')
    criado_por = db.Column(db.Integer, nullable=False)  # Removido FK temporariamente
    criado_em = db.Column(db.DateTime, default=datetime.utcnow)
    atualizado_em = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'codigo': self.codigo,
            'descricao': self.descricao,
            'equipamento_id': self.equipamento_id,
            'tipo': self.tipo,
            'oficina': self.oficina,
            'frequencia': self.frequencia,
            'condicao': self.condicao,
            'num_pessoas': self.num_pessoas,
            'dias_antecipacao': self.dias_antecipacao,
            'tempo_pessoa': self.tempo_pessoa,
            'forma_impressao': self.forma_impressao,
            'dias_semana': json.loads(self.dias_semana) if self.dias_semana else [],
            'status': self.status,
            'criado_por': self.criado_por,
            'criado_em': self.criado_em.isoformat() if self.criado_em else None,
            'atualizado_em': self.atualizado_em.isoformat() if self.atualizado_em else None,
            'atividades': [atividade.to_dict() for atividade in self.atividades] if hasattr(self, 'atividades') else []
        }
    
    def set_dias_semana(self, dias_lista):
        """Definir dias da semana como JSON"""
        self.dias_semana = json.dumps(dias_lista) if dias_lista else None
    
    def get_dias_semana(self):
        """Obter dias da semana como lista"""
        return json.loads(self.dias_semana) if self.dias_semana else []


class AtividadePMP(db.Model):
    """Modelo para atividades específicas de uma PMP"""
    __tablename__ = 'atividades_pmp'
    
    id = db.Column(db.Integer, primary_key=True)
    pmp_id = db.Column(db.Integer, nullable=False)  # Removido FK temporariamente
    
    # Dados da atividade (copiados do plano mestre)
    descricao = db.Column(db.Text, nullable=False)
    oficina = db.Column(db.String(100))
    frequencia = db.Column(db.String(100))
    tipo_manutencao = db.Column(db.String(100))
    conjunto = db.Column(db.String(100))
    ponto_controle = db.Column(db.String(100))
    valor_frequencia = db.Column(db.Integer)
    condicao = db.Column(db.String(50))
    
    # Ordem da atividade na PMP
    ordem = db.Column(db.Integer, default=1)
    
    # Status específico da atividade na PMP
    status = db.Column(db.String(20), default='ativo')
    
    # Metadados
    criado_em = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'pmp_id': self.pmp_id,
            'descricao': self.descricao,
            'oficina': self.oficina,
            'frequencia': self.frequencia,
            'tipo_manutencao': self.tipo_manutencao,
            'conjunto': self.conjunto,
            'ponto_controle': self.ponto_controle,
            'valor_frequencia': self.valor_frequencia,
            'condicao': self.condicao,
            'ordem': self.ordem,
            'status': self.status,
            'criado_em': self.criado_em.isoformat() if self.criado_em else None
        }


class HistoricoExecucaoPMP(db.Model):
    """Modelo para histórico de execução de PMPs"""
    __tablename__ = 'historico_execucao_pmp'
    
    id = db.Column(db.Integer, primary_key=True)
    pmp_id = db.Column(db.Integer, nullable=False)  # Removido FK temporariamente
    
    # Dados da execução
    data_programada = db.Column(db.DateTime, nullable=False)
    data_inicio = db.Column(db.DateTime)
    data_conclusao = db.Column(db.DateTime)
    
    # Status da execução
    status = db.Column(db.String(20), default='programada')  # programada, em_andamento, concluida, cancelada
    
    # Observações
    observacoes = db.Column(db.Text)
    
    # Responsáveis
    executado_por = db.Column(db.Integer)  # Removido FK temporariamente
    criado_por = db.Column(db.Integer, nullable=False)  # Removido FK temporariamente
    
    # Metadados
    criado_em = db.Column(db.DateTime, default=datetime.utcnow)
    atualizado_em = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'pmp_id': self.pmp_id,
            'data_programada': self.data_programada.isoformat() if self.data_programada else None,
            'data_inicio': self.data_inicio.isoformat() if self.data_inicio else None,
            'data_conclusao': self.data_conclusao.isoformat() if self.data_conclusao else None,
            'status': self.status,
            'observacoes': self.observacoes,
            'executado_por': self.executado_por,
            'criado_por': self.criado_por,
            'criado_em': self.criado_em.isoformat() if self.criado_em else None,
            'atualizado_em': self.atualizado_em.isoformat() if self.atualizado_em else None
        }

