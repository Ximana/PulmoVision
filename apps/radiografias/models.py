#app/radiografia/models.py
from django.db import models
from django.urls import reverse
from django.conf import settings
from apps.pacientes.models import Paciente
import uuid
import os

""" upload na pasta do projecto
def radiografia_imagem_path(instance, filename):
    ext = filename.split('.')[-1]
    filename = f'{uuid.uuid4().hex}.{ext}'
    return os.path.join('exames', filename)
"""

def radiografia_imagem_path(instance, filename):
    """
    Função otimizada para Cloudinary
    """
    ext = filename.split('.')[-1]
    filename = f'{uuid.uuid4().hex}.{ext}'
    # Use '/' ao invés de os.path.join para Cloudinary
    return f'projectos/django/pulmovision/radiografias/{filename}'

class Radiografia(models.Model):
    TIPOS_EXAME_CHOICES = (
        ('Raio-X', 'Raio-X'),
        ('Tomografia Computadorizada', 'Tomografia Computadorizada'),
    )
    
    EQUIPAMENTO_CHOICES = (
        ('Radiografia Digital (DR)', 'Radiografia Digital (DR)'),
        ('Radiografia Computadorizada (CR)', 'Radiografia Computadorizada (CR)'),
        ('Radiografia Convencional', 'Radiografia Convencional'),
        ('Equipamento Portátil', 'Equipamento Portátil'),
    )
    
    QUALIDADE_IMAGEM_CHOICES = (
        ('Ótima', 'Ótima'),
        ('Boa', 'Boa'),
        ('Regular', 'Regular'),
        ('Ruim', 'Ruim'),
    )
    
    # Relacionamentos
    paciente = models.ForeignKey(
        Paciente, 
        on_delete=models.CASCADE,
        verbose_name='Paciente',
        related_name='radiografias'
    )
    usuario = models.ForeignKey(
        settings.AUTH_USER_MODEL,  # Usuario
        on_delete=models.CASCADE,
        verbose_name='Usuário',
        related_name='radiografias'
    )
    
    # Dados do Exame
    data = models.DateField('Data do Exame')
    tipo = models.CharField(
        'Tipo de Exame',
        max_length=40,
        choices=TIPOS_EXAME_CHOICES
    )
    descricao = models.TextField('Descrição', blank=True, null=True)
    equipamento_usado = models.CharField(
        'Equipamento Utilizado',
        max_length=50,
        choices=EQUIPAMENTO_CHOICES
    )
    notas_tecnicas = models.TextField('Notas Técnicas', blank=True, null=True)
    qualidade_da_imagem = models.CharField(
        'Qualidade da Imagem',
        max_length=10,
        choices=QUALIDADE_IMAGEM_CHOICES
    )
    imagem = models.ImageField(
        'Imagem',
        upload_to=radiografia_imagem_path,
        help_text='Formatos aceitos: .jpg, .jpeg, .png'
    )
    
    dose_de_radiacao = models.DecimalField(
        'Dose de Radiação (mSv)',
        max_digits=5,
        decimal_places=2,
        blank=True,
        null=True,
        help_text='Dose de radiação em millisieverts (mSv)'
    )
    
    
    # Campos de Sistema
    criado_em = models.DateTimeField('Criado em', auto_now_add=True)
    atualizado_em = models.DateTimeField('Atualizado em', auto_now=True)
    
    class Meta:
        verbose_name = 'Radiografia'
        verbose_name_plural = 'Radiografias'
        ordering = ['-data', '-criado_em']
        
    def __str__(self):
        return f"Exame {self.tipo} - Paciente: {self.paciente.nome} {self.paciente.sobrenome} - Data: {self.data}"
    
    def get_absolute_url(self):
        return reverse("radiografias:detalhe", kwargs={"pk": self.pk})
    
    def get_usuario_nome(self):
        """Retorna o nome do usuário que realizou a radiografia."""
        return self.usuario.get_nome_completo()

    def get_usuario_funcao(self):
        """Retorna a função do usuário que realizou a radiografia."""
        return self.usuario.get_funcao_display()