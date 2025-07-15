# backend/middleware.py
import logging
import json
import traceback
from django.utils.deprecation import MiddlewareMixin
from rest_framework.exceptions import PermissionDenied, NotAuthenticated
from django.core.cache import cache
from django.http import HttpResponse
import time

logger = logging.getLogger('django')

class PermissionLoggingMiddleware(MiddlewareMixin):
    """
    Middleware para registrar información detallada sobre errores de permisos.
    Optimizado para reducir overhead de logging.
    """
    def process_exception(self, request, exception):
        if isinstance(exception, (PermissionDenied, NotAuthenticated)):
            # Intentar obtener información del usuario
            user_info = "Usuario anónimo"
            if hasattr(request, 'user') and request.user.is_authenticated:
                try:
                    profile = getattr(request.user, 'profile', None)
                    user_info = f"Usuario: {request.user.username}, Rol: {getattr(profile, 'rol', 'desconocido') if profile else 'Sin perfil'}"
                except:
                    user_info = f"Usuario: {request.user.username}, Sin perfil"
            
            # Registrar información sobre la solicitud sin procesar todo el body
            try:
                # Solo procesar body si es pequeño para evitar overhead
                body = {}
                if request.body and len(request.body) < 1024:  # Límite de 1KB
                    body = json.loads(request.body) if request.body else {}
            except:
                body = {}
            
            path = request.path
            method = request.method
            query = dict(request.GET)
            
            # Guardar el registro con menos detalle de stack trace
            logger.warning(
                f"Error de permisos: {exception}\n"
                f"Usuario: {user_info}\n"
                f"Ruta: {method} {path}\n"
                f"Query: {query}\n"
                f"Body: {body}"
            )
        
        return None
        
    def process_request(self, request):
        # Solo loguear rutas importantes y no estáticas
        if not request.path.startswith(('/static/', '/media/')):
            # Reducir detalle de log para rutas comunes
            if request.path.startswith('/api/'):
                logger.info(f"API: {request.method} {request.path}")
            
        return None
        
    def process_response(self, request, response):
        # Solo loguear errores 4xx y 5xx, excluyendo 404 comunes
        if hasattr(response, 'status_code') and response.status_code >= 400:
            if response.status_code == 404 and request.path.startswith(('/static/', '/media/')):
                # Ignorar 404 de archivos estáticos
                return response
                
            logger.warning(
                f"Respuesta con error: {response.status_code} para {request.method} {request.path}"
            )
            # Solo incluir contenido para errores de servidor (5xx)
            if hasattr(response, 'content') and response.status_code >= 500:
                try:
                    content = response.content.decode('utf-8')
                    logger.warning(f"Contenido de la respuesta: {content[:500]}")
                except:
                    pass
                    
        return response


class JudgeRateLimitMiddleware:
    """
    Middleware para limitar las solicitudes a Judge0.
    CORREGIDO: Compatible con LocMemCache y AuthenticationMiddleware.
    """
    def __init__(self, get_response):
        self.get_response = get_response
        self.rate_limit_cache = {}  # Cache local como respaldo
    
    def __call__(self, request):
        if request.path.startswith('/api/submit-codigo/') or request.path.startswith('/api/submit-batch/'):
            # CORREGIDO: Verificar que request.user existe
            if hasattr(request, 'user') and request.user.is_authenticated:
                user_id = request.user.id
            else:
                user_id = 'anonymous'
            
            key = f"judge_rate_limit_{user_id}"
            current_time = int(time.time())
            
            # CORREGIDO: Usar solo métodos compatibles con LocMemCache
            try:
                # Intentar usar cache de Django
                cache_data = cache.get(key, {'count': 0, 'window_start': current_time})
                
                # Verificar si necesitamos resetear la ventana (2 minutos = 120 segundos)
                if current_time - cache_data.get('window_start', 0) > 120:
                    cache_data = {'count': 0, 'window_start': current_time}
                
                # Verificar límite (5 solicitudes por 2 minutos)
                if cache_data['count'] >= 5:
                    return HttpResponse(
                        "Demasiadas solicitudes. Por favor, espere un momento antes de enviar más código.", 
                        status=429
                    )
                
                # Incrementar contador
                cache_data['count'] += 1
                
                # CORREGIDO: Guardar en cache con timeout de 120 segundos
                cache.set(key, cache_data, 120)
                
            except Exception as e:
                # Fallback a cache local si Django cache falla
                logger.warning(f"Error en cache de rate limiting: {e}")
                
                # Limpiar entradas antiguas del cache local
                if key in self.rate_limit_cache:
                    if current_time - self.rate_limit_cache[key]['window_start'] > 120:
                        del self.rate_limit_cache[key]
                
                # Verificar limite en cache local
                if key in self.rate_limit_cache:
                    if self.rate_limit_cache[key]['count'] >= 5:
                        return HttpResponse(
                            "Demasiadas solicitudes. Por favor, espere un momento antes de enviar más código.", 
                            status=429
                        )
                    self.rate_limit_cache[key]['count'] += 1
                else:
                    self.rate_limit_cache[key] = {'count': 1, 'window_start': current_time}
        
        return self.get_response(request)