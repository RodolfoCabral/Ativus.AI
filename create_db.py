import os
from app import create_app, db
from models import User

app = create_app()

# Criar um contexto de aplicação para operações com o banco de dados
with app.app_context():
    # Criar todas as tabelas definidas nos modelos
    db.create_all()
    
    # Verificar se o usuário administrador já existe
    admin_user = User.query.filter_by(email='rodolfocabral@outlook.com.br').first()
    
    # Se não existir, criar o usuário administrador
    if not admin_user:
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
    else:
        # Atualizar informações do usuário master
        admin_user.profile = 'master'
        admin_user.name = 'Rodolfo Cabral'
        admin_user.company = 'Melvin'
        admin_user.status = 'active'
        db.session.commit()
        print('Usuário administrador atualizado com sucesso!')
