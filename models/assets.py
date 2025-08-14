from datetime import datetime
from app import db

class Filial(db.Model):
    __tablename__ = 'filiais'
    
    id = db.Column(db.Integer, primary_key=True)
    tag = db.Column(db.String(50), nullable=False)
    descricao = db.Column(db.String(200), nullable=False)
    endereco = db.Column(db.String(200), nullable=False)
    cidade = db.Column(db.String(100), nullable=False)
    estado = db.Column(db.String(2), nullable=False)
    email = db.Column(db.String(100), nullable=False)
    telefone = db.Column(db.String(20), nullable=False)
    cnpj = db.Column(db.String(18), nullable=False)
    empresa = db.Column(db.String(100), nullable=False)
    data_criacao = db.Column(db.DateTime, default=datetime.utcnow)
    usuario_criacao = db.Column(db.String(100), nullable=False)
    
    # Relacionamento com setores
    setores = db.relationship('Setor', backref='filial_ref', lazy=True, cascade='all, delete-orphan')
    
    def to_dict(self):
        return {
            'id': self.id,
            'tag': self.tag,
            'descricao': self.descricao,
            'endereco': self.endereco,
            'cidade': self.cidade,
            'estado': self.estado,
            'email': self.email,
            'telefone': self.telefone,
            'cnpj': self.cnpj,
            'empresa': self.empresa,
            'data_criacao': self.data_criacao.isoformat() if self.data_criacao else None,
            'usuario_criacao': self.usuario_criacao
        }

class Setor(db.Model):
    __tablename__ = 'setores'
    
    id = db.Column(db.Integer, primary_key=True)
    tag = db.Column(db.String(50), nullable=False)
    descricao = db.Column(db.String(200), nullable=False)
    filial_id = db.Column(db.Integer, db.ForeignKey('filiais.id'), nullable=False)
    empresa = db.Column(db.String(100), nullable=False)
    data_criacao = db.Column(db.DateTime, default=datetime.utcnow)
    usuario_criacao = db.Column(db.String(100), nullable=False)
    
    # Relacionamento com equipamentos
    equipamentos = db.relationship('Equipamento', backref='setor_ref', lazy=True, cascade='all, delete-orphan')
    
    def to_dict(self):
        return {
            'id': self.id,
            'tag': self.tag,
            'descricao': self.descricao,
            'filial_id': self.filial_id,
            'filial_tag': self.filial_ref.tag if self.filial_ref else None,
            'filial_descricao': self.filial_ref.descricao if self.filial_ref else None,
            'empresa': self.empresa,
            'data_criacao': self.data_criacao.isoformat() if self.data_criacao else None,
            'usuario_criacao': self.usuario_criacao
        }

class Equipamento(db.Model):
    __tablename__ = 'equipamentos'
    
    id = db.Column(db.Integer, primary_key=True)
    tag = db.Column(db.String(50), nullable=False)
    descricao = db.Column(db.String(200), nullable=False)
    setor_id = db.Column(db.Integer, db.ForeignKey('setores.id'), nullable=False)
    foto = db.Column(db.String(255), nullable=True)  # Caminho para a foto do equipamento
    empresa = db.Column(db.String(100), nullable=False)
    data_criacao = db.Column(db.DateTime, default=datetime.utcnow)
    usuario_criacao = db.Column(db.String(100), nullable=False)
    
    def to_dict(self):
        return {
            'id': self.id,
            'tag': self.tag,
            'descricao': self.descricao,
            'setor_id': self.setor_id,
            'setor_tag': self.setor_ref.tag if self.setor_ref else None,
            'setor_descricao': self.setor_ref.descricao if self.setor_ref else None,
            'filial_id': self.setor_ref.filial_id if self.setor_ref else None,
            'filial_tag': self.setor_ref.filial_ref.tag if self.setor_ref and self.setor_ref.filial_ref else None,
            'filial_descricao': self.setor_ref.filial_ref.descricao if self.setor_ref and self.setor_ref.filial_ref else None,
            'foto': self.foto,
            'empresa': self.empresa,
            'data_criacao': self.data_criacao.isoformat() if self.data_criacao else None,
            'usuario_criacao': self.usuario_criacao
        }

class Categoria(db.Model):
    __tablename__ = 'categorias'
    
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    descricao = db.Column(db.String(200))
    empresa = db.Column(db.String(100), nullable=False)
    data_criacao = db.Column(db.DateTime, default=datetime.utcnow)
    usuario_criacao = db.Column(db.String(100), nullable=False)
    
    def to_dict(self):
        return {
            'id': self.id,
            'nome': self.nome,
            'descricao': self.descricao,
            'empresa': self.empresa,
            'data_criacao': self.data_criacao.isoformat() if self.data_criacao else None,
            'usuario_criacao': self.usuario_criacao
        }


class Chamado(db.Model):
    __tablename__ = 'chamados'
    
    id = db.Column(db.Integer, primary_key=True)
    descricao = db.Column(db.Text, nullable=False)
    filial_id = db.Column(db.Integer, db.ForeignKey('filiais.id'), nullable=False)
    setor_id = db.Column(db.Integer, db.ForeignKey('setores.id'), nullable=False)
    equipamento_id = db.Column(db.Integer, db.ForeignKey('equipamentos.id'), nullable=False)
    prioridade = db.Column(db.String(20), nullable=False)  # baixa, media, alta, seguranca
    status = db.Column(db.String(20), nullable=False, default='aberto')  # aberto, em_andamento, resolvido, fechado
    solicitante = db.Column(db.String(100), nullable=False)
    empresa = db.Column(db.String(100), nullable=False)
    data_criacao = db.Column(db.DateTime, default=datetime.utcnow)
    data_atualizacao = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    usuario_criacao = db.Column(db.String(100), nullable=False)
    
    # Relacionamentos
    filial_chamado = db.relationship('Filial', backref='chamados', lazy=True)
    setor_chamado = db.relationship('Setor', backref='chamados', lazy=True)
    equipamento_chamado = db.relationship('Equipamento', backref='chamados', lazy=True)
    
    def to_dict(self):
        return {
            'id': self.id,
            'descricao': self.descricao,
            'filial_id': self.filial_id,
            'filial_tag': self.filial_chamado.tag if self.filial_chamado else None,
            'filial_descricao': self.filial_chamado.descricao if self.filial_chamado else None,
            'setor_id': self.setor_id,
            'setor_tag': self.setor_chamado.tag if self.setor_chamado else None,
            'setor_descricao': self.setor_chamado.descricao if self.setor_chamado else None,
            'equipamento_id': self.equipamento_id,
            'equipamento_tag': self.equipamento_chamado.tag if self.equipamento_chamado else None,
            'equipamento_descricao': self.equipamento_chamado.descricao if self.equipamento_chamado else None,
            'prioridade': self.prioridade,
            'status': self.status,
            'solicitante': self.solicitante,
            'empresa': self.empresa,
            'data_criacao': self.data_criacao.isoformat() if self.data_criacao else None,
            'data_atualizacao': self.data_atualizacao.isoformat() if self.data_atualizacao else None,
            'usuario_criacao': self.usuario_criacao
        }

