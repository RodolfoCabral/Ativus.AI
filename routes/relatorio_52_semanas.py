from flask import Blueprint, jsonify, request, send_file
from flask_login import login_required, current_user
from models import db
from assets_models import Equipamento, OrdemServico
from models.pmp_limpo import PMP
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, PageBreak
from reportlab.lib.units import inch
from datetime import datetime, timedelta, date
import io
import calendar

relatorio_52_semanas_bp = Blueprint('relatorio_52_semanas', __name__)

# Helper to normalize date/datetime and add debug logs
def _to_date(x):
    try:
        if isinstance(x, datetime):
            return x.date()
        return x
    except Exception as e:
        print(f"DEBUG[to_date]: error converting {x!r} -> {e}")
        return x

def calcular_semanas_ano(ano=None):
    """Calcula as 52 semanas do ano"""
    if ano is None:
        ano = datetime.now().year
    
    # Primeira segunda-feira do ano
    primeiro_dia = datetime(ano, 1, 1)
    dias_ate_segunda = (7 - primeiro_dia.weekday()) % 7
    if primeiro_dia.weekday() != 0:  # Se não é segunda
        primeira_segunda = primeiro_dia + timedelta(days=dias_ate_segunda)
    else:
        primeira_segunda = primeiro_dia
    
    semanas = []
    for i in range(52):
        inicio_semana = primeira_segunda + timedelta(weeks=i)
        fim_semana = inicio_semana + timedelta(days=6)
        semanas.append({
            'numero': i + 1,
            'inicio': inicio_semana,
            'fim': fim_semana,
            'mes': inicio_semana.month
        })
    
    return semanas

def determinar_semanas_pmp(pmp, semanas_ano):
    """Determina em quais semanas a PMP deve ser executada"""
    if not pmp.data_inicio_plano:
        return []
    
    frequencia = pmp.frequencia.lower() if pmp.frequencia else ''
    semanas_execucao = []
    
    # Encontrar semana de início
    semana_inicio = None
    for semana in semanas_ano:
        print("DEBUG[determinar_semanas_pmp]:", f"PMP {{pmp.id}} data_inicio={{pmp.data_inicio_plano}} ({{type(pmp.data_inicio_plano)}})", f"semana_inicio={{_to_date(semana['inicio'])}}", f"semana_fim={{_to_date(semana['fim'])}}")
        if _to_date(semana['inicio']) <= _to_date(pmp.data_inicio_plano) <= _to_date(semana['fim']):
            semana_inicio = semana['numero']
            break
    
    if not semana_inicio:
        return []
    
    # Calcular frequência em semanas
    if frequencia == 'semanal':
        intervalo = 1
    elif frequencia == 'quinzenal':
        intervalo = 2
    elif frequencia == 'mensal':
        intervalo = 4
    elif frequencia == 'bimestral':
        intervalo = 8
    elif frequencia == 'trimestral':
        intervalo = 12
    elif frequencia == 'semestral':
        intervalo = 26
    elif frequencia == 'anual':
        intervalo = 52
    elif frequencia == 'diario':
        # Para diário, marcar todas as semanas
        return list(range(semana_inicio, 53))
    else:
        return []
    
    # Gerar semanas de execução
    semana_atual = semana_inicio
    while semana_atual <= 52:
        semanas_execucao.append(semana_atual)
        semana_atual += intervalo
    
    return semanas_execucao

def obter_status_os_semana(pmp_id, semana_numero, semanas_ano):
    # Normalizar datas de semana para datetime (início/fim do dia)
    # (duplicado removido)
    inicio_dt = datetime.combine(_to_date(semana['inicio']), datetime.min.time())
    fim_dt = datetime.combine(_to_date(semana['fim']), datetime.max.time())
    print("DEBUG[obter_status_os_semana]:", f"pmp_id={{pmp_id}} semana_numero={{semana_numero}}", f"inicio_dt={{inicio_dt}} ({{type(inicio_dt)}})", f"fim_dt={{fim_dt}} ({{type(fim_dt)}})")
    """Obtém o status da OS para uma PMP em uma semana específica"""
    # (duplicado removido)
    
    # Buscar OS da PMP nesta semana
    os_semana = OrdemServico.query.filter(
        OrdemServico.pmp_id == pmp_id,
        OrdemServico.data_criacao >= inicio_dt,
        OrdemServico.data_criacao <= fim_dt
    ).first()
    
    if not os_semana:
        return {'status': 'nao_gerada', 'numero_os': None}
    
    if os_semana.status == 'concluida':
        return {'status': 'concluida', 'numero_os': os_semana.id}
    else:
        return {'status': 'gerada', 'numero_os': os_semana.id}

def calcular_hh_por_mes_oficina(ano=None):
    """Calcula horas-homem por mês e oficina"""
    if ano is None:
        ano = datetime.now().year
    
    inicio_ano = datetime(ano, 1, 1)
    fim_ano = datetime(ano, 12, 31)
    print(f"DEBUG[HH]: ano={ano} inicio_ano={inicio_ano} ({type(inicio_ano)}), fim_ano={fim_ano} ({type(fim_ano)})")
    
    # Buscar todas as PMPs com OS no ano
    pmps_com_os = db.session.query(PMP).join(OrdemServico).filter(
        OrdemServico.data_criacao >= inicio_ano,
        OrdemServico.data_criacao <= fim_ano,
        OrdemServico.status == 'concluida'
    ).all()
    print(f"DEBUG[HH]: pmps_com_os={len(pmps_com_os)}")
    
    # Organizar por mês e oficina
    hh_por_mes_oficina = {}
    
    for mes in range(1, 13):
        nome_mes = calendar.month_name[mes]
        hh_por_mes_oficina[nome_mes] = {
            'total': 0,
            'oficinas': {}
        }
    
    for pmp in pmps_com_os:
        # Buscar OS concluídas desta PMP no ano
        os_concluidas = OrdemServico.query.filter(
            OrdemServico.pmp_id == pmp.id,
            OrdemServico.data_criacao >= inicio_ano,
            OrdemServico.data_criacao <= fim_ano,
            OrdemServico.status == 'concluida'
        ).all()
        print(f"DEBUG[HH]: PMP {pmp.id} os_concluidas={len(os_concluidas)}")
        
        for os in os_concluidas:
            mes_os = os.data_criacao.month
            nome_mes = calendar.month_name[mes_os]
            oficina = pmp.oficina or 'Não definida'
            hh = pmp.tempo_pessoa or 0
            
            # Somar no total do mês
            hh_por_mes_oficina[nome_mes]['total'] += hh
            
            # Somar na oficina específica
            if oficina not in hh_por_mes_oficina[nome_mes]['oficinas']:
                hh_por_mes_oficina[nome_mes]['oficinas'][oficina] = 0
            hh_por_mes_oficina[nome_mes]['oficinas'][oficina] += hh
    
    return hh_por_mes_oficina

@relatorio_52_semanas_bp.route('/api/relatorios/plano-52-semanas', methods=['GET'])
@login_required
def gerar_plano_52_semanas():
    try:
        ano = request.args.get('ano', datetime.now().year, type=int)
        
        # Calcular semanas do ano
        semanas_ano = calcular_semanas_ano(ano)
        print(f"DEBUG[route]: ano={ano} primeira_semana={{'inicio': semanas_ano[0]['inicio'], 'fim': semanas_ano[0]['fim']}} tipos=({type(semanas_ano[0]['inicio'])}, {type(semanas_ano[0]['fim'])})")
        
        # Buscar equipamentos e suas PMPs
        equipamentos = Equipamento.query.filter_by(empresa=current_user.company).all()
        
        # Criar PDF
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=landscape(A4), 
                              rightMargin=0.5*inch, leftMargin=0.5*inch,
                              topMargin=0.5*inch, bottomMargin=0.5*inch)
        
        elements = []
        styles = getSampleStyleSheet()
        
        # Título
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=16,
            spaceAfter=20,
            alignment=1  # Center
        )
        
        elements.append(Paragraph(f"Plano de Manutenção Preventiva - {ano}", title_style))
        elements.append(Paragraph(f"52 Semanas do Ano", title_style))
        elements.append(Spacer(1, 20))
        
        # Para cada equipamento
        for equipamento in equipamentos:
            pmps = PMP.query.filter_by(equipamento_id=equipamento.id).all()
            
            if not pmps:
                continue
            
            # Título do equipamento
            equip_style = ParagraphStyle(
                'EquipStyle',
                parent=styles['Heading2'],
                fontSize=12,
                spaceAfter=10
            )
            elements.append(Paragraph(f"Equipamento: {equipamento.descricao}", equip_style))
            
            # Criar tabela
            # Cabeçalho: Equipamento | PMP | 1 | 2 | 3 | ... | 52
            header = ['Equipamento', 'PMP'] + [str(i) for i in range(1, 53)]
            
            table_data = [header]
            
            # Para cada PMP do equipamento
            for i, pmp in enumerate(pmps):
                row = [equipamento.descricao if i == 0 else '', pmp.codigo]
                
                # Determinar semanas de execução
                semanas_execucao = determinar_semanas_pmp(pmp, semanas_ano)
                
                # Para cada semana (1-52)
                for semana_num in range(1, 53):
                    if semana_num in semanas_execucao:
                        # Verificar status da OS
                        status_os = obter_status_os_semana(pmp.id, semana_num, semanas_ano)
                        
                        if status_os['status'] == 'concluida':
                            row.append(f"OS#{status_os['numero_os']}")
                        elif status_os['status'] == 'gerada':
                            row.append(f"OS#{status_os['numero_os']}")
                        else:
                            row.append('●')  # Marcador para OS não gerada
                    else:
                        row.append('')
                
                table_data.append(row)
            
            # Criar tabela
            table = Table(table_data, colWidths=[1*inch, 1*inch] + [0.3*inch]*52)
            
            # Estilo da tabela
            table_style = [
                ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, -1), 8),
                ('GRID', (0, 0), (-1, -1), 1, colors.black),
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ]
            
            # Aplicar cores baseadas no status
            for row_idx in range(1, len(table_data)):
                pmp = pmps[row_idx - 1]
                semanas_execucao = determinar_semanas_pmp(pmp, semanas_ano)
                
                for col_idx, semana_num in enumerate(range(1, 53), start=2):
                    if semana_num in semanas_execucao:
                        status_os = obter_status_os_semana(pmp.id, semana_num, semanas_ano)
                        
                        if status_os['status'] == 'concluida':
                            # Verde para concluída
                            table_style.append(('BACKGROUND', (col_idx, row_idx), (col_idx, row_idx), colors.lightgreen))
                        elif status_os['status'] == 'gerada':
                            # Cinza escuro para gerada mas não concluída
                            table_style.append(('BACKGROUND', (col_idx, row_idx), (col_idx, row_idx), colors.lightgrey))
                        else:
                            # Cinza claro para não gerada
                            table_style.append(('BACKGROUND', (col_idx, row_idx), (col_idx, row_idx), colors.whitesmoke))
            
            table.setStyle(TableStyle(table_style))
            elements.append(table)
            elements.append(Spacer(1, 20))
        
        # Adicionar quebra de página antes da tabela de HH
        elements.append(PageBreak())
        
        # Tabela de Horas-Homem por Mês e Oficina
        elements.append(Paragraph("Resumo de Horas-Homem por Mês e Oficina", title_style))
        elements.append(Spacer(1, 20))
        
        hh_data = calcular_hh_por_mes_oficina(ano)
        
        # Obter todas as oficinas
        todas_oficinas = set()
        for mes_data in hh_data.values():
            todas_oficinas.update(mes_data['oficinas'].keys())
        todas_oficinas = sorted(list(todas_oficinas))
        
        # Criar tabela de HH
        hh_header = ['Mês', 'Total'] + todas_oficinas
        hh_table_data = [hh_header]
        
        meses_ordem = ['January', 'February', 'March', 'April', 'May', 'June',
                      'July', 'August', 'September', 'October', 'November', 'December']
        
        for mes_nome in meses_ordem:
            if mes_nome in hh_data:
                mes_data = hh_data[mes_nome]
                row = [mes_nome, str(int(mes_data['total']))]
                
                for oficina in todas_oficinas:
                    hh_oficina = mes_data['oficinas'].get(oficina, 0)
                    row.append(str(int(hh_oficina)))
                
                hh_table_data.append(row)
        
        # Criar tabela de HH
        hh_table = Table(hh_table_data)
        hh_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ]))
        
        elements.append(hh_table)
        
        # Gerar PDF
        doc.build(elements)
        buffer.seek(0)
        
        return send_file(
            buffer,
            as_attachment=True,
            download_name=f'Plano_52_Semanas_{ano}.pdf',
            mimetype='application/pdf'
        )
        
    except Exception as e:
        print(f"Erro ao gerar relatório: {e}")
        return jsonify({'error': str(e)}), 500
