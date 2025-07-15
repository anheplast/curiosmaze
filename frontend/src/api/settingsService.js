// src/api/settingsService.js
import apiClient from './axios';

const settingsService = {
  // Obtener todas las configuraciones de la plataforma
  async getPlatformSettings() {
    try {
      console.log('🔧 Obteniendo configuraciones de la plataforma...');
      const response = await apiClient.get('/platform-settings/');
      console.log('✅ Configuraciones obtenidas:', response.data);
      return response;
    } catch (error) {
      console.error('❌ Error al obtener configuraciones:', error);
      throw error;
    }
  },

  // Actualizar una configuración específica
  async updateSetting(key, value) {
    try {
      console.log(`🔧 Actualizando configuración: ${key} = ${value}`);
      const response = await apiClient.post('/platform-settings/', {
        key: key,
        value: value
      });
      console.log('✅ Configuración actualizada:', response.data);
      return response;
    } catch (error) {
      console.error('❌ Error al actualizar configuración:', error);
      throw error;
    }
  },

  // Obtener específicamente la configuración del selector de lenguajes
  async getLanguageSelectorConfig() {
    try {
      console.log('🎛️ Obteniendo configuración del selector de lenguajes...');
      const response = await apiClient.get('/language-selector-config/');
      console.log('✅ Configuración del selector obtenida:', response.data);
      return response;
    } catch (error) {
      console.error('❌ Error al obtener configuración del selector:', error);
      // Devolver configuración por defecto en caso de error
      return {
        data: {
          success: false,
          language_selector_enabled: false,
          default_language_id: 71
        }
      };
    }
  },

  // Funciones específicas
  async setLanguageSelectorEnabled(enabled) {
    return this.updateSetting('language_selector_enabled', enabled);
  },

  async setDefaultLanguage(languageId) {
    return this.updateSetting('default_language_id', languageId);
  }
};

export default settingsService;