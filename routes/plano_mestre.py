# Rotas para Plano Mestre
from flask import Blueprint, request, jsonify, session
from flask_login import login_required, current_user
from models import db
from models.plano_mestre import PlanoMestre, AtividadePlanoMestre, HistoricoExecucaoPlano
from datetime import datetime
import logging

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

plano_mestre_bp = Blueprint('plano_mestre', __name__, url_prefix='/api/plano-mestre')

@plano_mestre_bp.route('/equipamento/<int:equipamento_id>', methods=['GET'])
@login_required
def obter_plano_mestre(equipamento_id):
    """Obter plano mestre de um equipamento específico"""
    try:
        logger.info(f"Buscando plano mestre para equipamento {equipamento_id}")
        
        plano = PlanoMestre.query.filter_by(equipamento_id=equipamento_id).first()
        
        if not plano:
            # Se não existe plano mestre, criar um novo
            plano = PlanoMestre(
                equipamento_id=equipamento_id,
                nome=f"Plano Mestre - Equipamento {equipamento_id}",
                descricao="Plano mestre criado automaticamente",
                criado_por=current_user.id
            )
            db.session.add(plano)
            db.session.commit()
            logger.info(f"Novo plano mestre criado para equipamento {equipamento_id}")
        
        # Buscar atividades do plano
        atividades = AtividadePlanoMestre.query.filter_by(
            plano_mestre_id=plano.id
        ).order_by(AtividadePlanoMestre.ordem, AtividadePlanoMestre.criado_em).all()
        
        resultado = {
            'plano_mestre': plano.to_dict(),
            'atividades': [atividade.to_dict() for atividade in atividades]
        }
        
        return jsonify(resultado), 200
        
    except Exception as e:
        logger.error(f"Erro ao obter plano mestre: {str(e)}")
        return jsonify({'error': 'Erro interno do servidor'}), 500

@plano_mestre_bp.route('/equipamento/<int:equipamento_id>/atividades', methods=['POST'])
@login_required
def criar_atividade(equipamento_id):
    """Criar nova atividade no plano mestre"""
    try:
        data = request.get_json()
        logger.info(f"Criando atividade para equipamento {equipamento_id}: {data}")
        
        # Validar dados obrigatórios
        if not data.get('descricao'):
            return jsonify({'error': 'Descrição é obrigatória'}), 400
        
        # Buscar ou criar plano mestre
        plano = PlanoMestre.query.filter_by(equipamento_id=equipamento_id).first()
        if not plano:
            plano = PlanoMestre(
                equipamento_id=equipamento_id,
                nome=f"Plano Mestre - Equipamento {equipamento_id}",
                descricao="Plano mestre criado automaticamente",
                criado_por=current_user.id
            )
            db.session.add(plano)
            db.session.flush()  # Para obter o ID
        
        # Determinar próxima ordem
        ultima_ordem = db.session.query(db.func.max(AtividadePlanoMestre.ordem)).filter_by(
            plano_mestre_id=plano.id
        ).scalar() or 0
        
        # Criar nova atividade
        atividade = AtividadePlanoMestre(
            plano_mestre_id=plano.id,
            descricao=data['descricao'],
            oficina=data.get('oficina'),
            tipo_manutencao=data.get('tipo_manutencao'),
            frequencia=data.get('frequencia'),
            conjunto=data.get('conjunto'),
            ponto_controle=data.get('ponto_controle'),
            valor_frequencia=data.get('valor_frequencia'),
            condicao=data.get('condicao'),
            status_ativo=data.get('status_ativo', True),
            criado_por=current_user.id,
            ordem=ultima_ordem + 1
        )
        
        db.session.add(atividade)
        db.session.commit()
        
        logger.info(f"Atividade criada com sucesso: ID {atividade.id}")
        return jsonify(atividade.to_dict()), 201
        
    except Exception as e:
        db.session.rollback()
        logger.error(f"Erro ao criar atividade: {str(e)}")
        return jsonify({'error': 'Erro interno do servidor'}), 500

@plano_mestre_bp.route('/atividade/<int:atividade_id>', methods=['PUT'])
@login_required
def atualizar_atividade(atividade_id):
    """Atualizar atividade existente"""
    try:
        data = request.get_json()
        logger.info(f"Atualizando atividade {atividade_id}: {data}")
        
        atividade = AtividadePlanoMestre.query.get_or_404(atividade_id)
        
        # Validar dados obrigatórios
        if not data.get('descricao'):
            return jsonify({'error': 'Descrição é obrigatória'}), 400
        
        # Atualizar campos
        atividade.descricao = data['descricao']
        atividade.oficina = data.get('oficina')
        atividade.tipo_manutencao = data.get('tipo_manutencao')
        atividade.frequencia = data.get('frequencia')
        atividade.conjunto = data.get('conjunto')
        atividade.ponto_controle = data.get('ponto_controle')
        atividade.valor_frequencia = data.get('valor_frequencia')
        atividade.condicao = data.get('condicao')
        atividade.status_ativo = data.get('status_ativo', True)
        atividade.atualizado_em = datetime.utcnow()
        
        db.session.commit()
        
        logger.info(f"Atividade {atividade_id} atualizada com sucesso")
        return jsonify(atividade.to_dict()), 200
        
    except Exception as e:
        db.session.rollback()
        logger.error(f"Erro ao atualizar atividade: {str(e)}")
        return jsonify({'error': 'Erro interno do servidor'}), 500

@plano_mestre_bp.route('/atividade/<int:atividade_id>', methods=['DELETE'])
@login_required
def excluir_atividade(atividade_id):
    """Excluir atividade"""
    try:
        logger.info(f"Excluindo atividade {atividade_id}")
        
        atividade = AtividadePlanoMestre.query.get_or_404(atividade_id)
        
        db.session.delete(atividade)
        db.session.commit()
        
        logger.info(f"Atividade {atividade_id} excluída com sucesso")
        return jsonify({'message': 'Atividade excluída com sucesso'}), 200
        
    except Exception as e:
        db.session.rollback()
        logger.error(f"Erro ao excluir atividade: {str(e)}")
        return jsonify({'error': 'Erro interno do servidor'}), 500

@plano_mestre_bp.route('/atividade/<int:atividade_id>/copiar', methods=['POST'])
@login_required
def copiar_atividade(atividade_id):
    """Copiar atividade existente"""
    try:
        logger.info(f"Copiando atividade {atividade_id}")
        
        atividade_original = AtividadePlanoMestre.query.get_or_404(atividade_id)
        
        # Determinar próxima ordem
        ultima_ordem = db.session.query(db.func.max(AtividadePlanoMestre.ordem)).filter_by(
            plano_mestre_id=atividade_original.plano_mestre_id
        ).scalar() or 0
        
        # Criar cópia
        nova_atividade = AtividadePlanoMestre(
            plano_mestre_id=atividade_original.plano_mestre_id,
            descricao=f"{atividade_original.descricao} (Cópia)",
            oficina=atividade_original.oficina,
            tipo_manutencao=atividade_original.tipo_manutencao,
            frequencia=atividade_original.frequencia,
            conjunto=atividade_original.conjunto,
            ponto_controle=atividade_original.ponto_controle,
            valor_frequencia=atividade_original.valor_frequencia,
            condicao=atividade_original.condicao,
            status_ativo=atividade_original.status_ativo,
            criado_por=current_user.id,
            ordem=ultima_ordem + 1
        )
        
        db.session.add(nova_atividade)
        db.session.commit()
        
        logger.info(f"Atividade copiada com sucesso: ID {nova_atividade.id}")
        return jsonify(nova_atividade.to_dict()), 201
        
    except Exception as e:
        db.session.rollback()
        logger.error(f"Erro ao copiar atividade: {str(e)}")
        return jsonify({'error': 'Erro interno do servidor'}), 500

@plano_mestre_bp.route('/atividade/<int:atividade_id>/toggle', methods=['POST'])
@login_required
def toggle_atividade(atividade_id):
    """Marcar/desmarcar atividade como concluída"""
    try:
        data = request.get_json()
        logger.info(f"Toggle atividade {atividade_id}: {data}")
        
        atividade = AtividadePlanoMestre.query.get_or_404(atividade_id)
        
        if data.get('concluida'):
            atividade.marcar_concluida(data.get('observacoes'))
            
            # Registrar no histórico
            historico = HistoricoExecucaoPlano(
                plano_mestre_id=atividade.plano_mestre_id,
                atividade_id=atividade.id,
                executado_por=current_user.id,
                status_execucao='concluida',
                observacoes=data.get('observacoes')
            )
            db.session.add(historico)
        else:
            atividade.desmarcar_concluida()
        
        db.session.commit()
        
        logger.info(f"Atividade {atividade_id} toggle realizado com sucesso")
        return jsonify(atividade.to_dict()), 200
        
    except Exception as e:
        db.session.rollback()
        logger.error(f"Erro ao fazer toggle da atividade: {str(e)}")
        return jsonify({'error': 'Erro interno do servidor'}), 500

@plano_mestre_bp.route('/equipamento/<int:equipamento_id>/historico', methods=['GET'])
@login_required
def obter_historico(equipamento_id):
    """Obter histórico de execuções do plano mestre"""
    try:
        logger.info(f"Buscando histórico para equipamento {equipamento_id}")
        
        plano = PlanoMestre.query.filter_by(equipamento_id=equipamento_id).first()
        if not plano:
            return jsonify({'historico': []}), 200
        
        historico = HistoricoExecucaoPlano.query.filter_by(
            plano_mestre_id=plano.id
        ).order_by(HistoricoExecucaoPlano.data_execucao.desc()).all()
        
        resultado = [item.to_dict() for item in historico]
        
        return jsonify({'historico': resultado}), 200
        
    except Exception as e:
        logger.error(f"Erro ao obter histórico: {str(e)}")
        return jsonify({'error': 'Erro interno do servidor'}), 500

@plano_mestre_bp.route('/equipamento/<int:equipamento_id>/estatisticas', methods=['GET'])
@login_required
def obter_estatisticas(equipamento_id):
    """Obter estatísticas do plano mestre"""
    try:
        logger.info(f"Buscando estatísticas para equipamento {equipamento_id}")
        
        plano = PlanoMestre.query.filter_by(equipamento_id=equipamento_id).first()
        if not plano:
            return jsonify({
                'total_atividades': 0,
                'atividades_concluidas': 0,
                'atividades_pendentes': 0,
                'percentual_conclusao': 0
            }), 200
        
        total_atividades = AtividadePlanoMestre.query.filter_by(plano_mestre_id=plano.id).count()
        atividades_concluidas = AtividadePlanoMestre.query.filter_by(
            plano_mestre_id=plano.id, concluida=True
        ).count()
        atividades_pendentes = total_atividades - atividades_concluidas
        percentual_conclusao = (atividades_concluidas / total_atividades * 100) if total_atividades > 0 else 0
        
        estatisticas = {
            'total_atividades': total_atividades,
            'atividades_concluidas': atividades_concluidas,
            'atividades_pendentes': atividades_pendentes,
            'percentual_conclusao': round(percentual_conclusao, 2)
        }
        
        return jsonify(estatisticas), 200
        
    except Exception as e:
        logger.error(f"Erro ao obter estatísticas: {str(e)}")
        return jsonify({'error': 'Erro interno do servidor'}), 500

