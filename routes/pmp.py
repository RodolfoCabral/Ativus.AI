from flask import Blueprint, render_template, request, jsonify, current_app
from models.pmp import PMP, AtividadePMP, HistoricoExecucaoPMP
from assets_models import Equipamento
from models.plano_mestre import AtividadePlanoMestre
from app import db
import logging

pmp_bp = Blueprint('pmp_bp', __name__)

# Configura o logging
logging.basicConfig(level=logging.INFO)

@pmp_bp.route('/pmp-sistema')
def pmp_sistema():
    """
    Renderiza a página principal do sistema PMP para um equipamento específico.
    """
    equipamento_id = request.args.get('equipamento', type=int)
    if not equipamento_id:
        return "Erro: ID do equipamento não fornecido.", 400

    equipamento = Equipamento.query.get(equipamento_id)
    if not equipamento:
        return f"Erro: Equipamento com ID {equipamento_id} não encontrado.", 404

    try:
        # Tenta renderizar o template. Se houver um erro aqui, ele será capturado.
        return render_template('pmp-sistema.html', equipamento=equipamento)
    except Exception as e:
        # Captura qualquer erro durante a renderização do template (a causa mais provável do 500)
        current_app.logger.error(f"Erro ao renderizar pmp-sistema.html: {e}", exc_info=True)
        # Retorna uma página de erro detalhada para o usuário
        error_html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>Erro 500 - Erro no Template</title>
            <style>
                body {{ font-family: sans-serif; margin: 2em; background-color: #f8f9fa; }}
                .container {{ max-width: 800px; margin: auto; background: white; padding: 2em; border-radius: 8px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }}
                h1 {{ color: #dc3545; }}
                code {{ background: #e9ecef; padding: 0.2em 0.4em; border-radius: 4px; font-size: 1.1em; }}
            </style>
        </head>
        <body>
            <div class="container">
                <h1>Erro Interno do Servidor (500)</h1>
                <p>Ocorreu um erro ao tentar processar a página do Sistema PMP.</p>
                <p><strong>Causa Provável:</strong> Erro de sintaxe ou variável indefinida no template <code>pmp-sistema.html</code>.</p>
                <hr>
                <h2>Detalhes do Erro:</h2>
                <p><code>{e}</code></p>
                <p>Por favor, verifique os logs do servidor para o traceback completo e corrija o template.</p>
            </div>
        </body>
        </html>
        """
        return error_html, 500


@pmp_bp.route('/api/pmp/equipamento/<int:equipamento_id>/gerar', methods=['POST'])
def gerar_pmps(equipamento_id):
    """
    Gera PMPs agrupando atividades do plano mestre por:
    - Oficina
    - Frequência  
    - Tipo de manutenção
    - Condição do ativo
    """
    try:
        # Buscar plano mestre para este equipamento
        from models.plano_mestre import PlanoMestre
        plano_mestre = PlanoMestre.query.filter_by(equipamento_id=equipamento_id).first()
        
        if not plano_mestre:
            return jsonify({
                'success': False,
                'message': 'Nenhum plano mestre encontrado para este equipamento'
            }), 404
        
        # Buscar atividades do plano mestre
        atividades = AtividadePlanoMestre.query.filter_by(plano_mestre_id=plano_mestre.id).all()
        
        if not atividades:
            return jsonify({
                'success': False,
                'message': 'Nenhuma atividade encontrada no plano mestre deste equipamento'
            }), 404
        
        # Buscar informações do equipamento
        equipamento = Equipamento.query.get(equipamento_id)
        if not equipamento:
            return jsonify({
                'success': False,
                'message': 'Equipamento não encontrado'
            }), 404
        
        # Agrupar atividades por critérios
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
        
        current_app.logger.info(f"Encontrados {len(grupos)} grupos de atividades para equipamento {equipamento_id}")
        
        # Limpar PMPs antigas para este equipamento
        PMP.query.filter_by(equipamento_id=equipamento_id).delete()
        
        # Criar novas PMPs
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
                oficina=oficina,
                frequencia=frequencia,
                tipo_manutencao=tipo_manutencao,
                condicao=condicao,
                status='ativo',
                criado_por=1  # TODO: usar current_user.id quando autenticação estiver funcionando
            )
            
            db.session.add(nova_pmp)
            db.session.flush()  # Para obter o ID da nova PMP
            
            # Criar atividades da PMP
            for atividade_plano in atividades_grupo:
                nova_atividade_pmp = AtividadePMP(
                    pmp_id=nova_pmp.id,
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
            
            novas_pmps.append(nova_pmp)
            contador += 1
        
        # Salvar no banco
        db.session.commit()
        
        current_app.logger.info(f"Criadas {len(novas_pmps)} PMPs para equipamento {equipamento_id}")
        
        # Retornar PMPs criadas com contagem de atividades
        resultado = []
        for pmp in novas_pmps:
            pmp_dict = pmp.to_dict()
            pmp_dict['atividades_count'] = len([a for a in atividades if 
                a.oficina == pmp.oficina and 
                a.frequencia == pmp.frequencia and 
                a.tipo_manutencao == pmp.tipo_manutencao and 
                a.condicao == pmp.condicao
            ])
            resultado.append(pmp_dict)
        
        return jsonify(resultado), 201
        
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Erro ao gerar PMPs: {e}", exc_info=True)
        return jsonify({
            'success': False,
            'message': f'Erro interno: {str(e)}'
        }), 500

@pmp_bp.route('/api/pmp/equipamento/<int:equipamento_id>', methods=['GET'])
def get_pmps_por_equipamento(equipamento_id):
    """
    Retorna todas as PMPs de um equipamento.
    """
    pmps = PMP.query.filter_by(equipamento_id=equipamento_id).all()
    return jsonify([pmp.to_dict() for pmp in pmps])

@pmp_bp.route('/api/pmp/<int:pmp_id>', methods=['GET'])
def get_pmp_detalhes(pmp_id):
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
        atividades = AtividadePMP.query.filter_by(pmp_id=pmp_id).all()
        
        # Montar resposta com detalhes completos
        resultado = pmp.to_dict()
        resultado['atividades'] = [atividade.to_dict() for atividade in atividades]
        resultado['atividades_count'] = len(atividades)
        
        return jsonify(resultado), 200
        
    except Exception as e:
        current_app.logger.error(f"Erro ao buscar detalhes da PMP {pmp_id}: {e}", exc_info=True)
        return jsonify({
            'success': False,
            'message': f'Erro interno: {str(e)}'
        }), 500

