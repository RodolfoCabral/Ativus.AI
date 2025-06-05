from flask import Blueprint, request, jsonify, redirect, url_for, render_template
from flask_login import login_user, logout_user, login_required, current_user
from models import User, db

auth_bp = Blueprint('auth', __name__, url_prefix='/api')

@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.json
    
    if not data or not all(k in data for k in ('email', 'password')):
        return jsonify({'success': False, 'message': 'Dados incompletos'})
    
    user = User.query.filter_by(email=data['email']).first()
    
    if user and user.check_password(data['password']):
        # Verificar se o usuário está ativo
        if user.status == 'inactive':
            return jsonify({'success': False, 'message': 'Usuário bloqueado. Entre em contato com o administrador.'})
            
        login_user(user)
        return jsonify({
            'success': True, 
            'message': 'Login realizado com sucesso',
            'profile': user.profile,
            'name': user.name,
            'company': user.company
        })
    
    return jsonify({'success': False, 'message': 'Email ou senha inválidos'})

@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    return jsonify({'success': True, 'message': 'Logout realizado com sucesso'})

@auth_bp.route('/user')
@login_required
def get_user():
    return jsonify({
        'id': current_user.id,
        'email': current_user.email,
        'profile': current_user.profile,
        'name': current_user.name,
        'company': current_user.company,
        'status': current_user.status
    })

@auth_bp.route('/users', methods=['GET'])
@login_required
def get_users():
    # Todos os usuários podem ver a lista, mas apenas master pode modificar
    users = User.query.all()
    users_list = []
    
    for user in users:
        users_list.append({
            'id': user.id,
            'email': user.email,
            'name': user.name or '',
            'company': user.company or '',
            'profile': user.profile,
            'status': user.status
        })
    
    return jsonify({'success': True, 'users': users_list})

@auth_bp.route('/users', methods=['POST'])
@login_required
def create_user():
    # Verificar se o usuário tem permissão (apenas master)
    if current_user.profile != 'master':
        return jsonify({'success': False, 'message': 'Permissão negada. Apenas usuários master podem criar novos usuários.'}), 403
    
    data = request.json
    
    # Validar dados
    required_fields = ['email', 'password', 'name', 'company', 'profile', 'status']
    if not data or not all(k in data for k in required_fields):
        return jsonify({'success': False, 'message': 'Dados incompletos'})
    
    # Verificar se o email já existe
    if User.query.filter_by(email=data['email']).first():
        return jsonify({'success': False, 'message': 'Email já cadastrado'})
    
    # Criar novo usuário
    new_user = User(
        email=data['email'],
        name=data['name'],
        company=data['company'],
        profile=data['profile'],
        status=data['status']
    )
    new_user.set_password(data['password'])
    
    try:
        db.session.add(new_user)
        db.session.commit()
        return jsonify({
            'success': True, 
            'message': 'Usuário criado com sucesso',
            'user': {
                'id': new_user.id,
                'email': new_user.email,
                'name': new_user.name,
                'company': new_user.company,
                'profile': new_user.profile,
                'status': new_user.status
            }
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': f'Erro ao criar usuário: {str(e)}'}), 500

@auth_bp.route('/users/<int:user_id>', methods=['PUT'])
@login_required
def update_user(user_id):
    # Verificar se o usuário tem permissão (apenas master)
    if current_user.profile != 'master':
        return jsonify({'success': False, 'message': 'Permissão negada. Apenas usuários master podem editar usuários.'}), 403
    
    # Verificar se o usuário existe
    user_to_update = User.query.get(user_id)
    if not user_to_update:
        return jsonify({'success': False, 'message': 'Usuário não encontrado'}), 404
    
    data = request.json
    
    # Atualizar campos
    if 'name' in data:
        user_to_update.name = data['name']
    if 'company' in data:
        user_to_update.company = data['company']
    if 'profile' in data:
        user_to_update.profile = data['profile']
    if 'status' in data:
        user_to_update.status = data['status']
    if 'password' in data and data['password']:
        user_to_update.set_password(data['password'])
    
    try:
        db.session.commit()
        return jsonify({
            'success': True, 
            'message': 'Usuário atualizado com sucesso',
            'user': {
                'id': user_to_update.id,
                'email': user_to_update.email,
                'name': user_to_update.name,
                'company': user_to_update.company,
                'profile': user_to_update.profile,
                'status': user_to_update.status
            }
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': f'Erro ao atualizar usuário: {str(e)}'}), 500

@auth_bp.route('/users/<int:user_id>', methods=['DELETE'])
@login_required
def delete_user(user_id):
    # Verificar se o usuário tem permissão (apenas master)
    if current_user.profile != 'master':
        return jsonify({'success': False, 'message': 'Permissão negada. Apenas usuários master podem excluir usuários.'}), 403
    
    # Verificar se o usuário existe
    user_to_delete = User.query.get(user_id)
    if not user_to_delete:
        return jsonify({'success': False, 'message': 'Usuário não encontrado'}), 404
    
    # Não permitir excluir usuários master
    if user_to_delete.profile == 'master':
        return jsonify({'success': False, 'message': 'Não é permitido excluir usuários com perfil master'}), 403
    
    # Não permitir excluir o próprio usuário
    if user_to_delete.id == current_user.id:
        return jsonify({'success': False, 'message': 'Não é permitido excluir o próprio usuário'}), 403
    
    try:
        db.session.delete(user_to_delete)
        db.session.commit()
        return jsonify({
            'success': True, 
            'message': 'Usuário excluído com sucesso'
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': f'Erro ao excluir usuário: {str(e)}'}), 500
