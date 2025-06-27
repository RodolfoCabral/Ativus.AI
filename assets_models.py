from datetime import datetime
from models import db

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

