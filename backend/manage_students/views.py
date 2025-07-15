# backend/manage_students/views.py
from rest_framework import viewsets, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.db.models import Q
from django.shortcuts import get_object_or_404
from django.http import FileResponse
from django.utils import timezone

from .models import Estudiante, DocenteEstudiante, Asistencia, Evaluacion, Calificacion
from .serializers import (EstudianteListSerializer, DocenteEstudianteSerializer,
                         AsistenciaSerializer, AsistenciaRegistroSerializer,
                         EvaluacionSerializer, CalificacionSerializer,
                         CalificacionRegistroSerializer)
from users.models import User, UserProfile

import io
import csv
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph
from reportlab.lib.styles import getSampleStyleSheet

from users.permissions import IsAdmin, IsDocente


class EstudianteViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet para listar los estudiantes asignados a un docente"""
    serializer_class = EstudianteListSerializer
    permission_classes = [IsAuthenticated, IsDocente]
    
    def get_queryset(self):
        # Verificar que el usuario sea un docente
        try:
            perfil = self.request.user.profile
            if perfil.rol != 'docente':
                return Estudiante.objects.none()
        except:
            return Estudiante.objects.none()
        
        # Filtrar por los estudiantes asignados al docente
        curso = self.request.query_params.get('curso')
        paralelo = self.request.query_params.get('paralelo')
        
        # Obtenemos los estudiantes asignados al docente
        estudiantes = Estudiante.objects.filter(
            docentes=self.request.user
        )
        
        # Si se especifica curso y paralelo, filtramos adicionalmente
        if curso and paralelo:
            estudiantes = estudiantes.filter(
                user__profile__curso=curso,
                user__profile__paralelo=paralelo
            )
        
        return estudiantes.order_by('user__profile__apellidos', 'user__profile__nombres')


@api_view(['GET'])
@permission_classes([IsAuthenticated, IsDocente])
def lista_estudiantes(request):
    """Endpoint para listar estudiantes, ahora con filtros adicionales"""
    # Verificar que el usuario sea un docente
    try:
        perfil = request.user.profile
        if perfil.rol != 'docente':
            return Response(
                {"error": "No tiene permisos para acceder a esta información"},
                status=status.HTTP_403_FORBIDDEN
            )
    except:
        return Response(
            {"error": "No se pudo verificar el rol del usuario"},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    # Obtener parámetros de filtro
    curso = request.query_params.get('curso')
    paralelo = request.query_params.get('paralelo')
    estado = request.query_params.get('estado', 'activo')  # Nuevo: filtrar por estado, por defecto 'activo'
    
    # Parámetro mostrar_todos (por defecto False para mantener compatibilidad)
    mostrar_todos = request.query_params.get('mostrar_todos', 'false').lower() == 'true'
    
    # Filtrar perfiles de estudiantes (ahora incluye filtro por estado)
    perfiles = UserProfile.objects.filter(
        rol='estudiante'
    )
    
    # Filtrar por estado si se proporciona
    if estado and estado != 'todos':
        perfiles = perfiles.filter(estado=estado)
    
    if curso:
        perfiles = perfiles.filter(curso=curso)
    
    if paralelo:
        perfiles = perfiles.filter(paralelo=paralelo)
    
    # Lista para almacenar estudiantes
    estudiantes = []
    
    for perfil in perfiles:
        # Obtener o crear el registro de estudiante
        estudiante, created = Estudiante.objects.get_or_create(user=perfil.user)
        
        # Si mostrar_todos es True, incluir todos los estudiantes
        # Si no, verificar si está asignado al docente
        if mostrar_todos:
            asignado = True  # No verificamos asignación
        else:
            # Verificar si está asignado al docente (comportamiento original)
            asignado = DocenteEstudiante.objects.filter(
                docente=request.user,
                estudiante=estudiante
            ).exists()
        
        if asignado:
            # Construir manualmente el objeto de respuesta
            estudiantes.append({
                'id': perfil.user.id,
                'username': perfil.user.username,
                'email': perfil.user.email,
                'nombres': perfil.nombres,
                'apellidos': perfil.apellidos,
                'identificacion': perfil.identificacion,
                'edad': perfil.edad,
                'genero': perfil.genero,
                'fecha_nacimiento': perfil.fecha_nacimiento,
                'curso': perfil.curso,
                'paralelo': perfil.paralelo,
                'turno': perfil.turno,
                'estado': perfil.estado,  # Añadimos el estado explícitamente
                'categoria': 'Tecnología Educativa'
            })
    
    # Ordenar por apellidos y nombres
    estudiantes = sorted(estudiantes, key=lambda x: (x['apellidos'], x['nombres']))
    
    return Response(estudiantes)


@api_view(['GET'])
@permission_classes([IsAuthenticated, IsDocente])
def lista_asistencias(request):
    """Endpoint para listar asistencias registradas"""
    # Verificar que el usuario sea un docente
    try:
        perfil = request.user.profile
        if perfil.rol != 'docente':
            return Response(
                {"error": "No tiene permisos para acceder a esta información"},
                status=status.HTTP_403_FORBIDDEN
            )
    except:
        return Response(
            {"error": "No se pudo verificar el rol del usuario"},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    # Obtener parámetros de filtro
    fecha = request.query_params.get('fecha')
    curso = request.query_params.get('curso')
    paralelo = request.query_params.get('paralelo')
    
    # Si no se proporciona fecha, retornar error
    if not fecha:
        return Response(
            {"error": "Debe proporcionar una fecha para consultar asistencias"},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    # Obtener los estudiantes asignados al docente con el curso y paralelo especificados
    perfiles = UserProfile.objects.filter(
        rol='estudiante'
    )
    
    if curso:
        perfiles = perfiles.filter(curso=curso)
    
    if paralelo:
        perfiles = perfiles.filter(paralelo=paralelo)
    
    # Obtener los IDs de los usuarios estudiantes
    usuarios_ids = perfiles.values_list('user_id', flat=True)
    
    # Obtener los registros de estudiantes
    estudiantes = Estudiante.objects.filter(user_id__in=usuarios_ids)
    
    # Verificar cuáles están asignados al docente
    estudiantes_asignados = []
    for estudiante in estudiantes:
        asignado = DocenteEstudiante.objects.filter(
            docente=request.user,
            estudiante=estudiante
        ).exists()
        
        if asignado:
            estudiantes_asignados.append(estudiante.id)
    
    # Obtener las asistencias registradas para esos estudiantes en la fecha especificada
    asistencias = Asistencia.objects.filter(
        docente=request.user,
        estudiante_id__in=estudiantes_asignados,
        fecha=fecha
    )
    
    serializer = AsistenciaSerializer(asistencias, many=True)
    return Response(serializer.data)


@api_view(['POST'])
@permission_classes([IsAuthenticated, IsDocente])
def registrar_asistencia(request):
    """Endpoint para registrar asistencia de múltiples estudiantes"""
    # Verificar que el usuario sea un docente
    try:
        perfil = request.user.profile
        if perfil.rol != 'docente':
            return Response(
                {"error": "No tiene permisos para registrar asistencias"},
                status=status.HTTP_403_FORBIDDEN
            )
    except:
        return Response(
            {"error": "No se pudo verificar el rol del usuario"},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    serializer = AsistenciaRegistroSerializer(data=request.data)
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    # Datos validados
    fecha = serializer.validated_data['fecha']
    curso = serializer.validated_data['curso']
    paralelo = serializer.validated_data['paralelo']
    asistencias_data = serializer.validated_data['asistencias']
    
    # Registrar o actualizar las asistencias
    resultados = []
    
    for asistencia_data in asistencias_data:
        estudiante_id = asistencia_data['estudiante_id']
        presente = asistencia_data['presente']
        observacion = asistencia_data.get('observacion', '')
        
        try:
            # Verificar que el estudiante exista
            estudiante = get_object_or_404(Estudiante, user_id=estudiante_id)
            
            # Verificar que el estudiante esté asignado al docente
            asignado = DocenteEstudiante.objects.filter(
                docente=request.user,
                estudiante=estudiante
            ).exists()
            
            if not asignado:
                resultados.append({
                    'estudiante_id': estudiante_id,
                    'status': 'error',
                    'message': 'Estudiante no asignado a este docente'
                })
                continue
            
            # Verificar que el estudiante sea del curso y paralelo especificados
            perfil = estudiante.user.profile
            if perfil.curso != curso or perfil.paralelo != paralelo:
                resultados.append({
                    'estudiante_id': estudiante_id,
                    'status': 'error',
                    'message': 'Estudiante no pertenece al curso y paralelo especificados'
                })
                continue
            
            # Registrar o actualizar la asistencia
            asistencia, created = Asistencia.objects.update_or_create(
                estudiante=estudiante,
                docente=request.user,
                fecha=fecha,
                defaults={
                    'presente': presente,
                    'observacion': observacion
                }
            )
            
            resultados.append({
                'estudiante_id': estudiante_id,
                'status': 'success',
                'message': 'Asistencia registrada correctamente'
            })
            
        except Estudiante.DoesNotExist:
            resultados.append({
                'estudiante_id': estudiante_id,
                'status': 'error',
                'message': 'Estudiante no encontrado'
            })
    
    return Response({
        'fecha': fecha,
        'curso': curso,
        'paralelo': paralelo,
        'resultados': resultados
    })


@api_view(['GET'])
@permission_classes([IsAuthenticated, IsDocente])
def lista_calificaciones(request):
    """Endpoint para listar calificaciones registradas"""
    # Verificar que el usuario sea un docente
    try:
        perfil = request.user.profile
        if perfil.rol != 'docente':
            return Response(
                {"error": "No tiene permisos para acceder a esta información"},
                status=status.HTTP_403_FORBIDDEN
            )
    except:
        return Response(
            {"error": "No se pudo verificar el rol del usuario"},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    # Obtener parámetros de filtro
    nombre_evaluacion = request.query_params.get('nombre_evaluacion')
    curso = request.query_params.get('curso')
    paralelo = request.query_params.get('paralelo')
    
    # Si no se proporciona nombre de evaluación, retornar error
    if not nombre_evaluacion:
        return Response(
            {"error": "Debe proporcionar un nombre de evaluación para consultar calificaciones"},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    # Buscar la evaluación
    try:
        evaluacion = Evaluacion.objects.get(
            nombre=nombre_evaluacion,
            docente=request.user,
            curso=curso,
            paralelo=paralelo
        )
    except Evaluacion.DoesNotExist:
        # Si no existe, retornamos una lista vacía
        return Response([])
    
    # Obtener las calificaciones asociadas a esta evaluación
    calificaciones = Calificacion.objects.filter(
        evaluacion=evaluacion
    )
    
    serializer = CalificacionSerializer(calificaciones, many=True)
    return Response(serializer.data)


@api_view(['POST'])
@permission_classes([IsAuthenticated, IsDocente])
def registrar_calificaciones(request):
    """Endpoint para registrar calificaciones de múltiples estudiantes"""
    # Verificar que el usuario sea un docente
    try:
        perfil = request.user.profile
        if perfil.rol != 'docente':
            return Response(
                {"error": "No tiene permisos para registrar calificaciones"},
                status=status.HTTP_403_FORBIDDEN
            )
    except:
        return Response(
            {"error": "No se pudo verificar el rol del usuario"},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    serializer = CalificacionRegistroSerializer(data=request.data)
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    # Datos validados
    nombre_evaluacion = serializer.validated_data['nombre_evaluacion']
    fecha = serializer.validated_data['fecha']
    curso = serializer.validated_data['curso']
    paralelo = serializer.validated_data['paralelo']
    calificaciones_data = serializer.validated_data['calificaciones']
    
    # Obtener o crear la evaluación
    evaluacion, created = Evaluacion.objects.update_or_create(
        nombre=nombre_evaluacion,
        docente=request.user,
        curso=curso,
        paralelo=paralelo,
        defaults={
            'fecha': fecha
        }
    )
    
    # Registrar o actualizar las calificaciones
    resultados = []
    
    for calificacion_data in calificaciones_data:
        estudiante_id = calificacion_data['estudiante_id']
        valor = calificacion_data['valor']
        observacion = calificacion_data.get('observacion', '')
        
        try:
            # Verificar que el estudiante exista
            estudiante = get_object_or_404(Estudiante, user_id=estudiante_id)
            
            # Verificar que el estudiante esté asignado al docente
            asignado = DocenteEstudiante.objects.filter(
                docente=request.user,
                estudiante=estudiante
            ).exists()
            
            if not asignado:
                resultados.append({
                    'estudiante_id': estudiante_id,
                    'status': 'error',
                    'message': 'Estudiante no asignado a este docente'
                })
                continue
            
            # Verificar que el estudiante sea del curso y paralelo especificados
            perfil = estudiante.user.profile
            if perfil.curso != curso or perfil.paralelo != paralelo:
                resultados.append({
                    'estudiante_id': estudiante_id,
                    'status': 'error',
                    'message': 'Estudiante no pertenece al curso y paralelo especificados'
                })
                continue
            
            # Registrar o actualizar la calificación
            calificacion, created = Calificacion.objects.update_or_create(
                evaluacion=evaluacion,
                estudiante=estudiante,
                defaults={
                    'valor': valor,
                    'observacion': observacion
                }
            )
            
            resultados.append({
                'estudiante_id': estudiante_id,
                'status': 'success',
                'message': 'Calificación registrada correctamente'
            })
            
        except Estudiante.DoesNotExist:
            resultados.append({
                'estudiante_id': estudiante_id,
                'status': 'error',
                'message': 'Estudiante no encontrado'
            })
    
    return Response({
        'evaluacion_id': evaluacion.id,
        'nombre_evaluacion': nombre_evaluacion,
        'fecha': fecha,
        'curso': curso,
        'paralelo': paralelo,
        'resultados': resultados
    })


@api_view(['GET'])
@permission_classes([IsAuthenticated, IsDocente])
def generar_reporte_asistencia(request):
    """Endpoint para generar un reporte de asistencia en PDF"""
    # Verificar que el usuario sea un docente
    try:
        perfil = request.user.profile
        if perfil.rol != 'docente':
            return Response(
                {"error": "No tiene permisos para generar reportes"},
                status=status.HTTP_403_FORBIDDEN
            )
    except:
        return Response(
            {"error": "No se pudo verificar el rol del usuario"},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    # Obtener parámetros de filtro
    curso = request.query_params.get('curso')
    paralelo = request.query_params.get('paralelo')
    
    if not curso or not paralelo:
        return Response(
            {"error": "Debe especificar curso y paralelo para generar el reporte"},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    # Obtener los estudiantes asignados al docente con el curso y paralelo especificados
    perfiles = UserProfile.objects.filter(
        rol='estudiante',
        curso=curso,
        paralelo=paralelo
    )
    
    # Obtener los IDs de los usuarios estudiantes
    usuarios_ids = perfiles.values_list('user_id', flat=True)
    
    # Obtener los registros de estudiantes
    estudiantes = Estudiante.objects.filter(user_id__in=usuarios_ids)
    
    # Verificar cuáles están asignados al docente
    estudiantes_asignados = []
    for estudiante in estudiantes:
        asignado = DocenteEstudiante.objects.filter(
            docente=request.user,
            estudiante=estudiante
        ).exists()
        
        if asignado:
            estudiantes_asignados.append(estudiante)
    
    # Ordenar por apellidos
    estudiantes_asignados.sort(key=lambda e: e.user.profile.apellidos)
    
    # Obtener todas las asistencias de estos estudiantes
    asistencias = Asistencia.objects.filter(
        docente=request.user,
        estudiante__in=[e.id for e in estudiantes_asignados]
    ).order_by('fecha')
    
    # Agrupar por fecha
    fechas = asistencias.values_list('fecha', flat=True).distinct().order_by('fecha')
    
    # Crear un buffer para el PDF
    buffer = io.BytesIO()
    
    # Crear el documento PDF
    doc = SimpleDocTemplate(buffer, pagesize=letter)
    elements = []
    
    # Estilos
    styles = getSampleStyleSheet()
    title_style = styles['Heading1']
    subtitle_style = styles['Heading2']
    normal_style = styles['Normal']
    
    # Título
    elements.append(Paragraph(f"Reporte de Asistencia - Curso {curso} Paralelo {paralelo}", title_style))
    elements.append(Paragraph(f"Docente: {request.user.profile.nombres} {request.user.profile.apellidos}", subtitle_style))
    elements.append(Paragraph(f"Fecha de generación: {timezone.now().strftime('%d/%m/%Y %H:%M')}", normal_style))
    
    # Datos para la tabla
    data = [['Estudiante']]
    
    # Añadir fechas como columnas
    for fecha in fechas:
        data[0].append(fecha.strftime('%d/%m/%Y'))
    
    # Añadir filas para cada estudiante
    for estudiante in estudiantes_asignados:
        fila = [f"{estudiante.user.profile.apellidos}, {estudiante.user.profile.nombres}"]
        
        for fecha in fechas:
            try:
                asistencia = Asistencia.objects.get(
                    docente=request.user,
                    estudiante=estudiante,
                    fecha=fecha
                )
                fila.append('✓' if asistencia.presente else 'X')
            except Asistencia.DoesNotExist:
                fila.append('-')
        
        data.append(fila)
    
    # Crear la tabla
    table = Table(data)
    
    # Estilo de la tabla
    style = TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (0, -1), colors.lightgrey),
        ('GRID', (0, 0), (-1, -1), 1, colors.black)
    ])
    
    table.setStyle(style)
    elements.append(table)
    
    # Construir el PDF
    doc.build(elements)
    
    # Preparar la respuesta
    buffer.seek(0)
    return FileResponse(
        buffer, 
        as_attachment=True,
        filename=f"reporte_asistencia_{curso}{paralelo}.pdf"
    )


@api_view(['GET'])
@permission_classes([IsAuthenticated, IsDocente])
def generar_reporte_calificaciones(request):
    """Endpoint para generar un reporte de calificaciones en PDF"""
    # Verificar que el usuario sea un docente
    try:
        perfil = request.user.profile
        if perfil.rol != 'docente':
            return Response(
                {"error": "No tiene permisos para generar reportes"},
                status=status.HTTP_403_FORBIDDEN
            )
    except:
        return Response(
            {"error": "No se pudo verificar el rol del usuario"},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    # Obtener parámetros de filtro
    curso = request.query_params.get('curso')
    paralelo = request.query_params.get('paralelo')
    
    if not curso or not paralelo:
        return Response(
            {"error": "Debe especificar curso y paralelo para generar el reporte"},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    # Obtener las evaluaciones del docente para este curso y paralelo
    evaluaciones = Evaluacion.objects.filter(
        docente=request.user,
        curso=curso,
        paralelo=paralelo
    ).order_by('fecha')
    
    if not evaluaciones.exists():
        return Response(
            {"error": "No hay evaluaciones registradas para este curso y paralelo"},
            status=status.HTTP_404_NOT_FOUND
        )
    
    # Obtener los estudiantes asignados al docente con el curso y paralelo especificados
    perfiles = UserProfile.objects.filter(
        rol='estudiante',
        curso=curso,
        paralelo=paralelo
    )
    
    # Obtener los IDs de los usuarios estudiantes
    usuarios_ids = perfiles.values_list('user_id', flat=True)
    
    # Obtener los registros de estudiantes
    estudiantes = Estudiante.objects.filter(user_id__in=usuarios_ids)
    
    # Verificar cuáles están asignados al docente
    estudiantes_asignados = []
    for estudiante in estudiantes:
        asignado = DocenteEstudiante.objects.filter(
            docente=request.user,
            estudiante=estudiante
        ).exists()
        
        if asignado:
            estudiantes_asignados.append(estudiante)
    
    # Ordenar por apellidos
    estudiantes_asignados.sort(key=lambda e: e.user.profile.apellidos)
    
    # Crear un buffer para el PDF
    buffer = io.BytesIO()
    
    # Crear el documento PDF
    doc = SimpleDocTemplate(buffer, pagesize=letter)
    elements = []
    
    # Estilos
    styles = getSampleStyleSheet()
    title_style = styles['Heading1']
    subtitle_style = styles['Heading2']
    normal_style = styles['Normal']
    
    # Título
    elements.append(Paragraph(f"Reporte de Calificaciones - Curso {curso} Paralelo {paralelo}", title_style))
    elements.append(Paragraph(f"Docente: {request.user.profile.nombres} {request.user.profile.apellidos}", subtitle_style))
    elements.append(Paragraph(f"Fecha de generación: {timezone.now().strftime('%d/%m/%Y %H:%M')}", normal_style))
    
    # Datos para la tabla
    data = [['Estudiante']]
    
    # Añadir evaluaciones como columnas
    for evaluacion in evaluaciones:
        data[0].append(evaluacion.nombre)
    
    # Añadir promedio como última columna
    data[0].append('Promedio')
    
    # Añadir filas para cada estudiante
    for estudiante in estudiantes_asignados:
        fila = [f"{estudiante.user.profile.apellidos}, {estudiante.user.profile.nombres}"]
        
        # Para calcular el promedio
        valores = []
        
        for evaluacion in evaluaciones:
            try:
                calificacion = Calificacion.objects.get(
                    evaluacion=evaluacion,
                    estudiante=estudiante
                )
                fila.append(str(calificacion.valor))
                valores.append(float(calificacion.valor))
            except Calificacion.DoesNotExist:
                fila.append('-')
        
        # Calcular promedio
        if valores:
            promedio = sum(valores) / len(valores)
            fila.append(f"{promedio:.2f}")
        else:
            fila.append('-')
        
        data.append(fila)
    
    # Crear la tabla
    table = Table(data)
    
    # Estilo de la tabla
    style = TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (0, -1), colors.lightgrey),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('BACKGROUND', (-1, 0), (-1, -1), colors.lightblue)
    ])
    
    table.setStyle(style)
    elements.append(table)
    
    # Construir el PDF
    doc.build(elements)
    
    # Preparar la respuesta
    buffer.seek(0)
    return FileResponse(
        buffer, 
        as_attachment=True,
        filename=f"reporte_calificaciones_{curso}{paralelo}.pdf"
    )


@api_view(['GET'])
@permission_classes([IsAuthenticated, IsDocente])
def generar_reporte_estudiante(request, estudiante_id):
    """Endpoint para generar un reporte completo de un estudiante específico"""
    # Verificar que el usuario sea un docente
    try:
        perfil = request.user.profile
        if perfil.rol != 'docente':
            return Response(
                {"error": "No tiene permisos para generar reportes"},
                status=status.HTTP_403_FORBIDDEN
            )
    except:
        return Response(
            {"error": "No se pudo verificar el rol del usuario"},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    # Verificar que el estudiante exista
    try:
        estudiante = Estudiante.objects.get(user_id=estudiante_id)
    except Estudiante.DoesNotExist:
        return Response(
            {"error": "Estudiante no encontrado"},
            status=status.HTTP_404_NOT_FOUND
        )
    
    # Verificar que el estudiante esté asignado al docente
    asignado = DocenteEstudiante.objects.filter(
        docente=request.user,
        estudiante=estudiante
    ).exists()
    
    if not asignado:
        return Response(
            {"error": "No tiene permisos para acceder a la información de este estudiante"},
            status=status.HTTP_403_FORBIDDEN
        )
    
    # Obtener perfil del estudiante
    perfil = estudiante.user.profile
    
    # Obtener asistencias del estudiante
    asistencias = Asistencia.objects.filter(
        docente=request.user,
        estudiante=estudiante
    ).order_by('fecha')
    
    # Obtener calificaciones del estudiante
    calificaciones = Calificacion.objects.filter(
        estudiante=estudiante,
        evaluacion__docente=request.user
    ).select_related('evaluacion').order_by('evaluacion__fecha')
    
    # Crear un buffer para el PDF
    buffer = io.BytesIO()
    
    # Crear el documento PDF
    doc = SimpleDocTemplate(buffer, pagesize=letter)
    elements = []
    
    # Estilos
    styles = getSampleStyleSheet()
    title_style = styles['Heading1']
    subtitle_style = styles['Heading2']
    normal_style = styles['Normal']
    
    # Título
    elements.append(Paragraph(f"Reporte Individual del Estudiante", title_style))
    elements.append(Paragraph(f"{perfil.nombres} {perfil.apellidos}", subtitle_style))
    
    # Información básica
    elements.append(Paragraph("Información Básica", subtitle_style))
    datos_basicos = [
        ['Identificación', perfil.identificacion],
        ['Curso', perfil.curso],
        ['Paralelo', perfil.paralelo],
        ['Género', perfil.genero],
        ['Edad', str(perfil.edad) if perfil.edad else 'No especificada'],
        ['Email', estudiante.user.email]
    ]
    
    tabla_info = Table(datos_basicos, colWidths=[150, 300])
    tabla_info.setStyle(TableStyle([
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('BACKGROUND', (0, 0), (0, -1), colors.lightgrey),
        ('ALIGN', (0, 0), (0, -1), 'RIGHT'),
        ('ALIGN', (1, 0), (1, -1), 'LEFT'),
        ('PADDING', (0, 0), (-1, -1), 6)
    ]))
    
    elements.append(tabla_info)
    elements.append(Paragraph("<br/><br/>", normal_style))
    
    # Reporte de asistencia
    elements.append(Paragraph("Registro de Asistencia", subtitle_style))
    
    if asistencias.exists():
        datos_asistencia = [['Fecha', 'Estado', 'Observación']]
        
        for asistencia in asistencias:
            datos_asistencia.append([
                asistencia.fecha.strftime('%d/%m/%Y'),
                'Presente' if asistencia.presente else 'Ausente',
                asistencia.observacion or ''
            ])
        
        tabla_asistencia = Table(datos_asistencia, colWidths=[100, 100, 250])
        tabla_asistencia.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        
        elements.append(tabla_asistencia)
    else:
        elements.append(Paragraph("No hay registros de asistencia para este estudiante", normal_style))
    
    elements.append(Paragraph("<br/><br/>", normal_style))
    
    # Reporte de calificaciones
    elements.append(Paragraph("Registro de Calificaciones", subtitle_style))
    
    if calificaciones.exists():
        datos_calificaciones = [['Evaluación', 'Fecha', 'Calificación', 'Observación']]
        
        # Para calcular el promedio
        valores = []
        
        for calificacion in calificaciones:
            datos_calificaciones.append([
                calificacion.evaluacion.nombre,
                calificacion.evaluacion.fecha.strftime('%d/%m/%Y'),
                str(calificacion.valor),
                calificacion.observacion or ''
            ])
            valores.append(float(calificacion.valor))
        
        # Añadir promedio
        if valores:
            promedio = sum(valores) / len(valores)
            datos_calificaciones.append([
                'PROMEDIO', '', f"{promedio:.2f}", ''
            ])
        
        tabla_calificaciones = Table(datos_calificaciones, colWidths=[150, 100, 80, 120])
        tabla_calificaciones.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('BACKGROUND', (0, -1), (-1, -1), colors.lightblue) if valores else ('GRID', (0, 0), (-1, -1), 0, colors.white)
        ]))
        
        elements.append(tabla_calificaciones)
    else:
        elements.append(Paragraph("No hay registros de calificaciones para este estudiante", normal_style))
    
    # Información del docente y fecha de generación
    elements.append(Paragraph("<br/><br/>", normal_style))
    elements.append(Paragraph(f"Generado por: {request.user.profile.nombres} {request.user.profile.apellidos}", normal_style))
    elements.append(Paragraph(f"Fecha de generación: {timezone.now().strftime('%d/%m/%Y %H:%M')}", normal_style))
    
    # Construir el PDF
    doc.build(elements)
    
    # Preparar la respuesta
    buffer.seek(0)
    return FileResponse(
        buffer, 
        as_attachment=True,
        filename=f"reporte_estudiante_{perfil.apellidos}_{perfil.nombres}.pdf"
    )