# backend/manage_students/admin.py
from django.contrib import admin
from .models import Estudiante, DocenteEstudiante, Asistencia, Evaluacion, Calificacion

@admin.register(Estudiante)
class EstudianteAdmin(admin.ModelAdmin):
    list_display = ('get_nombre', 'get_identificacion', 'fecha_registro')
    search_fields = ('user__profile__nombres', 'user__profile__apellidos', 'user__profile__identificacion')
    list_filter = ('user__profile__curso', 'user__profile__paralelo')
    
    def get_nombre(self, obj):
        return f"{obj.user.profile.nombres} {obj.user.profile.apellidos}"
    get_nombre.short_description = 'Nombre completo'
    
    def get_identificacion(self, obj):
        return obj.user.profile.identificacion
    get_identificacion.short_description = 'Identificación'


@admin.register(DocenteEstudiante)
class DocenteEstudianteAdmin(admin.ModelAdmin):
    list_display = ('get_docente', 'get_estudiante', 'fecha_asignacion')
    search_fields = ('docente__profile__nombres', 'docente__profile__apellidos', 
                    'estudiante__user__profile__nombres', 'estudiante__user__profile__apellidos')
    list_filter = ('fecha_asignacion',)
    
    def get_docente(self, obj):
        return f"{obj.docente.profile.nombres} {obj.docente.profile.apellidos}"
    get_docente.short_description = 'Docente'
    
    def get_estudiante(self, obj):
        return f"{obj.estudiante.user.profile.nombres} {obj.estudiante.user.profile.apellidos}"
    get_estudiante.short_description = 'Estudiante'


@admin.register(Asistencia)
class AsistenciaAdmin(admin.ModelAdmin):
    list_display = ('get_estudiante', 'fecha', 'presente', 'get_docente')
    list_filter = ('fecha', 'presente', 'docente__profile__nombres')
    search_fields = ('estudiante__user__profile__nombres', 'estudiante__user__profile__apellidos', 
                    'docente__profile__nombres', 'docente__profile__apellidos')
    
    def get_estudiante(self, obj):
        return f"{obj.estudiante.user.profile.nombres} {obj.estudiante.user.profile.apellidos}"
    get_estudiante.short_description = 'Estudiante'
    
    def get_docente(self, obj):
        return f"{obj.docente.profile.nombres} {obj.docente.profile.apellidos}"
    get_docente.short_description = 'Docente'


@admin.register(Evaluacion)
class EvaluacionAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'fecha', 'curso', 'paralelo', 'get_docente')
    list_filter = ('fecha', 'curso', 'paralelo')
    search_fields = ('nombre', 'descripcion', 'docente__profile__nombres', 'docente__profile__apellidos')
    
    def get_docente(self, obj):
        return f"{obj.docente.profile.nombres} {obj.docente.profile.apellidos}"
    get_docente.short_description = 'Docente'


@admin.register(Calificacion)
class CalificacionAdmin(admin.ModelAdmin):
    list_display = ('get_estudiante', 'get_evaluacion', 'valor')
    list_filter = ('evaluacion__nombre', 'evaluacion__fecha')
    search_fields = ('estudiante__user__profile__nombres', 'estudiante__user__profile__apellidos', 
                    'evaluacion__nombre')
    
    def get_estudiante(self, obj):
        return f"{obj.estudiante.user.profile.nombres} {obj.estudiante.user.profile.apellidos}"
    get_estudiante.short_description = 'Estudiante'
    
    def get_evaluacion(self, obj):
        return f"{obj.evaluacion.nombre} ({obj.evaluacion.fecha})"
    get_evaluacion.short_description = 'Evaluación'