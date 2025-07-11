# tests/test_timeout_integration.py
from django.test import TestCase, Client
from django.urls import reverse
from django.utils import timezone
from evaluations.models import Evaluacion, Ejercicio, EstudianteEvaluacion
import json
from unittest.mock import patch

class TimeoutIntegrationTest(TestCase):
    def setUp(self):
        # Configurar datos de prueba
        self.setup_evaluacion_expirada()
        self.client = Client()
        self.client.login(username='test_student', password='testpassword')
        
    @patch('evaluations.judge_utils.ejecutar_codigo')
    def test_evaluacion_timeout_full_flow(self, mock_ejecutar):
        # Configurar mock para Judge0
        mock_ejecutar.return_value = {
            'success': True,
            'stdout': 'Test output',
            'stderr': '',
            'status': {'id': 3, 'description': 'Accepted'}
        }
        
        # Ejecutar el endpoint submit_batch como lo haría en caso de timeout
        response = self.client.post(
            reverse('submit_batch'),
            data=json.dumps({
                'evaluacion_id': self.evaluacion.id,
                'ejercicios': [
                    {'ejercicio_id': self.ejercicio1.id, 'codigo': 'print("test")'},
                    {'ejercicio_id': self.ejercicio2.id, 'codigo': 'print("test2")'}
                ]
            }),
            content_type='application/json'
        )
        
        # Verificar respuesta
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertTrue(data['success'])
        
        # Verificar que se actualizó el estado en BD
        estudiante_eval = EstudianteEvaluacion.objects.get(
            estudiante=self.student_user,
            evaluacion=self.evaluacion
        )
        self.assertEqual(estudiante_eval.estado, 'finalizado')
        
        # Verificar que se crearon las respuestas para ambos ejercicios
        self.assertEqual(estudiante_eval.respuestas.count(), 2)
        
        # Verificar que se guardó en historial
        from evaluations.models import HistorialEvaluacion
        self.assertTrue(
            HistorialEvaluacion.objects.filter(
                estudiante_id=self.student_user.id,
                evaluacion_id=self.evaluacion.id
            ).exists()
        )