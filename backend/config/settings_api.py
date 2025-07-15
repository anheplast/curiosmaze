# backend/config/settings_api.py
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
import json
import os

# Configuraciones por defecto
DEFAULT_SETTINGS = {
    'language_selector_enabled': False,
    'default_language_id': 71,  # Python
}

@csrf_exempt
@require_http_methods(["GET", "POST"])
def platform_settings(request):
    """Endpoint para manejar configuraciones de la plataforma"""
    
    if request.method == "GET":
        # Retornar configuraciones actuales
        settings = get_platform_settings()
        return JsonResponse({
            'success': True,
            'settings': settings
        })
    
    elif request.method == "POST":
        try:
            data = json.loads(request.body)
            setting_key = data.get('key')
            setting_value = data.get('value')
            
            if not setting_key:
                return JsonResponse({
                    'success': False,
                    'error': 'Clave de configuración requerida'
                }, status=400)
            
            # Guardar configuración
            success = save_platform_setting(setting_key, setting_value)
            
            if success:
                return JsonResponse({
                    'success': True,
                    'message': f'Configuración {setting_key} actualizada'
                })
            else:
                return JsonResponse({
                    'success': False,
                    'error': 'Error al guardar configuración'
                }, status=500)
                
        except json.JSONDecodeError:
            return JsonResponse({
                'success': False,
                'error': 'JSON inválido'
            }, status=400)
        except Exception as e:
            return JsonResponse({
                'success': False,
                'error': str(e)
            }, status=500)

def get_platform_settings():
    """Obtener todas las configuraciones de la plataforma"""
    settings = DEFAULT_SETTINGS.copy()
    
    # Leer desde variables de entorno o archivo
    settings['language_selector_enabled'] = os.environ.get(
        'LANGUAGE_SELECTOR_ENABLED', 'false'
    ).lower() == 'true'
    
    settings['default_language_id'] = int(os.environ.get(
        'DEFAULT_LANGUAGE_ID', '71'
    ))
    
    return settings

def save_platform_setting(key, value):
    """Guardar una configuración específica"""
    try:
        # Aquí podrías usar una base de datos, pero por simplicidad usamos archivos
        import json
        from pathlib import Path
        
        config_file = Path('platform_settings.json')
        
        # Leer configuraciones existentes
        if config_file.exists():
            with open(config_file, 'r') as f:
                settings = json.load(f)
        else:
            settings = DEFAULT_SETTINGS.copy()
        
        # Actualizar configuración
        settings[key] = value
        
        # Guardar
        with open(config_file, 'w') as f:
            json.dump(settings, f, indent=2)
        
        return True
    except Exception as e:
        print(f"Error guardando configuración: {e}")
        return False