# app/modelos/models.py
from django.db import models
from django.urls import reverse
from django.conf import settings
from django.core.validators import MinValueValidator, MaxValueValidator
import uuid
import os

class Modelo(models.Model):
    """
    Modelo para armazenar informações sobre modelos de IA
    para detecção de doenças pulmonares
    """
    
    # Informações básicas do modelo
    nome = models.CharField(
        'Nome do Modelo',
        max_length=100,
        help_text='Nome identificador do modelo de IA'
    )
    versao = models.CharField(
        'Versão',
        max_length=20,
        help_text='Versão do modelo (ex: 1.0, 2.1, etc.)'
    )
    data_treino = models.DateField(
        'Data do Treino',
        help_text='Data em que o modelo foi treinado'
    )
    
    # Métricas de performance
    acuracia = models.DecimalField(
        'Acurácia',
        max_digits=5,
        decimal_places=2,
        validators=[MinValueValidator(0.00), MaxValueValidator(100.00)],
        help_text='Acurácia do modelo em porcentagem (0-100%)'
    )
    precisao = models.DecimalField(
        'Precisão',
        max_digits=5,
        decimal_places=2,
        validators=[MinValueValidator(0.00), MaxValueValidator(100.00)],
        help_text='Precisão do modelo em porcentagem (0-100%)'
    )
    recall = models.DecimalField(
        'Recall',
        max_digits=5,
        decimal_places=2,
        validators=[MinValueValidator(0.00), MaxValueValidator(100.00)],
        help_text='Recall do modelo em porcentagem (0-100%)'
    )
    
    # Localização do modelo
    diretorio = models.CharField(
        'Diretório/URL do Modelo',
        max_length=500,
        help_text='Caminho para o diretório contendo modelo.keras e config.json, ou URL do modelo'
    )
    
    # Informações adicionais
    descricao = models.TextField(
        'Descrição',
        blank=True,
        null=True,
        help_text='Descrição detalhada do modelo e suas características'
    )
    
    # Relacionamento com usuário
    usuario = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        verbose_name='Usuário Responsável',
        related_name='modelos',
        help_text='Usuário responsável pelo cadastro do modelo'
    )
    
    # Campos de sistema
    criado_em = models.DateTimeField('Criado em', auto_now_add=True)
    atualizado_em = models.DateTimeField('Atualizado em', auto_now=True)
    
    # Status do modelo
    ativo = models.BooleanField(
        'Modelo Ativo',
        default=True,
        help_text='Define se o modelo está ativo para uso no sistema'
    )
    
    class Meta:
        verbose_name = 'Modelo'
        verbose_name_plural = 'Modelos'
        ordering = ['-data_treino', '-criado_em']
        unique_together = ['nome', 'versao']  # Evita duplicação de nome+versão
        
    def __str__(self):
        return f"{self.nome} v{self.versao} - Acurácia: {self.acuracia}%"
    
    def get_absolute_url(self):
        return reverse("modelos:detalhe", kwargs={"pk": self.pk})
    
    def get_usuario_nome(self):
        """Retorna o nome do usuário responsável pelo modelo."""
        return self.usuario.get_nome_completo()

    def get_usuario_funcao(self):
        """Retorna a função do usuário responsável pelo modelo."""
        return self.usuario.get_funcao_display()
    
    def get_f1_score(self):
        """Calcula e retorna o F1-Score baseado na precisão e recall."""
        try:
            precisao_decimal = float(self.precisao) / 100
            recall_decimal = float(self.recall) / 100
            f1 = 2 * (precisao_decimal * recall_decimal) / (precisao_decimal + recall_decimal)
            return round(f1 * 100, 2)
        except (ZeroDivisionError, TypeError):
            return 0.00
    
    def get_status_performance(self):
        """Retorna o status de performance baseado na acurácia."""
        acuracia = float(self.acuracia)
        if acuracia >= 90:
            return 'Excelente'
        elif acuracia >= 80:
            return 'Boa'
        elif acuracia >= 70:
            return 'Regular'
        else:
            return 'Baixa'
    
    def is_modelo_local(self):
        """Verifica se o modelo está armazenado localmente."""
        return not self.diretorio.startswith(('http://', 'https://'))
    
    def get_tipo_armazenamento(self):
        """Retorna o tipo de armazenamento do modelo."""
        if self.is_modelo_local():
            return 'Local'
        else:
            return 'Remoto (URL)'