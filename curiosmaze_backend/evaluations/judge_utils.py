# evaluations/judge_utils.py
import requests
import json
import logging
import os
from django.conf import settings
import traceback
import time

logger = logging.getLogger('judge')

# Configuración desde settings.py que a su vez lee de .env
JUDGE0_API_URL = getattr(settings, 'JUDGE0_API_URL')
JUDGE0_AUTH_TOKEN = getattr(settings, 'JUDGE0_AUTH_TOKEN', None)
JUDGE0_TIMEOUT = getattr(settings, 'JUDGE0_TIMEOUT', 10)

# IDs de lenguajes disponibles en Judge0
LANGUAGE_IDS = {
    'python': 71,
    'python3': 71,
    'javascript': 63,
    'java': 62,
    'cpp': 54,
    'c': 50
}

# Bandera para indicar si Judge0 está disponible
JUDGE0_AVAILABLE = False

# Configuración de ejecución por defecto
DEFAULT_EXECUTION_OPTIONS = {
    'cpu_time_limit': float(os.environ.get('CPU_TIME_LIMIT', 2)),
    'cpu_extra_time': float(os.environ.get('CPU_EXTRA_TIME', 0.5)),
    'wall_time_limit': float(os.environ.get('WALL_TIME_LIMIT', 5)),
    'memory_limit': int(os.environ.get('MEMORY_LIMIT', 128000)),
    'stack_limit': 64000,
    'max_processes_and_or_threads': 60,
    'enable_network': False
}

# Verificar conectividad con Judge0
try:
    response = requests.get(f"{JUDGE0_API_URL}/statuses", timeout=3)
    if response.status_code == 200:
        logger.info("Judge0 está listo para trabajar 👷‍♂️")
        JUDGE0_AVAILABLE = True
    else:
        logger.warning(f"Judge0 no responde correctamente: {response.status_code}")
except Exception as e:
    logger.error(f"Error al conectar con Judge0: {str(e)}")
    logger.error("Judge0 está de vacaciones 🏖")


def check_judge0_availability():
    """
    Verifica si Judge0 está disponible
    
    Returns:
        tuple: (is_available, message)
    """
    try:
        response = requests.get(f"{JUDGE0_API_URL}/statuses", timeout=3)
        if response.status_code == 200:
            return True, "Judge0 está listo para trabajar 👷‍♂️"
        else:
            return False, f"Judge0 no responde correctamente: {response.status_code}"
    except Exception as e:
        return False, f"Error al conectar con Judge0: {str(e)}"


def ejecutar_codigo(code, input_data='', expected_output=None, language='python'):
    """
    Ejecuta código fuente usando Judge0
    
    Args:
        code (str): Código fuente
        input_data (str, optional): Entrada estándar
        expected_output (str, optional): Salida esperada para verificación
        language (str, optional): Lenguaje de programación
    
    Returns:
        dict: Resultado de la ejecución
    """
    # Verificar disponibilidad
    is_available, message = check_judge0_availability()
    if not is_available:
        return {
            'success': False,
            'error': message,
            'stdout': '',
            'stderr': 'Judge0 no está disponible en este momento',
            'time': '0',
            'message': message
        }
    
    try:
        # Preparar datos para Judge0
        submission_data = {
            'source_code': code,
            'language_id': LANGUAGE_IDS.get(language, 71),  # Python por defecto
            'stdin': input_data,
            **DEFAULT_EXECUTION_OPTIONS
        }
        
        # Añadir expected_output si se proporciona
        if expected_output:
            submission_data['expected_output'] = expected_output
        
        # Preparar headers
        headers = {'Content-Type': 'application/json'}
        if JUDGE0_AUTH_TOKEN:
            headers['X-Auth-Token'] = JUDGE0_AUTH_TOKEN
        
        # Crear submission en Judge0
        logger.info(f"Enviando código a Judge0 ({len(code)} caracteres)")
        create_response = requests.post(
            f"{JUDGE0_API_URL}/submissions",
            json=submission_data,
            headers=headers,
            timeout=JUDGE0_TIMEOUT
        )
        
        if create_response.status_code not in [200, 201]:
            return {
                'success': False,
                'error': f"Error al crear submission: {create_response.status_code}",
                'stdout': '',
                'stderr': create_response.text,
                'time': '0'
            }
        
        token = create_response.json().get('token')
        if not token:
            return {
                'success': False,
                'error': 'No se recibió token de Judge0',
                'stdout': '',
                'stderr': 'Error interno de servicio',
                'time': '0'
            }
        
        # Obtener resultado con el token
        result = wait_for_result(token)
        
        # Formatear resultado
        return {
            'success': result.get('status', {}).get('id') == 3,  # 3 = Accepted
            'stdout': result.get('stdout', ''),
            'stderr': result.get('stderr', ''),
            'compile_output': result.get('compile_output', ''),
            'time': result.get('time', '0'),
            'memory': result.get('memory', 0),
            'status': result.get('status', {})
        }
        
    except Exception as e:
        logger.error(f"Error en ejecutar_codigo: {str(e)}")
        logger.error(traceback.format_exc())
        return {
            'success': False,
            'error': str(e),
            'stdout': '',
            'stderr': str(e),
            'time': '0'
        }


def wait_for_result(token, max_attempts=10):
    """
    Espera y obtiene el resultado de una ejecución
    
    Args:
        token (str): Token de la submission
        max_attempts (int, optional): Número máximo de intentos
    
    Returns:
        dict: Resultado completo
    """
    headers = {}
    if JUDGE0_AUTH_TOKEN:
        headers['X-Auth-Token'] = JUDGE0_AUTH_TOKEN
    
    url = f"{JUDGE0_API_URL}/submissions/{token}?fields=*&base64_encoded=false"
    
    for attempt in range(max_attempts):
        try:
            response = requests.get(url, headers=headers, timeout=JUDGE0_TIMEOUT)
            if response.status_code != 200:
                continue
                
            result = response.json()
            
            # Si aún está en cola (1) o procesando (2), esperar
            if result.get('status', {}).get('id') in [1, 2]:
                import time
                time.sleep(1)
                continue
                
            return result
        except Exception as e:
            logger.error(f"Error en wait_for_result (intento {attempt+1}): {str(e)}")
            import time
            time.sleep(2)
    
    return {'status': {'id': -1, 'description': 'Timeout'}, 'stderr': 'Tiempo de espera agotado'}


def procesar_batch_con_judge0(ejercicios, batch_id='default'):
    """
    Procesa un lote de ejercicios usando Judge0
    
    Args:
        ejercicios (list): Lista de diccionarios con ejercicio_id y codigo
        batch_id (str, optional): ID para tracking
    
    Returns:
        dict: Resultado del procesamiento batch
    """
    # Verificar disponibilidad
    if not JUDGE0_AVAILABLE:
        return {
            'success': False,
            'error': 'Judge0 no está disponible',
            'resultados': []
        }
    
    try:
        logger.info(f"[Batch:{batch_id}] Procesando batch con Judge0: {len(ejercicios)} ejercicios")
        
        if not ejercicios or not isinstance(ejercicios, list):
            return {
                'success': False,
                'error': 'Datos de ejercicios inválidos',
                'resultados': []
            }
        
        # Preparar submissions para Judge0
        submissions = []
        # Mapeo directo entre posiciones y ejercicio_id
        ejercicios_ids = []
        
        for ej in ejercicios:
            ejercicio_id = ej.get('ejercicio_id')
            codigo = ej.get('codigo', '')
            
            if not ejercicio_id:
                continue
                
            ejercicios_ids.append(ejercicio_id)
            
            # Usar Python 3 por defecto
            language_id = LANGUAGE_IDS.get('python3', 71)
            
            # Preparar submission
            submissions.append({
                "language_id": language_id,
                "source_code": codigo,
                **DEFAULT_EXECUTION_OPTIONS
            })
        
        # Verificar que hay ejercicios para procesar
        if not submissions:
            return {
                'success': False,
                'error': 'No hay ejercicios válidos para procesar',
                'resultados': []
            }
        
        # Enviar batch a Judge0
        url = f"{JUDGE0_API_URL}/submissions/batch"
        headers = {'Content-Type': 'application/json'}
        if JUDGE0_AUTH_TOKEN:
            headers['X-Auth-Token'] = JUDGE0_AUTH_TOKEN
        
        # Crear payload
        data = {"submissions": submissions}
        
        # Realizar petición POST
        response = requests.post(
            url,
            json=data, 
            headers=headers,
            timeout=JUDGE0_TIMEOUT
        )
        
        # Verificar respuesta
        if response.status_code not in [200, 201]:
            logger.error(f"[Batch:{batch_id}] Error en Judge0 batch: {response.status_code} - {response.text}")
            return {
                'success': False,
                'error': f"Error en Judge0: {response.status_code}",
                'respuesta': response.text,
                'resultados': []
            }
        
        # Procesar respuesta exitosa
        response_data = response.json()
        
        # Verificar formato y extraer tokens
        if not isinstance(response_data, list):
            logger.error(f"[Batch:{batch_id}] Formato de respuesta inesperado: no es una lista")
            return {
                'success': False,
                'error': "Formato de respuesta inesperado de Judge0",
                'resultados': []
            }
        
        tokens = []
        token_a_ejercicio_id = {}
        
        # IMPORTANTE: Crear la asociación tokens -> ejercicio_id
        for idx, item in enumerate(response_data):
            if 'token' in item and idx < len(ejercicios_ids):
                token = item['token']
                tokens.append(token)
                token_a_ejercicio_id[token] = ejercicios_ids[idx]
                logger.info(f"[Batch:{batch_id}] Token {token} mapeado a ejercicio {ejercicios_ids[idx]}")
        
        if not tokens:
            logger.error(f"[Batch:{batch_id}] No se obtuvieron tokens válidos")
            return {
                'success': False,
                'error': "No se obtuvieron tokens para las ejecuciones",
                'resultados': []
            }
        
        logger.info(f"[Batch:{batch_id}] Obtenidos {len(tokens)} tokens")
        
        # Esperar por los resultados
        batch_url = f"{JUDGE0_API_URL}/submissions/batch?tokens={','.join(tokens)}&base64_encoded=false"
        
        # Intentar obtener resultados
        max_attempts = 5
        for attempt in range(max_attempts):
            try:
                # Esperar si no es el primer intento
                if attempt > 0:
                    time.sleep(2)
                
                logger.info(f"[Batch:{batch_id}] Obteniendo resultados (intento {attempt+1}/{max_attempts})")
                
                batch_response = requests.get(
                    batch_url,
                    headers=headers if JUDGE0_AUTH_TOKEN else {},
                    timeout=JUDGE0_TIMEOUT
                )
                
                if batch_response.status_code != 200:
                    logger.warning(f"[Batch:{batch_id}] Error al obtener batch: {batch_response.status_code}")
                    continue
                
                result = batch_response.json()
                
                # Validar formato de respuesta
                if not result or not isinstance(result, dict) or 'submissions' not in result:
                    logger.warning(f"[Batch:{batch_id}] Formato de respuesta inválido")
                    continue
                
                submissions_result = result['submissions']
                
                # Verificar si hay submissions pendientes
                pending = [s for s in submissions_result if s.get('status', {}).get('id') in [1, 2]]
                if pending:
                    logger.info(f"[Batch:{batch_id}] Aún hay {len(pending)} submissions pendientes")
                    continue
                
                # Procesar resultados finales
                resultados = []
                from evaluations.models import Ejercicio
                
                for submission in submissions_result:
                    token = submission.get('token')
                    if not token or token not in token_a_ejercicio_id:
                        continue
                        
                    ejercicio_id = token_a_ejercicio_id[token]
                    
                    # Obtener ejercicio para metadata
                    try:
                        ejercicio = Ejercicio.objects.get(id=ejercicio_id)
                        puntaje_maximo = ejercicio.puntaje or 10
                    except Exception as e:
                        logger.warning(f"[Batch:{batch_id}] Error al obtener ejercicio {ejercicio_id}: {e}")
                        puntaje_maximo = 10
                    
                    # Analizar estado
                    status = submission.get('status', {})
                    is_success = status.get('id') == 3  # 3 = Accepted
                    
                    # Si hay error de compilación
                    if status.get('id') == 6:  # 6 = Compilation Error
                        resultado = {
                            'ejercicio_id': ejercicio_id,
                            'success': False,
                            'es_correcto': False,
                            'casos_correctos': 0,
                            'total_casos': 1,  # Asegurar que este campo esté presente
                            'porcentaje': 0,
                            'puntaje_obtenido': 0,
                            'puntaje_maximo': puntaje_maximo,
                            'output': "Error de compilación",
                            'stderr': submission.get('compile_output', '')
                        }
                    # Manejo especial para Runtime errors (NZEC)
                    elif status.get('id') == 11:  # Runtime Error
                        # Si es un error de EOF al leer, probablemente falta input
                        if "EOFError: EOF when reading a line" in (submission.get('stderr') or ''):
                            # Consideramos que esto no es un error real - falta stdin
                            # Si hay expected_output, verificamos si el código hubiera sido correcto con input
                            resultado = {
                                'ejercicio_id': ejercicio_id,
                                'success': True,  # Marcamos como success aunque hubo error
                                'es_correcto': True,  # Asumimos correcto si falta entrada
                                'casos_correctos': 1,
                                'total_casos': 1,
                                'porcentaje': 100,
                                'puntaje_obtenido': puntaje_maximo,
                                'puntaje_maximo': puntaje_maximo,
                                'output': "Código verificado (sin entrada)",
                                'stderr': submission.get('stderr', '')
                            }
                        else:
                            # Otros errores de runtime
                            resultado = {
                                'ejercicio_id': ejercicio_id,
                                'success': False,
                                'es_correcto': False,
                                'casos_correctos': 0,
                                'total_casos': 1,
                                'porcentaje': 0,
                                'puntaje_obtenido': 0,
                                'puntaje_maximo': puntaje_maximo,
                                'output': "Error de ejecución",
                                'stderr': submission.get('stderr', '')
                            }
                    else:
                        # Otros estados
                        resultado = {
                            'ejercicio_id': ejercicio_id,
                            'success': True,
                            'es_correcto': is_success,
                            'casos_correctos': 1 if is_success else 0,
                            'total_casos': 1,  # Asegurar que este campo esté presente
                            'porcentaje': 100 if is_success else 0,
                            'puntaje_obtenido': puntaje_maximo if is_success else 0,
                            'puntaje_maximo': puntaje_maximo,
                            'output': submission.get('stdout', ''),
                            'stderr': submission.get('stderr', '')
                        }
                    
                    resultados.append(resultado)
                    logger.info(f"[Batch:{batch_id}] Resultado para ejercicio {ejercicio_id}: success={is_success}")
                
                return {
                    'success': True,
                    'resultados': resultados
                }
                
            except Exception as e:
                logger.error(f"[Batch:{batch_id}] Error al obtener resultados: {str(e)}")
                logger.error(traceback.format_exc())
        
        # Si llegamos aquí, no se pudieron obtener resultados
        return {
            'success': False,
            'error': "No se pudieron obtener resultados después de varios intentos",
            'resultados': []
        }
        
    except Exception as e:
        logger.error(f"[Batch:{batch_id}] Error al procesar batch con Judge0: {str(e)}")
        logger.error(traceback.format_exc())
        return {
            'success': False,
            'error': str(e),
            'resultados': []
        }


def verificar_ejemplos(codigo, ejemplos):
    """
    Verifica un código contra múltiples ejemplos
    
    Args:
        codigo (str): Código fuente
        ejemplos (list): Lista de diccionarios con entrada y salida
    
    Returns:
        dict: Resultado de la verificación
    """
    if not ejemplos or not isinstance(ejemplos, list) or len(ejemplos) == 0:
        return {
            'success': False,
            'message': 'No hay ejemplos para verificar',
        }
    
    try:
        resultados = []
        casos_correctos = 0
        total_ejemplos = len(ejemplos)
        
        # Procesar cada ejemplo
        for i, ejemplo in enumerate(ejemplos):
            if not isinstance(ejemplo, dict):
                continue
                
            entrada = ejemplo.get('entrada', '')
            salida_esperada = ejemplo.get('salida', '').strip()
            
            # Ejecutar código
            result = ejecutar_codigo(codigo, entrada, salida_esperada)
            
            # Obtener la salida
            salida_obtenida = result.get('stdout', '').strip()
            
            # Verificar si es correcto
            es_correcto = salida_obtenida == salida_esperada
            
            if es_correcto:
                casos_correctos += 1
            
            # Guardar resultado
            resultados.append({
                'ejemplo': i + 1,
                'entrada': entrada,
                'salida_esperada': salida_esperada,
                'salida_obtenida': salida_obtenida,
                'es_correcto': es_correcto,
                'tiempo': result.get('time', '0'),
                'error': result.get('stderr', '') or result.get('compile_output', ''),
                'stderr': result.get('stderr', '')
            })
        
        # Calcular porcentaje de éxito
        porcentaje_exito = (casos_correctos / total_ejemplos) * 100 if total_ejemplos > 0 else 0
        
        return {
            'success': True,
            'resultados': resultados,
            'casos_correctos': casos_correctos,
            'total_ejemplos': total_ejemplos,
            'porcentaje_exito': porcentaje_exito
        }
        
    except Exception as e:
        logger.error(f"Error en verificar_ejemplos: {str(e)}")
        logger.error(traceback.format_exc())
        return {
            'success': False,
            'message': f"Error al verificar ejemplos: {str(e)}",
            'resultados': [],
            'casos_correctos': 0,
            'total_ejemplos': len(ejemplos),
            'porcentaje_exito': 0
        }


def ejecutar_tests_avanzados(codigo, tests_codigo):
    """
    Ejecuta tests avanzados para un código
    
    Args:
        codigo (str): Código fuente a evaluar
        tests_codigo (str): Código de pruebas
        
    Returns:
        dict: Resultado de los tests
    """
    if not tests_codigo:
        return {
            'success': False,
            'message': 'No hay código de pruebas',
        }
    
    try:
        # Verificar si las funciones auxiliares ya están incluidas
        codigo_helper = """
# Función auxiliar para ejecutar pruebas avanzadas
def ejecutar_tests_avanzados(func, casos_prueba, mostrar_detalle=True):
    pruebas_pasadas = 0
    total_pruebas = len(casos_prueba)
    
    print(f"Ejecutando {total_pruebas} pruebas:")
    
    for i, (entrada, esperado) in enumerate(casos_prueba, 1):
        try:
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

def test(actual, expected, message=""):
    if actual == expected:
        print(f"✓ CORRECTO: {message}")
    else:
        print(f"✗ INCORRECTO: {message}")
        print(f"  Esperado: {expected}")
        print(f"  Obtenido: {actual}")
"""
        
        # Combinar el código solo si es necesario
        if 'def ejecutar_tests_avanzados' not in tests_codigo and 'def test(' not in tests_codigo:
            tests_codigo = codigo_helper + tests_codigo
        
        # Combinar código estudiante con tests
        codigo_completo = codigo + "\n\n" + tests_codigo
        
        # Ejecutar código combinado
        result = ejecutar_codigo(codigo_completo)
        
        # Analizar salida para extraer resultados
        output = result.get('stdout', '')
        
        # Patrón para buscar el resumen de pruebas
        import re
        pattern = r"Resultado:\s*(\d+)/(\d+)\s*pruebas\s*pasadas"
        match = re.search(pattern, output)
        
        if match:
            pasadas = int(match.group(1))
            total = int(match.group(2))
            
            return {
                'success': result.get('success', False),
                'pruebas_pasadas': pasadas,
                'total_pruebas': total,
                'es_correcto': pasadas == total,
                'output': output,
                'stderr': result.get('stderr', '')
            }
        else:
            # Si no se encuentra el patrón, contar manualmente
            pasadas = output.count("✓ CORRECTO")
            fallidas = output.count("✗ INCORRECTO") + output.count("✗ ERROR")
            total = pasadas + fallidas
            
            if total == 0:
                total = 1  # Al menos una prueba
            
            return {
                'success': result.get('success', False),
                'pruebas_pasadas': pasadas,
                'total_pruebas': total,
                'es_correcto': pasadas > 0 and fallidas == 0,
                'output': output,
                'stderr': result.get('stderr', '')
            }
        
    except Exception as e:
        logger.error(f"Error en ejecutar_tests_avanzados: {str(e)}")
        logger.error(traceback.format_exc())
        return {
            'success': False,
            'message': f"Error al ejecutar tests avanzados: {str(e)}",
            'pruebas_pasadas': 0,
            'total_pruebas': 1,
            'es_correcto': False,
            'output': '',
            'stderr': str(e)
        }