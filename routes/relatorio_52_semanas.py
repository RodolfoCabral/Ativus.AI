
from flask import Blueprint, send_file, jsonify
from datetime import datetime, timedelta, date
from io import BytesIO
import traceback
from collections import defaultdict, OrderedDict

# ===== Imports do projeto =====
from models import db
from models.pmp_limpo import PMP
from assets_models import OrdemServico

# ===== ReportLab (PDF) =====
from reportlab.lib.pagesizes import A3, landscape
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, PageBreak
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import mm

relatorio_52_semanas_bp = Blueprint('relatorio_52_semanas', __name__)

# ---------- Utils de data ----------
def _to_date(x):
    try:
        if x is None:
            return None
        if isinstance(x, date) and not isinstance(x, datetime):
            return x
        if isinstance(x, datetime):
            return x.date()
        if isinstance(x, str):
            try:
                return datetime.fromisoformat(x).date()
            except Exception:
                return None
        return None
    except Exception:
        return None

def semanas_do_ano(ano:int):
    base = datetime(ano, 1, 1)
    semanas = []
    for i in range(52):
        ini = base + timedelta(weeks=i)
        fim = ini + timedelta(days=6)
        semanas.append({
            "numero": i+1,
            "inicio": ini.date(),
            "fim": fim.date()
        })
    return semanas

# ---------- Frequência -> semanas planejadas ----------
def semanas_planejadas(frequencia:str):
    """Retorna um set com números de semanas planejadas conforme a frequência textual."""
    if not frequencia:
        return set()
    f = str(frequencia).strip().lower()
    # mapeamentos comuns
    if f in {"diaria","diária","daily"}:
        return set(range(1,53))
    if f in {"semanal","weekly"}:
        return set(range(1,53))
    if f in {"quinzenal","biweekly","quizenal"}:
        return set(i for i in range(1,53) if (i % 2)==0)
    if f in {"mensal","monthly"}:
        return set([4,8,12,16,20,24,28,32,36,40,44,48])
    if f in {"bimestral","bimestra","bimonthly"}:
        return set([8,16,24,32,40,48])
    if f in {"trimestral","quarterly"}:
        return set([12,24,36,48])
    if f in {"semestral","half-year","semestre"}:
        return set([26,52])
    if f in {"anual","yearly","anualidade"}:
        return set([52])
    # fallback: tentar número de semanas por periodicidade (ex: "cada 6 semanas")
    import re
    m = re.search(r"(?:cada|a cada|every)\s*(\d+)\s*(?:semana|semanas|week|weeks)", f)
    if m:
        step = max(1, int(m.group(1)))
        return set([i for i in range(step, 53, step)])
    return set()

# ---------- Status por semana ----------
def status_os_na_semana(pmp_id:int, semana:dict):
    """Retorna (status, os_numero) para a semana.
       status: 'concluida'|'gerada'|'nao_gerada'|None
    """
    ini = datetime.combine(semana["inicio"], datetime.min.time())
    fim = datetime.combine(semana["fim"], datetime.max.time())
    os_ = OrdemServico.query.filter(
        OrdemServico.pmp_id == pmp_id,
        OrdemServico.data_criacao >= ini,
        OrdemServico.data_criacao <= fim
    ).order_by(OrdemServico.id.desc()).first()
    if os_:
        st = getattr(os_, "status", None)
        os_num = getattr(os_, "id", None)
        if st and str(st).lower() in {"concluida","concluída","done","finalizada"}:
            return ("concluida", os_num)
        else:
            return ("gerada", os_num)
    return ("nao_gerada", None)

# ---------- HH por mês / oficina ----------
def hh_por_mes_oficina(ano:int):
    ini = datetime(ano,1,1)
    fim = datetime(ano,12,31,23,59,59)
    os_conc = OrdemServico.query.filter(
        OrdemServico.status.in_(["concluida","concluída"]),
        OrdemServico.data_criacao >= ini,
        OrdemServico.data_criacao <= fim
    ).all()
    resumo = defaultdict(lambda: defaultdict(float))  # mês -> oficina -> hh
    oficinas_set = set()
    for os_ in os_conc:
        d = getattr(os_, "data_criacao", None)
        if not isinstance(d, (datetime, date)): 
            continue
        mes = d.month if isinstance(d, (datetime, date)) else None
        if not mes:
            continue
        hh = float(getattr(os_, "hh_total", 0) or 0)
        oficina = getattr(os_, "oficina", None) or getattr(os_, "setor", None) or "Outros"
        oficinas_set.add(oficina)
        resumo[mes][oficina] += hh
        resumo[mes]["Total"] += hh
    # ordenar por mês e garantir todas oficinas como colunas
    oficinas = ["Total"] + sorted([o for o in oficinas_set if o != "Total"])
    # construir matriz
    tabela = []
    for mes in range(1,13):
        linha = OrderedDict()
        linha["mes"] = mes
        for o in oficinas:
            linha[o] = resumo[mes].get(o, 0)
        tabela.append(linha)
    return oficinas, tabela

# ---------- Geração do PDF ----------
def gerar_pdf_visual(ano:int):
    semanas = semanas_do_ano(ano)
    # Buscar PMPs
    pmps = PMP.query.order_by(PMP.id.asc()).all()
    # Agrupar por equipamento
    grupos = defaultdict(list)
    for pmp in pmps:
        equip = getattr(pmp, "equipamento_nome", None) or getattr(pmp, "equipamento", None) or getattr(pmp, "descricao_equipamento", None) or "Equipamento sem nome"
        grupos[equip].append(pmp)

    buf = BytesIO()
    doc = SimpleDocTemplate(
        buf,
        pagesize=landscape(A3),
        leftMargin=10*mm, rightMargin=10*mm, topMargin=10*mm, bottomMargin=10*mm
    )
    story = []
    st = getSampleStyleSheet()
    h1 = st["Heading1"]; h1.fontSize = 16; h1.spaceAfter = 6
    h2 = st["Heading2"]; h2.fontSize = 12; h2.spaceAfter = 4
    normal = st["Normal"]; normal.fontSize = 8

    # Cabeçalho
    story.append(Paragraph(f"Plano de 52 Semanas - {ano}", h1))
    story.append(Paragraph(f"Gerado em: {datetime.now().strftime('%d/%m/%Y %H:%M')}", normal))
    story.append(Spacer(1, 6))

    # Cores
    VERDE = colors.Color(0.4, 0.73, 0.42)      # concluída
    CINZA_ESCURO = colors.Color(0.46, 0.46, 0.46)  # gerada
    CINZA_CLARO = colors.Color(0.74, 0.74, 0.74)   # não gerada

    # Tamanhos de coluna
    col_equip = 55*mm
    col_pmp = 35*mm
    col_freq = 22*mm
    col_sem = 8*mm  # 52 colunas
    widths = [col_equip, col_pmp, col_freq] + [col_sem]*52

    # Para cada equipamento, montar tabela
    for equip, lista in grupos.items():
        story.append(Spacer(1, 4))
        story.append(Paragraph(f"<b>Equipamento:</b> {equip}", h2))

        # Cabeçalho da matriz
        header = ["PMP", "Frequência", ""]  # col 0 vira mesclagem com 'PMP' e 'Frequência'
        header = ["PMP", "Frequência", ""] + [str(i) for i in range(1,53)]
        data = [header]

        # Estilo base
        style = TableStyle([
            ("FONT", (0,0), (-1,-1), "Helvetica", 7),
            ("GRID", (0,0), (-1,-1), 0.25, colors.black),
            ("ALIGN", (3,0), (-1,-1), "CENTER"),
            ("VALIGN", (0,0), (-1,-1), "MIDDLE"),
            ("BACKGROUND", (0,0), (-1,0), colors.whitesmoke),
        ])

        # Linhas por PMP
        for pmp in lista:
            freq_text = getattr(pmp, "frequencia", None) or getattr(pmp, "periodicidade", None) or ""
            semanas_plan = semanas_planejadas(freq_text)
            # linha base
            linha = [getattr(pmp, "descricao", f"PMP {getattr(pmp,'id','?')}"), str(freq_text), ""]
            # 52 colunas de semana
            for idx, sem in enumerate(semanas, start=1):
                # Verificar status real na semana
                st_sem, os_num = status_os_na_semana(getattr(pmp, "id", 0), sem)
                txt = ""
                cor = None
                if st_sem == "concluida":
                    cor = VERDE; txt = f"OS #{os_num}" if os_num else ""
                elif st_sem == "gerada":
                    cor = CINZA_ESCURO; txt = f"OS #{os_num}" if os_num else ""
                else:
                    # Sem OS: marcar apenas se for semana planejada
                    if idx in semanas_plan:
                        cor = CINZA_CLARO
                linha.append(txt)
                # aplicar cor depois via style (calculando posição)
            data.append(linha)

        # Aplicar cores por célula (varre novamente para não misturar índices)
        # data tem header (linha 0) + N linhas de PMPs
        for r, pmp in enumerate(lista, start=1):
            freq_text = getattr(pmp, "frequencia", None) or getattr(pmp, "periodicidade", None) or ""
            semanas_plan = semanas_planejadas(freq_text)
            for c, sem in enumerate(semanas, start=3):  # colunas a partir da 3 (0:PMP,1:FREQ,2:vazio)
                st_sem, os_num = status_os_na_semana(getattr(pmp, "id", 0), sem)
                if st_sem == "concluida":
                    style.add("BACKGROUND", (c, r), (c, r), VERDE)
                elif st_sem == "gerada":
                    style.add("BACKGROUND", (c, r), (c, r), CINZA_ESCURO)
                else:
                    if (c-2) in semanas_plan:
                        style.add("BACKGROUND", (c, r), (c, r), CINZA_CLARO)

        table = Table(data, colWidths=widths, repeatRows=1)
        table.setStyle(style)
        story.append(table)

        # Quebra se ficar muito grande
        story.append(Spacer(1, 8))

    # ---- Tabela de HH por mês/oficina ----
    oficinas, tabela_hh = hh_por_mes_oficina(ano)
    story.append(PageBreak())
    story.append(Paragraph("Resumo de HH por mês e oficina", h2))

    head_hh = ["Mês"] + oficinas
    data_hh = [head_hh]
    meses_pt = ["Janeiro","Fevereiro","Março","Abril","Maio","Junho","Julho","Agosto","Setembro","Outubro","Novembro","Dezembro"]
    for linha in tabela_hh:
        row = [meses_pt[linha["mes"]-1]]
        for o in oficinas:
            val = linha.get(o, 0)
            row.append(int(val) if float(val).is_integer() else round(float(val),2))
        data_hh.append(row)

    w0 = 35*mm
    wcols = [w0] + [25*mm]*len(oficinas)
    t_hh = Table(data_hh, colWidths=wcols, repeatRows=1)
    t_hh.setStyle(TableStyle([
        ("FONT", (0,0), (-1,-1), "Helvetica", 8),
        ("BACKGROUND", (0,0), (-1,0), colors.whitesmoke),
        ("GRID", (0,0), (-1,-1), 0.25, colors.black),
        ("ALIGN", (1,1), (-1,-1), "RIGHT"),
    ]))
    story.append(t_hh)

    # Build PDF
    doc.build(story)
    buf.seek(0)
    return buf

# ---------- Rota principal (visual) ----------
@relatorio_52_semanas_bp.route('/api/relatorios/plano-52-semanas', methods=['GET'])
def gerar_relatorio_visual():
    try:
        ano = int(datetime.now().year)
        pdf = gerar_pdf_visual(ano)
        fname = f"Plano_52_Semanas_{ano}_visual.pdf"
        return send_file(pdf, as_attachment=True, download_name=fname, mimetype="application/pdf")
    except Exception as e:
        print("Erro ao gerar PDF visual:", e)
        traceback.print_exc()
        return jsonify({"erro": str(e)}), 500
