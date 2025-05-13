# curiosmaze_backend/evaluations/tests/test_api.py

from django.test import TestCase
from django.contrib.auth import get_user_model
from django.utils import timezone
from rest_framework.test import APIClient
from users.models import UserProfile
from evaluations.models import Curso, Ejercicio, Evaluacion, EstudianteEvaluacion

User = get_user_model()

class EvaluationAPITestCase(TestCase):
    def setUp(self):
        # Crear usuario docente
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
        
        # Crear usuario estudiante
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
        
        # Crear clientes API
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
        
        # Fecha actual más 1 día
        fecha_futura = timezone.now() + timezone.timedelta(days=1)
        
        self.evaluacion_futura = Evaluacion.objects.create(
            titulo='Evaluación Futura',
            descripcion='Descripción de prueba',
            curso=self.curso,
            duracion_minutos=60,
            fecha_inicio=fecha_futura,
            estado='pendiente',
            creador=self.docente_user,
            puntaje_total=10,
            codigo_acceso='FUTURE'
        )
        
        # Fecha actual menos 1 día
        fecha_pasada = timezone.now() - timezone.timedelta(days=1)
        
        self.evaluacion_activa = Evaluacion.objects.create(
            titulo='Evaluación Activa',
            descripcion='Descripción de prueba',
            curso=self.curso,
            duracion_minutos=60,
            fecha_inicio=fecha_pasada,
            estado='activa',
            creador=self.docente_user,
            puntaje_total=10,
            codigo_acceso='ACTIVE'
        )
        
        # Inscribir estudiante en evaluación activa
        self.participacion = EstudianteEvaluacion.objects.create(
            estudiante=self.estudiante_user,
            evaluacion=self.evaluacion_activa,
            estado='activo',
            fecha_inicio=timezone.now()
        )
    
    def test_validar_codigo_evaluacion_futura(self):
        """Probar validación de código para evaluación futura"""
        response = self.anonymous_client.post('/api/evaluaciones/validar_codigo/', {
            'codigo': 'FUTURE'
        })
        self.assertEqual(response.status_code, 403)
        self.assertFalse(response.data['valid'])
        self.assertIn('no está disponible', response.data['error'])
    
    def test_validar_codigo_evaluacion_activa(self):
        """Probar validación de código para evaluación activa"""
        response = self.anonymous_client.post('/api/evaluaciones/validar_codigo/', {
            'codigo': 'ACTIVE'
        })
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.data['valid'])
        self.assertIn('id', response.data['evaluation'])
        
    def test_estudiante_acceso_evaluacion(self):
        """Probar que un estudiante inscrito puede acceder a su evaluación"""
        # Estudiante puede ver la evaluación en la que está inscrito
        response = self.estudiante_client.get('/api/evaluaciones/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['id'], self.evaluacion_activa.id)
        
        # Estudiante puede ver detalles de la evaluación en la que está inscrito
        response = self.estudiante_client.get(f'/api/evaluaciones/{self.evaluacion_activa.id}/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['id'], self.evaluacion_activa.id)
        
        # Estudiante no puede ver evaluación en la que no está inscrito
        response = self.estudiante_client.get(f'/api/evaluaciones/{self.evaluacion_futura.id}/')
        self.assertEqual(response.status_code, 403)
    
    def test_docente_creacion_evaluacion(self):
        """Probar que un docente puede crear evaluaciones"""
        data = {
            'titulo': 'Nueva Evaluación',
            'descripcion': 'Descripción de prueba',
            'curso': self.curso.id,
            'duracion_minutos': 60,
            'fecha_inicio': (timezone.now() + timezone.timedelta(days=2)).isoformat(),
            'estado': 'pendiente',
            'puntaje_total': 10,
            'ejercicios': [self.ejercicio.id]
        }
        
        response = self.docente_client.post('/api/evaluaciones/', data, format='json')
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data['titulo'], 'Nueva Evaluación')
        
        # Verificar que código de acceso fue generado
        self.assertIsNotNone(response.data['codigo_acceso'])