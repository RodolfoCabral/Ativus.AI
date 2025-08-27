from flask import Blueprint, request, jsonify, current_app
from models.pmp_limpo import PMP, AtividadePMP
from models import db
import logging

pmp_atualizar_bp = Blueprint('pmp_atualizar_bp', __name__)

@pmp_atualizar_bp.route('/api/pmp/<int:pmp_id>/atualizar', methods=['PUT'])
def atualizar_pmp(pmp_id):
    """
    Atualiza uma PMP existente com novos dados.
    """
    try:
        data = request.get_json()
        if not data:
            return jsonify({
                'success': False,
                'message': 'Dados não fornecidos'
            }), 400
        
        # Buscar PMP existente
        pmp = PMP.query.get(pmp_id)
        if not pmp:
            return jsonify({
                'success': False,
                'message': 'PMP não encontrada'
            }), 404
        
        current_app.logger.info(f"🔧 Atualizando PMP {pmp_id}: {pmp.codigo}")
        
        # Atualizar campos da PMP
        if 'descricao' in data:
            pmp.descricao = data['descricao']
        if 'tipo' in data:
            pmp.tipo = data['tipo']
        if 'oficina' in data:
            pmp.oficina = data['oficina']
        if 'frequencia' in data:
            pmp.frequencia = data['frequencia']
        if 'condicao' in data:
            pmp.condicao = data['condicao']
        if 'num_pessoas' in data:
            pmp.num_pessoas = data['num_pessoas']
        if 'dias_antecipacao' in data:
            pmp.dias_antecipacao = data['dias_antecipacao']
        if 'tempo_pessoa' in data:
            pmp.tempo_pessoa = data['tempo_pessoa']
        if 'forma_impressao' in data:
            pmp.forma_impressao = data['forma_impressao']
        if 'dias_semana' in data:
            import json
            pmp.dias_semana = json.dumps(data['dias_semana'])
        if 'status' in data:
            pmp.status = data['status']
        
        # Salvar alterações
        db.session.commit()
        
        current_app.logger.info(f"✅ PMP {pmp_id} atualizada com sucesso")
        
        # Retornar PMP atualizada
        pmp_dict = pmp.to_dict()
        pmp_dict['atividades_count'] = AtividadePMP.query.filter_by(pmp_id=pmp.id).count()
        
        return jsonify({
            'success': True,
            'message': 'PMP atualizada com sucesso',
            'pmp': pmp_dict
        }), 200
        
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"❌ Erro ao atualizar PMP {pmp_id}: {e}", exc_info=True)
        return jsonify({
            'success': False,
            'message': f'Erro interno: {str(e)}'
        }), 500

@pmp_atualizar_bp.route('/api/pmp/<int:pmp_id>/atividade/<int:atividade_id>/atualizar', methods=['PUT'])
def atualizar_atividade_pmp(pmp_id, atividade_id):
    """
    Atualiza uma atividade específica de uma PMP.
    """
    try:
        data = request.get_json()
        if not data:
            return jsonify({
                'success': False,
                'message': 'Dados não fornecidos'
            }), 400
        
        # Buscar atividade existente
        atividade = AtividadePMP.query.filter_by(id=atividade_id, pmp_id=pmp_id).first()
        if not atividade:
            return jsonify({
                'success': False,
                'message': 'Atividade não encontrada'
            }), 404
        
        current_app.logger.info(f"🔧 Atualizando atividade {atividade_id} da PMP {pmp_id}")
        
        # Atualizar campos da atividade
        if 'descricao' in data:
            atividade.descricao = data['descricao']
        if 'oficina' in data:
            atividade.oficina = data['oficina']
        if 'frequencia' in data:
            atividade.frequencia = data['frequencia']
        if 'tipo_manutencao' in data:
            atividade.tipo_manutencao = data['tipo_manutencao']
        if 'conjunto' in data:
            atividade.conjunto = data['conjunto']
        if 'ponto_controle' in data:
            atividade.ponto_controle = data['ponto_controle']
        if 'valor_frequencia' in data:
            atividade.valor_frequencia = data['valor_frequencia']
        if 'condicao' in data:
            atividade.condicao = data['condicao']
        if 'ordem' in data:
            atividade.ordem = data['ordem']
        if 'status' in data:
            atividade.status = data['status']
        
        # Salvar alterações
        db.session.commit()
        
        current_app.logger.info(f"✅ Atividade {atividade_id} atualizada com sucesso")
        
        return jsonify({
            'success': True,
            'message': 'Atividade atualizada com sucesso',
            'atividade': atividade.to_dict()
        }), 200
        
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"❌ Erro ao atualizar atividade {atividade_id}: {e}", exc_info=True)
        return jsonify({
            'success': False,
            'message': f'Erro interno: {str(e)}'
        }), 500

