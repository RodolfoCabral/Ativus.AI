from flask import Blueprint, request, jsonify, current_app
from models.pmp_limpo import PMP, AtividadePMP, HistoricoExecucaoPMP
from assets_models import Equipamento
from models.plano_mestre import PlanoMestre, AtividadePlanoMestre
from models import db
import logging

pmp_limpo_bp = Blueprint('pmp_limpo_bp', __name__)

# Configura o logging
logging.basicConfig(level=logging.INFO)

@pmp_limpo_bp.route('/api/pmp/equipamento/<int:equipamento_id>/gerar', methods=['POST'])
def gerar_pmps_limpo(equipamento_id):
    """
    Gera PMPs agrupando atividades do plano mestre por:
    - Oficina + Frequência + Tipo de manutenção + Condição
    
    CORRIGIDO: Usa estrutura real do banco com atividade_plano_mestre_id
    """
    try:
        current_app.logger.info(f"🔧 Iniciando geração de PMPs para equipamento {equipamento_id}")
        
        # 1. Buscar plano mestre para este equipamento
        plano_mestre = PlanoMestre.query.filter_by(equipamento_id=equipamento_id).first()
        
        if not plano_mestre:
            return jsonify({
                'success': False,
                'message': 'Nenhum plano mestre encontrado para este equipamento'
            }), 404
        
        # 2. Buscar atividades do plano mestre
        atividades = AtividadePlanoMestre.query.filter_by(plano_mestre_id=plano_mestre.id).all()
        
        if not atividades:
            return jsonify({
                'success': False,
                'message': 'Nenhuma atividade encontrada no plano mestre deste equipamento'
            }), 404
        
        # 3. Buscar informações do equipamento
        equipamento = Equipamento.query.get(equipamento_id)
        if not equipamento:
            return jsonify({
                'success': False,
                'message': 'Equipamento não encontrado'
            }), 404
        
        # 4. Agrupar atividades por critérios
        grupos = {}
        for atividade in atividades:
            # Criar chave de agrupamento
            chave = (
                atividade.oficina or 'Não definida',
                atividade.frequencia or 'Não definida', 
                atividade.tipo_manutencao or 'Não definida',
                atividade.condicao or 'funcionando'
            )
            
            if chave not in grupos:
                grupos[chave] = []
            grupos[chave].append(atividade)
        
        current_app.logger.info(f"📊 Encontrados {len(grupos)} grupos de atividades para equipamento {equipamento_id}")
        
        # 5. Limpar PMPs antigas para este equipamento
        pmps_antigas = PMP.query.filter_by(equipamento_id=equipamento_id).all()
        for pmp_antiga in pmps_antigas:
            # Deletar atividades da PMP antiga
            AtividadePMP.query.filter_by(pmp_id=pmp_antiga.id).delete()
            # Deletar histórico da PMP antiga
            HistoricoExecucaoPMP.query.filter_by(pmp_id=pmp_antiga.id).delete()
        # Deletar PMPs antigas
        PMP.query.filter_by(equipamento_id=equipamento_id).delete()
        
        # 6. Criar novas PMPs
        contador = 1
        novas_pmps = []
        
        for chave, atividades_grupo in grupos.items():
            oficina, frequencia, tipo_manutencao, condicao = chave
            
            # Gerar código único da PMP
            codigo_pmp = f"PMP-{contador:02d}-{equipamento.tag}"
            
            # Gerar descrição baseada nos critérios de agrupamento
            descricao_pmp = f"PREVENTIVA {frequencia.upper()} - {oficina.upper()}"
            
            # Criar nova PMP
            nova_pmp = PMP(
                equipamento_id=equipamento_id,
                codigo=codigo_pmp,
                descricao=descricao_pmp,
                tipo=tipo_manutencao,
                oficina=oficina,
                frequencia=frequencia,
                condicao=condicao,
                status='ativo',
                criado_por=1  # TODO: usar current_user.id quando autenticação estiver funcionando
            )
            
            db.session.add(nova_pmp)
            db.session.flush()  # Para obter o ID da nova PMP
            
            current_app.logger.info(f"✅ PMP criada: {codigo_pmp} (ID: {nova_pmp.id})")
            
            # 7. Criar atividades da PMP com referência ao plano mestre
            ordem = 1
            for atividade_plano in atividades_grupo:
                nova_atividade_pmp = AtividadePMP(
                    pmp_id=nova_pmp.id,
                    atividade_plano_mestre_id=atividade_plano.id,  # ✅ CAMPO OBRIGATÓRIO
                    ordem=ordem,
                    status='ativo',
                    # Campos duplicados para performance
                    descricao=atividade_plano.descricao,
                    oficina=atividade_plano.oficina,
                    frequencia=atividade_plano.frequencia,
                    tipo_manutencao=atividade_plano.tipo_manutencao,
                    conjunto=atividade_plano.conjunto,
                    ponto_controle=atividade_plano.ponto_controle,
                    valor_frequencia=atividade_plano.valor_frequencia,
                    condicao=atividade_plano.condicao
                )
                db.session.add(nova_atividade_pmp)
                ordem += 1
            
            novas_pmps.append(nova_pmp)
            contador += 1
        
        # 8. Salvar no banco
        db.session.commit()
        
        current_app.logger.info(f"🎉 Criadas {len(novas_pmps)} PMPs para equipamento {equipamento_id}")
        
        # 9. Retornar PMPs criadas com contagem de atividades
        resultado = []
        for pmp in novas_pmps:
            pmp_dict = pmp.to_dict()
            # Contar atividades da PMP
            pmp_dict['atividades_count'] = AtividadePMP.query.filter_by(pmp_id=pmp.id).count()
            resultado.append(pmp_dict)
        
        return jsonify({
            'success': True,
            'message': f'Criadas {len(novas_pmps)} PMPs com sucesso',
            'pmps': resultado
        }), 201
        
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"❌ Erro ao gerar PMPs: {e}", exc_info=True)
        return jsonify({
            'success': False,
            'message': f'Erro interno: {str(e)}'
        }), 500

@pmp_limpo_bp.route('/api/pmp/equipamento/<int:equipamento_id>', methods=['GET'])
def get_pmps_por_equipamento_limpo(equipamento_id):
    """
    Retorna todas as PMPs de um equipamento.
    """
    try:
        pmps = PMP.query.filter_by(equipamento_id=equipamento_id).all()
        
        resultado = []
        for pmp in pmps:
            pmp_dict = pmp.to_dict()
            # Adicionar contagem de atividades
            pmp_dict['atividades_count'] = AtividadePMP.query.filter_by(pmp_id=pmp.id).count()
            resultado.append(pmp_dict)
        
        return jsonify(resultado), 200
        
    except Exception as e:
        current_app.logger.error(f"❌ Erro ao buscar PMPs do equipamento {equipamento_id}: {e}")
        return jsonify({
            'success': False,
            'message': f'Erro interno: {str(e)}'
        }), 500

@pmp_limpo_bp.route('/api/pmp/<int:pmp_id>', methods=['GET'])
def get_pmp_detalhes_limpo(pmp_id):
    """
    Retorna os detalhes de uma PMP específica, incluindo suas atividades.
    """
    try:
        pmp = PMP.query.get(pmp_id)
        if not pmp:
            return jsonify({
                'success': False,
                'message': 'PMP não encontrada'
            }), 404
        
        # Buscar atividades da PMP
        atividades = AtividadePMP.query.filter_by(pmp_id=pmp_id).order_by(AtividadePMP.ordem).all()
        
        # Montar resposta com detalhes completos
        resultado = pmp.to_dict()
        resultado['atividades'] = [atividade.to_dict() for atividade in atividades]
        resultado['atividades_count'] = len(atividades)
        
        return jsonify(resultado), 200
        
    except Exception as e:
        current_app.logger.error(f"❌ Erro ao buscar detalhes da PMP {pmp_id}: {e}")
        return jsonify({
            'success': False,
            'message': f'Erro interno: {str(e)}'
        }), 500

@pmp_limpo_bp.route('/api/pmp/<int:pmp_id>/executar', methods=['POST'])
def executar_pmp_limpo(pmp_id):
    """
    Marca uma PMP como executada, criando registro no histórico.
    """
    try:
        data = request.get_json() or {}
        
        pmp = PMP.query.get(pmp_id)
        if not pmp:
            return jsonify({
                'success': False,
                'message': 'PMP não encontrada'
            }), 404
        
        # Criar registro de execução
        execucao = HistoricoExecucaoPMP(
            pmp_id=pmp_id,
            data_programada=data.get('data_programada'),
            data_inicio=data.get('data_inicio'),
            data_conclusao=data.get('data_conclusao'),
            status=data.get('status', 'concluida'),
            observacoes=data.get('observacoes'),
            executado_por=data.get('executado_por', 1),  # TODO: usar current_user.id
            criado_por=1  # TODO: usar current_user.id
        )
        
        db.session.add(execucao)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'PMP executada com sucesso',
            'execucao': execucao.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"❌ Erro ao executar PMP {pmp_id}: {e}")
        return jsonify({
            'success': False,
            'message': f'Erro interno: {str(e)}'
        }), 500



@pmp_limpo_bp.route('/api/pmp/<int:pmp_id>/atualizar', methods=['PUT'])
def atualizar_pmp_limpo(pmp_id):
    """
    Atualiza uma PMP existente com novos dados.
    CORRIGIDO: API de atualização para resolver problema dos valores fixos.
    """
    try:
        current_app.logger.info(f"🔧 Iniciando atualização PMP {pmp_id}")
        
        data = request.get_json()
        if not data:
            current_app.logger.error("❌ Dados não fornecidos")
            return jsonify({
                'success': False,
                'message': 'Dados não fornecidos'
            }), 400
        
        # Buscar PMP existente
        pmp = PMP.query.get(pmp_id)
        if not pmp:
            current_app.logger.error(f"❌ PMP {pmp_id} não encontrada")
            return jsonify({
                'success': False,
                'message': 'PMP não encontrada'
            }), 404
        
        current_app.logger.info(f"📦 Dados recebidos: {data}")
        current_app.logger.info(f"📋 PMP atual: {pmp.codigo}")
        
        # Atualizar campos da PMP
        campos_atualizados = []
        
        if 'num_pessoas' in data:
            valor_antigo = pmp.num_pessoas
            pmp.num_pessoas = int(data['num_pessoas'])
            campos_atualizados.append(f"num_pessoas: {valor_antigo} → {data['num_pessoas']}")
            current_app.logger.info(f"🔄 Atualizando num_pessoas: {valor_antigo} → {data['num_pessoas']}")
            
        if 'dias_antecipacao' in data:
            valor_antigo = pmp.dias_antecipacao
            pmp.dias_antecipacao = int(data['dias_antecipacao'])
            campos_atualizados.append(f"dias_antecipacao: {valor_antigo} → {data['dias_antecipacao']}")
            current_app.logger.info(f"🔄 Atualizando dias_antecipacao: {valor_antigo} → {data['dias_antecipacao']}")
            
        if 'tempo_pessoa' in data:
            valor_antigo = pmp.tempo_pessoa
            pmp.tempo_pessoa = float(data['tempo_pessoa'])
            campos_atualizados.append(f"tempo_pessoa: {valor_antigo} → {data['tempo_pessoa']}")
            current_app.logger.info(f"🔄 Atualizando tempo_pessoa: {valor_antigo} → {data['tempo_pessoa']}")
            
        if 'forma_impressao' in data:
            valor_antigo = pmp.forma_impressao
            pmp.forma_impressao = str(data['forma_impressao'])
            campos_atualizados.append(f"forma_impressao: '{valor_antigo}' → '{data['forma_impressao']}'")
            current_app.logger.info(f"🔄 Atualizando forma_impressao: {valor_antigo} → {data['forma_impressao']}")
        
        # Log das alterações
        current_app.logger.info(f"📝 Total de campos atualizados: {len(campos_atualizados)}")
        
        if not campos_atualizados:
            current_app.logger.warning("⚠️ Nenhum campo foi atualizado")
            return jsonify({
                'success': False,
                'message': 'Nenhum campo válido para atualizar'
            }), 400
        
        # Forçar atualização do timestamp
        from datetime import datetime
        pmp.atualizado_em = datetime.utcnow()
        current_app.logger.info(f"⏰ Timestamp atualizado: {pmp.atualizado_em}")
        
        # Salvar alterações com flush e commit explícitos
        try:
            current_app.logger.info("💾 Iniciando commit no banco...")
            db.session.add(pmp)  # Garantir que o objeto está na sessão
            db.session.flush()   # Forçar flush
            db.session.commit()  # Commit explícito
            current_app.logger.info("✅ Commit realizado com sucesso!")
        except Exception as commit_error:
            current_app.logger.error(f"❌ Erro no commit: {commit_error}")
            db.session.rollback()
            raise commit_error
        
        # Verificar se foi realmente salvo
        pmp_verificacao = PMP.query.get(pmp_id)
        current_app.logger.info(f"🔍 Verificação pós-commit:")
        current_app.logger.info(f"   - num_pessoas: {pmp_verificacao.num_pessoas}")
        current_app.logger.info(f"   - dias_antecipacao: {pmp_verificacao.dias_antecipacao}")
        current_app.logger.info(f"   - tempo_pessoa: {pmp_verificacao.tempo_pessoa}")
        current_app.logger.info(f"   - forma_impressao: {pmp_verificacao.forma_impressao}")
        
        current_app.logger.info(f"🎉 PMP {pmp_id} atualizada com sucesso!")
        
        # Retornar PMP atualizada
        pmp_dict = pmp_verificacao.to_dict()
        pmp_dict['atividades_count'] = AtividadePMP.query.filter_by(pmp_id=pmp.id).count()
        
        return jsonify({
            'success': True,
            'message': 'PMP atualizada com sucesso',
            'pmp': pmp_dict,
            'campos_atualizados': campos_atualizados
        }), 200
        
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"❌ Erro ao atualizar PMP {pmp_id}: {e}", exc_info=True)
        return jsonify({
            'success': False,
            'message': f'Erro interno: {str(e)}'
        }), 500

