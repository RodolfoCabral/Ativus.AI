from flask import Blueprint, request, jsonify, render_template
from flask_login import login_required, current_user
from models import db
from models.pmp import PMP, AtividadePMP, HistoricoExecucaoPMP
from models.plano_mestre import AtividadePlanoMestre
from datetime import datetime
import json

pmp_bp = Blueprint('pmp', __name__)

@pmp_bp.route('/pmp-sistema')
@login_required
def pmp_sistema():
    """Página principal do sistema PMP"""
    return render_template('pmp-sistema.html')

@pmp_bp.route('/api/pmps', methods=['GET'])
@login_required
def listar_pmps():
    """Listar PMPs por equipamento"""
    try:
        equipamento_id = request.args.get('equipamento_id')
        
        if not equipamento_id:
            return jsonify({'error': 'equipamento_id é obrigatório'}), 400
        
        pmps = PMP.query.filter_by(
            equipamento_id=equipamento_id,
            status='ativo'
        ).order_by(PMP.codigo).all()
        
        return jsonify({
            'pmps': [pmp.to_dict() for pmp in pmps]
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@pmp_bp.route('/api/pmps', methods=['POST'])
@login_required
def criar_pmp():
    """Criar nova PMP"""
    try:
        dados = request.get_json()
        
        # Validações
        if not dados.get('codigo'):
            return jsonify({'error': 'Código é obrigatório'}), 400
        
        if not dados.get('equipamento_id'):
            return jsonify({'error': 'equipamento_id é obrigatório'}), 400
        
        # Verificar se código já existe
        pmp_existente = PMP.query.filter_by(codigo=dados['codigo']).first()
        if pmp_existente:
            return jsonify({'error': 'Código já existe'}), 400
        
        # Criar PMP
        pmp = PMP(
            codigo=dados['codigo'],
            descricao=dados.get('descricao', ''),
            equipamento_id=dados['equipamento_id'],
            tipo=dados.get('tipo'),
            oficina=dados.get('oficina'),
            frequencia=dados.get('frequencia'),
            condicao=dados.get('condicao'),
            num_pessoas=dados.get('num_pessoas', 1),
            dias_antecipacao=dados.get('dias_antecipacao', 0),
            tempo_pessoa=dados.get('tempo_pessoa', 0.5),
            forma_impressao=dados.get('forma_impressao', 'comum'),
            criado_por=current_user.id
        )
        
        # Definir dias da semana
        if dados.get('dias_semana'):
            pmp.set_dias_semana(dados['dias_semana'])
        
        db.session.add(pmp)
        db.session.flush()  # Para obter o ID
        
        # Adicionar atividades
        if dados.get('atividades_ids'):
            for i, atividade_id in enumerate(dados['atividades_ids']):
                atividade_pmp = AtividadePMP(
                    pmp_id=pmp.id,
                    atividade_plano_mestre_id=atividade_id,
                    ordem=i + 1
                )
                db.session.add(atividade_pmp)
        
        db.session.commit()
        
        return jsonify({
            'message': 'PMP criada com sucesso',
            'id': pmp.id,
            'pmp': pmp.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@pmp_bp.route('/api/pmps/<int:pmp_id>', methods=['GET'])
@login_required
def obter_pmp(pmp_id):
    """Obter PMP específica"""
    try:
        pmp = PMP.query.get_or_404(pmp_id)
        return jsonify(pmp.to_dict())
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@pmp_bp.route('/api/pmps/<int:pmp_id>', methods=['PUT'])
@login_required
def atualizar_pmp(pmp_id):
    """Atualizar PMP"""
    try:
        pmp = PMP.query.get_or_404(pmp_id)
        dados = request.get_json()
        
        # Atualizar campos
        if 'descricao' in dados:
            pmp.descricao = dados['descricao']
        if 'tipo' in dados:
            pmp.tipo = dados['tipo']
        if 'oficina' in dados:
            pmp.oficina = dados['oficina']
        if 'frequencia' in dados:
            pmp.frequencia = dados['frequencia']
        if 'condicao' in dados:
            pmp.condicao = dados['condicao']
        if 'num_pessoas' in dados:
            pmp.num_pessoas = dados['num_pessoas']
        if 'dias_antecipacao' in dados:
            pmp.dias_antecipacao = dados['dias_antecipacao']
        if 'tempo_pessoa' in dados:
            pmp.tempo_pessoa = dados['tempo_pessoa']
        if 'forma_impressao' in dados:
            pmp.forma_impressao = dados['forma_impressao']
        if 'dias_semana' in dados:
            pmp.set_dias_semana(dados['dias_semana'])
        
        pmp.atualizado_em = datetime.utcnow()
        
        # Atualizar atividades se fornecidas
        if 'atividades_ids' in dados:
            # Remover atividades existentes
            AtividadePMP.query.filter_by(pmp_id=pmp.id).delete()
            
            # Adicionar novas atividades
            for i, atividade_id in enumerate(dados['atividades_ids']):
                atividade_pmp = AtividadePMP(
                    pmp_id=pmp.id,
                    atividade_plano_mestre_id=atividade_id,
                    ordem=i + 1
                )
                db.session.add(atividade_pmp)
        
        db.session.commit()
        
        return jsonify({
            'message': 'PMP atualizada com sucesso',
            'pmp': pmp.to_dict()
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@pmp_bp.route('/api/pmps/<int:pmp_id>', methods=['DELETE'])
@login_required
def excluir_pmp(pmp_id):
    """Excluir PMP (soft delete)"""
    try:
        pmp = PMP.query.get_or_404(pmp_id)
        
        # Soft delete
        pmp.status = 'inativo'
        pmp.atualizado_em = datetime.utcnow()
        
        db.session.commit()
        
        return jsonify({'message': 'PMP excluída com sucesso'})
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@pmp_bp.route('/api/pmps/gerar-automatico', methods=['POST'])
@login_required
def gerar_pmps_automatico():
    """Gerar PMPs automaticamente baseado nas atividades do plano mestre"""
    try:
        dados = request.get_json()
        equipamento_id = dados.get('equipamento_id')
        
        if not equipamento_id:
            return jsonify({'error': 'equipamento_id é obrigatório'}), 400
        
        # Buscar atividades do plano mestre
        atividades = AtividadePlanoMestre.query.filter_by(
            equipamento_id=equipamento_id,
            status='ativo'
        ).all()
        
        if not atividades:
            return jsonify({'error': 'Nenhuma atividade encontrada para este equipamento'}), 400
        
        # Agrupar atividades
        grupos = agrupar_atividades_para_pmp(atividades)
        
        # Gerar PMPs
        pmps_criadas = []
        contador = 1
        
        # Buscar tag do equipamento
        from assets_models import Equipamento
        equipamento = Equipamento.query.get(equipamento_id)
        if not equipamento:
            return jsonify({'error': 'Equipamento não encontrado'}), 404
        
        for grupo in grupos:
            codigo = f"PMP-{contador:02d}-{equipamento.tag}"
            
            # Verificar se código já existe
            while PMP.query.filter_by(codigo=codigo).first():
                contador += 1
                codigo = f"PMP-{contador:02d}-{equipamento.tag}"
            
            # Criar PMP
            pmp = PMP(
                codigo=codigo,
                descricao=gerar_descricao_pmp(grupo),
                equipamento_id=equipamento_id,
                tipo=grupo.get('tipo_manutencao'),
                oficina=grupo.get('oficina'),
                frequencia=grupo.get('frequencia'),
                condicao='Funcionando' if grupo.get('status_ativo') else 'Parado',
                num_pessoas=1,
                dias_antecipacao=0,
                tempo_pessoa=0.5,
                forma_impressao='comum',
                criado_por=current_user.id
            )
            
            # Definir terça como padrão
            pmp.set_dias_semana(['terca'])
            
            db.session.add(pmp)
            db.session.flush()
            
            # Adicionar atividades
            for i, atividade in enumerate(grupo['atividades']):
                atividade_pmp = AtividadePMP(
                    pmp_id=pmp.id,
                    atividade_plano_mestre_id=atividade.id,
                    ordem=i + 1
                )
                db.session.add(atividade_pmp)
            
            pmps_criadas.append(pmp.to_dict())
            contador += 1
        
        db.session.commit()
        
        return jsonify({
            'message': f'{len(pmps_criadas)} PMPs geradas com sucesso',
            'pmps': pmps_criadas
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

def agrupar_atividades_para_pmp(atividades):
    """Agrupar atividades por critérios para gerar PMPs"""
    grupos = {}
    
    for atividade in atividades:
        # Criar chave única baseada nos critérios
        chave = f"{atividade.oficina or 'sem-oficina'}_{atividade.frequencia or 'sem-frequencia'}_{atividade.tipo_manutencao or 'sem-tipo'}_{atividade.status_ativo}"
        
        if chave not in grupos:
            grupos[chave] = {
                'oficina': atividade.oficina,
                'frequencia': atividade.frequencia,
                'tipo_manutencao': atividade.tipo_manutencao,
                'status_ativo': atividade.status_ativo,
                'atividades': []
            }
        
        grupos[chave]['atividades'].append(atividade)
    
    return list(grupos.values())

def gerar_descricao_pmp(grupo):
    """Gerar descrição automática para PMP"""
    tipo = grupo.get('tipo_manutencao', 'Manutenção').upper()
    oficina = grupo.get('oficina', 'Geral').upper()
    frequencia = grupo.get('frequencia', 'Periódica').upper()
    
    return f"{tipo} {frequencia} - {oficina}"

@pmp_bp.route('/api/pmps/<int:pmp_id>/historico', methods=['GET'])
@login_required
def listar_historico_pmp(pmp_id):
    """Listar histórico de execução de uma PMP"""
    try:
        historicos = HistoricoExecucaoPMP.query.filter_by(
            pmp_id=pmp_id
        ).order_by(HistoricoExecucaoPMP.data_programada.desc()).all()
        
        return jsonify({
            'historicos': [historico.to_dict() for historico in historicos]
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@pmp_bp.route('/api/pmps/<int:pmp_id>/executar', methods=['POST'])
@login_required
def executar_pmp(pmp_id):
    """Registrar execução de PMP"""
    try:
        pmp = PMP.query.get_or_404(pmp_id)
        dados = request.get_json()
        
        # Criar registro de execução
        execucao = HistoricoExecucaoPMP(
            pmp_id=pmp.id,
            data_programada=datetime.fromisoformat(dados['data_programada'].replace('Z', '+00:00')),
            data_inicio=datetime.utcnow(),
            status='em_andamento',
            observacoes=dados.get('observacoes'),
            executado_por=current_user.id,
            criado_por=current_user.id
        )
        
        db.session.add(execucao)
        db.session.commit()
        
        return jsonify({
            'message': 'Execução iniciada com sucesso',
            'execucao': execucao.to_dict()
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

