
from flask import Blueprint, jsonify
from datetime import datetime, timedelta, date
from models import db
from models.pmp_limpo import PMP
from assets_models import OrdemServico
import traceback

relatorio_52_semanas_bp = Blueprint('relatorio_52_semanas', __name__)

# === Utilitário seguro de datas ===
def _to_date(x):
    """Normaliza para datetime.date. Retorna None se não conseguir converter."""
    try:
        if x is None:
            return None
        if isinstance(x, date) and not isinstance(x, datetime):
            return x
        if isinstance(x, datetime):
            return x.date()
        if isinstance(x, str):
            # tenta ISO (YYYY-MM-DD ou YYYY-MM-DDTHH:MM:SS)
            try:
                return datetime.fromisoformat(x).date()
            except Exception:
                pass
        return None
    except Exception as e:
        print(f"DEBUG[to_date]: erro ao converter {x!r} -> {e}")
        return None

# === Semanas do ano ===
def calcular_semanas_ano(ano: int):
    semanas = []
    inicio_ano = datetime(ano, 1, 1)
    for i in range(52):
        inicio_semana_dt = inicio_ano + timedelta(weeks=i)
        fim_semana_dt = inicio_semana_dt + timedelta(days=6)
        semanas.append({
            'numero': i + 1,
            'inicio': inicio_semana_dt.date(),
            'fim': fim_semana_dt.date(),
            'mes': inicio_semana_dt.month
        })
    print(f"DEBUG[semanas]: total={len(semanas)} ano={ano}")
    return semanas

# === Semanas associadas a uma PMP ===
def determinar_semanas_pmp(pmp: PMP, semanas_ano):
    semanas_pmp = []
    data_inicio_plano = _to_date(getattr(pmp, 'data_inicio_plano', None))
    print("DEBUG[determinar_semanas_pmp]: PMP", getattr(pmp, 'id', '?'),
          "data_inicio_plano=", data_inicio_plano, f"({type(data_inicio_plano)})")
    if data_inicio_plano is None:
        print(f"⚠️ Ignorando PMP {getattr(pmp, 'id', '?')}: data_inicio_plano ausente")
        return semanas_pmp  # vazio: será ignorada na rota
    for semana in semanas_ano:
        if semana['inicio'] <= data_inicio_plano <= semana['fim']:
            semanas_pmp.append(semana['numero'])
    return semanas_pmp

# === Status de OS por semana ===
def obter_status_os_semana(pmp_id: int, semana_numero: int, semanas_ano):
    semana = semanas_ano[semana_numero - 1]
    inicio_dt = datetime.combine(semana['inicio'], datetime.min.time())
    fim_dt = datetime.combine(semana['fim'], datetime.max.time())
    print("DEBUG[obter_status_os_semana]:", f"pmp_id={pmp_id}", f"semana={semana_numero}",
          f"intervalo=[{inicio_dt} .. {fim_dt}]")

    os_semana = OrdemServico.query.filter(
        OrdemServico.pmp_id == pmp_id,
        OrdemServico.data_criacao >= inicio_dt,
        OrdemServico.data_criacao <= fim_dt
    ).first()

    return os_semana.status if os_semana else 'sem_os'

# === HH por mês/oficina (mantém lógica existente) ===
def calcular_hh_por_mes_oficina(ano: int):
    inicio_ano = datetime(ano, 1, 1)
    fim_ano = datetime(ano, 12, 31)
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
            OrdemServico.status == 'concluida'
        ).all()
        print(f"DEBUG[HH]: PMP {pmp.id} os_concluidas={len(os_concluidas)}")
        for os_ in os_concluidas:
            try:
                mes = _to_date(os_.data_criacao).month if isinstance(os_.data_criacao, date) else os_.data_criacao.month
            except Exception:
                mes = _to_date(os_.data_criacao).month if _to_date(os_.data_criacao) else None
            if mes is None:
                continue
            hh_por_mes[mes] = hh_por_mes.get(mes, 0) + getattr(os_, 'hh_total', 0)
    return hh_por_mes

# === Endpoint principal ===
@relatorio_52_semanas_bp.route('/api/relatorios/plano-52-semanas', methods=['GET'])
def gerar_relatorio_plano_52():
    try:
        ano = datetime.now().year
        semanas_ano = calcular_semanas_ano(ano)
        print(f"DEBUG[route]: ano={ano}, primeira_semana={{'inicio': semanas_ano[0]['inicio'], 'fim': semanas_ano[0]['fim']}}")

        pmps = PMP.query.all()
        dados_relatorio = []

        for pmp in pmps:
            # Ignora PMPs sem data de início do plano
            data_inicio_plano = _to_date(getattr(pmp, 'data_inicio_plano', None))
            if data_inicio_plano is None:
                print(f"⚠️ Ignorando PMP {getattr(pmp, 'id', '?')}: data_inicio_plano ausente")
                continue

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
        resp = {
            'ano': ano,
            'total_pmps': len(pmps),
            'total_pmps_incluidas': len(dados_relatorio),
            'hh_por_mes': hh_por_mes,
            'dados': dados_relatorio
        }
        print("DEBUG[route]: resposta pronta -> ", {k: (len(v) if isinstance(v, (list, dict)) else v) for k, v in resp.items()})
        return jsonify(resp)

    except Exception as e:
        print("Erro ao gerar relatório:", e)
        traceback.print_exc()
        return jsonify({'erro': str(e)}), 500
