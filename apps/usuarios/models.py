#apps/usuarios/models.py
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.urls import reverse
import uuid
import os

def usuario_foto_path(instance, filename):
    ext = filename.split('.')[-1]
    filename = f'{uuid.uuid4().hex}.{ext}'
    return os.path.join('usuarios/perfil', filename)


class Usuario(AbstractUser):
    FUNCAO_CHOICES = (
        ('admin', 'Administrador'),
        ('medico', 'Médico'),
        ('tecnico', 'Técnico'),
        ('pesquisador', 'Pesquisador'),
    )
    
    # Campos básicos
    funcao = models.CharField(
        'Função',
        max_length=20,
        choices=FUNCAO_CHOICES,
        null=False,
        blank=False,
        help_text='Função do usuário no sistema'
    )
    
    # Informações de contato
    telefone = models.CharField(
        'Telefone',
        max_length=20,
        blank=True,
        help_text='Número de telefone para contato'
    )
    
    # Informações profissionais
    registro_profissional = models.CharField(
        'Registro Profissional',
        max_length=20,
        blank=True,
        help_text='Número de ordem/registro profissional'
    )
    especializacao = models.CharField(
        'Especialização',
        max_length=100,
        blank=True,
        help_text='Área de especialização'
    )
    
    # Mídia
    foto_perfil = models.ImageField(
        'Foto de Perfil',
        upload_to=usuario_foto_path,
        blank=True,
        null=True,
        help_text='Foto de perfil do usuário'
    )
    
    # Campos de sistema
    data_criacao = models.DateTimeField(
        'Data de Criação',
        auto_now_add=True
    )
    data_atualizacao = models.DateTimeField(
        'Data de Atualização',
        auto_now=True
    )
    
    class Meta:
        verbose_name = 'Usuário'
        verbose_name_plural = 'Usuários'
        ordering = ['first_name', 'last_name']
        
        
    def __str__(self):
        return f"{self.get_full_name()} ({self.get_funcao_display()})"
    
    def get_absolute_url(self):
        return reverse('usuarios:detalhe', kwargs={'pk': self.pk})
    
    def get_nome_completo(self):
        """Retorna o nome completo do usuário."""
        return self.get_full_name() or self.username
    
    def is_medico(self):
        """Verifica se o usuário é um médico."""
        return self.funcao == 'medico'
    
    def is_tecnico(self):
        """Verifica se o usuário é um técnico."""
        return self.funcao == 'tecnico'
    
    def is_admin(self):
        """Verifica se o usuário é um administrador."""
        return self.funcao == 'admin'
    
    def is_pesquisador(self):
        """Verifica se o usuário é um pesquisador."""
        return self.funcao == 'pesquisador'
    
    def save(self, *args, **kwargs):
        """Sobrescreve o método save para garantir que alguns campos estejam preenchidos
        baseados na função do usuário."""
        if self.funcao in ['medico', 'tecnico']:
            if not self.registro_profissional:
                raise ValueError('Registro profissional é obrigatório para médicos e técnicos.')
        
        # Garante que o username seja sempre em minúsculas
        self.username = self.username.lower()
        
        super().save(*args, **kwargs)
        
        
    def get_radiografias_realizadas(self):
        """Retorna todas as radiografias realizadas pelo usuário."""
        return self.radiografias.all()

    def get_total_radiografias(self):
        """Retorna o total de radiografias realizadas pelo usuário."""
        return self.radiografias.count()
    
    def get_total_deteccoes(self):
        """Retorna o total de radiografias realizadas pelo usuário."""
        return self.deteccoes.count()
    
