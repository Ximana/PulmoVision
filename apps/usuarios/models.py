from django.contrib.auth.models import AbstractUser
from django.db import models

class Usuario(AbstractUser):
    FUNCAO_CHOICES = (
        ('admin', 'Administrador'),
        ('medico', 'Médico'),
        ('tecnico', 'Técnico'),
        ('pesquisador', 'Pesquisador'),
    )
    
    funcao = models.CharField('Função', max_length=20, choices=FUNCAO_CHOICES)
    telefone = models.CharField('Telefone', max_length=20, blank=True)
    registro_profissional = models.CharField('Registro Profissional', max_length=20, blank=True, help_text='Número de ordem')
    especializacao = models.CharField('Especialização', max_length=100, blank=True)
    foto_perfil = models.ImageField('Foto de Perfil', upload_to='usuarios/perfil', blank=True, null=True)
    data_criacao = models.DateTimeField('Data de Criação', auto_now_add=True)
    data_atualizacao = models.DateTimeField('Data de Atualização', auto_now=True)

    class Meta:
        verbose_name = 'Usuário'
        verbose_name_plural = 'Usuários'
        ordering = ['first_name', 'last_name']

    def __str__(self):
        return f"{self.get_full_name()} ({self.get_funcao_display()})"

    def get_nome_completo(self):
        return f"{self.first_name} {self.last_name}"