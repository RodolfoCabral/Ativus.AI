from app import create_app
from models import db
from sqlalchemy import text

app = create_app()

with app.app_context():
    result = db.engine.execute(text('''
        SELECT os.id, os.pmp_id 
        FROM ordens_servico os 
        WHERE os.pmp_id IS NOT NULL 
        AND os.id NOT IN (SELECT DISTINCT os_id FROM atividades_os)
        LIMIT 10
    '''))

    for os_data in result:
        os_id, pmp_id = os_data

        atividades = db.engine.execute(text(f'''
            SELECT id, descricao, ordem 
            FROM atividades_pmp 
            WHERE pmp_id = {pmp_id}
        '''))

        for ativ in atividades:
            desc = ativ[1].replace("'", "''")
            db.engine.execute(text(f'''
                INSERT INTO atividades_os 
                (os_id, atividade_pmp_id, descricao, ordem, status, data_criacao)
                VALUES ({os_id}, {ativ[0]}, '{desc}', {ativ[2] or 1}, 'pendente', NOW())
            '''))

        print(f'OS {os_id}: atividades transferidas')

    db.session.commit()
    print('Transferência concluída!')
