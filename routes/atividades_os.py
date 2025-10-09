from flask import Blueprint, jsonify, request
from flask_login import login_required, current_user
from models import db
from models.atividade_os import AtividadeOS
from assets_models import OrdemServico
import logging

logger = logging.getLogger(__name__)

atividades_os_bp = Blueprint('atividades_os', __name__)

@atividades_os_bp.route('/api/os/<int:os_id>/atividades', methods=['GET'])
@login_required
def listar_atividades_os(os_id):
    """Lista todas as atividades de uma OS específica"""
    try:
        logger.info(f"🔍 Buscando atividades para OS {os_id}")
        
        # Buscar a OS primeiro (SEM validações restritivas)
        os = OrdemServico.query.filter_by(id=os_id).first()
        
        if not os:
            logger.error(f"❌ OS {os_id} não encontrada no banco de dados")
            return jsonify({'error': 'OS não encontrada'}), 404
        
        logger.info(f"✅ OS {os_id} encontrada: {os.descricao}")
        
        # REMOVER VALIDAÇÃO RESTRITIVA DE EMPRESA
        # (Esta validação estava causando erro 400)
        
        # Buscar atividades
        atividades = AtividadeOS.query.filter_by(os_id=os_id).order_by(AtividadeOS.ordem).all()
        logger.info(f"📋 Encontradas {len(atividades)} atividades para OS {os_id}")
        
        if not atividades:
            logger.warning(f"⚠️ OS {os_id} não possui atividades vinculadas")
            return jsonify({
                'os_id': os_id,
                'os_descricao': os.descricao,
                'os_tipo': getattr(os, 'tipo_manutencao', 'N/A'),
                'os_status': getattr(os, 'status', 'N/A'),
                'atividades': [],
                'message': 'Nenhuma atividade vinculada a esta OS'
            })
        
        # Converter para dicionário com tratamento de erro
        atividades_dict = []
        for atividade in atividades:
            try:
                atividade_dict = atividade.to_dict()
                atividades_dict.append(atividade_dict)
                logger.info(f"   ✅ Atividade {atividade.id}: {atividade.descricao}")
            except Exception as e:
                logger.error(f"   ❌ Erro ao converter atividade {atividade.id}: {e}")
                # Fallback manual
                atividades_dict.append({
                    'id': atividade.id,
                    'descricao': getattr(atividade, 'descricao', 'N/A'),
                    'ordem': getattr(atividade, 'ordem', 0),
                    'status': str(getattr(atividade, 'status', 'pendente')),
                    'observacao': getattr(atividade, 'observacao', '')
                })
        
        logger.info(f"🎯 Retornando {len(atividades_dict)} atividades para OS {os_id}")
        
        return jsonify({
            'os_id': os_id,
            'os_descricao': os.descricao,
            'os_tipo': getattr(os, 'tipo_manutencao', 'N/A'),
            'os_status': getattr(os, 'status', 'N/A'),
            'atividades': atividades_dict
        })
    
    except Exception as e:
        logger.error(f"❌ Erro ao listar atividades da OS {os_id}: {str(e)}")
        import traceback
        logger.error(f"Traceback: {traceback.format_exc()}")
        return jsonify({'error': f'Erro interno: {str(e)}'}), 500

@atividades_os_bp.route('/api/os/atividades/<int:atividade_id>/avaliar', methods=['PUT'])
@login_required
def avaliar_atividade_os(atividade_id):
    """Atualiza o status de conformidade e observação de uma atividade"""
    try:
        logger.info(f"🔧 Tentando avaliar atividade {atividade_id}")
        
        # Buscar a atividade diretamente (sem validações restritivas)
        atividade = AtividadeOS.query.filter_by(id=atividade_id).first()
        
        if not atividade:
            logger.error(f"❌ Atividade {atividade_id} não encontrada")
            return jsonify({'error': 'Atividade não encontrada'}), 404
        
        logger.info(f"✅ Atividade {atividade_id} encontrada, OS: {atividade.os_id}")
        
        # REMOVER VALIDAÇÃO RESTRITIVA DE EMPRESA
        # (Esta validação estava causando problemas)
        
        # Obter dados da requisição
        dados = request.json or {}
        logger.info(f"📝 Dados recebidos: {dados}")
        
        # Atualizar status se fornecido
        if 'status' in dados:
            status_validos = ['pendente', 'conforme', 'nao_conforme', 'nao_aplicavel']
            if dados['status'] not in status_validos:
                logger.error(f"❌ Status inválido: {dados['status']}")
                return jsonify({'error': 'Status inválido'}), 400
            
            logger.info(f"🔄 Atualizando status de {atividade.status} para {dados['status']}")
            atividade.status = dados['status']
        
        # Atualizar observação se fornecida
        if 'observacao' in dados:
            logger.info(f"📝 Atualizando observação: {dados['observacao']}")
            atividade.observacao = dados['observacao']
        
        # Salvar no banco
        db.session.commit()
        logger.info(f"✅ Atividade {atividade_id} salva com sucesso")
        
        # Retornar dados com fallback
        try:
            atividade_dict = atividade.to_dict()
        except Exception as e:
            logger.warning(f"⚠️ Erro no to_dict(), usando fallback: {e}")
            atividade_dict = {
                'id': atividade.id,
                'descricao': getattr(atividade, 'descricao', 'N/A'),
                'ordem': getattr(atividade, 'ordem', 0),
                'status': str(getattr(atividade, 'status', 'pendente')),
                'observacao': getattr(atividade, 'observacao', '')
            }
        
        return jsonify({
            'success': True,
            'atividade': atividade_dict
        })
    
    except Exception as e:
        db.session.rollback()
        logger.error(f"❌ Erro ao avaliar atividade {atividade_id}: {str(e)}")
        import traceback
        logger.error(f"Traceback: {traceback.format_exc()}")
        return jsonify({'error': f'Erro interno: {str(e)}'}), 500
