# apps/deteccoes/forms.py
from django import forms
from .models import Deteccao, AvaliacaoDeteccao

class DeteccaoCadastroForm(forms.ModelForm):
    class Meta:
        model = Deteccao
        fields = ['radiografia', 'doenca', 'resultado', 'probabilidade', 
                 'descobertas', 'estado']
        widgets = {
            'radiografia': forms.Select(attrs={'class': 'form-select'}),
            'doenca': forms.Select(attrs={'class': 'form-select'}),
            'resultado': forms.TextInput(attrs={'class': 'form-control'}),
            'probabilidade': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'descobertas': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'estado': forms.Select(attrs={'class': 'form-select'})
        }
        
    def clean_probabilidade(self):
        probabilidade = self.cleaned_data.get('probabilidade')
        if probabilidade is not None:
            if probabilidade < 0 or probabilidade > 100:
                raise forms.ValidationError('A probabilidade deve estar entre 0 e 100.')
        return probabilidade
    
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
