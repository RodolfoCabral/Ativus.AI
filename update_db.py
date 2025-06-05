import os
import sqlite3
from app import create_app

app = create_app()

# Caminho para o banco de dados SQLite
db_path = os.path.join(os.path.dirname(__file__), 'ativus.db')

# Criar um contexto de aplicação
with app.app_context():
    # Conectar ao banco de dados SQLite
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        # Verificar se a tabela user existe
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='user'")
        if cursor.fetchone():
            print("Tabela 'user' encontrada, realizando backup dos dados...")
            
            # Obter dados existentes
            cursor.execute("SELECT id, email, password_hash, profile, created_at, updated_at FROM user")
            existing_users = cursor.fetchall()
            
            print(f"Encontrados {len(existing_users)} usuários no banco de dados.")
            
            # Remover tabela antiga
            cursor.execute("DROP TABLE user")
            print("Tabela 'user' removida.")
            
            # Criar nova tabela com estrutura atualizada
            cursor.execute("""
            CREATE TABLE user (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                email VARCHAR(100) NOT NULL UNIQUE,
                password_hash VARCHAR(128) NOT NULL,
                profile VARCHAR(20) DEFAULT 'user',
                name VARCHAR(100),
                company VARCHAR(100),
                status VARCHAR(20) DEFAULT 'active',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """)
            print("Tabela 'user' recriada com estrutura atualizada.")
            
            # Restaurar dados existentes com valores padrão para novos campos
            for user in existing_users:
                id, email, password_hash, profile, created_at, updated_at = user
                
                # Definir valores padrão para o usuário master
                if email == 'rodolfocabral@outlook.com.br':
                    name = 'Rodolfo Cabral'
                    company = 'Melvin'
                    status = 'active'
                else:
                    name = email.split('@')[0]  # Nome padrão baseado no email
                    company = ''
                    status = 'active'
                
                cursor.execute("""
                INSERT INTO user (id, email, password_hash, profile, name, company, status, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (id, email, password_hash, profile, name, company, status, created_at, updated_at))
            
            conn.commit()
            print(f"Dados restaurados com sucesso para {len(existing_users)} usuários.")
            
            # Verificar se o usuário master existe
            cursor.execute("SELECT id FROM user WHERE email = 'rodolfocabral@outlook.com.br'")
            if not cursor.fetchone():
                # Criar usuário master se não existir
                from models import User, db
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
            # Se a tabela não existir, criar do zero
            from models import db
            db.create_all()
            print("Banco de dados criado do zero.")
            
            # Criar usuário master
            from models import User
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
    
    except Exception as e:
        conn.rollback()
        print(f"Erro ao atualizar banco de dados: {str(e)}")
    finally:
        conn.close()
        print("Operação concluída.")
