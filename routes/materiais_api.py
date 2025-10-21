from flask import Blueprint, request, jsonify
from flask_login import login_required, current_user
from models import db
from assets_models import MaterialEstoque
import logging

# Configurar logging
logger = logging.getLogger(__name__)

# Criar blueprint
materiais_bp = Blueprint('materiais', __name__)

@materiais_bp.route('/api/materiais', methods=['POST'])
@login_required
def criar_material():
    """API para criar um novo material no estoque"""
    try:
        data = request.get_json()
        
        # Validação básica dos dados obrigatórios
        if not data:
            return jsonify({
                'success': False,
                'message': 'Dados não fornecidos'
            }), 400
        
        # Campos obrigatórios
        campos_obrigatorios = ['codigo', 'descricao', 'tipoRecurso']
        for campo in campos_obrigatorios:
            if not data.get(campo):
                return jsonify({
                    'success': False,
                    'message': f'Campo obrigatório não preenchido: {campo}'
                }), 400
        
        # Verificar se o código já existe para esta empresa
        codigo_existente = MaterialEstoque.query.filter_by(
            codigo=data['codigo'],
            empresa=current_user.company
        ).first()
        
        if codigo_existente:
            return jsonify({
                'success': False,
                'message': f'Já existe um material com o código {data["codigo"]}'
            }), 400
        
        # Criar novo material
        novo_material = MaterialEstoque(
            # Dados básicos
            codigo=data['codigo'],
            nome=data['descricao'],  # O campo 'nome' no modelo corresponde à 'descrição' no form
            descricao=data.get('descricao', ''),
            
            # Tipo e categoria
            categoria=data.get('tipoRecurso', ''),
            
            # Dados de estoque
            unidade=data.get('unidadeMedida', 'UN'),
            valor_unitario=float(data.get('valorUnitario', 0)),
            quantidade_estoque=float(data.get('estoqueReal', 0)),
            estoque_minimo=float(data.get('estoqueMinimo', 0)),
            
            # Status
            ativo=True if data.get('status', 'Ativo') == 'Ativo' else False,
            
            # Dados da empresa e usuário
            empresa=current_user.company,
            usuario_criacao=current_user.name or current_user.email
        )
        
        # Salvar no banco
        db.session.add(novo_material)
        db.session.commit()
        
        logger.info(f"Material criado com sucesso: {novo_material.codigo} - {novo_material.nome}")
        
        return jsonify({
            'success': True,
            'message': 'Material cadastrado com sucesso!',
            'material': novo_material.to_dict()
        }), 201
        
    except ValueError as e:
        logger.error(f"Erro de validação ao criar material: {e}")
        return jsonify({
            'success': False,
            'message': f'Erro de validação: {str(e)}'
        }), 400
        
    except Exception as e:
        logger.error(f"Erro ao criar material: {e}")
        db.session.rollback()
        return jsonify({
            'success': False,
            'message': 'Erro interno do servidor'
        }), 500

@materiais_bp.route('/api/materiais', methods=['GET'])
@login_required
def listar_materiais():
    """API para listar materiais da empresa"""
    try:
        # Buscar materiais da empresa do usuário
        materiais = MaterialEstoque.query.filter_by(
            empresa=current_user.company
        ).order_by(MaterialEstoque.nome).all()
        
        return jsonify({
            'success': True,
            'materiais': [material.to_dict() for material in materiais],
            'total': len(materiais)
        })
        
    except Exception as e:
        logger.error(f"Erro ao listar materiais: {e}")
        return jsonify({
            'success': False,
            'message': 'Erro ao carregar materiais'
        }), 500

@materiais_bp.route('/api/materiais/<int:material_id>', methods=['GET'])
@login_required
def obter_material(material_id):
    """API para obter um material específico"""
    try:
        material = MaterialEstoque.query.filter_by(
            id=material_id,
            empresa=current_user.company
        ).first()
        
        if not material:
            return jsonify({
                'success': False,
                'message': 'Material não encontrado'
            }), 404
        
        return jsonify({
            'success': True,
            'material': material.to_dict()
        })
        
    except Exception as e:
        logger.error(f"Erro ao obter material: {e}")
        return jsonify({
            'success': False,
            'message': 'Erro ao carregar material'
        }), 500

@materiais_bp.route('/api/materiais/<int:material_id>', methods=['PUT'])
@login_required
def atualizar_material(material_id):
    """API para atualizar um material"""
    try:
        data = request.get_json()
        
        # Buscar material
        material = MaterialEstoque.query.filter_by(
            id=material_id,
            empresa=current_user.company
        ).first()
        
        if not material:
            return jsonify({
                'success': False,
                'message': 'Material não encontrado'
            }), 404
        
        # Atualizar campos
        if 'codigo' in data:
            # Verificar se o novo código já existe (exceto para o próprio material)
            codigo_existente = MaterialEstoque.query.filter(
                MaterialEstoque.codigo == data['codigo'],
                MaterialEstoque.empresa == current_user.company,
                MaterialEstoque.id != material_id
            ).first()
            
            if codigo_existente:
                return jsonify({
                    'success': False,
                    'message': f'Já existe um material com o código {data["codigo"]}'
                }), 400
            
            material.codigo = data['codigo']
        
        if 'descricao' in data:
            material.nome = data['descricao']
            material.descricao = data['descricao']
        
        if 'tipoRecurso' in data:
            material.categoria = data['tipoRecurso']
        
        if 'unidadeMedida' in data:
            material.unidade = data['unidadeMedida']
        
        if 'valorUnitario' in data:
            material.valor_unitario = float(data['valorUnitario'])
        
        if 'estoqueReal' in data:
            material.quantidade_estoque = float(data['estoqueReal'])
        
        if 'estoqueMinimo' in data:
            material.estoque_minimo = float(data['estoqueMinimo'])
        
        if 'status' in data:
            material.ativo = data['status'] == 'Ativo'
        
        # Salvar alterações
        db.session.commit()
        
        logger.info(f"Material atualizado: {material.codigo} - {material.nome}")
        
        return jsonify({
            'success': True,
            'message': 'Material atualizado com sucesso!',
            'material': material.to_dict()
        })
        
    except ValueError as e:
        logger.error(f"Erro de validação ao atualizar material: {e}")
        return jsonify({
            'success': False,
            'message': f'Erro de validação: {str(e)}'
        }), 400
        
    except Exception as e:
        logger.error(f"Erro ao atualizar material: {e}")
        db.session.rollback()
        return jsonify({
            'success': False,
            'message': 'Erro interno do servidor'
        }), 500

@materiais_bp.route('/api/materiais/<int:material_id>', methods=['DELETE'])
@login_required
def excluir_material(material_id):
    """API para excluir um material"""
    try:
        material = MaterialEstoque.query.filter_by(
            id=material_id,
            empresa=current_user.company
        ).first()
        
        if not material:
            return jsonify({
                'success': False,
                'message': 'Material não encontrado'
            }), 404
        
        # Em vez de excluir, marcar como inativo
        material.ativo = False
        db.session.commit()
        
        logger.info(f"Material desativado: {material.codigo} - {material.nome}")
        
        return jsonify({
            'success': True,
            'message': 'Material desativado com sucesso!'
        })
        
    except Exception as e:
        logger.error(f"Erro ao excluir material: {e}")
        db.session.rollback()
        return jsonify({
            'success': False,
            'message': 'Erro interno do servidor'
        }), 500

# Função para registrar o blueprint
def register_materiais_blueprint(app):
    """Registra o blueprint de materiais na aplicação"""
    app.register_blueprint(materiais_bp)
    logger.info("Blueprint de materiais registrado com sucesso")
