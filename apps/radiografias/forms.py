# app/radiografias/forms.py
from django import forms
from .models import Radiografia

class RadiografiaCadastroForm(forms.ModelForm):
    class Meta:
        model = Radiografia
        fields = [
            'paciente', 'data', 'tipo', 'descricao', 'equipamento_usado',
            'notas_tecnicas', 'qualidade_da_imagem', 'imagem', 'dose_de_radiacao'
        ]
        widgets = {
            'data': forms.DateInput(attrs={'type': 'date'}),
            'descricao': forms.Textarea(attrs={'rows': 3}),
            'notas_tecnicas': forms.Textarea(attrs={'rows': 3}),
        }