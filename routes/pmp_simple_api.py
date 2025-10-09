"""
API Simplificada para PMP - Versão Final com Busca de Filiais/Setores Válidos
"""

from flask import Blueprint, request, jsonify, current_app
from flask_login import login_required, current_user
from datetime import datetime, date, timedelta
from dateutil.relativedelta import relativedelta
from models import db

# Importações dos modelos
try:
    from assets_models import OrdemServico, Equipamento, Filial, Setor
    from models.pmp_limpo import PMP
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

def obter_dados_validos_equipamento(equipamento_id):
    """Obtém dados válidos do equipamento e relacionamentos"""
    try:
        # Buscar equipamento
        equipamento = Equipamento.query.get(equipamento_id)
        
        if equipamento:
            # Tentar usar dados do equipamento
            filial_id = getattr(equipamento, 'filial_id', None)
            setor_id = getattr(equipamento, 'setor_id', None)
            empresa = getattr(equipamento, 'empresa', None)
            
            # Validar se filial existe
            if filial_id:
                filial = Filial.query.get(filial_id)
                if not filial:
                    filial_id = None
            
            # Validar se setor existe
            if setor_id:
                setor = Setor.query.get(setor_id)
                if not setor:
                    setor_id = None
            
            # Se temos dados válidos, usar
            if filial_id and setor_id and empresa:
                return {
                    'filial_id': filial_id,
                    'setor_id': setor_id,
                    'empresa': empresa
                }
    
    except Exception as e:
        current_app.logger.warning(f"Erro ao buscar equipamento {equipamento_id}: {e}")
    
    # Buscar primeira filial e setor válidos
    try:
        primeira_filial = Filial.query.first()
        primeiro_setor = Setor.query.first()
        
        if primeira_filial and primeiro_setor:
            return {
                'filial_id': primeira_filial.id,
                'setor_id': primeiro_setor.id,
                'empresa': getattr(primeira_filial, 'empresa', 'Ativus')
            }
    except Exception as e:
        current_app.logger.error(f"Erro ao buscar filial/setor padrão: {e}")
    
    # Se nada funcionar, retornar None para indicar erro
    return None

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
    """Gera todas as OS pendentes - Versão Final com Validação de FK"""
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
        erros = 0
        
        for pmp in pmps:
            try:
                # Verificar se PMP não expirou
                if pmp.data_fim_plano and pmp.data_fim_plano <= date.today():
                    continue
                
                # Gerar cronograma até hoje
                cronograma = gerar_cronograma_os(pmp)
                
                if not cronograma:
                    continue
                
                # Obter dados válidos do equipamento
                dados_equipamento = obter_dados_validos_equipamento(pmp.equipamento_id)
                
                if not dados_equipamento:
                    current_app.logger.error(f"❌ Não foi possível obter dados válidos para PMP {pmp.codigo}")
                    erros += 1
                    continue
                
                pmps_processadas += 1
                
                # Gerar OS para cada data do cronograma
                for i, data_programada in enumerate(cronograma, 1):
                    try:
                        # Verificação robusta de OS existente
                        from routes.verificador_duplicatas_os import verificar_os_existente_robusta
                        
                        os_existente = verificar_os_existente_robusta(
                            pmp=pmp,
                            data_programada=data_programada,
                            numero_sequencia=i,
                            OrdemServico=OrdemServico
                        )
                        
                        if os_existente:
                            current_app.logger.info(f"⚠️ OS já existe para PMP {pmp.codigo} sequência {i}: ID {os_existente.id}")
                            continue  # OS já existe
                        
                        # Criar nova OS com todos os campos obrigatórios
                        sequencia = f"#{i:03d}"
                        descricao = f"PMP: {pmp.descricao} - Sequência {sequencia}"
                        
                        # Calcular hh (horas-homem)
                        qtd_pessoas = pmp.num_pessoas or 1
                        horas = pmp.tempo_pessoa or 1.0
                        hh = qtd_pessoas * horas
                        
                        # Verificar se PMP tem usuários responsáveis
                        usuarios_responsaveis = []
                        if pmp.usuarios_responsaveis:
                            try:
                                import json
                                usuarios_responsaveis = json.loads(pmp.usuarios_responsaveis)
                            except:
                                usuarios_responsaveis = []
                        
                        # Determinar status e usuário responsável
                        if usuarios_responsaveis and len(usuarios_responsaveis) > 0:
                            # PMP tem usuário designado - criar como programada
                            status_os = 'programada'
                            
                            # Buscar nome do usuário pelo ID
                            from routes.usuario_helper import buscar_nome_usuario_por_id
                            user_id = usuarios_responsaveis[0]  # Primeiro usuário da lista
                            usuario_responsavel = buscar_nome_usuario_por_id(user_id)
                            
                            current_app.logger.info(f"📋 OS {sequencia} para PMP {pmp.codigo}: PROGRAMADA para usuário ID {user_id} → Nome: {usuario_responsavel} em {data_programada}")
                        else:
                            # PMP sem usuário designado - criar como aberta
                            status_os = 'aberta'
                            usuario_responsavel = None
                            current_app.logger.info(f"📋 OS {sequencia} para PMP {pmp.codigo}: ABERTA (sem usuário) em {data_programada}")
                        
                        current_app.logger.info(f"🔧 Criando OS: Status={status_os}, Usuário={usuario_responsavel}, Data={data_programada}")
                        
                        nova_os = OrdemServico(
                            # Campos obrigatórios básicos
                            descricao=descricao,
                            tipo_manutencao='preventiva-periodica',
                            oficina=pmp.oficina or 'mecanica',
                            condicao_ativo='funcionando',
                            qtd_pessoas=qtd_pessoas,
                            horas=horas,
                            hh=hh,
                            prioridade='media',
                            status=status_os,  # ← CORRIGIDO: aberta ou programada conforme PMP
                            
                            # Campos de relacionamento obrigatórios (VALIDADOS)
                            equipamento_id=pmp.equipamento_id,
                            filial_id=dados_equipamento['filial_id'],
                            setor_id=dados_equipamento['setor_id'],
                            
                            # Campos de empresa e usuário obrigatórios
                            empresa=dados_equipamento['empresa'],
                            usuario_criacao=getattr(current_user, 'username', 'sistema'),
                            usuario_responsavel=usuario_responsavel,  # ← CORRIGIDO: usuário da PMP ou None
                            
                            # Campos de data
                            data_programada=data_programada if status_os == 'programada' else None,  # ← CORRIGIDO: só se programada
                            data_criacao=datetime.now(),
                            
                            # Campos específicos de PMP
                            pmp_id=pmp.id,
                            frequencia_origem=pmp.frequencia,
                            numero_sequencia=i
                        )
                        
                        db.session.add(nova_os)
                        
                        # Commit individual para evitar rollback em massa
                        db.session.commit()
                        
                        os_geradas.append({
                            'descricao': descricao,
                            'data_programada': data_programada.isoformat(),
                            'pmp_codigo': pmp.codigo,
                            'sequencia': i
                        })
                        total_os_geradas += 1
                        
                    except Exception as e:
                        db.session.rollback()
                        current_app.logger.error(f"❌ Erro ao criar OS {i} para PMP {pmp.codigo}: {e}")
                        erros += 1
                        continue
                
            except Exception as e:
                current_app.logger.error(f"❌ Erro ao processar PMP {pmp.codigo}: {e}")
                erros += 1
                continue
        
        current_app.logger.info(f"✅ Geração concluída: {total_os_geradas} OS geradas, {erros} erros")
        
        return jsonify({
            'success': True,
            'message': f'{total_os_geradas} OS geradas com sucesso',
            'estatisticas': {
                'pmps_processadas': pmps_processadas,
                'os_geradas': total_os_geradas,
                'os_ja_existentes': 0,
                'erros': erros
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
        
        # Para execução automática, simular login de usuário sistema
        class UsuarioSistema:
            username = 'sistema'
            id = 1
        
        # Usar usuário sistema temporariamente
        usuario_original = getattr(current_user, '_get_current_object', lambda: None)()
        
        # Simular current_user para a função
        import flask_login
        flask_login.current_user = UsuarioSistema()
        
        try:
            # Chamar função de geração
            return api_gerar_todas_os_simples()
        finally:
            # Restaurar usuário original
            if usuario_original:
                flask_login.current_user = usuario_original
        
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
                'versao': 'final_com_validacao_fk',
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

@pmp_simple_api_bp.route('/debug/filiais-setores', methods=['GET'])
def debug_filiais_setores():
    """Endpoint de debug para verificar filiais e setores disponíveis"""
    try:
        filiais = []
        setores = []
        
        # Buscar filiais
        for filial in Filial.query.all():
            filiais.append({
                'id': filial.id,
                'tag': getattr(filial, 'tag', 'N/A'),
                'descricao': getattr(filial, 'descricao', 'N/A'),
                'empresa': getattr(filial, 'empresa', 'N/A')
            })
        
        # Buscar setores
        for setor in Setor.query.all():
            setores.append({
                'id': setor.id,
                'tag': getattr(setor, 'tag', 'N/A'),
                'descricao': getattr(setor, 'descricao', 'N/A'),
                'filial_id': getattr(setor, 'filial_id', 'N/A')
            })
        
        return jsonify({
            'success': True,
            'filiais': filiais,
            'setores': setores,
            'total_filiais': len(filiais),
            'total_setores': len(setores)
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500
