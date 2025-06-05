import os
from app import create_app
from models import db, User

app = create_app()

# Criar um contexto de aplicação para operações com o banco de dados
with app.app_context():
    # Criar todas as tabelas definidas nos modelos
    print("Criando estrutura do banco de dados...")
    db.create_all()
    print("Estrutura do banco de dados criada com sucesso!")
    
    # Criar o usuário administrador
    print("Criando usuário administrador...")
    admin = User(
        email='rodolfocabral@outlook.com.br', 
        profile='master',
        name='Rodolfo Cabral',
        company='Melvin',
        status='active'
    )
    admin.set_password('101002Rm#')
    db.session.add(admin)
    db.session.commit()
    print('Usuário administrador criado com sucesso!')
