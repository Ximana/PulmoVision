# app/modelos/forms.py
from django import forms
from .models import Modelo

class ModeloCadastroForm(forms.ModelForm):
    class Meta:
        model = Modelo
        fields = ['nome', 'versao', 'data_treino', 'acuracia', 'precisao', 'recall', 
                 'diretorio', 'descricao', 'ativo']
        widgets = {
            'nome': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ex: ResNet50-PulmoVision'
            }),
            'versao': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ex: 1.0, 2.1, 3.0'
            }),
            'data_treino': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
            'acuracia': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01',
                'min': '0',
                'max': '100',
                'placeholder': 'Ex: 95.50'
            }),
            'precisao': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01',
                'min': '0',
                'max': '100',
                'placeholder': 'Ex: 92.30'
            }),
            'recall': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01',
                'min': '0',
                'max': '100',
                'placeholder': 'Ex: 88.75'
            }),
            'diretorio': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ex: /models/resnet50/ ou https://example.com/modelo/'
            }),
            'descricao': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Descrição detalhada do modelo, arquitetura utilizada, datasets de treino, etc.'
            }),
            'ativo': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            })
        }
        labels = {
            'nome': 'Nome do Modelo',
            'versao': 'Versão',
            'data_treino': 'Data do Treino',
            'acuracia': 'Acurácia (%)',
            'precisao': 'Precisão (%)',
            'recall': 'Recall (%)',
            'diretorio': 'Diretório/URL do Modelo',
            'descricao': 'Descrição',
            'ativo': 'Modelo Ativo'
        }

    def clean_nome(self):
        nome = self.cleaned_data.get('nome')
        if nome:
            nome = nome.strip()
            if len(nome) < 3:
                raise forms.ValidationError('O nome do modelo deve ter pelo menos 3 caracteres.')
        return nome

    def clean_versao(self):
        versao = self.cleaned_data.get('versao')
        if versao:
            versao = versao.strip()
            if not versao:
                raise forms.ValidationError('A versão é obrigatória.')
        return versao

    def clean_diretorio(self):
        diretorio = self.cleaned_data.get('diretorio')
        if diretorio:
            diretorio = diretorio.strip()
            if not diretorio:
                raise forms.ValidationError('O diretório/URL é obrigatório.')
        return diretorio

    def clean(self):
        cleaned_data = super().clean()
        nome = cleaned_data.get('nome')
        versao = cleaned_data.get('versao')
        
        # Verificar se já existe um modelo com o mesmo nome e versão
        if nome and versao:
            existing = Modelo.objects.filter(nome=nome, versao=versao)
            if self.instance.pk:
                existing = existing.exclude(pk=self.instance.pk)
            
            if existing.exists():
                raise forms.ValidationError(
                    f'Já existe um modelo com nome "{nome}" e versão "{versao}". '
                    'Use um nome ou versão diferentes.'
                )
        
        return cleaned_data


class ModeloEdicaoForm(forms.ModelForm):
    class Meta:
        model = Modelo
        fields = ['nome', 'versao', 'data_treino', 'acuracia', 'precisao', 'recall', 
                 'diretorio', 'descricao', 'ativo']
        widgets = {
            'nome': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ex: ResNet50-PulmoVision'
            }),
            'versao': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ex: 1.0, 2.1, 3.0'
            }),
            'data_treino': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
            'acuracia': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01',
                'min': '0',
                'max': '100',
                'placeholder': 'Ex: 95.50'
            }),
            'precisao': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01',
                'min': '0',
                'max': '100',
                'placeholder': 'Ex: 92.30'
            }),
            'recall': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01',
                'min': '0',
                'max': '100',
                'placeholder': 'Ex: 88.75'
            }),
            'diretorio': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ex: /models/resnet50/ ou https://example.com/modelo/'
            }),
            'descricao': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Descrição detalhada do modelo, arquitetura utilizada, datasets de treino, etc.'
            }),
            'ativo': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            })
        }
        labels = {
            'nome': 'Nome do Modelo',
            'versao': 'Versão',
            'data_treino': 'Data do Treino',
            'acuracia': 'Acurácia (%)',
            'precisao': 'Precisão (%)',
            'recall': 'Recall (%)',
            'diretorio': 'Diretório/URL do Modelo',
            'descricao': 'Descrição',
            'ativo': 'Modelo Ativo'
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Tornar alguns campos não obrigatórios na edição
        self.fields['descricao'].required = False

    def clean_nome(self):
        nome = self.cleaned_data.get('nome')
        if nome:
            nome = nome.strip()
            if len(nome) < 3:
                raise forms.ValidationError('O nome do modelo deve ter pelo menos 3 caracteres.')
        return nome

    def clean_versao(self):
        versao = self.cleaned_data.get('versao')
        if versao:
            versao = versao.strip()
            if not versao:
                raise forms.ValidationError('A versão é obrigatória.')
        return versao

    def clean_diretorio(self):
        diretorio = self.cleaned_data.get('diretorio')
        if diretorio:
            diretorio = diretorio.strip()
            if not diretorio:
                raise forms.ValidationError('O diretório/URL é obrigatório.')
        return diretorio

    def clean(self):
        cleaned_data = super().clean()
        nome = cleaned_data.get('nome')
        versao = cleaned_data.get('versao')
        
        # Verificar se já existe um modelo com o mesmo nome e versão
        if nome and versao:
            existing = Modelo.objects.filter(nome=nome, versao=versao)
            if self.instance.pk:
                existing = existing.exclude(pk=self.instance.pk)
            
            if existing.exists():
                raise forms.ValidationError(
                    f'Já existe um modelo com nome "{nome}" e versão "{versao}". '
                    'Use um nome ou versão diferentes.'
                )
        
        return cleaned_data


class ModeloBuscaForm(forms.Form):
    """Form para busca de modelos"""
    search = forms.CharField(
        max_length=100,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Pesquisar por nome do modelo ou versão'
        }),
        label='Buscar'
    )
    
    ativo = forms.BooleanField(
        required=False,
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        label='Apenas modelos ativos'
    )