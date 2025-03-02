#apps/deteccoes/models_utils/detetor.py
import os
import numpy as np
import tensorflow as tf
from PIL import Image
import json
from django.conf import settings
from ..models import Deteccao
from io import BytesIO
import reportlab
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image as ReportImage, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch

os.environ['CUDA_VISIBLE_DEVICES'] = '-1'  # Desativa uso de GPU

class DetectorDoencasPulmonares:
    def __init__(self):
        self.img_height = 224
        self.img_width = 224
        self.model = None
        self.classes = ['normal', 'tuberculose', 'pneumonia', 'covid']
        self.loaded = False
        
    def carregar_modelo(self, diretorio_modelo=None):
        """
        Carrega um modelo salvo do diretório especificado.
        Se nenhum diretório for especificado, carrega o modelo mais recente.
        
        Args:
            diretorio_modelo (str, optional): Caminho para o diretório do modelo.
                                              Se None, usa o mais recente. 
        
        Returns:
            bool: True se o modelo foi carregado com sucesso
        
        Raises:
            FileNotFoundError: Se nenhum modelo for encontrado
        """
        if diretorio_modelo is None:
            # Usar o modelo mais recente se não for especificado
            todos_modelos = [os.path.join(settings.ML_MODELS_DIR, d) for d in os.listdir(settings.ML_MODELS_DIR) 
                           if os.path.isdir(os.path.join(settings.ML_MODELS_DIR, d))]
            
            if not todos_modelos:
                raise FileNotFoundError("Nenhum modelo encontrado no diretório de modelos")
            
            # Seleciona o diretório mais recente baseado na data de criação
            diretorio_modelo = max(todos_modelos, key=os.path.getctime)
        elif not os.path.isdir(diretorio_modelo):
            # Se um diretório foi especificado, mas não é um caminho absoluto, assumimos que é relativo a ML_MODELS_DIR
            diretorio_modelo = os.path.join(settings.ML_MODELS_DIR, diretorio_modelo)
            
            if not os.path.isdir(diretorio_modelo):
                raise FileNotFoundError(f"Diretório do modelo não encontrado: {diretorio_modelo}")
        
        # Carregar configurações
        caminho_config = os.path.join(diretorio_modelo, 'config.json')
        if not os.path.exists(caminho_config):
            raise FileNotFoundError(f"Arquivo de configuração não encontrado em {caminho_config}")
            
        with open(caminho_config, 'r') as f:
            config = json.load(f)
            
        self.img_height = config.get('img_height', 224)
        self.img_width = config.get('img_width', 224)
        self.classes = config.get('classes', ['normal', 'tuberculose', 'pneumonia', 'covid'])
        
        # Carregar modelo
        caminho_modelo = os.path.join(diretorio_modelo, 'modelo.keras')
        if not os.path.exists(caminho_modelo):
            raise FileNotFoundError(f"Arquivo do modelo não encontrado em {caminho_modelo}")
            
        try:
            self.model = tf.keras.models.load_model(caminho_modelo)
            self.loaded = True
            print(f"Modelo carregado com sucesso de: {caminho_modelo}")
            return True
        except Exception as e:
            print(f"Erro ao carregar o modelo: {str(e)}")
            raise
    
    def processar_imagem(self, imagem_path):
        """
        Processa uma imagem para análise
        """
        try:
            # Pode ser um caminho de arquivo ou um objeto de arquivo
            if isinstance(imagem_path, str):
                img = Image.open(imagem_path).convert('RGB')
            else:
                img = Image.open(imagem_path).convert('RGB')
                
            img = img.resize((self.img_width, self.img_height))
            img_array = tf.keras.preprocessing.image.img_to_array(img)
            img_array = img_array / 255.0  # Normalização
            
            # Adicionar a dimensão de batch
            img_array = np.expand_dims(img_array, axis=0)
            return img_array
            
        except Exception as e:
            raise ValueError(f"Erro ao processar a imagem: {str(e)}")
    
    def detectar_doenca(self, imagem_path):
        """
        Detecta doença a partir de uma imagem de radiografia
        """
        if not self.loaded:
            self.carregar_modelo()
        
        # Processar imagem
        img_array = self.processar_imagem(imagem_path)
        
        # Predição
        predicoes = self.model.predict(img_array)
        class_idx = np.argmax(predicoes[0])
        probabilidade = float(predicoes[0][class_idx]) * 100
        
        # Mapear para a classificação do modelo Django
        mapeamento_doencas = {
            'normal': 'Normal',
            'tuberculose': 'Tuberculose',
            'pneumonia': 'Pneumonia',
            'covid': 'Covid-19'
        }
        
        doenca_detectada = mapeamento_doencas.get(self.classes[class_idx], 'Desconhecido')
        
        # Resultados completos para todas as classes
        resultados_completos = {}
        for i, classe in enumerate(self.classes):
            resultados_completos[mapeamento_doencas.get(classe, classe)] = float(predicoes[0][i]) * 100
        
        # Preparar resultado
        resultado = {
            'doenca': doenca_detectada,
            'probabilidade': probabilidade,
            'resultados_completos': resultados_completos,
            'resultado_texto': f'Detectado {doenca_detectada} com {probabilidade:.2f}% de probabilidade',
            'descobertas': self._gerar_descobertas(doenca_detectada, probabilidade, resultados_completos)
        }
        
        return resultado
    
    def _gerar_descobertas(self, doenca, probabilidade, resultados_completos):
        """
        Gera texto de descobertas baseado na doença detectada
        """
        descobertas = f"Análise de radiografia pulmonar realizada pelo sistema PulmoVision:\n\n"
        descobertas += f"Diagnóstico Primário: {doenca} (Probabilidade: {probabilidade:.2f}%)\n\n"
        
        descobertas += "Resultados detalhados:\n"
        for classe, prob in resultados_completos.items():
            descobertas += f"- {classe}: {prob:.2f}%\n"
        
        descobertas += "\nInterpretação:\n"
        
        # Adicionar interpretação específica para cada doença
        if doenca == "Tuberculose":
            descobertas += "- Padrão sugestivo de infecção por Mycobacterium tuberculosis\n"
            descobertas += "- Possível presença de infiltrados nos lobos superiores\n"
            descobertas += "- Recomenda-se avaliação clínica completa e testes confirmatórios\n"
        elif doenca == "Pneumonia":
            descobertas += "- Opacidade pulmonar sugestiva de infecção bacteriana ou viral\n"
            descobertas += "- Possível consolidação lobar\n"
            descobertas += "- Recomenda-se avaliação clínica e tratamento apropriado\n"
        elif doenca == "Covid-19":
            descobertas += "- Padrão de vidro fosco bilateral típico de infecção por SARS-CoV-2\n"
            descobertas += "- Possível comprometimento periférico dos campos pulmonares\n"
            descobertas += "- Recomenda-se isolamento e monitoramento dos parâmetros vitais\n"
        elif doenca == "Normal":
            descobertas += "- Nenhuma anormalidade significativa detectada\n"
            descobertas += "- Campos pulmonares claros sem evidência de infecção ativa\n"
        
        descobertas += "\nObservações: Este é um resultado gerado por inteligência artificial e deve ser validado por um profissional de saúde qualificado."
        
        return descobertas

# Instância global para reutilização
detector = DetectorDoencasPulmonares()

def analisar_radiografia(radiografia_obj):
    """
    Analisa uma radiografia e retorna uma detecção
    """
    if not detector.loaded:
        detector.carregar_modelo()
    
    # Obter o caminho do arquivo de imagem da radiografia
    imagem_path = radiografia_obj.imagem.path
    
    # Detectar doença
    resultado = detector.detectar_doenca(imagem_path)
    
    return resultado

def gerar_deteccao_pdf(deteccao):
    """
    Gera um PDF com os detalhes da detecção
    """
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter)
    styles = getSampleStyleSheet()
    elements = []
    
    # Título
    titulo_style = ParagraphStyle(
        name='TituloStyle',
        parent=styles['Heading1'],
        fontSize=16,
        alignment=1,
        spaceAfter=12
    )
    elements.append(Paragraph("RELATÓRIO DE DETECÇÃO DE DOENÇA PULMONAR", titulo_style))
    elements.append(Spacer(1, 0.25*inch))
    
    # Informações da detecção
    data_style = ParagraphStyle(name='DataStyle', parent=styles['Normal'], fontSize=10)
    elements.append(Paragraph(f"<b>ID da Detecção:</b> {deteccao.id}", data_style))
    elements.append(Paragraph(f"<b>Data:</b> {deteccao.criado_em.strftime('%d/%m/%Y %H:%M')}", data_style))
    elements.append(Paragraph(f"<b>Radiografia ID:</b> {deteccao.radiografia.id}", data_style))
    elements.append(Paragraph(f"<b>Paciente:</b> {deteccao.radiografia.paciente.get_nome_completo()}", data_style))
    elements.append(Paragraph(f"<b>Realizado por:</b> {deteccao.usuario.get_full_name()}", data_style))
    elements.append(Spacer(1, 0.2*inch))
    
    # Resultado
    resultado_style = ParagraphStyle(
        name='ResultadoStyle',
        parent=styles['Heading2'],
        fontSize=14,
        alignment=1,
        spaceBefore=12,
        spaceAfter=12,
        backColor=colors.lightgrey,
        borderColor=colors.black,
        borderWidth=1,
        borderPadding=5
    )
    elements.append(Paragraph(f"RESULTADO: {deteccao.doenca} ({deteccao.probabilidade}%)", resultado_style))
    elements.append(Spacer(1, 0.2*inch))
    
    # Descobertas
    elements.append(Paragraph("<b>DESCOBERTAS:</b>", styles['Heading3']))
    descobertas_style = ParagraphStyle(name='DescobertasStyle', parent=styles['Normal'], fontSize=10, leading=14)
    descobertas_paras = deteccao.descobertas.split('\n')
    for para in descobertas_paras:
        if para.strip():
            elements.append(Paragraph(para, descobertas_style))
            elements.append(Spacer(1, 0.1*inch))
    
    # Tentar adicionar imagem da radiografia
    try:
        img = ReportImage(deteccao.radiografia.imagem.path, width=4*inch, height=4*inch)
        elements.append(Paragraph("<b>IMAGEM DA RADIOGRAFIA:</b>", styles['Heading3']))
        elements.append(img)
    except Exception as e:
        elements.append(Paragraph("Imagem não disponível", styles['Normal']))
    
    # Rodapé
    elements.append(Spacer(1, 0.5*inch))
    footer_style = ParagraphStyle(name='FooterStyle', parent=styles['Normal'], fontSize=8, alignment=1, textColor=colors.grey)
    elements.append(Paragraph("Este relatório foi gerado automaticamente pelo sistema PulmoVision. Os resultados devem ser validados por um profissional de saúde qualificado.", footer_style))
    
    # Montar PDF
    doc.build(elements)
    
    pdf = buffer.getvalue()
    buffer.close()
    
    return pdf