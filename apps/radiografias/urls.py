from django.urls import path
from . import views

app_name = 'radiografias'

urlpatterns = [
    path('lista/', views.lista_view, name='lista'),
    path('detalhe/', views.detalhe_view, name='detalhe')
]