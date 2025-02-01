from django.shortcuts import render, redirect
from django.urls import path
from . import views


def lista_view(request):
    
    return render(request, 'radiografias/lista.html')

def detalhe_view(request):
    return render(request, 'radiografias/detalhe.html')