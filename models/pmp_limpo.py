from datetime import datetime
from models import db
import json

class PMP(db.Model):
    """Modelo para Procedimento de Manutenção Preventiva - Estrutura Real do Banco"""
    __tablename__ = 'pmps'
    
    # Campos conforme estrutura real do banco
    id = db.Column(db.Integer, primary_key=True)
    codigo = db.Column(db.String(50), nullable=False, unique=True)
    descricao = db.Column(db.Text, nullable=False)
    equipamento_id = db.Column(db.Integer, nullable=False)
    tipo = db.Column(db.String(100))
    oficina = db.Column(db.String(100))
    frequencia = db.Column(db.String(100))
    condicao = db.Column(db.String(50))
    num_pessoas = db.Column(db.Integer, default=1)
    dias_antecipacao = db.Column(db.Integer, default=0)
    tempo_pessoa = db.Column(db.Float, default=0.5)
    forma_impressao = db.Column(db.String(50), default='comum')
    dias_semana = db.Column(db.Text)  # JSON array
    status = db.Column(db.String(20), default='ativo')
    criado_por = db.Column(db.Integer, nullable=False)
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
            'atualizado_em': self.atualizado_em.isoformat() if self.atualizado_em else None
        }

class AtividadePMP(db.Model):
    """Modelo para Atividades de PMP - Estrutura Real do Banco"""
    __tablename__ = 'atividades_pmp'
    
    # Campos conforme estrutura real do banco
    id = db.Column(db.Integer, primary_key=True)
    pmp_id = db.Column(db.Integer, db.ForeignKey('pmps.id'), nullable=False)
    atividade_plano_mestre_id = db.Column(db.Integer, db.ForeignKey('atividades_plano_mestre.id'), nullable=False)
    ordem = db.Column(db.Integer, default=1)
    status = db.Column(db.String(20), default='ativo')
    criado_em = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Campos duplicados da atividade do plano mestre (para performance)
    descricao = db.Column(db.Text)
    oficina = db.Column(db.String(100))
    frequencia = db.Column(db.String(100))
    tipo_manutencao = db.Column(db.String(100))
    conjunto = db.Column(db.String(100))
    ponto_controle = db.Column(db.String(100))
    valor_frequencia = db.Column(db.Integer)
    condicao = db.Column(db.String(50))
    
    # Relacionamentos
    pmp = db.relationship('PMP', backref='atividades')
    
    def to_dict(self):
        return {
            'id': self.id,
            'pmp_id': self.pmp_id,
            'atividade_plano_mestre_id': self.atividade_plano_mestre_id,
            'ordem': self.ordem,
            'status': self.status,
            'criado_em': self.criado_em.isoformat() if self.criado_em else None,
            'descricao': self.descricao,
            'oficina': self.oficina,
            'frequencia': self.frequencia,
            'tipo_manutencao': self.tipo_manutencao,
            'conjunto': self.conjunto,
            'ponto_controle': self.ponto_controle,
            'valor_frequencia': self.valor_frequencia,
            'condicao': self.condicao
        }

class HistoricoExecucaoPMP(db.Model):
    """Modelo para Histórico de Execução de PMP - Estrutura Real do Banco"""
    __tablename__ = 'historico_execucao_pmp'
    
    # Campos conforme estrutura real do banco
    id = db.Column(db.Integer, primary_key=True)
    pmp_id = db.Column(db.Integer, db.ForeignKey('pmps.id'), nullable=False)
    data_programada = db.Column(db.DateTime)
    data_inicio = db.Column(db.DateTime)
    data_conclusao = db.Column(db.DateTime)
    status = db.Column(db.String(20), default='programada')  # programada, em_andamento, concluida, cancelada
    observacoes = db.Column(db.Text)
    executado_por = db.Column(db.Integer)
    criado_por = db.Column(db.Integer, nullable=False)
    criado_em = db.Column(db.DateTime, default=datetime.utcnow)
    atualizado_em = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relacionamento
    pmp = db.relationship('PMP', backref='historico_execucoes')
    
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

