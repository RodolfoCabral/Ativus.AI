from flask import Blueprint, request, jsonify, session
from flask_login import current_user, login_required
from models import db
from datetime import datetime, date
import os

# Importação segura dos modelos
try:
    from assets_models import OrdemServico, Chamado, Filial, Setor, Equipamento
    OS_AVAILABLE = True
except ImportError as e:
    print(f"Erro ao importar modelos de OS: {e}")
    OS_AVAILABLE = False

ordens_servico_bp = Blueprint('ordens_servico', __name__)

def get_current_user():
    """Obtém informações do usuário atual da sessão"""
    return {
        'name': session.get('user_name', 'Usuário'),
        'company': session.get('user_company', 'Empresa'),
        'profile': session.get('user_profile', 'user')
    }

@ordens_servico_bp.route('/api/ordens-servico', methods=['POST'])
@login_required
def criar_ordem_servico():
    """Criar uma nova ordem de serviço"""
    if not OS_AVAILABLE:
        return jsonify({'error': 'Funcionalidade de OS não disponível'}), 503

    try:
        if not current_user.is_authenticated:
            return jsonify({'error': 'Usuário não autenticado'}), 401

        data = request.get_json()
        user_info = get_current_user()

        # Validar dados obrigatórios
        required_fields = ['descricao', 'tipo_manutencao', 'oficina', 'condicao_ativo',
                          'qtd_pessoas', 'horas', 'prioridade', 'filial_id', 'setor_id', 'equipamento_id']

        for field in required_fields:
            if field not in data or data[field] is None or data[field] == '':
                return jsonify({'error': f'Campo {field} é obrigatório'}), 400

        # Validar tipos de dados
        try:
            qtd_pessoas = int(data['qtd_pessoas'])
            horas = float(data['horas'])
            filial_id = int(data['filial_id'])
            setor_id = int(data['setor_id'])
            equipamento_id = int(data['equipamento_id'])
        except (ValueError, TypeError):
            return jsonify({'error': 'Dados numéricos inválidos'}), 400

        # Validar valores
        if qtd_pessoas < 1:
            return jsonify({'error': 'Quantidade de pessoas deve ser pelo menos 1'}), 400

        if horas < 0.5:
            return jsonify({'error': 'Horas deve ser pelo menos 0.5'}), 400

        # Validar enums
        tipos_manutencao_validos = ['corretiva', 'melhoria', 'setup', 'pmoc', 'inspecao', 'assistencia_tecnica']
        if data['tipo_manutencao'] not in tipos_manutencao_validos:
            return jsonify({'error': 'Tipo de manutenção inválido'}), 400

        oficinas_validas = ['mecanica', 'eletrica', 'automacao', 'eletromecanico', 'operacional']
        if data['oficina'] not in oficinas_validas:
            return jsonify({'error': 'Oficina inválida'}), 400

        condicoes_validas = ['parado', 'funcionando']
        if data['condicao_ativo'] not in condicoes_validas:
            return jsonify({'error': 'Condição do ativo inválida'}), 400

        prioridades_validas = ['baixa', 'media', 'alta', 'seguranca', 'preventiva']
        if data['prioridade'] not in prioridades_validas:
            return jsonify({'error': 'Prioridade inválida'}), 400

        # Verificar se filial, setor e equipamento existem e pertencem à empresa do usuário
        filial = Filial.query.filter_by(id=filial_id).first()
        if not filial:
            return jsonify({'error': 'Filial não encontrada'}), 404

        setor = Setor.query.filter_by(id=setor_id, filial_id=filial_id).first()
        if not setor:
            return jsonify({'error': 'Setor não encontrado ou não pertence à filial selecionada'}), 404

        equipamento = Equipamento.query.filter_by(id=equipamento_id, setor_id=setor_id).first()
        if not equipamento:
            return jsonify({'error': 'Equipamento não encontrado ou não pertence ao setor selecionado'}), 404

        # Verificar se o chamado existe (se fornecido)
        chamado_id = data.get('chamado_id')
        chamado = None
        if chamado_id:
            chamado = Chamado.query.filter_by(id=chamado_id).first()
            if not chamado:
                return jsonify({'error': 'Chamado não encontrado'}), 404

        # Calcular HH
        hh = qtd_pessoas * horas

        # Criar nova ordem de serviço
        nova_os = OrdemServico(
            chamado_id=chamado_id,
            descricao=data['descricao'],
            tipo_manutencao=data['tipo_manutencao'],
            oficina=data['oficina'],
            condicao_ativo=data['condicao_ativo'],
            qtd_pessoas=qtd_pessoas,
            horas=horas,
            hh=hh,
            prioridade=data['prioridade'],
            filial_id=filial_id,
            setor_id=setor_id,
            equipamento_id=equipamento_id,
            empresa=user_info['company'],
            usuario_criacao=user_info['name']
        )

        db.session.add(nova_os)

        # Atualizar status do chamado para "os_criada"
        if chamado:
            chamado.status = 'os_criada'

        db.session.commit()

        return jsonify({
            'success': True,
            'message': 'Ordem de Serviço criada com sucesso',
            'ordem_servico': nova_os.to_dict()
        }), 201

    except Exception as e:
        db.session.rollback()
        print(f"Erro ao criar OS: {e}")
        return jsonify({'error': f'Erro interno do servidor: {str(e)}'}), 500

@ordens_servico_bp.route('/api/ordens-servico', methods=['GET'])
@login_required
def listar_ordens_servico():
    if not OS_AVAILABLE:
        return jsonify({'error': 'Funcionalidade de OS não disponível'}), 503

    try:
        if not current_user.is_authenticated:
            return jsonify({'error': 'Usuário não autenticado'}), 401

        user_info = get_current_user()
        status = request.args.get('status', 'todos')
        prioridade = request.args.get('prioridade')

        query = OrdemServico.query.filter_by(empresa=user_info['company'])

        if status != 'todos':
            if status == 'abertas':
                query = query.filter(OrdemServico.status.in_(['aberta', 'programada']))
            elif status == 'em_andamento':
                query = query.filter_by(status='em_andamento')
            elif status == 'concluidas':
                query = query.filter(OrdemServico.status.in_(['concluida', 'cancelada']))
            else:
                query = query.filter_by(status=status)

        if prioridade:
            query = query.filter_by(prioridade=prioridade)

        ordens_servico = query.order_by(OrdemServico.data_criacao.desc()).all()

        return jsonify({
            'success': True,
            'ordens_servico': [os.to_dict() for os in ordens_servico]
        })

    except Exception as e:
        print(f"Erro ao listar OS: {e}")
        return jsonify({'error': f'Erro interno do servidor: {str(e)}'}), 500

@ordens_servico_bp.route('/api/ordens-servico/<int:os_id>', methods=['GET'])
@login_required
def obter_ordem_servico(os_id):
    if not OS_AVAILABLE:
        return jsonify({'error': 'Funcionalidade de OS não disponível'}), 503

    try:
        if not current_user.is_authenticated:
            return jsonify({'error': 'Usuário não autenticado'}), 401

        ordem_servico = OrdemServico.query.filter_by(id=os_id).first()
        if not ordem_servico:
            return jsonify({'error': 'Ordem de Serviço não encontrada'}), 404

        return jsonify({
            'success': True,
            'ordem_servico': ordem_servico.to_dict()
        })

    except Exception as e:
        print(f"Erro ao obter OS: {e}")
        return jsonify({'error': f'Erro interno do servidor: {str(e)}'}), 500

@ordens_servico_bp.route('/api/ordens-servico/<int:os_id>/programar', methods=['PUT'])
@login_required
def programar_ordem_servico(os_id):
    if not OS_AVAILABLE:
        return jsonify({'error': 'Funcionalidade de OS não disponível'}), 503

    try:
        if not current_user.is_authenticated:
            return jsonify({'error': 'Usuário não autenticado'}), 401

        data = request.get_json()

        if not data.get('data_programada') or not data.get('usuario_responsavel'):
            return jsonify({'error': 'Data programada e usuário responsável são obrigatórios'}), 400

        try:
            data_programada = datetime.strptime(data['data_programada'], '%Y-%m-%d').date()
        except ValueError:
            return jsonify({'error': 'Formato de data inválido. Use YYYY-MM-DD'}), 400

        ordem_servico = OrdemServico.query.filter_by(id=os_id).first()
        if not ordem_servico:
            return jsonify({'error': 'Ordem de Serviço não encontrada'}), 404

        ordem_servico.data_programada = data_programada
        ordem_servico.usuario_responsavel = str(data['usuario_responsavel'])
        ordem_servico.status = 'programada'
        ordem_servico.data_atualizacao = datetime.utcnow()

        # Atualizar status do chamado, se houver
        if ordem_servico.chamado_id:
            chamado = Chamado.query.filter_by(id=ordem_servico.chamado_id).first()
            if chamado:
                chamado.status = 'os_programada'

        db.session.commit()

        return jsonify({
            'success': True,
            'message': 'Ordem de Serviço programada com sucesso',
            'ordem_servico': ordem_servico.to_dict()
        })

    except Exception as e:
        db.session.rollback()
        print(f"Erro ao programar OS: {e}")
        return jsonify({'error': f'Erro interno do servidor: {str(e)}'}), 500

@ordens_servico_bp.route('/api/ordens-servico/estatisticas', methods=['GET'])
@login_required
def estatisticas_ordens_servico():
    if not OS_AVAILABLE:
        return jsonify({'error': 'Funcionalidade de OS não disponível'}), 503

    try:
        if not current_user.is_authenticated:
            return jsonify({'error': 'Usuário não autenticado'}), 401

        user_info = get_current_user()

        total = OrdemServico.query.filter_by(empresa=user_info['company']).count()
        abertas = OrdemServico.query.filter_by(empresa=user_info['company'], status='aberta').count()
        programadas = OrdemServico.query.filter_by(empresa=user_info['company'], status='programada').count()
        em_andamento = OrdemServico.query.filter_by(empresa=user_info['company'], status='em_andamento').count()
        concluidas = OrdemServico.query.filter_by(empresa=user_info['company'], status='concluida').count()

        alta_prioridade = OrdemServico.query.filter_by(empresa=user_info['company'], prioridade='alta').count()
        seguranca = OrdemServico.query.filter_by(empresa=user_info['company'], prioridade='seguranca').count()
        preventivas = OrdemServico.query.filter_by(empresa=user_info['company'], prioridade='preventiva').count()

        return jsonify({
            'success': True,
            'estatisticas': {
                'total': total,
                'abertas': abertas,
                'programadas': programadas,
                'em_andamento': em_andamento,
                'concluidas': concluidas,
                'alta_prioridade': alta_prioridade,
                'seguranca': seguranca,
                'preventivas': preventivas
            }
        })

    except Exception as e:
        print(f"Erro ao obter estatísticas de OS: {e}")
        return jsonify({'error': f'Erro interno do servidor: {str(e)}'}), 500
