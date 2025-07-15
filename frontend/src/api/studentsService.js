// src/api/studentsService.js 
import apiClient from './axios';

const studentsService = {
  // Obtener lista de estudiantes con opciones extendidas
  getEstudiantes(curso, paralelo, mostrarTodos = true, estado = 'activo') {
    return apiClient.get('/manage-students/estudiantes/', {
      params: { 
        curso, 
        paralelo,
        mostrar_todos: mostrarTodos,
        estado: estado
      }
    });
  },
  
  // Obtener asistencias
  getAsistencias(fecha, curso, paralelo) {
    return apiClient.get('/manage-students/asistencias/', {
      params: { fecha, curso, paralelo }
    });
  },
  
  // Registrar asistencia
  registrarAsistencia(datosAsistencia) {
    return apiClient.post('/manage-students/asistencias/registrar/', datosAsistencia);
  },
  
  // Obtener calificaciones
  getCalificaciones(nombreEvaluacion, curso, paralelo) {
    return apiClient.get('/manage-students/calificaciones/', {
      params: { nombre_evaluacion: nombreEvaluacion, curso, paralelo }
    });
  },
  
  // Registrar calificaciones
  registrarCalificaciones(datosCalificacion) {
    return apiClient.post('/manage-students/calificaciones/registrar/', datosCalificacion);
  },
  
  // Generar reportes
  generarReporteAsistencia(curso, paralelo) {
    return apiClient.get('/manage-students/reportes/asistencia/', {
      params: { curso, paralelo },
      responseType: 'blob'
    });
  },
  
  generarReporteCalificaciones(curso, paralelo) {
    return apiClient.get('/manage-students/reportes/calificaciones/', {
      params: { curso, paralelo },
      responseType: 'blob'
    });
  },
  
  generarReporteEstudiante(estudianteId) {
    return apiClient.get(`/manage-students/reportes/estudiante/${estudianteId}/`, {
      responseType: 'blob'
    });
  }
};

export default studentsService;