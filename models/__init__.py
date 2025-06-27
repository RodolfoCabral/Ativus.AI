# Pacote models
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
import bcrypt

# Inicialização do SQLAlchemy
db = SQLAlchemy()

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    profile = db.Column(db.String(20), default='user')
    name = db.Column(db.String(100), nullable=True)
    company = db.Column(db.String(100), nullable=True)
    status = db.Column(db.String(20), default='active')
    created_at = db.Column(db.DateTime, server_default=db.func.now())
    updated_at = db.Column(db.DateTime, server_default=db.func.now(), onupdate=db.func.now())
    
    def set_password(self, password):
        """Gera um hash da senha fornecida."""
        salt = bcrypt.gensalt()
        self.password_hash = bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')
    
    def check_password(self, password):
        """Verifica se a senha fornecida corresponde ao hash armazenado."""
        return bcrypt.checkpw(password.encode('utf-8'), self.password_hash.encode('utf-8'))
    
    def to_dict(self):
        """Converte o objeto User para um dicionário."""
        return {
            'id': self.id,
            'email': self.email,
            'profile': self.profile,
            'name': self.name,
            'company': self.company,
            'status': self.status,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

# Exportar para uso externo
__all__ = ['db', 'User']

