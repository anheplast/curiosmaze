# backend/config/urls.py - CORREGIDO para Django Debug Toolbar
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic import RedirectView
from .settings_api import platform_settings

# URLs principales
urlpatterns = [
    path('admin/', admin.site.urls),
    
    # URLs de la API
    path('api/users/', include('users.urls')),  # App de usuarios existente
    path('api/', include('evaluations.urls')),  # App de evaluaciones
    
    # Para cualquier otra ruta, simplemente devolver una respuesta que indique
    # que es una API (no necesitamos servir el frontend desde Django)
    path('', RedirectView.as_view(url='/api/', permanent=False)),
    
    # Endpoint de configuraciones
    path('api/platform-settings/', platform_settings, name='platform-settings'),
    
    # Gestión de estudiantes
    path('api/manage-students/', include('manage_students.urls')),
]

# =================================================================
# CONFIGURACIÓN PARA DESARROLLO (Debug Toolbar)
# =================================================================
if settings.DEBUG:
    # Importar debug toolbar solo si está disponible
    try:
        import debug_toolbar
        # Agregar las URLs del debug toolbar
        urlpatterns = [
            path('__debug__/', include(debug_toolbar.urls)),
        ] + urlpatterns
        print("Debug Toolbar configurado correctamente")
    except ImportError:
        print("Debug Toolbar no disponible")
    
    # Servir archivos estáticos y media durante el desarrollo
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

# En producción, los archivos estáticos son servidos por Nginx
else:
    print("📦 Modo producción - archivos estáticos servidos por servidor web")