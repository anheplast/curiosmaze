# tests/test_evaluation_timeout.py
from django.test import TestCase
from unittest.mock import patch, MagicMock
from evaluations.views import submit_batch

class EvaluationTimeoutTests(TestCase):
    def setUp(self):
        # Configurar usuario, evaluación y ejercicios para la prueba
        self.setup_test_data()
        
    @patch('evaluations.views.judge0_service.check_availability')
    @patch('evaluations.views.procesar_ejercicio')
    def test_submit_batch_handles_timeout_correctly(self, mock_procesar, mock_check):
        # Configurar mocks
        mock_check.return_value = (True, "Judge0 disponible")
        mock_procesar.side_effect = self.mock_procesar_ejercicio
        
        # Preparar datos de solicitud para simular timeout
        request_data = {
            'evaluacion_id': self.evaluacion.id,
            'ejercicios': [
                {'ejercicio_id': self.ejercicio1.id, 'codigo': 'print("test")'},
                {'ejercicio_id': self.ejercicio2.id, 'codigo': 'print("test2")'}
            ],
            'timeout': True  # Flag para simular timeout
        }
        
        # Ejecutar vista
        response = submit_batch(self.request_mock(request_data))
        
        # Verificar que todos los ejercicios fueron procesados
        self.assertEqual(mock_procesar.call_count, 2)
        
        # Verificar que se guardaron los resultados
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.data['success'])
        
        # Verificar que se guardó el estado de finalización
        estudiante_eval = EstudianteEvaluacion.objects.get(
            estudiante=self.user,
            evaluacion=self.evaluacion
        )
        self.assertEqual(estudiante_eval.estado, 'finalizado')
        self.assertIsNotNone(estudiante_eval.fecha_fin)
        
    def mock_procesar_ejercicio(self, codigo, ejercicio_id, evaluacion_id, estudiante_evaluacion_id):
        # Simular respuesta de procesar_ejercicio
        return {
            'ejercicio_id': ejercicio_id,
            'success': True,
            'casos_correctos': 1,
            'total_casos': 1,
            'porcentaje': 100,
            'puntaje_obtenido': 10,
            'puntaje_maximo': 10,
            'es_correcto': True
        }