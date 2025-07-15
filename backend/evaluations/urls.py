# backend/evaluations/urls.py
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views
from .views import admin_check_evaluacion, finalizar_evaluacion, resultados_evaluacion, get_participantes_evaluacion, obtener_historial_evaluaciones, obtener_evaluacion_historial, get_evaluacion_resultados_completos

# Configurar routers para ViewSets
router = DefaultRouter()
router.register(r'cursos', views.CursoViewSet, basename='curso')
router.register(r'ejercicios', views.EjercicioViewSet, basename='ejercicio')
router.register(r'evaluaciones', views.EvaluacionViewSet, basename='evaluacion')
router.register(r'usuarios', views.UsuarioViewSet, basename='usuario')

urlpatterns = [
    # Incluir las URLs generadas por el router
    path('', include(router.urls)),
    
    # Endpoint para obtener detalles específicos de evaluación
    path('evaluaciones/<int:pk>/detalles/', views.get_detalles_evaluacion, name='get_detalles_evaluacion'),
    
    # Endpoints para prueba y envío de código
    path('test-codigo/', views.test_codigo, name='test_codigo'),
    path('submit-codigo/', views.submit_codigo, name='submit_codigo'),
    path('evaluaciones/<int:pk>/admin-check/', admin_check_evaluacion, name='admin_check_evaluacion'),
    
    # Endpoint para obtener el estado de la evaluación
    path('evaluaciones/<int:pk>/finalizar/', finalizar_evaluacion, name='finalizar_evaluacion'),
    path('evaluaciones/<int:pk>/resultados/', resultados_evaluacion, name='resultados_evaluacion'),
    
    path('evaluaciones/<int:pk>/participantes/', get_participantes_evaluacion, name='participantes-evaluacion'),
    
    path('evaluaciones/<int:pk>/ajustar-puntaje/', views.ajustar_puntaje, name='ajustar-puntaje'),
    path('evaluaciones/<int:pk>/expulsar-estudiante/', views.expulsar_estudiante, name='expulsar-estudiante'),
    
    # Nueva ruta para procesamiento en lote
    path('submit-batch/', views.submit_batch, name='submit_batch'),
    
    # Nueva ruta para obtener el historial de evaluaciones
    path('historial-evaluaciones/', obtener_historial_evaluaciones, name='historial-evaluaciones'),
    path('historial/<int:historial_id>/', obtener_evaluacion_historial, name='evaluacion-historial'),
    
    # NUEVA: Ruta para eliminar del historial
    path('historial/<int:historial_id>/eliminar/', views.eliminar_evaluacion_historial, name='eliminar-evaluacion-historial'),
    
    path('debug/historial/<int:evaluation_id>/', views.debug_historial, name='debug-historial'),
    
    path('evaluaciones/<int:pk>/resultados-completos/', get_evaluacion_resultados_completos, name='resultados-completos'),
    
    # Configuraciones de plataforma
    path('platform-settings/', views.platform_settings_view, name='platform-settings'),
    path('language-selector-config/', views.get_language_selector_config, name='language-selector-config'),
]