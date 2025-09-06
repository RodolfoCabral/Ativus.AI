"""
Módulo de Analytics e Relatórios para Sistema PMP/OS
Fornece insights sobre performance, tendências e alertas
"""

from flask import Blueprint, request, jsonify, current_app
from datetime import datetime, date, timedelta
from sqlalchemy import text, func, and_, or_
from models import db

# Importações dos modelos
try:
    from assets_models import OrdemServico
    from models.pmp_limpo import PMP
    MODELS_AVAILABLE = True
except ImportError as e:
    current_app.logger.error(f"Erro ao importar modelos: {e}")
    MODELS_AVAILABLE = False

pmp_analytics_bp = Blueprint('pmp_analytics', __name__)

@pmp_analytics_bp.route('/api/pmp/analytics/dashboard', methods=['GET'])
def dashboard_analytics():
    """
    Dashboard principal com métricas gerais do sistema PMP/OS
    """
    if not MODELS_AVAILABLE:
        return jsonify({'error': 'Modelos não disponíveis'}), 503
    
    try:
        current_app.logger.info("📊 Gerando dashboard de analytics")
        
        hoje = date.today()
        inicio_mes = hoje.replace(day=1)
        inicio_semana = hoje - timedelta(days=hoje.weekday())
        
        # Métricas gerais
        total_pmps = PMP.query.count()
        pmps_ativas = PMP.query.filter(PMP.data_inicio_plano.isnot(None)).count()
        
        total_os_pmp = OrdemServico.query.filter(OrdemServico.pmp_id.isnot(None)).count()
        os_mes_atual = OrdemServico.query.filter(
            and_(
                OrdemServico.pmp_id.isnot(None),
                OrdemServico.data_criacao >= inicio_mes
            )
        ).count()
        
        # OS por status
        os_por_status = db.session.query(
            OrdemServico.status,
            func.count(OrdemServico.id)
        ).filter(
            OrdemServico.pmp_id.isnot(None)
        ).group_by(OrdemServico.status).all()
        
        # Frequências mais usadas
        freq_populares = db.session.query(
            PMP.frequencia,
            func.count(PMP.id)
        ).filter(
            PMP.frequencia.isnot(None)
        ).group_by(PMP.frequencia).order_by(
            func.count(PMP.id).desc()
        ).limit(5).all()
        
        # Performance por frequência (últimos 30 dias)
        data_limite = hoje - timedelta(days=30)
        performance_freq = db.session.query(
            OrdemServico.frequencia_origem,
            func.count(OrdemServico.id).label('total'),
            func.avg(
                func.extract('epoch', OrdemServico.data_finalizacao - OrdemServico.data_criacao) / 3600
            ).label('tempo_medio_horas')
        ).filter(
            and_(
                OrdemServico.pmp_id.isnot(None),
                OrdemServico.data_criacao >= data_limite,
                OrdemServico.data_finalizacao.isnot(None)
            )
        ).group_by(OrdemServico.frequencia_origem).all()
        
        # Tendência de geração (últimos 7 dias)
        tendencia = []
        for i in range(7):
            data_analise = hoje - timedelta(days=i)
            count = OrdemServico.query.filter(
                and_(
                    OrdemServico.pmp_id.isnot(None),
                    func.date(OrdemServico.data_criacao) == data_analise
                )
            ).count()
            
            tendencia.append({
                'data': data_analise.isoformat(),
                'os_geradas': count
            })
        
        tendencia.reverse()  # Ordem cronológica
        
        return jsonify({
            'success': True,
            'data_geracao': hoje.isoformat(),
            'metricas_gerais': {
                'total_pmps': total_pmps,
                'pmps_ativas': pmps_ativas,
                'total_os_geradas': total_os_pmp,
                'os_mes_atual': os_mes_atual,
                'taxa_ativacao': round((pmps_ativas / total_pmps * 100) if total_pmps > 0 else 0, 1)
            },
            'os_por_status': [{'status': status, 'quantidade': count} for status, count in os_por_status],
            'frequencias_populares': [{'frequencia': freq, 'quantidade': count} for freq, count in freq_populares],
            'performance_frequencia': [
                {
                    'frequencia': freq,
                    'total_os': int(total),
                    'tempo_medio_horas': round(float(tempo) if tempo else 0, 2)
                } for freq, total, tempo in performance_freq
            ],
            'tendencia_7_dias': tendencia
        }), 200
        
    except Exception as e:
        current_app.logger.error(f"❌ Erro no dashboard analytics: {e}", exc_info=True)
        return jsonify({'error': f'Erro interno: {str(e)}'}), 500

@pmp_analytics_bp.route('/api/pmp/analytics/alertas', methods=['GET'])
def alertas_sistema():
    """
    Sistema de alertas para identificar problemas e oportunidades
    """
    if not MODELS_AVAILABLE:
        return jsonify({'error': 'Modelos não disponíveis'}), 503
    
    try:
        current_app.logger.info("🚨 Gerando alertas do sistema")
        
        hoje = date.today()
        alertas = []
        
        # Alerta 1: PMPs sem data de início
        pmps_sem_data = PMP.query.filter(PMP.data_inicio_plano.is_(None)).count()
        if pmps_sem_data > 0:
            alertas.append({
                'tipo': 'configuracao',
                'nivel': 'warning',
                'titulo': 'PMPs sem data de início',
                'descricao': f'{pmps_sem_data} PMPs não têm data de início definida',
                'acao_sugerida': 'Definir datas de início para ativar geração automática',
                'quantidade': pmps_sem_data
            })
        
        # Alerta 2: OS atrasadas (mais de 3 dias)
        data_limite_atraso = hoje - timedelta(days=3)
        os_atrasadas = OrdemServico.query.filter(
            and_(
                OrdemServico.pmp_id.isnot(None),
                OrdemServico.status.in_(['aberta', 'programada']),
                OrdemServico.data_programada < data_limite_atraso
            )
        ).count()
        
        if os_atrasadas > 0:
            alertas.append({
                'tipo': 'execucao',
                'nivel': 'error',
                'titulo': 'OS atrasadas',
                'descricao': f'{os_atrasadas} OS estão atrasadas há mais de 3 dias',
                'acao_sugerida': 'Revisar programação e priorizar execução',
                'quantidade': os_atrasadas
            })
        
        # Alerta 3: Frequências com baixa performance
        freq_problematicas = db.session.query(
            OrdemServico.frequencia_origem,
            func.avg(
                func.extract('epoch', OrdemServico.data_finalizacao - OrdemServico.data_criacao) / 86400
            ).label('tempo_medio_dias')
        ).filter(
            and_(
                OrdemServico.pmp_id.isnot(None),
                OrdemServico.data_finalizacao.isnot(None),
                OrdemServico.data_criacao >= hoje - timedelta(days=30)
            )
        ).group_by(OrdemServico.frequencia_origem).having(
            func.avg(
                func.extract('epoch', OrdemServico.data_finalizacao - OrdemServico.data_criacao) / 86400
            ) > 7
        ).all()
        
        if freq_problematicas:
            for freq, tempo_medio in freq_problematicas:
                alertas.append({
                    'tipo': 'performance',
                    'nivel': 'warning',
                    'titulo': f'Performance baixa - {freq}',
                    'descricao': f'OS de frequência {freq} levam em média {round(tempo_medio, 1)} dias para finalizar',
                    'acao_sugerida': 'Revisar processos e recursos para esta frequência',
                    'tempo_medio_dias': round(tempo_medio, 1)
                })
        
        # Alerta 4: Equipamentos com muitas OS pendentes
        equip_sobrecarregados = db.session.query(
            PMP.equipamento_id,
            func.count(OrdemServico.id).label('os_pendentes')
        ).join(
            OrdemServico, PMP.id == OrdemServico.pmp_id
        ).filter(
            OrdemServico.status.in_(['aberta', 'programada'])
        ).group_by(PMP.equipamento_id).having(
            func.count(OrdemServico.id) > 5
        ).all()
        
        if equip_sobrecarregados:
            for equip_id, count in equip_sobrecarregados:
                alertas.append({
                    'tipo': 'capacidade',
                    'nivel': 'warning',
                    'titulo': f'Equipamento sobrecarregado',
                    'descricao': f'Equipamento ID {equip_id} tem {count} OS pendentes',
                    'acao_sugerida': 'Revisar programação e distribuir carga',
                    'equipamento_id': equip_id,
                    'os_pendentes': count
                })
        
        # Alerta 5: Sucesso - Sistema funcionando bem
        if not alertas:
            alertas.append({
                'tipo': 'sucesso',
                'nivel': 'success',
                'titulo': 'Sistema funcionando bem',
                'descricao': 'Nenhum problema crítico detectado no sistema PMP/OS',
                'acao_sugerida': 'Continuar monitoramento regular'
            })
        
        return jsonify({
            'success': True,
            'data_analise': hoje.isoformat(),
            'total_alertas': len(alertas),
            'alertas': alertas,
            'resumo_niveis': {
                'error': len([a for a in alertas if a['nivel'] == 'error']),
                'warning': len([a for a in alertas if a['nivel'] == 'warning']),
                'success': len([a for a in alertas if a['nivel'] == 'success'])
            }
        }), 200
        
    except Exception as e:
        current_app.logger.error(f"❌ Erro nos alertas: {e}", exc_info=True)
        return jsonify({'error': f'Erro interno: {str(e)}'}), 500

@pmp_analytics_bp.route('/api/pmp/analytics/relatorio-mensal', methods=['GET'])
def relatorio_mensal():
    """
    Relatório mensal detalhado de performance do sistema
    """
    if not MODELS_AVAILABLE:
        return jsonify({'error': 'Modelos não disponíveis'}), 503
    
    try:
        # Obter mês/ano da query string ou usar atual
        mes = request.args.get('mes', type=int) or date.today().month
        ano = request.args.get('ano', type=int) or date.today().year
        
        current_app.logger.info(f"📈 Gerando relatório mensal para {mes}/{ano}")
        
        # Calcular período
        inicio_mes = date(ano, mes, 1)
        if mes == 12:
            fim_mes = date(ano + 1, 1, 1) - timedelta(days=1)
        else:
            fim_mes = date(ano, mes + 1, 1) - timedelta(days=1)
        
        # OS geradas no mês
        os_mes = OrdemServico.query.filter(
            and_(
                OrdemServico.pmp_id.isnot(None),
                OrdemServico.data_criacao >= inicio_mes,
                OrdemServico.data_criacao <= fim_mes
            )
        ).all()
        
        # Estatísticas gerais
        total_os = len(os_mes)
        os_finalizadas = len([os for os in os_mes if os.status == 'finalizada'])
        os_pendentes = len([os for os in os_mes if os.status in ['aberta', 'programada']])
        
        # Performance por frequência
        freq_stats = {}
        for os in os_mes:
            freq = os.frequencia_origem or 'indefinida'
            if freq not in freq_stats:
                freq_stats[freq] = {'total': 0, 'finalizadas': 0, 'tempo_total': 0}
            
            freq_stats[freq]['total'] += 1
            if os.status == 'finalizada':
                freq_stats[freq]['finalizadas'] += 1
                if os.data_finalizacao and os.data_criacao:
                    tempo_exec = (os.data_finalizacao - os.data_criacao).total_seconds() / 3600
                    freq_stats[freq]['tempo_total'] += tempo_exec
        
        # Calcular médias
        for freq in freq_stats:
            stats = freq_stats[freq]
            stats['taxa_conclusao'] = round(
                (stats['finalizadas'] / stats['total'] * 100) if stats['total'] > 0 else 0, 1
            )
            stats['tempo_medio_horas'] = round(
                (stats['tempo_total'] / stats['finalizadas']) if stats['finalizadas'] > 0 else 0, 2
            )
        
        # Distribuição por dias do mês
        distribuicao_diaria = {}
        for os in os_mes:
            dia = os.data_criacao.day
            if dia not in distribuicao_diaria:
                distribuicao_diaria[dia] = 0
            distribuicao_diaria[dia] += 1
        
        return jsonify({
            'success': True,
            'periodo': {
                'mes': mes,
                'ano': ano,
                'inicio': inicio_mes.isoformat(),
                'fim': fim_mes.isoformat()
            },
            'resumo_geral': {
                'total_os_geradas': total_os,
                'os_finalizadas': os_finalizadas,
                'os_pendentes': os_pendentes,
                'taxa_conclusao_geral': round((os_finalizadas / total_os * 100) if total_os > 0 else 0, 1)
            },
            'performance_por_frequencia': freq_stats,
            'distribuicao_diaria': distribuicao_diaria,
            'data_geracao': date.today().isoformat()
        }), 200
        
    except Exception as e:
        current_app.logger.error(f"❌ Erro no relatório mensal: {e}", exc_info=True)
        return jsonify({'error': f'Erro interno: {str(e)}'}), 500

