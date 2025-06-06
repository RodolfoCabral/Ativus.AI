import os
from app import create_app, db
from models import User
import bcrypt

def init_db():
    app = create_app()
    with app.app_context():
        # Criar tabelas
        db.create_all()
        
        # Verificar se já existe um usuário master
        if not User.query.filter_by(email='rodolfocabral@outlook.com.br').first():
            # Criar hash da senha
            password = '101002Rm#'
            hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
            
            # Criar usuário master
            master_user = User(
                email='rodolfocabral@outlook.com.br',
                password=hashed_password,
                name='Rodolfo Cabral',
                company='Melvin',
                profile='master',
                status='active'
            )
            
            db.session.add(master_user)
            db.session.commit()
            print("Usuário master criado com sucesso!")
        else:
            print("Usuário master já existe.")
        
        # Criar usuários de teste
        create_test_users()

def create_test_users():
    # Verificar se já existem usuários de teste
    if not User.query.filter_by(email='admin@teste.com').first():
        # Criar hash da senha
        password = 'senha123'
        hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
        
        # Criar usuário admin
        admin_user = User(
            email='admin@teste.com',
            password=hashed_password,
            name='Administrador Teste',
            company='Empresa Teste',
            profile='admin',
            status='active'
        )
        
        db.session.add(admin_user)
        
        # Criar usuário comum
        user = User(
            email='usuario@teste.com',
            password=hashed_password,
            name='Usuário Comum',
            company='Empresa Teste',
            profile='user',
            status='active'
        )
        
        db.session.add(user)
        db.session.commit()
        print("Usuários de teste criados com sucesso!")
    else:
        print("Usuários de teste já existem.")

if __name__ == '__main__':
    init_db()
