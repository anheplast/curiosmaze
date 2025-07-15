# users/apps.py

from django.apps import AppConfig


class UsersConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'users'
    verbose_name = 'Gestión de Usuarios'


class UsersConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'users'
    
    def ready(self):
        # Crear configuración institucional por defecto al iniciar
        try:
            from .models import InstitutionSettings
            InstitutionSettings.get_instance()
        except Exception:
            # Ignorar errores durante migraciones
            pass