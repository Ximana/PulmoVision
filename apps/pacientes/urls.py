#apps/pacinets/urls.py
from django.urls import path
from . import views

app_name = 'pacientes'

urlpatterns = [
    path('lista', views.PacienteListView.as_view(), name='lista'),
    path('<int:pk>/', views.PacienteDetailView.as_view(), name='detalhe'),
    #path('novo/', views.PacienteCreateView.as_view(), name='novo'),
    path('<int:pk>/editar/', views.PacienteUpdateView.as_view(), name='editar'),
    path('<int:pk>/remover/', views.PacienteDeleteView.as_view(), name='remover'),
]