from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('apps.core.urls')),
    path('usuarios/', include('apps.usuarios.urls')),
    path('pacientes/', include('apps.pacientes.urls')),
    path('deteccoes/', include('apps.deteccoes.urls')),
    path('radiografias/', include('apps.radiografias.urls')),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)