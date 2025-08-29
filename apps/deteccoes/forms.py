# apps/deteccoes/forms.py
from django import forms
from .models import Deteccao, AvaliacaoDeteccao
from apps.modelos.models import Modelo

class DeteccaoCadastroForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Filtrar apenas modelos ativos
        self.fields['modelo'].queryset = Modelo.objects.filter(ativo=True)
        
        # Tentar definir o modelo padrão 'pv1'
        try:
            modelo_padrao = Modelo.objects.filter(nome='pv1', ativo=True).first()
            if modelo_padrao:
                self.fields['modelo'].initial = modelo_padrao
        except Modelo.DoesNotExist:
            pass
    
    class Meta:
        model = Deteccao
        fields = ['radiografia', 'modelo']
        widgets = {
            'radiografia': forms.Select(attrs={'class': 'form-select'}),
            'modelo': forms.Select(attrs={'class': 'form-select'}),
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