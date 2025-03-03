# apps/deteccoes/utils.py
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch, cm, mm
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image, Flowable, KeepTogether
from reportlab.pdfgen import canvas
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from io import BytesIO
from django.conf import settings
import os
from datetime import datetime
import json

class MCLine(Flowable):
    """Custom flowable for drawing a stylish line"""
    def __init__(self, width, height=0.5):
        Flowable.__init__(self)
        self.width = width
        self.height = height

    def draw(self):
        self.canv.setStrokeColor(colors.HexColor('#198754'))
        self.canv.setLineWidth(self.height)
        self.canv.line(0, 0, self.width, 0)

class ProgressBar(Flowable):
    """Custom flowable for drawing a progress bar"""
    def __init__(self, width, value, height=8, color=colors.HexColor('#198754')):
        Flowable.__init__(self)
        self.width = width
        self.value = min(value, 100)  # Cap at 100%
        self.height = height
        
        # Set color based on value
        if value >= 70:
            self.color = colors.HexColor('#dc3545')  # danger
        elif value >= 40:
            self.color = colors.HexColor('#ffc107')  # warning
        else:
            self.color = color  # default green

    def draw(self):
        # Draw background
        self.canv.setFillColor(colors.HexColor('#f8f9fa'))
        self.canv.roundRect(0, 0, self.width, self.height, 2, fill=1, stroke=0)
        
        # Draw progress
        self.canv.setFillColor(self.color)
        progress_width = (self.value / 100) * self.width
        self.canv.roundRect(0, 0, progress_width, self.height, 2, fill=1, stroke=0)

def create_header_footer(canvas, doc):
    # Save canvas state
    canvas.saveState()
    
    # Header
    header_color = colors.HexColor('#198754')
    canvas.setFillColor(header_color)
    canvas.roundRect(doc.leftMargin - 10, doc.pagesize[1] - 2.5*inch, 
                     doc.width + 20, 1.5*inch, 10, fill=1, stroke=0)
    
    # Logo placeholder
    logo_path = os.path.join(settings.STATIC_ROOT, 'img', 'logo.png')
    if os.path.exists(logo_path):
        canvas.drawImage(logo_path, doc.leftMargin, doc.pagesize[1] - 2.2*inch, 
                         width=1*inch, height=1*inch, mask='auto')
        logo_offset = 1.2*inch
    else:
        logo_offset = 0
    
    # Header text
    canvas.setFillColor(colors.white)
    canvas.setFont("Helvetica-Bold", 24)
    canvas.drawString(doc.leftMargin + logo_offset, doc.pagesize[1] - 1.5*inch, "PulmoVision")
    canvas.setFont("Helvetica", 14)
    canvas.drawString(doc.leftMargin + logo_offset, doc.pagesize[1] - 1.8*inch, "Relatório de Detecção Pulmonar")
    
    # Footer
    canvas.setFillColor(header_color)
    canvas.roundRect(doc.leftMargin - 10, 0.2*inch, doc.width + 20, 0.5*inch, 10, fill=1, stroke=0)
    
    # Footer text (corrigido)
    canvas.setFillColor(colors.white)
    canvas.setFont("Helvetica", 8)
    footer_text = f"Documento gerado em {datetime.now().strftime('%d/%m/%Y %H:%M')} | Página {canvas.getPageNumber()}"
    canvas.drawRightString(doc.pagesize[0] - doc.rightMargin, 0.45*inch, footer_text)
    canvas.drawString(doc.leftMargin, 0.45*inch, "© PulmoVision 2025 - Todos os direitos reservados")
    
    # Restore canvas state
    canvas.restoreState()


def gerar_deteccao_pdf(deteccao):
    buffer = BytesIO()
    
    # Document setup
    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=50,
        leftMargin=50,
        topMargin=120,  # Increased to accommodate header
        bottomMargin=60
    )
    
    # Styles
    styles = getSampleStyleSheet()
    styles.add(ParagraphStyle(
        name='SectionTitle',
        parent=styles['Heading2'],
        fontSize=16,
        spaceBefore=20,
        spaceAfter=10,
        textColor=colors.HexColor('#198754'),
        borderPadding=(10, 0, 10, 0),
    ))
    
    styles.add(ParagraphStyle(
        name='NormalText',
        parent=styles['Normal'],
        fontSize=11,
        spaceBefore=6,
        spaceAfter=6,
        leading=16
    ))
    
    styles.add(ParagraphStyle(
        name='SmallText',
        parent=styles['Normal'],
        fontSize=9,
        leading=12
    ))
    
    styles.add(ParagraphStyle(
        name='BoldText',
        parent=styles['NormalText'],
        fontName='Helvetica-Bold'
    ))
    
    styles.add(ParagraphStyle(
        name='CardTitle',
        parent=styles['Heading3'],
        fontSize=14,
        textColor=colors.HexColor('#198754'),
        spaceBefore=6,
        spaceAfter=6,
    ))
    
    # Content elements
    elements = []
    
    # Add some space after header
    elements.append(Spacer(1, 20))
    
    # Main diagnostic banner
    diag_color = colors.HexColor('#198754')
    if deteccao.probabilidade >= 70:
        diag_color = colors.HexColor('#dc3545')  # danger
    elif deteccao.probabilidade >= 40:
        diag_color = colors.HexColor('#ffc107')  # warning
    
    main_diag_data = [
        [Paragraph(f"<font color='white' size='14'><b>DIAGNÓSTICO: {deteccao.diagnostico}</b></font>", styles['NormalText']),
         Paragraph(f"<font color='white' size='14'><b>PROBABILIDADE: {deteccao.probabilidade}%</b></font>", styles['NormalText'])]
    ]
    
    main_diag_table = Table(main_diag_data, colWidths=[doc.width*0.6, doc.width*0.4])
    main_diag_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), diag_color),
        ('BOX', (0, 0), (-1, -1), 1, diag_color),
        ('ALIGN', (0, 0), (0, 0), 'LEFT'),
        ('ALIGN', (1, 0), (1, 0), 'RIGHT'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('PADDING', (0, 0), (-1, -1), 10),
        ('ROUNDEDCORNERS', [8, 8, 8, 8]),
    ]))
    elements.append(main_diag_table)
    
    # Status Overview Card
    elements.append(Spacer(1, 15))
    elements.append(Paragraph("Visão Geral do Status", styles['SectionTitle']))
    elements.append(MCLine(doc.width))
    elements.append(Spacer(1, 6))
    
    status_data = [
        [
            Paragraph("<font color='#198754'><b>Estado</b></font>", styles['BoldText']),
            Paragraph("<font color='#198754'><b>Data de Criação</b></font>", styles['BoldText']),
            Paragraph("<font color='#198754'><b>ID do Exame</b></font>", styles['BoldText']),
        ],
        [
            Paragraph(f"{deteccao.estado}", styles['NormalText']),
            Paragraph(f"{deteccao.criado_em.strftime('%d/%m/%Y')}", styles['NormalText']),
            Paragraph(f"{deteccao.pk}", styles['NormalText']),
        ]
    ]
    
    status_table = Table(status_data, colWidths=[doc.width/3.0]*3)
    status_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#f8f9fa')),
        ('BACKGROUND', (0, 1), (-1, 1), colors.white),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.lightgrey),
        ('BOX', (0, 0), (-1, -1), 1, colors.HexColor('#198754')),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('PADDING', (0, 0), (-1, -1), 8),
    ]))
    elements.append(status_table)
    
    # Two-column layout for patient and X-ray info
    elements.append(Spacer(1, 15))
    
    # Patient Information Section
    patient_title = Paragraph("Informações do Paciente", styles['SectionTitle'])
    patient_line = MCLine(doc.width/2 - 10)
    
    patient = deteccao.radiografia.paciente
    patient_data = [
        [Paragraph("<font color='#198754'><b>Nome Completo:</b></font>", styles['SmallText']), 
         Paragraph(f"{patient.get_nome_completo()}", styles['NormalText'])],
        [Paragraph("<font color='#198754'><b>Data de Nascimento:</b></font>", styles['SmallText']), 
         Paragraph(f"{patient.data_nascimento.strftime('%d/%m/%Y')}", styles['NormalText'])],
        [Paragraph("<font color='#198754'><b>Idade:</b></font>", styles['SmallText']), 
         Paragraph(f"{patient.get_idade()} anos", styles['NormalText'])],
        [Paragraph("<font color='#198754'><b>Gênero:</b></font>", styles['SmallText']), 
         Paragraph(f"{patient.genero}", styles['NormalText'])],
        [Paragraph("<font color='#198754'><b>Tipo Sanguíneo:</b></font>", styles['SmallText']), 
         Paragraph(f"{patient.tipo_sanguineo or 'Não informado'}", styles['NormalText'])],
        [Paragraph("<font color='#198754'><b>Nº do BI:</b></font>", styles['SmallText']), 
         Paragraph(f"{patient.numero_bi or 'Não informado'}", styles['NormalText'])],
    ]
    
    patient_table = Table(patient_data, colWidths=[doc.width/6, doc.width/3])
    patient_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#f8f9fa')),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.lightgrey),
        ('BOX', (0, 0), (-1, -1), 1, colors.HexColor('#198754')),
        ('ALIGN', (0, 0), (0, -1), 'RIGHT'),
        ('ALIGN', (1, 0), (1, -1), 'LEFT'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('PADDING', (0, 0), (-1, -1), 6),
    ]))
    
    # X-Ray Information Section
    xray_title = Paragraph("Informações da Radiografia", styles['SectionTitle'])
    xray_line = MCLine(doc.width/2 - 10)
    
    xray = deteccao.radiografia
    xray_data = [
        [Paragraph("<font color='#198754'><b>Data do Exame:</b></font>", styles['SmallText']), 
         Paragraph(f"{xray.data.strftime('%d/%m/%Y')}", styles['NormalText'])],
        [Paragraph("<font color='#198754'><b>Tipo de Exame:</b></font>", styles['SmallText']), 
         Paragraph(f"{xray.tipo}", styles['NormalText'])],
        [Paragraph("<font color='#198754'><b>Equipamento:</b></font>", styles['SmallText']), 
         Paragraph(f"{xray.equipamento_usado}", styles['NormalText'])],
        [Paragraph("<font color='#198754'><b>Qualidade:</b></font>", styles['SmallText']), 
         Paragraph(f"{xray.qualidade_da_imagem}", styles['NormalText'])],
        [Paragraph("<font color='#198754'><b>Dose de Radiação:</b></font>", styles['SmallText']), 
         Paragraph(f"{xray.dose_de_radiacao} mSv" if xray.dose_de_radiacao else 'Não informado', styles['NormalText'])],
    ]
    
    xray_table = Table(xray_data, colWidths=[doc.width/6, doc.width/3])
    xray_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#f8f9fa')),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.lightgrey),
        ('BOX', (0, 0), (-1, -1), 1, colors.HexColor('#198754')),
        ('ALIGN', (0, 0), (0, -1), 'RIGHT'),
        ('ALIGN', (1, 0), (1, -1), 'LEFT'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('PADDING', (0, 0), (-1, -1), 6),
    ]))
    
    # Put Patient and X-ray info side by side
    info_data = [[patient_title, xray_title],
                 [patient_line, xray_line],
                 [Spacer(1, 6), Spacer(1, 6)],
                 [patient_table, xray_table]]
    
    info_table = Table(info_data, colWidths=[doc.width/2, doc.width/2])
    info_table.setStyle(TableStyle([
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('RIGHTPADDING', (0, 0), (0, -1), 10),
        ('LEFTPADDING', (1, 0), (1, -1), 10),
    ]))
    elements.append(info_table)
    
    # Probability by Condition 
    elements.append(Spacer(1, 20))
    elements.append(Paragraph("Probabilidades por Condição", styles['SectionTitle']))
    elements.append(MCLine(doc.width))
    elements.append(Spacer(1, 10))
    
    # Create probability tables
    if hasattr(deteccao, 'resultados_completos') and deteccao.resultados_completos:
        # Ensure we have a dict (it might be stored as JSON string)
        if isinstance(deteccao.resultados_completos, str):
            resultados_completos = json.loads(deteccao.resultados_completos)
        else:
            resultados_completos = deteccao.resultados_completos
        
        prob_items = []
        
        # Sort results by probability (highest first)
        sorted_results = sorted(resultados_completos.items(), key=lambda x: x[1], reverse=True)
        
        for doenca, valor in sorted_results:
            # Determine color based on value
            if valor >= 70:
                valor_color = '#dc3545'  # danger
            elif valor >= 40:
                valor_color = '#ffc107'  # warning
            else:
                valor_color = '#198754'  # success
                
            disease_row = [
                Paragraph(f"{'<b>' if doenca == deteccao.diagnostico else ''}{doenca}{'</b>' if doenca == deteccao.diagnostico else ''}", styles['NormalText']),
                Paragraph(f"<font color='{valor_color}'><b>{valor:.2f}%</b></font>", styles['NormalText']),
            ]
            
            disease_table = Table([disease_row], colWidths=[doc.width*0.7, doc.width*0.2])
            disease_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#f8f9fa')),
                ('ALIGN', (0, 0), (0, 0), 'LEFT'),
                ('ALIGN', (1, 0), (1, 0), 'RIGHT'),
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                ('PADDING', (0, 0), (-1, -1), 8),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 14),  # Extra padding for progress bar
            ]))
            
            prob_items.append(disease_table)
            prob_items.append(ProgressBar(doc.width*0.9, valor))
            prob_items.append(Spacer(1, 6))
    else:
        prob_items = [Paragraph("Não há informações detalhadas de probabilidade disponíveis.", styles['NormalText'])]
    
    for item in prob_items:
        elements.append(item)
    
    # Clinical Interpretation
    elements.append(Spacer(1, 20))
    elements.append(Paragraph("Interpretação Clínica", styles['SectionTitle']))
    elements.append(MCLine(doc.width))
    elements.append(Spacer(1, 10))
    
    if hasattr(deteccao, 'interpretacao') and deteccao.interpretacao:
        # Title of analysis
        elements.append(Paragraph(f"<font color='#198754'><b>Análise baseada em radiografia de tórax - {deteccao.diagnostico} ({deteccao.probabilidade:.2f}%)</b></font>", styles['CardTitle']))
        elements.append(Spacer(1, 10))
        
        # If we have formatted interpretation
        if hasattr(deteccao, 'interpretacao_formatada'):
            interp = deteccao.interpretacao_formatada
            
            # Radiological features
            if 'caracteristicas' in interp and interp['caracteristicas']:
                elements.append(KeepTogether([
                    Paragraph("<b><font color='#198754'>Características Radiológicas</font></b>", styles['BoldText']),
                    Spacer(1, 6),
                    Paragraph(interp['caracteristicas'].replace('\n', '<br/>'), styles['NormalText']),
                    Spacer(1, 10)
                ]))
                
            # Affected areas
            if 'areas_afetadas' in interp and interp['areas_afetadas']:
                elements.append(KeepTogether([
                    Paragraph("<b><font color='#198754'>Áreas Potencialmente Afetadas</font></b>", styles['BoldText']),
                    Spacer(1, 6),
                    Paragraph(interp['areas_afetadas'].replace('\n', '<br/>'), styles['NormalText']),
                    Spacer(1, 10)
                ]))
                
            # Recommendations
            if 'recomendacoes' in interp and interp['recomendacoes']:
                elements.append(KeepTogether([
                    Paragraph("<b><font color='#198754'>Recomendações</font></b>", styles['BoldText']),
                    Spacer(1, 6),
                    Paragraph(interp['recomendacoes'].replace('\n', '<br/>'), styles['NormalText']),
                    Spacer(1, 10)
                ]))
                
            # Reliability level
            if 'confiabilidade' in interp and interp['confiabilidade']:
                elements.append(KeepTogether([
                    Paragraph("<b><font color='#198754'>Nível de Confiabilidade</font></b>", styles['BoldText']),
                    Spacer(1, 6),
                    Paragraph(interp['confiabilidade'].replace('\n', '<br/>'), styles['NormalText']),
                    Spacer(1, 10)
                ]))
                
            # Differential diagnoses
            if 'diferenciais' in interp and interp['diferenciais']:
                elements.append(KeepTogether([
                    Paragraph("<b><font color='#198754'>Diagnósticos Diferenciais</font></b>", styles['BoldText']),
                    Spacer(1, 6),
                    Paragraph(interp['diferenciais'].replace('\n', '<br/>'), styles['NormalText']),
                    Spacer(1, 10)
                ]))
                
            # Observation
            if 'observacao' in interp and interp['observacao']:
                elements.append(KeepTogether([
                    Paragraph(interp['observacao'].replace('\n', '<br/>'), styles['NormalText']),
                ]))
            else:
                elements.append(KeepTogether([
                    Paragraph("<i><font color='#856404'><b>OBSERVAÇÃO:</b> Esta interpretação é gerada automaticamente e deve ser validada por um radiologista ou médico especialista. Correlação com dados clínicos e laboratoriais é imprescindível para o diagnóstico definitivo.</font></i>", styles['NormalText']),
                ]))
        else:
            # If no formatted interpretation, use the raw interpretation
            elements.append(Paragraph(deteccao.interpretacao.replace('\n', '<br/>'), styles['NormalText']))
    else:
        elements.append(Paragraph("<i>Interpretação não disponível para esta detecção.</i>", styles['NormalText']))
    
    # Build PDF
    doc.build(elements, onFirstPage=create_header_footer, onLaterPages=create_header_footer)
    pdf = buffer.getvalue()
    buffer.close()
    return pdf