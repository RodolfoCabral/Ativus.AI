from flask import Blueprint, request, jsonify, session
from flask_login import current_user, login_required
from models import db
from datetime import datetime
import os

# Importação segura dos modelos de ativos
try:
    from assets_models import Chamado, Filial, Setor, Equipamento
    CHAMADOS_AVAILABLE = True
except ImportError as e:
    print(f"Erro ao importar modelos de chamados: {e}")
    CHAMADOS_AVAILABLE = False

chamados_bp = Blueprint('chamados', __name__)

def get_current_user():
    """Obtém informações do usuário atual da sessão"""
    if current_user.is_authenticated:
        return {
            'name': current_user.name or current_user.email.split('@')[0],
            'company': current_user.company or 'Empresa',
            'profile': current_user.profile or 'user'
        }
    else:
        return {
            'name': session.get('user_name', 'Usuário'),
            'company': session.get('user_company', 'Empresa'),
            'profile': session.get('user_profile', 'user')
        }

@chamados_bp.route('/api/chamados', methods=['POST'])
@login_required
def criar_chamado():
    data = request.get_json()
    print("Usuário autenticado:", current_user.email)
    """Criar um novo chamado"""
    if not CHAMADOS_AVAILABLE:
        return jsonify({'error': 'Funcionalidade de chamados não disponível'}), 503
    
    try:
        if not current_user.is_authenticated:
            return jsonify({'error': 'Usuário não autenticado'}), 401
        
        data = request.get_json()
        user_info = get_current_user()
        
        # Validar dados obrigatórios
        required_fields = ['descricao', 'filial_id', 'setor_id', 'equipamento_id', 'prioridade', 'solicitante']
        for field in required_fields:
            if not data.get(field):
                return jsonify({'error': f'Campo {field} é obrigatório'}), 400
        
        # Validar prioridade
        prioridades_validas = ['baixa', 'media', 'alta', 'seguranca']
        if data['prioridade'] not in prioridades_validas:
            return jsonify({'error': 'Prioridade inválida'}), 400
        
        # Verificar se filial, setor e equipamento existem e pertencem à empresa do usuário
        filial = Filial.query.filter_by(id=data['filial_id']).first()
        if not filial:
            return jsonify({'error': 'Filial não encontrada'}), 404
        
        setor = Setor.query.filter_by(id=data['setor_id'], filial_id=data['filial_id']).first()
        if not setor:
            return jsonify({'error': 'Setor não encontrado ou não pertence à filial selecionada'}), 404
        
        equipamento = Equipamento.query.filter_by(id=data['equipamento_id'], setor_id=data['setor_id']).first()
        if not equipamento:
            return jsonify({'error': 'Equipamento não encontrado ou não pertence ao setor selecionado'}), 404
        
        # Criar novo chamado
        novo_chamado = Chamado(
            descricao=data['descricao'],
            filial_id=data['filial_id'],
            setor_id=data['setor_id'],
            equipamento_id=data['equipamento_id'],
            prioridade=data['prioridade'],
            solicitante=data['solicitante'],
            empresa=user_info['company'],
            usuario_criacao=user_info['name']
        )
        
        db.session.add(novo_chamado)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Chamado criado com sucesso',
            'chamado': novo_chamado.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Erro interno do servidor: {str(e)}'}), 500

@chamados_bp.route('/api/chamados', methods=['GET'])
def listar_chamados():
    """Listar chamados da empresa do usuário"""
    if not CHAMADOS_AVAILABLE:
        return jsonify({'error': 'Funcionalidade de chamados não disponível'}), 503
    
    try:
        if not current_user.is_authenticated:
            return jsonify({'error': 'Usuário não autenticado'}), 401
        
        user_info = get_current_user()
        status = request.args.get('status', 'todos')
        
        query = Chamado.query.filter_by(empresa=user_info['company'])
        
        if status != 'todos':
            if status == 'abertos':
                chamados = Chamado.query.filter(Chamado.status.in_(['aberto', 'em_andamento', 'os_criada', 'os_programada'])).all()
            elif status == 'fechados':
                query = query.filter(Chamado.status.in_(['resolvido', 'fechado']))
            else:
                query = query.filter_by(status=status)
        
        chamados = query.order_by(Chamado.data_criacao.desc()).all()
        
        return jsonify({
            'success': True,
            'chamados': [chamado.to_dict() for chamado in chamados]
        })
        
    except Exception as e:
        return jsonify({'error': f'Erro interno do servidor: {str(e)}'}), 500

@chamados_bp.route('/api/chamados/<int:chamado_id>', methods=['GET'])
def obter_chamado(chamado_id):
    """Obter detalhes de um chamado específico"""
    if not CHAMADOS_AVAILABLE:
        return jsonify({'error': 'Funcionalidade de chamados não disponível'}), 503
    
    try:
        if not current_user.is_authenticated:
            return jsonify({'error': 'Usuário não autenticado'}), 401
        
        user_info = get_current_user()
        
        chamado = Chamado.query.filter_by(id=chamado_id).first()
        if not chamado:
            return jsonify({'error': 'Chamado não encontrado'}), 404
        
        return jsonify({
            'success': True,
            'chamado': chamado.to_dict()
        })
        
    except Exception as e:
        return jsonify({'error': f'Erro interno do servidor: {str(e)}'}), 500

@chamados_bp.route('/api/chamados/estatisticas', methods=['GET'])
def estatisticas_chamados():
    """Obter estatísticas dos chamados"""
    if not CHAMADOS_AVAILABLE:
        return jsonify({'error': 'Funcionalidade de chamados não disponível'}), 503
    
    try:
        if not current_user.is_authenticated:
            return jsonify({'error': 'Usuário não autenticado'}), 401
        
        user_info = get_current_user()
        
        # Contar chamados por status
        total = Chamado.query.filter_by(empresa=user_info['company']).count()
        abertos = Chamado.query.filter_by(empresa=user_info['company'], status='aberto').count()
        em_andamento = Chamado.query.filter_by(empresa=user_info['company'], status='em_andamento').count()
        resolvidos = Chamado.query.filter_by(empresa=user_info['company'], status='resolvido').count()
        fechados = Chamado.query.filter_by(empresa=user_info['company'], status='fechado').count()
        
        # Contar por prioridade
        alta_prioridade = Chamado.query.filter_by(empresa=user_info['company'], prioridade='alta').count()
        seguranca = Chamado.query.filter_by(empresa=user_info['company'], prioridade='seguranca').count()
        
        return jsonify({
            'success': True,
            'estatisticas': {
                'total': total,
                'abertos': abertos,
                'em_andamento': em_andamento,
                'resolvidos': resolvidos,
                'fechados': fechados,
                'alta_prioridade': alta_prioridade,
                'seguranca': seguranca
            }
        })
        
    except Exception as e:
        return jsonify({'error': f'Erro interno do servidor: {str(e)}'}), 500

