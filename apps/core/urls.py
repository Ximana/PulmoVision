#apps/core/urls-py
from django.urls import path
from . import views

urlpatterns = [
    path('', views.HomeView.as_view(), name='home'),
    path('sobre/', views.sobre_view, name='sobre'),
]
