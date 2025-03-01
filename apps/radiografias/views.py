# app/radiografias/views.py
from django.views.generic import CreateView, ListView, DetailView, UpdateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import redirect, render
from django.contrib import messages
from .models import Radiografia
from .forms import RadiografiaCadastroForm, RadiografiaEdicaoForm
from apps.pacientes.models import Paciente
from django.urls import reverse_lazy
from django.contrib.messages.views import SuccessMessageMixin
from django.db.models import Q

class RadiografiaListView(LoginRequiredMixin, ListView):
    model = Radiografia
    template_name = 'radiografias/lista.html'
    context_object_name = 'radiografias'
    paginate_by = 10
    
    def get_queryset(self):
        queryset = super().get_queryset()
        search_query = self.request.GET.get('search', '')
        
        if search_query:
            queryset = queryset.filter(
                Q(paciente__nome__icontains=search_query) |
                Q(paciente__sobrenome__icontains=search_query) |
                Q(paciente__numero_bi__icontains=search_query)
            )
        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = RadiografiaCadastroForm()
        context['pacientes'] = Paciente.objects.all()
        context['search_query'] = self.request.GET.get('search', '')
        return context
    
    def post(self, request, *args, **kwargs):
        form = RadiografiaCadastroForm(request.POST, request.FILES)
        if form.is_valid():
            radiografia = form.save(commit=False)
            radiografia.usuario = request.user
            radiografia.save()
            #messages.success(request, 'Radiografia cadastrada com sucesso!')
            return redirect(radiografia.get_absolute_url())
        
        self.object_list = self.get_queryset()
        context = self.get_context_data(form=form)
        return self.render_to_response(context)

class RadiografiaDetailView(LoginRequiredMixin, DetailView):
    model = Radiografia
    template_name = 'radiografias/detalhe.html'
    context_object_name = 'radiografia'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Adiciona o formulário no contexto com a instância atual
        context['form'] = RadiografiaCadastroForm(instance=self.object)
        return context

class RadiografiaUpdateView(LoginRequiredMixin, SuccessMessageMixin, UpdateView):
    model = Radiografia
    form_class = RadiografiaEdicaoForm
    template_name = 'radiografias/detalhe.html'
    success_message = "Os dados da radiografia foram atualizados!"
    
    def get_success_url(self):
        return reverse_lazy('radiografias:detalhe', kwargs={'pk': self.object.pk})
    
    def form_invalid(self, form):
        # Para debug - imprimir os erros no console
        #print("Erros do formulário:", form.errors)
        #messages.error(self.request, "Erro ao atualizar os dados da radiografia. Verifique os campos.")
        return render(self.request, self.template_name, {
            'radiografia': self.get_object(),
            'form': form
        })
        
    def form_valid(self, form):
        # Preservar o paciente atual
        form.instance.paciente = self.get_object().paciente
        response = super().form_valid(form)
        #messages.success(self.request, self.success_message)
        return response

class RadiografiaDeleteView(LoginRequiredMixin, SuccessMessageMixin, DeleteView):
    model = Radiografia
    success_url = reverse_lazy('radiografias:lista')
    success_message = "radiografia removida com sucesso!"
    
    def delete(self, request, *args, **kwargs):
        messages.success(self.request, self.success_message)
        return super().delete(request, *args, **kwargs)
    