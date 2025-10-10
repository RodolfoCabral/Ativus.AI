
from flask import Blueprint, jsonify, request
from datetime import datetime, timedelta, date
from models import db
from models.pmp_limpo import PMP
from assets_models import OrdemServico

relatorio_52_semanas_bp = Blueprint('relatorio_52_semanas', __name__)

# Helper seguro para normalizar date/datetime
def _to_date(x):
    try:
        if isinstance(x, datetime):
            return x.date()
        return x
    except Exception as e:
        print(f"DEBUG[to_date]: erro ao converter {x!r} -> {e}")
        return x

# Gera todas as semanas do ano atual
def calcular_semanas_ano(ano):
    semanas = []
    # Começa em 1º de janeiro e cria 52 blocos de 7 dias
    inicio_ano = datetime(ano, 1, 1)
    for i in range(52):
        inicio_semana = inicio_ano + timedelta(weeks=i)
        fim_semana = inicio_semana + timedelta(days=6)
        semanas.append({
            'numero': i + 1,
            'inicio': inicio_semana.date(),
            'fim': fim_semana.date(),
            'mes': inicio_semana.month
        })
    print(f"DEBUG[semanas]: total={len(semanas)}")
    return semanas

# Determina as semanas associadas a cada PMP
def determinar_semanas_pmp(pmp, semanas_ano):
    semanas_pmp = []
    for semana in semanas_ano:
        print("DEBUG[determinar_semanas_pmp]: PMP", pmp.id,
              "data_inicio=", pmp.data_inicio_plano, "(" + str(type(pmp.data_inicio_plano)) + ")",
              "semana_inicio=", _to_date(semana['inicio']),
              "semana_fim=", _to_date(semana['fim']))
        if _to_date(semana['inicio']) <= _to_date(pmp.data_inicio_plano) <= _to_date(semana['fim']):
            semanas_pmp.append(semana['numero'])
    return semanas_pmp

# Obtém o status da OS em uma semana específica
def obter_status_os_semana(pmp_id, semana_numero, semanas_ano):
    semana = semanas_ano[semana_numero - 1]
    inicio_dt = datetime.combine(_to_date(semana['inicio']), datetime.min.time())
    fim_dt = datetime.combine(_to_date(semana['fim']), datetime.max.time())
    print("DEBUG[obter_status_os_semana]:", f"pmp_id={pmp_id}", f"semana_numero={semana_numero}",
          f"inicio_dt={inicio_dt} ({type(inicio_dt)})", f"fim_dt={fim_dt} ({type(fim_dt)})")

    os_semana = OrdemServico.query.filter(
        OrdemServico.pmp_id == pmp_id,
        OrdemServico.data_criacao >= inicio_dt,
        OrdemServico.data_criacao <= fim_dt
    ).first()

    if os_semana:
        return os_semana.status
    return 'sem_os'

# Calcula horas-homem (HH) por mês e oficina
def calcular_hh_por_mes_oficina(ano):
    inicio_ano = datetime(ano, 1, 1)
    fim_ano = datetime(ano, 12, 31, 23, 59, 59, 999999)
    print(f"DEBUG[HH]: ano={ano}, inicio_ano={inicio_ano}, fim_ano={fim_ano}")

    pmps_com_os = db.session.query(PMP).join(OrdemServico).filter(
        OrdemServico.data_criacao >= inicio_ano,
        OrdemServico.data_criacao <= fim_ano,
        OrdemServico.status == 'concluida'
    ).all()
    print(f"DEBUG[HH]: pmps_com_os={len(pmps_com_os)}")

    hh_por_mes = {}
    for pmp in pmps_com_os:
        os_concluidas = OrdemServico.query.filter(
            OrdemServico.pmp_id == pmp.id,
            OrdemServico.status == 'concluida',
            OrdemServico.data_criacao >= inicio_ano,
            OrdemServico.data_criacao <= fim_ano
        ).all()
        print(f"DEBUG[HH]: PMP {pmp.id} os_concluidas={len(os_concluidas)}")
        for os_ in os_concluidas:
            mes = os_.data_criacao.month
            hh_por_mes[mes] = hh_por_mes.get(mes, 0) + getattr(os_, 'hh_total', 0)
    return hh_por_mes

# Endpoint principal
@relatorio_52_semanas_bp.route('/api/relatorios/plano-52-semanas', methods=['GET'])
def gerar_relatorio_plano_52():
    try:
        ano = datetime.now().year
        semanas_ano = calcular_semanas_ano(ano)
        print(f"DEBUG[route]: ano={ano}, primeira_semana={{'inicio': semanas_ano[0]['inicio'], 'fim': semanas_ano[0]['fim']}} tipos=({type(semanas_ano[0]['inicio'])}, {type(semanas_ano[0]['fim'])})")

        pmps = PMP.query.all()
        dados_relatorio = []

        for pmp in pmps:
            semanas_pmp = determinar_semanas_pmp(pmp, semanas_ano)
            dados_pmp = {
                'pmp_id': pmp.id,
                'descricao': getattr(pmp, 'descricao', ''),
                'semanas': []
            }
            for num_semana in semanas_pmp:
                status = obter_status_os_semana(pmp.id, num_semana, semanas_ano)
                dados_pmp['semanas'].append({
                    'numero': num_semana,
                    'status': status
                })
            dados_relatorio.append(dados_pmp)

        hh_por_mes = calcular_hh_por_mes_oficina(ano)
        return jsonify({
            'ano': ano,
            'total_pmps': len(pmps),
            'hh_por_mes': hh_por_mes,
            'dados': dados_relatorio
        })

    except Exception as e:
        print(f"Erro ao gerar relatório: {e}")
        return jsonify({'erro': str(e)}), 500
