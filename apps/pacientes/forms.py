from django import forms
from .models import Paciente

class PacienteRegistroForm(forms.ModelForm):
    class Meta:
        model = Paciente
        fields = [
            'nome', 'sobrenome', 'data_nascimento', 'genero', 'tipo_sanguineo',
            'nome_da_mae', 'numero_bi', 'telefone', 'contato_emergencia',
            'municipio', 'provincia', 'foto'
        ]
        widgets = {
            'data_nascimento': forms.DateInput(attrs={'type': 'date'}),
            'foto': forms.FileInput(attrs={'class': 'form-control-file'})
        }