from django.urls import path
from . import views

app_name = 'deteccoes'

urlpatterns = [
    
    path('lista', views.DeteccaoListView.as_view(), name='lista'),
    
    
]