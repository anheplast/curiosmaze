# curiosmaze_backend/evaluations/models.py
from django.db import models
from django.utils.crypto import get_random_string
import uuid
from users.models import User  # Importa tu modelo de usuario existente


class Curso(models.Model):
    """
    Modelo para representar un curso o asignatura
    """
    nombre = models.CharField(max_length=100)
    descripcion = models.TextField(blank=True)
    docente = models.ForeignKey(User, on_delete=models.CASCADE, related_name='cursos')
    estudiantes = models.ManyToManyField(User, related_name='cursos_inscritos', blank=True)
    
    class Meta:
        verbose_name = 'Curso'
        verbose_name_plural = 'Cursos'
    
    def __str__(self):
        return self.nombre


class Ejercicio(models.Model):
    """
    Modelo para representar un ejercicio
    """
    TIPO_CHOICES = (
        ('practico', 'Práctico'),
        ('teorico', 'Teórico'),
    )
    
    DIFICULTAD_CHOICES = (
        ('facil', 'Fácil'),
        ('intermedio', 'Intermedio'),
        ('dificil', 'Difícil'),
    )
    
    titulo = models.CharField(max_length=200)
    descripcion = models.TextField()
    tipo = models.CharField(max_length=20, choices=TIPO_CHOICES)
    dificultad = models.CharField(max_length=20, choices=DIFICULTAD_CHOICES, default='intermedio')  
    credito = models.CharField(max_length=200, blank=True, null=True)  
    contenido = models.JSONField(help_text="Contenido del ejercicio en formato JSON", blank=True, null=True)
    puntaje = models.PositiveIntegerField(default=1)
    creador = models.ForeignKey(
        User, 
        on_delete=models.SET_NULL,  # Cambiado a SET_NULL
        null=True,                  # Permitir valores NULL
        related_name='ejercicios'
    )
    creador_nombre = models.CharField(max_length=255, blank=True, null=True)
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    tests_avanzados = models.JSONField(help_text="Tests avanzados en formato JSON", blank=True, null=True)
    
    class Meta:
        verbose_name = 'Ejercicio'
        verbose_name_plural = 'Ejercicios'
    
    def __str__(self):
        return self.titulo
    
    def save(self, *args, **kwargs):
        # Guardar el nombre del creador si existe
        if self.creador and not self.creador_nombre:
            try:
                perfil = self.creador.profile
                self.creador_nombre = f"{perfil.nombres} {perfil.apellidos}"
            except:
                self.creador_nombre = self.creador.username
        super().save(*args, **kwargs)
    
    def get_etiquetas(self):
        """Método helper para obtener etiquetas del contenido"""
        if not self.contenido:
            return []
            
        if isinstance(self.contenido, str):
            try:
                contenido = json.loads(self.contenido)
            except:
                return []
        else:
            contenido = self.contenido
            
        if isinstance(contenido, dict) and 'etiquetas' in contenido:
            etiquetas = contenido['etiquetas']
            if isinstance(etiquetas, list):
                return etiquetas
                
        return []


class Evaluacion(models.Model):
    """
    Modelo para representar una evaluación
    """
    ESTADO_CHOICES = (
        ('pendiente', 'Pendiente'),
        ('activa', 'Activa'),
        ('finalizada', 'Finalizada'),
    )
    
    titulo = models.CharField(max_length=200)
    descripcion = models.TextField(blank=True)
    curso = models.ForeignKey(Curso, on_delete=models.CASCADE, related_name='evaluaciones')
    ejercicios = models.ManyToManyField(Ejercicio, through='EvaluacionEjercicio')
    duracion_minutos = models.PositiveIntegerField(default=60)
    fecha_inicio = models.DateTimeField()
    fecha_fin = models.DateTimeField(null=True, blank=True)
    codigo_acceso = models.CharField(max_length=8, unique=True, editable=False)
    estado = models.CharField(max_length=10, choices=ESTADO_CHOICES, default='pendiente')
    permitir_revision = models.BooleanField(default=True)
    mostrar_resultado = models.BooleanField(default=True)
    orden_aleatorio = models.BooleanField(default=False)
    puntaje_total = models.PositiveIntegerField(default=0)
    puntaje_aprobacion = models.PositiveIntegerField(default=60, help_text="Porcentaje mínimo para aprobar")
    creador = models.ForeignKey(User, on_delete=models.CASCADE, related_name='evaluaciones')
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = 'Evaluación'
        verbose_name_plural = 'Evaluaciones'
    
    def __str__(self):
        return self.titulo
    
    def save(self, *args, **kwargs):
        # Generar código de acceso único si no existe
        if not self.codigo_acceso:
            self.codigo_acceso = get_random_string(8).upper()
        super().save(*args, **kwargs)


class EvaluacionEjercicio(models.Model):
    """
    Modelo de relación entre Evaluación y Ejercicio
    """
    evaluacion = models.ForeignKey(Evaluacion, on_delete=models.CASCADE)
    ejercicio = models.ForeignKey(Ejercicio, on_delete=models.CASCADE)
    orden = models.PositiveIntegerField(default=0)
    
    class Meta:
        verbose_name = 'Ejercicio de Evaluación'
        verbose_name_plural = 'Ejercicios de Evaluación'
        ordering = ['orden']
        unique_together = ('evaluacion', 'ejercicio')
    
    def __str__(self):
        return f"{self.evaluacion.titulo} - {self.ejercicio.titulo}"




class EstudianteEvaluacion(models.Model):
    """
    Modelo para representar la participación de un estudiante en una evaluación
    """
    ESTADO_CHOICES = (
        ('pendiente', 'Pendiente'),
        ('activo', 'Activo'),
        ('finalizado', 'Finalizado'),
        ('expulsado', 'Expulsado'),
    )
    
    estudiante = models.ForeignKey(User, on_delete=models.CASCADE, related_name='participaciones')
    evaluacion = models.ForeignKey(Evaluacion, on_delete=models.CASCADE, related_name='participantes')
    estado = models.CharField(max_length=10, choices=ESTADO_CHOICES, default='pendiente')
    fecha_inicio = models.DateTimeField(null=True, blank=True)
    fecha_fin = models.DateTimeField(null=True, blank=True)
    puntaje = models.FloatField(null=True, blank=True)
    ajustes_puntaje = models.FloatField(default=0, help_text="Ajustes adicionales al puntaje")
    progreso = models.PositiveIntegerField(default=0, help_text="Porcentaje de progreso")
    ip_acceso = models.GenericIPAddressField(null=True, blank=True)
    
    class Meta:
        verbose_name = 'Participación en Evaluación'
        verbose_name_plural = 'Participaciones en Evaluaciones'
        unique_together = ('estudiante', 'evaluacion')
    
    def __str__(self):
        return f"{self.estudiante.username} - {self.evaluacion.titulo}"



class RespuestaEjercicio(models.Model):
    """
    Modelo para representar la respuesta de un estudiante a un ejercicio
    """
    estudiante_evaluacion = models.ForeignKey(EstudianteEvaluacion, on_delete=models.CASCADE, related_name='respuestas')
    ejercicio = models.ForeignKey(Ejercicio, on_delete=models.CASCADE, related_name='respuestas')
    respuesta = models.JSONField(help_text="Respuesta del estudiante en formato JSON")
    es_correcta = models.BooleanField(null=True, blank=True)
    puntaje_obtenido = models.FloatField(default=0)
    tiempo_respuesta = models.DurationField(null=True, blank=True)
    fecha_respuesta = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = 'Respuesta a Ejercicio'
        verbose_name_plural = 'Respuestas a Ejercicios'
        unique_together = ('estudiante_evaluacion', 'ejercicio')
    
    def __str__(self):
        return f"{self.estudiante_evaluacion.estudiante.username} - {self.ejercicio.titulo}"


class AjustePuntaje(models.Model):
    """
    Modelo para registrar los ajustes de puntaje realizados por el docente
    """
    estudiante_evaluacion = models.ForeignKey(EstudianteEvaluacion, on_delete=models.CASCADE, related_name='historial_ajustes')
    docente = models.ForeignKey(User, on_delete=models.CASCADE, related_name='ajustes_realizados')
    puntaje_anterior = models.FloatField()
    ajuste = models.FloatField()
    puntaje_nuevo = models.FloatField()
    motivo = models.TextField()
    fecha = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = 'Ajuste de Puntaje'
        verbose_name_plural = 'Ajustes de Puntaje'
    
    def __str__(self):
        return f"Ajuste para {self.estudiante_evaluacion.estudiante.username} por {self.docente.username}"
 
    
class HistorialEvaluacion(models.Model):
    """
    Modelo para almacenar el historial completo de evaluaciones finalizadas
    """
    # Guardar ID del estudiante directamente para evitar dependencias
    estudiante_id = models.IntegerField(default=0)
    estudiante_nombre = models.CharField(max_length=200, default='')
    estudiante_email = models.EmailField(default='')
    
    # Guardar información de la evaluación original
    evaluacion_id = models.IntegerField(default=0)
    evaluacion_titulo = models.CharField(max_length=200, default='')
    evaluacion_descripcion = models.TextField(blank=True, default='')
    evaluacion_puntaje_total = models.PositiveIntegerField(default=0)
    evaluacion_codigo_acceso = models.CharField(max_length=8, default='')
    
    # Información del docente
    docente_id = models.IntegerField(default=0)
    docente_nombre = models.CharField(max_length=200, default='')
    
    # Información de la participación
    fecha_inicio = models.DateTimeField(null=True, blank=True)
    fecha_fin = models.DateTimeField(null=True, blank=True)
    fecha_almacenamiento = models.DateTimeField(auto_now_add=True)  # Cuando se guardó en historial
    
    # Resultados
    puntaje_total = models.FloatField(default=0)
    porcentaje_aprobacion = models.FloatField(default=0)
    tiempo_total = models.DurationField(null=True, blank=True)
    
    # Detalles completos de la evaluación y respuestas
    detalles = models.JSONField(help_text="Detalles completos de la evaluación incluyendo respuestas", default=dict)
    
    # Estado de la evaluación
    evaluacion_activa = models.BooleanField(default=True)  # Falso si la evaluación fue borrada
    
    class Meta:
        verbose_name = "Historial de Evaluación"
        verbose_name_plural = "Historiales de Evaluaciones"
        ordering = ['-fecha_almacenamiento']
        indexes = [
            models.Index(fields=['estudiante_id', '-fecha_almacenamiento']),
            models.Index(fields=['evaluacion_id']),
        ]
    
    def __str__(self):
        return f"{self.estudiante_nombre} - {self.evaluacion_titulo} ({self.fecha_almacenamiento.strftime('%d/%m/%Y')})"
    
    
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
