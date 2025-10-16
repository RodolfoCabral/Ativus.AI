"""
Relatório de Plano de 52 Semanas
Gera PDF com cronograma anual de manutenções preventivas
Versão corrigida com consultas SQL ajustadas para a estrutura real da BD
"""

import io
import logging
from datetime import datetime, timedelta
from collections import defaultdict
from flask import Blueprint, current_app, send_file, jsonify
from flask_login import login_required, current_user
from sqlalchemy import text




# Configuração básica do logger
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

# Formato do log
formatter = logging.Formatter('%(asctime)s [%(levelname)s] %(message)s')

# Handler para console (pode adicionar um FileHandler se quiser gravar em arquivo)
console_handler = logging.StreamHandler()
console_handler.setFormatter(formatter)
logger.addHandler(console_handler)

# ReportLab imports
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib import colors
from reportlab.lib.units import mm
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, PageBreak
from reportlab.lib.styles import getSampleStyleSheet






# Blueprint
relatorio_52_semanas_bp = Blueprint('relatorio_52_semanas', __name__)

# ---------- Funções de consulta SQL direta ----------
def executar_sql(query, params=None):
    """Executa consulta SQL direta usando a conexão do Flask-SQLAlchemy."""
    try:
        from models import db
        result = db.session.execute(text(query), params or {})
        return result.fetchall()
    except Exception as e:
        logger.error(f"[REL52] ❌ Erro na consulta SQL: {e}")
        # Em caso de erro, fazer rollback para não afetar próximas consultas
        try:
            from models import db
            db.session.rollback()
        except:
            pass
        return []

def buscar_equipamentos(empresa):
    """Busca equipamentos usando SQL direto com colunas básicas."""
    query = """
    SELECT id, descricao, tag
    FROM equipamentos 
    WHERE empresa = :empresa
    ORDER BY descricao
    """
    return executar_sql(query, {'empresa': empresa})

def buscar_pmps(equipamento_id):
    """Busca PMPs de um equipamento usando SQL direto."""
    query = """
    SELECT id, codigo, descricao, frequencia
    FROM pmps 
    WHERE equipamento_id = :equipamento_id
    ORDER BY codigo
    """
    return executar_sql(query, {'equipamento_id': equipamento_id})

def buscar_os_semana(pmp_id, data_inicio, data_fim):
    """Busca OS de uma PMP em uma semana específica usando SQL direto."""
    query = """
    SELECT id, status, data_criacao
    FROM ordens_servico 
    WHERE pmp_id = :pmp_id
    AND data_criacao >= :data_inicio
    AND data_criacao <= :data_fim
    ORDER BY data_criacao DESC
    LIMIT 1
    """
    return executar_sql(query, {
        'pmp_id': pmp_id,
        'data_inicio': data_inicio,
        'data_fim': data_fim
    })

def buscar_os_ano(ano):
    """Busca todas as OS do ano usando SQL direto com colunas básicas."""
    query = """
    SELECT id, status, data_criacao
    FROM ordens_servico 
    WHERE EXTRACT(YEAR FROM data_criacao) = :ano
    ORDER BY data_criacao
    """
    return executar_sql(query, {'ano': ano})

def verificar_estrutura_tabelas():
    """Verifica quais colunas existem nas tabelas principais."""
    logger.info("[REL52] 🔍 Verificando estrutura das tabelas...")
    
    # Verificar colunas da tabela equipamentos
    query_equipamentos = """
    SELECT column_name 
    FROM information_schema.columns 
    WHERE table_name = 'equipamentos'
    ORDER BY ordinal_position
    """
    colunas_equipamentos = executar_sql(query_equipamentos)
    logger.info(f"[REL52] 📋 Colunas equipamentos: {[col[0] for col in colunas_equipamentos]}")
    
    # Verificar colunas da tabela pmps
    query_pmps = """
    SELECT column_name 
    FROM information_schema.columns 
    WHERE table_name = 'pmps'
    ORDER BY ordinal_position
    """
    colunas_pmps = executar_sql(query_pmps)
    logger.info(f"[REL52] 📋 Colunas pmps: {[col[0] for col in colunas_pmps]}")
    
    # Verificar colunas da tabela ordens_servico
    query_os = """
    SELECT column_name 
    FROM information_schema.columns 
    WHERE table_name = 'ordens_servico'
    ORDER BY ordinal_position
    """
    colunas_os = executar_sql(query_os)
    logger.info(f"[REL52] 📋 Colunas ordens_servico: {[col[0] for col in colunas_os]}")

# ---------- Cálculo de semanas ----------
def calcular_semanas_ano(ano):
    """Calcula as 52 semanas do ano."""
    semanas = []
    # Primeira segunda-feira do ano
    primeiro_dia = datetime(ano, 1, 1)
    dias_para_segunda = (7 - primeiro_dia.weekday()) % 7
    if primeiro_dia.weekday() != 0:  # Se não é segunda
        dias_para_segunda = 7 - primeiro_dia.weekday()
    
    primeira_segunda = primeiro_dia + timedelta(days=dias_para_segunda)
    
    for i in range(52):
        inicio_semana = primeira_segunda + timedelta(weeks=i)
        fim_semana = inicio_semana + timedelta(days=6)
        semanas.append({
            'numero': i + 1,
            'inicio': inicio_semana.date(),
            'fim': fim_semana.date()
        })
    
    return semanas

# ---------- Frequências de PMP ----------
def semanas_planejadas(frequencia):
    """Retorna as semanas em que a PMP deve ser executada baseado na frequência."""
    freq = (frequencia or "").lower().strip()
    
    if "diario" in freq or "diária" in freq:
        return list(range(1, 53))  # Todas as semanas
    elif "semanal" in freq:
        return list(range(1, 53))  # Todas as semanas
    elif "quinzenal" in freq:
        return list(range(1, 53, 2))  # A cada 2 semanas
    elif "mensal" in freq:
        return list(range(1, 53, 4))  # A cada 4 semanas
    elif "bimestral" in freq:
        return list(range(1, 53, 8))  # A cada 8 semanas
    elif "trimestral" in freq:
        return list(range(1, 53, 12))  # A cada 12 semanas
    elif "semestral" in freq:
        return list(range(1, 53, 26))  # A cada 26 semanas
    elif "anual" in freq:
        return [1]  # Apenas primeira semana
    else:
        return []  # Frequência desconhecida

# ---------- Função: status_os_na_semana ----------
def status_os_na_semana(pmp_id, semana):
    """Retorna o status e número da OS associada à PMP naquela semana."""
    try:
        logger.debug(f"[REL52] 🔍 Iniciando verificação de OS da PMP {pmp_id} na semana {semana}")

        ini = datetime.combine(semana["inicio"], datetime.min.time())
        fim = datetime.combine(semana["fim"], datetime.max.time())

        logger.debug(f"[REL52] Intervalo calculado: {ini} → {fim}")

        # Buscar OS da PMP nesta semana
        os_list = buscar_os_semana(pmp_id, ini, fim)
        logger.debug(f"[REL52] 🔎 Resultado da busca de OS: {os_list}")

        if os_list:
            os_row = os_list[0]  # Primeira OS encontrada
            os_num = os_row[0]  # ID da OS
            status = (os_row[1] or "").lower()  # status da OS

            logger.info(f"[REL52] ✅ OS encontrada para PMP {pmp_id}: ID={os_num}, Status={status}")

            if "concl" in status or "final" in status:
                logger.debug(f"[REL52] OS {os_num} está concluída.")
                return "concluida", os_num

            logger.debug(f"[REL52] OS {os_num} está apenas gerada (não concluída).")
            return "gerada", os_num

        logger.warning(f"[REL52] ⚠️ Nenhuma OS encontrada para PMP {pmp_id} nesta semana.")
        return "nao_gerada", None

    except Exception as e:
        logger.exception(f"[REL52] ❌ Erro ao consultar OS (PMP={pmp_id}): {e}")
        return "erro", None

# ---------- Função: status_os_na_semanahh_por_mes_oficina ----------
def hh_por_mes_oficina(ano):
    """
    Calcula HH por mês e por oficina com base nas OS concluídas,
    considerando o valor de HH armazenado em 'ordens_servico.hh'
    e a oficina associada à PMP.
    """
    try:
        logger.info(f"[REL52] 🚀 Iniciando cálculo de HH por mês/oficina para o ano {ano}")

        # Consulta SQL corrigida (usa os.hh)
        query = """
        SELECT 
            os.id AS os_id,
            os.status AS status,
            os.data_criacao AS data_criacao,
            p.oficina AS oficina,
            COALESCE(os.hh, 0) AS hh_real
        FROM ordens_servico os
        LEFT JOIN pmps p ON os.pmp_id = p.id
        WHERE EXTRACT(YEAR FROM os.data_criacao) = :ano
        ORDER BY os.data_criacao
        """
        os_detalhadas = executar_sql(query, {'ano': ano})

        if not os_detalhadas:
            logger.warning(f"[REL52] ⚠️ Nenhuma OS encontrada para o ano {ano}.")
            return [], []

        logger.info(f"[REL52] 📊 Encontradas {len(os_detalhadas)} OS com dados de oficina e HH real.")

        resumo = defaultdict(lambda: defaultdict(float))
        oficinas = set()

        for i, os_row in enumerate(os_detalhadas, start=1):
            os_id, status, data_criacao, oficina, hh_real = os_row

            if not data_criacao:
                logger.warning(f"[REL52] ⚠️ OS {os_id} sem data_criacao válida, ignorada.")
                continue

            mes = data_criacao.month
            oficina = oficina or "Não informada"
            hh = float(hh_real or 0)

            # Ignora HH nulos ou 0
            if hh <= 0:
                logger.debug(f"[REL52] ⚠️ OS {os_id} possui HH=0, ignorada.")
                continue

            resumo[mes][oficina] += hh
            resumo[mes]["Total"] += hh
            oficinas.add(oficina)

            logger.debug(f"[REL52] ➕ OS {os_id}: {hh}h adicionadas à oficina '{oficina}' (mês {mes})")

        logger.info(f"[REL52] 📈 Oficinas encontradas: {list(oficinas)}")

    except Exception as e:
        logger.exception(f"[REL52] ❌ Erro ao calcular HH por mês/oficina: {e}")
        return [], []

    # Organizar oficinas (Total primeiro)
    oficinas = ["Total"] + sorted(o for o in oficinas if o != "Total")

    # Criar tabela mensal
    meses = [
        "Janeiro", "Fevereiro", "Março", "Abril", "Maio", "Junho",
        "Julho", "Agosto", "Setembro", "Outubro", "Novembro", "Dezembro"
    ]
    tabela = []

    for m in range(1, 13):
        linha = {"mes": meses[m-1]}
        for oficina in oficinas:
            valor = resumo[m].get(oficina, 0.0)
            linha[oficina] = valor
        tabela.append(linha)
        logger.debug(f"[REL52] 📅 Mês {m:02d} ({meses[m-1]}): {linha}")

    logger.info(f"[REL52] ✅ Cálculo de HH concluído com sucesso para {ano}")
    return oficinas, tabela


# ---------- Geração do PDF ----------
def gerar_pdf_52_semanas(ano):
def gerar_pdf_52_semanas(ano):
    """Gera PDF com 1 equipamento por página, 2 tabelas (1–26 e 27–52), conforme modelo visual."""
    logger.info("[REL52] 🚀 Gerando plano de 52 semanas (ano=%s)", ano)

    try:
        verificar_estrutura_tabelas()
        semanas_ano = calcular_semanas_ano(ano)
        equipamentos = buscar_equipamentos(current_user.company)
        logger.info(f"[REL52] 🔧 {len(equipamentos)} equipamentos encontrados.")

        buffer = io.BytesIO()
        doc = SimpleDocTemplate(
            buffer,
            pagesize=landscape(A4),
            rightMargin=10 * mm,
            leftMargin=10 * mm,
            topMargin=15 * mm,
            bottomMargin=15 * mm,
        )

        styles = getSampleStyleSheet()
        title_style = styles["Title"]
        heading_style = styles["Heading2"]
        normal_style = styles["Normal"]
        elements = []

        # Cabeçalho geral
        elements.append(Paragraph("PLANO DE MANUTENÇÃO PREVENTIVA - 52 SEMANAS", title_style))
        elements.append(Paragraph(f"Ano: {ano}", heading_style))
        elements.append(Paragraph(f"Gerado em: {datetime.now().strftime('%d/%m/%Y %H:%M')}", normal_style))
        elements.append(Spacer(1, 20))

        # Se não há equipamentos
        if not equipamentos:
            elements.append(Paragraph("⚠️ Nenhum equipamento encontrado para esta empresa.", normal_style))
            doc.build(elements)
            return buffer

        # ---------- LOOP DOS EQUIPAMENTOS ----------
        for equipamento in equipamentos:
            equipamento_id = equipamento[0]
            equipamento_nome = equipamento[1]
            pmps = buscar_pmps(equipamento_id)
            logger.info(f"[REL52] 📋 Equipamento {equipamento_nome}: {len(pmps)} PMPs")

            if not pmps:
                continue

            # Título do equipamento
            elements.append(Paragraph(f"Equipamento: {equipamento_nome}", heading_style))
            elements.append(Spacer(1, 5))

            def gerar_tabela(inicio, fim):
                header = ["PMP"] + [str(i) for i in range(inicio, fim + 1)]
                table_data = [header]

                for pmp in pmps:
                    pmp_id = pmp[0]
                    pmp_codigo = pmp[1] or f"PMP-{pmp_id}"
                    pmp_freq = pmp[3] or "mensal"
                    semanas_exec = semanas_planejadas(pmp_freq)

                    row = [pmp_codigo]
                    for semana in semanas_ano[inicio - 1:fim]:
                        status, os_num = status_os_na_semana(pmp_id, semana)
                        if os_num:
                            texto = str(os_num)
                        elif semana["numero"] in semanas_exec:
                            texto = "*"
                        else:
                            texto = ""
                        row.append(texto)
                    table_data.append(row)

                col_widths = [30 * mm] + [6 * mm] * (fim - inicio + 1)
                table = Table(table_data, colWidths=col_widths)

                # Estilo
                estilo = TableStyle([
                    ('GRID', (0, 0), (-1, -1), 0.4, colors.black),
                    ('FONT', (0, 0), (-1, -1), 'Helvetica', 7),
                    ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                    ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                    ('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey),
                    ('FONTNAME', (0, 1), (-1, -1), 'Helvetica-Bold'),
                ])

                # Colorir conforme status
                for row_idx in range(1, len(table_data)):
                    pmp = pmps[row_idx - 1]
                    pmp_id = pmp[0]
                    pmp_freq = pmp[3] or "mensal"
                    semanas_exec = semanas_planejadas(pmp_freq)

                    for col_idx in range(1, len(table_data[row_idx])):
                        semana_num = inicio + col_idx - 1
                        if semana_num > fim:
                            continue
                        semana = semanas_ano[semana_num - 1]
                        status, _ = status_os_na_semana(pmp_id, semana)

                        if status == "concluida":
                            estilo.add('BACKGROUND', (col_idx, row_idx), (col_idx, row_idx),
                                       colors.Color(0.2, 0.8, 0.2))  # Verde
                            estilo.add('TEXTCOLOR', (col_idx, row_idx), (col_idx, row_idx), colors.white)
                        elif status == "gerada":
                            estilo.add('BACKGROUND', (col_idx, row_idx), (col_idx, row_idx),
                                       colors.Color(0.4, 0.4, 0.4))  # Cinza escuro
                            estilo.add('TEXTCOLOR', (col_idx, row_idx), (col_idx, row_idx), colors.white)
                        elif semana_num in semanas_exec:
                            estilo.add('BACKGROUND', (col_idx, row_idx), (col_idx, row_idx),
                                       colors.Color(0.95, 0.95, 0.95))  # Cinza claro

                table.setStyle(estilo)
                return table

            # Tabela 1 (1–26)
            table1 = gerar_tabela(1, 26)
            elements.append(table1)
            elements.append(Spacer(1, 10))

            # Tabela 2 (27–52)
            table2 = gerar_tabela(27, 52)
            elements.append(table2)
            elements.append(PageBreak())

        # ---------- Resumo HH ----------
        oficinas, tabela_hh = hh_por_mes_oficina(ano)
        if tabela_hh:
            elements.append(Paragraph("RESUMO DE HORAS-HOMEM POR MÊS E OFICINA", heading_style))
            header_hh = ['Mês'] + oficinas
            data_hh = [header_hh]
            for linha in tabela_hh:
                row = [linha['mes']] + [f"{linha.get(o, 0.0):.1f}" for o in oficinas]
                data_hh.append(row)

            table_hh = Table(data_hh)
            estilo_hh = TableStyle([
                ('GRID', (0, 0), (-1, -1), 0.5, colors.black),
                ('FONT', (0, 0), (-1, -1), 'Helvetica', 8),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                ('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey),
                ('BACKGROUND', (0, 0), (0, -1), colors.lightgrey),
            ])
            table_hh.setStyle(estilo_hh)
            elements.append(table_hh)

        # Monta o PDF
        doc.build(elements)
        buffer.seek(0)
        logger.info("[REL52] ✅ PDF final gerado com sucesso")
        return buffer

    except Exception as e:
        logger.exception("[REL52] ❌ Erro ao gerar PDF: %s", e)
        raise

# ---------- Rota da API ----------
@relatorio_52_semanas_bp.route('/api/relatorios/plano-52-semanas', methods=['GET'])
@login_required
def gerar_relatorio_52_semanas():
    """Endpoint para gerar o relatório de 52 semanas."""
    try:
        ano = datetime.now().year
        
        # Gerar PDF
        pdf_buffer = gerar_pdf_52_semanas(ano)
        
        # Retornar arquivo
        return send_file(
            pdf_buffer,
            as_attachment=True,
            download_name=f'Plano_52_Semanas_{ano}.pdf',
            mimetype='application/pdf'
        )
        
    except Exception as e:
        current_app.logger.error(f"Erro ao gerar relatório: {e}")
        return jsonify({'error': 'Erro ao gerar relatório'}), 500
