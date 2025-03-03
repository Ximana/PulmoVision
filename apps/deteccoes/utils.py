# apps/deteccoes/utils.py
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch, cm, mm
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image, Flowable
from reportlab.pdfgen import canvas
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from io import BytesIO
from django.conf import settings
import os
from datetime import datetime

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

def create_header_footer(canvas, doc):
    # Save canvas state
    canvas.saveState()
    
    # Header
    header_color = colors.HexColor('#198754')
    canvas.setFillColor(header_color)
    canvas.rect(0, doc.pagesize[1] - 2.5*inch, doc.pagesize[0], 1.5*inch, fill=1)
    
    # Header text
    canvas.setFillColor(colors.white)
    canvas.setFont("Helvetica-Bold", 24)
    canvas.drawString(doc.leftMargin, doc.pagesize[1] - 1.5*inch, "PulmoVision")
    canvas.setFont("Helvetica", 14)
    canvas.drawString(doc.leftMargin, doc.pagesize[1] - 1.8*inch, "Relatório de Detecção")
    
    # Footer
    canvas.setFillColor(header_color)
    canvas.rect(0, 0, doc.pagesize[0], 0.5*inch, fill=1)
    
    # Footer text
    canvas.setFillColor(colors.white)
    canvas.setFont("Helvetica", 8)
    footer_text = f"Documento gerado em {datetime.now().strftime('%d/%m/%Y %H:%M')} | Página {doc.page}"
    canvas.drawRightString(doc.pagesize[0] - doc.rightMargin, 0.25*inch, footer_text)
    
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
        bottomMargin=50
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
        borderColor=colors.HexColor('#198754'),
        borderWidth=1,
        borderRadius=5
    ))
    
    styles.add(ParagraphStyle(
        name='NormalText',
        parent=styles['Normal'],
        fontSize=12,
        spaceBefore=6,
        spaceAfter=6,
        leading=16
    ))
    
    # Content elements
    elements = []
    
    # Add some space after header
    elements.append(Spacer(1, 30))
    
    # Status Box
    status_data = [[
        Paragraph(f"<font color='#198754'><b>Status:</b></font><br/>{deteccao.estado}", styles['NormalText']),
        Paragraph(f"<font color='#198754'><b>Probabilidade:</b></font><br/>{deteccao.probabilidade}%", styles['NormalText']),
        Paragraph(f"<font color='#198754'><b>Data:</b></font><br/>{deteccao.criado_em.strftime('%d/%m/%Y')}", styles['NormalText'])
    ]]
    
    status_table = Table(status_data, colWidths=[doc.width/3.0]*3)
    status_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#f8f9fa')),
        ('BOX', (0, 0), (-1, -1), 1, colors.HexColor('#198754')),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('PADDING', (0, 0), (-1, -1), 15),
        ('ROUNDEDCORNERS', [10, 10, 10, 10]),
    ]))
    elements.append(status_table)
    
    # Diagnostic Box
    elements.append(Spacer(1, 20))
    diagnostic_data = [[
        Paragraph(f"<font size=14 color='#198754'><b>Diagnóstico:</b></font> {deteccao.diagnostico}", styles['NormalText'])
    ]]
    diagnostic_table = Table(diagnostic_data, colWidths=[doc.width])
    diagnostic_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#e9ecef')),
        ('BOX', (0, 0), (-1, -1), 1, colors.gray),
        ('PADDING', (0, 0), (-1, -1), 15),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
    ]))
    elements.append(diagnostic_table)
    
    # Patient Information Section
    elements.append(Paragraph("Informações do Paciente", styles['SectionTitle']))
    elements.append(MCLine(doc.width))
    
    patient = deteccao.radiografia.paciente
    patient_data = [
        ['Nome Completo:', patient.get_nome_completo()],
        ['Data de Nascimento:', patient.data_nascimento.strftime('%d/%m/%Y')],
        ['Idade:', f"{patient.get_idade()} anos"],
        ['Gênero:', patient.genero],
        ['Tipo Sanguíneo:', patient.tipo_sanguineo or 'Não informado'],
        ['Nº do BI:', patient.numero_bi or 'Não informado'],
    ]
    
    patient_table = Table(patient_data, colWidths=[150, 300])
    patient_table.setStyle(TableStyle([
        ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 0), (-1, -1), 12),
        ('TEXTCOLOR', (0, 0), (0, -1), colors.HexColor('#198754')),
        ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#ffffff')),
        ('GRID', (0, 0), (-1, -1), 0.25, colors.lightgrey),
        ('BOX', (0, 0), (-1, -1), 1, colors.HexColor('#198754')),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('PADDING', (0, 0), (-1, -1), 8),
    ]))
    elements.append(patient_table)
    
    # X-Ray Information Section
    elements.append(Paragraph("Informações da Radiografia", styles['SectionTitle']))
    elements.append(MCLine(doc.width))
    
    xray = deteccao.radiografia
    xray_data = [
        ['Data do Exame:', xray.data.strftime('%d/%m/%Y')],
        ['Tipo de Exame:', xray.tipo],
        ['Equipamento:', xray.equipamento_usado],
        ['Qualidade:', xray.qualidade_da_imagem],
        ['Dose de Radiação:', f"{xray.dose_de_radiacao} mSv" if xray.dose_de_radiacao else 'Não informado'],
    ]
    
    xray_table = Table(xray_data, colWidths=[150, 300])
    xray_table.setStyle(TableStyle([
        ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 0), (-1, -1), 12),
        ('TEXTCOLOR', (0, 0), (0, -1), colors.HexColor('#198754')),
        ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#ffffff')),
        ('GRID', (0, 0), (-1, -1), 0.25, colors.lightgrey),
        ('BOX', (0, 0), (-1, -1), 1, colors.HexColor('#198754')),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('PADDING', (0, 0), (-1, -1), 8),
    ]))
    elements.append(xray_table)
    
    # Detailed Findings
    elements.append(Paragraph("Descobertas Detalhadas", styles['SectionTitle']))
    elements.append(MCLine(doc.width))
    
    findings_style = ParagraphStyle(
        'Findings',
        parent=styles['Normal'],
        fontSize=12,
        leading=16,
        spaceBefore=10,
        spaceAfter=10,
        backColor=colors.HexColor('#f8f9fa'),
        borderPadding=10,
        borderColor=colors.HexColor('#198754'),
        borderWidth=1,
        borderRadius=5
    )
    elements.append(Paragraph(deteccao.descobertas, findings_style))
    
    # Build PDF
    doc.build(elements, onFirstPage=create_header_footer, onLaterPages=create_header_footer)
    pdf = buffer.getvalue()
    buffer.close()
    return pdf