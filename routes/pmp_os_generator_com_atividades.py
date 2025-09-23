from flask import Blueprint, jsonify, request
from models import db
from models.pmp_limpo import PMP, AtividadePMP
from models.assets_models import OrdemServico
from models.atividade_os import AtividadeOS, StatusConformidade
from datetime import datetime

pmp_os_generator_bp = Blueprint(
    'pmp_os_generator_bp',
    __name__,
    url_prefix='/api/pmp'
)

@pmp_os_generator_bp.route("/<int:pmp_id>/gerar-os", methods=["POST"])
def gerar_os_de_pmp(pmp_id):
    """Gera uma Ordem de Serviço a partir de um PMP e transfere suas atividades."""
    pmp = PMP.query.get_or_404(pmp_id)

    # Verificar se já existe uma OS aberta para este PMP
    os_existente = OrdemServico.query.filter_by(
        pmp_id=pmp.id,
        status=\'aberta\'
    ).first()

    if os_existente:
        return jsonify({"message": f"Já existe uma OS aberta (#{os_existente.id}) para este PMP."}), 409

    # 1. Criar a nova Ordem de Serviço
    nova_os = OrdemServico(
        descricao=f"PMP: {pmp.descricao}",
        tipo_manutencao=\'preventiva\',  # OS de PMP é sempre preventiva
        oficina=pmp.oficina,
        condicao_ativo=pmp.condicao,
        qtd_pessoas=pmp.num_pessoas,
        horas=pmp.tempo_pessoa,
        prioridade=\'preventiva\',
        status=\'aberta\',
        equipamento_id=pmp.equipamento_id,
        pmp_id=pmp.id,
        frequencia_origem=pmp.frequencia,
        # Preencher outros campos necessários
        filial_id=1, # Substituir por lógica real para obter filial
        setor_id=1, # Substituir por lógica real para obter setor
        empresa="Empresa Padrão", # Substituir por lógica real
        usuario_criacao="Sistema", # Substituir por lógica real
        data_criacao=datetime.utcnow()
    )
    
    db.session.add(nova_os)
    db.session.flush()  # Garante que nova_os.id esteja disponível

    # 2. Transferir as atividades do PMP para a nova OS
    atividades_pmp = AtividadePMP.query.filter_by(pmp_id=pmp.id).order_by(AtividadePMP.ordem).all()

    for atividade_pmp in atividades_pmp:
        nova_atividade_os = AtividadeOS(
            os_id=nova_os.id,
            atividade_pmp_id=atividade_pmp.id,
            descricao=atividade_pmp.descricao, # Copia a descrição
            ordem=atividade_pmp.ordem,
            status=StatusConformidade.PENDENTE # Status inicial
        )
        db.session.add(nova_atividade_os)

    try:
        db.session.commit()
        return jsonify({
            "message": "Ordem de Serviço gerada com sucesso!",
            "os_id": nova_os.id,
            "atividades_transferidas": len(atividades_pmp)
        }), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": f"Erro ao gerar OS: {str(e)}"}), 500

