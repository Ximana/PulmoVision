# apps/detecoes/urls.py
from django.urls import path
from . import views

app_name = 'modelos'

urlpatterns = [
    path('lista/', views.ModeloListView.as_view(), name='lista'),
    path('<int:pk>/', views.ModeloDetailView.as_view(), name='detalhe'),
    path('<int:pk>/editar/', views.ModeloUpdateView.as_view(), name='editar'),
    path('<int:pk>/remover/', views.ModeloDeleteView.as_view(), name='remover'),
    path('<int:pk>/ativar/', views.ativar_modelo, name='ativar'),
    path('<int:pk>/desativar/', views.desativar_modelo, name='desativar'),
]