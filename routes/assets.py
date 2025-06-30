from flask import Blueprint, request, jsonify
from flask_login import login_required, current_user
from models import db
from models.user import User
from datetime import datetime

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
    user = get_current_user()
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
    user = get_current_user()
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


# ==================== EDIÇÃO DE ATIVOS ====================

@assets_bp.route('/api/filiais/<int:filial_id>', methods=['PUT'])
@login_required
def update_filial(filial_id):
    """Editar filial existente"""
    has_permission, user_or_message = check_admin_permission()
    if not has_permission:
        return jsonify({'success': False, 'message': user_or_message}), 403
    
    if not ASSETS_AVAILABLE:
        return jsonify({'success': False, 'message': 'Funcionalidade de ativos não disponível'}), 503
    
    try:
        # Buscar filial
        if current_user.profile == 'master':
            filial = Filial.query.get(filial_id)
        else:
            filial = Filial.query.filter_by(id=filial_id, empresa=current_user.company).first()
        
        if not filial:
            return jsonify({'success': False, 'message': 'Filial não encontrada'}), 404
        
        data = request.get_json()
        
        # Validar campos obrigatórios
        required_fields = ['tag', 'descricao', 'endereco', 'cidade', 'estado', 'email', 'telefone', 'cnpj']
        for field in required_fields:
            if not data.get(field):
                return jsonify({'success': False, 'message': f'Campo {field} é obrigatório'}), 400
        
        # Verificar se nova tag já existe (exceto na própria filial)
        existing = Filial.query.filter_by(tag=data['tag'], empresa=current_user.company).filter(Filial.id != filial_id).first()
        if existing:
            return jsonify({'success': False, 'message': 'Tag já existe nesta empresa'}), 400
        
        # Atualizar dados
        filial.tag = data['tag']
        filial.descricao = data['descricao']
        filial.endereco = data['endereco']
        filial.cidade = data['cidade']
        filial.estado = data['estado']
        filial.email = data['email']
        filial.telefone = data['telefone']
        filial.cnpj = data['cnpj']
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Filial atualizada com sucesso',
            'filial': filial.to_dict()
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)}), 500

@assets_bp.route('/api/setores/<int:setor_id>', methods=['PUT'])
@login_required
def update_setor(setor_id):
    """Editar setor existente"""
    has_permission, user_or_message = check_admin_permission()
    if not has_permission:
        return jsonify({'success': False, 'message': user_or_message}), 403
    
    if not ASSETS_AVAILABLE:
        return jsonify({'success': False, 'message': 'Funcionalidade de ativos não disponível'}), 503
    
    try:
        # Buscar setor
        if current_user.profile == 'master':
            setor = Setor.query.get(setor_id)
        else:
            setor = Setor.query.filter_by(id=setor_id, empresa=current_user.company).first()
        
        if not setor:
            return jsonify({'success': False, 'message': 'Setor não encontrado'}), 404
        
        data = request.get_json()
        
        # Validar campos obrigatórios
        required_fields = ['tag', 'descricao', 'filial_id']
        for field in required_fields:
            if not data.get(field):
                return jsonify({'success': False, 'message': f'Campo {field} é obrigatório'}), 400
        
        # Verificar se filial existe
        filial = Filial.query.filter_by(id=data['filial_id'], empresa=current_user.company).first()
        if not filial:
            return jsonify({'success': False, 'message': 'Filial não encontrada'}), 404
        
        # Verificar se nova tag já existe na filial (exceto no próprio setor)
        existing = Setor.query.filter_by(tag=data['tag'], filial_id=data['filial_id']).filter(Setor.id != setor_id).first()
        if existing:
            return jsonify({'success': False, 'message': 'Tag já existe nesta filial'}), 400
        
        # Atualizar dados
        setor.tag = data['tag']
        setor.descricao = data['descricao']
        setor.filial_id = data['filial_id']
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Setor atualizado com sucesso',
            'setor': setor.to_dict()
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)}), 500

@assets_bp.route('/api/equipamentos/<int:equipamento_id>', methods=['PUT'])
@login_required
def update_equipamento(equipamento_id):
    """Editar equipamento existente"""
    has_permission, user_or_message = check_admin_permission()
    if not has_permission:
        return jsonify({'success': False, 'message': user_or_message}), 403
    
    if not ASSETS_AVAILABLE:
        return jsonify({'success': False, 'message': 'Funcionalidade de ativos não disponível'}), 503
    
    try:
        # Buscar equipamento
        if current_user.profile == 'master':
            equipamento = Equipamento.query.get(equipamento_id)
        else:
            equipamento = Equipamento.query.filter_by(id=equipamento_id, empresa=current_user.company).first()
        
        if not equipamento:
            return jsonify({'success': False, 'message': 'Equipamento não encontrado'}), 404
        
        data = request.get_json()
        
        # Validar campos obrigatórios
        required_fields = ['tag', 'descricao', 'setor_id']
        for field in required_fields:
            if not data.get(field):
                return jsonify({'success': False, 'message': f'Campo {field} é obrigatório'}), 400
        
        # Verificar se setor existe
        setor = Setor.query.filter_by(id=data['setor_id'], empresa=current_user.company).first()
        if not setor:
            return jsonify({'success': False, 'message': 'Setor não encontrado'}), 404
        
        # Verificar se nova tag já existe no setor (exceto no próprio equipamento)
        existing = Equipamento.query.filter_by(tag=data['tag'], setor_id=data['setor_id']).filter(Equipamento.id != equipamento_id).first()
        if existing:
            return jsonify({'success': False, 'message': 'Tag já existe neste setor'}), 400
        
        # Atualizar dados
        equipamento.tag = data['tag']
        equipamento.descricao = data['descricao']
        equipamento.setor_id = data['setor_id']
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Equipamento atualizado com sucesso',
            'equipamento': equipamento.to_dict()
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)}), 500

# ==================== EXCLUSÃO DE ATIVOS ====================

@assets_bp.route('/api/filiais/<int:filial_id>', methods=['DELETE'])
@login_required
def delete_filial(filial_id):
    """Excluir filial e todos os seus dependentes"""
    has_permission, user_or_message = check_admin_permission()
    if not has_permission:
        return jsonify({'success': False, 'message': user_or_message}), 403
    
    if not ASSETS_AVAILABLE:
        return jsonify({'success': False, 'message': 'Funcionalidade de ativos não disponível'}), 503
    
    try:
        # Buscar filial
        if current_user.profile == 'master':
            filial = Filial.query.get(filial_id)
        else:
            filial = Filial.query.filter_by(id=filial_id, empresa=current_user.company).first()
        
        if not filial:
            return jsonify({'success': False, 'message': 'Filial não encontrada'}), 404
        
        # Contar dependentes
        setores_count = len(filial.setores)
        equipamentos_count = sum(len(setor.equipamentos) for setor in filial.setores)
        
        # Excluir (cascade vai remover setores e equipamentos automaticamente)
        db.session.delete(filial)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': f'Filial excluída com sucesso. Removidos também: {setores_count} setores e {equipamentos_count} equipamentos.',
            'removed': {
                'filiais': 1,
                'setores': setores_count,
                'equipamentos': equipamentos_count
            }
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)}), 500

@assets_bp.route('/api/setores/<int:setor_id>', methods=['DELETE'])
@login_required
def delete_setor(setor_id):
    """Excluir setor e todos os seus equipamentos"""
    has_permission, user_or_message = check_admin_permission()
    if not has_permission:
        return jsonify({'success': False, 'message': user_or_message}), 403
    
    if not ASSETS_AVAILABLE:
        return jsonify({'success': False, 'message': 'Funcionalidade de ativos não disponível'}), 503
    
    try:
        # Buscar setor
        if current_user.profile == 'master':
            setor = Setor.query.get(setor_id)
        else:
            setor = Setor.query.filter_by(id=setor_id, empresa=current_user.company).first()
        
        if not setor:
            return jsonify({'success': False, 'message': 'Setor não encontrado'}), 404
        
        # Contar equipamentos
        equipamentos_count = len(setor.equipamentos)
        
        # Excluir (cascade vai remover equipamentos automaticamente)
        db.session.delete(setor)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': f'Setor excluído com sucesso. Removidos também: {equipamentos_count} equipamentos.',
            'removed': {
                'setores': 1,
                'equipamentos': equipamentos_count
            }
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)}), 500

@assets_bp.route('/api/equipamentos/<int:equipamento_id>', methods=['DELETE'])
@login_required
def delete_equipamento(equipamento_id):
    """Excluir equipamento"""
    has_permission, user_or_message = check_admin_permission()
    if not has_permission:
        return jsonify({'success': False, 'message': user_or_message}), 403
    
    if not ASSETS_AVAILABLE:
        return jsonify({'success': False, 'message': 'Funcionalidade de ativos não disponível'}), 503
    
    try:
        # Buscar equipamento
        if current_user.profile == 'master':
            equipamento = Equipamento.query.get(equipamento_id)
        else:
            equipamento = Equipamento.query.filter_by(id=equipamento_id, empresa=current_user.company).first()
        
        if not equipamento:
            return jsonify({'success': False, 'message': 'Equipamento não encontrado'}), 404
        
        # Excluir
        db.session.delete(equipamento)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Equipamento excluído com sucesso.',
            'removed': {
                'equipamentos': 1
            }
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)}), 500

# ==================== OBTER DADOS PARA EDIÇÃO ====================

@assets_bp.route('/api/filiais/<int:filial_id>', methods=['GET'])
@login_required
def get_filial(filial_id):
    """Obter dados de uma filial específica"""
    if not ASSETS_AVAILABLE:
        return jsonify({'success': False, 'message': 'Funcionalidade de ativos não disponível'}), 503
    
    try:
        # Buscar filial
        if current_user.profile == 'master':
            filial = Filial.query.get(filial_id)
        else:
            filial = Filial.query.filter_by(id=filial_id, empresa=current_user.company).first()
        
        if not filial:
            return jsonify({'success': False, 'message': 'Filial não encontrada'}), 404
        
        return jsonify({
            'success': True,
            'filial': filial.to_dict()
        })
        
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

@assets_bp.route('/api/setores/<int:setor_id>', methods=['GET'])
@login_required
def get_setor(setor_id):
    """Obter dados de um setor específico"""
    if not ASSETS_AVAILABLE:
        return jsonify({'success': False, 'message': 'Funcionalidade de ativos não disponível'}), 503
    
    try:
        # Buscar setor
        if current_user.profile == 'master':
            setor = Setor.query.get(setor_id)
        else:
            setor = Setor.query.filter_by(id=setor_id, empresa=current_user.company).first()
        
        if not setor:
            return jsonify({'success': False, 'message': 'Setor não encontrado'}), 404
        
        return jsonify({
            'success': True,
            'setor': setor.to_dict()
        })
        
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

@assets_bp.route('/api/equipamentos/<int:equipamento_id>', methods=['GET'])
@login_required
def get_equipamento(equipamento_id):
    """Obter dados de um equipamento específico"""
    if not ASSETS_AVAILABLE:
        return jsonify({'success': False, 'message': 'Funcionalidade de ativos não disponível'}), 503
    
    try:
        # Buscar equipamento
        if current_user.profile == 'master':
            equipamento = Equipamento.query.get(equipamento_id)
        else:
            equipamento = Equipamento.query.filter_by(id=equipamento_id, empresa=current_user.company).first()
        
        if not equipamento:
            return jsonify({'success': False, 'message': 'Equipamento não encontrado'}), 404
        
        return jsonify({
            'success': True,
            'equipamento': equipamento.to_dict()
        })
        
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

