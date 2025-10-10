# -*- coding: utf-8 -*-
"""
Relatorio Plano 52 Semanas (PDF Visual Paginado) - com LOGS [REL52] e correção de contexto SQLAlchemy
"""

import traceback
import logging
from io import BytesIO
from datetime import datetime, timedelta, date
from collections import defaultdict, OrderedDict
from flask import Blueprint, send_file, jsonify, current_app

# ===== LOGGING =====
logger = logging.getLogger("relatorio_52")
if not logger.handlers:
    handler = logging.StreamHandler()
    fmt = logging.Formatter("[REL52] %(levelname)s: %(message)s")
    handler.setFormatter(fmt)
    logger.addHandler(handler)
logger.setLevel(logging.INFO)

logger.info("🔧 Inicializando módulo relatorio_52_semanas.py")

# ===== OBTÉM DB DO CONTEXTO DO APP =====
try:
    db = current_app.extensions["sqlalchemy"].db
    logger.info("✅ Conectado ao contexto SQLAlchemy existente via current_app")
except Exception as e:
    logger.error("❌ Não foi possível obter SQLAlchemy do current_app: %s", e)
    db = None

# ===== Imports do projeto =====
try:
    from models.pmp_limpo import PMP
    from models.assets import equipamento as EquipamentoModel
    from assets_models import OrdemServico
    logger.info("✅ Imports de modelos concluídos (PMP, equipamento, OrdemServico)")
except Exception as e:
    logger.error("❌ Erro ao importar modelos: %s", e)
    logger.error(traceback.format_exc())

# ===== ReportLab (PDF) =====
from reportlab.lib.pagesizes import A3, landscape
from reportlab.lib import colors
from reportlab.platypus import (
    SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, PageBreak
)
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import mm

relatorio_52_semanas_bp = Blueprint('relatorio_52_semanas', __name__)
logger.info("✅ Blueprint 'relatorio_52_semanas' criado")


# ---------- Utils de data ----------
def _to_date(x):
    if isinstance(x, datetime):
        return x.date()
    if isinstance(x, date):
        return x
    try:
        return datetime.fromisoformat(str(x)).date()
    except Exception:
        return None


def semanas_do_ano(ano: int):
    base = datetime(ano, 1, 1)
    return [{"numero": i + 1,
             "inicio": (base + timedelta(weeks=i)).date(),
             "fim": (base + timedelta(weeks=i, days=6)).date()} for i in range(52)]


# ---------- Frequência ----------
def semanas_planejadas(frequencia: str):
    if not frequencia:
        return set()
    f = frequencia.lower()
    if "diar" in f:
        return set(range(1, 53))
    if "seman" in f:
        return set(range(1, 53))
    if "quinzen" in f:
        return {i for i in range(2, 53, 2)}
    if "mens" in f:
        return {4, 8, 12, 16, 20, 24, 28, 32, 36, 40, 44, 48}
    if "bimes" in f:
        return {8, 16, 24, 32, 40, 48}
    if "trimes" in f:
        return {12, 24, 36, 48}
    if "semest" in f:
        return {26, 52}
    if "anual" in f:
        return {52}
    return set()


# ---------- Status OS ----------
def status_os_na_semana(pmp_id: int, semana: dict):
    ini = datetime.combine(semana["inicio"], datetime.min.time())
    fim = datetime.combine(semana["fim"], datetime.max.time())
    os_ = OrdemServico.query.filter(
        OrdemServico.pmp_id == pmp_id,
        OrdemServico.data_criacao >= ini,
        OrdemServico.data_criacao <= fim
    ).order_by(OrdemServico.id.desc()).first()
    if os_:
        status = (getattr(os_, "status", "") or "").lower()
        os_num = getattr(os_, "id", None)
        if "conclu" in status or "final" in status:
            return "concluida", os_num
        return "gerada", os_num
    return "nao_gerada", None


# ---------- HH por mês ----------
def hh_por_mes_oficina(ano: int):
    ini, fim = datetime(ano, 1, 1), datetime(ano, 12, 31, 23, 59, 59)
    os_conc = OrdemServico.query.filter(
        OrdemServico.status.in_(["concluida", "concluída"]),
        OrdemServico.data_criacao >= ini,
        OrdemServico.data_criacao <= fim
    ).all()
    resumo = defaultdict(lambda: defaultdict(float))
    oficinas = set()
    for os_ in os_conc:
        mes = os_.data_criacao.month
        hh = float(getattr(os_, "hh_total", 0) or 0)
        oficina = getattr(os_, "oficina", None) or "Outros"
        resumo[mes][oficina] += hh
        resumo[mes]["Total"] += hh
        oficinas.add(oficina)
    oficinas = ["Total"] + sorted(o for o in oficinas if o != "Total")
    tabela = [{ "mes": m, **{o: resumo[m].get(o, 0.0) for o in oficinas} } for m in range(1, 13)]
    return oficinas, tabela


# ---------- Geração do PDF ----------
def gerar_pdf_visual_paginas(ano: int, equipamentos_por_pagina: int = 10):
    """
    Gera o PDF do plano 52 semanas em formato A3 paisagem.
    """
    # 🔧 Importes internos para evitar NameError fora do contexto do app
    from models.pmp_limpo import PMP
    from models.assets import equipamento as EquipamentoModel
    from assets_models import OrdemServico

    logger.info("🚀 Iniciando geração do PDF para o ano %s", ano)

    semanas = semanas_do_ano(ano)
    semanas_1 = [s for s in semanas if s["numero"] <= 26]
    semanas_2 = [s for s in semanas if s["numero"] > 26]

    pmps = PMP.query.order_by(PMP.id.asc()).all()
    grupos = defaultdict(list)

    for pmp in pmps:
        equip_id = getattr(pmp, "equipamento_id", None)
        nome_equip = "Equipamento sem nome"
        try:
            if equip_id:
                eq = EquipamentoModel.query.get(equip_id)
                if eq and getattr(eq, "descricao", None):
                    nome_equip = eq.descricao
        except Exception as e:
            logger.error("❌ Erro ao obter nome do equipamento (%s): %s", equip_id, e)
        grupos[nome_equip].append(pmp)

    equipamentos = sorted(grupos.keys(), key=str.lower)
    buf = BytesIO()
    doc = SimpleDocTemplate(buf, pagesize=landscape(A3), leftMargin=10 * mm, rightMargin=10 * mm)
    story = []
    st = getSampleStyleSheet()
    h1, h2, normal = st["Heading1"], st["Heading2"], st["Normal"]
    h1.fontSize, h2.fontSize, normal.fontSize = 16, 12, 8

    estilos = {
        "VERDE": colors.Color(0.4, 0.73, 0.42),
        "CINZA_ESCURO": colors.Color(0.46, 0.46, 0.46),
        "CINZA_CLARO": colors.Color(0.74, 0.74, 0.74),
    }

    def desenhar_metade(semanas_metade, titulo):
        story.append(Paragraph(f"Plano de 52 Semanas - {ano} ({titulo})", h1))
        story.append(Paragraph(f"Gerado em {datetime.now():%d/%m/%Y %H:%M}", normal))
        story.append(Spacer(1, 6))
        for i in range(0, len(equipamentos), equipamentos_por_pagina):
            subset = equipamentos[i:i + equipamentos_por_pagina]
            for equip in subset:
                story.append(Paragraph(f"<b>Equipamento:</b> {equip}", h2))
                table_data = [["PMP", "Freq."] + [str(s["numero"]) for s in semanas_metade]]
                for pmp in grupos[equip]:
                    freq = getattr(pmp, "frequencia", "") or getattr(pmp, "periodicidade", "")
                    linha = [pmp.descricao, freq]
                    sem_plan = semanas_planejadas(freq)
                    for sem in semanas_metade:
                        st_sem, os_num = status_os_na_semana(pmp.id, sem)
                        txt = f"OS #{os_num}" if os_num else ""
                        if st_sem == "nao_gerada" and sem["numero"] not in sem_plan:
                            txt = ""
                        linha.append(txt)
                    table_data.append(linha)
                widths = [60 * mm, 25 * mm] + [10 * mm] * len(semanas_metade)
                t = Table(table_data, colWidths=widths)
                s = TableStyle([("GRID", (0, 0), (-1, -1), 0.25, colors.black),
                                ("FONT", (0, 0), (-1, -1), "Helvetica", 7)])
                for r in range(1, len(table_data)):
                    freq = table_data[r][1]
                    sem_plan = semanas_planejadas(freq)
                    for c, sem in enumerate(semanas_metade, start=2):
                        st_sem, _ = status_os_na_semana(grupos[equip][r - 1].id, sem)
                        if st_sem == "concluida":
                            s.add("BACKGROUND", (c, r), (c, r), estilos["VERDE"])
                        elif st_sem == "gerada":
                            s.add("BACKGROUND", (c, r), (c, r), estilos["CINZA_ESCURO"])
                        elif sem["numero"] in sem_plan:
                            s.add("BACKGROUND", (c, r), (c, r), estilos["CINZA_CLARO"])
                t.setStyle(s)
                story.append(t)
                story.append(Spacer(1, 6))
            if i + equipamentos_por_pagina < len(equipamentos):
                story.append(PageBreak())

    desenhar_metade(semanas_1, "Semanas 1–26")
    story.append(PageBreak())
    desenhar_metade(semanas_2, "Semanas 27–52")

    # HH por oficina
    oficinas, tabela_hh = hh_por_mes_oficina(ano)
    story.append(PageBreak())
    story.append(Paragraph("Resumo de HH por mês e oficina", h2))
    data_hh = [["Mês"] + oficinas]
    meses = ["Jan", "Fev", "Mar", "Abr", "Mai", "Jun", "Jul", "Ago", "Set", "Out", "Nov", "Dez"]
    for l in tabela_hh:
        linha = [meses[l["mes"] - 1]] + [round(l[o], 2) for o in oficinas]
        data_hh.append(linha)
    t_hh = Table(data_hh, colWidths=[35 * mm] + [25 * mm] * len(oficinas))
    t_hh.setStyle(TableStyle([
        ("GRID", (0, 0), (-1, -1), 0.25, colors.black),
        ("BACKGROUND", (0, 0), (-1, 0), colors.whitesmoke),
        ("FONT", (0, 0), (-1, -1), "Helvetica", 8),
    ]))
    story.append(t_hh)

    doc.build(story)
    buf.seek(0)
    return buf


@relatorio_52_semanas_bp.route('/api/relatorios/plano-52-semanas', methods=['GET'])
def gerar_relatorio_visual():
    logger.info("🌐 GET /api/relatorios/plano-52-semanas recebido")
    try:
        ano = datetime.now().year
        pdf = gerar_pdf_visual_paginas(ano)
        fname = f"Plano_52_Semanas_{ano}_visual.pdf"
        logger.info("📦 Enviando arquivo %s", fname)
        return send_file(pdf, as_attachment=True, download_name=fname, mimetype="application/pdf")
    except Exception as e:
        logger.error("❌ Erro ao gerar PDF: %s", e)
        logger.error(traceback.format_exc())
        return jsonify({"erro": str(e)}), 500
