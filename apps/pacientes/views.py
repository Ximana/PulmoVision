#apps/pacientes/views.py
from django.views.generic import CreateView, ListView, DetailView, UpdateView, DeleteView
from django.urls import reverse_lazy
from django.contrib.messages.views import SuccessMessageMixin
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render, redirect
from .models import Paciente
from .forms import PacienteRegistroForm
from django.contrib import messages
from django.db.models import Q
from apps.radiografias.models import Radiografia
from apps.deteccoes.models import Deteccao

class PacienteListView(ListView):
    model = Paciente
    template_name = 'pacientes/lista.html'
    context_object_name = 'pacientes'
    paginate_by = 10
    
    # Funcao para pesquisa de pacientes
    def get_queryset(self):
        queryset = super().get_queryset()
        search_query = self.request.GET.get('search', '')
        
        if search_query:
            queryset = queryset.filter(
                Q(nome__icontains=search_query) |
                Q(sobrenome__icontains=search_query) |
                Q(numero_bi__icontains=search_query) |
                Q(nome_da_mae__icontains=search_query)
            )
        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = PacienteRegistroForm()
        context['search_query'] = self.request.GET.get('search', '')
        return context
    
    def post(self, request, *args, **kwargs):
        form = PacienteRegistroForm(request.POST, request.FILES)
        if form.is_valid():
            paciente = form.save()
            #messages.success(request, 'Paciente cadastrado com sucesso!')
            return redirect(paciente.get_absolute_url())
        
        # Se o formulário não for válido, retorna à lista com os erros
        self.object_list = self.get_queryset()
        context = self.get_context_data(form=form)
        return self.render_to_response(context)

class PacienteDetailView(LoginRequiredMixin, DetailView):
    model = Paciente
    template_name = 'pacientes/detalhe.html'
    context_object_name = 'paciente'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Adiciona o formulário no contexto
        context['form'] = PacienteRegistroForm(instance=self.object)
        
        # Obtém todas as radiografias do paciente
        context['radiografias'] = Radiografia.objects.filter(paciente=self.object)
        # Obtém todas as detecções associadas às radiografias do paciente
        context['deteccoes'] = Deteccao.objects.filter(radiografia__paciente=self.object)
        
        return context

class PacienteCreateView(LoginRequiredMixin, SuccessMessageMixin, CreateView):
    model = Paciente
    form_class = PacienteRegistroForm
    template_name = 'pacientes/adicionarModal.html'
    success_url = reverse_lazy('pacientes:lista')
    success_message = "Paciente %(nome)s foi cadastrado com sucesso!"

class PacienteUpdateView(LoginRequiredMixin, SuccessMessageMixin, UpdateView):
    model = Paciente
    form_class = PacienteRegistroForm
    template_name = 'pacientes/detalhe.html'  # Apontamos para detalhe.html já que o modal está lá
    success_message = "Dados do paciente %(nome)s foram atualizados com sucesso!"
    
    def get_success_url(self):
        return reverse_lazy('pacientes:detalhe', kwargs={'pk': self.object.pk})
    
    def form_invalid(self, form):
        # Em caso de erro, retorna para a página de detalhes com o formulário e erros
        return render(self.request, self.template_name, {
            'paciente': self.get_object(),
            'form': form
        })

class PacienteDeleteView(LoginRequiredMixin, SuccessMessageMixin, DeleteView):
    model = Paciente
    success_url = reverse_lazy('pacientes:lista')
    success_message = "Paciente removido com sucesso!"
    
    def delete(self, request, *args, **kwargs):
        messages.success(self.request, self.success_message)
        return super().delete(request, *args, **kwargs)