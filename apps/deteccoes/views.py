from django.views.generic import CreateView, ListView, DetailView, UpdateView, DeleteView
from django.urls import reverse_lazy
from django.contrib.messages.views import SuccessMessageMixin
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render, redirect
from apps.pacientes.models import Paciente
from apps.radiografias.models import Radiografia
#from .models import Deteccao
from django.contrib import messages
from django.db.models import Q




class DeteccaoListView(ListView):
    #model = Paciente
    template_name = 'deteccoes/lista.html'
    #context_object_name = 'pacientes'
    #paginate_by = 10
    
   
    
    