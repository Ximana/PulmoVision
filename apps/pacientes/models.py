from django.db import models
from django.urls import reverse

class Paciente(models.Model):
    GENERO_CHOICES = (
        ('M', 'Masculino'),
        ('F', 'Feminino'),
        ('O', 'Outro'),
    )
    
    TIPO_SANGUINEO_CHOICES = (
        ('A+', 'A+'), ('A-', 'A-'),
        ('B+', 'B+'), ('B-', 'B-'),
        ('AB+', 'AB+'), ('AB-', 'AB-'),
        ('O+', 'O+'), ('O-', 'O-'),
    )
    
    # Dados Pessoais
    nome = models.CharField('Nome', max_length=100)
    sobrenome = models.CharField('Sobrenome', max_length=100)    
    data_nascimento = models.DateField('Data de Nascimento')
    genero = models.CharField('Gênero', max_length=10, choices=GENERO_CHOICES)
    tipo_sanguineo = models.CharField('Tipo Sanguíneo', max_length=3, choices=TIPO_SANGUINEO_CHOICES, blank=True, null=True)
    nome_da_mae = models.CharField('Nome da mãe', max_length=100, blank=True, null=True)
    numero_bi = models.CharField('Número do BI', max_length=30, unique=True, blank=True, null=True, help_text='Número do BI')
    
    # Contactos
    telefone = models.CharField('Telefone', max_length=20, blank=True, null=True)
    contato_emergencia = models.CharField('Contacto de Emergência', max_length=100, blank=True, null=True)
    
    # Endereço
    municipio = models.CharField('Município', max_length=100, blank=True, null=True)
    provincia = models.CharField('Província', max_length=100, blank=True, null=True)
    
    # Sistema
    foto = models.ImageField('Foto', upload_to='pacientes/fotos', blank=True, null=True)
    data_criacao = models.DateTimeField('Data de Criação', auto_now_add=True)
    data_atualizacao = models.DateTimeField('Data de Atualização', auto_now=True)
    
    class Meta:
        verbose_name = 'Paciente'
        verbose_name_plural = 'Pacientes'
        ordering = ['nome', 'sobrenome']
        
    def __str__(self):
        return f"{self.nome} {self.sobrenome}"
    
    def get_absolute_url(self):
        return reverse("pacientes:detalhe", kwargs={"pk": self.pk})
    
    def get_idade(self):
        from datetime import date
        hoje = date.today()
        return hoje.year - self.data_nascimento.year - ((hoje.month, hoje.day) < (self.data_nascimento.month, self.data_nascimento.day))

    def get_nome_completo(self):
        return f"{self.nome} {self.sobrenome}"