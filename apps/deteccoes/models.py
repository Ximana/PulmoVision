#apps/deteccoes/models-py
from django.db import models
from django.urls import reverse
from django.conf import settings
from django.core.validators import MinValueValidator, MaxValueValidator
from apps.radiografias.models import Radiografia

class Deteccao(models.Model):
    DOENCA_CHOICES = (
        ('Tuberculose', 'Tuberculose'),
        ('Pneumonia', 'Pneumonia'),
        ('Covid-19', 'Covid-19'),
    )
    
    ESTADO_CHOICES = (
        ('Pendente', 'Pendente'),
        ('Em Análise', 'Em Análise'),
        ('Concluído', 'Concluído'),
        ('Revisão Necessária', 'Revisão Necessária'),
    )
    
    # Relacionamentos
    radiografia = models.ForeignKey(
        Radiografia,
        on_delete=models.CASCADE,
        verbose_name='Radiografia',
        related_name='deteccoes'
    )
    usuario = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        verbose_name='Usuário',
        related_name='deteccoes'
    )
    
    # Dados da Detecção
    doenca = models.CharField(
        'Doença',
        max_length=20,
        choices=DOENCA_CHOICES
    )
    resultado = models.CharField(
        'Resultado',
        max_length=255,
        help_text='Resultado da análise de detecção'
    )
    probabilidade = models.DecimalField(
        'Probabilidade',
        max_digits=5,
        decimal_places=2,
        help_text='Probabilidade em porcentagem (0-100)'
    )
    descobertas = models.TextField(
        'Descobertas',
        help_text='Descobertas detalhadas da análise'
    )
    estado = models.CharField(
        'Estado',
        max_length=20,
        choices=ESTADO_CHOICES,
        default='Pendente'
    )
    
    # Campos de Sistema
    criado_em = models.DateTimeField('Criado em', auto_now_add=True)
    atualizado_em = models.DateTimeField('Atualizado em', auto_now=True)
    
    class Meta:
        verbose_name = 'Detecção'
        verbose_name_plural = 'Detecções'
        ordering = ['-criado_em']
        
    def __str__(self):
        return f"Detecção de {self.doenca} - Paciente: {self.radiografia.paciente.get_nome_completo()} - Data: {self.data}"
    
    def get_absolute_url(self):
        return reverse("deteccoes:detalhe", kwargs={"pk": self.pk})
    

class AvaliacaoDeteccao(models.Model):
    AVALIACAO_CHOICES = (
        ('Correto', 'Correto'),
        ('Parcialmente Correto', 'Parcialmente Correto'),
        ('Incorreto', 'Incorreto'),
    )
    
    # Relacionamentos
    deteccao = models.ForeignKey(
        Deteccao,  # Agora referenciamos diretamente a classe Deteccao
        on_delete=models.CASCADE,
        verbose_name='Detecção',
        related_name='avaliacoes'
    )
    usuario = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        verbose_name='Usuário',
        related_name='avaliacoes_deteccao'
    )
    
    # Dados da Avaliação
    avaliacao = models.CharField(
        'Avaliação',
        max_length=20,
        choices=AVALIACAO_CHOICES,
        help_text='Avaliação geral da detecção'
    )
    criticas = models.TextField(
        'Críticas',
        blank=True,
        null=True,
        help_text='Críticas construtivas sobre a detecção'
    )
    sugestoes = models.TextField(
        'Sugestões',
        blank=True,
        null=True,
        help_text='Sugestões de melhoria para o sistema'
    )
    
    # Campos de Sistema
    criado_em = models.DateTimeField('Criado em', auto_now_add=True)
    atualizado_em = models.DateTimeField('Atualizado em', auto_now=True)
    
    class Meta:
        verbose_name = 'Avaliação de Detecção'
        verbose_name_plural = 'Avaliações de Detecção'
        ordering = ['-criado_em']
        unique_together = ['deteccao', 'usuario']
        
    def __str__(self):
        return f"Avaliação - Detecção: {self.deteccao.id} - Usuário: {self.usuario.get_nome_completo()}"
    
    def get_absolute_url(self):
        return reverse("avaliacoes:detalhe", kwargs={"pk": self.pk})