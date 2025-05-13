<!-- components/AdminHome.vue -->
<template>
  <div class="judge0-monitor-wrapper">
    <div class="box content-container">
      <!-- Cabecera con título -->
      <div class="header-section">
        <div class="header-content">
          <h1 class="title">🧩 CURIOSMAZE</h1>
          <p class="subtitle">Panel de Monitoreo Judge0</p>
        </div>
      </div>

      <!-- Componente verificador de conexión -->
      <Judge0ConnectionChecker />

      <!-- Tarjetas de Estado de Judge0 -->
      <div class="status-cards-grid">
        <div class="status-card system-info">
          <div class="status-card-header">
            <span class="status-icon">🖥️</span>
            <h2>Información del Sistema</h2>
          </div>
          <div class="status-card-content">
            <div v-if="loading.systemInfo" class="loading-content">
              <div class="loader"></div>
              <p>Cargando información...</p>
            </div>
            <div v-else-if="error.systemInfo" class="error-content">
              <span class="error-icon">⚠️</span>
              <p>{{ error.systemInfo }}</p>
            </div>
            <div v-else-if="systemInfo" class="info-items">
              <div class="info-item">
                <span class="info-label">CPU:</span>
                <span>{{ systemInfo.CPU || 'No disponible' }}</span>
              </div>
              <div class="info-item">
                <span class="info-label">Memoria:</span>
                <span>{{ systemInfo.Mem || 'No disponible' }}</span>
              </div>
              <div class="info-item">
                <span class="info-label">Arquitectura:</span>
                <span>{{ systemInfo.Architecture || 'No disponible' }}</span>
              </div>
            </div>
          </div>
          <div class="status-card-footer">
            <button class="action-btn refresh-btn" @click="fetchSystemInfo">
              <span class="refresh-icon">🔄</span> Actualizar
            </button>
          </div>
        </div>

        <div class="status-card workers">
          <div class="status-card-header">
            <span class="status-icon">👷</span>
            <h2>Estado de Trabajadores</h2>
          </div>
          <div class="status-card-content">
            <div v-if="loading.workers" class="loading-content">
              <div class="loader"></div>
              <p>Cargando trabajadores...</p>
            </div>
            <div v-else-if="error.workers" class="error-content">
              <span class="error-icon">⚠️</span>
              <p>{{ error.workers }}</p>
            </div>
            <div v-else-if="workers.length > 0" class="info-items">
              <div v-for="(worker, index) in workers" :key="index" class="worker-item">
                <div class="worker-header">
                  <span class="worker-name">Cola: {{ worker.queue }}</span>
                  <span :class="['worker-status', getWorkerStatusClass(worker)]">
                    {{ getWorkerStatusText(worker) }}
                  </span>
                </div>
                <div class="worker-stats">
                  <div class="stat-item">
                    <span class="stat-icon">📊</span>
                    <span class="stat-label">En espera:</span>
                    <span class="stat-value">{{ worker.size }}</span>
                  </div>
                  <div class="stat-item">
                    <span class="stat-icon">🟢</span>
                    <span class="stat-label">Disponibles:</span>
                    <span class="stat-value">{{ worker.idle }}</span>
                  </div>
                  <div class="stat-item">
                    <span class="stat-icon">⚙️</span>
                    <span class="stat-label">Trabajando:</span>
                    <span class="stat-value">{{ worker.working }}</span>
                  </div>
                </div>
              </div>
            </div>
            <div v-else class="empty-state">
              <span class="empty-icon">🔍</span>
              <p>No hay información de trabajadores disponible</p>
            </div>
          </div>
          <div class="status-card-footer">
            <button class="action-btn refresh-btn" @click="fetchWorkers">
              <span class="refresh-icon">🔄</span> Actualizar
            </button>
          </div>
        </div>

        <div class="status-card config">
          <div class="status-card-header">
            <span class="status-icon">⚙️</span>
            <h2>Configuración</h2>
          </div>
          <div class="status-card-content">
            <div v-if="loading.config" class="loading-content">
              <div class="loader"></div>
              <p>Cargando configuración...</p>
            </div>
            <div v-else-if="error.config" class="error-content">
              <span class="error-icon">⚠️</span>
              <p>{{ error.config }}</p>
            </div>
            <div v-else-if="config" class="info-items">
              <div class="info-item">
                <span class="info-label">Límite de tiempo CPU:</span>
                <span>{{ config.cpu_time_limit }} s</span>
              </div>
              <div class="info-item">
                <span class="info-label">Límite de memoria:</span>
                <span>{{ formatMemory(config.memory_limit) }}</span>
              </div>
              <div class="info-item">
                <span class="info-label">Límite de pila:</span>
                <span>{{ formatMemory(config.stack_limit) }}</span>
              </div>
              <div class="info-item">
                <span class="info-label">Acceso a red:</span>
                <span>{{ config.enable_network ? '✅ Habilitado' : '❌ Deshabilitado' }}</span>
              </div>
            </div>
          </div>
          <div class="status-card-footer">
            <button class="action-btn refresh-btn" @click="fetchConfig">
              <span class="refresh-icon">🔄</span> Actualizar
            </button>
          </div>
        </div>

        <div class="status-card languages">
          <div class="status-card-header">
            <span class="status-icon">🔤</span>
            <h2>Lenguajes Disponibles</h2>
          </div>
          <div class="status-card-content">
            <div v-if="loading.languages" class="loading-content">
              <div class="loader"></div>
              <p>Cargando lenguajes...</p>
            </div>
            <div v-else-if="error.languages" class="error-content">
              <span class="error-icon">⚠️</span>
              <p>{{ error.languages }}</p>
            </div>
            <div v-else-if="languages.length > 0" class="languages-grid">
              <div v-for="lang in languages" :key="lang.id" class="language-item">
                <span class="language-icon">{{ getLanguageIcon(lang.name) }}</span>
                <span class="language-name">{{ lang.name }}</span>
              </div>
            </div>
            <div v-else class="empty-state">
              <span class="empty-icon">🔍</span>
              <p>No hay lenguajes disponibles</p>
            </div>
          </div>
          <div class="status-card-footer">
            <button class="action-btn refresh-btn" @click="fetchLanguages">
              <span class="refresh-icon">🔄</span> Actualizar
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- Notificación de estado -->
    <transition name="fade">
      <div v-if="notification.show" class="custom-notification" :class="notification.type">
        <button class="notification-close" @click="notification.show = false">×</button>
        <div class="notification-header">
          <span class="notification-icon">{{ notification.icon }}</span>
          <span class="notification-title">{{ notification.title }}</span>
        </div>
        <div class="notification-content">
          {{ notification.message }}
        </div>
      </div>
    </transition>
  </div>
</template>

<script>
import { ref, reactive, onMounted } from 'vue';
import Judge0ConnectionChecker from '@/components/Judge0ConnectionChecker.vue';
import axios from 'axios';

export default {
  name: 'AdminHome',
  components: {
    Judge0ConnectionChecker
  },
  setup() {
    // Estado para la información del sistema
    const systemInfo = ref(null);
    const workers = ref([]);
    const config = ref(null);
    const languages = ref([]);

    // Estado de carga
    const loading = reactive({
      systemInfo: false,
      workers: false,
      config: false,
      languages: false
    });

    // Estado de errores
    const error = reactive({
      systemInfo: null,
      workers: null,
      config: null,
      languages: null
    });

    // Estado de notificación
    const notification = reactive({
      show: false,
      title: '',
      message: '',
      type: 'is-info',
      icon: '📢',
      timeout: null
    });

    // Base URL para la API de Judge0 (desde variable de entorno)
    const judge0BaseUrl = import.meta.env.VITE_JUDGE0_API_URL;

    // Mostrar notificación
    const showNotification = (title, message, type = 'is-info', icon = '📢') => {
      // Si ya hay una notificación visible, limpiar su timeout
      if (notification.timeout) {
        clearTimeout(notification.timeout);
      }

      // Configurar la nueva notificación
      notification.title = title;
      notification.message = message;
      notification.type = type;
      notification.icon = icon;
      notification.show = true;

      // Configurar el timeout para ocultar la notificación
      notification.timeout = setTimeout(() => {
        notification.show = false;
      }, 4000);
    };

    // Obtener información del sistema
    const fetchSystemInfo = async () => {
      loading.systemInfo = true;
      error.systemInfo = null;

      try {
        const response = await axios.get(`${judge0BaseUrl}/system_info`);
        systemInfo.value = response.data;
        showNotification('Éxito', 'Información del sistema actualizada', 'is-success', '✅');
      } catch (err) {
        console.error('Error al obtener información del sistema:', err);
        error.systemInfo = 'No se pudo obtener la información del sistema. Verifique que Judge0 esté en ejecución.';
        showNotification('Error', error.systemInfo, 'is-danger', '❌');
      } finally {
        loading.systemInfo = false;
      }
    };

    // Obtener información de los trabajadores
    const fetchWorkers = async () => {
      loading.workers = true;
      error.workers = null;

      try {
        const response = await axios.get(`${judge0BaseUrl}/workers`);
        workers.value = response.data;
        showNotification('Éxito', 'Información de trabajadores actualizada', 'is-success', '✅');
      } catch (err) {
        console.error('Error al obtener información de trabajadores:', err);
        error.workers = 'No se pudo obtener la información de los trabajadores.';
        showNotification('Error', error.workers, 'is-danger', '❌');
      } finally {
        loading.workers = false;
      }
    };

    // Obtener configuración
    const fetchConfig = async () => {
      loading.config = true;
      error.config = null;

      try {
        const response = await axios.get(`${judge0BaseUrl}/config_info`);
        config.value = response.data;
        showNotification('Éxito', 'Configuración actualizada', 'is-success', '✅');
      } catch (err) {
        console.error('Error al obtener configuración:', err);
        error.config = 'No se pudo obtener la configuración.';
        showNotification('Error', error.config, 'is-danger', '❌');
      } finally {
        loading.config = false;
      }
    };

    // Obtener lenguajes disponibles
    const fetchLanguages = async () => {
      loading.languages = true;
      error.languages = null;

      try {
        const response = await axios.get(`${judge0BaseUrl}/languages`);
        // Limitar a 12 lenguajes para que se vea mejor en la UI
        languages.value = response.data.slice(0, 12);
        showNotification('Éxito', 'Lenguajes actualizados', 'is-success', '✅');
      } catch (err) {
        console.error('Error al obtener lenguajes:', err);
        error.languages = 'No se pudo obtener la lista de lenguajes.';
        showNotification('Error', error.languages, 'is-danger', '❌');
      } finally {
        loading.languages = false;
      }
    };

    // Formatear memoria (KB a MB)
    const formatMemory = (kb) => {
      if (!kb) return 'No disponible';
      if (kb < 1024) return `${kb} KB`;
      return `${(kb / 1024).toFixed(1)} MB`;
    };

    // Obtener estado de los trabajadores
    const getWorkerStatusClass = (worker) => {
      if (worker.failed > 0) return 'status-error';
      if (worker.size > 0 && worker.idle === 0) return 'status-busy';
      if (worker.idle > 0) return 'status-good';
      return 'status-neutral';
    };

    const getWorkerStatusText = (worker) => {
      if (worker.failed > 0) return '❌ Error';
      if (worker.size > 0 && worker.idle === 0) return '🔶 Ocupado';
      if (worker.idle > 0) return '✅ Disponible';
      return '⚪ Neutro';
    };

    // Asignar iconos a lenguajes comunes
    const getLanguageIcon = (langName) => {
      const langLower = langName.toLowerCase();
      
      if (langLower.includes('python')) return '🐍';
      if (langLower.includes('java')) return '☕';
      if (langLower.includes('c++')) return '🔷';
      if (langLower.includes('c#')) return '🔶';
      if (langLower.includes(' c ')) return '©️';
      if (langLower.includes('ruby')) return '💎';
      if (langLower.includes('javascript')) return '🟨';
      if (langLower.includes('php')) return '🐘';
      if (langLower.includes('rust')) return '🦀';
      if (langLower.includes('go')) return '🔵';
      if (langLower.includes('assembly')) return '⚙️';
      if (langLower.includes('basic')) return '🔢';
      
      // Icono por defecto para lenguajes no identificados
      return '📝';
    };

    onMounted(() => {
      // Cargar datos iniciales
      fetchSystemInfo();
      fetchWorkers();
      fetchConfig();
      fetchLanguages();
    });

    return {
      systemInfo,
      workers,
      config,
      languages,
      loading,
      error,
      notification,
      fetchSystemInfo,
      fetchWorkers,
      fetchConfig,
      fetchLanguages,
      formatMemory,
      getWorkerStatusClass,
      getWorkerStatusText,
      getLanguageIcon
    };
  }
};
</script>

<style scoped>
/* Variables de color heredadas del diseño existente */
:root {
  --color-bg-main: #1C1C21;
  --color-bg-element: #2A2A30;
  --color-bg-element-alt: #25252A;
  --color-bg-element-hover: #32323A;
  --color-border: #36363c;
  --color-border-focus: #7E91FF;
  --color-text-primary: #ffffff;
  --color-text-secondary: #e0e0e0;
  --color-text-muted: #9090A0;
  
  /* Nueva paleta con color principal EBB300 */
  --color-primary: #EBB300;
  --color-primary-light: #FFD03F;
  --color-primary-dark: #C89500;
  --color-secondary: #6B7280;
  --color-success: #9DBEB6;
  --color-info: #65B1C1;
  --color-warning: #FFBD2E;
  --color-danger: #FF6B6B;
  
  --border-radius-lg: 12px;
  --border-radius: 8px;
  --border-radius-sm: 6px;
  --shadow-lg: 0 8px 16px rgba(0, 0, 0, 0.2);
  --shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
  --shadow-sm: 0 2px 6px rgba(0, 0, 0, 0.1);
  --transition-fast: 0.2s;
  --transition-smooth: 0.3s;
}

/* Estilos generales */
.judge0-monitor-wrapper {
  padding: 1.5rem;
  background-color: var(--color-bg-main);
  color: var(--color-text-primary);
  min-height: 100vh;
}

.content-container {
  background-color: var(--color-bg-main);
  border-radius: var(--border-radius-lg);
  border-top: 4px solid var(--color-primary);
  box-shadow: var(--shadow-lg);
  width: 100%;
  margin: 0 auto;
  padding: 2rem;
}

/* Cabecera */
.header-section {
  display: flex;
  justify-content: center;
  align-items: center;
  margin-bottom: 2rem;
  text-align: center;
}

.header-content {
  text-align: center;
}

.header-content .title {
  color: var(--color-primary);
  font-size: 2.5rem;
  margin-bottom: 0.5rem;
  font-weight: 700;
  text-shadow: 0 2px 4px rgba(0, 0, 0, 0.3);
}

.header-content .subtitle {
  color: var(--color-text-secondary);
  font-size: 1.2rem;
  margin-top: 0;
}

/* Grid de tarjetas de estado */
.status-cards-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
  gap: 1.5rem;
  margin-top: 2rem;
}

.status-card {
  border-radius: var(--border-radius);
  overflow: hidden;
  box-shadow: var(--shadow);
  display: flex;
  flex-direction: column;
  background-color: var(--color-bg-element);
  border: 2px solid var(--color-border);
  height: 100%;
  min-height: 280px;
  transition: transform var(--transition-fast), box-shadow var(--transition-fast);
}

.status-card:hover {
  /* transform: translateY(-5px); */
  box-shadow: var(--shadow-lg);
  border-color: var(--color-primary-light);
}

/* Encabezados de tarjetas con colores temáticos */
.status-card.system-info .status-card-header {
  background-color: rgba(101, 177, 193, 0.2); /* Info azul */
  border-bottom: 3px solid var(--color-info);
}

.status-card.workers .status-card-header {
  background-color: rgba(157, 190, 182, 0.2); /* Success verde */
  border-bottom: 3px solid var(--color-success);
}

.status-card.config .status-card-header {
  background-color: rgba(235, 179, 0, 0.2); /* Primary amarillo */
  border-bottom: 3px solid var(--color-primary);
}

.status-card.languages .status-card-header {
  background-color: rgba(126, 145, 255, 0.2); /* Púrpura */
  border-bottom: 3px solid var(--color-border-focus);
}

.status-card-header {
  padding: 1.25rem;
  display: flex;
  align-items: center;
}

.status-icon {
  font-size: 1.75rem;
  margin-right: 0.75rem;
}

.status-card-header h2 {
  font-size: 1.25rem;
  font-weight: 600;
  color: var(--color-text-primary);
  margin: 0;
}

.status-card-content {
  flex-grow: 1;
  padding: 1.25rem;
  overflow-y: auto;
}

.status-card-footer {
  padding: 1rem;
  border-top: 1px solid var(--color-border);
  background-color: var(--color-bg-element-alt);
  display: flex;
  justify-content: center;
}

/* Información en tarjetas */
.info-items {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
}

.info-item {
  display: flex;
  justify-content: space-between;
  padding: 0.5rem 0.75rem;
  border-radius: var(--border-radius-sm);
  background-color: var(--color-bg-element-alt);
  border-left: 3px solid var(--color-primary);
}

.info-label {
  font-weight: 600;
  color: var(--color-text-secondary);
}

/* Estados de trabajadores */
.worker-item {
  margin-bottom: 1rem;
  padding: 0.75rem;
  border-radius: var(--border-radius-sm);
  background-color: var(--color-bg-element-alt);
  border: 1px solid var(--color-border);
}

.worker-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 0.75rem;
  padding-bottom: 0.5rem;
  border-bottom: 1px solid var(--color-border);
}

.worker-name {
  font-weight: 600;
  color: var(--color-text-primary);
}

.worker-status {
  padding: 0.25rem 0.5rem;
  border-radius: 20px;
  font-size: 0.75rem;
  font-weight: 600;
  display: flex;
  align-items: center;
}

.status-good {
  background-color: rgba(157, 190, 182, 0.2);
  color: var(--color-success);
}

.status-busy {
  background-color: rgba(255, 189, 46, 0.2);
  color: var(--color-warning);
}

.status-error {
  background-color: rgba(255, 107, 107, 0.2);
  color: var(--color-danger);
}

.status-neutral {
  background-color: rgba(107, 114, 128, 0.2);
  color: var(--color-text-secondary);
}

.worker-stats {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 0.5rem;
}

.stat-item {
  text-align: center;
  padding: 0.5rem;
  border-radius: var(--border-radius-sm);
  background-color: var(--color-bg-main);
  display: flex;
  flex-direction: column;
  align-items: center;
}

.stat-icon {
  font-size: 1.25rem;
  margin-bottom: 0.25rem;
}

.stat-label {
  font-size: 0.7rem;
  color: var(--color-text-muted);
  margin-bottom: 0.25rem;
}

.stat-value {
  font-size: 1.1rem;
  font-weight: 600;
  color: var(--color-text-primary);
}

/* Lenguajes */
.languages-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(120px, 1fr));
  gap: 0.75rem;
}

.language-item {
  padding: 0.75rem;
  border-radius: var(--border-radius-sm);
  background-color: var(--color-bg-element-alt);
  display: flex;
  flex-direction: column;
  align-items: center;
  text-align: center;
  border: 1px solid var(--color-border);
  transition: transform var(--transition-fast), border-color var(--transition-fast);
}

.language-item:hover {
  transform: translateY(-2px);
  border-color: var(--color-primary);
}

.language-icon {
  font-size: 1.75rem;
  margin-bottom: 0.5rem;
}

.language-name {
  font-size: 0.75rem;
  color: var(--color-text-secondary);
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

/* Botón de acción */
.action-btn {
  background-color: var(--color-bg-main);
  color: var(--color-text-primary);
  border: 1px solid var(--color-border);
  border-radius: var(--border-radius-sm);
  padding: 0.5rem 1rem;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  transition: all var(--transition-fast);
  cursor: pointer;
}

.refresh-icon {
  margin-right: 0.5rem;
}

.action-btn:hover {
  background-color: var(--color-primary);
  color: var(--color-bg-main);
  transform: translateY(-2px);
  box-shadow: var(--shadow-sm);
}

/* Estados de carga y error */
.loading-content {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 2rem 0;
  color: var(--color-text-secondary);
}

.loader {
  border: 4px solid var(--color-bg-element);
  border-top: 4px solid var(--color-primary);
  border-radius: 50%;
  width: 30px;
  height: 30px;
  animation: spin 1s linear infinite;
  margin-bottom: 1rem;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

.error-content {
  padding: 1rem;
  background-color: rgba(255, 107, 107, 0.1);
  border-radius: var(--border-radius-sm);
  color: var(--color-danger);
  display: flex;
  align-items: center;
}

.error-icon {
  font-size: 1.5rem;
  margin-right: 0.75rem;
}

.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 2rem 0;
  color: var(--color-text-muted);
  text-align: center;
}

.empty-icon {
  font-size: 2.5rem;
  margin-bottom: 1rem;
}

/* Notificación personalizada */
.custom-notification {
  position: fixed;
  top: 20px;
  right: 20px;
  background-color: var(--color-bg-element);
  border-left: 4px solid var(--color-primary);
  color: var(--color-text-primary);
  padding: 1.25rem;
  border-radius: var(--border-radius);
  box-shadow: var(--shadow-lg);
  z-index: 1000;
  width: 320px;
  animation: slideIn 0.3s ease-out;
}

.custom-notification.is-success {
  border-left-color: var(--color-success);
}

.custom-notification.is-danger {
  border-left-color: var(--color-danger);
}

.custom-notification.is-warning {
  border-left-color: var(--color-warning);
}

.custom-notification.is-info {
  border-left-color: var(--color-info);
}

.notification-close {
  position: absolute;
  top: 12px;
  right: 12px;
  background: none;
  border: none;
  color: var(--color-text-secondary);
  cursor: pointer;
  font-size: 1.25rem;
  line-height: 1;
}

.notification-header {
  display: flex;
  align-items: center;
  margin-bottom: 0.75rem;
}

.notification-icon {
  margin-right: 0.5rem;
  font-size: 1.25rem;
}

.notification-title {
  font-weight: 600;
  font-size: 1.1rem;
}

.notification-content {
  font-size: 0.95rem;
  color: var(--color-text-secondary);
  line-height: 1.5;
}

@keyframes slideIn {
  from {
    transform: translateX(100%);
    opacity: 0;
  }
  to {
    transform: translateX(0);
    opacity: 1;
  }
}

/* Transiciones */
.fade-enter-active, .fade-leave-active {
  transition: opacity 0.3s, transform 0.3s;
}

.fade-enter-from, .fade-leave-to {
  opacity: 0;
  transform: translateY(-10px);
}

/* Adaptación responsiva */
@media screen and (max-width: 768px) {
  .judge0-monitor-wrapper {
    padding: 1rem;
  }

  .content-container {
    padding: 1.5rem;
  }

  .header-content .title {
    font-size: 2rem;
  }

  .status-cards-grid {
    grid-template-columns: 1fr;
  }

  .worker-stats {
    grid-template-columns: 1fr;
  }
}
</style>