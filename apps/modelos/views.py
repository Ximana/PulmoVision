# app/detecoes/views.py
from django.views.generic import CreateView, ListView, DetailView, UpdateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render, get_object_or_404
from django.contrib import messages
from django.urls import reverse_lazy
from django.contrib.messages.views import SuccessMessageMixin
from django.db.models import Q
from django.http import JsonResponse
from .models import Modelo
from .forms import ModeloCadastroForm, ModeloEdicaoForm

class ModeloListView(LoginRequiredMixin, ListView):
    model = Modelo
    template_name = 'modelos/lista.html'
    context_object_name = 'modelos'
    paginate_by = 10
    
    def get_queryset(self):
        queryset = super().get_queryset()
        search_query = self.request.GET.get('search', '')
        apenas_ativos = self.request.GET.get('ativo', '')
        
        if search_query:
            queryset = queryset.filter(
                Q(nome__icontains=search_query) |
                Q(versao__icontains=search_query) |
                Q(descricao__icontains=search_query)
            )
        
        if apenas_ativos:
            queryset = queryset.filter(ativo=True)
            
        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = ModeloCadastroForm()
        context['search_query'] = self.request.GET.get('search', '')
        context['apenas_ativos'] = self.request.GET.get('ativo', '')
        
        # Estatísticas dos modelos
        total_modelos = Modelo.objects.count()
        modelos_ativos = Modelo.objects.filter(ativo=True).count()
        context['stats'] = {
            'total': total_modelos,
            'ativos': modelos_ativos,
            'inativos': total_modelos - modelos_ativos
        }
        
        return context
    
    def post(self, request, *args, **kwargs):
        form = ModeloCadastroForm(request.POST)
        if form.is_valid():
            modelo = form.save(commit=False)
            modelo.usuario = request.user
            modelo.save()
            messages.success(request, 'Modelo cadastrado com sucesso!')
            return redirect(modelo.get_absolute_url())
        
        self.object_list = self.get_queryset()
        context = self.get_context_data(form=form)
        return self.render_to_response(context)

class ModeloDetailView(LoginRequiredMixin, DetailView):
    model = Modelo
    template_name = 'modelos/detalhe.html'
    context_object_name = 'modelo'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Adiciona o formulário no contexto com a instância atual
        context['form'] = ModeloEdicaoForm(instance=self.object)
        return context

class ModeloUpdateView(LoginRequiredMixin, SuccessMessageMixin, UpdateView):
    model = Modelo
    form_class = ModeloEdicaoForm
    template_name = 'modelos/detalhe.html'
    success_message = "Os dados do modelo foram atualizados!"
    
    def get_success_url(self):
        return reverse_lazy('detecoes:detalhe', kwargs={'pk': self.object.pk})
    
    def form_invalid(self, form):
        # Para debug - imprimir os erros no console
        # print("Erros do formulário:", form.errors)
        messages.error(self.request, "Erro ao atualizar os dados do modelo. Verifique os campos.")
        return render(self.request, self.template_name, {
            'modelo': self.get_object(),
            'form': form
        })
        
    def form_valid(self, form):
        # Preservar o usuário atual
        form.instance.usuario = self.get_object().usuario
        response = super().form_valid(form)
        return response

class ModeloDeleteView(LoginRequiredMixin, SuccessMessageMixin, DeleteView):
    model = Modelo
    success_url = reverse_lazy('modelos:lista')
    success_message = "Modelo removido com sucesso!"
    
    def delete(self, request, *args, **kwargs):
        messages.success(self.request, self.success_message)
        return super().delete(request, *args, **kwargs)

@login_required
def ativar_modelo(request, pk):
    """View para ativar um modelo"""
    modelo = get_object_or_404(Modelo, pk=pk)
    modelo.ativo = True
    modelo.save()
    messages.success(request, f'Modelo "{modelo.nome}" v{modelo.versao} foi ativado!')
    return redirect('modelos:detalhe', pk=pk)

@login_required
def desativar_modelo(request, pk):
    """View para desativar um modelo"""
    modelo = get_object_or_404(Modelo, pk=pk)
    modelo.ativo = False
    modelo.save()
    messages.warning(request, f'Modelo "{modelo.nome}" v{modelo.versao} foi desativado!')
    return redirect('modelos:detalhe', pk=pk)