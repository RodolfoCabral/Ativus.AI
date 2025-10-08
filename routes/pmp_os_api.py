#!/usr/bin/env python3
"""
API Aprimorada para Geração Automática de OS baseada em PMPs
Endpoints completos para controle e monitoramento do sistema
"""

from flask import Blueprint, request, jsonify, current_app
from flask_login import login_required, current_user
from datetime import datetime, date, timedelta
from models import db
from sistema_geracao_os_pmp_aprimorado import (
    GeradorOSPMPAprimorado,
    gerar_todas_os_pmp,
    gerar_os_pmp_codigo,
    verificar_pendencias_os_pmp
)

# Importações dos modelos
try:
    from assets_models import OrdemServico
    from models.pmp_limpo import PMP
    from models.atividade_os import AtividadeOS
    OS_AVAILABLE = True
except ImportError as e:
    current_app.logger.error(f"Erro ao importar modelos: {e}")
    OS_AVAILABLE = False

pmp_os_api_bp = Blueprint('pmp_os_api', __name__)

@pmp_os_api_bp.route('/api/pmp/os/verificar-pendencias', methods=['GET'])
@login_required
def api_verificar_pendencias():
    """
    Verifica pendências de OS para todas as PMPs ativas
    """
    try:
        current_app.logger.info("🔍 API: Verificando pendências de OS para PMPs")
        
        resultado = verificar_pendencias_os_pmp()
        
        if resultado['success']:
            return jsonify({
                'success': True,
                'pendencias': resultado['pendencias'],
                'resumo': {
                    'total_pmps_verificadas': resultado['total_pmps_verificadas'],
                    'total_pmps_com_pendencias': resultado['total_pmps_com_pendencias'],
                    'total_os_pendentes': sum(p['os_pendentes'] for p in resultado['pendencias'])
                },
                'timestamp': datetime.now().isoformat()
            })
        else:
            return jsonify({
                'success': False,
                'error': resultado['error']
            }), 500
            
    except Exception as e:
        current_app.logger.error(f"❌ Erro na API de verificação de pendências: {e}")
        return jsonify({
            'success': False,
            'error': f'Erro interno: {str(e)}'
        }), 500

@pmp_os_api_bp.route('/api/pmp/os/gerar-todas', methods=['POST'])
@login_required
def api_gerar_todas_os():
    """
    Gera todas as OS pendentes para PMPs ativas
    """
    try:
        current_app.logger.info("🚀 API: Iniciando geração de todas as OS pendentes")
        
        # Verificar se usuário tem permissão (opcional)
        if hasattr(current_user, 'profile') and current_user.profile not in ['admin', 'manager']:
            return jsonify({
                'success': False,
                'error': 'Permissão insuficiente para gerar OS automaticamente'
            }), 403
        
        resultado = gerar_todas_os_pmp()
        
        if resultado['success']:
            stats = resultado['estatisticas']
            return jsonify({
                'success': True,
                'message': f'{stats["os_geradas"]} OS geradas com sucesso',
                'estatisticas': stats,
                'resumo': {
                    'pmps_processadas': stats['pmps_processadas'],
                    'os_geradas': stats['os_geradas'],
                    'os_ja_existentes': stats['os_ja_existentes'],
                    'erros': stats['erros']
                },
                'os_geradas': resultado['os_geradas'],
                'timestamp': datetime.now().isoformat()
            })
        else:
            return jsonify({
                'success': False,
                'error': resultado['error'],
                'estatisticas': resultado.get('estatisticas', {})
            }), 500
            
    except Exception as e:
        current_app.logger.error(f"❌ Erro na API de geração de todas as OS: {e}")
        return jsonify({
            'success': False,
            'error': f'Erro interno: {str(e)}'
        }), 500

@pmp_os_api_bp.route('/api/pmp/os/gerar-pmp/<string:pmp_codigo>', methods=['POST'])
@login_required
def api_gerar_os_pmp_especifica(pmp_codigo):
    """
    Gera OS para uma PMP específica
    """
    try:
        current_app.logger.info(f"🎯 API: Gerando OS para PMP específica: {pmp_codigo}")
        
        resultado = gerar_os_pmp_codigo(pmp_codigo)
        
        if resultado['success']:
            resultado_pmp = resultado['resultado_pmp']
            return jsonify({
                'success': True,
                'message': f'{resultado_pmp["os_geradas"]} OS geradas para PMP {pmp_codigo}',
                'pmp_codigo': pmp_codigo,
                'resultado_pmp': resultado_pmp,
                'estatisticas': resultado['estatisticas'],
                'timestamp': datetime.now().isoformat()
            })
        else:
            return jsonify({
                'success': False,
                'error': resultado['error']
            }), 404 if 'não encontrada' in resultado['error'] else 500
            
    except Exception as e:
        current_app.logger.error(f"❌ Erro na API de geração de OS para PMP {pmp_codigo}: {e}")
        return jsonify({
            'success': False,
            'error': f'Erro interno: {str(e)}'
        }), 500

@pmp_os_api_bp.route('/api/pmp/os/status-sistema', methods=['GET'])
@login_required
def api_status_sistema():
    """
    Retorna status geral do sistema de geração de OS
    """
    try:
        current_app.logger.info("📊 API: Consultando status do sistema")
        
        # Estatísticas gerais
        total_pmps = PMP.query.filter_by(status='ativo').count()
        total_pmps_com_data = PMP.query.filter(
            PMP.status == 'ativo',
            PMP.data_inicio_plano.isnot(None)
        ).count()
        
        total_os_pmp = OrdemServico.query.filter(
            OrdemServico.pmp_id.isnot(None)
        ).count()
        
        # OS geradas hoje
        hoje = date.today()
        os_hoje = OrdemServico.query.filter(
            OrdemServico.pmp_id.isnot(None),
            OrdemServico.data_programada == hoje
        ).count()
        
        # Verificar pendências rapidamente
        pendencias = verificar_pendencias_os_pmp()
        total_pendencias = 0
        if pendencias['success']:
            total_pendencias = sum(p['os_pendentes'] for p in pendencias['pendencias'])
        
        return jsonify({
            'success': True,
            'status': {
                'sistema_ativo': OS_AVAILABLE,
                'total_pmps_ativas': total_pmps,
                'total_pmps_com_data_inicio': total_pmps_com_data,
                'total_os_de_pmp': total_os_pmp,
                'os_programadas_hoje': os_hoje,
                'total_os_pendentes': total_pendencias,
                'ultima_verificacao': datetime.now().isoformat()
            },
            'configuracao': {
                'gera_os_automaticamente': True,
                'limite_dias_futuro': 365,
                'frequencias_suportadas': [
                    'diaria', 'semanal', 'quinzenal', 'mensal',
                    'bimestral', 'trimestral', 'semestral', 'anual'
                ]
            }
        })
        
    except Exception as e:
        current_app.logger.error(f"❌ Erro na API de status do sistema: {e}")
        return jsonify({
            'success': False,
            'error': f'Erro interno: {str(e)}'
        }), 500

@pmp_os_api_bp.route('/api/pmp/os/cronograma/<string:pmp_codigo>', methods=['GET'])
@login_required
def api_cronograma_pmp(pmp_codigo):
    """
    Retorna cronograma de OS para uma PMP específica
    """
    try:
        current_app.logger.info(f"📅 API: Consultando cronograma para PMP {pmp_codigo}")
        
        # Buscar PMP
        pmp = PMP.query.filter_by(codigo=pmp_codigo).first()
        if not pmp:
            return jsonify({
                'success': False,
                'error': f'PMP {pmp_codigo} não encontrada'
            }), 404
        
        # Gerar cronograma
        gerador = GeradorOSPMPAprimorado()
        
        # Validar PMP
        valida, motivo = gerador.validar_pmp(pmp)
        if not valida:
            return jsonify({
                'success': False,
                'error': f'PMP inválida: {motivo}'
            }), 400
        
        # Gerar cronograma completo
        datas_cronograma = gerador.gerar_cronograma_os(pmp)
        
        # Verificar quais OS já existem
        os_existentes = OrdemServico.query.filter_by(pmp_id=pmp.id).all()
        datas_existentes = {os.data_programada for os in os_existentes}
        
        # Montar cronograma detalhado
        cronograma = []
        hoje = date.today()
        
        for i, data in enumerate(datas_cronograma, 1):
            status = 'pendente'
            os_id = None
            
            if data in datas_existentes:
                status = 'gerada'
                os_existente = next((os for os in os_existentes if os.data_programada == data), None)
                if os_existente:
                    os_id = os_existente.id
                    if os_existente.status == 'concluida':
                        status = 'concluida'
                    elif os_existente.status in ['programada', 'em_execucao']:
                        status = 'programada'
            elif data > hoje:
                status = 'futura'
            
            cronograma.append({
                'sequencia': i,
                'data_programada': data.isoformat(),
                'status': status,
                'os_id': os_id,
                'dias_desde_hoje': (data - hoje).days,
                'eh_passado': data < hoje,
                'eh_hoje': data == hoje,
                'eh_futuro': data > hoje
            })
        
        return jsonify({
            'success': True,
            'pmp': {
                'codigo': pmp.codigo,
                'descricao': pmp.descricao,
                'data_inicio': pmp.data_inicio_plano.isoformat(),
                'data_fim': pmp.data_fim_plano.isoformat() if pmp.data_fim_plano else None,
                'frequencia': pmp.frequencia,
                'status': pmp.status
            },
            'cronograma': cronograma,
            'resumo': {
                'total_datas': len(cronograma),
                'os_geradas': len([c for c in cronograma if c['status'] in ['gerada', 'programada', 'concluida']]),
                'os_pendentes': len([c for c in cronograma if c['status'] == 'pendente']),
                'os_futuras': len([c for c in cronograma if c['status'] == 'futura']),
                'os_concluidas': len([c for c in cronograma if c['status'] == 'concluida'])
            }
        })
        
    except Exception as e:
        current_app.logger.error(f"❌ Erro na API de cronograma para PMP {pmp_codigo}: {e}")
        return jsonify({
            'success': False,
            'error': f'Erro interno: {str(e)}'
        }), 500

@pmp_os_api_bp.route('/api/pmp/os/simular-geracao', methods=['POST'])
@login_required
def api_simular_geracao():
    """
    Simula a geração de OS sem salvar no banco (modo dry-run)
    """
    try:
        current_app.logger.info("🧪 API: Simulando geração de OS")
        
        data = request.get_json() or {}
        pmp_codigo = data.get('pmp_codigo')
        
        if pmp_codigo:
            # Simular para PMP específica
            pmp = PMP.query.filter_by(codigo=pmp_codigo).first()
            if not pmp:
                return jsonify({
                    'success': False,
                    'error': f'PMP {pmp_codigo} não encontrada'
                }), 404
            
            pmps_para_simular = [pmp]
        else:
            # Simular para todas as PMPs
            pmps_para_simular = PMP.query.filter(
                PMP.status == 'ativo',
                PMP.data_inicio_plano.isnot(None)
            ).all()
        
        # Executar simulação
        gerador = GeradorOSPMPAprimorado()
        simulacao = []
        
        for pmp in pmps_para_simular:
            # Validar PMP
            valida, motivo = gerador.validar_pmp(pmp)
            if not valida:
                simulacao.append({
                    'pmp_codigo': pmp.codigo,
                    'pmp_descricao': pmp.descricao,
                    'processada': False,
                    'motivo': motivo,
                    'os_a_gerar': 0
                })
                continue
            
            # Gerar cronograma até hoje
            datas_necessarias = [d for d in gerador.gerar_cronograma_os(pmp) if d <= gerador.hoje]
            
            # Contar OS existentes
            os_existentes = OrdemServico.query.filter_by(pmp_id=pmp.id).count()
            
            os_a_gerar = len(datas_necessarias) - os_existentes
            
            simulacao.append({
                'pmp_codigo': pmp.codigo,
                'pmp_descricao': pmp.descricao,
                'processada': True,
                'os_a_gerar': max(0, os_a_gerar),
                'os_existentes': os_existentes,
                'total_datas': len(datas_necessarias),
                'frequencia': pmp.frequencia,
                'data_inicio': pmp.data_inicio_plano.isoformat()
            })
        
        # Calcular totais
        total_os_a_gerar = sum(s['os_a_gerar'] for s in simulacao if s['processada'])
        total_pmps_processadas = len([s for s in simulacao if s['processada']])
        
        return jsonify({
            'success': True,
            'simulacao': simulacao,
            'resumo': {
                'total_pmps_analisadas': len(simulacao),
                'total_pmps_processadas': total_pmps_processadas,
                'total_os_a_gerar': total_os_a_gerar,
                'modo': 'simulacao_apenas'
            },
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        current_app.logger.error(f"❌ Erro na API de simulação: {e}")
        return jsonify({
            'success': False,
            'error': f'Erro interno: {str(e)}'
        }), 500

@pmp_os_api_bp.route('/api/pmp/os/logs-geracao', methods=['GET'])
@login_required
def api_logs_geracao():
    """
    Retorna logs das últimas gerações de OS
    """
    try:
        current_app.logger.info("📋 API: Consultando logs de geração")
        
        # Por enquanto, retornar logs básicos
        # Em uma implementação completa, isso viria de um sistema de logs persistente
        
        # Buscar OS geradas recentemente de PMPs
        limite_dias = request.args.get('dias', 7, type=int)
        data_limite = date.today() - timedelta(days=limite_dias)
        
        os_recentes = OrdemServico.query.filter(
            OrdemServico.pmp_id.isnot(None),
            OrdemServico.data_programada >= data_limite
        ).order_by(OrdemServico.data_programada.desc()).limit(100).all()
        
        logs = []
        for os in os_recentes:
            pmp = PMP.query.get(os.pmp_id) if os.pmp_id else None
            logs.append({
                'timestamp': os.data_programada.isoformat(),
                'acao': 'OS_GERADA',
                'os_id': os.id,
                'pmp_codigo': pmp.codigo if pmp else 'N/A',
                'descricao': os.descricao,
                'status': os.status,
                'sequencia': os.numero_sequencia
            })
        
        return jsonify({
            'success': True,
            'logs': logs,
            'filtros': {
                'ultimos_dias': limite_dias,
                'data_limite': data_limite.isoformat(),
                'total_registros': len(logs)
            },
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        current_app.logger.error(f"❌ Erro na API de logs: {e}")
        return jsonify({
            'success': False,
            'error': f'Erro interno: {str(e)}'
        }), 500

# Endpoint para webhook/cron job automático
@pmp_os_api_bp.route('/api/pmp/os/executar-automatico', methods=['POST'])
def api_executar_automatico():
    """
    Endpoint para execução automática via cron job ou webhook
    Não requer login para permitir automação
    """
    try:
        # Verificar token de segurança (opcional)
        token = request.headers.get('X-Automation-Token')
        expected_token = current_app.config.get('AUTOMATION_TOKEN')
        
        if expected_token and token != expected_token:
            return jsonify({
                'success': False,
                'error': 'Token de automação inválido'
            }), 401
        
        current_app.logger.info("🤖 API: Execução automática iniciada")
        
        # Executar geração automática
        resultado = gerar_todas_os_pmp()
        
        if resultado['success']:
            stats = resultado['estatisticas']
            current_app.logger.info(f"✅ Execução automática concluída: {stats['os_geradas']} OS geradas")
            
            return jsonify({
                'success': True,
                'message': 'Execução automática concluída',
                'estatisticas': stats,
                'timestamp': datetime.now().isoformat()
            })
        else:
            current_app.logger.error(f"❌ Falha na execução automática: {resultado['error']}")
            return jsonify({
                'success': False,
                'error': resultado['error']
            }), 500
            
    except Exception as e:
        current_app.logger.error(f"❌ Erro na execução automática: {e}")
        return jsonify({
            'success': False,
            'error': f'Erro interno: {str(e)}'
        }), 500
