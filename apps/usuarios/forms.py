#/app/usuarios/forms.py
from django import forms
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from .models import Usuario

class UsuarioRegistroForm(UserCreationForm):
    class Meta:
        model = Usuario
        fields = ('username', 'email', 'first_name', 'last_name', 'funcao', 
                 'telefone', 'registro_profissional', 'especializacao', 
                 'foto_perfil', 'password1', 'password2')
        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs['class'] = 'form-control'

class UsuarioEdicaoForm(UserChangeForm):
    password = None
    
    class Meta:
        model = Usuario
        fields = ('email', 'first_name', 'last_name', 'funcao', 
                 'telefone', 'registro_profissional', 'especializacao', 
                 'foto_perfil', 'is_active')
        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs['class'] = 'form-control'