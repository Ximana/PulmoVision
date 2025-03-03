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
            str: Texto de interpretação estruturado em seções
        """
        # Cabeçalho da interpretação
        interpretacao = f"ANÁLISE RADIOGRÁFICA TORÁCICA - {diagnostico.upper()} ({probabilidade:.2f}%)\n\n"
        
        # Seção de características radiológicas específicas por doença
        if diagnostico == "Tuberculose":
            interpretacao += "• Características radiológicas:\n"
            interpretacao += "  - Infiltrados predominantes em lobos superiores\n"
            interpretacao += "  - Possíveis cavitações de paredes irregulares\n"
            interpretacao += "  - Nódulos de distribuição segmentar\n"
            interpretacao += "  - Padrão fibronodular com retração do parênquima\n"
            interpretacao += "  - Possível derrame pleural, geralmente unilateral e de pequeno volume\n\n"
            
            interpretacao += "• Áreas potencialmente afetadas:\n"
            interpretacao += "  - Predominância em lobos superiores (segmentos apicais e posteriores)\n"
            interpretacao += "  - Segmentos apicais dos lobos inferiores\n"
            interpretacao += "  - Possível envolvimento pleural adjacente\n\n"
            
            interpretacao += "• Recomendações:\n"
            interpretacao += "  - Confirmação bacteriológica por teste molecular rápido (GeneXpert MTB/RIF)\n"
            interpretacao += "  - Baciloscopia de escarro em série (3 amostras)\n"
            interpretacao += "  - Cultura para micobactérias e teste de sensibilidade a antimicrobianos\n"
            interpretacao += "  - Avaliação de contatos domiciliares\n"
            interpretacao += "  - Considerar tomografia computadorizada de tórax em casos de alta suspeita e RX normal\n\n"
            
        elif diagnostico == "Pneumonia":
            interpretacao += "• Características radiológicas:\n"
            interpretacao += "  - Opacidade(s) de espaço aéreo com densidade aumentada\n"
            interpretacao += "  - Consolidação lobar ou multilobar\n"
            interpretacao += "  - Presença de broncograma aéreo nas áreas afetadas\n"
            interpretacao += "  - Possível derrame pleural associado (geralmente unilateral)\n"
            interpretacao += "  - Distribuição frequentemente segmentar ou lobar\n\n"
            
            interpretacao += "• Áreas potencialmente afetadas:\n"
            interpretacao += "  - Distribuição variável, com predomínio em lobos inferiores\n"
            interpretacao += "  - Pneumonia bacteriana típica: padrão lobar\n"
            interpretacao += "  - Pneumonia atípica: padrão intersticial difuso\n"
            interpretacao += "  - Possível acometimento bilateral em casos graves\n\n"
            
            interpretacao += "• Recomendações:\n"
            interpretacao += "  - Avaliação clínica completa com atenção à frequência respiratória e oximetria\n"
            interpretacao += "  - Exames laboratoriais: hemograma, proteína C reativa, procalcitonina\n"
            interpretacao += "  - Coleta de culturas (sangue e escarro) antes de iniciar antibioticoterapia\n"
            interpretacao += "  - Estratificação de risco (scores CURB-65 ou PSI/PORT)\n"
            interpretacao += "  - Considerar tomografia em casos de evolução desfavorável\n\n"
            
        elif diagnostico == "Covid-19":
            interpretacao += "• Características radiológicas:\n"
            interpretacao += "  - Opacidades em vidro fosco (padrão mais comum)\n"
            interpretacao += "  - Distribuição bilateral, periférica e basal predominante\n"
            interpretacao += "  - Padrão reticular sobreposto a vidro fosco (pavimentação em mosaico)\n"
            interpretacao += "  - Consolidações nas fases mais avançadas\n"
            interpretacao += "  - Ausência habitual de derrame pleural e adenomegalias\n\n"
            
            interpretacao += "• Áreas potencialmente afetadas:\n"
            interpretacao += "  - Distribuição bilateral e assimétrica\n"
            interpretacao += "  - Predomínio em regiões periféricas e posteriores\n"
            interpretacao += "  - Maior acometimento de lobos inferiores\n"
            interpretacao += "  - Progressão centro-lobular em casos avançados\n\n"
            
            interpretacao += "• Recomendações:\n"
            interpretacao += "  - Confirmação por teste RT-PCR para SARS-CoV-2\n"
            interpretacao += "  - Monitoramento contínuo de saturação de oxigênio e sinais vitais\n"
            interpretacao += "  - Avaliação laboratorial: hemograma, dímero-D, ferritina, PCR\n"
            interpretacao += "  - Considerar tomografia computadorizada para avaliação da extensão\n"
            interpretacao += "  - Vigilância para progressão rápida ou complicações (TEP, sobreinfecção)\n\n"
            
        elif diagnostico == "Normal":
            interpretacao += "• Características radiológicas:\n"
            interpretacao += "  - Campos pulmonares bem ventilados sem opacidades focais ou difusas\n"
            interpretacao += "  - Tramas brônquica e vascular de calibre e distribuição normais\n"
            interpretacao += "  - Ausência de consolidações, nódulos ou massas identificáveis\n"
            interpretacao += "  - Silhueta cardíaca de dimensões normais\n"
            interpretacao += "  - Seios costofrênicos livres bilateralmente\n\n"
            
            interpretacao += "• Observações:\n"
            interpretacao += "  - Exame sem alterações significativas identificáveis\n"
            interpretacao += "  - Hilos pulmonares de morfologia e densidade preservadas\n"
            interpretacao += "  - Diafragmas com cúpulas bem definidas e regulares\n"
            interpretacao += "  - Arcabouço ósseo torácico sem lesões aparentes\n\n"
            
            interpretacao += "• Recomendações:\n"
            interpretacao += "  - Correlação com quadro clínico do paciente\n"
            interpretacao += "  - Se persistência de sintomas respiratórios, considerar métodos diagnósticos complementares\n"
            interpretacao += "  - Radiografia normal não exclui completamente patologias em fase inicial\n"
            interpretacao += "  - Considerar acompanhamento clínico conforme sintomatologia\n\n"
        
        # Adicionar informações sobre a confiabilidade
        if probabilidade >= 90:
            interpretacao += "NÍVEL DE CONFIABILIDADE: ALTO (>90%)\n"
            interpretacao += "- O padrão radiológico apresenta características fortemente sugestivas do diagnóstico indicado\n"
            interpretacao += "- Alta especificidade para o diagnóstico proposto\n"
            interpretacao += "- Correlação clínica ainda recomendada para confirmação\n\n"
        elif probabilidade >= 75:
            interpretacao += "NÍVEL DE CONFIABILIDADE: MODERADO (75-90%)\n"
            interpretacao += "- O padrão radiológico apresenta características compatíveis com o diagnóstico indicado\n"
            interpretacao += "- Especificidade moderada para o diagnóstico proposto\n"
            interpretacao += "- Correlação clínica necessária e exames complementares podem ser úteis\n\n"
        else:
            interpretacao += "NÍVEL DE CONFIABILIDADE: LIMITADO (<75%)\n"
            interpretacao += "- O padrão radiológico apresenta algumas características do diagnóstico indicado\n" 
            interpretacao += "- Sobreposição significativa com outros diagnósticos diferenciais\n"
            interpretacao += "- Correlação clínica essencial e exames complementares fortemente recomendados\n\n"
        
        # Adicionar diagnósticos diferenciais relevantes
        diferenciais_adicionados = False
        for doenca, prob in sorted(resultados_completos.items(), key=lambda x: x[1], reverse=True):
            if doenca != diagnostico and prob > 20:
                if not diferenciais_adicionados:
                    interpretacao += "DIAGNÓSTICOS DIFERENCIAIS:\n"
                    diferenciais_adicionados = True
                
                interpretacao += f"• {doenca} ({prob:.2f}%):\n"
                
                if doenca == "Tuberculose":
                    interpretacao += "  - Considerar na presença de sintomas respiratórios prolongados, perda de peso, histórico epidemiológico\n"
                    interpretacao += "  - Recomenda-se investigação com baciloscopia e teste molecular\n"
                elif doenca == "Pneumonia":
                    interpretacao += "  - Considerar quando há febre, tosse produtiva e alterações auscultatórias focais\n"
                    interpretacao += "  - Avaliar resposta a antibioticoterapia e leucocitose\n"
                elif doenca == "Covid-19":
                    interpretacao += "  - Considerar em contexto epidemiológico e sintomas típicos (anosmia, disgeusia, fadiga)\n"
                    interpretacao += "  - Indicado teste específico para SARS-CoV-2\n"
                else:  # Outras condições ou Normal
                    interpretacao += "  - Avaliar conforme apresentação clínica\n"
        
        # Nota de observação final
        interpretacao += "\nOBSERVAÇÃO IMPORTANTE:\n"
        interpretacao += "Esta interpretação é gerada automaticamente por um sistema de inteligência artificial e deve ser validada por um médico especialista. "
        interpretacao += "A correlação com dados clínicos e laboratoriais é imprescindível para o diagnóstico definitivo. "
        interpretacao += "O resultado não substitui a avaliação médica presencial."
        
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
        
        # Usar emojis para tornar mais amigável e organizar a informação
        descobertas += f"DIAGNÓSTICO SUGERIDO: {diagnostico}\n"
        descobertas += f"NÍVEL DE CONFIANÇA: {probabilidade:.1f}%\n\n"
        
        # Adicionar classificação de confiabilidade em linguagem simples
        if probabilidade >= 90:
            descobertas += "CONFIABILIDADE: ALTA\n\n"
        elif probabilidade >= 75:
            descobertas += "CONFIABILIDADE: MODERADA\n\n"
        else:
            descobertas += "CONFIABILIDADE: LIMITADA\n\n"
        
        # Explicação do diagnóstico em linguagem simples
        descobertas += "O QUE ISTO SIGNIFICA:\n\n"
        
        if diagnostico == "Tuberculose":
            descobertas += "• A imagem do seu pulmão apresenta sinais que podem indicar tuberculose\n\n"
            descobertas += "• A tuberculose é uma infecção causada por uma bactéria que afeta principalmente os pulmões\n\n"
            descobertas += "• Sintomas comuns incluem:\n"
            descobertas += "  - Tosse persistente por mais de 3 semanas\n"
            descobertas += "  - Febre, geralmente no período da tarde\n"
            descobertas += "  - Suores noturnos que podem molhar a roupa de cama\n"
            descobertas += "  - Perda de peso sem causa aparente\n"
            descobertas += "  - Cansaço e fraqueza\n\n"
            descobertas += "• A tuberculose tem tratamento eficaz e cura na maioria dos casos quando seguido corretamente\n\n"
            descobertas += "• É uma doença que pode ser transmitida pelo ar, mas é prevenível e tratável\n\n"
            
        elif diagnostico == "Pneumonia":
            descobertas += "• A imagem do seu pulmão mostra áreas que sugerem uma infecção chamada pneumonia\n\n"
            descobertas += "• A pneumonia é uma inflamação nos pulmões geralmente causada por bactérias, vírus ou fungos\n\n"
            descobertas += "• Sintomas comuns incluem:\n"
            descobertas += "  - Tosse com catarro (que pode ser amarelado ou esverdeado)\n"
            descobertas += "  - Febre e calafrios\n"
            descobertas += "  - Dificuldade para respirar ou respiração rápida\n"
            descobertas += "  - Dor no peito ao respirar ou tossir\n"
            descobertas += "  - Sensação de cansaço ou falta de energia\n\n"
            descobertas += "• A maioria das pneumonias pode ser tratada com antibióticos se forem causadas por bactérias\n\n"
            descobertas += "• O tempo de recuperação varia de poucos dias a algumas semanas, dependendo da gravidade\n\n"
            
        elif diagnostico == "Covid-19":
            descobertas += "• A imagem do seu pulmão mostra um padrão que pode ser compatível com Covid-19\n\n"
            descobertas += "• A Covid-19 é causada pelo vírus SARS-CoV-2 e pode afetar os pulmões de maneira característica\n\n"
            descobertas += "• Sintomas comuns incluem:\n"
            descobertas += "  - Febre ou sensação febril\n"
            descobertas += "  - Tosse seca (sem catarro)\n"
            descobertas += "  - Cansaço e dores no corpo\n"
            descobertas += "  - Perda de olfato e/ou paladar\n"
            descobertas += "  - Dificuldade para respirar (em casos mais graves)\n\n"
            descobertas += "• É importante realizar um teste específico para Covid-19 para confirmar o diagnóstico\n\n"
            descobertas += "• O tratamento depende da gravidade dos sintomas e pode incluir medicamentos para aliviar os sintomas\n\n"
            
        elif diagnostico == "Normal":
            descobertas += "• A imagem do seu pulmão não mostra alterações significativas\n\n"
            descobertas += "• Isto significa que não foram encontradas anormalidades visíveis na radiografia\n\n"
            descobertas += "• É importante saber que:\n"
            descobertas += "  - Algumas condições podem não aparecer em radiografias simples\n"
            descobertas += "  - Se você está com sintomas, eles devem ser avaliados pelo seu médico mesmo com raio-x normal\n"
            descobertas += "  - Seu médico pode recomendar outros exames se necessário\n\n"
            descobertas += "• Uma radiografia normal é geralmente um bom sinal, mas não descarta completamente todas as condições\n\n"
        
        # Adicionar outras possibilidades relevantes
        outras_possibilidades = []
        for doenca, prob in sorted(resultados_completos.items(), key=lambda x: x[1], reverse=True):
            if doenca != diagnostico and prob > 15:
                outras_possibilidades.append((doenca, prob))
        
        if outras_possibilidades:
            descobertas += "OUTRAS POSSIBILIDADES A CONSIDERAR:\n\n"
            for doenca, prob in outras_possibilidades:
                descobertas += f"• {doenca} ({prob:.1f}%)\n"
                if doenca == "Tuberculose":
                    descobertas += "  - Infecção que afeta principalmente os pulmões\n"
                elif doenca == "Pneumonia":
                    descobertas += "  - Infecção que causa inflamação nos pulmões\n"
                elif doenca == "Covid-19":
                    descobertas += "  - Infecção viral que pode afetar os pulmões\n"
                elif doenca == "Normal":
                    descobertas += "  - Ausência de alterações significativas\n"
            descobertas += "\n"
        
        # Próximos passos em linguagem acessível
        descobertas += "PRÓXIMOS PASSOS RECOMENDADOS:\n\n"
        descobertas += "Converse com seu médico sobre este resultado\n\n"
        descobertas += "Lembre-se: esta análise foi feita por computador e precisa ser confirmada por um profissional de saúde\n\n"
        descobertas += "Siga as orientações médicas para tratamento ou exames adicionais\n\n"
        descobertas += "Não deixe de relatar todos os seus sintomas ao médico, mesmo se o resultado for normal\n\n"
        descobertas += "Em caso de piora dos sintomas, procure atendimento médico imediatamente\n\n"
        
        # Alerta importante
        descobertas += "IMPORTANTE: Este resultado é uma análise preliminar gerada por inteligência artificial. "
        descobertas += "Toda interpretação deve ser confirmada por um médico qualificado antes de qualquer decisão sobre tratamento ou diagnóstico."
        
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