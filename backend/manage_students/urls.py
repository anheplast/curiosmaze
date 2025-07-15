# backend/manage_students/urls.py
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'estudiantes-asignados', views.EstudianteViewSet, basename='estudiante-asignado')

urlpatterns = [
    path('', include(router.urls)),
    
    # Endpoints para estudiantes
    path('estudiantes/', views.lista_estudiantes, name='lista-estudiantes'),
    
    # Endpoints para asistencias
    path('asistencias/', views.lista_asistencias, name='lista-asistencias'),
    path('asistencias/registrar/', views.registrar_asistencia, name='registrar-asistencia'),
    
    # Endpoints para calificaciones
    path('calificaciones/', views.lista_calificaciones, name='lista-calificaciones'),
    path('calificaciones/registrar/', views.registrar_calificaciones, name='registrar-calificaciones'),
    
    # Endpoints para reportes
    path('reportes/asistencia/', views.generar_reporte_asistencia, name='reporte-asistencia'),
    path('reportes/calificaciones/', views.generar_reporte_calificaciones, name='reporte-calificaciones'),
    path('reportes/estudiante/<int:estudiante_id>/', views.generar_reporte_estudiante, name='reporte-estudiante'),
]