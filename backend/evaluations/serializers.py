# backend/evaluations/serializers.py
from rest_framework import serializers
import json
from users.models import User, UserProfile 
from .models import (
    Curso, Ejercicio, Evaluacion, EvaluacionEjercicio,
    EstudianteEvaluacion, RespuestaEjercicio, AjustePuntaje
)


class UsuarioSerializer(serializers.ModelSerializer):
    """
    Serializador para el modelo de Usuario
    """
    rol = serializers.SerializerMethodField()
    nombre_completo = serializers.SerializerMethodField()
    
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'nombre_completo', 'rol']
        read_only_fields = ['id']
    
    def get_rol(self, obj):
        try:
            return obj.profile.rol
        except UserProfile.DoesNotExist:
            return "sin_rol"
    
    def get_nombre_completo(self, obj):
        try:
            profile = obj.profile
            return f"{profile.nombres} {profile.apellidos}".strip()
        except UserProfile.DoesNotExist:
            return obj.username


class CursoSerializer(serializers.ModelSerializer):
    """
    Serializador para el modelo de Curso
    """
    docente_nombre = serializers.SerializerMethodField()
    estudiantes_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Curso
        fields = ['id', 'nombre', 'descripcion', 'docente', 'docente_nombre', 
                  'estudiantes', 'estudiantes_count']
        read_only_fields = ['id', 'docente', 'docente_nombre', 'estudiantes_count']
    
    def get_docente_nombre(self, obj):
        try:
            profile = obj.docente.profile
            return f"{profile.nombres} {profile.apellidos}".strip()
        except UserProfile.DoesNotExist:
            return obj.docente.username
    
    def get_estudiantes_count(self, obj):
        return obj.estudiantes.count()


class EjercicioSerializer(serializers.ModelSerializer):
    """
    Serializador para el modelo de Ejercicio
    """
    creador_nombre = serializers.SerializerMethodField()
    etiquetas = serializers.SerializerMethodField()
    templates_por_lenguaje = serializers.SerializerMethodField()
    
    class Meta:
        model = Ejercicio
        fields = ['id', 'titulo', 'descripcion', 'tipo', 'dificultad', 'credito',
                 'contenido', 'puntaje', 'creador', 'creador_nombre', 
                 'fecha_creacion', 'tests_avanzados', 'etiquetas', 'templates_por_lenguaje']
        read_only_fields = ['id', 'creador', 'creador_nombre', 'fecha_creacion']
    
    def get_creador_nombre(self, obj):
        try:
            profile = obj.creador.profile
            return f"{profile.nombres} {profile.apellidos}".strip()
        except UserProfile.DoesNotExist:
            return obj.creador.username
    
    def get_etiquetas(self, obj):
        """Extrae las etiquetas del campo contenido"""
        return obj.get_etiquetas()  # Usar el método helper
    
    
    def get_templates_por_lenguaje(self, obj):
        """
        Extrae las plantillas por lenguaje del campo contenido
        VERSIÓN CORREGIDA con mejor manejo de errores
        """
        try:
            # Primero intentar desde la propiedad del modelo
            if hasattr(obj, 'templates_por_lenguaje'):
                templates_desde_modelo = obj.templates_por_lenguaje
                if templates_desde_modelo and isinstance(templates_desde_modelo, dict):
                    print(f"🔧 Serializador: Templates desde modelo para ejercicio {obj.id}: {templates_desde_modelo}")
                    return templates_desde_modelo
            
            # Si no, buscar en el contenido directamente
            if obj.contenido:
                contenido = obj.contenido
                if isinstance(contenido, str):
                    try:
                        contenido = json.loads(contenido)
                    except json.JSONDecodeError:
                        print(f"❌ Error al parsear contenido JSON para ejercicio {obj.id}")
                        return {}
                
                if isinstance(contenido, dict) and 'templates' in contenido:
                    templates = contenido.get('templates', {})
                    if isinstance(templates, dict):
                        print(f"🔧 Serializador: Templates desde contenido para ejercicio {obj.id}: {templates}")
                        return templates
            
            print(f"⚠️ Serializador: No se encontraron templates para ejercicio {obj.id}")
            return {}
            
        except Exception as e:
            print(f"❌ Error en get_templates_por_lenguaje para ejercicio {obj.id}: {str(e)}")
            return {}
    

    def create(self, validated_data):
        """
        Guarda las etiquetas y templates por lenguaje en el contenido al crear un ejercicio
        """
        # Asegurarnos de que contenido sea un diccionario
        contenido = validated_data.get('contenido', {}) or {}
        if not isinstance(contenido, dict):
            try:
                contenido = json.loads(contenido) if isinstance(contenido, str) else {}
            except:
                contenido = {}
        
        # Obtener datos enviados por el cliente
        request = self.context.get('request')
        if request and hasattr(request, 'data'):
            # Procesar templates por lenguaje
            templates_por_lenguaje = request.data.get('templates_por_lenguaje', None)
            if templates_por_lenguaje is not None:
                # Convertir a diccionario si es string
                if isinstance(templates_por_lenguaje, str):
                    try:
                        templates_por_lenguaje = json.loads(templates_por_lenguaje)
                    except:
                        templates_por_lenguaje = {}
                
                # Guardar templates en el contenido
                contenido['templates'] = templates_por_lenguaje
                
            # Procesar tests avanzados por lenguaje
            tests_por_lenguaje = request.data.get('tests_por_lenguaje', None)
            if tests_por_lenguaje is not None:
                # Convertir a diccionario si es string
                if isinstance(tests_por_lenguaje, str):
                    try:
                        tests_por_lenguaje = json.loads(tests_por_lenguaje)
                    except:
                        tests_por_lenguaje = {}
                
                # Guardar en tests_avanzados
                validated_data['tests_avanzados'] = tests_por_lenguaje
            
            # Actualizar contenido
            validated_data['contenido'] = contenido
        
        # Usar el creador del contexto
        user = self.context.get('request').user if self.context.get('request') else None
        if user and user.is_authenticated:
            validated_data['creador'] = user
        
        return super().create(validated_data)

    def update(self, instance, validated_data):
        """
        Actualiza las etiquetas y templates por lenguaje al modificar un ejercicio
        """
        # Obtener contenido existente
        contenido = validated_data.get('contenido', instance.contenido) or {}
        if not isinstance(contenido, dict):
            try:
                contenido = json.loads(contenido) if isinstance(contenido, str) else {}
            except:
                contenido = {}
        
        # Obtener datos enviados por el cliente
        request = self.context.get('request')
        if request and hasattr(request, 'data'):
            # Procesar templates por lenguaje
            templates_por_lenguaje = request.data.get('templates_por_lenguaje', None)
            if templates_por_lenguaje is not None:
                # Convertir a diccionario si es string
                if isinstance(templates_por_lenguaje, str):
                    try:
                        templates_por_lenguaje = json.loads(templates_por_lenguaje)
                    except:
                        templates_por_lenguaje = {}
                
                # Guardar templates en el contenido
                contenido['templates'] = templates_por_lenguaje
                
            # Procesar tests avanzados por lenguaje
            tests_por_lenguaje = request.data.get('tests_por_lenguaje', None)
            if tests_por_lenguaje is not None:
                # Convertir a diccionario si es string
                if isinstance(tests_por_lenguaje, str):
                    try:
                        tests_por_lenguaje = json.loads(tests_por_lenguaje)
                    except:
                        tests_por_lenguaje = {}
                
                # Guardar en tests_avanzados
                validated_data['tests_avanzados'] = tests_por_lenguaje
            
            # Actualizar contenido
            validated_data['contenido'] = contenido
        
        return super().update(instance, validated_data)

    def update(self, instance, validated_data):
        """
        Actualiza las etiquetas y templates por lenguaje al modificar un ejercicio
        """
        # Obtener contenido existente
        contenido = validated_data.get('contenido', instance.contenido) or {}
        if not isinstance(contenido, dict):
            try:
                contenido = json.loads(contenido) if isinstance(contenido, str) else {}
            except:
                contenido = {}
        
        # Obtener datos enviados por el cliente
        request = self.context.get('request')
        if request and hasattr(request, 'data'):
            # Procesar templates por lenguaje
            templates_por_lenguaje = request.data.get('templates_por_lenguaje', None)
            if templates_por_lenguaje is not None:
                # Convertir a diccionario si es string
                if isinstance(templates_por_lenguaje, str):
                    try:
                        templates_por_lenguaje = json.loads(templates_por_lenguaje)
                    except:
                        templates_por_lenguaje = {}
                
                # Guardar templates en el contenido
                contenido['templates'] = templates_por_lenguaje
                
            # Procesar tests avanzados por lenguaje
            tests_por_lenguaje = request.data.get('tests_por_lenguaje', None)
            if tests_por_lenguaje is not None:
                # Convertir a diccionario si es string
                if isinstance(tests_por_lenguaje, str):
                    try:
                        tests_por_lenguaje = json.loads(tests_por_lenguaje)
                    except:
                        tests_por_lenguaje = {}
                
                # Guardar en tests_avanzados
                validated_data['tests_avanzados'] = tests_por_lenguaje
            
            # Actualizar contenido
            validated_data['contenido'] = contenido
        
        return super().update(instance, validated_data)

class EvaluacionEjercicioSerializer(serializers.ModelSerializer):
        """
        Serializador para la relación entre Evaluación y Ejercicio
        """
        ejercicio_detalle = EjercicioSerializer(source='ejercicio', read_only=True)
        
        class Meta:
            model = EvaluacionEjercicio
            fields = ['ejercicio', 'ejercicio_detalle', 'orden']
    


class EvaluacionSerializer(serializers.ModelSerializer):
    """
    Serializador para el modelo de Evaluación (versión básica)
    """
    creador_nombre = serializers.SerializerMethodField()
    curso_nombre = serializers.SerializerMethodField()
    estudiantes_total = serializers.SerializerMethodField()
    estudiantes_activos = serializers.SerializerMethodField()
    
    
    class Meta:
        model = Evaluacion
        fields = [
            'id', 'titulo', 'descripcion', 'curso', 'curso_nombre', 'duracion_minutos',
            'fecha_inicio', 'fecha_fin', 'codigo_acceso', 'estado', 'permitir_revision',
            'mostrar_resultado', 'orden_aleatorio', 'puntaje_total', 'puntaje_aprobacion',
            'creador', 'creador_nombre', 'fecha_creacion', 'estudiantes_total', 'estudiantes_activos'
        ]
        read_only_fields = ['id', 'codigo_acceso', 'creador', 'creador_nombre', 'fecha_creacion']
        # Curso opcional
        extra_kwargs = {
            'curso': {'required': False, 'allow_null': True}
        }


    def get_creador_nombre(self, obj):
        try:
            profile = obj.creador.profile
            return f"{profile.nombres} {profile.apellidos}".strip()
        except UserProfile.DoesNotExist:
            return obj.creador.username
    
    def get_curso_nombre(self, obj):
        if obj.curso:
            return obj.curso.nombre
        return "Sin curso asignado"  # O simplemente return None
    
    def get_estudiantes_total(self, obj):
        return obj.participantes.count()
    
    def get_estudiantes_activos(self, obj):
        return obj.participantes.filter(estado='activo').count()
    
    def create(self, validated_data):
        # Extraer ejercicios del request data si existe
        ejercicios_ids = self.context['request'].data.get('ejercicios', [])
        
        # Si no se proporciona curso, establecer como None
        if 'curso' not in validated_data:
            validated_data['curso'] = None
        
        # Crear la evaluación sin los ejercicios primero
        evaluacion = Evaluacion.objects.create(**validated_data)
        
        # Asociar ejercicios a la evaluación
        for i, ejercicio_id in enumerate(ejercicios_ids):
            EvaluacionEjercicio.objects.create(
                evaluacion=evaluacion,
                ejercicio_id=ejercicio_id,
                orden=i
            )
        
        return evaluacion   
    
    
    def update(self, instance, validated_data):
        # Actualizar campos normales
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        
        # Extraer ejercicios del request data si existe
        ejercicios_ids = self.context['request'].data.get('ejercicios')
        
        if ejercicios_ids:
            # Eliminar relaciones existentes
            instance.evaluacionejercicio_set.all().delete()
            
            # Crear nuevas relaciones
            for i, ejercicio_id in enumerate(ejercicios_ids):
                EvaluacionEjercicio.objects.create(
                    evaluacion=instance,
                    ejercicio_id=ejercicio_id,
                    orden=i
                )
        
        return instance


class EvaluacionDetalladaSerializer(EvaluacionSerializer):
    """
    Serializador extendido para el modelo de Evaluación (con detalles completos)
    """
    ejercicios = serializers.SerializerMethodField()
    
    class Meta(EvaluacionSerializer.Meta):
        fields = EvaluacionSerializer.Meta.fields + ['ejercicios']
    
    def get_ejercicios(self, obj):
        ejercicios_evaluacion = EvaluacionEjercicio.objects.filter(evaluacion=obj).order_by('orden')
        return EvaluacionEjercicioSerializer(ejercicios_evaluacion, many=True).data


class RespuestaEjercicioSerializer(serializers.ModelSerializer):
    """
    Serializador para el modelo de Respuesta a Ejercicio
    """
    ejercicio_titulo = serializers.SerializerMethodField()
    
    class Meta:
        model = RespuestaEjercicio
        fields = ['id', 'estudiante_evaluacion', 'ejercicio', 'ejercicio_titulo', 
                  'respuesta', 'es_correcta', 'puntaje_obtenido', 
                  'tiempo_respuesta', 'fecha_respuesta']
        read_only_fields = ['id', 'fecha_respuesta']
    
    def get_ejercicio_titulo(self, obj):
        return obj.ejercicio.titulo


class EstudianteEvaluacionSerializer(serializers.ModelSerializer):
    """
    Serializador para el modelo de Participación de Estudiante en Evaluación
    """
    estudiante_nombre = serializers.SerializerMethodField()
    evaluacion_titulo = serializers.SerializerMethodField()
    progreso_porcentaje = serializers.SerializerMethodField()
    respuestas = RespuestaEjercicioSerializer(many=True, read_only=True)
    
    class Meta:
        model = EstudianteEvaluacion
        fields = ['id', 'estudiante', 'estudiante_nombre', 'evaluacion', 
                  'evaluacion_titulo', 'estado', 'fecha_inicio', 'fecha_fin',
                  'puntaje', 'ajustes_puntaje', 'progreso', 'progreso_porcentaje',
                  'ip_acceso', 'respuestas', 'tiempo_total_ms']
        read_only_fields = ['id', 'fecha_inicio', 'fecha_fin', 'puntaje',
                           'ajustes_puntaje', 'progreso', 'ip_acceso']
    
    def get_estudiante_nombre(self, obj):
        try:
            profile = obj.estudiante.profile
            return f"{profile.nombres} {profile.apellidos}".strip()
        except UserProfile.DoesNotExist:
            return obj.estudiante.username
    
    def get_evaluacion_titulo(self, obj):
        return obj.evaluacion.titulo
    
    def get_progreso_porcentaje(self, obj):
        total_ejercicios = obj.evaluacion.ejercicios.count()
        if total_ejercicios == 0:
            return 0
        respondidos = obj.respuestas.count()
        return int((respondidos / total_ejercicios) * 100)


class AjustePuntajeSerializer(serializers.ModelSerializer):
    """
    Serializador para el modelo de Ajuste de Puntaje
    """
    docente_nombre = serializers.SerializerMethodField()
    estudiante_nombre = serializers.SerializerMethodField()
    
    class Meta:
        model = AjustePuntaje
        fields = ['id', 'estudiante_evaluacion', 'estudiante_nombre', 'docente', 
                  'docente_nombre', 'puntaje_anterior', 'ajuste', 'puntaje_nuevo', 
                  'motivo', 'fecha']
        read_only_fields = ['id', 'fecha']
    
    def get_docente_nombre(self, obj):
        try:
            profile = obj.docente.profile
            return f"{profile.nombres} {profile.apellidos}".strip()
        except UserProfile.DoesNotExist:
            return obj.docente.username
    
    def get_estudiante_nombre(self, obj):
        try:
            estudiante = obj.estudiante_evaluacion.estudiante
            profile = estudiante.profile
            return f"{profile.nombres} {profile.apellidos}".strip()
        except UserProfile.DoesNotExist:
            return obj.estudiante_evaluacion.estudiante.username