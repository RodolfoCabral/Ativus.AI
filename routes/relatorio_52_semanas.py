
from flask import Blueprint, jsonify, send_file
from datetime import datetime, timedelta, date
from io import BytesIO
import traceback

# Imports do projeto
from models import db
from models.pmp_limpo import PMP
from assets_models import OrdemServico

# PDF
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas

# === Blueprint (NOME QUE O LOADER ESPERA) ===
relatorio_52_semanas_bp = Blueprint('relatorio_52_semanas', __name__)

# === Utilitário seguro de datas ===
def _to_date(x):
    """Normaliza entradas para datetime.date. Retorna None se não conseguir converter."""
    try:
        if x is None:
            return None
        if isinstance(x, date) and not isinstance(x, datetime):
            return x
        if isinstance(x, datetime):
            return x.date()
        if isinstance(x, str):
            try:
                # tenta ISO (YYYY-MM-DD ou YYYY-MM-DDTHH:MM:SS)
                return datetime.fromisoformat(x).date()
            except Exception:
                return None
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
            d = getattr(os_, 'data_criacao', None)
            d = d if isinstance(d, (datetime, date)) else None
            if d is None:
                continue
            mes = d.month if isinstance(d, (datetime, date)) else None
            if mes is None:
                continue
            hh_por_mes[mes] = hh_por_mes.get(mes, 0) + getattr(os_, 'hh_total', 0)
    return hh_por_mes

# === Geração de PDF com dados reais ===
def _desenha_pdf(dados_relatorio, ano, hh_por_mes):
    buffer = BytesIO()
    c = canvas.Canvas(buffer, pagesize=A4)
    width, height = A4

    # Cabeçalho
    c.setFont("Helvetica-Bold", 14)
    c.drawString(40, height - 40, f"Plano de 52 Semanas - {ano}")
    c.setFont("Helvetica", 10)
    c.drawString(40, height - 55, f"Gerado em: {datetime.now().strftime('%d/%m/%Y %H:%M')}")

    y = height - 80

    # HH por mês (resumo)
    c.setFont("Helvetica-Bold", 11)
    c.drawString(40, y, "Resumo HH por mês:")
    y -= 16
    c.setFont("Helvetica", 9)
    if hh_por_mes:
        meses = sorted(hh_por_mes.items(), key=lambda kv: kv[0])
        linha = ", ".join([f"{m:02d}: {v}" for m, v in meses])
        c.drawString(40, y, linha)
        y -= 20
    else:
        c.drawString(40, y, "(sem HH acumulado no ano)")
        y -= 20

    # Lista de PMPs e semanas
    c.setFont("Helvetica-Bold", 11)
    c.drawString(40, y, "PMPs e semanas:")
    y -= 16

    c.setFont("Helvetica", 9)
    for pmp in dados_relatorio:
        if y < 60:
            c.showPage()
            y = height - 40
            c.setFont("Helvetica-Bold", 14)
            c.drawString(40, y, f"Plano de 52 Semanas - {ano}")
            y -= 25
            c.setFont("Helvetica", 9)

        c.setFont("Helvetica-Bold", 9)
        c.drawString(40, y, f"PMP {pmp['pmp_id']} - {pmp.get('descricao', '')}")
        y -= 12
        c.setFont("Helvetica", 9)

        if pmp['semanas']:
            semanas_txt = ', '.join([str(s['numero']) if isinstance(s, dict) else str(s) for s in pmp['semanas']])
            c.drawString(60, y, f"Semanas: {semanas_txt}")
            y -= 12

            # Status por semana (se disponível)
            if pmp.get('status_por_semana'):
                status_linhas = []
                for k in sorted(pmp['status_por_semana'].keys()):
                    status_linhas.append(f"S{k:02d}:{pmp['status_por_semana'][k]}")
                # quebrar em múltiplas linhas se muito longo
                linha = ", ".join(status_linhas)
                while len(linha) > 110:
                    corte = linha[:110]
                    resto = linha[110:]
                    c.drawString(60, y, corte)
                    y -= 12
                    linha = resto
                c.drawString(60, y, linha)
                y -= 12
        else:
            c.drawString(60, y, "(sem semanas relacionadas)")
            y -= 12

        y -= 6

    c.showPage()
    c.save()
    buffer.seek(0)
    return buffer

# === Endpoint principal: retorna PDF binário ===
@relatorio_52_semanas_bp.route('/api/relatorios/plano-52-semanas', methods=['GET'])
def gerar_relatorio_plano_52():
    try:
        ano = datetime.now().year
        semanas_ano = calcular_semanas_ano(ano)
        print(f"DEBUG[route]: ano={ano}, primeira_semana={{'inicio': semanas_ano[0]['inicio'], 'fim': semanas_ano[0]['fim']}}")

        pmps = PMP.query.all()
        dados_relatorio = []

        for pmp in pmps:
            data_inicio_plano = _to_date(getattr(pmp, 'data_inicio_plano', None))
            if data_inicio_plano is None:
                print(f"⚠️ Ignorando PMP {getattr(pmp, 'id', '?')}: data_inicio_plano ausente")
                continue

            semanas_pmp = determinar_semanas_pmp(pmp, semanas_ano)
            # também coletar status por semana
            status_map = {}
            for num_semana in semanas_pmp:
                status_map[num_semana] = obter_status_os_semana(pmp.id, num_semana, semanas_ano)

            dados_relatorio.append({
                'pmp_id': pmp.id,
                'descricao': getattr(pmp, 'descricao', ''),
                'semanas': [{'numero': s} for s in semanas_pmp],
                'status_por_semana': status_map
            })

        hh_por_mes = calcular_hh_por_mes_oficina(ano)

        # === Gera PDF com dados reais ===
        pdf_buffer = _desenha_pdf(dados_relatorio, ano, hh_por_mes)
        fname = f"Plano_52_Semanas_{ano}.pdf"
        return send_file(pdf_buffer, as_attachment=True, download_name=fname, mimetype="application/pdf")

    except Exception as e:
        print("Erro ao gerar relatório:", e)
        traceback.print_exc()
        return jsonify({'erro': str(e)}), 500
