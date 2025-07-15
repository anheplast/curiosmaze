# backend/evaluations/views.py
import concurrent.futures
import json
import logging
import os
import subprocess
import tempfile
import threading
import time
from functools import lru_cache
from django.db import models

from django.conf import settings
from django.core.cache import cache
from django.db.models import Avg, Count, Q
from django.http import JsonResponse, Http404
from django.shortcuts import get_object_or_404
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt

from rest_framework import permissions, status, viewsets
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response

from users.models import User, UserProfile
from users.permissions import (
    AllowValidateAccessCode,
    HasEvaluationAccess,
    IsAdmin,
    IsDocente,
    IsEstudiante,
    IsOwnerOrDocenteOrAdmin,
)

from .models import (
    AjustePuntaje,
    Curso,
    Ejercicio,
    EstudianteEvaluacion,
    Evaluacion,
    HistorialEvaluacion,
    RespuestaEjercicio,
)
from .serializers import (
    AjustePuntajeSerializer,
    CursoSerializer,
    EjercicioSerializer,
    EstudianteEvaluacionSerializer,
    EvaluacionDetalladaSerializer,
    EvaluacionSerializer,
    RespuestaEjercicioSerializer,
    UsuarioSerializer,
)



logger = logging.getLogger('judge')



def get_codigo_con_funciones_auxiliares(ejercicio, codigo):
    """
    Asegura que el código tenga todas las funciones auxiliares necesarias para los tests.

    Args:
        ejercicio: Ejercicio que se está evaluando
        codigo (str): El código del estudiante

    Returns:
        str: Código con funciones auxiliares si son necesarias
    """
    if not codigo:
        return codigo

    # Verificar si el código necesita la función auxiliar de tests
    tests_avanzados = ejercicio.tests_avanzados
    if not tests_avanzados and hasattr(ejercicio, 'contenido') and ejercicio.contenido:
        contenido = ejercicio.contenido
        if isinstance(contenido, str):
            try:
                contenido = json.loads(contenido)
            except:
                contenido = {}
        
        if isinstance(contenido, dict):
            tests_avanzados = contenido.get('tests_avanzados')

    # Si hay tests avanzados, añadir funciones auxiliares
    if tests_avanzados:
        # Verificar si la función ya está incluida
        if 'def ejecutar_tests_avanzados' not in codigo and 'def test(' not in codigo:
            # Definición de las funciones auxiliares
            auxiliar_function = '''# Función auxiliar para ejecutar pruebas avanzadas (añadida automáticamente)
def ejecutar_tests_avanzados(func, casos_prueba, mostrar_detalle=True):
    """
    Ejecuta una serie de pruebas para una función.

    Args:
        func: La función a probar
        casos_prueba: Lista de tuplas (entrada, salida_esperada)
        mostrar_detalle: Si es True, muestra el detalle de cada caso

    Returns:
        int: Número de pruebas pasadas
    """
    pruebas_pasadas = 0
    total_pruebas = len(casos_prueba)

    print(f"Ejecutando {total_pruebas} pruebas:")

    for i, (entrada, esperado) in enumerate(casos_prueba, 1):
        try:
            # Si la entrada es una tupla, desempaquetar
            if isinstance(entrada, tuple):
                resultado = func(*entrada)
            else:
                resultado = func(entrada)

            if resultado == esperado:
                pruebas_pasadas += 1
                if mostrar_detalle:
                    print(f"✓ CORRECTO - Prueba {i}: con entrada {entrada} se obtuvo {resultado}")
            else:
                if mostrar_detalle:
                    print(f"✗ INCORRECTO - Prueba {i}: con entrada {entrada}")
                    print(f"  Se esperaba: {esperado}")
                    print(f"  Se obtuvo: {resultado}")
        except Exception as e:
            if mostrar_detalle:
                print(f"✗ ERROR - Prueba {i}: con entrada {entrada}")
                print(f"  Error: {str(e)}")

    print(f"Resultado: {pruebas_pasadas}/{total_pruebas} pruebas pasadas")
    return pruebas_pasadas

# Función auxiliar para realizar pruebas básicas
def test(actual, expected, message=""):
    if actual == expected:
        print(f"✓ CORRECTO: {message}")
    else:
        print(f"✗ INCORRECTO: {message}")
        print(f"  Esperado: {expected}")
        print(f"  Obtenido: {actual}")
'''

            # Añadir la función al principio del código
            return auxiliar_function + '\n\n' + codigo

    # Si no se necesita, devolver el código sin cambios
    return codigo




def procesar_ejercicio(codigo, ejercicio_id, evaluacion_id, estudiante_evaluacion_id=None, language_id=71):
    """
    Procesa un ejercicio específico y evalúa su código
    
    Args:
        codigo (str): Código fuente a evaluar
        ejercicio_id (int): ID del ejercicio
        evaluacion_id (int): ID de la evaluación
        estudiante_evaluacion_id (int, optional): ID de la participación del estudiante
        
    Returns:
        dict: Resultado de la evaluación del ejercicio
    """
    try:
        # Obtener ejercicio y evaluación
        ejercicio = get_object_or_404(Ejercicio, id=ejercicio_id)
        evaluacion = get_object_or_404(Evaluacion, id=evaluacion_id)
        
        # Verificar de dónde viene el puntaje
        puntaje_maximo = ejercicio.puntaje or 10
        
        # AGREGAR LOGGING
        print(f"DEBUG - Ejercicio ID: {ejercicio_id}")
        print(f"DEBUG - Puntaje del ejercicio: {ejercicio.puntaje}")
        print(f"DEBUG - Puntaje máximo usado: {puntaje_maximo}")
        
        # Verificar si ya existe participación 
        if estudiante_evaluacion_id:
            try:
                estudiante_evaluacion = EstudianteEvaluacion.objects.get(id=estudiante_evaluacion_id)
            except EstudianteEvaluacion.DoesNotExist:
                # Si no se encuentra, crear un resultado con error
                return {
                    'ejercicio_id': ejercicio_id,
                    'success': False,
                    'message': 'No se encontró la participación del estudiante'
                }
        else:
            # Asumir que estamos en un método decorado con @api_view y tenemos acceso a request
            from rest_framework.request import Request
            request = Request._current.get()
            
            if not request:
                return {
                    'ejercicio_id': ejercicio_id,
                    'success': False,
                    'message': 'No se pudo determinar el usuario actual'
                }
                
            # Obtener o crear participación para el usuario actual
            try:
                estudiante_evaluacion, _ = EstudianteEvaluacion.objects.get_or_create(
                    estudiante=request.user,
                    evaluacion=evaluacion,
                    defaults={'estado': 'activo', 'fecha_inicio': timezone.now()}
                )
            except Exception as e:
                return {
                    'ejercicio_id': ejercicio_id,
                    'success': False,
                    'message': f'Error al crear participación: {str(e)}'
                }

        # Obtener contenido del ejercicio para extraer tests o ejemplos
        contenido = ejercicio.contenido or {}
        if isinstance(contenido, str):
            try:
                contenido = json.loads(contenido)
            except:
                contenido = {}
        
        # Verificar si hay código de prueba avanzado
        tests_avanzados = ejercicio.tests_avanzados
        if not tests_avanzados and contenido and isinstance(contenido, dict):
            tests_avanzados = contenido.get('tests_avanzados')
        
        # Añadir funciones auxiliares si son necesarias
        codigo = get_codigo_con_funciones_auxiliares(ejercicio, codigo)
        
        # Preparar los datos de resultado
        resultado = {
            'ejercicio_id': ejercicio_id,
            'success': True,
            'casos_correctos': 0,
            'total_casos': 0,
            'porcentaje': 0,
            'puntaje_obtenido': 0,
            'puntaje_maximo': ejercicio.puntaje or 10,
            'es_correcto': False
        }
        
        # Si hay tests avanzados, ejecutarlos
        if tests_avanzados:
            # Ejecutamos realmente los tests
            try:
                # Importar la nueva función de judge_utils
                from .judge_utils import ejecutar_tests_avanzados
                
                # Ejecutar tests avanzados
                test_result = ejecutar_tests_avanzados(codigo, tests_avanzados, language_id)
                
                # Analizar resultado
                if test_result['success']:
                    casos_correctos = test_result['casos_correctos']
                    total_casos = test_result['total_casos']
                    es_correcto = test_result['es_correcto']
                    
                    # Actualizar resultado
                    resultado['casos_correctos'] = casos_correctos
                    resultado['total_casos'] = total_casos
                    resultado['es_correcto'] = es_correcto
                    resultado['porcentaje'] = (casos_correctos / total_casos) * 100 if total_casos > 0 else 0
                    resultado['puntaje_obtenido'] = (casos_correctos / total_casos) * resultado['puntaje_maximo'] if total_casos > 0 else 0
                    
                    # Añadir salida y stderr para diagnóstico
                    resultado['output'] = test_result['output']
                    resultado['stderr'] = test_result['stderr']
                else:
                    resultado['success'] = False
                    resultado['message'] = 'Error en los tests avanzados'
                    resultado['stderr'] = test_result['stderr']
            except Exception as e:
                return {
                    'ejercicio_id': ejercicio_id,
                    'success': False,
                    'message': f'Error al ejecutar tests avanzados: {str(e)}'
                }
        
        # Si hay ejemplos, usarlos como casos de prueba
        elif 'ejemplos' in contenido and contenido['ejemplos']:
            # Intentar usar la nueva función de judge_utils
            try:
                from .judge_utils import verificar_ejemplos
                
                ejemplos = contenido['ejemplos']
                verification_result = verificar_ejemplos(codigo, ejemplos)
                
                if verification_result['success']:
                    casos_correctos = verification_result['casos_correctos']
                    total_casos = verification_result['total_casos']
                    es_correcto = verification_result['es_correcto']
                    
                    # Actualizar resultado
                    resultado['casos_correctos'] = casos_correctos
                    resultado['total_casos'] = total_casos
                    resultado['es_correcto'] = es_correcto
                    resultado['porcentaje'] = (casos_correctos / total_casos) * 100 if total_casos > 0 else 0
                    resultado['puntaje_obtenido'] = (casos_correctos / total_casos) * resultado['puntaje_maximo'] if total_casos > 0 else 0
                    resultado['output'] = verification_result['output']
                else:
                    resultado['success'] = False
                    resultado['message'] = 'Error al verificar ejemplos'
                    resultado['stderr'] = verification_result.get('stderr', '')
            except ImportError:
                # Si no existe judge_utils, usar el método original
                ejemplos = contenido['ejemplos']
                
                # Validar ejemplos para asegurar que tengan estructura correcta
                ejemplos_validos = []
                for ej in ejemplos:
                    if isinstance(ej, dict) and 'entrada' in ej and 'salida' in ej:
                        ejemplos_validos.append(ej)
                
                total_casos = len(ejemplos_validos)
                casos_correctos = 0
                output_total = []
                
                # Evaluar cada ejemplo
                for ejemplo in ejemplos_validos:
                    entrada = ejemplo.get('entrada', '')
                    salida_esperada = ejemplo.get('salida', '').strip()
                    
                    # Ejecutar realmente el código
                    try:
                        import tempfile
                        import subprocess
                        
                        # Crear archivo con el código
                        with tempfile.NamedTemporaryFile(suffix='.py', delete=False) as f:
                            f.write(codigo.encode('utf-8'))
                            temp_file = f.name
                        
                        # Crear archivo con la entrada
                        with tempfile.NamedTemporaryFile(suffix='.txt', delete=False) as f:
                            f.write(entrada.encode('utf-8'))
                            input_file = f.name
                        
                        # Ejecutar el código con la entrada
                        process = subprocess.run(
                            ['python', temp_file],
                            stdin=open(input_file, 'r'),
                            capture_output=True,
                            text=True,
                            timeout=5
                        )
                        
                        # Verificar si la salida coincide con la esperada
                        salida_obtenida = process.stdout.strip()
                        
                        # Registrar esta salida para diagnóstico
                        output_total.append({
                            'input': entrada,
                            'expected': salida_esperada,
                            'actual': salida_obtenida,
                            'correct': salida_obtenida == salida_esperada,
                            'stderr': process.stderr
                        })
                        
                        if salida_obtenida == salida_esperada:
                            casos_correctos += 1
                        
                        # Limpiar archivos temporales
                        import os
                        try:
                            os.unlink(temp_file)
                            os.unlink(input_file)
                        except:
                            pass
                            
                    except subprocess.TimeoutExpired:
                        # Este ejemplo falló por timeout
                        output_total.append({
                            'input': entrada,
                            'expected': salida_esperada,
                            'actual': "TIMEOUT",
                            'correct': False,
                            'stderr': "Tiempo de ejecución excedido"
                        })
                        continue
                    except Exception as e:
                        # Este ejemplo falló por algún error
                        import logging
                        logging.error(f"Error en ejemplo: {str(e)}")
                        output_total.append({
                            'input': entrada,
                            'expected': salida_esperada,
                            'actual': "ERROR",
                            'correct': False,
                            'stderr': str(e)
                        })
                        continue
                
                # Actualizar resultado
                resultado['casos_correctos'] = casos_correctos
                resultado['total_casos'] = total_casos
                resultado['es_correcto'] = casos_correctos == total_casos
                resultado['porcentaje'] = (casos_correctos / total_casos) * 100 if total_casos > 0 else 0
                resultado['puntaje_obtenido'] = (casos_correctos / total_casos) * resultado['puntaje_maximo'] if total_casos > 0 else 0
                resultado['output'] = output_total
        
        # Si no hay tests ni ejemplos, ejecutar una vez para verificar que compile
        else:
            try:
                from .judge_utils import ejecutar_codigo
                
                # Intentar ejecutar el código
                code_result = ejecutar_codigo(codigo)
                
                # Si no hay errores, consideramos que el ejercicio es correcto
                if code_result['success']:
                    resultado['casos_correctos'] = 1
                    resultado['total_casos'] = 1
                    resultado['es_correcto'] = True
                    resultado['porcentaje'] = 100
                    resultado['puntaje_obtenido'] = resultado['puntaje_maximo']
                else:
                    resultado['casos_correctos'] = 0
                    resultado['total_casos'] = 1
                    resultado['es_correcto'] = False
                    resultado['porcentaje'] = 0
                    resultado['puntaje_obtenido'] = 0
                
                # Añadir salida y stderr para diagnóstico
                resultado['output'] = code_result['stdout']
                resultado['stderr'] = code_result['stderr']
            except ImportError:
                # Si no existe judge_utils, usar el método original
                import tempfile
                import subprocess
                
                # Crear archivo con el código
                with tempfile.NamedTemporaryFile(suffix='.py', delete=False) as f:
                    f.write(codigo.encode('utf-8'))
                    temp_file = f.name
                
                # Intentar ejecutar el código
                process = subprocess.run(
                    ['python', temp_file],
                    capture_output=True,
                    text=True,
                    timeout=5
                )
                
                # Si no hay errores, consideramos que el ejercicio es correcto
                if process.returncode == 0:
                    resultado['casos_correctos'] = 1
                    resultado['total_casos'] = 1
                    resultado['es_correcto'] = True
                    resultado['porcentaje'] = 100
                    resultado['puntaje_obtenido'] = resultado['puntaje_maximo']
                else:
                    resultado['casos_correctos'] = 0
                    resultado['total_casos'] = 1
                    resultado['es_correcto'] = False
                    resultado['porcentaje'] = 0
                    resultado['puntaje_obtenido'] = 0
                
                # Añadir salida y stderr para diagnóstico
                resultado['output'] = process.stdout
                resultado['stderr'] = process.stderr
                
                # Limpiar archivo temporal
                import os
                try:
                    os.unlink(temp_file)
                except:
                    pass
        
        # Guardar respuesta en la base de datos - más robusto ante errores DB
        try:
            # Preparar objeto de respuesta para guardar
            respuesta_content = {
                'codigo': codigo,
                'resultados': resultado.get('output', [])
            }
            
            # Si hay stderr, añadirlo
            if 'stderr' in resultado and resultado['stderr']:
                respuesta_content['stderr'] = resultado['stderr']
            
            respuesta, created = RespuestaEjercicio.objects.update_or_create(
                estudiante_evaluacion=estudiante_evaluacion,
                ejercicio=ejercicio,
                defaults={
                    'respuesta': respuesta_content,
                    'es_correcta': resultado['es_correcto'],
                    'puntaje_obtenido': resultado['puntaje_obtenido'],
                    'fecha_respuesta': timezone.now(),
                    
                }
            )
        except Exception as db_error:
            # Reportar el error pero no fallar la ejecución completa
            import logging
            logging.error(f"Error al guardar respuesta en BD: {str(db_error)}")
            # Añadir información al resultado
            resultado['db_warning'] = "Respuesta evaluada pero no guardada en base de datos"
        
        return resultado
        
    except Exception as e:
        import logging
        logging.error(f"Error en procesar_ejercicio: {str(e)}")
        return {
            'ejercicio_id': ejercicio_id,
            'success': False,
            'message': f'Error: {str(e)}',
            'casos_correctos': 0,
            'total_casos': 1,  # Asegurar que este campo exista
            'porcentaje': 0,
            'puntaje_obtenido': 0,
            'puntaje_maximo': ejercicio.puntaje or 10,
            'es_correcto': False
        }



class CursoViewSet(viewsets.ModelViewSet):
    """
    ViewSet para gestionar los cursos
    """
    serializer_class = CursoSerializer
    permission_classes = [(IsAdmin|IsDocente)]
    
    def get_queryset(self):
        user = self.request.user
        try:
            profile = UserProfile.objects.get(user=user)
            # Si es admin, ve todos los cursos
            if profile.rol == 'admin' or user.is_superuser:
                return Curso.objects.all()
            # Si es docente, solo ve sus propios cursos
            return Curso.objects.filter(docente=user)
        except UserProfile.DoesNotExist:
            if user.is_superuser:
                return Curso.objects.all()
            return Curso.objects.none()
    
    def perform_create(self, serializer):
        serializer.save(docente=self.request.user)


class EjercicioViewSet(viewsets.ModelViewSet):
    """
    ViewSet para gestionar los ejercicios
    """
    serializer_class = EjercicioSerializer
    permission_classes = [(IsAdmin|IsDocente)]
    
    def get_queryset(self):
        user = self.request.user
        try:
            profile = UserProfile.objects.get(user=user)
            # Si es admin O DOCENTE, ve todos los ejercicios
            if profile.rol == 'admin' or profile.rol == 'docente' or user.is_superuser:
                return Ejercicio.objects.all()
            # Otros roles no ven ejercicios
            return Ejercicio.objects.none()
        except UserProfile.DoesNotExist:
            if user.is_superuser:
                return Ejercicio.objects.all()
            return Ejercicio.objects.none()
    
    def perform_create(self, serializer):
        serializer.save(creador=self.request.user)


class EvaluacionViewSet(viewsets.ModelViewSet):
    """
    ViewSet para gestionar las evaluaciones
    """
    def get_serializer_class(self):
        if self.action in ['retrieve', 'detalles']:
            return EvaluacionDetalladaSerializer
        return EvaluacionSerializer
    
    def get_queryset(self):
        user = self.request.user
        autor_id = self.request.query_params.get('autor_id', None)
        
        # Si se proporciona autor_id, filtrar por creador
        if autor_id:
            return Evaluacion.objects.filter(creador_id=autor_id)
        
        try:
            profile = UserProfile.objects.get(user=user)
            # Si es admin, ve todas las evaluaciones
            if profile.rol == 'admin' or user.is_superuser:
                return Evaluacion.objects.all()
            
            # Si es docente, solo ve sus propias evaluaciones y las del curso
            if profile.rol == 'docente':
                return Evaluacion.objects.filter(
                    Q(creador=user) | Q(curso__in=Curso.objects.filter(docente=user))
                )
            
            # Si es estudiante, ve las evaluaciones en las que está inscrito
            if profile.rol == 'estudiante':
                participaciones = EstudianteEvaluacion.objects.filter(estudiante=user)
                return Evaluacion.objects.filter(id__in=participaciones.values_list('evaluacion_id', flat=True))
            
            return Evaluacion.objects.none()
        except UserProfile.DoesNotExist:
            if user.is_superuser:
                return Evaluacion.objects.all()
            return Evaluacion.objects.none()
    
    def get_permissions(self):
        """
        Configura permisos dinámicamente basados en la acción.
        """
        if self.action == 'validar_codigo':
            return [AllowValidateAccessCode()]
        elif self.action == 'inscribir':
            return [IsAuthenticated(), IsEstudiante()] 
        elif self.action in ['retrieve', 'detalles']:
            return [IsAuthenticated(), HasEvaluationAccess()]
        else:
            return [IsAuthenticated(), (IsAdmin | IsDocente)()]
        
    def perform_create(self, serializer):
        """
        Establece el usuario que crea la evaluación como creador de la misma.
        """
        serializer.save(creador=self.request.user)
    
    @action(detail=False, methods=['post'])
    def validar_codigo(self, request):
        """
        Endpoint para validar códigos de acceso a evaluaciones.
        Puede ser usado tanto por usuarios autenticados como por
        usuarios sin autenticar.
        """
        try:
            # Validar datos de entrada
            codigo = request.data.get('codigo')
            
            if not codigo:
                return Response(
                    {"valid": False, "error": "Debe proporcionar un código de acceso"},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Buscar la evaluación con este código
            try:
                evaluacion = Evaluacion.objects.get(codigo_acceso=codigo.upper())
                
                # Verificar si la evaluación está activa
                ahora = timezone.now()
                if evaluacion.fecha_inicio > ahora:
                    return Response(
                        {"valid": False, "error": f"Esta evaluación aún no está disponible. Comienza el {evaluacion.fecha_inicio.strftime('%d/%m/%Y a las %H:%M')}"},
                        status=status.HTTP_403_FORBIDDEN
                    )
                
                # Verificar si la evaluación ya expiró (si tiene fecha de cierre)
                if evaluacion.fecha_fin and evaluacion.fecha_fin < ahora:
                    return Response(
                        {"valid": False, "error": "Esta evaluación ya ha expirado"},
                        status=status.HTTP_403_FORBIDDEN
                    )
                
                # Obtener IDs de ejercicios
                ejercicios_ids = list(evaluacion.ejercicios.values_list('id', flat=True))
                
                # Si el usuario está autenticado y es estudiante, registrar su acceso
                if request.user.is_authenticated:
                    try:
                        profile = UserProfile.objects.get(user=request.user)
                        if profile.rol == 'estudiante':
                            # Registrar participación del estudiante
                            EstudianteEvaluacion.objects.get_or_create(
                                estudiante=request.user,
                                evaluacion=evaluacion,
                                defaults={'estado': 'pendiente'}
                            )
                    except UserProfile.DoesNotExist:
                        pass
                
                # Todo ok, devolver datos de la evaluación
                return Response({
                    "valid": True,
                    "evaluation": {
                        "id": evaluacion.id,
                        "titulo": evaluacion.titulo,
                        "descripcion": evaluacion.descripcion,
                        "duracion_minutos": evaluacion.duracion_minutos,
                        "fecha_inicio": evaluacion.fecha_inicio.isoformat(),
                        "fecha_fin": evaluacion.fecha_fin.isoformat() if evaluacion.fecha_fin else None,
                        "permitir_revision": evaluacion.permitir_revision,
                        "mostrar_resultado": evaluacion.mostrar_resultado,
                        "orden_aleatorio": evaluacion.orden_aleatorio,
                        "ejercicios": ejercicios_ids,
                        "estado": evaluacion.estado,
                        "codigo_acceso": evaluacion.codigo_acceso
                    }
                })
            except Evaluacion.DoesNotExist:
                return Response(
                    {"valid": False, "error": "Código de acceso inválido"},
                    status=status.HTTP_404_NOT_FOUND
                )
        except Exception as e:
            import logging
            logger = logging.getLogger('django')
            logger.error(f"Error al validar código de acceso: {str(e)}")
            return Response(
                {"valid": False, "error": "Error interno del servidor"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated, IsEstudiante])
    def inscribir(self, request, pk=None):
        """
        Endpoint para que un estudiante se inscriba en una evaluación
        usando un código de acceso.
        """
        try:
            evaluacion = self.get_object()
            codigo = request.data.get('codigo')
            
            # Verificar código de acceso
            if not codigo or codigo.upper() != evaluacion.codigo_acceso:
                return Response(
                    {"error": "Código de acceso inválido"},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Verificar si la evaluación está activa
            ahora = timezone.now()
            if evaluacion.fecha_inicio > ahora:
                return Response(
                    {"error": f"Esta evaluación aún no está disponible. Comienza el {evaluacion.fecha_inicio.strftime('%d/%m/%Y a las %H:%M')}"},
                    status=status.HTTP_403_FORBIDDEN
                )
            
            # Verificar si la evaluación ya expiró
            if evaluacion.fecha_fin and evaluacion.fecha_fin < ahora:
                return Response(
                    {"error": "Esta evaluación ya ha expirado"},
                    status=status.HTTP_403_FORBIDDEN
                )
            
            # Crear o actualizar registro de participación
            participacion, created = EstudianteEvaluacion.objects.get_or_create(
                estudiante=request.user,
                evaluacion=evaluacion,
                defaults={'estado': 'pendiente'}
            )
            
            return Response({
                "success": True,
                "message": "Inscripción exitosa",
                "participacion_id": participacion.id
            })
            
        except Exception as e:
            import logging
            logger = logging.getLogger('django')
            logger.error(f"Error en inscripción: {str(e)}")
            return Response(
                {"error": "Error al procesar la inscripción"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    def create(self, request, *args, **kwargs):
        # Añadir logs
        print("Datos recibidos para crear evaluación:", request.data)
        
        if 'ejercicios' in request.data:
            print("Ejercicios recibidos:", request.data['ejercicios'])
        else:
            print("No se recibieron ejercicios en la solicitud")
        
        # Continuar con la lógica normal
        return super().create(request, *args, **kwargs)
    
    def update(self, request, *args, **kwargs):
        # Añadir logs
        print("Datos recibidos para actualizar evaluación:", request.data)
        
        if 'ejercicios' in request.data:
            print("Ejercicios recibidos:", request.data['ejercicios'])
        else:
            print("No se recibieron ejercicios en la solicitud")
        
        # Continuar con la lógica normal
        return super().update(request, *args, **kwargs)
    
    def destroy(self, request, *args, **kwargs):
        """
        Sobrescribe el método destroy para guardar evaluaciones en historial antes de borrar
        """
        evaluacion = self.get_object()
        
        # Guardar todas las participaciones finalizadas en el historial
        participaciones_finalizadas = EstudianteEvaluacion.objects.filter(
            evaluacion=evaluacion,
            estado='finalizado'
        )
        
        for participacion in participaciones_finalizadas:
            guardar_evaluacion_en_historial(participacion)
        
        # Actualizar todos los historiales relacionados a esta evaluación
        HistorialEvaluacion.objects.filter(
            evaluacion_id=evaluacion.id
        ).update(evaluacion_activa=False)
        
        return super().destroy(request, *args, **kwargs)
    
    

class UsuarioViewSet(viewsets.ModelViewSet):
    """
    ViewSet para gestionar usuarios
    """
    serializer_class = UsuarioSerializer
    
    def get_permissions(self):
        if self.action in ['list', 'retrieve', 'create', 'update', 'partial_update', 'destroy']:
            return [IsAdminUser()]
        return [permissions.IsAuthenticated()]
    
    def get_queryset(self):
        # Los admins pueden ver todos los usuarios
        # Los docentes solo pueden ver a sus estudiantes
        user = self.request.user
        
        try:
            profile = UserProfile.objects.get(user=user)
            if profile.rol == 'admin' or user.is_superuser:
                return User.objects.all()
            elif profile.rol == 'docente':
                # Obtener los cursos donde el usuario es docente
                cursos_docente = Curso.objects.filter(docente=user)
                # Obtener los estudiantes de esos cursos
                estudiantes_ids = []
                for curso in cursos_docente:
                    estudiantes_ids.extend(curso.estudiantes.values_list('id', flat=True))
                
                return User.objects.filter(id__in=estudiantes_ids)
        except UserProfile.DoesNotExist:
            if user.is_superuser:
                return User.objects.all()
        
        # Los estudiantes no deberían acceder a esta vista
        return User.objects.none()




@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_detalles_evaluacion(request, pk):
    """
    Obtener detalles completos de una evaluación incluyendo ejercicios
    """
    try:
        evaluacion = Evaluacion.objects.get(pk=pk)
        
        print(f"Obteniendo detalles para evaluación ID: {pk}")
        print(f"Título: {evaluacion.titulo}")
        
        # Verificar si hay ejercicios directamente
        ejercicios_count = evaluacion.ejercicios.count()
        print(f"Cantidad de ejercicios (directa): {ejercicios_count}")
        
        # Verificar si hay relaciones en EvaluacionEjercicio
        ee_count = evaluacion.evaluacionejercicio_set.count()
        print(f"Cantidad de relaciones EvaluacionEjercicio: {ee_count}")
        
        # Obtener ejercicios completos usando el serializador
        ejercicios = []
        for ee in evaluacion.evaluacionejercicio_set.all().order_by('orden'):
            ejercicio = ee.ejercicio
            
            # Log para cada ejercicio
            print(f"Procesando ejercicio ID: {ejercicio.id}, Título: {ejercicio.titulo}")
            
            # USAR EL SERIALIZADOR en lugar de construir manualmente
            from .serializers import EjercicioSerializer
            serializer = EjercicioSerializer(ejercicio)
            ejercicio_data = serializer.data
            
            # Extraer información del contenido JSON para campos adicionales
            contenido = ejercicio.contenido or {}
            if isinstance(contenido, str):
                try:
                    contenido = json.loads(contenido)
                except:
                    contenido = {}
            
            # Agregar campos adicionales que necesita el frontend
            ejercicio_data.update({
                'restricciones': contenido.get('restricciones', ''),
                'formato_salida': contenido.get('formato_salida', ''),
                'ejemplos': contenido.get('ejemplos', []),
                'tests_publicos': contenido.get('tests_publicos', []),
                'orden': ee.orden
            })
            
            ejercicios.append(ejercicio_data)
        
        # Usar el serializador de evaluación base
        from .serializers import EvaluacionSerializer
        evaluacion_serializer = EvaluacionSerializer(evaluacion)
        evaluacion_data = evaluacion_serializer.data
        
        # Agregar los ejercicios procesados
        evaluacion_data['ejercicios'] = ejercicios
        
        print(f"Respuesta exitosa: {len(ejercicios)} ejercicios encontrados")
        
        return Response({
            'success': True,
            'evaluacion': evaluacion_data
        })
        
    except Evaluacion.DoesNotExist:
        print(f"Evaluación ID {pk} no encontrada")
        return Response({
            'success': False,
            'error': 'Evaluación no encontrada'
        }, status=status.HTTP_404_NOT_FOUND)
        
    except Exception as e:
        print(f"Error en get_detalles_evaluacion: {str(e)}")
        import traceback
        traceback.print_exc()
        return Response({
            'success': False,
            'error': 'Error del servidor'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# Funciones para ejecutar código de los estudiantes
def ejecutar_codigo(codigo, entrada):
    """
    Ejecuta código Python con una entrada determinada y devuelve el resultado.
    Optimizado para reducir operaciones I/O.
    """
    import hashlib
    
    # Calcular hashes para caché
    codigo_hash = hashlib.md5(codigo.encode()).hexdigest()
    entrada_hash = hashlib.md5(entrada.encode()).hexdigest()
    
    # Guardar en caché temporal por 1 hora
    cache.set(f"codigo_{codigo_hash}", codigo, timeout=3600)
    cache.set(f"entrada_{entrada_hash}", entrada, timeout=3600)
    
    # Crear archivo temporal para el código
    with tempfile.NamedTemporaryFile(suffix='.py', delete=False) as f:
        f.write(codigo.encode('utf-8'))
        temp_file = f.name
    
    # Crear archivo temporal para la entrada
    with tempfile.NamedTemporaryFile(suffix='.txt', delete=False) as f:
        f.write(entrada.encode('utf-8'))
        input_file = f.name
    
    try:
        start_time = time.time()
        process = subprocess.Popen(
            ['python', temp_file],
            stdin=open(input_file, 'r'),
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        
        try:
            output, error = process.communicate(timeout=5)
            execution_time = time.time() - start_time
            
            return {
                'output': output,
                'error': error,
                'time': execution_time
            }
        except subprocess.TimeoutExpired:
            process.kill()
            return {
                'output': '',
                'error': 'Tiempo de ejecución excedido (límite: 5 segundos)',
                'time': 5.0
            }
    finally:
        # Eliminar archivos temporales en segundo plano
        def cleanup():
            try:
                if os.path.exists(temp_file):
                    os.unlink(temp_file)
                if os.path.exists(input_file):
                    os.unlink(input_file)
            except:
                pass
        threading.Thread(target=cleanup).start()
        

@lru_cache(maxsize=128)
def ejecutar_codigo_cached(codigo_hash, entrada_hash):
    """Versión en caché de ejecutar_código que usa hashes como claves."""
    codigo = cache.get(f"codigo_{codigo_hash}")
    entrada = cache.get(f"entrada_{entrada_hash}")
    
    if not codigo or not entrada:
        return {
            'output': '',
            'error': 'Datos de ejecución no encontrados',
            'time': 0
        }
    
    return ejecutar_codigo(codigo, entrada)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def submit_codigo(request):
    """
    Evalúa el código del estudiante contra un ejercicio usando Judge0
    """
    try:
        codigo = request.data.get('codigo')
        ejercicio_id = request.data.get('ejercicio_id')
        evaluacion_id = request.data.get('evaluacion_id')
        
        logger.info(f"Ejecución iniciada para estudiante {request.user.id}, "
                   f"evaluación {evaluacion_id}, ejercicio {ejercicio_id}")
        
        if not codigo or not ejercicio_id or not evaluacion_id:
            return Response({
                'success': False,
                'message': 'Datos incompletos'
            }, status=400)
            
        # Obtener o crear participación del estudiante
        evaluacion = get_object_or_404(Evaluacion, pk=evaluacion_id)
        estudiante_evaluacion, created = EstudianteEvaluacion.objects.get_or_create(
            estudiante=request.user,
            evaluacion=evaluacion,
            defaults={
                'estado': 'activo',
                'fecha_inicio': timezone.now()  # IMPORTANTE: Asegurar fecha_inicio
            }
        )
        
        # Si ya existía pero no tenía fecha_inicio, establecerla
        if not created and not estudiante_evaluacion.fecha_inicio:
            estudiante_evaluacion.fecha_inicio = timezone.now()
            estudiante_evaluacion.save()
            logger.info(f"[Batch:{batch_id}] Establecida fecha_inicio para participación existente")
        
        # Obtener el ejercicio
        ejercicio = get_object_or_404(Ejercicio, pk=ejercicio_id)
        
        # Verificar disponibilidad de Judge0
        is_available, message = check_judge0_availability()
        if not is_available:
            return Response({
                'ejercicio_id': ejercicio_id,
                'success': False,
                'message': 'El servicio Judge0 no está disponible en este momento',
                'details': message
            }, status=503)  # 503 Service Unavailable
            
        # Preparar resultado
        resultado = {
            'ejercicio_id': ejercicio_id,
            'success': True,
            'casos_correctos': 0,
            'total_casos': 0,
            'porcentaje': 0,
            'puntaje_obtenido': 0,
            'puntaje_maximo': ejercicio.puntaje or 10,
            'es_correcto': False
        }
        
        # Determinar el tipo de prueba a ejecutar
        
        # 1. Verificar si hay tests avanzados
        tests_avanzados = ejercicio.tests_avanzados
        if not tests_avanzados and hasattr(ejercicio, 'contenido') and ejercicio.contenido:
            contenido = ejercicio.contenido
            if isinstance(contenido, str):
                try:
                    contenido = json.loads(contenido)
                except:
                    contenido = {}
            
            if isinstance(contenido, dict):
                tests_avanzados = contenido.get('tests_avanzados')
                
        if tests_avanzados:
            # Ejecutar tests avanzados
            from .judge_utils import ejecutar_tests_avanzados
            
            # Obtener el ID del lenguaje de la solicitud
            language_id = request.data.get('language_id', 71)  # Por defecto: Python
    
            test_result = ejecutar_tests_avanzados(codigo, tests_avanzados, language_id)
            
            if test_result['success']:
                casos_correctos = test_result['pruebas_pasadas']
                total_casos = test_result['total_pruebas']
                es_correcto = test_result['es_correcto']
                
                # Actualizar resultado
                resultado['casos_correctos'] = casos_correctos
                resultado['total_casos'] = total_casos
                resultado['es_correcto'] = es_correcto
                resultado['porcentaje'] = (casos_correctos / total_casos) * 100 if total_casos > 0 else 0
                resultado['puntaje_obtenido'] = (casos_correctos / total_casos) * resultado['puntaje_maximo'] if total_casos > 0 else 0
                
                # Añadir salida para diagnóstico
                resultado['output'] = test_result['output']
                resultado['stderr'] = test_result['stderr']
            else:
                resultado['success'] = False
                resultado['message'] = 'Error en los tests avanzados'
                resultado['stderr'] = test_result['stderr']
        
        # 2. Si hay ejemplos, usarlos como casos de prueba
        elif 'ejemplos' in contenido and contenido['ejemplos']:
            # Usar función de judge_utils para verificar ejemplos
            from .judge_utils import verificar_ejemplos
            
            ejemplos = contenido['ejemplos']
            verification_result = verificar_ejemplos(codigo, ejemplos)
            
            if verification_result['success']:
                casos_correctos = verification_result['casos_correctos']
                total_casos = verification_result['total_ejemplos']
                es_correcto = casos_correctos == total_casos
                
                # Actualizar resultado
                resultado['casos_correctos'] = casos_correctos
                resultado['total_casos'] = total_casos
                resultado['es_correcto'] = es_correcto
                resultado['porcentaje'] = verification_result['porcentaje_exito']
                resultado['puntaje_obtenido'] = (casos_correctos / total_casos) * resultado['puntaje_maximo'] if total_casos > 0 else 0
                resultado['output'] = verification_result['resultados']
            else:
                resultado['success'] = False
                resultado['message'] = 'Error al verificar ejemplos'
                resultado['stderr'] = verification_result.get('message', '')
        
        # 3. Si no hay tests ni ejemplos, ejecutar código simple
        else:
            # Usar función de judge_utils para ejecutar el código
            from .judge_utils import ejecutar_codigo
            
            code_result = ejecutar_codigo(codigo)
            
            # Si no hay errores, consideramos que el ejercicio es correcto
            if code_result['success']:
                resultado['casos_correctos'] = 1
                resultado['total_casos'] = 1
                resultado['es_correcto'] = True
                resultado['porcentaje'] = 100
                resultado['puntaje_obtenido'] = resultado['puntaje_maximo']
            else:
                resultado['casos_correctos'] = 0
                resultado['total_casos'] = 1
                resultado['es_correcto'] = False
                resultado['porcentaje'] = 0
                resultado['puntaje_obtenido'] = 0
            
            # Añadir salida para diagnóstico
            resultado['output'] = code_result['stdout']
            resultado['stderr'] = code_result['stderr']
        
        # Guardar respuesta en la base de datos
        try:
            # CORREGIDO: Obtener language_id del ejercicio enviado
            language_id = ej.get('language_id', 71)  # Por defecto Python
            logger.info(f"[Batch:{batch_id}] Guardando con language_id: {language_id} para ejercicio {ejercicio_id}")
            
            # Preparar objeto de respuesta para guardar
            respuesta_content = {
                'codigo': codigo,
                'resultados': resultado.get('output', []),
                'language_id': language_id  # AGREGAR AL JSON TAMBIÉN
            }
            
            # Si hay stderr, añadirlo
            if 'stderr' in resultado and resultado['stderr']:
                respuesta_content['stderr'] = resultado['stderr']
            
            respuesta, created = RespuestaEjercicio.objects.update_or_create(
                estudiante_evaluacion=estudiante_evaluacion,
                ejercicio=ejercicio,
                defaults={
                    'respuesta': respuesta_content,
                    'es_correcta': resultado['es_correcto'],
                    'puntaje_obtenido': resultado['puntaje_obtenido'],
                    'fecha_respuesta': timezone.now(),
                    'language_id': language_id
                }
            )
            
            logger.info(f"[Batch:{batch_id}] Respuesta guardada con language_id {language_id} para ejercicio {ejercicio_id}")
            
        except Exception as db_error:
            # Reportar el error pero no fallar la ejecución completa
            logger.error(f"Error al guardar respuesta en BD: {str(db_error)}")
            # Añadir información al resultado
            resultado['db_warning'] = "Respuesta evaluada pero no guardada en base de datos"
        
        return Response(resultado)
        
    except Exception as e:
        logger.error(f"Error en submit_codigo: {str(e)}")
        return Response({
            'ejercicio_id': ejercicio_id if 'ejercicio_id' in locals() else None,
            'success': False,
            'message': f'Error: {str(e)}'
        }, status=500)



@api_view(['POST'])
@permission_classes([IsAuthenticated])
def submit_batch(request):
    """Procesa múltiples ejercicios en paralelo para evaluación final."""
    try:
        evaluacion_id = request.data.get('evaluacion_id')
        ejercicios = request.data.get('ejercicios', [])
        batch_id = request.data.get('batch_id', 'unknown')
        
        # IMPORTANTE: Obtener resultados_judge0 que el frontend ya procesó
        resultados_judge0 = request.data.get('resultados_judge0', [])
        
        
        logger.info(f"[Batch:{batch_id}] Inicio de procesamiento batch para evaluación {evaluacion_id} con {len(ejercicios)} ejercicios")
        
        if not evaluacion_id or not ejercicios:
            return Response({
                'success': False,
                'message': 'Datos incompletos'
            }, status=status.HTTP_400_BAD_REQUEST)
            
        # Verificar evaluación
        try:
            evaluacion = Evaluacion.objects.get(pk=evaluacion_id)
            logger.info(f"[Batch:{batch_id}] Evaluación encontrada: {evaluacion.titulo}")
        except Evaluacion.DoesNotExist:
            return Response({
                'success': False,
                'message': 'Evaluación no encontrada'
            }, status=status.HTTP_404_NOT_FOUND)
            
        # Obtener participación
        estudiante_evaluacion, created = EstudianteEvaluacion.objects.get_or_create(
            estudiante=request.user,
            evaluacion=evaluacion,
            defaults={
                'estado': 'activo',
                'fecha_inicio': timezone.now()
            }
        )
        

        # MODIFICADO: Usar resultados de Judge0 si están disponibles
        if resultados_judge0:
            logger.info(f"[Batch:{batch_id}] Usando resultados de Judge0 procesados por el frontend")
            resultados = resultados_judge0
        else:
            # Fallback al procesamiento local si no hay resultados de Judge0
            logger.info(f"[Batch:{batch_id}] No hay resultados de Judge0, usando procesamiento local")
            resultados = []

            # Importar la función auxiliar para añadir funciones de test si no existen
            from .models import get_codigo_con_funciones_auxiliares
            
            # Variables para el resultado total
            total_puntaje = 0
            puntaje_maximo = 0

            # Procesamiento local de cada ejercicio
            for idx, ej in enumerate(ejercicios):
                try:
                    ejercicio_id = ej.get('ejercicio_id')
                    codigo = ej.get('codigo', '')
                    
                    logger.info(f"[Batch:{batch_id}] Procesando ejercicio {idx+1}/{len(ejercicios)}: ID={ejercicio_id}")
                    
                    if not ejercicio_id:
                        logger.warning(f"[Batch:{batch_id}] Ejercicio sin ID")
                        resultados.append({
                            'ejercicio_id': None,
                            'success': False,
                            'message': 'ID de ejercicio no proporcionado'
                        })
                        continue
                        
                    # Verificar si el ejercicio existe
                    try:
                        ejercicio = Ejercicio.objects.get(id=ejercicio_id)
                        logger.info(f"[Batch:{batch_id}] Ejercicio encontrado: {ejercicio.titulo}")
                    except Ejercicio.DoesNotExist:
                        logger.warning(f"[Batch:{batch_id}] Ejercicio {ejercicio_id} no encontrado")
                        resultados.append({
                            'ejercicio_id': ejercicio_id,
                            'success': False,
                            'message': 'Ejercicio no encontrado'
                        })
                        continue
                    
                    # MODIFICADO: Manejar ejercicios sin código o con código vacío
                    if not codigo or codigo.strip() == '':
                        logger.info(f"[Batch:{batch_id}] Ejercicio {ejercicio_id} sin código, asignando 0 puntos")
                        resultado = {
                            'ejercicio_id': ejercicio_id,
                            'success': True,
                            'es_correcto': False,
                            'casos_correctos': 0,
                            'total_casos': 1,
                            'porcentaje': 0,
                            'puntaje_obtenido': 0,
                            'puntaje_maximo': ejercicio.puntaje or 10
                        }
                        resultados.append(resultado)
                        puntaje_maximo += ejercicio.puntaje or 10
                        
                        # Guardar en la base de datos
                        respuesta_content = {
                            'codigo': '',
                            'resultados': []
                        }
                        
                        RespuestaEjercicio.objects.update_or_create(
                            estudiante_evaluacion=estudiante_evaluacion,
                            ejercicio=ejercicio,
                            defaults={
                                'respuesta': respuesta_content,
                                'es_correcta': resultado.get('es_correcto', False),
                                'puntaje_obtenido': resultado.get('puntaje_obtenido', 0),
                                'fecha_respuesta': timezone.now(),
                                'language_id': language_id
                            }
                        )
                        print(f"[Batch:{batch_id}] Respuesta guardada: ejercicio {ejercicio_id}, language_id {language_id}, es_correcta {resultado.get('es_correcto', False)}")
                        continue
                    
                    # Aplicar funciones auxiliares si son necesarias y hay código
                    codigo = get_codigo_con_funciones_auxiliares(ejercicio, codigo)
                    logger.info(f"[Batch:{batch_id}] Código con funciones auxiliares preparado para ejercicio {ejercicio_id}")
                    
                    # Procesar el ejercicio
                    try:
                        logger.info(f"[Batch:{batch_id}] Ejecutando procesamiento para ejercicio {ejercicio_id}")
                        resultado = procesar_ejercicio(codigo, ejercicio_id, evaluacion_id, estudiante_evaluacion.id)
                        logger.info(f"[Batch:{batch_id}] Resultado: {resultado.get('success')}, Es correcto: {resultado.get('es_correcto', False)}")
                        
                        resultados.append(resultado)
                        
                        # Sumar puntaje si fue exitoso
                        if resultado.get('success', False):
                            total_puntaje += resultado.get('puntaje_obtenido', 0)
                            puntaje_maximo += resultado.get('puntaje_maximo', 0)
                    except Exception as e:
                        logger.error(f"[Batch:{batch_id}] Error al procesar ejercicio {ejercicio_id}: {str(e)}")
                        resultados.append({
                            'ejercicio_id': ejercicio_id,
                            'success': False,
                            'message': f'Error: {str(e)}'
                        })
                except Exception as e:
                    logger.error(f"[Batch:{batch_id}] Error general en ejercicio {idx+1}: {str(e)}")
                    resultados.append({
                        'ejercicio_id': ej.get('ejercicio_id'),
                        'success': False,
                        'message': f'Error general: {str(e)}'
                    })
        
        # Para todos los resultados, guardar en la base de datos
        # MEJORADO: Mejor manejo de errores al guardar respuestas
        for resultado in resultados:
            # Solo procesar resultados válidos
            if not resultado.get('ejercicio_id'):
                continue
            
            ejercicio_id = resultado.get('ejercicio_id')
            
            # Guardar en la base de datos
            try:
                ejercicio = Ejercicio.objects.get(id=ejercicio_id)
                
                # CORREGIDO: Obtener datos del ejercicio enviado incluyendo language_id
                ejercicio_enviado = next(
                    (ej for ej in ejercicios if ej.get('ejercicio_id') == ejercicio_id), 
                    {}
                )
                
                codigo_ejercicio = ejercicio_enviado.get('codigo', '')
                language_id = ejercicio_enviado.get('language_id', 71)  # Por defecto Python
                
                logger.info(f"[Batch:{batch_id}] Guardando Judge0 result con language_id: {language_id} para ejercicio {ejercicio_id}")
                
                respuesta_content = {
                    'codigo': codigo_ejercicio,
                    'resultados': resultado.get('output', []),
                    'language_id': language_id  # AGREGAR AL JSON
                }
                
                # Añadir stderr si existe
                if resultado.get('stderr'):
                    respuesta_content['stderr'] = resultado.get('stderr')
                
                # IMPORTANTE: Siempre sobrescribir la respuesta, no mantener respuestas previas
                RespuestaEjercicio.objects.update_or_create(
                    estudiante_evaluacion=estudiante_evaluacion,
                    ejercicio=ejercicio,
                    defaults={
                        'respuesta': respuesta_content,
                        'es_correcta': resultado.get('es_correcto', False),
                        'puntaje_obtenido': resultado.get('puntaje_obtenido', 0),
                        'fecha_respuesta': timezone.now(),
                        'language_id': language_id  # DESCOMENTAR Y CORREGIR
                    }
                )
                
                logger.info(f"[Batch:{batch_id}] Judge0 result guardado con language_id {language_id} para ejercicio {ejercicio_id}")
            
            
            except Exception as db_error:
                logger.error(f"[Batch:{batch_id}] Error al guardar respuesta en DB para ejercicio {ejercicio_id}: {str(db_error)}")
                
        print(f"[Batch:{batch_id}] Total respuestas guardadas: {len(resultados)}")
        
        # Actualizar estado estudiante
        try:
            total_ejercicios = evaluacion.ejercicios.count()
            ejercicios_respondidos = RespuestaEjercicio.objects.filter(
                estudiante_evaluacion=estudiante_evaluacion
            ).count()
            
            # Calcular puntuación total de los resultados actuales
            total_puntaje = sum(resultado.get('puntaje_obtenido', 0) for resultado in resultados)
            puntaje_maximo = sum(resultado.get('puntaje_maximo', 0) for resultado in resultados)
            
            estudiante_evaluacion.progreso = (ejercicios_respondidos / total_ejercicios) * 100 if total_ejercicios > 0 else 0
            estudiante_evaluacion.puntaje = total_puntaje
            
            if ejercicios_respondidos >= total_ejercicios:
                estudiante_evaluacion.estado = 'finalizado'
                estudiante_evaluacion.fecha_fin = timezone.now()
                
                # CRÍTICO: Calcular tiempo ANTES de guardar en historial
                if not estudiante_evaluacion.tiempo_total_ms:
                    # Intentar obtener del request data
                    tiempo_desde_frontend = request.data.get('tiempo_total_ms')
                    if tiempo_desde_frontend and tiempo_desde_frontend > 0:
                        estudiante_evaluacion.tiempo_total_ms = int(tiempo_desde_frontend)
                        logger.info(f"[Batch:{batch_id}] Tiempo desde frontend: {tiempo_desde_frontend}ms")
                    # Si no hay tiempo del frontend, calcular desde fechas
                    elif estudiante_evaluacion.fecha_inicio and estudiante_evaluacion.fecha_fin:
                        tiempo_ms = int((estudiante_evaluacion.fecha_fin - estudiante_evaluacion.fecha_inicio).total_seconds() * 1000)
                        estudiante_evaluacion.tiempo_total_ms = tiempo_ms
                        logger.info(f"[Batch:{batch_id}] Tiempo calculado desde fechas: {tiempo_ms}ms")
                    else:
                        logger.warning(f"[Batch:{batch_id}] No se pudo calcular tiempo total")
                
                # Guardar primero el estudiante con el tiempo
                estudiante_evaluacion.save()
                
                # IMPORTANTE: Solo guardar en historial si no existe ya
                historial_existente = HistorialEvaluacion.objects.filter(
                    estudiante_id=estudiante_evaluacion.estudiante.id,
                    evaluacion_id=estudiante_evaluacion.evaluacion.id
                ).first()
                
                if not historial_existente:
                    # Guardar en historial con todas las respuestas ya procesadas
                    guardar_evaluacion_en_historial(estudiante_evaluacion)
                    logger.info(f"[Batch:{batch_id}] Historial guardado correctamente")
                else:
                    logger.info(f"[Batch:{batch_id}] Historial ya existe, no se duplica")
            else:
                estudiante_evaluacion.save()
            
            logger.info(f"[Batch:{batch_id}] Estado del estudiante actualizado: {estudiante_evaluacion.estado}, Progreso: {estudiante_evaluacion.progreso}%, Puntaje: {estudiante_evaluacion.puntaje}")
        except Exception as update_error:
            logger.error(f"[Batch:{batch_id}] Error al actualizar estado estudiante: {str(update_error)}")
        
        puntaje_sobre_10 = (total_puntaje / puntaje_maximo) * 10 if puntaje_maximo > 0 else 0
        logger.info(f"[Batch:{batch_id}] Procesamiento completado: {total_puntaje}/{puntaje_maximo} puntos, {puntaje_sobre_10}/10")
        
        return Response({
            'success': True,
            'message': 'Procesamiento en lote completado',
            'resultados': resultados,
            'total_puntaje': total_puntaje,
            'puntaje_maximo': puntaje_maximo,
            'puntaje_sobre_10': round(puntaje_sobre_10, 2),
            'progreso': estudiante_evaluacion.progreso,
            'estado': estudiante_evaluacion.estado
        })
    except Exception as e:
        logger.error(f"Error en submit_batch: {str(e)}")
        return Response({
            'success': False,
            'message': f'Error del servidor: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def test_codigo(request):
    """
    Ejecuta una prueba rápida del código del estudiante para un ejercicio específico
    """
    try:
        logger.info(f"Test iniciado para estudiante {request.user.id}")
        
        codigo = request.data.get('codigo')
        ejercicio_id = request.data.get('ejercicio_id')
        evaluacion_id = request.data.get('evaluacion_id')
        
        if not codigo or not ejercicio_id or not evaluacion_id:
            return Response({
                'success': False,
                'message': 'Datos incompletos'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Verificar que el ejercicio pertenece a la evaluación
        try:
            evaluacion = Evaluacion.objects.get(pk=evaluacion_id)
            ejercicio = Ejercicio.objects.get(pk=ejercicio_id)
            
            if ejercicio not in evaluacion.ejercicios.all():
                return Response({
                    'success': False,
                    'message': 'El ejercicio no pertenece a esta evaluación'
                }, status=status.HTTP_400_BAD_REQUEST)
        except (Evaluacion.DoesNotExist, Ejercicio.DoesNotExist):
            return Response({
                'success': False,
                'message': 'Evaluación o ejercicio no encontrado'
            }, status=status.HTTP_404_NOT_FOUND)
        
        # Obtener el contenido del ejercicio
        contenido = ejercicio.contenido
        if isinstance(contenido, str):
            try:
                contenido = json.loads(contenido)
            except:
                contenido = {}
        
        # Obtener caso de prueba (primer ejemplo)
        ejemplos = contenido.get('ejemplos', [])
        if not ejemplos:
            return Response({
                'success': False,
                'message': 'No hay ejemplos disponibles para este ejercicio'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        ejemplo = ejemplos[0]
        
        # NUEVO: Intentar usar Judge0 si está disponible
        try:
            from .judge_utils import JUDGE0_API_URL
            if JUDGE0_API_URL:
                # Usar las nuevas funciones de judge_utils.py
                from .judge_utils import ejecutar_codigo
                
                # Ejecutar código con Judge0
                result = ejecutar_codigo(codigo, ejemplo.get('entrada', ''))
                
                if result['stderr']:
                    return Response({
                        'success': False,
                        'message': 'Error al ejecutar el código',
                        'output': result['stderr']
                    }, status=status.HTTP_400_BAD_REQUEST)
                
                # Comparar resultado con la salida esperada
                salida_esperada = ejemplo.get('salida', '').strip()
                salida_obtenida = result['stdout'].strip()
                
                es_correcto = salida_obtenida == salida_esperada
                
                logger.info(f"Test completado. Estudiante: {request.user.id}, "
                           f"Ejercicio: {ejercicio_id}, "
                           f"Correcto: {es_correcto}")
                
                return Response({
                    'success': True,
                    'correct': es_correcto,
                    'expected_output': salida_esperada,
                    'actual_output': salida_obtenida,
                    'execution_time': result['time']
                })
                
        except (ImportError, AttributeError) as e:
            # Si falla Judge0, continuamos con el método antiguo
            logger.warning(f"No se pudo usar Judge0 para test_codigo: {str(e)}")
            
        # Método original (fallback) si Judge0 no está disponible
        result = ejecutar_codigo(codigo, ejemplo.get('entrada', ''))
        
        if result['error']:
            return Response({
                'success': False,
                'message': 'Error al ejecutar el código',
                'output': result['error']
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Comparar resultado con la salida esperada
        salida_esperada = ejemplo.get('salida', '').strip()
        salida_obtenida = result['output'].strip()
        
        es_correcto = salida_obtenida == salida_esperada
        
        logger.info(f"Test completado. Estudiante: {request.user.id}, "
                   f"Ejercicio: {ejercicio_id}, "
                   f"Correcto: {es_correcto}")
        
        return Response({
            'success': True,
            'correct': es_correcto,
            'expected_output': salida_esperada,
            'actual_output': salida_obtenida,
            'execution_time': result['time']
        })
        
    except Exception as e:
        print(f"Error en test de código: {str(e)}")
        return Response({
            'success': False,
            'message': f'Error del servidor: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
    
        
@api_view(['GET'])
def admin_check_evaluacion(request, pk):
    """Endpoint de verificación administrativa para evaluaciones"""
    if not request.user.is_staff:
        return JsonResponse({'error': 'Acceso denegado'}, status=403)
        
    try:
        evaluacion = Evaluacion.objects.get(pk=pk)
        ejercicios_directos = list(evaluacion.ejercicios.values('id', 'titulo'))
        ejercicios_relacion = list(
            evaluacion.evaluacionejercicio_set.select_related('ejercicio')
            .values('ejercicio__id', 'ejercicio__titulo', 'orden')
        )
        
        return JsonResponse({
            'id': evaluacion.id,
            'titulo': evaluacion.titulo,
            'ejercicios_directos': ejercicios_directos,
            'ejercicios_relacion': ejercicios_relacion,
            'tiene_ejercicios': len(ejercicios_directos) > 0 or len(ejercicios_relacion) > 0
        })
    except Evaluacion.DoesNotExist:
        return JsonResponse({'error': 'Evaluación no encontrada'}, status=404)
    



@api_view(['POST'])
@permission_classes([IsAuthenticated])
def finalizar_evaluacion(request, pk):
    """
    Finaliza oficialmente una evaluación para un estudiante
    """
    try:
        estudiante_id = request.data.get('estudiante_id')
        tiempo_total_ms = request.data.get('tiempo_total_ms')  # RECIBIR tiempo del frontend
        
        if not estudiante_id:
            estudiante_id = request.user.id
            
        evaluacion = get_object_or_404(Evaluacion, pk=pk)
        estudiante = get_object_or_404(User, pk=estudiante_id)
        
        # Buscar o crear registro de participación
        participacion, created = EstudianteEvaluacion.objects.get_or_create(
            estudiante=estudiante,
            evaluacion=evaluacion,
            defaults={'estado': 'finalizado', 'fecha_fin': timezone.now()}
        )
        
        # Si no es nueva, actualizar estado y fecha
        if not created:
            participacion.estado = 'finalizado'
            participacion.fecha_fin = timezone.now()
        
        # CRÍTICO: Guardar tiempo total si se proporcionó desde el frontend
        if tiempo_total_ms and tiempo_total_ms > 0:
            participacion.tiempo_total_ms = int(tiempo_total_ms)
            print(f"✅ Tiempo total guardado desde frontend: {tiempo_total_ms}ms ({tiempo_total_ms/1000:.1f}s)")
        elif participacion.fecha_inicio and participacion.fecha_fin:
            # Calcular desde fechas como fallback
            tiempo_ms = int((participacion.fecha_fin - participacion.fecha_inicio).total_seconds() * 1000)
            participacion.tiempo_total_ms = tiempo_ms
            print(f"⚠️ Tiempo total calculado desde fechas: {tiempo_ms}ms ({tiempo_ms/1000:.1f}s)")
        else:
            print("❌ No se pudo determinar el tiempo total de la evaluación")
        
        participacion.save()
        
        # Guardar en historial DESPUÉS de guardar el tiempo
        guardar_evaluacion_en_historial(participacion)
        
        return Response({
            'success': True,
            'message': 'Evaluación finalizada con éxito',
            'tiempo_guardado_ms': participacion.tiempo_total_ms,
            'tiempo_guardado_segundos': participacion.tiempo_total_ms / 1000 if participacion.tiempo_total_ms else None
        })
        
    except Exception as e:
        print(f"❌ Error al finalizar evaluación: {str(e)}")
        return Response({
            'success': False,
            'message': f'Error al finalizar evaluación: {str(e)}'
        }, status=500)



@api_view(['GET'])
@permission_classes([IsAuthenticated])
def resultados_evaluacion(request, pk):
    """
    Obtiene los resultados de una evaluación para un estudiante
    """
    try:
        estudiante_id = request.query_params.get('estudiante_id')
        if not estudiante_id:
            estudiante_id = request.user.id
            
        evaluacion = get_object_or_404(Evaluacion, pk=pk)
        estudiante = get_object_or_404(User, pk=estudiante_id)
        
        participacion = get_object_or_404(
            EstudianteEvaluacion, 
            estudiante=estudiante,
            evaluacion=evaluacion
        )
        
        # Obtener todas las respuestas
        respuestas = RespuestaEjercicio.objects.filter(
            estudiante_evaluacion=participacion
        ).select_related('ejercicio')
        
        # Calcular estadísticas
        puntaje_total = participacion.puntaje or 0
        puntaje_maximo = sum(e.puntaje for e in evaluacion.ejercicios.all())
        
        # Calcular puntaje sobre 10
        puntaje_sobre_10 = 0
        if puntaje_maximo > 0:
            puntaje_sobre_10 = (puntaje_total / puntaje_maximo) * 10
        
        # Preparar detalles de respuestas
        respuestas_detalle = []
        for r in respuestas:
            respuestas_detalle.append({
                'ejercicio_id': r.ejercicio.id,
                'ejercicio_titulo': r.ejercicio.titulo,
                'puntaje_obtenido': r.puntaje_obtenido,
                'puntaje_maximo': r.ejercicio.puntaje,
                'es_correcta': r.es_correcta,
                'fecha_respuesta': r.fecha_respuesta.isoformat()
            })
        
        return Response({
            'success': True,
            'puntaje_total': puntaje_total,
            'puntaje_maximo': puntaje_maximo,
            'puntaje_sobre_10': round(puntaje_sobre_10, 2),
            'porcentaje': round((puntaje_total / puntaje_maximo) * 100, 2) if puntaje_maximo > 0 else 0,
            'estado': participacion.estado,
            'fecha_inicio': participacion.fecha_inicio.isoformat() if participacion.fecha_inicio else None,
            'fecha_fin': participacion.fecha_fin.isoformat() if participacion.fecha_fin else None,
            'respuestas': respuestas_detalle
        })
        
    except EstudianteEvaluacion.DoesNotExist:
        return Response({
            'success': False,
            'message': 'No se encontró registro de participación en esta evaluación'
        }, status=404)
        
    except Exception as e:
        return Response({
            'success': False,
            'message': f'Error al obtener resultados: {str(e)}'
        }, status=500)
        
        
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_participantes_evaluacion(request, pk):
    """
    Obtiene todos los participantes de una evaluación específica.
    """
    try:
        evaluacion = get_object_or_404(Evaluacion, pk=pk)
        
        # Verificar permisos
        user = request.user
        is_creador = (evaluacion.creador == user)
        is_staff = user.is_staff or user.is_superuser
        is_docente = hasattr(user, 'profile') and getattr(user.profile, 'rol', '') == 'docente'
        
        if not (is_creador or is_staff or is_docente):
            return Response({
                'success': False,
                'message': 'No tiene permisos para ver los participantes'
            }, status=403)
        
        # Obtener participantes
        participaciones = EstudianteEvaluacion.objects.filter(
            evaluacion=evaluacion
        ).select_related('estudiante')
        
        # Añadir log para debuggear
        print(f"\n=== Debug Participaciones Evaluación {pk} ===")
        print(f"Total participaciones encontradas: {participaciones.count()}")
        for p in participaciones:
            print(f"""
Estudiante: {p.estudiante.username}
Estado: {p.estado}
Ingreso: {p.fecha_inicio}
Progreso: {p.progreso}%
Puntaje: {p.puntaje}
---""")
        
        # Formatear datos
        participantes = []
        for participacion in participaciones:
            try:
                estudiante = participacion.estudiante
                estudiante_nombre = estudiante.username
                
                # Intentar obtener el nombre completo del perfil si existe
                try:
                    if hasattr(estudiante, 'profile'):
                        perfil = estudiante.profile
                        if hasattr(perfil, 'nombres') and hasattr(perfil, 'apellidos'):
                            estudiante_nombre = f"{perfil.nombres} {perfil.apellidos}"
                except:
                    pass
                
                # Log detallado de cada participante procesado
                print(f"Procesando participante: {estudiante_nombre}")
                print(f"Estado actual: {participacion.estado}")
                
                participantes.append({
                    'id': participacion.id,
                    'estudiante_id': estudiante.id,
                    'estudiante_nombre': estudiante_nombre,
                    'email': estudiante.email,
                    'estado': participacion.estado,
                    'progreso': participacion.progreso,
                    'puntaje': participacion.puntaje,
                    'fecha_inicio': participacion.fecha_inicio.isoformat() if participacion.fecha_inicio else None,
                    'fecha_fin': participacion.fecha_fin.isoformat() if participacion.fecha_fin else None
                })
            except Exception as e:
                print(f"Error al procesar participante: {e}")
        
        print(f"=== Fin Debug Participaciones ===\n")
        return Response(participantes)
        
    except Exception as e:
        print(f"Error general en get_participantes_evaluacion: {str(e)}")
        return Response({
            'success': False,
            'message': f'Error al obtener participantes: {str(e)}'
        }, status=500)
        
        
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def ajustar_puntaje(request, pk):
    """Endpoint para ajustar el puntaje de un estudiante en una evaluación"""
    try:
        evaluacion = get_object_or_404(Evaluacion, pk=pk)
        estudiante_id = request.data.get('estudiante_id')
        ajuste = request.data.get('ajuste')
        motivo = request.data.get('motivo', '')
        
        if not estudiante_id or ajuste is None:
            return Response({
                'success': False,
                'message': 'Datos incompletos'
            }, status=400)
            
        # Verificar permisos (solo docente o admin)
        user = request.user
        is_admin = user.is_superuser or (hasattr(user, 'profile') and user.profile.rol == 'admin')
        is_docente = hasattr(user, 'profile') and user.profile.rol == 'docente'
        is_creador = evaluacion.creador == user
        
        if not (is_admin or is_docente or is_creador):
            return Response({
                'success': False,
                'message': 'No tiene permisos para realizar esta acción'
            }, status=403)
        
        # Buscar la participación del estudiante
        try:
            estudiante = User.objects.get(id=estudiante_id)
            participacion = EstudianteEvaluacion.objects.get(
                evaluacion=evaluacion,
                estudiante=estudiante
            )
            
            # Guardar el puntaje anterior para el registro
            puntaje_anterior = participacion.puntaje or 0
            
            # Aplicar el ajuste
            nuevo_puntaje = puntaje_anterior + float(ajuste)
            participacion.puntaje = nuevo_puntaje
            participacion.ajustes_puntaje = (participacion.ajustes_puntaje or 0) + float(ajuste)
            participacion.save()
            
            # Registrar el ajuste en el historial
            AjustePuntaje.objects.create(
                estudiante_evaluacion=participacion,
                docente=user,
                puntaje_anterior=puntaje_anterior,
                ajuste=float(ajuste),
                puntaje_nuevo=nuevo_puntaje,
                motivo=motivo
            )
            
            return Response({
                'success': True,
                'message': 'Puntaje ajustado correctamente',
                'puntaje_anterior': puntaje_anterior,
                'ajuste': ajuste,
                'puntaje_nuevo': nuevo_puntaje
            })
            
        except User.DoesNotExist:
            return Response({
                'success': False,
                'message': 'Estudiante no encontrado'
            }, status=404)
        except EstudianteEvaluacion.DoesNotExist:
            return Response({
                'success': False,
                'message': 'El estudiante no está participando en esta evaluación'
            }, status=404)
            
    except Exception as e:
        return Response({
            'success': False,
            'message': f'Error al ajustar puntaje: {str(e)}'
        }, status=500)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def expulsar_estudiante(request, pk):
    """Endpoint para expulsar a un estudiante de una evaluación"""
    try:
        evaluacion = get_object_or_404(Evaluacion, pk=pk)
        estudiante_id = request.data.get('estudiante_id')
        
        if not estudiante_id:
            return Response({
                'success': False,
                'message': 'ID de estudiante no proporcionado'
            }, status=400)
            
        # Verificar permisos (solo docente o admin)
        user = request.user
        is_admin = user.is_superuser or (hasattr(user, 'profile') and user.profile.rol == 'admin')
        is_docente = hasattr(user, 'profile') and user.profile.rol == 'docente'
        is_creador = evaluacion.creador == user
        
        if not (is_admin or is_docente or is_creador):
            return Response({
                'success': False,
                'message': 'No tiene permisos para realizar esta acción'
            }, status=403)
        
        # Buscar la participación del estudiante
        try:
            estudiante = User.objects.get(id=estudiante_id)
            participacion = EstudianteEvaluacion.objects.get(
                evaluacion=evaluacion,
                estudiante=estudiante
            )
            
            # Cambiar estado a expulsado
            participacion.estado = 'expulsado'
            participacion.fecha_fin = timezone.now()
            participacion.save()
            
            return Response({
                'success': True,
                'message': f'Estudiante {estudiante.username} expulsado correctamente'
            })
            
        except User.DoesNotExist:
            return Response({
                'success': False,
                'message': 'Estudiante no encontrado'
            }, status=404)
        except EstudianteEvaluacion.DoesNotExist:
            return Response({
                'success': False,
                'message': 'El estudiante no está participando en esta evaluación'
            }, status=404)
            
    except Exception as e:
        return Response({
            'success': False,
            'message': f'Error al expulsar estudiante: {str(e)}'
        }, status=500)
        
        

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def obtener_historial_evaluaciones(request):
    """
    Obtiene el historial de evaluaciones de un estudiante
    """
    try:
        estudiante_id = request.query_params.get('estudiante_id')
        if not estudiante_id:
            estudiante_id = request.user.id
            
        # Obtener historial desde la tabla de historial
        historiales = HistorialEvaluacion.objects.filter(
            estudiante_id=estudiante_id
        ).order_by('-fecha_fin')
        
        # Preparar respuesta
        resultados = []
        
        for historial in historiales:
            # Preparar datos de respuestas con manejo defensivo
            respuestas_data = []
            
            # Obtener respuestas del historial de manera segura
            detalles = historial.detalles or {}
            respuestas_historial = detalles.get('respuestas', [])
            
            for respuesta in respuestas_historial:
                try:
                    # Manejar diferentes formatos de datos de manera defensiva
                    respuestas_data.append({
                        'ejercicio_id': respuesta.get('ejercicio_id'),
                        'ejercicio_titulo': respuesta.get('ejercicio_titulo', f"Ejercicio {respuesta.get('ejercicio_id', 'N/A')}"),
                        'puntaje_obtenido': respuesta.get('puntaje_obtenido', 0),
                        'puntaje_maximo': respuesta.get('puntaje_maximo', respuesta.get('ejercicio_puntaje', 30)),  # Fallback a nombres anteriores
                        'es_correcta': respuesta.get('es_correcta', False),
                        'codigo': respuesta.get('codigo', ''),
                        'resultados': respuesta.get('resultados', []),
                        'fecha_respuesta': respuesta.get('fecha_respuesta', '')
                    })
                except Exception as e:
                    print(f"Error procesando respuesta individual: {str(e)}")
                    # Continuar con la siguiente respuesta en caso de error
                    continue
            
            # Calcular puntaje sobre 10 de manera segura
            puntaje_sobre_10 = 0
            if historial.evaluacion_puntaje_total and historial.evaluacion_puntaje_total > 0:
                puntaje_sobre_10 = (historial.puntaje_total / historial.evaluacion_puntaje_total) * 10
            
            # Crear objeto para la evaluación
            eval_data = {
                'id': historial.id,  # ID del historial
                'evaluacion_id': historial.evaluacion_id,  # ID de la evaluación original
                'titulo': historial.evaluacion_titulo or f"Evaluación {historial.evaluacion_id}",
                'fecha_inicio': historial.fecha_inicio.isoformat() if historial.fecha_inicio else None,
                'fecha_fin': historial.fecha_fin.isoformat() if historial.fecha_fin else None,
                'puntaje': historial.puntaje_total or 0,
                'puntaje_sobre_10': round(puntaje_sobre_10, 2),
                'color_clase': get_color_clase(puntaje_sobre_10),
                'respuestas': respuestas_data,
                'tiempo_total': str(historial.tiempo_total) if historial.tiempo_total else None,               
                'tiempo_total_ms': historial.tiempo_total_ms or 0,
                'detalles_adicionales': historial.detalles or {},
                'evaluacion_activa': getattr(historial, 'evaluacion_activa', True)
            }
            
            resultados.append(eval_data)
        
        return Response({
            'success': True,
            'historial': resultados
        })
    
    except Exception as e:
        print(f"Error al obtener historial: {str(e)}")
        import traceback
        traceback.print_exc()
        return Response({
            'success': False,
            'message': f'Error al obtener historial: {str(e)}'
        }, status=500)
        
        
   
   

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def obtener_evaluacion_historial(request, historial_id):
    """
    Obtiene una evaluación específica del historial para visualización
    """
    try:
        historial = HistorialEvaluacion.objects.get(
            id=historial_id,
            estudiante_id=request.user.id
        )
        
        # CORREGIDO: Construir datos de evaluación con ejercicios completos
        evaluacion_data = {
            'id': historial.evaluacion_id,
            'titulo': historial.evaluacion_titulo,
            'descripcion': historial.evaluacion_descripcion,
            'fecha_inicio': historial.fecha_inicio.isoformat() if historial.fecha_inicio else None,
            'fecha_fin': historial.fecha_fin.isoformat() if historial.fecha_fin else None,
            'puntaje_total': historial.puntaje_total,
            'tiempo_total_ms': historial.tiempo_total_ms,
            'ejercicios': []
        }
        
        # CORREGIDO: Extraer ejercicios desde detalles con prioridad
        ejercicios_desde_detalles = []
        
        if historial.detalles and isinstance(historial.detalles, dict):
            # 1. PRIORIDAD: Ejercicios completos desde detalles.ejercicios
            if 'ejercicios' in historial.detalles and historial.detalles['ejercicios']:
                ejercicios_desde_detalles = historial.detalles['ejercicios']
                print(f"DEBUG: Encontrados {len(ejercicios_desde_detalles)} ejercicios en detalles.ejercicios")
            
            # 2. FALLBACK: Construir desde detalles.respuestas
            elif 'respuestas' in historial.detalles and historial.detalles['respuestas']:
                print(f"DEBUG: Construyendo ejercicios desde {len(historial.detalles['respuestas'])} respuestas")
                
                for respuesta in historial.detalles['respuestas']:
                    ejercicio = {
                        'id': respuesta.get('ejercicio_id'),
                        'titulo': respuesta.get('ejercicio_titulo', f"Ejercicio {respuesta.get('ejercicio_id')}"),
                        'descripcion': respuesta.get('ejercicio_descripcion', ''),
                        'puntaje': respuesta.get('puntaje_maximo', 30),
                        'codigo': respuesta.get('codigo', ''),
                        'template': respuesta.get('codigo', ''),  # Para compatibilidad
                        'language_id': respuesta.get('language_id', 71),  # IMPORTANTE
                        'es_correcta': respuesta.get('es_correcta', False),
                        'puntaje_obtenido': respuesta.get('puntaje_obtenido', 0),
                        'puntaje_maximo': respuesta.get('puntaje_maximo', 30),
                        'resultados': respuesta.get('resultados', ''),
                        'stderr': respuesta.get('stderr', ''),
                        
                        # Campos por defecto
                        'contenido': {},
                        'restricciones': '',
                        'formato_salida': '',
                        'ejemplos': [],
                        'pista': '',
                        'etiquetas': [],
                        'credito': '',
                        'tests_avanzados': None,
                        'templates_por_lenguaje': {},
                    }
                    ejercicios_desde_detalles.append(ejercicio)
        
        # Si se encontraron ejercicios en detalles, usarlos
        if ejercicios_desde_detalles:
            evaluacion_data['ejercicios'] = ejercicios_desde_detalles
            print(f"DEBUG: Usando {len(ejercicios_desde_detalles)} ejercicios desde detalles")
        
        # 3. FALLBACK FINAL: Intentar recuperar desde la evaluación original
        else:
            print("DEBUG: No se encontraron ejercicios en detalles, intentando desde evaluación original")
            try:
                evaluacion_original = Evaluacion.objects.get(id=historial.evaluacion_id)
                ejercicios_originales = list(evaluacion_original.ejercicios.all())
                
                for ejercicio in ejercicios_originales:
                    contenido = ejercicio.contenido or {}
                    if isinstance(contenido, str):
                        try:
                            contenido = json.loads(contenido)
                        except:
                            contenido = {}
                    
                    evaluacion_data['ejercicios'].append({
                        'id': ejercicio.id,
                        'titulo': ejercicio.titulo,
                        'descripcion': ejercicio.descripcion,
                        'puntaje': ejercicio.puntaje,
                        'codigo': '',  # No tenemos el código del estudiante
                        'template': contenido.get('template', ''),
                        'language_id': 71,  # Por defecto
                        'es_correcta': False,
                        'puntaje_obtenido': 0,
                        'puntaje_maximo': ejercicio.puntaje,
                        'resultados': '',
                        'stderr': '',
                        'contenido': contenido,
                        'restricciones': contenido.get('restricciones', ''),
                        'formato_salida': contenido.get('formato_salida', ''),
                        'ejemplos': contenido.get('ejemplos', []),
                        'pista': contenido.get('pista', ''),
                        'etiquetas': contenido.get('etiquetas', []),
                        'credito': contenido.get('credito', ''),
                        'tests_avanzados': contenido.get('tests_avanzados'),
                        'templates_por_lenguaje': contenido.get('templates_por_lenguaje', {}),
                    })
                
                print(f"DEBUG: Añadidos {len(ejercicios_originales)} ejercicios desde evaluación original")
                
            except Evaluacion.DoesNotExist:
                print("DEBUG: Evaluación original no encontrada")
        
        print(f"DEBUG: Retornando {len(evaluacion_data['ejercicios'])} ejercicios en historial ID {historial_id}")
        
        return Response({
            'success': True,
            'evaluacion': evaluacion_data,
            'tiempo_total': str(historial.tiempo_total) if historial.tiempo_total else '0:00:00',
            'es_historial': True
        })
    
    except HistorialEvaluacion.DoesNotExist:
        return Response({
            'success': False,
            'message': 'Historial no encontrado'
        }, status=404)
    except Exception as e:
        logger.error(f"Error al obtener evaluación del historial: {str(e)}")
        return Response({
            'success': False,
            'message': f'Error al obtener evaluación del historial: {str(e)}'
        }, status=500)
   
        
        

def get_color_clase(score):
    if score >= 9:
        return 'excellent'
    elif score >= 7:
        return 'good'
    elif score >= 5:
        return 'average'
    else:
        return 'poor'
 
        


def guardar_evaluacion_en_historial(estudiante_evaluacion):
    """
    Guarda una evaluación finalizada en el historial con datos mejorados
    """
    try:
        print(f"DEBUG: Guardando evaluación {estudiante_evaluacion.evaluacion.id} en historial")
        
        # Verificar si ya existe un registro
        historial_existente = HistorialEvaluacion.objects.filter(
            estudiante_id=estudiante_evaluacion.estudiante.id,
            evaluacion_id=estudiante_evaluacion.evaluacion.id
        ).first()
        
        if historial_existente:
            print(f"DEBUG: Historial ya existe para evaluación {estudiante_evaluacion.evaluacion.id}, estudiante {estudiante_evaluacion.estudiante.id}")
            return historial_existente
        
        evaluacion = estudiante_evaluacion.evaluacion
        estudiante = estudiante_evaluacion.estudiante
        
        # CORREGIDO: Función helper para obtener nombres
        def get_full_name(user):
            try:
                if hasattr(user, 'profile') and user.profile:
                    nombres = getattr(user.profile, 'nombres', '')
                    apellidos = getattr(user.profile, 'apellidos', '')
                    full_name = f"{nombres} {apellidos}".strip()
                    return full_name if full_name else user.username
                else:
                    return user.username
            except:
                return user.username
        
        # CORREGIDO: Obtener todas las respuestas con .select_related() para optimizar
        respuestas = RespuestaEjercicio.objects.filter(
            estudiante_evaluacion=estudiante_evaluacion
        ).select_related('ejercicio').order_by('ejercicio__id')
        
        print(f"DEBUG: Procesando {respuestas.count()} respuestas")
        
        # Convertir respuestas a formato JSON con language_id
        respuestas_json = []
        ejercicios_json = []
        
        for respuesta in respuestas:
            ejercicio = respuesta.ejercicio
            
            # CORREGIDO: Manejar el campo respuesta que puede ser string o dict
            respuesta_data = respuesta.respuesta
            codigo = ''
            resultados = ''
            stderr = ''
            
            if isinstance(respuesta_data, dict):
                codigo = respuesta_data.get('codigo', '')
                resultados = respuesta_data.get('resultados', '')
                stderr = respuesta_data.get('stderr', '')
            elif isinstance(respuesta_data, str):
                try:
                    parsed = json.loads(respuesta_data)
                    if isinstance(parsed, dict):
                        codigo = parsed.get('codigo', '')
                        resultados = parsed.get('resultados', '')
                        stderr = parsed.get('stderr', '')
                    else:
                        codigo = respuesta_data
                except json.JSONDecodeError:
                    codigo = respuesta_data
            
            # CORREGIDO: Obtener language_id del modelo o del JSON
            language_id = getattr(respuesta, 'language_id', 71)
            
            # Si no está en el modelo, intentar obtenerlo del JSON
            if language_id == 71 and isinstance(respuesta_data, dict) and 'language_id' in respuesta_data:
                language_id = respuesta_data.get('language_id', 71)
            
            print(f"DEBUG: Respuesta para ejercicio {ejercicio.id}: language_id={language_id}, código={len(codigo)} chars")
            
            # Respuesta para el historial
            respuesta_json = {
                'ejercicio_id': ejercicio.id,
                'ejercicio_titulo': ejercicio.titulo,
                'ejercicio_descripcion': ejercicio.descripcion,
                'es_correcta': respuesta.es_correcta,
                'puntaje_obtenido': float(respuesta.puntaje_obtenido),
                'puntaje_maximo': float(ejercicio.puntaje),
                'codigo': codigo,
                'resultados': resultados,
                'stderr': stderr,
                'language_id': language_id,  # IMPORTANTE: Guardar language_id
                'fecha_respuesta': respuesta.fecha_respuesta.isoformat() if respuesta.fecha_respuesta else None
            }
            respuestas_json.append(respuesta_json)
            
            # CORREGIDO: Ejercicio completo para modo historial
            contenido_ejercicio = ejercicio.contenido or {}
            if isinstance(contenido_ejercicio, str):
                try:
                    contenido_ejercicio = json.loads(contenido_ejercicio)
                except json.JSONDecodeError:
                    contenido_ejercicio = {}
            
            ejercicio_json = {
                'id': ejercicio.id,
                'titulo': ejercicio.titulo,
                'descripcion': ejercicio.descripcion,
                'puntaje': float(ejercicio.puntaje),
                'dificultad': ejercicio.dificultad,
                'codigo': codigo,  # El código que escribió el estudiante
                'template': codigo,  # Para compatibilidad
                'language_id': language_id,  # IMPORTANTE: Para el modo historial
                'es_correcta': respuesta.es_correcta,
                'puntaje_obtenido': float(respuesta.puntaje_obtenido),
                'puntaje_maximo': float(ejercicio.puntaje),
                'resultados': resultados,
                'stderr': stderr,
                
                # Contenido original del ejercicio
                'contenido': contenido_ejercicio,
                'restricciones': contenido_ejercicio.get('restricciones', ''),
                'formato_salida': contenido_ejercicio.get('formato_salida', ''),
                'ejemplos': contenido_ejercicio.get('ejemplos', []),
                'pista': contenido_ejercicio.get('pista', ''),
                'etiquetas': contenido_ejercicio.get('etiquetas', []),
                'credito': contenido_ejercicio.get('credito', ''),
                'tests_avanzados': contenido_ejercicio.get('tests_avanzados'),
                'templates_por_lenguaje': contenido_ejercicio.get('templates_por_lenguaje', {}),
            }
            ejercicios_json.append(ejercicio_json)
        
        # CORREGIDO: Calcular estadísticas correctas
        total_ejercicios = len(ejercicios_json)
        ejercicios_correctos = len([r for r in respuestas_json if r['es_correcta']])
        puntaje_total = sum([r['puntaje_obtenido'] for r in respuestas_json])
        puntaje_maximo = sum([r['puntaje_maximo'] for r in respuestas_json])
        porcentaje = (puntaje_total / puntaje_maximo * 100) if puntaje_maximo > 0 else 0
        puntaje_sobre_10 = (puntaje_total / puntaje_maximo * 10) if puntaje_maximo > 0 else 0
        
        # CORREGIDO: Calcular tiempo correctamente
        tiempo_total_ms = estudiante_evaluacion.tiempo_total_ms
        if tiempo_total_ms:
            print(f"🕐 Guardando historial - tiempo_total_ms desde BD: {tiempo_total_ms}")
            tiempo_total = timezone.timedelta(milliseconds=tiempo_total_ms)
            print(f"✅ Usando tiempo desde BD: {tiempo_total_ms}ms ({tiempo_total_ms/1000:.1f}s)")
        elif estudiante_evaluacion.fecha_inicio and estudiante_evaluacion.fecha_fin:
            tiempo_total = estudiante_evaluacion.fecha_fin - estudiante_evaluacion.fecha_inicio
            tiempo_total_ms = int(tiempo_total.total_seconds() * 1000)
            print(f"🕐 Calculado tiempo desde fechas: {tiempo_total_ms}ms")
        else:
            tiempo_total = timezone.timedelta(0)
            tiempo_total_ms = 0
            print("⚠️ No se pudo calcular tiempo total")
        
        # CORREGIDO: Obtener nombres usando la función helper
        estudiante_nombre = get_full_name(estudiante)
        docente_nombre = get_full_name(evaluacion.creador)
        
        # Crear el registro de historial
        historial = HistorialEvaluacion.objects.create(
            estudiante_id=estudiante.id,
            estudiante_nombre=estudiante_nombre,
            estudiante_email=estudiante.email,
            
            evaluacion_id=evaluacion.id,
            evaluacion_titulo=evaluacion.titulo,
            evaluacion_descripcion=evaluacion.descripcion,
            evaluacion_puntaje_total=evaluacion.ejercicios.aggregate(models.Sum('puntaje'))['puntaje__sum'] or 0,
            evaluacion_codigo_acceso=evaluacion.codigo_acceso,
            
            docente_id=evaluacion.creador.id,
            docente_nombre=docente_nombre,
            
            fecha_inicio=estudiante_evaluacion.fecha_inicio,
            fecha_fin=estudiante_evaluacion.fecha_fin,
            
            puntaje_total=puntaje_total,
            porcentaje_aprobacion=porcentaje,
            tiempo_total=tiempo_total,
            tiempo_total_ms=tiempo_total_ms,
            
            # CORREGIDO: Detalles completos con ejercicios
            detalles={
                'respuestas': respuestas_json,
                'ejercicios': ejercicios_json,  # IMPORTANTE: Incluir ejercicios completos
                'estadisticas': {
                    'total_ejercicios': total_ejercicios,
                    'ejercicios_correctos': ejercicios_correctos,
                    'puntaje_total': puntaje_total,
                    'puntaje_maximo': puntaje_maximo,
                    'puntaje_sobre_10': round(puntaje_sobre_10, 2),
                    'porcentaje': round(porcentaje, 2),
                    'color_clase': get_color_clase(puntaje_sobre_10)
                },
                'evaluacion': {
                    'titulo': evaluacion.titulo,
                    'descripcion': evaluacion.descripcion,
                    'fecha_creacion': evaluacion.fecha_creacion.isoformat() if evaluacion.fecha_creacion else None,
                    'duracion_minutos': evaluacion.duracion_minutos,
                    'permitir_revision': evaluacion.permitir_revision,
                    'mostrar_resultado': evaluacion.mostrar_resultado,
                }
            }
        )
        
        print(f"DEBUG: Historial guardado exitosamente. ID: {historial.id}")
        print(f"DEBUG: Guardados {len(ejercicios_json)} ejercicios en el historial")
        
        return historial
        
    except Exception as e:
        print(f"❌ Error guardando en historial: {str(e)}")
        import traceback
        traceback.print_exc()
        return None



        
        
        
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def debug_historial(request, evaluation_id):
    """
    Endpoint de debug para verificar historial de una evaluación
    """
    try:
        historial_count = HistorialEvaluacion.objects.filter(evaluacion_id=evaluation_id).count()
        historiales = HistorialEvaluacion.objects.filter(evaluacion_id=evaluation_id).values()
        
        return Response({
            'evaluation_id': evaluation_id,
            'historial_count': historial_count,
            'historiales': list(historiales)
        })
    except Exception as e:
        return Response({
            'error': str(e)
        }, status=500)
        
 
# Resultados completos de evaluación        

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_evaluacion_resultados_completos(request, pk):
    """
    Obtiene los resultados completos de una evaluación para un estudiante,
    incluyendo todos los datos necesarios para la pantalla de resultados.
    """
    try:
        estudiante_id = request.query_params.get('estudiante_id')
        if not estudiante_id:
            estudiante_id = request.user.id
            
        evaluacion = get_object_or_404(Evaluacion, pk=pk)
        
        # Log adicional para depuración
        print(f"DEBUG: Obteniendo resultados completos para evaluación {pk}, estudiante {estudiante_id}")
        
        # Buscar participación en evaluación
        participacion = get_object_or_404(
            EstudianteEvaluacion, 
            estudiante_id=estudiante_id,
            evaluacion=evaluacion
        )
        
        print(f"DEBUG: Participación encontrada, estado: {participacion.estado}, puntaje: {participacion.puntaje}")
        
        # Obtener todas las respuestas
        respuestas = RespuestaEjercicio.objects.filter(
            estudiante_evaluacion=participacion
        ).select_related('ejercicio')
        
        print(f"DEBUG: Respuestas obtenidas: {respuestas.count()}")
        
        # Preparar respuestas detalladas con toda la información necesaria
        respuestas_detalle = []
        for respuesta in respuestas:
            ejercicio = respuesta.ejercicio
            
            # Extraer código, resultado, stderr, etc.
            codigo = ""
            resultados = []
            stderr = ""
            
            if isinstance(respuesta.respuesta, dict):
                codigo = respuesta.respuesta.get('codigo', '')
                resultados = respuesta.respuesta.get('resultados', [])
                stderr = respuesta.respuesta.get('stderr', '')
            elif isinstance(respuesta.respuesta, str):
                try:
                    respuesta_dict = json.loads(respuesta.respuesta)
                    codigo = respuesta_dict.get('codigo', '')
                    resultados = respuesta_dict.get('resultados', [])
                    stderr = respuesta_dict.get('stderr', '')
                except:
                    codigo = respuesta.respuesta
            
            # Crear objeto de respuesta detallado
            respuestas_detalle.append({
                'ejercicio_id': ejercicio.id,
                'ejercicio_titulo': ejercicio.titulo,
                'ejercicio_descripcion': ejercicio.descripcion,
                'puntaje_obtenido': respuesta.puntaje_obtenido,
                'puntaje_maximo': ejercicio.puntaje,
                'es_correcta': respuesta.es_correcta,
                'codigo': codigo,
                'resultados': resultados,
                'stderr': stderr,
                'fecha_respuesta': respuesta.fecha_respuesta.isoformat()
            })
        
        # Si no hay respuestas, intentar obtenerlas de otras fuentes
        if not respuestas_detalle:
            print("DEBUG: No hay respuestas en BD, buscando en historial")
            try:
                # Intentar obtener del historial
                historial = HistorialEvaluacion.objects.filter(
                    estudiante_id=estudiante_id,
                    evaluacion_id=evaluacion.id
                ).first()
                
                if historial and historial.detalles and 'respuestas' in historial.detalles:
                    print(f"DEBUG: Encontradas {len(historial.detalles['respuestas'])} respuestas en historial")
                    respuestas_detalle = historial.detalles['respuestas']
            except Exception as e:
                print(f"DEBUG: Error al buscar en historial: {str(e)}")
                
        # Si aún no hay respuestas, usar los ejercicios originales como último recurso
        if not respuestas_detalle:
            print("DEBUG: Buscando ejercicios originales de la evaluación")
            # Al menos incluir los ejercicios de la evaluación
            ejercicios = evaluacion.ejercicios.all()
            print(f"DEBUG: Encontrados {ejercicios.count()} ejercicios originales")
            
            for ejercicio in ejercicios:
                respuestas_detalle.append({
                    'ejercicio_id': ejercicio.id,
                    'ejercicio_titulo': ejercicio.titulo,
                    'ejercicio_descripcion': ejercicio.descripcion,
                    'puntaje_obtenido': 0,
                    'puntaje_maximo': ejercicio.puntaje,
                    'es_correcta': False,
                    'codigo': '',
                    'resultados': [],
                    'stderr': '',
                    'fecha_respuesta': timezone.now().isoformat()
                })
        
        # Calcular estadísticas
        puntaje_total = participacion.puntaje or 0
        puntaje_maximo = sum(e.puntaje for e in evaluacion.ejercicios.all())
        
        # Calcular puntaje sobre 10
        puntaje_sobre_10 = 0
        if puntaje_maximo > 0:
            puntaje_sobre_10 = (puntaje_total / puntaje_maximo) * 10
        
        # Determinar color
        def get_color_clase(score):
            if score >= 9: return 'excellent'
            if score >= 7: return 'good'
            if score >= 5: return 'average'
            return 'poor'
        
        color_clase = get_color_clase(puntaje_sobre_10)
        
        print(f"DEBUG: Puntuación calculada: {puntaje_total}/{puntaje_maximo} ({puntaje_sobre_10}/10)")
        print(f"DEBUG: Retornando {len(respuestas_detalle)} respuestas detalladas")
        
        # Datos completos para la vista
        return Response({
            'success': True,
            'evaluation': {
                'id': evaluacion.id,
                'titulo': evaluacion.titulo,
                'descripcion': evaluacion.descripcion,
                'fecha_inicio': participacion.fecha_inicio.isoformat() if participacion.fecha_inicio else None,
                'fecha_fin': participacion.fecha_fin.isoformat() if participacion.fecha_fin else None,
                'puntaje_total': puntaje_total,
                'puntaje_maximo': puntaje_maximo,
                'puntaje_sobre_10': puntaje_sobre_10,
                'color_clase': color_clase,
                'formattedScore': f"{puntaje_sobre_10:.1f}/10",
                'formattedScoreDisplay': 
                    "¡Excelente!" if puntaje_sobre_10 >= 9 else
                    "¡Muy bien!" if puntaje_sobre_10 >= 7 else
                    "Regular" if puntaje_sobre_10 >= 5 else 
                    "Necesita mejorar",
                'showAchievement': puntaje_sobre_10 >= 9,
                'porcentaje': round((puntaje_total / puntaje_maximo) * 100, 2) if puntaje_maximo > 0 else 0,
                'estado': participacion.estado,
                'tiempo_total': str(participacion.fecha_fin - participacion.fecha_inicio) if participacion.fecha_fin and participacion.fecha_inicio else None,
                'respuestas': respuestas_detalle,
                'ejercicios_count': evaluacion.ejercicios.count(),
                'completados_count': len([r for r in respuestas_detalle if r['es_correcta']])
            }
        })
        
    except EstudianteEvaluacion.DoesNotExist:
        return Response({
            'success': False,
            'message': 'No se encontró registro de participación en esta evaluación'
        }, status=404)
        
    except Exception as e:
        print(f"DEBUG: Error en get_evaluacion_resultados_completos: {str(e)}")
        import traceback
        print(traceback.format_exc())
        return Response({
            'success': False,
            'message': f'Error al obtener resultados detallados: {str(e)}'
        }, status=500)
        
        
@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def eliminar_evaluacion_historial(request, historial_id):
    """
    Elimina una evaluación específica del historial
    """
    try:
        # Verificar permisos - solo docentes o admin
        user = request.user
        is_admin = user.is_superuser or (hasattr(user, 'profile') and user.profile.rol == 'admin')
        is_docente = hasattr(user, 'profile') and user.profile.rol == 'docente'
        
        if not (is_admin or is_docente):
            return Response({
                'success': False,
                'message': 'No tiene permisos para realizar esta acción'
            }, status=403)
        
        # Buscar la evaluación en el historial
        historial = get_object_or_404(HistorialEvaluacion, id=historial_id)
        
        # Verificar que el docente sea el creador original (solo si no es admin)
        if not is_admin and historial.docente_id != user.id:
            return Response({
                'success': False,
                'message': 'Solo puedes eliminar evaluaciones que hayas creado'
            }, status=403)
        
        # Eliminar del historial
        evaluacion_titulo = historial.evaluacion_titulo
        historial.delete()
        
        logger.info(f"Evaluación '{evaluacion_titulo}' eliminada del historial por {user.username}")
        
        return Response({
            'success': True,
            'message': f'Evaluación "{evaluacion_titulo}" eliminada del historial correctamente'
        })
        
    except Exception as e:
        logger.error(f"Error al eliminar evaluación del historial: {str(e)}")
        return Response({
            'success': False,
            'message': f'Error al eliminar evaluación del historial: {str(e)}'
        }, status=500)
        
        
        
# evaluations/views.py - AGREGAR al final del archivo

@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated, (IsAdmin | IsDocente)])
def platform_settings_view(request):
    """
    Vista para manejar configuraciones de la plataforma
    Solo admins y docentes pueden modificar configuraciones
    """
    from .models import PlatformSettings
    
    if request.method == 'GET':
        try:
            # Obtener todas las configuraciones importantes
            settings = {
                'language_selector_enabled': PlatformSettings.get_language_selector_enabled(),
                'default_language_id': PlatformSettings.get_setting('default_language_id', 71),
            }
            
            return Response({
                'success': True,
                'settings': settings
            })
        except Exception as e:
            logger.error(f"Error al obtener configuraciones: {str(e)}")
            return Response({
                'success': False,
                'error': 'Error al obtener configuraciones'
            }, status=500)
    
    elif request.method == 'POST':
        try:
            setting_key = request.data.get('key')
            setting_value = request.data.get('value')
            
            if not setting_key:
                return Response({
                    'success': False,
                    'error': 'Clave de configuración requerida'
                }, status=400)
            
            # Validar configuraciones permitidas
            allowed_settings = [
                'language_selector_enabled',
                'default_language_id'
            ]
            
            if setting_key not in allowed_settings:
                return Response({
                    'success': False,
                    'error': f'Configuración {setting_key} no permitida'
                }, status=400)
            
            # Guardar configuración
            if setting_key == 'language_selector_enabled':
                PlatformSettings.set_language_selector_enabled(bool(setting_value))
            else:
                PlatformSettings.set_setting(setting_key, setting_value)
            
            logger.info(f"Configuración actualizada por {request.user.username}: {setting_key} = {setting_value}")
            
            return Response({
                'success': True,
                'message': f'Configuración {setting_key} actualizada correctamente'
            })
            
        except Exception as e:
            logger.error(f"Error al actualizar configuración: {str(e)}")
            return Response({
                'success': False,
                'error': f'Error al actualizar configuración: {str(e)}'
            }, status=500)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_language_selector_config(request):
    """
    Vista específica para obtener la configuración del selector de lenguajes
    Disponible para todos los usuarios autenticados
    """
    from .models import PlatformSettings
    
    try:
        enabled = PlatformSettings.get_language_selector_enabled()
        default_language = PlatformSettings.get_setting('default_language_id', 71)
        
        return Response({
            'success': True,
            'language_selector_enabled': enabled,
            'default_language_id': default_language
        })
    except Exception as e:
        logger.error(f"Error al obtener configuración del selector: {str(e)}")
        return Response({
            'success': False,
            'error': 'Error al obtener configuración',
            'language_selector_enabled': False,  # Por seguridad, deshabilitado por defecto
            'default_language_id': 71
        }, status=500)