// src/api/authService.js
import apiClient from './axios';

const authService = {
  // Obtener token CSRF
  getCsrfToken() {
    return apiClient.get('/users/csrf-token/');
  },

  // Iniciar sesión (ahora con manejo de CSRF)
  async login(credentials) {
    try {
      // Primero obtener un token CSRF
      await this.getCsrfToken();
      // Luego intentar el login
      return await apiClient.post('/users/login/', credentials);
    } catch (error) {
      console.error('Error durante la obtención del token CSRF o login:', error);
      throw error;
    }
  },
  
  // Resetear contraseña (después de login con contraseña temporal)
  async resetPassword(data) {
    try {
      console.log("DATOS ENVIADOS PARA RESET PASSWORD:", JSON.stringify(data));
      await this.getCsrfToken();
      return await apiClient.post('/users/reset-password/', data, {
        headers: {
          'Authorization': null  // Anular el header global
        }
      });
    } catch (error) {
      console.error('Error al resetear contraseña:', error);
      throw error;
    }
  },
  
  // Solicitar recuperación de contraseña
  async requestPasswordReset(data) {
    try {
      await this.getCsrfToken();
      return await apiClient.post('/users/request-password-reset/', data);
    } catch (error) {
      console.error('Error al solicitar recuperación de contraseña:', error);
      throw error;
    }
  },
  
  // Confirmar recuperación con código (si se implementa)
  async confirmPasswordReset(data) {
    try {
      await this.getCsrfToken();
      return await apiClient.post('/users/confirm-password-reset/', data);
    } catch (error) {
      console.error('Error al confirmar recuperación de contraseña:', error);
      throw error;
    }
  },
  
  // Obtener perfil del usuario
  getUserProfile() {
    return apiClient.get('/users/profile/');
  },
  
  // Registrar un nuevo docente
  async registerDocente(data) {
    try {
      await this.getCsrfToken();
      return await apiClient.post('/users/register/docente/', data);
    } catch (error) {
      console.error('Error durante el registro de docente:', error);
      throw error;
    }
  },
  
  // Registrar un nuevo usuario (estudiante)
  async registerUser(data) {
    try {
      await this.getCsrfToken();
      return await apiClient.post('/users/users/', data);
    } catch (error) {
      console.error('Error durante el registro de usuario:', error);
      throw error;
    }
  },
  
  // MÉTODOS PARA GESTIÓN DE USUARIOS
  
  // Obtener usuarios por estado con mejor manejo de errores
  async getUsersByStatus(estado) {
    try {
      console.log(`Solicitando usuarios con estado: ${estado}`);
      console.log('Token en localStorage:', localStorage.getItem('token'));
      
      const response = await apiClient.get(`/users/by-status/${estado}/`);
      console.log(`Usuarios ${estado} obtenidos:`, response.data);
      return response;
    } catch (error) {
      console.error('Error al obtener usuarios por estado:', error);
      
      // Mostrar más detalles del error si están disponibles
      if (error.response) {
        console.error('Datos del error:', error.response.data);
        console.error('Estado HTTP:', error.response.status);
        console.error('Encabezados:', error.response.headers);
      } else if (error.request) {
        console.error('No se recibió respuesta:', error.request);
      }
      
      throw error;
    }
  },

  // Actualizar estado de usuario
  async updateUserStatus(userData) {
    try {
      console.log(`Actualizando estado de usuario:`, userData);
      await this.getCsrfToken();
      const response = await apiClient.post('/users/update-status/', userData);
      console.log('Respuesta de actualización:', response.data);
      return response;
    } catch (error) {
      console.error('Error al actualizar estado de usuario:', error);
      
      if (error.response) {
        console.error('Datos del error:', error.response.data);
      }
      
      throw error;
    }
  },
  
  // MÉTODOS PARA EL SISTEMA DE GESTIÓN
  
  // Crear usuario (para administradores)
  async createUser(userData) {
    try {
      await this.getCsrfToken();
      const response = await apiClient.post('/users/create/', userData);
      return response;
    } catch (error) {
      console.error('Error al crear usuario:', error);
      throw error;
    }
  },
  
  // Actualizar usuario existente
  async updateUser(userId, userData) {
    try {
      await this.getCsrfToken();
      const response = await apiClient.put(`/users/update/${userId}/`, userData);
      return response;
    } catch (error) {
      console.error('Error al actualizar usuario:', error);
      throw error;
    }
  },
  
  // Eliminar usuario definitivamente
  async deleteUser(userId) {
    try {
      await this.getCsrfToken();
      const response = await apiClient.delete(`/users/delete/${userId}/`);
      return response;
    } catch (error) {
      console.error('Error al eliminar usuario:', error);
      throw error;
    }
  },
  
  // Resetear contraseña de usuario (administrador)
  async adminResetPassword(data) {
    try {
      await this.getCsrfToken();
      const response = await apiClient.post('/users/admin-reset-password/', data);
      return response;
    } catch (error) {
      console.error('Error al resetear contraseña de usuario:', error);
      throw error;
    }
  },
  
  // Importar usuarios desde archivo
  async importUsers(formData) {
    try {
      await this.getCsrfToken();
      const response = await apiClient.post('/users/import/', formData, {
        headers: {
          'Content-Type': 'multipart/form-data'
        }
      });
      return response;
    } catch (error) {
      console.error('Error al importar usuarios:', error);
      throw error;
    }
  }
};

export default authService;