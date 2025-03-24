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
from django.db.models import Q
from django.http import JsonResponse
import json

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
    
    # Função para pesquisa e filtragem de usuários
    def get_queryset(self):
        queryset = super().get_queryset()
        
        # Busca por texto
        search_query = self.request.GET.get('q', '')
        
        # Filtros específicos
        funcao_filter = self.request.GET.get('funcao', '')
        status_filter = self.request.GET.get('status', '')
        
        # Aplicar filtro de busca textual
        if search_query:
            queryset = queryset.filter(
                Q(first_name__icontains=search_query) |
                Q(last_name__icontains=search_query) |
                Q(username__icontains=search_query) |
                Q(email__icontains=search_query) |
                Q(registro_profissional__icontains=search_query)
            )
        
        # Aplicar filtro por função
        if funcao_filter:
            queryset = queryset.filter(funcao=funcao_filter)
        
        # Aplicar filtro por status
        if status_filter:
            is_active = status_filter == '1'
            queryset = queryset.filter(is_active=is_active)
        
        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = UsuarioRegistroForm()  # Adiciona um formulário vazio ao contexto
        
        # Contagens por função
        context['medicos_count'] = Usuario.objects.filter(funcao='medico').count()
        context['tecnicos_count'] = Usuario.objects.filter(funcao='tecnico').count()
        context['admins_count'] = Usuario.objects.filter(funcao='admin').count()
        context['pesquisadores_count'] = Usuario.objects.filter(funcao='pesquisador').count()
        
        # Adicionar os parâmetros de busca e filtros ao contexto para manter estado
        context['search_query'] = self.request.GET.get('q', '')
        context['funcao_filter'] = self.request.GET.get('funcao', '')
        context['status_filter'] = self.request.GET.get('status', '')
        
        return context
    
    
    def post(self, request, *args, **kwargs):
        form = UsuarioRegistroForm(request.POST, request.FILES)
        is_ajax = request.headers.get('X-Requested-With') == 'XMLHttpRequest'
        
        try:
            if form.is_valid():
                usuario = form.save()
                
                if is_ajax:
                    return JsonResponse({
                        'success': True,
                        'message': 'Usuário cadastrado com sucesso!',
                        'redirect_url': usuario.get_absolute_url()
                    })
                else:
                    messages.success(request, 'Usuário cadastrado com sucesso!')
                    return redirect(usuario.get_absolute_url())
            else:
                # Se o formulário tiver erros de validação
                if is_ajax:
                    # Formatar os erros para JSON
                    field_errors = {}
                    for field, errors in form.errors.items():
                        field_errors[field] = [str(error) for error in errors]
                    
                    return JsonResponse({
                        'success': False,
                        'errors': field_errors,
                        'message': 'Verifique os erros no formulário.'
                    })
                else:
                    messages.error(request, 'Verifique os erros no formulário.')
       
        except ValueError as e:
            # Captura especificamente o erro do registro profissional
            if is_ajax:
                return JsonResponse({
                    'success': False,
                    'errors': {'registro_profissional': [str(e)]},
                    'message': str(e)
                })
            else:
                messages.error(request, str(e))
                form.add_error('registro_profissional', str(e))
        
        except Exception as e:
            # Captura outros erros inesperados
            if is_ajax:
                return JsonResponse({
                    'success': False,
                    'message': f'Erro ao cadastrar usuário: {str(e)}'
                })
            else:
                messages.error(request, f'Erro ao cadastrar usuário: {str(e)}')
        
        # Se o formulário não for válido e não for AJAX, retorna à lista com os erros
        if not is_ajax:
            self.object_list = self.get_queryset()
            context = self.get_context_data(form=form)
            return self.render_to_response(context)
    
class UsuarioDetailView(LoginRequiredMixin, DetailView):
    model = Usuario
    template_name = 'usuarios/detalhe.html'
    context_object_name = 'usuario'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Adiciona o formulário no contexto
        context['form'] = UsuarioRegistroForm(instance=self.object)
        
        return context

class UsuarioDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Usuario
    success_url = reverse_lazy('usuarios:lista')
    success_message = "Usuario removido com sucesso!"
    
    def test_func(self):
        return self.request.user.funcao == 'admin'
    
    def delete(self, request, *args, **kwargs):
        messages.success(self.request, self.success_message)
        return super().delete(request, *args, **kwargs)
    

class AtualizarPerfilView(LoginRequiredMixin, UpdateView):
    model = Usuario
    fields = ['first_name', 'last_name', 'email', 'telefone', 'especializacao']
    template_name = 'usuarios/detalhe.html'  # Será redirecionado, não precisa de template próprio
    
    # funcao para retornar a pagina anterior
    def get_success_url(self):
        return reverse_lazy('usuarios:detalhe', kwargs={'pk': self.object.pk})
    
    def get_object(self, queryset=None):
        return self.request.user
    
    def form_valid(self, form):
        #messages.success(self.request, 'Perfil atualizado com sucesso!')
        return super().form_valid(form)
    
    def form_invalid(self, form):
        messages.error(self.request, 'Erro ao atualizar perfil. Verifique os dados informados.')
        return redirect(reverse_lazy('usuarios:detalhe', kwargs={'pk': self.object.pk}))


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
        
        return redirect(reverse_lazy('usuarios:detalhe', kwargs={'pk': request.user.pk}))
    
class AlterarSenhaView(LoginRequiredMixin, View):
    def post(self, request, *args, **kwargs):
        senha_atual = request.POST.get('senha_atual')
        nova_senha = request.POST.get('nova_senha')
        confirmar_senha = request.POST.get('confirmar_senha')
        
        if not request.user.check_password(senha_atual):
            messages.error(request, 'Senha atual incorreta.')
            return redirect(reverse_lazy('usuarios:detalhe', kwargs={'pk': request.user.pk}))
            
        if nova_senha != confirmar_senha:
            messages.error(request, 'As novas senhas não coincidem.')
            return redirect(reverse_lazy('usuarios:detalhe', kwargs={'pk': request.user.pk}))
            
        if len(nova_senha) < 8:
            messages.error(request, 'A nova senha deve ter pelo menos 8 caracteres.')
            return redirect(reverse_lazy('usuarios:detalhe', kwargs={'pk': request.user.pk}))
            
        # Verificar se a senha contém letras e números
        if not any(c.isalpha() for c in nova_senha) or not any(c.isdigit() for c in nova_senha):
            messages.error(request, 'A senha deve conter letras e números.')
            return redirect(reverse_lazy('usuarios:detalhe', kwargs={'pk': request.user.pk}))
        
        try:
            request.user.set_password(nova_senha)
            request.user.save()
            # Atualiza a sessão para manter o usuário logado
            update_session_auth_hash(request, request.user)
            messages.success(request, 'Senha alterada com sucesso!')
        except Exception as e:
            messages.error(request, 'Erro ao alterar a senha. Tente novamente.')
            
        return redirect(reverse_lazy('usuarios:detalhe', kwargs={'pk': request.user.pk}))
  
"""  
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
"""