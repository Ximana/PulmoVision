from django.db import models
from django.urls import reverse
from ..pacientes.models import Paciente
from ..usuarios.models import Usuario

class Radiografia(models.Model):
    TIPOS_EXAME_CHOICES = (
        ('XRAY', 'Raio-X'),
        ('CT', 'Tomografia Computadorizada'),
    )
    
    paciente = models.ForeignKey(Paciente, on_delete=models.CASCADE)
    usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE)
    data = models.DateField('Data')
    tipo = models.CharField('Tipo', max_length=50, choices=TIPOS_EXAME_CHOICES)
    
    
    imagem = models.ImageField('Imagem', upload_to='media/exames')
    data_criacao = models.DateTimeField('Data de Criação', auto_now_add=True)
    data_atualizacao = models.DateTimeField('Data de Atualização', auto_now=True)