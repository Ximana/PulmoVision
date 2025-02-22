#apps/deteccoes/forms.py
from django.urls import path
from . import views

app_name = 'deteccoes'


urlpatterns = [
    path('lista/', views.DeteccaoListView.as_view(), name='lista'),
    path('<int:pk>/', views.DeteccaoDetailView.as_view(), name='detalhe'),
    path('<int:pk>/avaliacoes/', views.AvaliacoesDeteccaoListView.as_view(), name='avaliacoes'),
    path('<int:pk>/pdf/', views.download_deteccao_pdf, name='pdf'),
]