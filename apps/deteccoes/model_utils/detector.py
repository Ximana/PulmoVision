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
        Detecta doença a partir de uma imagem de radiografia de tórax
        
        Args:
            imagem_path: Caminho ou objeto de arquivo da imagem
            
        Returns:
            dict: Dicionário com informações da detecção
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
        
        diagnostico = mapeamento_doencas.get(self.classes[class_idx], 'Desconhecido')
        
        # Resultados completos para todas as classes
        resultados_completos = {}
        for i, classe in enumerate(self.classes):
            resultados_completos[mapeamento_doencas.get(classe, classe)] = float(predicoes[0][i]) * 100
        
        # Gerar interpretação detalhada
        interpretacao = self._gerar_interpretacao(diagnostico, probabilidade, resultados_completos)
        
        # Gerar descobertas detalhadas
        descobertas = self._gerar_descobertas(diagnostico, probabilidade, resultados_completos)
        
        # Preparar resultado
        resultado = {
            'diagnostico': diagnostico,
            'probabilidade': probabilidade,
            'resultados_completos': resultados_completos,
            'interpretacao': interpretacao,
            'descobertas': descobertas
        }
        
        return resultado
    
    def _gerar_interpretacao(self, diagnostico, probabilidade, resultados_completos):
        """
        Gera interpretação clínica baseada no diagnóstico e nas probabilidades
        
        Args:
            diagnostico: Diagnóstico principal
            probabilidade: Probabilidade do diagnóstico principal
            resultados_completos: Probabilidades de todas as classes
            
        Returns:
            str: Texto de interpretação
        """
        interpretacao = f"Análise baseada em radiografia de tórax - {diagnostico} ({probabilidade:.2f}%):\n\n"
        
        # Adicionar informações específicas por doença
        if diagnostico == "Tuberculose":
            interpretacao += "• Características radiológicas: Possíveis infiltrados nos lobos superiores, cavitações, "
            interpretacao += "nódulos e/ou opacidades irregulares sugestivas de tuberculose pulmonar.\n"
            interpretacao += "• Áreas potencialmente afetadas: Predominantemente nos lobos superiores e segmentos apicais dos lobos inferiores.\n"
            interpretacao += "• Recomendações: Confirmação bacteriológica recomendada. Considerar teste molecular rápido (GeneXpert MTB/RIF), "
            interpretacao += "baciloscopia e cultura para confirmação diagnóstica.\n"
            
        elif diagnostico == "Pneumonia":
            interpretacao += "• Características radiológicas: Opacidade(s) de espaço aéreo, possível consolidação lobar ou multilobar, "
            interpretacao += "broncograma aéreo e/ou derrame pleural associado.\n"
            interpretacao += "• Áreas potencialmente afetadas: Distribuição variável, frequentemente nos lobos inferiores.\n"
            interpretacao += "• Recomendações: Avaliação clínica completa, considerar testes laboratoriais incluindo hemograma, "
            interpretacao += "proteína C reativa e procalcitonina para avaliação de gravidade.\n"
            
        elif diagnostico == "Covid-19":
            interpretacao += "• Características radiológicas: Opacidades em vidro fosco, principalmente bilaterais e periféricas, "
            interpretacao += "possíveis consolidações e padrão reticular.\n"
            interpretacao += "• Áreas potencialmente afetadas: Distribuição frequentemente bilateral, periférica e basal.\n"
            interpretacao += "• Recomendações: Considerar teste de PCR para SARS-CoV-2, monitorar saturação de oxigênio "
            interpretacao += "e sinais vitais. Avaliar necessidade de exames adicionais como tomografia computadorizada.\n"
            
        elif diagnostico == "Normal":
            interpretacao += "• Características radiológicas: Campos pulmonares claros sem opacidades significativas. "
            interpretacao += "Estruturas brônquicas e vasculares de aspecto normal.\n"
            interpretacao += "• Observações: Ausência de consolidações, nódulos ou massas. Silhueta cardíaca e hilos de morfologia preservada.\n"
            interpretacao += "• Recomendações: Se persistência de sintomas respiratórios apesar de radiografia normal, "
            interpretacao += "considerar outros métodos diagnósticos ou repetir exame conforme evolução clínica.\n"
        
        # Adicionar informações sobre a confiabilidade
        if probabilidade >= 90:
            interpretacao += "\nALTA CONFIABILIDADE: O padrão radiológico apresenta características fortemente sugestivas do diagnóstico indicado.\n"
        elif probabilidade >= 75:
            interpretacao += "\nCONFIABILIDADE MODERADA: O padrão radiológico apresenta características compatíveis com o diagnóstico indicado.\n"
        else:
            interpretacao += "\nCONFIABILIDADE LIMITADA: O padrão radiológico apresenta algumas características do diagnóstico indicado, porém com sobreposição significativa com outros diagnósticos. Correlação clínica essencial.\n"
        
        # Adicionar alertas para diagnósticos diferenciais relevantes
        for doenca, prob in resultados_completos.items():
            if doenca != diagnostico and prob > 20:
                interpretacao += f"\nDIAGNÓSTICO DIFERENCIAL: {doenca} ({prob:.2f}%) - Deve ser considerado na avaliação clínica.\n"
        
        interpretacao += "\nOBSERVAÇÃO: Esta interpretação é gerada automaticamente e deve ser validada por um radiologista ou médico especialista. Correlação com dados clínicos e laboratoriais é imprescindível para o diagnóstico definitivo."
        
        return interpretacao
    
    def _gerar_descobertas(self, diagnostico, probabilidade, resultados_completos):
        """
        Gera texto de descobertas simplificado para usuários não-técnicos/pacientes
        
        Args:
            diagnostico: Diagnóstico principal detectado
            probabilidade: Probabilidade do diagnóstico principal
            resultados_completos: Probabilidades de todas as classes
        
        Returns:
            str: Texto de descobertas em linguagem acessível
        """
        descobertas = f"RESULTADO DA ANÁLISE DE RADIOGRAFIA PULMONAR\n\n"
        descobertas += f"A análise computadorizada sugere: {diagnostico}\n"
        descobertas += f"Nível de confiança: {probabilidade:.1f}%\n\n"
        
        descobertas += "O QUE ISTO SIGNIFICA:\n"
        
        if diagnostico == "Tuberculose":
            descobertas += "• A imagem apresenta sinais que podem indicar uma infecção por tuberculose nos pulmões.\n"
            descobertas += "• A tuberculose é uma doença infecciosa causada pela bactéria Mycobacterium tuberculosis.\n"
            descobertas += "• Sintomas comuns incluem tosse persistente, febre, suores noturnos e perda de peso.\n"
            descobertas += "• É importante realizar testes adicionais para confirmar este diagnóstico.\n"
            
        elif diagnostico == "Pneumonia":
            descobertas += "• A imagem mostra áreas de possível infecção pulmonar compatíveis com pneumonia.\n"
            descobertas += "• A pneumonia é uma inflamação dos pulmões geralmente causada por infecção.\n"
            descobertas += "• Sintomas típicos incluem tosse com catarro, febre, falta de ar e dor torácica.\n"
            descobertas += "• O tratamento geralmente envolve antibióticos, especialmente se for de origem bacteriana.\n"
            
        elif diagnostico == "Covid-19":
            descobertas += "• A imagem apresenta padrões que podem ser compatíveis com pneumonia por COVID-19.\n"
            descobertas += "• A COVID-19 é causada pelo vírus SARS-CoV-2 e pode afetar os pulmões de maneira característica.\n"
            descobertas += "• Sintomas comuns incluem febre, tosse seca, fadiga e perda de olfato ou paladar.\n"
            descobertas += "• Um teste específico para COVID-19 é recomendado para confirmar este diagnóstico.\n"
            
        elif diagnostico == "Normal":
            descobertas += "• Não foram detectadas alterações significativas na radiografia pulmonar.\n"
            descobertas += "• Os campos pulmonares parecem estar sem anormalidades visíveis nesta imagem.\n"
            descobertas += "• Se você estiver apresentando sintomas respiratórios, é importante discuti-los com seu médico mesmo com radiografia normal.\n"
            descobertas += "• Algumas condições podem não ser visíveis em radiografias convencionais.\n"
        
        # Adicionar outros resultados significativos
        outras_possibilidades = []
        for doenca, prob in resultados_completos.items():
            if doenca != diagnostico and prob > 15:
                outras_possibilidades.append(f"{doenca} ({prob:.1f}%)")
        
        if outras_possibilidades:
            descobertas += "\nOUTRAS POSSIBILIDADES PARA CONSIDERAR:\n"
            for possibilidade in outras_possibilidades:
                descobertas += f"• {possibilidade}\n"
        
        descobertas += "\nPRÓXIMOS PASSOS RECOMENDADOS:\n"
        descobertas += "• Discuta estes resultados com seu médico assistente.\n"
        descobertas += "• Este é uma análise preliminar realizada por computador e requer interpretação médica profissional.\n"
        descobertas += "• Siga as recomendações médicas para exames adicionais ou tratamento conforme necessário.\n"
        descobertas += "• Nunca ignore sintomas mesmo se o resultado da radiografia for normal.\n"
        
        descobertas += "\nIMPORTANTE: Esta análise foi gerada por um sistema de inteligência artificial e deve sempre ser revisada por um profissional de saúde qualificado."
        
        return descobertas

# Instância global para reutilização
detector = DetectorDoencasPulmonares()

def analisar_radiografia(radiografia_obj):
    """
    Analisa uma radiografia e retorna uma detecção
    
    Args:
        radiografia_obj: Objeto do modelo Radiografia
        
    Returns:
        dict: Resultado da análise
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