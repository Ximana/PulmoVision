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
        widgets = {
            'foto_perfil': forms.FileInput(attrs={'class': 'form-control-file'}),
            'funcao': forms.Select(attrs={'class': 'form-select'})
        }
        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Aplicar classes Bootstrap aos campos
        for field_name, field in self.fields.items():
            if field_name == 'funcao':
                field.widget.attrs['class'] = 'form-select'
            else:
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
            
class UsuarioPerfilForm(forms.ModelForm):
    class Meta:
        model = Usuario
        fields = ['first_name', 'last_name', 'email', 'telefone', 'especializacao']
        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Tornar campos obrigatórios
        self.fields['first_name'].required = True
        self.fields['last_name'].required = True
        self.fields['email'].required = True
        
    def clean_email(self):
        email = self.cleaned_data.get('email')
        if email and Usuario.objects.exclude(pk=self.instance.pk).filter(email=email).exists():
            raise forms.ValidationError('Este email já está em uso.')
        return email