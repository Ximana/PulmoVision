# apps/core/views.py
from django.views.generic import ListView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Count, Avg
from apps.pacientes.models import Paciente
from apps.radiografias.models import Radiografia
from apps.deteccoes.models import Deteccao, AvaliacaoDeteccao
from django.shortcuts import render

def sobre_view(request):
    return render(request, 'core/sobre.html')

class HomeView(LoginRequiredMixin, ListView):
    template_name = 'core/home.html'
    model = Deteccao
    context_object_name = 'deteccoes_recentes'

    def get_queryset(self):
        # Retorna as últimas 5 detecções
        return Deteccao.objects.select_related('radiografia__paciente').order_by('-criado_em')[:10]

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Estatísticas gerais
        context['total_pacientes'] = Paciente.objects.count()
        context['total_deteccoes'] = Deteccao.objects.count()
        context['total_radiografias'] = Radiografia.objects.count()
        
        # Calcula a taxa de precisão média baseada nas avaliações
        avaliacoes = AvaliacaoDeteccao.objects.all()
        total_avaliacoes = avaliacoes.count()
        
        if total_avaliacoes > 0:
            # Considera "Correto" como 100% e "Parcialmente Correto" como 50%
            corretas = avaliacoes.filter(avaliacao='Correto').count()
            parcialmente = avaliacoes.filter(avaliacao='Parcialmente Correto').count()
            taxa_precisao = ((corretas * 100) + (parcialmente * 50)) / total_avaliacoes
            context['taxa_precisao'] = round(taxa_precisao, 1)
        else:
            context['taxa_precisao'] = 0
        
        # Estatísticas adicionais para o dashboard
        context['deteccoes_por_doenca'] = (
            Deteccao.objects.values('doenca')
            .annotate(total=Count('id'))
            .order_by('-total')
        )
        
        context['deteccoes_por_estado'] = (
            Deteccao.objects.values('estado')
            .annotate(total=Count('id'))
            .order_by('-total')
        )
        
        # Média de probabilidade por doença
        context['media_probabilidade'] = (
            Deteccao.objects.values('doenca')
            .annotate(media=Avg('probabilidade'))
            .order_by('doenca')
        )

        return context