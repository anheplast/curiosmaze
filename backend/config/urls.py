# config/urls.py
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic import RedirectView
from .settings_api import platform_settings


urlpatterns = [
    path('admin/', admin.site.urls),
    
    # URLs de la API
    path('api/users/', include('users.urls')),  # App de usuarios existente
    path('api/', include('evaluations.urls')),  # Cambiado a 'evaluations'
    
    # Para cualquier otra ruta, simplemente devolver una respuesta que indique
    # que es una API (no necesitamos servir el frontend desde Django)
    path('', RedirectView.as_view(url='/api/', permanent=False)),
    
    
    # Endpoint de configuraciones
    path('api/platform-settings/', platform_settings, name='platform-settings'),
    
    # Gestion de estudiantes
    path('api/manage-students/', include('manage_students.urls')),
    # ...
]

# Servir archivos estáticos y media durante el desarrollo
if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)