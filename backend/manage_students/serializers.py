# backend/manage_students/serializers.py
from rest_framework import serializers
from users.serializers import UserSerializer, UserProfileSerializer
from .models import Estudiante, DocenteEstudiante, Asistencia, Evaluacion, Calificacion
from django.contrib.auth import get_user_model

User = get_user_model()


class DocenteEstudianteSerializer(serializers.ModelSerializer):
    class Meta:
        model = DocenteEstudiante
        fields = ['id', 'docente', 'estudiante', 'fecha_asignacion']


class EstudianteListSerializer(serializers.ModelSerializer):
    """Serializer para listar estudiantes con sus datos de perfil"""
    id = serializers.IntegerField(source='user.id')
    username = serializers.CharField(source='user.username')
    email = serializers.CharField(source='user.email')
    nombres = serializers.CharField(source='user.profile.nombres')
    apellidos = serializers.CharField(source='user.profile.apellidos')
    identificacion = serializers.CharField(source='user.profile.identificacion')
    edad = serializers.IntegerField(source='user.profile.edad')
    genero = serializers.CharField(source='user.profile.genero')
    fecha_nacimiento = serializers.DateField(source='user.profile.fecha_nacimiento')
    curso = serializers.CharField(source='user.profile.curso')
    paralelo = serializers.CharField(source='user.profile.paralelo')
    
    class Meta:
        model = Estudiante
        fields = ['id', 'username', 'email', 'nombres', 'apellidos', 'identificacion',
                 'edad', 'genero', 'fecha_nacimiento', 'curso', 'paralelo']


class AsistenciaSerializer(serializers.ModelSerializer):
    """Serializer para el modelo de Asistencia"""
    estudiante_nombre = serializers.CharField(source='estudiante.user.profile.nombres', read_only=True)
    estudiante_apellido = serializers.CharField(source='estudiante.user.profile.apellidos', read_only=True)
    
    class Meta:
        model = Asistencia
        fields = ['id', 'estudiante', 'docente', 'fecha', 'presente', 'observacion', 
                 'fecha_registro', 'estudiante_nombre', 'estudiante_apellido']
        read_only_fields = ['fecha_registro']


class AsistenciaRegistroSerializer(serializers.Serializer):
    """Serializer para registrar múltiples asistencias a la vez"""
    fecha = serializers.DateField()
    curso = serializers.CharField(max_length=10)
    paralelo = serializers.CharField(max_length=5)
    asistencias = serializers.ListField(child=serializers.DictField())
    
    def validate(self, data):
        """Validar que el formato de asistencias sea correcto"""
        for asistencia in data['asistencias']:
            if 'estudiante_id' not in asistencia or 'presente' not in asistencia:
                raise serializers.ValidationError("Cada asistencia debe incluir estudiante_id y presente")
        return data


class EvaluacionSerializer(serializers.ModelSerializer):
    """Serializer para el modelo de Evaluación"""
    class Meta:
        model = Evaluacion
        fields = ['id', 'nombre', 'descripcion', 'fecha', 'docente', 'curso', 
                 'paralelo', 'fecha_creacion']
        read_only_fields = ['fecha_creacion']


class CalificacionSerializer(serializers.ModelSerializer):
    """Serializer para el modelo de Calificación"""
    estudiante_nombre = serializers.CharField(source='estudiante.user.profile.nombres', read_only=True)
    estudiante_apellido = serializers.CharField(source='estudiante.user.profile.apellidos', read_only=True)
    evaluacion_nombre = serializers.CharField(source='evaluacion.nombre', read_only=True)
    
    class Meta:
        model = Calificacion
        fields = ['id', 'evaluacion', 'estudiante', 'valor', 'observacion', 
                 'fecha_registro', 'estudiante_nombre', 'estudiante_apellido',
                 'evaluacion_nombre']
        read_only_fields = ['fecha_registro']


class CalificacionRegistroSerializer(serializers.Serializer):
    """Serializer para registrar múltiples calificaciones a la vez"""
    nombre_evaluacion = serializers.CharField(max_length=100)
    fecha = serializers.DateField()
    curso = serializers.CharField(max_length=10)
    paralelo = serializers.CharField(max_length=5)
    calificaciones = serializers.ListField(child=serializers.DictField())
    
    def validate(self, data):
        """Validar que el formato de calificaciones sea correcto"""
        for calificacion in data['calificaciones']:
            if 'estudiante_id' not in calificacion or 'valor' not in calificacion:
                raise serializers.ValidationError("Cada calificación debe incluir estudiante_id y valor")
            
            # Validar que el valor esté en el rango de 0 a 10
            valor = calificacion['valor']
            if valor < 0 or valor > 10:
                raise serializers.ValidationError("La calificación debe estar entre 0 y 10")
        
        return data