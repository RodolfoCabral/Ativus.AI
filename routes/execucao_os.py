from flask import Blueprint, request, jsonify, session
from assets_models import ExecucaoOS, MaterialUtilizado, MaterialEstoque, OrdemServico, Chamado
from models import db
from datetime import datetime
import os

execucao_bp = Blueprint('execucao', __name__)

def verificar_autenticacao():
    """Verifica se o usuário está autenticado"""
    if 'user_id' not in session:
        return False, {'error': 'Usuário não autenticado'}, 401
    return True, None, None

def obter_dados_usuario():
    """Obtém dados do usuário da sessão"""
    return {
        'user_id': session.get('user_id'),
        'username': session.get('username'),
        'empresa': session.get('empresa'),
        'user_type': session.get('user_type')
    }

@execucao_bp.route('/api/execucoes-os', methods=['POST'])
def criar_execucao():
    """Criar nova execução de OS"""
    try:
        # Verificar autenticação
        auth_ok, error_response, status_code = verificar_autenticacao()
        if not auth_ok:
            return jsonify(error_response), status_code
        
        user_data = obter_dados_usuario()
        data = request.get_json()
        
        # Validar dados obrigatórios
        if not data.get('os_id'):
            return jsonify({'error': 'ID da OS é obrigatório'}), 400
        
        # Verificar se a OS existe e pertence à empresa do usuário
        os = OrdemServico.query.filter_by(
            id=data['os_id'],
            empresa=user_data['empresa']
        ).first()
        
        if not os:
            return jsonify({'error': 'Ordem de serviço não encontrada'}), 404
        
        # Verificar se já existe execução para esta OS
        execucao_existente = ExecucaoOS.query.filter_by(os_id=data['os_id']).first()
        if execucao_existente:
            return jsonify({'error': 'Já existe uma execução para esta OS'}), 400
        
        # Criar nova execução
        execucao = ExecucaoOS(
            os_id=data['os_id'],
            data_inicio=datetime.fromisoformat(data['data_inicio'].replace('Z', '+00:00')) if data.get('data_inicio') else None,
            data_fim=datetime.fromisoformat(data['data_fim'].replace('Z', '+00:00')) if data.get('data_fim') else None,
            lista_execucao_status=data.get('lista_execucao_status', 'C'),
            observacoes=data.get('observacoes'),
            executor=user_data['username'],
            empresa=user_data['empresa']
        )
        
        db.session.add(execucao)
        
        # Atualizar status da OS para "em_andamento"
        os.status = 'em_andamento'
        os.data_inicio = execucao.data_inicio
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Execução criada com sucesso',
            'execucao': execucao.to_dict()
        })
        
    except Exception as e:
        db.session.rollback()
        print(f"Erro ao criar execução: {str(e)}")
        return jsonify({'error': 'Erro interno do servidor'}), 500

@execucao_bp.route('/api/execucoes-os/<int:execucao_id>', methods=['PUT'])
def atualizar_execucao(execucao_id):
    """Atualizar execução existente"""
    try:
        # Verificar autenticação
        auth_ok, error_response, status_code = verificar_autenticacao()
        if not auth_ok:
            return jsonify(error_response), status_code
        
        user_data = obter_dados_usuario()
        data = request.get_json()
        
        # Buscar execução
        execucao = ExecucaoOS.query.filter_by(
            id=execucao_id,
            empresa=user_data['empresa']
        ).first()
        
        if not execucao:
            return jsonify({'error': 'Execução não encontrada'}), 404
        
        # Atualizar dados
        if 'data_inicio' in data:
            execucao.data_inicio = datetime.fromisoformat(data['data_inicio'].replace('Z', '+00:00')) if data['data_inicio'] else None
        
        if 'data_fim' in data:
            execucao.data_fim = datetime.fromisoformat(data['data_fim'].replace('Z', '+00:00')) if data['data_fim'] else None
        
        if 'lista_execucao_status' in data:
            execucao.lista_execucao_status = data['lista_execucao_status']
        
        if 'observacoes' in data:
            execucao.observacoes = data['observacoes']
        
        # Atualizar OS relacionada
        os = execucao.ordem_servico
        if execucao.data_inicio:
            os.data_inicio = execucao.data_inicio
        if execucao.data_fim:
            os.data_conclusao = execucao.data_fim
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Execução atualizada com sucesso',
            'execucao': execucao.to_dict()
        })
        
    except Exception as e:
        db.session.rollback()
        print(f"Erro ao atualizar execução: {str(e)}")
        return jsonify({'error': 'Erro interno do servidor'}), 500

@execucao_bp.route('/api/execucoes-os/por-os/<int:os_id>', methods=['GET'])
def obter_execucao_por_os(os_id):
    """Obter execução por ID da OS"""
    try:
        # Verificar autenticação
        auth_ok, error_response, status_code = verificar_autenticacao()
        if not auth_ok:
            return jsonify(error_response), status_code
        
        user_data = obter_dados_usuario()
        
        # Buscar execução
        execucao = ExecucaoOS.query.join(OrdemServico).filter(
            ExecucaoOS.os_id == os_id,
            OrdemServico.empresa == user_data['empresa']
        ).first()
        
        if execucao:
            return jsonify({
                'success': True,
                'execucao': execucao.to_dict()
            })
        else:
            return jsonify({
                'success': True,
                'execucao': None
            })
        
    except Exception as e:
        print(f"Erro ao buscar execução: {str(e)}")
        return jsonify({'error': 'Erro interno do servidor'}), 500

@execucao_bp.route('/api/materiais-estoque', methods=['GET'])
def listar_materiais_estoque():
    """Listar materiais de estoque da empresa"""
    try:
        # Verificar autenticação
        auth_ok, error_response, status_code = verificar_autenticacao()
        if not auth_ok:
            return jsonify(error_response), status_code
        
        user_data = obter_dados_usuario()
        
        # Buscar materiais ativos da empresa
        materiais = MaterialEstoque.query.filter_by(
            empresa=user_data['empresa'],
            ativo=True
        ).order_by(MaterialEstoque.nome).all()
        
        return jsonify({
            'success': True,
            'materiais': [material.to_dict() for material in materiais]
        })
        
    except Exception as e:
        print(f"Erro ao listar materiais de estoque: {str(e)}")
        return jsonify({'error': 'Erro interno do servidor'}), 500

@execucao_bp.route('/api/materiais-utilizados', methods=['POST'])
def criar_material_utilizado():
    """Criar registro de material utilizado"""
    try:
        # Verificar autenticação
        auth_ok, error_response, status_code = verificar_autenticacao()
        if not auth_ok:
            return jsonify(error_response), status_code
        
        user_data = obter_dados_usuario()
        data = request.get_json()
        
        # Validar dados obrigatórios
        if not data.get('execucao_id') or not data.get('quantidade'):
            return jsonify({'error': 'Execução ID e quantidade são obrigatórios'}), 400
        
        # Verificar se a execução existe e pertence à empresa
        execucao = ExecucaoOS.query.join(OrdemServico).filter(
            ExecucaoOS.id == data['execucao_id'],
            OrdemServico.empresa == user_data['empresa']
        ).first()
        
        if not execucao:
            return jsonify({'error': 'Execução não encontrada'}), 404
        
        # Criar material utilizado
        material = MaterialUtilizado(
            execucao_id=data['execucao_id'],
            tipo_material=data.get('tipo_material', 'estoque'),
            quantidade=float(data['quantidade']),
            empresa=user_data['empresa'],
            usuario_criacao=user_data['username']
        )
        
        if data.get('tipo_material') == 'estoque':
            material.material_estoque_id = data.get('material_estoque_id')
            # Buscar valor unitário do material de estoque
            material_estoque = MaterialEstoque.query.get(data.get('material_estoque_id'))
            if material_estoque:
                material.valor_unitario = material_estoque.valor_unitario
        else:
            material.nome_material = data.get('nome_material')
            material.valor_unitario = float(data.get('valor_unitario', 0))
        
        # Calcular valor total
        material.calcular_valor_total()
        
        db.session.add(material)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Material registrado com sucesso',
            'material': material.to_dict()
        })
        
    except Exception as e:
        db.session.rollback()
        print(f"Erro ao criar material utilizado: {str(e)}")
        return jsonify({'error': 'Erro interno do servidor'}), 500

@execucao_bp.route('/api/materiais-utilizados/<int:material_id>', methods=['PUT'])
def atualizar_material_utilizado(material_id):
    """Atualizar material utilizado"""
    try:
        # Verificar autenticação
        auth_ok, error_response, status_code = verificar_autenticacao()
        if not auth_ok:
            return jsonify(error_response), status_code
        
        user_data = obter_dados_usuario()
        data = request.get_json()
        
        # Buscar material
        material = MaterialUtilizado.query.filter_by(
            id=material_id,
            empresa=user_data['empresa']
        ).first()
        
        if not material:
            return jsonify({'error': 'Material não encontrado'}), 404
        
        # Atualizar dados
        if 'quantidade' in data:
            material.quantidade = float(data['quantidade'])
        
        if 'tipo_material' in data:
            material.tipo_material = data['tipo_material']
        
        if data.get('tipo_material') == 'estoque':
            if 'material_estoque_id' in data:
                material.material_estoque_id = data['material_estoque_id']
                # Atualizar valor unitário
                material_estoque = MaterialEstoque.query.get(data['material_estoque_id'])
                if material_estoque:
                    material.valor_unitario = material_estoque.valor_unitario
        else:
            if 'nome_material' in data:
                material.nome_material = data['nome_material']
            if 'valor_unitario' in data:
                material.valor_unitario = float(data['valor_unitario'])
        
        # Recalcular valor total
        material.calcular_valor_total()
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Material atualizado com sucesso',
            'material': material.to_dict()
        })
        
    except Exception as e:
        db.session.rollback()
        print(f"Erro ao atualizar material: {str(e)}")
        return jsonify({'error': 'Erro interno do servidor'}), 500

@execucao_bp.route('/api/materiais-utilizados/por-execucao/<int:execucao_id>', methods=['GET'])
def listar_materiais_por_execucao(execucao_id):
    """Listar materiais utilizados por execução"""
    try:
        # Verificar autenticação
        auth_ok, error_response, status_code = verificar_autenticacao()
        if not auth_ok:
            return jsonify(error_response), status_code
        
        user_data = obter_dados_usuario()
        
        # Buscar materiais
        materiais = MaterialUtilizado.query.join(ExecucaoOS).join(OrdemServico).filter(
            MaterialUtilizado.execucao_id == execucao_id,
            OrdemServico.empresa == user_data['empresa']
        ).all()
        
        return jsonify({
            'success': True,
            'materiais': [material.to_dict() for material in materiais]
        })
        
    except Exception as e:
        print(f"Erro ao listar materiais por execução: {str(e)}")
        return jsonify({'error': 'Erro interno do servidor'}), 500

@execucao_bp.route('/api/ordens-servico/<int:os_id>/encerrar', methods=['POST'])
def encerrar_os(os_id):
    """Encerrar ordem de serviço"""
    try:
        # Verificar autenticação
        auth_ok, error_response, status_code = verificar_autenticacao()
        if not auth_ok:
            return jsonify(error_response), status_code
        
        user_data = obter_dados_usuario()
        
        # Buscar OS
        os = OrdemServico.query.filter_by(
            id=os_id,
            empresa=user_data['empresa']
        ).first()
        
        if not os:
            return jsonify({'error': 'Ordem de serviço não encontrada'}), 404
        
        # Atualizar status da OS
        os.status = 'concluida'
        if not os.data_conclusao:
            os.data_conclusao = datetime.utcnow()
        
        # Atualizar status do chamado relacionado (se houver)
        if os.chamado_origem:
            os.chamado_origem.status = 'concluido'
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Ordem de serviço encerrada com sucesso'
        })
        
    except Exception as e:
        db.session.rollback()
        print(f"Erro ao encerrar OS: {str(e)}")
        return jsonify({'error': 'Erro interno do servidor'}), 500

