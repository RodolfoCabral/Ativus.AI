from flask import Blueprint, request, jsonify
from flask_login import login_required, current_user
from models import db
from models.user import User
from datetime import datetime
import traceback

# Importação segura dos modelos de ativos
try:
    from assets_models import Filial, Setor, Equipamento, Categoria
    ASSETS_AVAILABLE = True
except ImportError as e:
    print(f"Erro ao importar modelos de ativos: {e}")
    ASSETS_AVAILABLE = False

assets_bp = Blueprint('assets', __name__)

def check_admin_permission():
    """Verificar se o usuário tem permissão de admin"""
    if not current_user.is_authenticated:
        return False, "Usuário não autenticado"
    if current_user.profile not in ['admin', 'master']:
        return False, "Acesso negado. Apenas administradores podem realizar esta ação."
    return True, current_user

# ==================== FILIAIS ====================

@assets_bp.route('/api/filiais', methods=['GET'])
@login_required
def get_filiais():
    """Listar filiais da empresa do usuário"""
    if not ASSETS_AVAILABLE:
        return jsonify({'success': False, 'message': 'Funcionalidade de ativos não disponível'}), 503
    
    try:
        # Filtrar por empresa do usuário
        if current_user.profile == 'master':
            filiais = Filial.query.all()
        else:
            filiais = Filial.query.filter_by(empresa=current_user.company).all()
        
        return jsonify({
            'success': True,
            'filiais': [filial.to_dict() for filial in filiais]
        })
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

@assets_bp.route('/api/filiais', methods=['POST'])
@login_required
def create_filial():
    """Criar nova filial"""
    has_permission, user_or_message = check_admin_permission()
    if not has_permission:
        return jsonify({'success': False, 'message': user_or_message}), 403
    
    data = request.get_json()
    
    # Validar campos obrigatórios
    required_fields = ['tag', 'descricao', 'endereco', 'cidade', 'estado', 'email', 'telefone', 'cnpj']
    for field in required_fields:
        if not data.get(field):
            return jsonify({'success': False, 'message': f'Campo {field} é obrigatório'}), 400
    
    try:
        # Verificar se tag já existe na empresa
        existing = Filial.query.filter_by(tag=data['tag'], empresa=current_user.company).first()
        if existing:
            return jsonify({'success': False, 'message': 'Tag já existe nesta empresa'}), 400
        
        # Criar nova filial
        filial = Filial(
            tag=data['tag'],
            descricao=data['descricao'],
            endereco=data['endereco'],
            cidade=data['cidade'],
            estado=data['estado'],
            email=data['email'],
            telefone=data['telefone'],
            cnpj=data['cnpj'],
            empresa=current_user.company,
            usuario_criacao=current_user.email
        )
        
        db.session.add(filial)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Filial cadastrada com sucesso',
            'filial': filial.to_dict()
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)}), 500

# ==================== SETORES ====================

@assets_bp.route('/api/setores', methods=['GET'])
@login_required
def get_setores():
    """Listar setores da empresa do usuário"""
    try:
        # Filtrar por empresa do usuário
        if current_user.profile == 'master':
            setores = Setor.query.all()
        else:
            setores = Setor.query.filter_by(empresa=current_user.company).all()
        
        return jsonify({
            'success': True,
            'setores': [setor.to_dict() for setor in setores]
        })
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

@assets_bp.route('/api/setores', methods=['POST'])
@login_required
def create_setor():
    """Criar novo setor"""
    has_permission, user_or_message = check_admin_permission()
    if not has_permission:
        return jsonify({'success': False, 'message': user_or_message}), 403
    
    data = request.get_json()
    
    # Validar campos obrigatórios
    required_fields = ['tag', 'descricao', 'filial_id']
    for field in required_fields:
        if not data.get(field):
            return jsonify({'success': False, 'message': f'Campo {field} é obrigatório'}), 400
    
    try:
        # Verificar se filial existe e pertence à empresa
        filial = Filial.query.filter_by(id=data['filial_id'], empresa=current_user.company).first()
        if not filial:
            return jsonify({'success': False, 'message': 'Filial não encontrada'}), 400
        
        # Verificar se tag já existe na empresa
        existing = Setor.query.filter_by(tag=data['tag'], empresa=current_user.company).first()
        if existing:
            return jsonify({'success': False, 'message': 'Tag já existe nesta empresa'}), 400
        
        # Criar novo setor
        setor = Setor(
            tag=data['tag'],
            descricao=data['descricao'],
            filial_id=data['filial_id'],
            empresa=current_user.company,
            usuario_criacao=current_user.email
        )
        
        db.session.add(setor)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Setor cadastrado com sucesso',
            'setor': setor.to_dict()
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)}), 500

# ==================== EQUIPAMENTOS ====================

@assets_bp.route('/api/equipamentos', methods=['GET'])
@login_required
def get_equipamentos():
    """Listar equipamentos da empresa do usuário"""
    try:
        # Filtrar por empresa do usuário
        if current_user.profile == 'master':
            equipamentos = Equipamento.query.all()
        else:
            equipamentos = Equipamento.query.filter_by(empresa=current_user.company).all()
        
        return jsonify({
            'success': True,
            'equipamentos': [equipamento.to_dict() for equipamento in equipamentos]
        })
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

@assets_bp.route('/api/equipamentos', methods=['POST'])
@login_required
def create_equipamento():
    """Criar novo equipamento"""
    has_permission, user_or_message = check_admin_permission()
    if not has_permission:
        return jsonify({'success': False, 'message': user_or_message}), 403
    
    data = request.get_json()
    
    # Validar campos obrigatórios
    required_fields = ['tag', 'descricao', 'setor_id']
    for field in required_fields:
        if not data.get(field):
            return jsonify({'success': False, 'message': f'Campo {field} é obrigatório'}), 400
    
    try:
        # Verificar se setor existe e pertence à empresa
        setor = Setor.query.filter_by(id=data['setor_id'], empresa=current_user.company).first()
        if not setor:
            return jsonify({'success': False, 'message': 'Setor não encontrado ou não pertence à sua empresa'}), 400
        
        # Verificar se tag já existe na empresa
        existing = Equipamento.query.filter_by(tag=data['tag'], empresa=current_user.company).first()
        if existing:
            return jsonify({'success': False, 'message': 'Tag já existe nesta empresa'}), 400
        
        # Criar novo equipamento
        equipamento = Equipamento(
            tag=data['tag'],
            descricao=data['descricao'],
            setor_id=data['setor_id'],
            empresa=current_user.company,
            usuario_criacao=current_user.email
        )
        
        db.session.add(equipamento)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Equipamento cadastrado com sucesso',
            'equipamento': equipamento.to_dict()
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)}), 500

# ==================== CATEGORIAS ====================

@assets_bp.route('/api/categorias', methods=['GET'])
def get_categorias():
    """Listar categorias da empresa do usuário"""
    user = current_user #get_current_user()
    if not user:
        return jsonify({'success': False, 'message': 'Usuário não autenticado'}), 401
    
    try:
        # Filtrar por empresa do usuário
        if user.profile == 'master':
            categorias = Categoria.query.all()
        else:
            categorias = Categoria.query.filter_by(empresa=user.company).all()
        
        return jsonify({
            'success': True,
            'categorias': [categoria.to_dict() for categoria in categorias]
        })
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

@assets_bp.route('/api/categorias', methods=['POST'])
def create_categoria():
    """Criar nova categoria"""
    has_permission, user_or_message = check_admin_permission()
    if not has_permission:
        return jsonify({'success': False, 'message': user_or_message}), 403
    
    user = user_or_message
    data = request.get_json()
    
    # Validar campos obrigatórios
    if not data.get('nome'):
        return jsonify({'success': False, 'message': 'Nome é obrigatório'}), 400
    
    try:
        # Verificar se categoria já existe na empresa
        existing = Categoria.query.filter_by(nome=data['nome'], empresa=user.company).first()
        if existing:
            return jsonify({'success': False, 'message': 'Categoria já existe nesta empresa'}), 400
        
        # Criar nova categoria
        categoria = Categoria(
            nome=data['nome'],
            descricao=data.get('descricao', ''),
            empresa=user.company,
            usuario_criacao=user.email
        )
        
        db.session.add(categoria)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Categoria criada com sucesso',
            'categoria': categoria.to_dict()
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)}), 500

# ==================== ÁRVORE DE ATIVOS ====================

@assets_bp.route('/api/arvore-ativos', methods=['GET'])
def get_arvore_ativos():
    """Obter árvore hierárquica de ativos"""
    user = current_user #get_current_user()
    if not user:
        return jsonify({'success': False, 'message': 'Usuário não autenticado'}), 401
    
    try:
        # Filtrar por empresa do usuário
        if user.profile == 'master':
            filiais = Filial.query.all()
        else:
            filiais = Filial.query.filter_by(empresa=user.company).all()
        
        arvore = []
        for filial in filiais:
            filial_data = filial.to_dict()
            filial_data['setores'] = []
            
            for setor in filial.setores:
                setor_data = setor.to_dict()
                setor_data['equipamentos'] = [eq.to_dict() for eq in setor.equipamentos]
                filial_data['setores'].append(setor_data)
            
            arvore.append(filial_data)
        
        return jsonify({
            'success': True,
            'arvore': arvore
        })
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500


# ==================== EXCLUSÃO ====================

@assets_bp.route('/api/filiais/<int:filial_id>', methods=['DELETE'])
@login_required
def delete_filial(filial_id):
    """Excluir uma filial e todos os seus setores e equipamentos"""
    user = current_user #get_current_user()
    if not user:
        return jsonify({'success': False, 'message': 'Usuário não autenticado'}), 401
    
    # Verificar permissões (apenas admin e master podem excluir)
    if user.profile not in ['admin', 'master']:
        return jsonify({'success': False, 'message': 'Permissão negada. Apenas administradores podem excluir ativos.'}), 403
    
    try:
        filial = Filial.query.get(filial_id)
        if not filial:
            return jsonify({'success': False, 'message': 'Filial não encontrada'}), 404
        
        # Verificar se o usuário tem permissão para esta empresa
        if user.profile != 'master' and filial.empresa != user.company:
            return jsonify({'success': False, 'message': 'Permissão negada. Você só pode excluir ativos da sua empresa.'}), 403
        
        # Contar setores e equipamentos que serão excluídos
        setores_count = Setor.query.filter_by(filial_id=filial_id).count()
        equipamentos_count = 0
        for setor in Setor.query.filter_by(filial_id=filial_id).all():
            equipamentos_count += Equipamento.query.filter_by(setor_id=setor.id).count()
        
        # Excluir todos os equipamentos dos setores da filial
        for setor in Setor.query.filter_by(filial_id=filial_id).all():
            Equipamento.query.filter_by(setor_id=setor.id).delete()
        
        # Excluir todos os setores da filial
        Setor.query.filter_by(filial_id=filial_id).delete()
        
        # Excluir a filial
        db.session.delete(filial)
        db.session.commit()
        
        return jsonify({
            'success': True, 
            'message': f'Filial excluída com sucesso! Também foram excluídos {setores_count} setores e {equipamentos_count} equipamentos.'
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': f'Erro ao excluir filial: {str(e)}'}), 500

@assets_bp.route('/api/setores/<int:setor_id>', methods=['DELETE'])
@login_required
def delete_setor(setor_id):
    """Excluir um setor e todos os seus equipamentos"""
    user = current_user #get_current_user()
    if not user:
        return jsonify({'success': False, 'message': 'Usuário não autenticado'}), 401
    
    # Verificar permissões (apenas admin e master podem excluir)
    if user.profile not in ['admin', 'master']:
        return jsonify({'success': False, 'message': 'Permissão negada. Apenas administradores podem excluir ativos.'}), 403
    
    try:
        setor = Setor.query.get(setor_id)
        if not setor:
            return jsonify({'success': False, 'message': 'Setor não encontrado'}), 404
        
        # Verificar se o usuário tem permissão para esta empresa
        if user.profile != 'master' and setor.empresa != user.company:
            return jsonify({'success': False, 'message': 'Permissão negada. Você só pode excluir ativos da sua empresa.'}), 403
        
        # Contar equipamentos que serão excluídos
        equipamentos_count = Equipamento.query.filter_by(setor_id=setor_id).count()
        
        # Excluir todos os equipamentos do setor
        Equipamento.query.filter_by(setor_id=setor_id).delete()
        
        # Excluir o setor
        db.session.delete(setor)
        db.session.commit()
        
        return jsonify({
            'success': True, 
            'message': f'Setor excluído com sucesso! Também foram excluídos {equipamentos_count} equipamentos.'
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': f'Erro ao excluir setor: {str(e)}'}), 500

@assets_bp.route('/api/equipamentos/<int:equipamento_id>', methods=['DELETE'])
@login_required
def delete_equipamento(equipamento_id):
    """Excluir um equipamento"""
    user = current_user #get_current_user()
    if not user:
        return jsonify({'success': False, 'message': 'Usuário não autenticado'}), 401
    
    # Verificar permissões (apenas admin e master podem excluir)
    if user.profile not in ['admin', 'master']:
        return jsonify({'success': False, 'message': 'Permissão negada. Apenas administradores podem excluir ativos.'}), 403
    
    try:
        equipamento = Equipamento.query.get(equipamento_id)
        if not equipamento:
            return jsonify({'success': False, 'message': 'Equipamento não encontrado'}), 404
        
        # Verificar se o usuário tem permissão para esta empresa
        if user.profile != 'master' and equipamento.empresa != user.company:
            return jsonify({'success': False, 'message': 'Permissão negada. Você só pode excluir ativos da sua empresa.'}), 403
        
        # Excluir o equipamento
        db.session.delete(equipamento)
        db.session.commit()
        
        return jsonify({
            'success': True, 
            'message': 'Equipamento excluído com sucesso!'
        })
    except Exception as e:
        db.session.rollback()
        print("ERRO AO EXCLUIR EQUIPAMENTO:")
        print(traceback.format_exc())  # <-- Isto mostrará no log do Heroku ou console local
        return jsonify({'success': False, 'message': f'Erro ao excluir equipamento: {str(e)}'}), 500

