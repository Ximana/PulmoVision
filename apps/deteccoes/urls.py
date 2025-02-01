from django.urls import path
from . import views

app_name = 'deteccoes'

urlpatterns = [
    path('lista/', views.lista_view, name='lista'),
]