# apps/deteccoes/forms.py
from django import forms
from .models import Deteccao, AvaliacaoDeteccao

class DeteccaoCadastroForm(forms.ModelForm):
    class Meta:
        model = Deteccao
        fields = ['radiografia']
        widgets = {
            'radiografia': forms.Select(attrs={'class': 'form-select'}),
        }
    
class AvaliacaoDeteccaoCadastroForm(forms.ModelForm):
    class Meta:
        model = AvaliacaoDeteccao
        fields = ['avaliacao', 'criticas', 'sugestoes']
        widgets = {
            'avaliacao': forms.Select(
                attrs={'class': 'form-select'},
                choices=AvaliacaoDeteccao.AVALIACAO_CHOICES
            ),
            'criticas': forms.Textarea(
                attrs={'class': 'form-control', 'rows': 3}
            ),
            'sugestoes': forms.Textarea(
                attrs={'class': 'form-control', 'rows': 3}
            ),
        }
