from models import db
from datetime import datetime

class AtividadeOS(db.Model):
    __tablename__ = 'atividades_os'

    id = db.Column(db.Integer, primary_key=True)
    os_id = db.Column(db.Integer, db.ForeignKey('ordens_servico.id'), nullable=False)
    atividade_pmp_id = db.Column(db.Integer, db.ForeignKey('atividades_pmp.id'), nullable=True)
    
    # Campos da atividade
    descricao = db.Column(db.Text, nullable=False)
    instrucao = db.Column(db.Text, nullable=True)
    ordem = db.Column(db.Integer, default=1)
    
    # Campos de avaliação
    status = db.Column(db.String(20), default='pendente', nullable=False)  # pendente, conforme, nao_conforme, nao_aplicavel
    observacao = db.Column(db.Text, nullable=True)
    
    # Campos de controle
    data_criacao = db.Column(db.DateTime, default=datetime.utcnow)
    data_atualizacao = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'os_id': self.os_id,
            'atividade_pmp_id': self.atividade_pmp_id,
            'descricao': self.descricao,
            'instrucao': self.instrucao,
            'ordem': self.ordem,
            'status': self.status,
            'observacao': self.observacao,
            'data_criacao': self.data_criacao.isoformat() if self.data_criacao else None,
            'data_atualizacao': self.data_atualizacao.isoformat() if self.data_atualizacao else None
        }
