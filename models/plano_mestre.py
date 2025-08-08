# Modelos para Plano Mestre
from datetime import datetime
from models import db

class PlanoMestre(db.Model):
    """
    Modelo para armazenar planos mestre de equipamentos.
    Cada equipamento pode ter um plano mestre único.
    """
    __tablename__ = 'planos_mestre'
    
    id = db.Column(db.Integer, primary_key=True)
    equipamento_id = db.Column(db.Integer, nullable=False, unique=True, index=True)
    nome = db.Column(db.String(200), nullable=False)
    descricao = db.Column(db.Text)
    status = db.Column(db.String(20), default='ativo')  # ativo, inativo
    criado_por = db.Column(db.Integer, nullable=False)  # ID do usuário
    criado_em = db.Column(db.DateTime, default=datetime.utcnow)
    atualizado_em = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relacionamento com atividades
    atividades = db.relationship('AtividadePlanoMestre', backref='plano_mestre', lazy=True, cascade='all, delete-orphan')
    
    def to_dict(self):
        return {
            'id': self.id,
            'equipamento_id': self.equipamento_id,
            'nome': self.nome,
            'descricao': self.descricao,
            'status': self.status,
            'criado_por': self.criado_por,
            'criado_em': self.criado_em.isoformat() if self.criado_em else None,
            'atualizado_em': self.atualizado_em.isoformat() if self.atualizado_em else None,
            'total_atividades': len(self.atividades)
        }

class AtividadePlanoMestre(db.Model):
    """
    Modelo para armazenar atividades específicas de cada plano mestre.
    Cada atividade pertence a um plano mestre específico.
    """
    __tablename__ = 'atividades_plano_mestre'
    
    id = db.Column(db.Integer, primary_key=True)
    plano_mestre_id = db.Column(db.Integer, db.ForeignKey('planos_mestre.id'), nullable=False, index=True)
    
    # Dados da atividade
    descricao = db.Column(db.Text, nullable=False)
    oficina = db.Column(db.String(50))  # eletrica, mecanica, instrumentacao, civil
    tipo_manutencao = db.Column(db.String(50))  # preventiva-periodica, preventiva-preditiva, corretiva
    frequencia = db.Column(db.String(50))  # diario, semanal, mensal, etc.
    conjunto = db.Column(db.String(100))
    ponto_controle = db.Column(db.String(50))  # visual, auditivo, medicao, teste
    valor_frequencia = db.Column(db.Integer)
    condicao = db.Column(db.String(50))  # funcionando, parado
    status_ativo = db.Column(db.Boolean, default=True)
    
    # Controle de execução
    concluida = db.Column(db.Boolean, default=False)
    data_conclusao = db.Column(db.DateTime)
    observacoes = db.Column(db.Text)
    
    # Auditoria
    criado_por = db.Column(db.Integer, nullable=False)
    criado_em = db.Column(db.DateTime, default=datetime.utcnow)
    atualizado_em = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Ordem de exibição
    ordem = db.Column(db.Integer, default=0)
    
    def to_dict(self):
        return {
            'id': self.id,
            'plano_mestre_id': self.plano_mestre_id,
            'descricao': self.descricao,
            'oficina': self.oficina,
            'tipo_manutencao': self.tipo_manutencao,
            'frequencia': self.frequencia,
            'conjunto': self.conjunto,
            'ponto_controle': self.ponto_controle,
            'valor_frequencia': self.valor_frequencia,
            'condicao': self.condicao,
            'status_ativo': self.status_ativo,
            'concluida': self.concluida,
            'data_conclusao': self.data_conclusao.isoformat() if self.data_conclusao else None,
            'observacoes': self.observacoes,
            'criado_por': self.criado_por,
            'criado_em': self.criado_em.isoformat() if self.criado_em else None,
            'atualizado_em': self.atualizado_em.isoformat() if self.atualizado_em else None,
            'ordem': self.ordem
        }
    
    def marcar_concluida(self, observacoes=None):
        """Marca a atividade como concluída"""
        self.concluida = True
        self.data_conclusao = datetime.utcnow()
        if observacoes:
            self.observacoes = observacoes
        self.atualizado_em = datetime.utcnow()
    
    def desmarcar_concluida(self):
        """Desmarca a atividade como concluída"""
        self.concluida = False
        self.data_conclusao = None
        self.atualizado_em = datetime.utcnow()

class HistoricoExecucaoPlano(db.Model):
    """
    Modelo para armazenar histórico de execuções do plano mestre.
    Registra quando e por quem cada atividade foi executada.
    """
    __tablename__ = 'historico_execucao_plano'
    
    id = db.Column(db.Integer, primary_key=True)
    plano_mestre_id = db.Column(db.Integer, db.ForeignKey('planos_mestre.id'), nullable=False, index=True)
    atividade_id = db.Column(db.Integer, db.ForeignKey('atividades_plano_mestre.id'), nullable=False, index=True)
    
    # Dados da execução
    executado_por = db.Column(db.Integer, nullable=False)  # ID do usuário
    data_execucao = db.Column(db.DateTime, default=datetime.utcnow)
    status_execucao = db.Column(db.String(20), default='concluida')  # concluida, pendente, cancelada
    observacoes = db.Column(db.Text)
    tempo_execucao = db.Column(db.Integer)  # em minutos
    
    # Dados técnicos coletados
    dados_coletados = db.Column(db.JSON)  # Para armazenar medições, fotos, etc.
    
    def to_dict(self):
        return {
            'id': self.id,
            'plano_mestre_id': self.plano_mestre_id,
            'atividade_id': self.atividade_id,
            'executado_por': self.executado_por,
            'data_execucao': self.data_execucao.isoformat() if self.data_execucao else None,
            'status_execucao': self.status_execucao,
            'observacoes': self.observacoes,
            'tempo_execucao': self.tempo_execucao,
            'dados_coletados': self.dados_coletados
        }

