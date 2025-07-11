# curiosmaze_backend/users/tests/test_permissions.py

from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from users.models import UserProfile
from evaluations.models import Curso, Ejercicio, Evaluacion

User = get_user_model()

class PermissionTestCase(TestCase):
    def setUp(self):
        # Crear usuarios para cada rol
        self.admin_user = User.objects.create_user(
            username='admin_test',
            email='admin@test.com',
            password='testpass123'
        )
        self.admin_profile = UserProfile.objects.create(
            user=self.admin_user,
            rol='admin',
            nombres='Admin',
            apellidos='Test',
            identificacion='admin123'
        )
        
        self.docente_user = User.objects.create_user(
            username='docente_test',
            email='docente@test.com',
            password='testpass123'
        )
        self.docente_profile = UserProfile.objects.create(
            user=self.docente_user,
            rol='docente',
            nombres='Docente',
            apellidos='Test',
            identificacion='docente123'
        )
        
        self.estudiante_user = User.objects.create_user(
            username='estudiante_test',
            email='estudiante@test.com',
            password='testpass123'
        )
        self.estudiante_profile = UserProfile.objects.create(
            user=self.estudiante_user,
            rol='estudiante',
            nombres='Estudiante',
            apellidos='Test',
            identificacion='estudiante123'
        )
        
        # Crear clientes API para cada rol
        self.admin_client = APIClient()
        self.admin_client.force_authenticate(user=self.admin_user)
        
        self.docente_client = APIClient()
        self.docente_client.force_authenticate(user=self.docente_user)
        
        self.estudiante_client = APIClient()
        self.estudiante_client.force_authenticate(user=self.estudiante_user)
        
        self.anonymous_client = APIClient()
        
        # Crear datos de prueba
        self.curso = Curso.objects.create(
            nombre='Curso de Prueba',
            docente=self.docente_user
        )
        
        self.ejercicio = Ejercicio.objects.create(
            titulo='Ejercicio de Prueba',
            descripcion='Descripción de prueba',
            tipo='practico',
            puntaje=10,
            creador=self.docente_user
        )
        
        self.evaluacion = Evaluacion.objects.create(
            titulo='Evaluación de Prueba',
            descripcion='Descripción de prueba',
            curso=self.curso,
            duracion_minutos=60,
            fecha_inicio='2025-05-01T12:00:00Z',
            estado='pendiente',
            creador=self.docente_user,
            puntaje_total=10,
            codigo_acceso='TEST123'
        )
    
    def test_curso_permissions(self):
        """Prueba permisos para el modelo Curso"""
        # Admin puede ver cursos
        response = self.admin_client.get('/api/cursos/')
        self.assertEqual(response.status_code, 200)
        
        # Docente puede ver cursos
        response = self.docente_client.get('/api/cursos/')
        self.assertEqual(response.status_code, 200)
        
        # Estudiante no puede ver cursos
        response = self.estudiante_client.get('/api/cursos/')
        self.assertEqual(response.status_code, 403)
        
        # Usuario anónimo no puede ver cursos
        response = self.anonymous_client.get('/api/cursos/')
        self.assertEqual(response.status_code, 401)
    
    def test_ejercicio_permissions(self):
        """Prueba permisos para el modelo Ejercicio"""
        # Admin puede ver ejercicios
        response = self.admin_client.get('/api/ejercicios/')
        self.assertEqual(response.status_code, 200)
        
        # Docente puede ver ejercicios
        response = self.docente_client.get('/api/ejercicios/')
        self.assertEqual(response.status_code, 200)
        
        # Estudiante no puede ver ejercicios
        response = self.estudiante_client.get('/api/ejercicios/')
        self.assertEqual(response.status_code, 403)
        
        # Usuario anónimo no puede ver ejercicios
        response = self.anonymous_client.get('/api/ejercicios/')
        self.assertEqual(response.status_code, 401)
    
    def test_validar_codigo_permissions(self):
        """Prueba permisos para validar código de acceso"""
        # Cualquier usuario puede validar códigos
        response = self.anonymous_client.post('/api/evaluaciones/validar_codigo/', {
            'codigo': 'TEST123'
        })
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.data['valid'])
        
        # Código incorrecto
        response = self.anonymous_client.post('/api/evaluaciones/validar_codigo/', {
            'codigo': 'INVALID'
        })
        self.assertEqual(response.status_code, 404)
        self.assertFalse(response.data['valid'])
    
    def test_evaluacion_permissions(self):
        """Prueba permisos para el modelo Evaluacion"""
        # Admin puede ver evaluaciones
        response = self.admin_client.get('/api/evaluaciones/')
        self.assertEqual(response.status_code, 200)
        
        # Docente puede ver evaluaciones
        response = self.docente_client.get('/api/evaluaciones/')
        self.assertEqual(response.status_code, 200)
        
        # Estudiante solo puede ver evaluaciones en las que está inscrito
        response = self.estudiante_client.get('/api/evaluaciones/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 0)  # No debería ver ninguna evaluación
        
        # Usuario anónimo no puede ver evaluaciones
        response = self.anonymous_client.get('/api/evaluaciones/')
        self.assertEqual(response.status_code, 401)
        
        # Test para get_detalles_evaluacion
        # Admin puede ver detalles
        response = self.admin_client.get(f'/api/evaluaciones/{self.evaluacion.id}/detalles/')
        self.assertEqual(response.status_code, 200)
        
        # Docente puede ver detalles
        response = self.docente_client.get(f'/api/evaluaciones/{self.evaluacion.id}/detalles/')
        self.assertEqual(response.status_code, 200)
        
        # Estudiante no puede ver detalles si no está inscrito
        response = self.estudiante_client.get(f'/api/evaluaciones/{self.evaluacion.id}/detalles/')
        self.assertEqual(response.status_code, 403)