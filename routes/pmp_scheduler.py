#!/usr/bin/env python3
"""
Sistema de agendamento por frequência para PMPs
Gera OS apenas nas datas corretas baseado na frequência
"""

from flask import Blueprint, request, jsonify, current_app
from datetime import datetime, date, timedelta
from sqlalchemy import text, and_, or_
from models import db

# Importações dos modelos
try:
    from assets_models import OrdemServico
    from models.pmp_limpo import PMP
    MODELS_AVAILABLE = True
except ImportError as e:
    current_app.logger.error(f"Erro ao importar modelos: {e}")
    MODELS_AVAILABLE = False

pmp_scheduler_bp = Blueprint('pmp_scheduler', __name__)

def calcular_todas_datas_geracao(data_inicio, frequencia, data_fim=None):
    """
    Calcula todas as datas de geração baseado na frequência
    """
    try:
        if isinstance(data_inicio, str):
            data_inicio = datetime.strptime(data_inicio, '%Y-%m-%d').date()
        elif isinstance(data_inicio, datetime):
            data_inicio = data_inicio.date()
        
        if data_fim and isinstance(data_fim, str):
            data_fim = datetime.strptime(data_fim, '%Y-%m-%d').date()
        elif isinstance(data_fim, datetime):
            data_fim = data_fim.date()
        
        # Se não tem data fim, calcular até 1 ano no futuro
        if not data_fim:
            data_fim = data_inicio + timedelta(days=365)
        
        datas = []
        data_atual = data_inicio
        
        # Primeira data sempre é a data de início
        datas.append(data_atual)
        
        # Calcular próximas datas baseado na frequência
        while data_atual < data_fim:
            if frequencia == 'diaria':
                data_atual += timedelta(days=1)
            elif frequencia == 'semanal':
                data_atual += timedelta(weeks=1)
            elif frequencia == 'quinzenal':
                data_atual += timedelta(weeks=2)
            elif frequencia == 'mensal':
                # Próximo mês, mesmo dia
                if data_atual.month == 12:
                    try:
                        data_atual = data_atual.replace(year=data_atual.year + 1, month=1)
                    except ValueError:
                        data_atual = data_atual.replace(year=data_atual.year + 1, month=1, day=1)
                else:
                    try:
                        data_atual = data_atual.replace(month=data_atual.month + 1)
                    except ValueError:
                        # Dia não existe no próximo mês (ex: 31/01 -> 28/02)
                        next_month = data_atual.replace(month=data_atual.month + 1, day=1)
                        last_day = (next_month.replace(month=next_month.month + 1) - timedelta(days=1)).day
                        data_atual = next_month.replace(day=min(data_atual.day, last_day))
            elif frequencia == 'bimestral':
                # 2 meses
                for _ in range(2):
                    if data_atual.month == 12:
                        data_atual = data_atual.replace(year=data_atual.year + 1, month=1)
                    else:
                        try:
                            data_atual = data_atual.replace(month=data_atual.month + 1)
                        except ValueError:
                            next_month = data_atual.replace(month=data_atual.month + 1, day=1)
                            last_day = (next_month.replace(month=next_month.month + 1) - timedelta(days=1)).day
                            data_atual = next_month.replace(day=min(data_atual.day, last_day))
            elif frequencia == 'trimestral':
                # 3 meses
                for _ in range(3):
                    if data_atual.month == 12:
                        data_atual = data_atual.replace(year=data_atual.year + 1, month=1)
                    else:
                        try:
                            data_atual = data_atual.replace(month=data_atual.month + 1)
                        except ValueError:
                            next_month = data_atual.replace(month=data_atual.month + 1, day=1)
                            last_day = (next_month.replace(month=next_month.month + 1) - timedelta(days=1)).day
                            data_atual = next_month.replace(day=min(data_atual.day, last_day))
            elif frequencia == 'semestral':
                # 6 meses
                for _ in range(6):
                    if data_atual.month == 12:
                        data_atual = data_atual.replace(year=data_atual.year + 1, month=1)
                    else:
                        try:
                            data_atual = data_atual.replace(month=data_atual.month + 1)
                        except ValueError:
                            next_month = data_atual.replace(month=data_atual.month + 1, day=1)
                            last_day = (next_month.replace(month=next_month.month + 1) - timedelta(days=1)).day
                            data_atual = next_month.replace(day=min(data_atual.day, last_day))
            elif frequencia == 'anual':
                data_atual = data_atual.replace(year=data_atual.year + 1)
            else:
                # Frequência desconhecida, assumir semanal
                data_atual += timedelta(weeks=1)
            
            if data_atual <= data_fim:
                datas.append(data_atual)
        
        return datas
        
    except Exception as e:
        current_app.logger.error(f"Erro ao calcular datas de geração: {e}")
        return [data_inicio]  # Retorna pelo menos a data inicial

@pmp_scheduler_bp.route('/api/pmp/<int:pmp_id>/cronograma-geracao', methods=['GET'])
def obter_cronograma_geracao(pmp_id):
    """
    Obtém cronograma completo de geração de OS para uma PMP
    """
    if not MODELS_AVAILABLE:
        return jsonify({'error': 'Modelos não disponíveis'}), 503
    
    try:
        current_app.logger.info(f"📅 Obtendo cronograma para PMP {pmp_id}")
        
        # Buscar PMP
        pmp = PMP.query.get(pmp_id)
        if not pmp:
            return jsonify({'error': 'PMP não encontrada'}), 404
        
        if not pmp.data_inicio_plano:
            return jsonify({'error': 'PMP não possui data de início definida'}), 400
        
        # Calcular todas as datas de geração
        datas_geracao = calcular_todas_datas_geracao(
            pmp.data_inicio_plano,
            pmp.frequencia or 'semanal',
            pmp.data_fim_plano
        )
        
        # Buscar OS já geradas para esta PMP
        os_existentes = OrdemServico.query.filter_by(pmp_id=pmp_id).all()
        os_por_data = {os.data_programada: os for os in os_existentes if os.data_programada}
        
        # Montar cronograma
        cronograma = []
        hoje = date.today()
        
        for i, data_geracao in enumerate(datas_geracao):
            sequencia = i + 1
            os_existente = os_por_data.get(data_geracao)
            
            item = {
                'sequencia': sequencia,
                'data_geracao': data_geracao.isoformat(),
                'data_passou': data_geracao <= hoje,
                'os_gerada': bool(os_existente),
                'os_id': os_existente.id if os_existente else None,
                'os_status': os_existente.status if os_existente else None,
                'deve_gerar': data_geracao <= hoje and not os_existente,
                'dias_restantes': (data_geracao - hoje).days if data_geracao > hoje else 0
            }
            
            cronograma.append(item)
        
        # Estatísticas
        total_datas = len(cronograma)
        os_geradas = len([item for item in cronograma if item['os_gerada']])
        pendentes = len([item for item in cronograma if item['deve_gerar']])
        futuras = len([item for item in cronograma if not item['data_passou']])
        
        return jsonify({
            'success': True,
            'pmp_id': pmp_id,
            'pmp_atividade': pmp.atividade,
            'frequencia': pmp.frequencia,
            'data_inicio_plano': pmp.data_inicio_plano.isoformat(),
            'data_fim_plano': pmp.data_fim_plano.isoformat() if pmp.data_fim_plano else None,
            'cronograma': cronograma,
            'estatisticas': {
                'total_datas': total_datas,
                'os_geradas': os_geradas,
                'os_pendentes': pendentes,
                'datas_futuras': futuras,
                'percentual_cumprimento': round((os_geradas / total_datas) * 100, 1) if total_datas > 0 else 0
            }
        }), 200
        
    except Exception as e:
        current_app.logger.error(f"❌ Erro ao obter cronograma: {e}", exc_info=True)
        return jsonify({'error': f'Erro interno: {str(e)}'}), 500

@pmp_scheduler_bp.route('/api/pmp/verificar-pendencias-hoje', methods=['GET'])
def verificar_pendencias_hoje():
    """
    Verifica quais PMPs têm OS pendentes para hoje
    """
    if not MODELS_AVAILABLE:
        return jsonify({'error': 'Modelos não disponíveis'}), 503
    
    try:
        current_app.logger.info("🔍 Verificando pendências para hoje")
        
        hoje = date.today()
        pendencias = []
        
        # Buscar todas as PMPs ativas com data de início
        pmps_ativas = PMP.query.filter(
            PMP.data_inicio_plano.isnot(None),
            PMP.data_inicio_plano <= hoje
        ).all()
        
        current_app.logger.info(f"📋 Verificando {len(pmps_ativas)} PMPs ativas")
        
        for pmp in pmps_ativas:
            try:
                # Calcular datas de geração até hoje
                datas_geracao = calcular_todas_datas_geracao(
                    pmp.data_inicio_plano,
                    pmp.frequencia or 'semanal',
                    hoje
                )
                
                # Verificar quais datas não têm OS gerada
                for data_geracao in datas_geracao:
                    if data_geracao <= hoje:
                        os_existente = OrdemServico.query.filter_by(
                            pmp_id=pmp.id,
                            data_programada=data_geracao
                        ).first()
                        
                        if not os_existente:
                            pendencias.append({
                                'pmp_id': pmp.id,
                                'pmp_atividade': pmp.atividade,
                                'equipamento_tag': pmp.equipamento.tag if pmp.equipamento else 'N/A',
                                'data_geracao': data_geracao.isoformat(),
                                'frequencia': pmp.frequencia,
                                'dias_atraso': (hoje - data_geracao).days,
                                'prioridade': 'alta' if (hoje - data_geracao).days > 7 else 'media'
                            })
                
            except Exception as e:
                current_app.logger.error(f"❌ Erro ao processar PMP {pmp.id}: {e}")
                continue
        
        # Ordenar por dias de atraso (mais atrasadas primeiro)
        pendencias.sort(key=lambda x: x['dias_atraso'], reverse=True)
        
        return jsonify({
            'success': True,
            'data_verificacao': hoje.isoformat(),
            'total_pendencias': len(pendencias),
            'pendencias': pendencias,
            'resumo': {
                'criticas': len([p for p in pendencias if p['dias_atraso'] > 7]),
                'hoje': len([p for p in pendencias if p['dias_atraso'] == 0]),
                'atrasadas': len([p for p in pendencias if p['dias_atraso'] > 0])
            }
        }), 200
        
    except Exception as e:
        current_app.logger.error(f"❌ Erro ao verificar pendências: {e}", exc_info=True)
        return jsonify({'error': f'Erro interno: {str(e)}'}), 500

@pmp_scheduler_bp.route('/api/pmp/gerar-os-pendentes', methods=['POST'])
def gerar_os_pendentes():
    """
    Gera todas as OS pendentes até hoje
    """
    if not MODELS_AVAILABLE:
        return jsonify({'error': 'Modelos não disponíveis'}), 503
    
    try:
        current_app.logger.info("🚀 Gerando OS pendentes")
        
        data = request.get_json() or {}
        limite = data.get('limite', 50)  # Limite de OS a gerar por vez
        
        # Obter pendências
        response = verificar_pendencias_hoje()
        pendencias_data = response[0].get_json()
        
        if not pendencias_data.get('success'):
            return jsonify({'error': 'Erro ao obter pendências'}), 500
        
        pendencias = pendencias_data['pendencias'][:limite]
        os_geradas = []
        erros = []
        
        # Importar função de geração de OS
        from routes.pmp_os_generator import gerar_os_from_pmp
        
        for pendencia in pendencias:
            try:
                # Preparar dados para geração
                os_data = {
                    'pmp_id': pendencia['pmp_id'],
                    'data_inicio_plano': pendencia['data_geracao']
                }
                
                # Simular request para gerar OS
                with current_app.test_request_context(json=os_data):
                    result = gerar_os_from_pmp()
                    
                    if result[1] in [200, 201]:  # Sucesso
                        os_info = result[0].get_json()
                        os_geradas.append({
                            'pmp_id': pendencia['pmp_id'],
                            'pmp_atividade': pendencia['pmp_atividade'],
                            'data_geracao': pendencia['data_geracao'],
                            'os_id': os_info.get('os', {}).get('id'),
                            'dias_atraso': pendencia['dias_atraso']
                        })
                        current_app.logger.info(f"✅ OS gerada para PMP {pendencia['pmp_id']} - Data: {pendencia['data_geracao']}")
                    else:
                        erro_info = result[0].get_json()
                        erros.append({
                            'pmp_id': pendencia['pmp_id'],
                            'data_geracao': pendencia['data_geracao'],
                            'erro': erro_info.get('error', 'Erro desconhecido')
                        })
                
            except Exception as e:
                current_app.logger.error(f"❌ Erro ao gerar OS para PMP {pendencia['pmp_id']}: {e}")
                erros.append({
                    'pmp_id': pendencia['pmp_id'],
                    'data_geracao': pendencia['data_geracao'],
                    'erro': str(e)
                })
        
        return jsonify({
            'success': True,
            'message': f'{len(os_geradas)} OS geradas, {len(erros)} erros',
            'os_geradas': os_geradas,
            'erros': erros,
            'total_processadas': len(pendencias),
            'data_processamento': date.today().isoformat()
        }), 200
        
    except Exception as e:
        current_app.logger.error(f"❌ Erro ao gerar OS pendentes: {e}", exc_info=True)
        return jsonify({'error': f'Erro interno: {str(e)}'}), 500

@pmp_scheduler_bp.route('/api/pmp/estatisticas-frequencia', methods=['GET'])
def estatisticas_frequencia():
    """
    Obtém estatísticas de cumprimento por frequência
    """
    if not MODELS_AVAILABLE:
        return jsonify({'error': 'Modelos não disponíveis'}), 503
    
    try:
        current_app.logger.info("📊 Calculando estatísticas de frequência")
        
        hoje = date.today()
        
        # Buscar PMPs por frequência
        query = text("""
            SELECT 
                frequencia,
                COUNT(*) as total_pmps,
                COUNT(CASE WHEN data_inicio_plano IS NOT NULL THEN 1 END) as pmps_ativas
            FROM pmps 
            GROUP BY frequencia
            ORDER BY total_pmps DESC
        """)
        
        result = db.session.execute(query)
        frequencias = result.fetchall()
        
        estatisticas = []
        
        for freq_row in frequencias:
            frequencia, total_pmps, pmps_ativas = freq_row
            
            if not frequencia:
                frequencia = 'não_definida'
            
            # Calcular estatísticas de OS para esta frequência
            os_query = text("""
                SELECT 
                    COUNT(*) as total_os,
                    COUNT(CASE WHEN status = 'concluida' THEN 1 END) as os_concluidas,
                    COUNT(CASE WHEN data_programada <= :hoje AND status != 'concluida' THEN 1 END) as os_atrasadas
                FROM ordens_servico 
                WHERE frequencia_origem = :frequencia
            """)
            
            os_result = db.session.execute(os_query, {
                'frequencia': frequencia,
                'hoje': hoje
            })
            os_stats = os_result.fetchone()
            
            total_os, os_concluidas, os_atrasadas = os_stats if os_stats else (0, 0, 0)
            
            estatisticas.append({
                'frequencia': frequencia,
                'total_pmps': total_pmps,
                'pmps_ativas': pmps_ativas,
                'total_os_geradas': total_os,
                'os_concluidas': os_concluidas,
                'os_atrasadas': os_atrasadas,
                'percentual_conclusao': round((os_concluidas / total_os) * 100, 1) if total_os > 0 else 0,
                'percentual_atraso': round((os_atrasadas / total_os) * 100, 1) if total_os > 0 else 0
            })
        
        return jsonify({
            'success': True,
            'data_calculo': hoje.isoformat(),
            'estatisticas': estatisticas,
            'resumo_geral': {
                'total_pmps': sum([e['total_pmps'] for e in estatisticas]),
                'pmps_ativas': sum([e['pmps_ativas'] for e in estatisticas]),
                'total_os': sum([e['total_os_geradas'] for e in estatisticas]),
                'os_concluidas': sum([e['os_concluidas'] for e in estatisticas]),
                'os_atrasadas': sum([e['os_atrasadas'] for e in estatisticas])
            }
        }), 200
        
    except Exception as e:
        current_app.logger.error(f"❌ Erro ao calcular estatísticas: {e}", exc_info=True)
        return jsonify({'error': f'Erro interno: {str(e)}'}), 500

