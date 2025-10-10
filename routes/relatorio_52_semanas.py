
# -*- coding: utf-8 -*-
"""Relatório Plano 52 Semanas (PDF Visual Paginado)
- Mantém o endpoint original: /api/relatorios/plano-52-semanas
- A3 paisagem
- Semanas 1–26 (página(s)) e 27–52 (página(s))
- Até 10 equipamentos/PMPs por página (gera páginas extras quando necessário)
- Linhas = PMPs do equipamento; Colunas = Semanas (26 por metade)
- Cores por status: concluída (verde), gerada (cinza escuro), planejada sem OS (cinza claro)
- Legenda colorida no rodapé de cada página
- Tabela final: HH por mês e por oficina
"""

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

# Mantém o mesmo nome de blueprint esperado pelo app
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
       status: 'concluida'|'gerada'|'nao_gerada'
    """
    ini = datetime.combine(semana["inicio"], datetime.min.time())
    fim = datetime.combine(semana["fim"], datetime.max.time())
    os_ = OrdemServico.query.filter(
        OrdemServico.pmp_id == pmp_id,
        OrdemServico.data_criacao >= ini,
        OrdemServico.data_criacao <= fim
    ).order_by(OrdemServico.id.desc()).first()
    if os_:
        st = (getattr(os_, "status", None) or "").lower()
        os_num = getattr(os_, "id", None)  # troque para os_.codigo se preferir
        if st in {"concluida","concluída","done","finalizada"}:
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
        mes = d.month
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
            linha[o] = resumo[mes].get(o, 0.0)
        tabela.append(linha)
    return oficinas, tabela

# ---------- Desenho da grade por equipamento (metade do ano) ----------
def _tabela_equipamento(pmps, semanas, estilos_cores):
    VERDE = estilos_cores["VERDE"]
    CINZA_ESCURO = estilos_cores["CINZA_ESCURO"]
    CINZA_CLARO = estilos_cores["CINZA_CLARO"]

    # Larguras
    col_pmp = 60*mm
    col_freq = 25*mm
    col_sem = 10*mm  # 26 colunas -> 260 mm aprox
    widths = [col_pmp, col_freq] + [col_sem]*len(semanas)

    # Cabeçalho
    header = ["PMP", "Frequência"] + [str(s["numero"]) for s in semanas]
    data = [header]

    style = TableStyle([
        ("FONT", (0,0), (-1,-1), "Helvetica", 7),
        ("GRID", (0,0), (-1,-1), 0.25, colors.black),
        ("ALIGN", (2,0), (-1,-1), "CENTER"),
        ("VALIGN", (0,0), (-1,-1), "MIDDLE"),
        ("BACKGROUND", (0,0), (-1,0), colors.whitesmoke),
    ])

    # Prepara linhas PMP
    for pmp in pmps:
        desc = getattr(pmp, "descricao", f"PMP {getattr(pmp,'id','?')}")
        freq_text = getattr(pmp, "frequencia", None) or getattr(pmp, "periodicidade", None) or ""
        semanas_plan = semanas_planejadas(freq_text)

        linha = [desc, str(freq_text)]
        # 26 colunas de semana
        for sem in semanas:
            st_sem, os_num = status_os_na_semana(getattr(pmp, "id", 0), sem)
            txt = ""
            if st_sem == "concluida":
                txt = f"OS #{os_num}" if os_num else ""
            elif st_sem == "gerada":
                txt = f"OS #{os_num}" if os_num else ""
            else:
                # sem OS -> marca se for planejada
                if sem["numero"] in semanas_plan:
                    txt = ""
            linha.append(txt)
        data.append(linha)

    # Aplicar cores por célula (linha a linha, semana a semana)
    for r, pmp in enumerate(pmps, start=1):
        freq_text = getattr(pmp, "frequencia", None) or getattr(pmp, "periodicidade", None) or ""
        semanas_plan = semanas_planejadas(freq_text)
        for c, sem in enumerate(semanas, start=2):  # coluna 0:PMP 1:FREQ; semanas começam no índice 2
            st_sem, _ = status_os_na_semana(getattr(pmp, "id", 0), sem)
            if st_sem == "concluida":
                style.add("BACKGROUND", (c, r), (c, r), VERDE)
            elif st_sem == "gerada":
                style.add("BACKGROUND", (c, r), (c, r), CINZA_ESCURO)
            else:
                if sem["numero"] in semanas_plan:
                    style.add("BACKGROUND", (c, r), (c, r), CINZA_CLARO)

    table = Table(data, colWidths=widths, repeatRows=1)
    table.setStyle(style)
    return table

def _legenda_tabela(estilos_cores):
    VERDE = estilos_cores["VERDE"]
    CINZA_ESCURO = estilos_cores["CINZA_ESCURO"]
    CINZA_CLARO = estilos_cores["CINZA_CLARO"]

    data = [
        ["Legenda:", "", "Concluída", "", "Gerada", "", "Planejada", ""],
    ]
    t = Table(data, colWidths=[22*mm, 8*mm, 22*mm, 8*mm, 22*mm, 8*mm, 22*mm, 8*mm])
    style = TableStyle([
        ("FONT", (0,0), (-1,-1), "Helvetica", 8),
        ("VALIGN", (0,0), (-1,-1), "MIDDLE"),
        ("GRID", (0,0), (-1,-1), 0.25, colors.black),
        ("BACKGROUND", (1,0), (1,0), VERDE),
        ("BACKGROUND", (3,0), (3,0), CINZA_ESCURO),
        ("BACKGROUND", (5,0), (5,0), CINZA_CLARO),
    ])
    t.setStyle(style)
    return t

# ---------- Geração do PDF (duas metades) ----------
def gerar_pdf_visual_paginas(ano:int, equipamentos_por_pagina:int=10):
    semanas = semanas_do_ano(ano)
    semanas_1 = [s for s in semanas if 1 <= s["numero"] <= 26]
    semanas_2 = [s for s in semanas if 27 <= s["numero"] <= 52]

    # Buscar PMPs e agrupar por equipamento
    pmps = PMP.query.order_by(PMP.id.asc()).all()
    grupos = defaultdict(list)
    for pmp in pmps:
        # Ignorar PMPs sem data de início de plano (coerente com versões anteriores)
        data_inicio_plano = _to_date(getattr(pmp, "data_inicio_plano", None))
        if data_inicio_plano is None:
            continue
        equip = getattr(pmp, "equipamento_nome", None) or getattr(pmp, "equipamento", None) or getattr(pmp, "descricao_equipamento", None) or "Equipamento sem nome"
        grupos[equip].append(pmp)

    # Ordenar equipamentos por nome
    equipamentos = sorted(grupos.keys(), key=lambda x: str(x).lower())

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

    # Cores
    estilos_cores = {
        "VERDE": colors.Color(0.4, 0.73, 0.42),
        "CINZA_ESCURO": colors.Color(0.46, 0.46, 0.46),
        "CINZA_CLARO": colors.Color(0.74, 0.74, 0.74),
    }

    def _pagina_metade(semanas_metade, titulo_metade):
        # Cabeçalho
        story.append(Paragraph(f"Plano de 52 Semanas - {ano} ({titulo_metade})", h1))
        story.append(Paragraph(f"Gerado em: {datetime.now().strftime('%d/%m/%Y %H:%M')}", normal))
        story.append(Spacer(1, 6))

        # Paginador por equipamentos
        for i in range(0, len(equipamentos), equipamentos_por_pagina):
            subset = equipamentos[i:i+equipamentos_por_pagina]
            for equip in subset:
                story.append(Paragraph(f"<b>Equipamento:</b> {equip}", h2))
                tabela_1 = _tabela_equipamento(grupos[equip], semanas_metade, estilos_cores)
                story.append(tabela_1)
                story.append(Spacer(1, 6))
            # legenda no fim de cada bloco de página
            story.append(_legenda_tabela(estilos_cores))
            # próxima página, se ainda houver mais equipamentos
            if i + equipamentos_por_pagina < len(equipamentos):
                story.append(PageBreak())

    # Metade 1 (semanas 1–26)
    _pagina_metade(semanas_1, "Semanas 1–26")
    # Nova página para a segunda metade
    story.append(PageBreak())
    # Metade 2 (semanas 27–52)
    _pagina_metade(semanas_2, "Semanas 27–52")

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
            val = linha.get(o, 0.0)
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

# ---------- Rota principal (visual paginado) ----------
@relatorio_52_semanas_bp.route('/api/relatorios/plano-52-semanas', methods=['GET'])
def gerar_relatorio_visual():
    try:
        ano = int(datetime.now().year)
        equipamentos_por_pagina = 10  # conforme solicitado
        pdf = gerar_pdf_visual_paginas(ano, equipamentos_por_pagina=equipamentos_por_pagina)
        fname = f"Plano_52_Semanas_{ano}_visual.pdf"
        return send_file(pdf, as_attachment=True, download_name=fname, mimetype="application/pdf")
    except Exception as e:
        print("Erro ao gerar PDF visual paginado:", e)
        traceback.print_exc()
        return jsonify({"erro": str(e)}), 500
