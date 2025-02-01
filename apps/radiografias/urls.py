from django.urls import path
from . import views

app_name = 'radiografias'

urlpatterns = [
    path('lista/', views.RadiografiaListView.as_view(), name='lista'),
    path('<int:pk>/', views.RadiografiaDetailView.as_view(), name='detalhe'),
    #path('<int:pk>/editar/', views.RadiografiasUpdateView.as_view(), name='editar'),
    path('<int:pk>/remover/', views.RadiografiaDeleteView.as_view(), name='remover'),
]