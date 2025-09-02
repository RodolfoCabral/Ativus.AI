from flask import Blueprint, request, jsonify, current_app, session
from models.pmp_limpo import PMP, AtividadePMP, HistoricoExecucaoPMP
from assets_models import Equipamento
from models.plano_mestre import PlanoMestre, AtividadePlanoMestre
from models import db
import logging
from datetime import datetime

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

@pmp_limpo_bp.route('/api/pmp/<int:pmp_id>/atualizar', methods=['PUT'])
def atualizar_pmp_limpo(pmp_id):
    """
    Atualiza uma PMP existente com novos dados.
    
    CAMPOS SUPORTADOS:
    - num_pessoas: Número de pessoas para execução
    - dias_antecipacao: Dias para antecipar a geração de O.S.
    - tempo_pessoa: Tempo por pessoa em horas decimais
    - forma_impressao: Forma de impressão da O.S.
    - descricao: Descrição da PMP
    - tipo: Tipo de manutenção
    - oficina: Oficina responsável
    - frequencia: Frequência da manutenção
    - condicao: Condição do ativo
    - status: Status da PMP
    """
    try:
        current_app.logger.info(f"🔧 Iniciando atualização PMP {pmp_id}")
        
        # 1. Validar dados recebidos
        data = request.get_json()
        if not data:
            current_app.logger.error("❌ Nenhum dado recebido na requisição")
            return jsonify({
                'success': False,
                'message': 'Dados não fornecidos'
            }), 400
        
        current_app.logger.info(f"📦 Dados recebidos: {data}")
        
        # 2. Buscar PMP existente
        pmp = PMP.query.get(pmp_id)
        if not pmp:
            current_app.logger.error(f"❌ PMP {pmp_id} não encontrada")
            return jsonify({
                'success': False,
                'message': 'PMP não encontrada'
            }), 404
        
        current_app.logger.info(f"✅ PMP encontrada: {pmp.codigo}")
        
        # 3. Atualizar campos da PMP
        campos_atualizados = []
        
        # Campos de configuração (principais)
        if 'num_pessoas' in data:
            valor_antigo = pmp.num_pessoas
            try:
                pmp.num_pessoas = int(data['num_pessoas'])
                campos_atualizados.append(f"num_pessoas: {valor_antigo} → {pmp.num_pessoas}")
                current_app.logger.info(f"🔄 Atualizando num_pessoas: {valor_antigo} → {pmp.num_pessoas}")
            except (ValueError, TypeError) as e:
                current_app.logger.error(f"❌ Erro ao converter num_pessoas: {e}")
                return jsonify({
                    'success': False,
                    'message': f'Valor inválido para num_pessoas: {data["num_pessoas"]}'
                }), 400
        
        if 'dias_antecipacao' in data:
            valor_antigo = pmp.dias_antecipacao
            try:
                pmp.dias_antecipacao = int(data['dias_antecipacao'])
                campos_atualizados.append(f"dias_antecipacao: {valor_antigo} → {pmp.dias_antecipacao}")
                current_app.logger.info(f"🔄 Atualizando dias_antecipacao: {valor_antigo} → {pmp.dias_antecipacao}")
            except (ValueError, TypeError) as e:
                current_app.logger.error(f"❌ Erro ao converter dias_antecipacao: {e}")
                return jsonify({
                    'success': False,
                    'message': f'Valor inválido para dias_antecipacao: {data["dias_antecipacao"]}'
                }), 400
        
        if 'tempo_pessoa' in data:
            valor_antigo = pmp.tempo_pessoa
            try:
                pmp.tempo_pessoa = float(data['tempo_pessoa'])
                campos_atualizados.append(f"tempo_pessoa: {valor_antigo} → {pmp.tempo_pessoa}")
                current_app.logger.info(f"🔄 Atualizando tempo_pessoa: {valor_antigo} → {pmp.tempo_pessoa}")
            except (ValueError, TypeError) as e:
                current_app.logger.error(f"❌ Erro ao converter tempo_pessoa: {e}")
                return jsonify({
                    'success': False,
                    'message': f'Valor inválido para tempo_pessoa: {data["tempo_pessoa"]}'
                }), 400
        
        if 'forma_impressao' in data:
            valor_antigo = pmp.forma_impressao
            pmp.forma_impressao = str(data['forma_impressao'])
            campos_atualizados.append(f"forma_impressao: '{valor_antigo}' → '{pmp.forma_impressao}'")
            current_app.logger.info(f"🔄 Atualizando forma_impressao: '{valor_antigo}' → '{pmp.forma_impressao}'")
        
        # Outros campos opcionais
        if 'descricao' in data:
            valor_antigo = pmp.descricao
            pmp.descricao = str(data['descricao'])
            campos_atualizados.append(f"descricao: '{valor_antigo}' → '{pmp.descricao}'")
            current_app.logger.info(f"🔄 Atualizando descricao")
        
        if 'tipo' in data:
            valor_antigo = pmp.tipo
            pmp.tipo = str(data['tipo'])
            campos_atualizados.append(f"tipo: '{valor_antigo}' → '{pmp.tipo}'")
            current_app.logger.info(f"🔄 Atualizando tipo")
        
        if 'oficina' in data:
            valor_antigo = pmp.oficina
            pmp.oficina = str(data['oficina'])
            campos_atualizados.append(f"oficina: '{valor_antigo}' → '{pmp.oficina}'")
            current_app.logger.info(f"🔄 Atualizando oficina")
        
        if 'frequencia' in data:
            valor_antigo = pmp.frequencia
            pmp.frequencia = str(data['frequencia'])
            campos_atualizados.append(f"frequencia: '{valor_antigo}' → '{pmp.frequencia}'")
            current_app.logger.info(f"🔄 Atualizando frequencia")
        
        if 'condicao' in data:
            valor_antigo = pmp.condicao
            pmp.condicao = str(data['condicao'])
            campos_atualizados.append(f"condicao: '{valor_antigo}' → '{pmp.condicao}'")
            current_app.logger.info(f"🔄 Atualizando condicao")
        
        if 'status' in data:
            valor_antigo = pmp.status
            pmp.status = str(data['status'])
            campos_atualizados.append(f"status: '{valor_antigo}' → '{pmp.status}'")
            current_app.logger.info(f"🔄 Atualizando status")
        
        # Novos campos - Controle
        if 'data_inicio_plano' in data:
            valor_antigo = pmp.data_inicio_plano
            if data['data_inicio_plano']:
                try:
                    from datetime import datetime
                    pmp.data_inicio_plano = datetime.strptime(data['data_inicio_plano'], '%Y-%m-%d').date()
                    campos_atualizados.append(f"data_inicio_plano: {valor_antigo} → {pmp.data_inicio_plano}")
                    current_app.logger.info(f"🔄 Atualizando data_inicio_plano: {pmp.data_inicio_plano}")
                except ValueError as e:
                    current_app.logger.error(f"❌ Erro ao converter data_inicio_plano: {e}")
                    return jsonify({
                        'success': False,
                        'message': f'Data de início inválida: {data["data_inicio_plano"]}'
                    }), 400
            else:
                pmp.data_inicio_plano = None
                campos_atualizados.append(f"data_inicio_plano: {valor_antigo} → None")
        
        if 'data_fim_plano' in data:
            valor_antigo = pmp.data_fim_plano
            if data['data_fim_plano']:
                try:
                    from datetime import datetime
                    data_fim = datetime.strptime(data['data_fim_plano'], '%Y-%m-%d').date()
                    
                    # Validar se data fim é posterior à data início
                    if pmp.data_inicio_plano and data_fim <= pmp.data_inicio_plano:
                        return jsonify({
                            'success': False,
                            'message': 'A data de fim deve ser posterior à data de início'
                        }), 400
                    
                    pmp.data_fim_plano = data_fim
                    campos_atualizados.append(f"data_fim_plano: {valor_antigo} → {pmp.data_fim_plano}")
                    current_app.logger.info(f"🔄 Atualizando data_fim_plano: {pmp.data_fim_plano}")
                except ValueError as e:
                    current_app.logger.error(f"❌ Erro ao converter data_fim_plano: {e}")
                    return jsonify({
                        'success': False,
                        'message': f'Data de fim inválida: {data["data_fim_plano"]}'
                    }), 400
            else:
                pmp.data_fim_plano = None
                campos_atualizados.append(f"data_fim_plano: {valor_antigo} → None")
        
        # Novos campos - Programação
        if 'usuarios_responsaveis' in data:
            valor_antigo = pmp.usuarios_responsaveis
            import json
            pmp.usuarios_responsaveis = json.dumps(data['usuarios_responsaveis']) if data['usuarios_responsaveis'] else None
            campos_atualizados.append(f"usuarios_responsaveis: {valor_antigo} → {pmp.usuarios_responsaveis}")
            current_app.logger.info(f"🔄 Atualizando usuarios_responsaveis")
        
        # Novos campos - Materiais
        if 'materiais' in data:
            valor_antigo = pmp.materiais
            import json
            pmp.materiais = json.dumps(data['materiais']) if data['materiais'] else None
            campos_atualizados.append(f"materiais: materiais atualizados")
            current_app.logger.info(f"🔄 Atualizando materiais: {len(data['materiais']) if data['materiais'] else 0} itens")
        
        # 4. Atualizar timestamp de modificação
        pmp.atualizado_em = datetime.utcnow()
        current_app.logger.info(f"🕒 Timestamp atualizado: {pmp.atualizado_em}")
        
        # 5. Salvar no banco com commit robusto
        current_app.logger.info("💾 Iniciando commit no banco...")
        
        try:
            # Garantir que o objeto está na sessão
            db.session.add(pmp)
            
            # Forçar flush para detectar erros antes do commit
            db.session.flush()
            current_app.logger.info("✅ Flush realizado com sucesso")
            
            # Commit final
            db.session.commit()
            current_app.logger.info("✅ Commit realizado com sucesso!")
            
            # Verificar se as alterações foram realmente salvas
            pmp_verificacao = PMP.query.get(pmp_id)
            current_app.logger.info(f"🔍 Verificação pós-commit:")
            current_app.logger.info(f"   num_pessoas: {pmp_verificacao.num_pessoas}")
            current_app.logger.info(f"   dias_antecipacao: {pmp_verificacao.dias_antecipacao}")
            current_app.logger.info(f"   tempo_pessoa: {pmp_verificacao.tempo_pessoa}")
            current_app.logger.info(f"   forma_impressao: {pmp_verificacao.forma_impressao}")
            
        except Exception as commit_error:
            current_app.logger.error(f"❌ Erro no commit: {commit_error}", exc_info=True)
            db.session.rollback()
            return jsonify({
                'success': False,
                'message': f'Erro ao salvar no banco: {str(commit_error)}'
            }), 500
        
        current_app.logger.info(f"🎉 PMP {pmp_id} atualizada com sucesso!")
        current_app.logger.info(f"📝 Campos alterados: {campos_atualizados}")
        
        # 6. Retornar PMP atualizada
        pmp_dict = pmp.to_dict()
        pmp_dict['atividades_count'] = AtividadePMP.query.filter_by(pmp_id=pmp.id).count()
        
        return jsonify({
            'success': True,
            'message': 'PMP atualizada com sucesso',
            'pmp': pmp_dict,
            'campos_atualizados': campos_atualizados
        }), 200
        
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"❌ Erro geral ao atualizar PMP {pmp_id}: {e}", exc_info=True)
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



@pmp_limpo_bp.route('/api/usuarios/empresa', methods=['GET'])
def buscar_usuarios_empresa():
    """
    Busca usuários da mesma empresa - VERSÃO SIMPLIFICADA
    """
    try:
        current_app.logger.info("🔍 Buscando usuários da mesma empresa")
        
        # 1. Pegar ID do usuário logado (ajustar conforme sua autenticação)
        usuario_logado_id = 1  # TODO: Pegar da sessão real
        current_app.logger.info(f"👤 ID do usuário logado: {usuario_logado_id}")
        
        from sqlalchemy import text
        
        # 2. Buscar o nome da empresa (coluna company) do usuário logado
        query_empresa = text("""
            SELECT company 
            FROM "user" 
            WHERE id = :user_id
        """)
        
        result_empresa = db.session.execute(query_empresa, {'user_id': usuario_logado_id})
        empresa_row = result_empresa.fetchone()
        
        if not empresa_row:
            current_app.logger.error(f"❌ Usuário {usuario_logado_id} não encontrado na tabela user")
            raise Exception(f"Usuário {usuario_logado_id} não encontrado")
        
        nome_empresa = empresa_row.company
        current_app.logger.info(f"🏢 Empresa do usuário: {nome_empresa}")
        
        # 3. Listar todos os usuários (coluna name) que possuem a mesma company
        query_usuarios = text("""
            SELECT id, name, email
            FROM "user" 
            WHERE company = :company_name
            ORDER BY name
        """)
        
        result_usuarios = db.session.execute(query_usuarios, {
            'company_name': nome_empresa
        })
        
        usuarios_raw = result_usuarios.fetchall()
        current_app.logger.info(f"👥 Usuários encontrados da empresa '{nome_empresa}': {len(usuarios_raw)}")
        
        # 4. Converter para formato da API
        usuarios_lista = []
        for usuario in usuarios_raw:
            # Pular o próprio usuário logado na lista de seleção
            if usuario.id == usuario_logado_id:
                current_app.logger.info(f"  ⏭️ Pulando usuário logado: {usuario.name}")
                continue
                
            usuario_dict = {
                'id': usuario.id,
                'nome': usuario.name,
                'email': usuario.email,
                'cargo': 'Não informado',
                'status': 'ativo'
            }
            usuarios_lista.append(usuario_dict)
            current_app.logger.info(f"  ✅ {usuario_dict['nome']} ({usuario_dict['email']})")
        
        # 5. Retornar dados reais
        current_app.logger.info(f"🎉 Retornando {len(usuarios_lista)} usuários da empresa '{nome_empresa}'")
        
        return jsonify({
            'success': True,
            'usuarios': usuarios_lista,
            'total': len(usuarios_lista),
            'empresa_nome': nome_empresa,
            'usuario_logado_id': usuario_logado_id,
            'fonte': 'BANCO_REAL'
        }), 200
        
    except Exception as e:
        current_app.logger.error(f"❌ Erro ao buscar usuários: {e}", exc_info=True)
        
        # Fallback para dados mock apenas em caso de erro
        usuarios_mock = [
            {'id': 2, 'nome': 'João Silva', 'email': 'joao@empresa.com', 'cargo': 'Técnico', 'status': 'ativo'},
            {'id': 3, 'nome': 'Maria Santos', 'email': 'maria@empresa.com', 'cargo': 'Supervisora', 'status': 'ativo'}
        ]
        
        current_app.logger.info(f"⚠️ Usando dados mock: {len(usuarios_mock)} usuários")
        
        return jsonify({
            'success': True,
            'usuarios': usuarios_mock,
            'total': len(usuarios_mock),
            'mock': True,
            'erro': str(e)
        }), 200

