from app import create_app
from models import db
from sqlalchemy import text

app = create_app()

with app.app_context():
    print("🔍 Iniciando transferência de atividades PMP para OS...")

    # Usando db.session.execute em vez de engine.execute
    result = db.session.execute(text('''
        SELECT os.id, os.pmp_id 
        FROM ordens_servico os 
        WHERE os.pmp_id IS NOT NULL 
        AND os.id NOT IN (SELECT DISTINCT os_id FROM atividades_os)
        LIMIT 10
    '''))

    transferidos = 0

    for os_data in result:
        os_id, pmp_id = os_data
        print(f"➡️ OS {os_id} vinculada à PMP {pmp_id}")

        atividades = db.session.execute(text('''
            SELECT id, descricao, ordem 
            FROM atividades_pmp 
            WHERE pmp_id = :pmp_id
        '''), {"pmp_id": pmp_id})

        count = 0
        for ativ in atividades:
            desc = ativ.descricao.replace("'", "''") if ativ.descricao else ""
            ordem = ativ.ordem or 1

            db.session.execute(text('''
                INSERT INTO atividades_os 
                (os_id, atividade_pmp_id, descricao, ordem, status, data_criacao)
                VALUES (:os_id, :atividade_pmp_id, :descricao, :ordem, 'pendente', NOW())
            '''), {
                "os_id": os_id,
                "atividade_pmp_id": ativ.id,
                "descricao": desc,
                "ordem": ordem
            })
            count += 1

        if count > 0:
            print(f"✅ {count} atividades transferidas para OS {os_id}")
            transferidos += 1
        else:
            print(f"⚠️ Nenhuma atividade encontrada para PMP {pmp_id}")

    db.session.commit()
    print(f"🎯 Transferência concluída! {transferidos} OS atualizadas.")
