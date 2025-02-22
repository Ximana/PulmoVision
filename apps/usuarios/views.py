#/app/usuarios/views.py
from django.contrib.auth import login, logout, authenticate, update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django.views.generic import ListView, CreateView, UpdateView, DeleteView, DetailView, TemplateView, View
from django.contrib import messages
from .models import Usuario
from .forms import UsuarioRegistroForm, UsuarioEdicaoForm
from django.contrib.auth.forms import PasswordChangeForm

def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            messages.success(request, 'Login realizado com sucesso!')
            return redirect('home')
        else:
            messages.error(request, 'Usuário ou senha inválidos')
    return render(request, 'usuarios/login.html')

@login_required
def logout_view(request):
    logout(request)
    messages.success(request, 'Logout realizado com sucesso!')
    return redirect('home')

class UsuarioListView(LoginRequiredMixin, UserPassesTestMixin, ListView):
    model = Usuario
    template_name = 'usuarios/lista.html'
    context_object_name = 'usuarios'
    paginate_by = 10

    def test_func(self):
        return self.request.user.funcao == 'admin'

class UsuarioCreateView(LoginRequiredMixin, UserPassesTestMixin, CreateView):
    model = Usuario
    form_class = UsuarioRegistroForm
    template_name = 'usuarios/usuario_form.html'
    success_url = reverse_lazy('usuario_lista')

    def test_func(self):
        return self.request.user.funcao == 'admin'

    def form_valid(self, form):
        messages.success(self.request, 'Usuário criado com sucesso!')
        return super().form_valid(form)

class UsuarioUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Usuario
    form_class = UsuarioEdicaoForm
    template_name = 'usuarios/usuario_form.html'
    success_url = reverse_lazy('usuario_lista')

    def test_func(self):
        return self.request.user.funcao == 'admin'

    def form_valid(self, form):
        messages.success(self.request, 'Usuário atualizado com sucesso!')
        return super().form_valid(form)

class UsuarioDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Usuario
    template_name = 'usuarios/usuario_confirmar_delete.html'
    success_url = reverse_lazy('usuario_lista')

    def test_func(self):
        return self.request.user.funcao == 'admin'

    def delete(self, request, *args, **kwargs):
        messages.success(request, 'Usuário removido com sucesso!')
        return super().delete(request, *args, **kwargs)
    

class UsuarioPerfilView(LoginRequiredMixin, DetailView):
    model = Usuario
    template_name = 'usuaios/perfil.html'
    context_object_name = 'usuario'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Adiciona o formulário no contexto
        context['form'] = UsuarioEdicaoForm(instance=self.object)
        
        return context
    
class PerfilView(LoginRequiredMixin, TemplateView):
    template_name = 'usuarios/perfil.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        
        # Calcular estatísticas do usuário
        deteccoes = user.radiografias.all().prefetch_related('deteccoes')
        total_deteccoes = sum(radiografia.deteccoes.count() for radiografia in deteccoes)
        
        # Calcular taxa de precisão média das detecções
        taxa_precisao = 0
        deteccoes_com_probabilidade = []
        for radiografia in deteccoes:
            deteccoes_com_probabilidade.extend(
                radiografia.deteccoes.filter(probabilidade__isnull=False)
                .values_list('probabilidade', flat=True)
            )
        
        if deteccoes_com_probabilidade:
            taxa_precisao = round(sum(deteccoes_com_probabilidade) / len(deteccoes_com_probabilidade), 1)
        
        context.update({
            'total_deteccoes': total_deteccoes,
            'taxa_precisao': taxa_precisao,
        })
        
        return context


class AtualizarPerfilView(LoginRequiredMixin, UpdateView):
    model = Usuario
    fields = ['first_name', 'last_name', 'email', 'telefone', 'especializacao']
    template_name = 'usuarios/perfil.html'  # Será redirecionado, não precisa de template próprio
    success_url = reverse_lazy('usuarios:perfil')
    
    def get_object(self, queryset=None):
        return self.request.user
    
    def form_valid(self, form):
        messages.success(self.request, 'Perfil atualizado com sucesso!')
        return super().form_valid(form)
    
    def form_invalid(self, form):
        messages.error(self.request, 'Erro ao atualizar perfil. Verifique os dados informados.')
        return redirect('usuarios:perfil')


class AtualizarFotoView(LoginRequiredMixin, View):
    def post(self, request, *args, **kwargs):
        try:
            foto = request.FILES.get('foto_perfil')
            if foto:
                # Se já existe uma foto, deletar a antiga
                if request.user.foto_perfil:
                    request.user.foto_perfil.delete()
                
                request.user.foto_perfil = foto
                request.user.save()
                messages.success(request, 'Foto de perfil atualizada com sucesso!')
            else:
                messages.error(request, 'Nenhuma foto foi selecionada.')
                
        except Exception as e:
            messages.error(request, 'Erro ao atualizar foto de perfil.')
            
        return redirect('usuarios:perfil')
    
class AlterarSenhaView(LoginRequiredMixin, View):
    def post(self, request, *args, **kwargs):
        senha_atual = request.POST.get('senha_atual')
        nova_senha = request.POST.get('nova_senha')
        confirmar_senha = request.POST.get('confirmar_senha')
        
        if not request.user.check_password(senha_atual):
            messages.error(request, 'Senha atual incorreta.')
            return redirect('usuarios:perfil')
            
        if nova_senha != confirmar_senha:
            messages.error(request, 'As novas senhas não coincidem.')
            return redirect('usuarios:perfil')
            
        if len(nova_senha) < 8:
            messages.error(request, 'A nova senha deve ter pelo menos 8 caracteres.')
            return redirect('usuarios:perfil')
            
        # Verificar se a senha contém letras e números
        if not any(c.isalpha() for c in nova_senha) or not any(c.isdigit() for c in nova_senha):
            messages.error(request, 'A senha deve conter letras e números.')
            return redirect('usuarios:perfil')
        
        try:
            request.user.set_password(nova_senha)
            request.user.save()
            # Atualiza a sessão para manter o usuário logado
            update_session_auth_hash(request, request.user)
            messages.success(request, 'Senha alterada com sucesso!')
        except Exception as e:
            messages.error(request, 'Erro ao alterar a senha. Tente novamente.')
            
        return redirect('usuarios:perfil')