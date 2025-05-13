// src/api/exercisesService.js
import apiClient from './axios';

const exercisesService = {
  // Obtener todos los ejercicios
  getEjercicios() {
    return apiClient.get('/ejercicios/');
  },
  
  // Obtener un ejercicio específico
  getEjercicio(id) {
    return apiClient.get(`/ejercicios/${id}/`);
  },
  
  // Crear un nuevo ejercicio
  crearEjercicio(datosEjercicio) {
    return apiClient.post('/ejercicios/', datosEjercicio);
  },
  
  // Actualizar un ejercicio existente
  actualizarEjercicio(id, datosEjercicio) {
    return apiClient.put(`/ejercicios/${id}/`, datosEjercicio);
  },
  
  // Eliminar un ejercicio
  eliminarEjercicio(id) {
    return apiClient.delete(`/ejercicios/${id}/`);
  }
};

export default exercisesService;