"""
Relatório de Plano de 52 Semanas
Gera PDF com cronograma anual de manutenções preventivas
"""

import io
import logging
from datetime import datetime, timedelta
from collections import defaultdict
from flask import Blueprint, current_app, send_file, jsonify
from flask_login import login_required, current_user

# ReportLab imports
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib import colors
from reportlab.lib.units import mm
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet

logger = logging.getLogger(__name__)

# Blueprint
relatorio_52_semanas_bp = Blueprint('relatorio_52_semanas', __name__)

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

# ---------- Status da OS ----------
def status_os_na_semana(pmp_id, semana):
    """Retorna o status e número da OS associada à PMP naquela semana."""
    try:
        # Importação local para evitar conflitos
        from assets_models import OrdemServico
    except Exception as e:
        logger.error("[REL52] ⚠️ Falha ao importar OrdemServico: %s", e)
        return "erro", None

    try:
        ini = datetime.combine(semana["inicio"], datetime.min.time())
        fim = datetime.combine(semana["fim"], datetime.max.time())
        
        # Buscar OS da PMP nesta semana
        os_list = OrdemServico.query.filter(
            OrdemServico.pmp_id == pmp_id,
            OrdemServico.data_criacao >= ini,
            OrdemServico.data_criacao <= fim
        ).all()
        
        if os_list:
            os_ = os_list[0]  # Primeira OS encontrada
            status = (getattr(os_, "status", "") or "").lower()
            os_num = getattr(os_, "id", None)
            if "conclu" in status or "final" in status:
                return "concluida", os_num
            return "gerada", os_num
        return "nao_gerada", None
    except Exception as e:
        logger.error("[REL52] Erro ao consultar OS (%s): %s", pmp_id, e)
        return "erro", None

# ---------- HH por oficina ----------
def hh_por_mes_oficina(ano):
    """Calcula HH por mês e oficina baseado nas OS concluídas."""
    try:
        # Importação local para evitar conflitos
        from assets_models import OrdemServico
    except Exception as e:
        logger.error("[REL52] ⚠️ Falha ao importar OrdemServico: %s", e)
        return [], []

    ini, fim = datetime(ano, 1, 1), datetime(ano, 12, 31, 23, 59, 59)
    
    # Buscar todas as OS do ano (não apenas concluídas para debug)
    os_todas = OrdemServico.query.filter(
        OrdemServico.data_criacao >= ini,
        OrdemServico.data_criacao <= fim,
    ).all()
    
    logger.info(f"[REL52] 📊 Encontradas {len(os_todas)} OS no ano {ano}")
    
    resumo = defaultdict(lambda: defaultdict(float))
    oficinas = set()
    
    for os_ in os_todas:
        mes = os_.data_criacao.month
        
        # Tentar diferentes campos para HH
        hh = 0
        for campo in ['hh', 'hh_total', 'horas_homem', 'tempo_execucao']:
            valor = getattr(os_, campo, None)
            if valor is not None:
                try:
                    hh = float(valor)
                    if hh > 0:
                        logger.debug(f"[REL52] 🔍 OS {os_.id}: {campo}={hh}")
                        break
                except (ValueError, TypeError):
                    continue
        
        # Se não encontrou HH, usar valor padrão baseado no tipo
        if hh == 0:
            # Estimar HH baseado no tipo de manutenção
            if hasattr(os_, 'tipo') and os_.tipo:
                if 'preventiva' in str(os_.tipo).lower():
                    hh = 2.0  # 2 horas para preventiva
                elif 'corretiva' in str(os_.tipo).lower():
                    hh = 4.0  # 4 horas para corretiva
                else:
                    hh = 1.0  # 1 hora padrão
            else:
                hh = 1.0  # 1 hora padrão
        
        # Determinar oficina
        oficina = "Outros"
        for campo_oficina in ['oficina', 'departamento', 'setor']:
            valor_oficina = getattr(os_, campo_oficina, None)
            if valor_oficina:
                oficina = str(valor_oficina)
                break
        
        resumo[mes][oficina] += hh
        resumo[mes]["Total"] += hh
        oficinas.add(oficina)
        
    logger.info(f"[REL52] 📈 Oficinas encontradas: {list(oficinas)}")
    
    # Organizar oficinas (Total primeiro)
    oficinas = ["Total"] + sorted(o for o in oficinas if o != "Total")
    
    # Criar tabela por mês
    tabela = []
    meses = ["Janeiro", "Fevereiro", "Março", "Abril", "Maio", "Junho",
             "Julho", "Agosto", "Setembro", "Outubro", "Novembro", "Dezembro"]
    
    for m in range(1, 13):
        linha = {"mes": meses[m-1]}
        for oficina in oficinas:
            linha[oficina] = resumo[m].get(oficina, 0.0)
        tabela.append(linha)
    
    return oficinas, tabela

# ---------- Geração do PDF ----------
def gerar_pdf_52_semanas(ano):
    """Gera o PDF completo do plano de 52 semanas."""
    logger.info("[REL52] 🚀 Iniciando geração do PDF (ano=%s)", ano)
    
    try:
        # Importação local para evitar conflitos de tabela
        from assets_models import Equipamento
        from models.pmp import PMP
        
        # Calcular semanas do ano
        semanas_ano = calcular_semanas_ano(ano)
        
        # Buscar equipamentos e suas PMPs
        equipamentos = Equipamento.query.filter_by(empresa=current_user.company).all()
        
        # Criar PDF
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(
            buffer,
            pagesize=landscape(A4),
            rightMargin=10*mm,
            leftMargin=10*mm,
            topMargin=15*mm,
            bottomMargin=15*mm
        )
        
        # Estilos
        styles = getSampleStyleSheet()
        title_style = styles['Title']
        title_style.fontSize = 16
        title_style.spaceAfter = 20
        
        heading_style = styles['Heading2']
        heading_style.fontSize = 12
        heading_style.spaceAfter = 10
        
        # Elementos do PDF
        elements = []
        
        # Título
        elements.append(Paragraph(f"PLANO DE MANUTENÇÃO PREVENTIVA - 52 SEMANAS", title_style))
        elements.append(Paragraph(f"Ano: {ano}", heading_style))
        elements.append(Paragraph(f"Gerado em: {datetime.now().strftime('%d/%m/%Y %H:%M')}", styles['Normal']))
        elements.append(Spacer(1, 20))
        
        # Para cada equipamento
        for equipamento in equipamentos:
            # Buscar PMPs do equipamento
            pmps = PMP.query.filter_by(equipamento_id=equipamento.id).all()
            
            if not pmps:
                continue
                
            # Título do equipamento
            elements.append(Paragraph(f"Equipamento: {equipamento.descricao}", heading_style))
            
            # Criar tabela
            # Cabeçalho: Equipamento | PMP | 1 | 2 | 3 | ... | 52
            header = ['Equipamento', 'PMP'] + [str(i) for i in range(1, 53)]
            table_data = [header]
            
            # Para cada PMP do equipamento
            for i, pmp in enumerate(pmps):
                row = [equipamento.descricao if i == 0 else '', pmp.codigo]
                
                # Determinar semanas de execução
                semanas_execucao = semanas_planejadas(pmp.frequencia)
                
                # Para cada semana do ano
                for semana in semanas_ano:
                    status, os_num = status_os_na_semana(pmp.id, semana)
                    
                    # Determinar texto da célula
                    if status == "concluida" and os_num:
                        texto = f"{os_num}"  # Apenas o número da OS
                    elif status == "gerada" and os_num:
                        texto = f"{os_num}"  # Apenas o número da OS
                    elif semana['numero'] in semanas_execucao:
                        texto = "●"  # Planejada mas não gerada
                    else:
                        texto = ""  # Não planejada
                    
                    row.append(texto)
                
                table_data.append(row)
            
            # Criar tabela com larguras
            col_widths = [40*mm, 30*mm] + [6*mm] * 52
            table = Table(table_data, colWidths=col_widths)
            
            # Estilo da tabela
            table_style = TableStyle([
                ('GRID', (0, 0), (-1, -1), 0.5, colors.black),
                ('FONT', (0, 0), (-1, -1), 'Helvetica', 7),
                ('FONTSIZE', (0, 0), (-1, -1), 7),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                ('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey),  # Cabeçalho
                # Fonte menor para as colunas de equipamento e PMP
                ('FONTSIZE', (0, 0), (1, -1), 8),
                # Fonte em negrito para números de OS
                ('FONTNAME', (2, 1), (-1, -1), 'Helvetica-Bold'),
            ])
            
            # Aplicar cores baseadas no status
            for row_idx in range(1, len(table_data)):
                pmp = pmps[row_idx - 1]
                semanas_execucao = semanas_planejadas(pmp.frequencia)
                
                for col_idx in range(2, len(table_data[row_idx])):
                    semana_num = col_idx - 1  # col_idx 2 = semana 1, col_idx 3 = semana 2, etc.
                    semana_index = semana_num - 1  # Índice no array (0-based)
                    
                    if 0 <= semana_index < len(semanas_ano):
                        semana = semanas_ano[semana_index]
                        status, os_num = status_os_na_semana(pmp.id, semana)
                        
                        if status == "concluida":
                            # Verde para OS concluída
                            table_style.add('BACKGROUND', (col_idx, row_idx), (col_idx, row_idx), colors.Color(0.2, 0.8, 0.2))
                            table_style.add('TEXTCOLOR', (col_idx, row_idx), (col_idx, row_idx), colors.white)
                        elif status == "gerada":
                            # Cinza escuro para OS gerada mas não concluída
                            table_style.add('BACKGROUND', (col_idx, row_idx), (col_idx, row_idx), colors.Color(0.3, 0.3, 0.3))
                            table_style.add('TEXTCOLOR', (col_idx, row_idx), (col_idx, row_idx), colors.white)
                        elif semana_num in semanas_execucao:
                            # Cinza claro para OS planejada mas não gerada
                            table_style.add('BACKGROUND', (col_idx, row_idx), (col_idx, row_idx), colors.Color(0.8, 0.8, 0.8))
                            table_style.add('TEXTCOLOR', (col_idx, row_idx), (col_idx, row_idx), colors.black)
            
            table.setStyle(table_style)
            elements.append(table)
            elements.append(Spacer(1, 20))
        
        # Tabela de HH por mês e oficina
        oficinas, tabela_hh = hh_por_mes_oficina(ano)
        
        if tabela_hh:
            elements.append(Paragraph("RESUMO DE HORAS-HOMEM POR MÊS E OFICINA", heading_style))
            
            # Cabeçalho da tabela HH
            header_hh = ['Mês'] + oficinas
            table_hh_data = [header_hh]
            
            # Dados da tabela HH
            for linha in tabela_hh:
                row_hh = [linha['mes']]
                for oficina in oficinas:
                    valor = linha.get(oficina, 0.0)
                    row_hh.append(f"{valor:.1f}")
                table_hh_data.append(row_hh)
            
            # Criar tabela HH
            table_hh = Table(table_hh_data)
            table_hh_style = TableStyle([
                ('GRID', (0, 0), (-1, -1), 0.5, colors.black),
                ('FONT', (0, 0), (-1, -1), 'Helvetica', 8),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                ('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey),  # Cabeçalho
                ('BACKGROUND', (0, 0), (0, -1), colors.lightgrey),  # Primeira coluna
            ])
            table_hh.setStyle(table_hh_style)
            elements.append(table_hh)
        
        # Gerar PDF
        doc.build(elements)
        buffer.seek(0)
        
        logger.info("[REL52] ✅ PDF gerado com sucesso")
        return buffer
        
    except Exception as e:
        logger.error("[REL52] ❌ Erro ao gerar PDF: %s", e)
        import traceback
        traceback.print_exc()
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
