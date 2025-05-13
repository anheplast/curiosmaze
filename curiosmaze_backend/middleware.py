# curiosmaze_backend/middleware.py
import logging
import json
import traceback
from django.utils.deprecation import MiddlewareMixin
from rest_framework.exceptions import PermissionDenied, NotAuthenticated

from django.core.cache import cache
from django.http import HttpResponse

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
            if request.user.is_authenticated:
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
    def __init__(self, get_response):
        self.get_response = get_response
    
    def __call__(self, request):
        if request.path.startswith('/api/submit-codigo/') or request.path.startswith('/api/submit-batch/'):
            user_id = request.user.id if request.user.is_authenticated else 'anonymous'
            key = f"judge_rate_limit_{user_id}"
            
            # Modificado: máximo 5 solicitudes por 2 minutos (antes era 10 por minuto)
            if cache.get(key, 0) >= 5:
                return HttpResponse("Demasiadas solicitudes. Por favor, espere un momento antes de enviar más código.", status=429)
            
            cache.incr(key, 1)
            if cache.ttl(key) < 0:
                cache.expire(key, 120)  # Aumentado a 120 segundos (2 minutos)
        
        return self.get_response(request)