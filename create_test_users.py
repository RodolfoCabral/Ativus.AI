import os
from app import create_app
from models import db, User

app = create_app()

# Criar um contexto de aplicação para operações com o banco de dados
with app.app_context():
    # Criar usuário extra para teste (perfil admin)
    admin_test = User.query.filter_by(email='admin@teste.com').first()
    
    if not admin_test:
        print("Criando usuário de teste com perfil admin...")
        admin_test = User(
            email='admin@teste.com',
            name='Administrador Teste',
            company='Empresa Teste',
            profile='admin',
            status='active'
        )
        admin_test.set_password('senha123')
        db.session.add(admin_test)
        db.session.commit()
        print('Usuário de teste (admin) criado com sucesso!')
    else:
        print('Usuário de teste (admin) já existe.')
    
    # Criar usuário extra para teste (perfil user)
    user_test = User.query.filter_by(email='usuario@teste.com').first()
    
    if not user_test:
        print("Criando usuário de teste com perfil user...")
        user_test = User(
            email='usuario@teste.com',
            name='Usuário Comum',
            company='Empresa Teste',
            profile='user',
            status='active'
        )
        user_test.set_password('senha123')
        db.session.add(user_test)
        db.session.commit()
        print('Usuário de teste (user) criado com sucesso!')
    else:
        print('Usuário de teste (user) já existe.')
