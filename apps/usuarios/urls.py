#/app/usuarios/urls.py
from django.urls import path
from . import views

app_name = 'usuarios'

urlpatterns = [
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('lista/', views.UsuarioListView.as_view(), name='lista'),
    path('novo/', views.UsuarioCreateView.as_view(), name='novo'),
    path('editar/<int:pk>/', views.UsuarioUpdateView.as_view(), name='editar'),
    path('excluir/<int:pk>/', views.UsuarioDeleteView.as_view(), name='excluir'),
    path('perfil/', views.PerfilView.as_view(), name='perfil'),
    path('perfil/atualizar/', views.AtualizarPerfilView.as_view(), name='atualizar_perfil'),
    path('perfil/foto/atualizar/', views.AtualizarFotoView.as_view(), name='atualizar_foto'),
    path('perfil/senha/alterar/', views.AlterarSenhaView.as_view(), name='alterar_senha'),
]