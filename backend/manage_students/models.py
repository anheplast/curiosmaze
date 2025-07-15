# backend/manage_students/models.py
from django.db import models
from django.conf import settings

class Estudiante(models.Model):
    """Modelo para gestionar estudiantes"""
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='estudiante')
    docentes = models.ManyToManyField(settings.AUTH_USER_MODEL, through='DocenteEstudiante', related_name='estudiantes_asignados')
    fecha_registro = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        try:
            return f"{self.user.profile.nombres} {self.user.profile.apellidos}"
        except:
            return str(self.user)
    
    class Meta:
        verbose_name = "Estudiante"
        verbose_name_plural = "Estudiantes"


class DocenteEstudiante(models.Model):
    """Modelo para relacionar docentes con estudiantes"""
    docente = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='asignaciones_docente')
    estudiante = models.ForeignKey(Estudiante, on_delete=models.CASCADE, related_name='asignaciones_estudiante')
    fecha_asignacion = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ('docente', 'estudiante')
        verbose_name = "Asignación Docente-Estudiante"
        verbose_name_plural = "Asignaciones Docente-Estudiante"


class Asistencia(models.Model):
    """Modelo para registrar la asistencia de los estudiantes"""
    estudiante = models.ForeignKey(Estudiante, on_delete=models.CASCADE, related_name='asistencias')
    docente = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='asistencias_registradas')
    fecha = models.DateField()
    presente = models.BooleanField(default=True)
    observacion = models.TextField(blank=True, null=True)
    fecha_registro = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ('estudiante', 'docente', 'fecha')
        verbose_name = "Asistencia"
        verbose_name_plural = "Asistencias"
        ordering = ['-fecha', 'estudiante__user__profile__apellidos']


class Evaluacion(models.Model):
    """Modelo para registrar evaluaciones"""
    nombre = models.CharField(max_length=100)
    descripcion = models.TextField(blank=True, null=True)
    fecha = models.DateField()
    docente = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='evaluaciones_creadas')
    curso = models.CharField(max_length=10)
    paralelo = models.CharField(max_length=5)
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ('nombre', 'docente', 'curso', 'paralelo', 'fecha')
        verbose_name = "Evaluación"
        verbose_name_plural = "Evaluaciones"
        ordering = ['-fecha']
    
    def __str__(self):
        return f"{self.nombre} - {self.curso}{self.paralelo} ({self.fecha})"


class Calificacion(models.Model):
    """Modelo para registrar calificaciones de los estudiantes"""
    evaluacion = models.ForeignKey(Evaluacion, on_delete=models.CASCADE, related_name='calificaciones')
    estudiante = models.ForeignKey(Estudiante, on_delete=models.CASCADE, related_name='calificaciones')
    valor = models.DecimalField(max_digits=4, decimal_places=2)
    observacion = models.TextField(blank=True, null=True)
    fecha_registro = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ('evaluacion', 'estudiante')
        verbose_name = "Calificación"
        verbose_name_plural = "Calificaciones"
    
    def __str__(self):
        return f"{self.estudiante} - {self.evaluacion.nombre}: {self.valor}"