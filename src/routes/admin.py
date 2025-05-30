from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from src import db
from src.models.user import User, AccessRequest

admin_bp = Blueprint('admin', __name__, url_prefix='/admin')

@admin_bp.route('/')
@login_required
def index():
    if not current_user.is_admin:
        flash('Acesso negado. Você não tem permissão para acessar esta área.', 'error')
        return redirect(url_for('main.dashboard'))
    return render_template('admin/index.html')

@admin_bp.route('/users')
@login_required
def users():
    if not current_user.is_admin:
        flash('Acesso negado. Você não tem permissão para acessar esta área.', 'error')
        return redirect(url_for('main.dashboard'))
    
    users = User.query.all()
    return render_template('admin/users.html', users=users)

@admin_bp.route('/access_requests')
@login_required
def access_requests():
    if not current_user.is_admin:
        flash('Acesso negado. Você não tem permissão para acessar esta área.', 'error')
        return redirect(url_for('main.dashboard'))
    
    requests = AccessRequest.query.filter_by(status='pending').all()
    return render_template('admin/access_requests.html', requests=requests)

@admin_bp.route('/approve_request/<int:request_id>', methods=['POST'])
@login_required
def approve_request(request_id):
    if not current_user.is_admin:
        flash('Acesso negado. Você não tem permissão para acessar esta área.', 'error')
        return redirect(url_for('main.dashboard'))
    
    access_request = AccessRequest.query.get_or_404(request_id)
    
    # Criar novo usuário
    user = User(
        name=access_request.name,
        email=access_request.email,
        phone=access_request.phone,
        is_admin=False
    )
    
    # Gerar senha temporária
    import secrets
    import string
    alphabet = string.ascii_letters + string.digits
    temp_password = ''.join(secrets.choice(alphabet) for i in range(10))
    user.set_password(temp_password)
    
    # Atualizar status da solicitação
    access_request.status = 'approved'
    
    db.session.add(user)
    db.session.commit()
    
    # Enviar email com credenciais
    from flask_mail import Message
    from src import mail
    
    try:
        msg = Message(
            'Acesso Aprovado - OS Management',
            recipients=[user.email]
        )
        msg.body = f'''
        Olá {user.name},
        
        Sua solicitação de acesso ao sistema OS Management foi aprovada!
        
        Suas credenciais de acesso são:
        Email: {user.email}
        Senha temporária: {temp_password}
        
        Por favor, faça login e altere sua senha o mais breve possível.
        
        Atenciosamente,
        Equipe OS Management
        '''
        mail.send(msg)
        flash(f'Usuário {user.email} criado com sucesso e email com credenciais enviado.', 'success')
    except Exception as e:
        flash(f'Usuário criado, mas houve um problema ao enviar o email: {str(e)}', 'warning')
    
    return redirect(url_for('admin.access_requests'))

@admin_bp.route('/reject_request/<int:request_id>', methods=['POST'])
@login_required
def reject_request(request_id):
    if not current_user.is_admin:
        flash('Acesso negado. Você não tem permissão para acessar esta área.', 'error')
        return redirect(url_for('main.dashboard'))
    
    access_request = AccessRequest.query.get_or_404(request_id)
    access_request.status = 'rejected'
    db.session.commit()
    
    flash(f'Solicitação de {access_request.email} rejeitada.', 'info')
    return redirect(url_for('admin.access_requests'))
