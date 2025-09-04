#!/usr/bin/env python3
"""
API para geração automática de Ordens de Serviço baseada em PMPs
"""

from flask import Blueprint, request, jsonify, current_app, session
from datetime import datetime, date, timedelta
from sqlalchemy import text
from models import db

# Importações dos modelos
try:
    from assets_models import OrdemServico
    from models.pmp_limpo import PMP
    OS_AVAILABLE = True
except ImportError as e:
    current_app.logger.error(f"Erro ao importar modelos: {e}")
    OS_AVAILABLE = False

pmp_os_generator_bp = Blueprint('pmp_os_generator', __name__)

def get_current_user_id():
    """Obtém ID do usuário logado da sessão"""
    try:
        # Tentar diferentes chaves da sessão
        if 'user_id' in session:
            return session['user_id']
        elif 'id' in session:
            return session['id']
        elif 'current_user_id' in session:
            return session['current_user_id']
        else:
            # Buscar qualquer chave que contenha 'user' ou 'id'
            for key in session.keys():
                if 'user' in key.lower() or 'id' in key.lower():
                    try:
                        return int(session[key])
                    except:
                        continue
        return None
    except Exception as e:
        current_app.logger.error(f"Erro ao obter usuário da sessão: {e}")
        return None

def calcular_proxima_data(data_inicio, frequencia):
    """Calcula a próxima data baseada na frequência"""
    try:
        if isinstance(data_inicio, str):
            data_inicio = datetime.strptime(data_inicio, '%Y-%m-%d').date()
        elif isinstance(data_inicio, datetime):
            data_inicio = data_inicio.date()
        
        if frequencia == 'diaria':
            return data_inicio + timedelta(days=1)
        elif frequencia == 'semanal':
            return data_inicio + timedelta(weeks=1)
        elif frequencia == 'quinzenal':
            return data_inicio + timedelta(weeks=2)
        elif frequencia == 'mensal':
            # Próximo mês, mesmo dia
            if data_inicio.month == 12:
                return data_inicio.replace(year=data_inicio.year + 1, month=1)
            else:
                try:
                    return data_inicio.replace(month=data_inicio.month + 1)
                except ValueError:
                    # Caso o dia não exista no próximo mês (ex: 31/01 -> 28/02)
                    next_month = data_inicio.replace(month=data_inicio.month + 1, day=1)
                    return next_month.replace(day=min(data_inicio.day, 
                        (next_month.replace(month=next_month.month + 1) - timedelta(days=1)).day))
        elif frequencia == 'bimestral':
            return calcular_proxima_data(calcular_proxima_data(data_inicio, 'mensal'), 'mensal')
        elif frequencia == 'trimestral':
            # 3 meses
            for _ in range(3):
                data_inicio = calcular_proxima_data(data_inicio, 'mensal')
            return data_inicio
        elif frequencia == 'semestral':
            # 6 meses
            for _ in range(6):
                data_inicio = calcular_proxima_data(data_inicio, 'mensal')
            return data_inicio
        elif frequencia == 'anual':
            return data_inicio.replace(year=data_inicio.year + 1)
        else:
            # Frequência desconhecida, assumir semanal
            return data_inicio + timedelta(weeks=1)
            
    except Exception as e:
        current_app.logger.error(f"Erro ao calcular próxima data: {e}")
        return data_inicio + timedelta(weeks=1)  # Fallback

@pmp_os_generator_bp.route('/api/pmp/gerar-os', methods=['POST'])
def gerar_os_from_pmp():
    """
    Gera OS baseada em PMP quando data de início é definida
    """
    if not OS_AVAILABLE:
        return jsonify({'error': 'Funcionalidade de OS não disponível'}), 503
    
    try:
        current_app.logger.info("🔄 Iniciando geração de OS baseada em PMP")
        
        data = request.get_json()
        pmp_id = data.get('pmp_id')
        data_inicio_plano = data.get('data_inicio_plano')
        
        if not pmp_id or not data_inicio_plano:
            return jsonify({'error': 'PMP ID e data de início são obrigatórios'}), 400
        
        # Buscar PMP
        pmp = PMP.query.get(pmp_id)
        if not pmp:
            return jsonify({'error': 'PMP não encontrada'}), 404
        
        current_app.logger.info(f"📋 PMP encontrada: {pmp.atividade} (ID: {pmp_id})")
        
        # Converter data de início
        if isinstance(data_inicio_plano, str):
            data_inicio = datetime.strptime(data_inicio_plano, '%Y-%m-%d').date()
        else:
            data_inicio = data_inicio_plano
        
        # Verificar se já existe OS para esta PMP na data
        os_existente = OrdemServico.query.filter_by(
            pmp_id=pmp_id,
            data_programada=data_inicio
        ).first()
        
        if os_existente:
            current_app.logger.info(f"⚠️ OS já existe para esta PMP na data {data_inicio}")
            return jsonify({
                'message': 'OS já existe para esta data',
                'os_id': os_existente.id,
                'ja_existe': True
            }), 200
        
        # Obter usuário logado
        usuario_logado_id = get_current_user_id()
        if not usuario_logado_id:
            return jsonify({'error': 'Usuário não autenticado'}), 401
        
        # Buscar dados do usuário para empresa
        query_user = text("SELECT name, company FROM \"user\" WHERE id = :user_id")
        result_user = db.session.execute(query_user, {'user_id': usuario_logado_id})
        user_data = result_user.fetchone()
        
        if not user_data:
            return jsonify({'error': 'Dados do usuário não encontrados'}), 404
        
        user_name, user_company = user_data
        
        # Determinar usuário responsável e prioridade
        usuarios_responsaveis = pmp.usuarios_responsaveis or []
        
        if usuarios_responsaveis and len(usuarios_responsaveis) > 0:
            # Tem usuário responsável - vai para carteira do técnico
            usuario_responsavel = usuarios_responsaveis[0].get('nome', '')
            prioridade = 'preventiva'
            status = 'programada'
            current_app.logger.info(f"👤 OS será atribuída ao usuário: {usuario_responsavel}")
        else:
            # Sem usuário responsável - vai para chamados por prioridade
            usuario_responsavel = None
            prioridade = 'preventiva'
            status = 'aberta'
            current_app.logger.info("📋 OS será adicionada aos chamados por prioridade")
        
        # Calcular próxima data baseada na frequência
        frequencia = pmp.frequencia or 'semanal'
        proxima_data = calcular_proxima_data(data_inicio, frequencia)
        
        # Contar quantas OS já foram geradas para esta PMP
        count_os = OrdemServico.query.filter_by(pmp_id=pmp_id).count()
        numero_sequencia = count_os + 1
        
        # Criar OS
        nova_os = OrdemServico(
            # Dados da PMP
            pmp_id=pmp_id,
            descricao=f"PMP: {pmp.atividade} - Sequência #{numero_sequencia}",
            tipo_manutencao='preventiva',
            oficina=pmp.forma_impressao or 'mecanica',
            condicao_ativo='funcionando',
            qtd_pessoas=pmp.num_pessoas or 1,
            horas=pmp.tempo_pessoa or 1.0,
            prioridade=prioridade,
            status=status,
            
            # Dados do equipamento (da PMP)
            filial_id=pmp.equipamento.setor_ref.filial_id if pmp.equipamento and pmp.equipamento.setor_ref else 1,
            setor_id=pmp.equipamento.setor_id if pmp.equipamento else 1,
            equipamento_id=pmp.equipamento_id,
            
            # Dados do usuário
            empresa=user_company,
            usuario_criacao=user_name,
            usuario_responsavel=usuario_responsavel,
            
            # Datas
            data_programada=data_inicio,
            
            # Campos PMP
            data_proxima_geracao=proxima_data,
            frequencia_origem=frequencia,
            numero_sequencia=numero_sequencia
        )
        
        # Calcular HH
        nova_os.calcular_hh()
        
        # Salvar no banco
        db.session.add(nova_os)
        db.session.commit()
        
        current_app.logger.info(f"✅ OS criada com sucesso: ID {nova_os.id}")
        
        return jsonify({
            'success': True,
            'message': f'OS #{nova_os.id} criada com sucesso',
            'os': nova_os.to_dict(),
            'proxima_geracao': proxima_data.isoformat(),
            'usuario_responsavel': usuario_responsavel,
            'vai_para': 'carteira_tecnico' if usuario_responsavel else 'chamados_prioridade'
        }), 201
        
    except Exception as e:
        current_app.logger.error(f"❌ Erro ao gerar OS: {e}", exc_info=True)
        db.session.rollback()
        return jsonify({'error': f'Erro interno: {str(e)}'}), 500

@pmp_os_generator_bp.route('/api/pmp/<int:pmp_id>/verificar-proxima-os', methods=['GET'])
def verificar_proxima_os(pmp_id):
    """
    Verifica se é hora de gerar a próxima OS para uma PMP
    """
    try:
        current_app.logger.info(f"🔍 Verificando próxima OS para PMP {pmp_id}")
        
        # Buscar PMP
        pmp = PMP.query.get(pmp_id)
        if not pmp:
            return jsonify({'error': 'PMP não encontrada'}), 404
        
        # Buscar última OS gerada para esta PMP
        ultima_os = OrdemServico.query.filter_by(pmp_id=pmp_id)\
                                     .order_by(OrdemServico.numero_sequencia.desc())\
                                     .first()
        
        hoje = date.today()
        
        if not ultima_os:
            # Primeira OS - verificar se data de início já passou
            if pmp.data_inicio_plano and pmp.data_inicio_plano <= hoje:
                return jsonify({
                    'deve_gerar': True,
                    'motivo': 'Primeira OS da PMP',
                    'data_sugerida': hoje.isoformat()
                }), 200
            else:
                return jsonify({
                    'deve_gerar': False,
                    'motivo': 'Data de início ainda não chegou',
                    'data_inicio_plano': pmp.data_inicio_plano.isoformat() if pmp.data_inicio_plano else None
                }), 200
        
        # Verificar se é hora da próxima geração
        if ultima_os.data_proxima_geracao and ultima_os.data_proxima_geracao <= hoje:
            return jsonify({
                'deve_gerar': True,
                'motivo': f'Data de próxima geração chegou ({ultima_os.data_proxima_geracao})',
                'data_sugerida': ultima_os.data_proxima_geracao.isoformat(),
                'ultima_os_id': ultima_os.id,
                'numero_sequencia_proxima': ultima_os.numero_sequencia + 1
            }), 200
        else:
            return jsonify({
                'deve_gerar': False,
                'motivo': f'Próxima geração em {ultima_os.data_proxima_geracao}',
                'data_proxima_geracao': ultima_os.data_proxima_geracao.isoformat() if ultima_os.data_proxima_geracao else None,
                'dias_restantes': (ultima_os.data_proxima_geracao - hoje).days if ultima_os.data_proxima_geracao else None
            }), 200
        
    except Exception as e:
        current_app.logger.error(f"❌ Erro ao verificar próxima OS: {e}", exc_info=True)
        return jsonify({'error': f'Erro interno: {str(e)}'}), 500

@pmp_os_generator_bp.route('/api/pmp/gerar-os-automatica', methods=['POST'])
def gerar_os_automatica():
    """
    Gera OS automaticamente para PMPs que estão na data de geração
    """
    try:
        current_app.logger.info("🤖 Iniciando geração automática de OS")
        
        hoje = date.today()
        os_geradas = []
        
        # Buscar PMPs que precisam gerar OS hoje
        pmps_ativas = PMP.query.filter(
            PMP.data_inicio_plano.isnot(None),
            PMP.data_inicio_plano <= hoje
        ).all()
        
        current_app.logger.info(f"📋 Encontradas {len(pmps_ativas)} PMPs ativas")
        
        for pmp in pmps_ativas:
            try:
                # Verificar se deve gerar OS
                response = verificar_proxima_os(pmp.id)
                data = response[0].get_json()
                
                if data.get('deve_gerar'):
                    # Gerar OS
                    os_data = {
                        'pmp_id': pmp.id,
                        'data_inicio_plano': data.get('data_sugerida', hoje.isoformat())
                    }
                    
                    # Simular request para gerar OS
                    with current_app.test_request_context(json=os_data):
                        result = gerar_os_from_pmp()
                        if result[1] == 201:  # Status 201 = criado
                            os_info = result[0].get_json()
                            os_geradas.append({
                                'pmp_id': pmp.id,
                                'pmp_atividade': pmp.atividade,
                                'os_id': os_info['os']['id'],
                                'motivo': data.get('motivo')
                            })
                            current_app.logger.info(f"✅ OS gerada para PMP {pmp.id}: {pmp.atividade}")
                        
            except Exception as e:
                current_app.logger.error(f"❌ Erro ao processar PMP {pmp.id}: {e}")
                continue
        
        return jsonify({
            'success': True,
            'message': f'{len(os_geradas)} OS geradas automaticamente',
            'os_geradas': os_geradas,
            'data_processamento': hoje.isoformat()
        }), 200
        
    except Exception as e:
        current_app.logger.error(f"❌ Erro na geração automática: {e}", exc_info=True)
        return jsonify({'error': f'Erro interno: {str(e)}'}), 500

