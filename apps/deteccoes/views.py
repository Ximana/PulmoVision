#apps/deteccoes/views.py
from django.views.generic import CreateView, ListView, DetailView, UpdateView, DeleteView
from django.urls import reverse_lazy
from django.contrib.messages.views import SuccessMessageMixin
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render, redirect, get_object_or_404
from apps.pacientes.models import Paciente
from apps.radiografias.models import Radiografia
from .models import Deteccao, AvaliacaoDeteccao
from django.contrib import messages
from django.db.models import Q
from .forms import DeteccaoCadastroForm, AvaliacaoDeteccaoCadastroForm


class DeteccaoListView(LoginRequiredMixin, ListView):
    model = Deteccao
    template_name = 'deteccoes/lista.html'
    context_object_name = 'deteccoes'
    paginate_by = 10
    
    def get_queryset(self):
        queryset = super().get_queryset()
        search_query = self.request.GET.get('search', '')
        
        if search_query:
            queryset = queryset.filter(
                Q(radiografia__paciente__nome__icontains=search_query) |
                Q(radiografia__paciente__sobrenome__icontains=search_query) |
                Q(radiografia__paciente__numero_bi__icontains=search_query) |
                Q(doenca__icontains=search_query) |
                Q(estado__icontains=search_query)
            )
        
        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['radiografias'] = Radiografia.objects.all()
        context['search_query'] = self.request.GET.get('search', '')
        context['form'] = DeteccaoCadastroForm()  # Adicione esta linha
        return context

    def post(self, request, *args, **kwargs):
        form = DeteccaoCadastroForm(request.POST)
        if form.is_valid():
            deteccao = form.save(commit=False)
            deteccao.usuario = request.user
            deteccao.save()
            messages.success(request, 'Detecção registrada com sucesso!')
            return redirect('deteccoes:lista')
        else:
            context = self.get_context_data()
            context['form'] = form
            return render(request, self.template_name, context)

class DeteccaoDetailView(LoginRequiredMixin, DetailView):
    model = Deteccao
    template_name = 'deteccoes/detalhe.html'
    context_object_name = 'deteccao'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = AvaliacaoDeteccaoCadastroForm()
        # Verificar se o usuário já avaliou esta detecção
        context['ja_avaliou'] = AvaliacaoDeteccao.objects.filter(
            deteccao=self.object,
            usuario=self.request.user
        ).exists()
        return context
    
    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        form = AvaliacaoDeteccaoCadastroForm(request.POST)
        
        if form.is_valid():
            try:
                # Verifica se já existe uma avaliação deste usuário para esta detecção
                avaliacao_existente = AvaliacaoDeteccao.objects.filter(
                    deteccao=self.object,
                    usuario=request.user
                ).first()
                
                if avaliacao_existente:
                    # Atualiza a avaliação existente
                    for field in form.cleaned_data:
                        setattr(avaliacao_existente, field, form.cleaned_data[field])
                    avaliacao_existente.save()
                    messages.success(request, 'Avaliação atualizada com sucesso!')
                else:
                    # Cria nova avaliação
                    avaliacao = form.save(commit=False)
                    avaliacao.usuario = request.user
                    avaliacao.deteccao = self.object
                    avaliacao.save()
                    messages.success(request, 'Avaliação registrada com sucesso!')
                
                return redirect('deteccoes:detalhe', pk=self.object.pk)
            
            except Exception as e:
                messages.error(request, f'Erro ao salvar avaliação: {str(e)}')
        else:
            messages.error(request, 'Por favor, corrija os erros no formulário.')
        
        # Se houver erros, renderiza a página novamente com o formulário
        context = self.get_context_data(form=form)
        return render(request, self.template_name, context)
    
class AvaliacoesDeteccaoListView(LoginRequiredMixin, ListView):
    model = AvaliacaoDeteccao
    template_name = 'deteccoes/listar_avaliacoes_deteccao.html'
    context_object_name = 'avaliacoes'
    paginate_by = 10
    
    def get_queryset(self):
        self.deteccao = get_object_or_404(Deteccao, pk=self.kwargs['pk'])
        return AvaliacaoDeteccao.objects.filter(deteccao=self.deteccao).order_by('-criado_em')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['deteccao'] = self.deteccao
        context['form'] = AvaliacaoDeteccaoCadastroForm()
        return context