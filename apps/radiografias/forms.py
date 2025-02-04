from django import forms
from .models import Radiografia

class RadiografiaCadastroForm(forms.ModelForm):
    class Meta:
        model = Radiografia
        fields = ['paciente', 'data', 'tipo', 'equipamento_usado', 'qualidade_da_imagem', 
                 'dose_de_radiacao', 'imagem', 'descricao', 'notas_tecnicas']
        widgets = {
            'paciente': forms.Select(attrs={'class': 'form-select'}),
            'data': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'tipo': forms.Select(attrs={'class': 'form-select'}),
            'equipamento_usado': forms.Select(attrs={'class': 'form-select'}),
            'qualidade_da_imagem': forms.Select(attrs={'class': 'form-select'}),
            'dose_de_radiacao': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'descricao': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'notas_tecnicas': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'imagem': forms.FileInput(attrs={'class': 'form-control'})
        }