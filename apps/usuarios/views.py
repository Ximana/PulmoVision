from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from django.contrib import messages
from .models import Usuario
from .forms import UsuarioRegistroForm, UsuarioEdicaoForm

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
    template_name = 'usuarios/usuario_lista.html'
    context_object_name = 'usuarios'

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