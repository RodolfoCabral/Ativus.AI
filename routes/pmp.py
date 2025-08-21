from flask import Blueprint, render_template, request, jsonify, current_app
from models.pmp import PMP, AtividadePMP, HistoricoExecucaoPMP
from models.assets import Equipamento
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
    Gera PMPs agrupando atividades do plano mestre.
    """
    atividades = AtividadePlanoMestre.query.filter_by(equipamento_id=equipamento_id).all()
    
    # Agrupa por (oficina, frequencia, tipo_manutencao, condicao)
    grupos = {}
    for at in atividades:
        chave = (at.oficina, at.frequencia, at.tipo_manutencao, at.condicao)
        if chave not in grupos:
            grupos[chave] = []
        grupos[chave].append(at)

    # Limpa PMPs antigas para este equipamento
    PMP.query.filter_by(equipamento_id=equipamento_id).delete()
    
    # Cria novas PMPs
    contador = 1
    equipamento_tag = Equipamento.query.get(equipamento_id).tag
    novas_pmps = []

    for chave, atividades_grupo in grupos.items():
        oficina, frequencia, tipo, condicao = chave
        
        codigo_pmp = f"PMP-{contador:02d}-{equipamento_tag}"
        descricao_pmp = f"PMP para {oficina} com frequência {frequencia}"

        nova_pmp = PMP(
            equipamento_id=equipamento_id,
            codigo=codigo_pmp,
            descricao=descricao_pmp,
            # Adicione outros campos conforme necessário
        )
        db.session.add(nova_pmp)
        db.session.flush() # Para obter o ID da nova PMP

        for at_plano_mestre in atividades_grupo:
            nova_atividade_pmp = AtividadePMP(
                pmp_id=nova_pmp.id,
                descricao=at_plano_mestre.descricao,
                # Mapeie outros campos se necessário
            )
            db.session.add(nova_atividade_pmp)
        
        novas_pmps.append(nova_pmp)
        contador += 1

    db.session.commit()
    return jsonify([pmp.to_dict() for pmp in novas_pmps]), 201

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
    pmp = PMP.query.get_or_404(pmp_id)
    return jsonify(pmp.to_dict(incluir_atividades=True))

