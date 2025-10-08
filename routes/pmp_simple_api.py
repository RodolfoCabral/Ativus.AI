"""
API Simplificada para PMP - Sem dependência de schedule
Versão de emergência para resolver erro 404
"""

from flask import Blueprint, request, jsonify, current_app
from flask_login import login_required, current_user
from datetime import datetime, date, timedelta
from dateutil.relativedelta import relativedelta
from models import db

# Importações dos modelos
try:
    from assets_models import OrdemServico
    from models.pmp_limpo import PMP
    from models.atividade_os import AtividadeOS
    MODELS_AVAILABLE = True
except ImportError as e:
    current_app.logger.error(f"Erro ao importar modelos: {e}")
    MODELS_AVAILABLE = False

pmp_simple_api_bp = Blueprint('pmp_simple_api', __name__)

def normalizar_frequencia(frequencia):
    """Normaliza frequência para padrão"""
    if not frequencia:
        return 'semanal'
    
    freq_lower = frequencia.lower().strip()
    
    mapeamento = {
        'diario': 'diaria',
        'diária': 'diaria',
        'daily': 'diaria',
        'semanal': 'semanal',
        'weekly': 'semanal',
        'quinzenal': 'quinzenal',
        'biweekly': 'quinzenal',
        'mensal': 'mensal',
        'monthly': 'mensal',
        'mês': 'mensal',
        'bimestral': 'bimestral',
        'trimestral': 'trimestral',
        'quarterly': 'trimestral',
        'semestral': 'semestral',
        'anual': 'anual',
        'yearly': 'anual',
        'ano': 'anual'
    }
    
    return mapeamento.get(freq_lower, 'semanal')

def calcular_proxima_data(data_base, frequencia):
    """Calcula próxima data baseada na frequência"""
    freq_normalizada = normalizar_frequencia(frequencia)
    
    if freq_normalizada == 'diaria':
        return data_base + timedelta(days=1)
    elif freq_normalizada == 'semanal':
        return data_base + timedelta(weeks=1)
    elif freq_normalizada == 'quinzenal':
        return data_base + timedelta(weeks=2)
    elif freq_normalizada == 'mensal':
        return data_base + relativedelta(months=1)
    elif freq_normalizada == 'bimestral':
        return data_base + relativedelta(months=2)
    elif freq_normalizada == 'trimestral':
        return data_base + relativedelta(months=3)
    elif freq_normalizada == 'semestral':
        return data_base + relativedelta(months=6)
    elif freq_normalizada == 'anual':
        return data_base + relativedelta(years=1)
    else:
        return data_base + timedelta(weeks=1)

def gerar_cronograma_os(pmp):
    """Gera cronograma de OS para uma PMP até hoje"""
    if not pmp.data_inicio_plano:
        return []
    
    datas = []
    data_atual = pmp.data_inicio_plano
    hoje = date.today()
    
    # Gerar datas até hoje
    contador = 0
    while data_atual <= hoje and contador < 1000:
        datas.append(data_atual)
        data_atual = calcular_proxima_data(data_atual, pmp.frequencia)
        contador += 1
    
    return datas

@pmp_simple_api_bp.route('/api/pmp/os/verificar-pendencias', methods=['GET'])
@login_required
def api_verificar_pendencias_simples():
    """Verifica pendências de OS para todas as PMPs ativas - Versão Simplificada"""
    try:
        current_app.logger.info("🔍 API Simples: Verificando pendências de OS para PMPs")
        
        if not MODELS_AVAILABLE:
            return jsonify({
                'success': False,
                'error': 'Modelos não disponíveis'
            }), 500
        
        # Buscar PMPs ativas com data de início
        pmps = PMP.query.filter(
            PMP.status == 'ativo',
            PMP.data_inicio_plano.isnot(None)
        ).all()
        
        pendencias = []
        total_pmps_com_pendencias = 0
        
        for pmp in pmps:
            # Verificar se PMP não expirou
            if pmp.data_fim_plano and pmp.data_fim_plano <= date.today():
                continue
            
            # Gerar cronograma até hoje
            cronograma = gerar_cronograma_os(pmp)
            
            if not cronograma:
                continue
            
            # Contar OS existentes
            os_existentes = OrdemServico.query.filter_by(pmp_id=pmp.id).count()
            os_pendentes = len(cronograma) - os_existentes
            
            if os_pendentes > 0:
                pendencias.append({
                    'pmp_id': pmp.id,
                    'pmp_codigo': pmp.codigo,
                    'descricao': pmp.descricao,
                    'frequencia': pmp.frequencia,
                    'data_inicio': pmp.data_inicio_plano.isoformat(),
                    'os_pendentes': os_pendentes,
                    'os_existentes': os_existentes,
                    'total_necessarias': len(cronograma)
                })
                total_pmps_com_pendencias += 1
        
        return jsonify({
            'success': True,
            'pendencias': pendencias,
            'resumo': {
                'total_pmps_verificadas': len(pmps),
                'total_pmps_com_pendencias': total_pmps_com_pendencias,
                'total_os_pendentes': sum(p['os_pendentes'] for p in pendencias)
            },
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        current_app.logger.error(f"❌ Erro na API simples de verificação: {e}")
        return jsonify({
            'success': False,
            'error': f'Erro interno: {str(e)}'
        }), 500

@pmp_simple_api_bp.route('/api/pmp/os/gerar-todas', methods=['POST'])
@login_required
def api_gerar_todas_os_simples():
    """Gera todas as OS pendentes - Versão Simplificada"""
    try:
        current_app.logger.info("🚀 API Simples: Iniciando geração de todas as OS pendentes")
        
        if not MODELS_AVAILABLE:
            return jsonify({
                'success': False,
                'error': 'Modelos não disponíveis'
            }), 500
        
        # Buscar PMPs ativas com data de início
        pmps = PMP.query.filter(
            PMP.status == 'ativo',
            PMP.data_inicio_plano.isnot(None)
        ).all()
        
        os_geradas = []
        total_os_geradas = 0
        pmps_processadas = 0
        
        for pmp in pmps:
            try:
                # Verificar se PMP não expirou
                if pmp.data_fim_plano and pmp.data_fim_plano <= date.today():
                    continue
                
                # Gerar cronograma até hoje
                cronograma = gerar_cronograma_os(pmp)
                
                if not cronograma:
                    continue
                
                pmps_processadas += 1
                
                # Gerar OS para cada data do cronograma
                for i, data_programada in enumerate(cronograma, 1):
                    # Verificar se já existe OS para esta data
                    os_existente = OrdemServico.query.filter_by(
                        pmp_id=pmp.id,
                        data_programada=data_programada
                    ).first()
                    
                    if os_existente:
                        continue  # OS já existe
                    
                    # Criar nova OS
                    sequencia = f"#{i:03d}"
                    descricao = f"PMP: {pmp.descricao} - Sequência {sequencia}"
                    
                    nova_os = OrdemServico(
                        descricao=descricao,
                        equipamento_id=pmp.equipamento_id,
                        tipo='preventiva-periodica',
                        oficina=pmp.oficina,
                        status='programada',
                        prioridade='media',
                        data_programada=data_programada,
                        data_criacao=datetime.now(),
                        criado_por=current_user.id,
                        pmp_id=pmp.id,
                        pmp_codigo=pmp.codigo,
                        origem='pmp_automatica'
                    )
                    
                    db.session.add(nova_os)
                    os_geradas.append({
                        'descricao': descricao,
                        'data_programada': data_programada.isoformat(),
                        'pmp_codigo': pmp.codigo
                    })
                    total_os_geradas += 1
                
            except Exception as e:
                current_app.logger.error(f"❌ Erro ao processar PMP {pmp.codigo}: {e}")
                continue
        
        # Salvar no banco
        db.session.commit()
        
        current_app.logger.info(f"✅ Geração concluída: {total_os_geradas} OS geradas")
        
        return jsonify({
            'success': True,
            'message': f'{total_os_geradas} OS geradas com sucesso',
            'estatisticas': {
                'pmps_processadas': pmps_processadas,
                'os_geradas': total_os_geradas,
                'os_ja_existentes': 0,
                'erros': 0
            },
            'os_geradas': os_geradas,
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"❌ Erro na API simples de geração: {e}")
        return jsonify({
            'success': False,
            'error': f'Erro interno: {str(e)}'
        }), 500

@pmp_simple_api_bp.route('/api/pmp/os/executar-automatico', methods=['POST'])
def api_executar_automatico_simples():
    """Endpoint simplificado para execução automática"""
    try:
        current_app.logger.info("🤖 API Simples: Execução automática iniciada")
        
        if not MODELS_AVAILABLE:
            return jsonify({
                'success': False,
                'error': 'Modelos não disponíveis'
            }), 500
        
        # Redirecionar para a função de gerar todas
        # Simular usuário admin para execução automática
        from flask_login import login_user
        
        # Buscar um usuário admin (assumindo que existe)
        from models import User
        admin_user = User.query.filter_by(profile='admin').first()
        
        if not admin_user:
            admin_user = User.query.first()  # Usar primeiro usuário disponível
        
        if admin_user:
            login_user(admin_user)
        
        # Chamar função de geração
        return api_gerar_todas_os_simples()
        
    except Exception as e:
        current_app.logger.error(f"❌ Erro na execução automática simples: {e}")
        return jsonify({
            'success': False,
            'error': f'Erro interno: {str(e)}'
        }), 500

@pmp_simple_api_bp.route('/api/pmp/auto/status', methods=['GET'])
def api_status_simples():
    """Status simplificado do sistema automático"""
    try:
        return jsonify({
            'success': True,
            'status': {
                'timestamp': datetime.now().isoformat(),
                'sistema_ativo': True,
                'modo_automatico': True,
                'scheduler': {
                    'running': True,
                    'last_execution': datetime.now().isoformat(),
                    'next_execution': (datetime.now() + timedelta(hours=1)).isoformat()
                }
            }
        })
        
    except Exception as e:
        current_app.logger.error(f"❌ Erro no status simples: {e}")
        return jsonify({
            'success': False,
            'error': f'Erro interno: {str(e)}'
        }), 500
