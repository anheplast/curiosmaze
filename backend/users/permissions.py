# backend/users/permissions.py

from rest_framework import permissions
from .models import UserProfile

class IsAdmin(permissions.BasePermission):
    """
    Permiso para usuarios con rol de administrador.
    """
    message = "Se requiere rol de administrador."
    
    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False
        
        try:
            profile = UserProfile.objects.get(user=request.user)
            return profile.rol == 'admin'
        except UserProfile.DoesNotExist:
            return request.user.is_superuser

class IsDocente(permissions.BasePermission):
    """
    Permiso para usuarios con rol de docente.
    """
    message = "Se requiere rol de docente."
    
    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False
        
        try:
            profile = UserProfile.objects.get(user=request.user)
            return profile.rol == 'docente'
        except UserProfile.DoesNotExist:
            return False

class IsEstudiante(permissions.BasePermission):
    """
    Permiso para usuarios con rol de estudiante.
    """
    message = "Se requiere rol de estudiante."
    
    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False
        
        try:
            profile = UserProfile.objects.get(user=request.user)
            return profile.rol == 'estudiante'
        except UserProfile.DoesNotExist:
            return False



class IsOwnerOrDocenteOrAdmin(permissions.BasePermission):
    """
    Permiso para el propietario de un objeto, docentes o administradores.
    """
    message = "Solo el propietario, docentes o administradores pueden acceder a este recurso."
    
    def has_object_permission(self, request, view, obj):
        if not request.user.is_authenticated:
            return False
        
        # Verificar si el usuario es el propietario
        if hasattr(obj, 'creador') and obj.creador == request.user:
            return True
        
        # Verificar si es docente o admin
        try:
            profile = UserProfile.objects.get(user=request.user)
            return profile.rol in ['docente', 'admin']
        except UserProfile.DoesNotExist:
            return request.user.is_superuser

class HasEvaluationAccess(permissions.BasePermission):
    """
    Permiso para estudiantes que tienen acceso a una evaluación específica.
    """
    message = "No tiene acceso a esta evaluación."
    
    def has_permission(self, request, view):
        # Si no es una acción de detalle, no aplica
        if view.action not in ['retrieve', 'detalles']:
            return False
        
        # Si el usuario está autenticado, verificar su rol
        if request.user.is_authenticated:
            try:
                profile = UserProfile.objects.get(user=request.user)
                # Docentes y admin siempre tienen acceso
                if profile.rol in ['docente', 'admin']:
                    return True
                
                # Estudiantes necesitan estar registrados en la evaluación
                if profile.rol == 'estudiante':
                    from evaluations.models import EstudianteEvaluacion
                    return EstudianteEvaluacion.objects.filter(
                        estudiante=request.user,
                        evaluacion_id=view.kwargs.get('pk')
                    ).exists()
                
                return False
            except UserProfile.DoesNotExist:
                return request.user.is_superuser
        
        # Si no está autenticado, no tiene acceso
        return False

class AllowValidateAccessCode(permissions.BasePermission):
    """
    Permiso especial que permite a cualquier usuario (autenticado o no)
    validar un código de acceso a una evaluación.
    """
    def has_permission(self, request, view):
        # Solo permitir POST para validar códigos
        if request.method != 'POST':
            return False
        
        # Solo permitir acceso a la acción "validar_codigo"
        if getattr(view, 'action', None) != 'validar_codigo':
            return False
        
        return True