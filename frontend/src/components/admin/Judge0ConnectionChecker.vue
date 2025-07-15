<!-- src/components/admin/Judge0ConnectionChecker.vue -->
<template>
  <div class="judge0-checker">
    <div class="checker-card">
      <div class="checker-header">
        <div class="title-container">
          <span class="status-emoji">{{ statusEmoji }}</span>
          <h3>Estado de Judge0</h3>
        </div>
        <span :class="['status-indicator', connectionStatus]"></span>
      </div>
      
      <div class="checker-content">
        <p v-if="connectionStatus === 'checking'" class="status-message checking">
          <span class="loading-spinner"></span> Verificando conexión...
        </p>
        <p v-else-if="connectionStatus === 'connected'" class="status-message success">
          <span class="status-icon">✅</span> Conectado a Judge0 correctamente
        </p>
        <p v-else-if="connectionStatus === 'error'" class="status-message error">
          <span class="status-icon">❌</span> Error de conexión con Judge0
        </p>
        <p v-else class="status-message">
          <span class="status-icon">❓</span> No se ha verificado la conexión con Judge0
        </p>
        
        <div class="connection-info" v-if="connectionStatus === 'connected'">
          <div class="info-item">
            <span class="info-icon">🌐</span>
            <span class="info-label">URL:</span>
            <span class="info-value">{{ judge0Url }}</span>
          </div>
          <div class="info-item">
            <span class="info-icon">📦</span>
            <span class="info-label">Versión:</span>
            <span class="info-value">{{ version || 'Desconocida' }}</span>
          </div>
        </div>
        
        <div class="details-section" v-if="connectionDetails && Object.keys(connectionDetails).length > 0">
          <div class="details-header" @click="toggleDetails">
            <span>{{ showDetails ? '🔽 Ocultar detalles' : '▶️ Ver detalles' }}</span>
          </div>
          
          <div class="details-content" v-if="showDetails">
            <pre>{{ JSON.stringify(connectionDetails, null, 2) }}</pre>
          </div>
        </div>
        
        <div class="error-message" v-if="connectionStatus === 'error' && errorMessage">
          <h4>❗ Error:</h4>
          <p>{{ errorMessage }}</p>
          <p class="error-tip">Asegúrate que Judge0 esté activo en la dirección configurada</p>
        </div>
      </div>
      
      <div class="checker-actions">
        <button 
          class="action-button" 
          @click="checkConnection"
          :disabled="connectionStatus === 'checking'"
        >
          <span class="button-icon">🔄</span> Verificar conexión
        </button>
        
        <a 
          :href="`${judge0Url}/dummy-client.html`" 
          target="_blank" 
          class="action-button secondary"
        >
          <span class="button-icon">🔗</span> Abrir Judge0 Client
        </a>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, computed, onMounted } from 'vue';
import axios from 'axios';

export default {
  name: 'Judge0ConnectionChecker',
  
  setup() {
    const connectionStatus = ref('unknown'); // unknown, checking, connected, error
    const connectionDetails = ref(null);
    const errorMessage = ref('');
    const showDetails = ref(false);
    const version = ref('');
    
    // Obtener la URL de Judge0 desde variables de entorno
    const judge0Url = import.meta.env.VITE_JUDGE0_API_URL;
    
    const statusEmoji = computed(() => {
      switch (connectionStatus.value) {
        case 'connected': return '🟢';
        case 'checking': return '🟡';
        case 'error': return '🔴';
        default: return '⚪';
      }
    });
    
    const toggleDetails = () => {
      showDetails.value = !showDetails.value;
    };
    
    const checkConnection = async () => {
      try {
        connectionStatus.value = 'checking';
        errorMessage.value = '';
        connectionDetails.value = null;
        
        // Intentar obtener información básica de Judge0
        const response = await axios.get(`${judge0Url}/about`);
        
        if (response.status === 200) {
          connectionStatus.value = 'connected';
          connectionDetails.value = response.data;
          version.value = response.data.version || '';
          
          // Obtener más información del sistema si está disponible
          try {
            const systemInfoResponse = await axios.get(`${judge0Url}/system_info`);
            if (systemInfoResponse.status === 200) {
              connectionDetails.value = {
                ...connectionDetails.value,
                systemInfo: systemInfoResponse.data
              };
            }
          } catch (systemError) {
            console.warn('No se pudo obtener información del sistema:', systemError);
          }
          
          // Obtener información de los workers
          try {
            const workersResponse = await axios.get(`${judge0Url}/workers`);
            if (workersResponse.status === 200) {
              connectionDetails.value = {
                ...connectionDetails.value,
                workers: workersResponse.data
              };
            }
          } catch (workersError) {
            console.warn('No se pudo obtener información de workers:', workersError);
          }
        } else {
          connectionStatus.value = 'error';
          errorMessage.value = `Error de conexión: ${response.status} ${response.statusText}`;
        }
      } catch (error) {
        connectionStatus.value = 'error';
        errorMessage.value = error.message || 'Error desconocido al conectar con Judge0';
        console.error('Error al verificar conexión con Judge0:', error);
      }
    };
    
    // Verificar conexión al montar el componente
    onMounted(() => {
      checkConnection();
    });
    
    return {
      connectionStatus,
      connectionDetails,
      errorMessage,
      showDetails,
      toggleDetails,
      checkConnection,
      judge0Url,
      statusEmoji,
      version
    };
  }
};
</script>

<style scoped>
/* =================== CONTENEDOR PRINCIPAL =================== */
.judge0-checker {
  margin-bottom: 1.5rem;
  width: 100%;
}

.checker-card {
  background-color: var(--color-bg-element);
  border-radius: var(--border-radius);
  box-shadow: var(--shadow);
  overflow: hidden;
  border: 2px solid var(--color-border);
  transition: box-shadow var(--transition-smooth);
}

.checker-card:hover {
  box-shadow: var(--shadow-lg);
}

/* =================== HEADER DEL CHECKER =================== */
.checker-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1rem 1.25rem;
  background-color: var(--color-bg-element-alt);
  border-bottom: 1px solid var(--color-border);
}

.title-container {
  display: flex;
  align-items: center;
  gap: 0.75rem;
}

.status-emoji {
  font-size: 1.5rem;
}

.checker-header h3 {
  margin: 0;
  color: var(--color-text-primary);
  font-size: 1.2rem;
  font-weight: 600;
}

/* =================== INDICADORES DE ESTADO =================== */
.status-indicator {
  width: 12px;
  height: 12px;
  border-radius: 50%;
  display: inline-block;
}

.status-indicator.unknown {
  background-color: var(--color-text-muted);
}

.status-indicator.checking {
  background-color: var(--color-warning);
  animation: pulse 1s infinite alternate;
}

.status-indicator.connected {
  background-color: var(--color-success);
}

.status-indicator.error {
  background-color: var(--color-error);
}

/* =================== CONTENIDO Y MENSAJES =================== */
.checker-content {
  padding: 1.25rem;
  color: var(--color-text-primary);
}

.status-message {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  margin-bottom: 1.25rem;
  font-size: 1.05rem;
}

.status-icon {
  font-size: 1.25rem;
}

.status-message.success {
  color: var(--color-success);
}

.status-message.checking {
  color: var(--color-warning);
}

.status-message.error {
  color: var(--color-error);
}

.loading-spinner {
  display: inline-block;
  width: 16px;
  height: 16px;
  border: 2px solid rgba(255, 255, 255, 0.2);
  border-radius: 50%;
  border-top-color: var(--color-warning);
  animation: spin 1s ease-in-out infinite;
}

/* =================== INFORMACIÓN DE CONEXIÓN =================== */
.connection-info {
  background-color: var(--color-bg-element-alt);
  border-radius: var(--border-radius-sm);
  padding: 1rem;
  margin-bottom: 1.25rem;
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
}

.info-item {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.info-icon {
  font-size: 1.1rem;
  width: 1.5rem;
  text-align: center;
}

.info-label {
  font-weight: 600;
  color: var(--color-text-secondary);
  min-width: 80px;
}

.info-value {
  color: var(--color-primary);
  font-family: monospace;
  word-break: break-all;
}

/* =================== SECCIÓN DE DETALLES =================== */
.details-section {
  margin-top: 1.25rem;
  border: 1px solid var(--color-border);
  border-radius: var(--border-radius-sm);
  overflow: hidden;
}

.details-header {
  display: flex;
  justify-content: center;
  align-items: center;
  padding: 0.75rem;
  background-color: var(--color-bg-element-alt);
  cursor: pointer;
  user-select: none;
  transition: background-color var(--transition-fast);
  font-weight: 500;
}

.details-header:hover {
  background-color: var(--color-bg-element-hover);
}

.details-content {
  padding: 1rem;
  background-color: var(--color-bg-main);
  overflow-x: auto;
  max-height: 250px;
  overflow-y: auto;
}

.details-content pre {
  margin: 0;
  font-family: monospace;
  font-size: 0.85rem;
  color: var(--color-text-secondary);
  background-color: var(--color-bg-darker);
}

/* =================== MENSAJES DE ERROR =================== */
.error-message {
  margin-top: 1.25rem;
  padding: 1rem;
  background-color: var(--color-error-bg);
  border-left: 3px solid var(--color-error);
  border-radius: var(--border-radius-sm);
}

.error-message h4 {
  margin: 0 0 0.5rem 0;
  color: var(--color-error);
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.error-message p {
  margin: 0 0 0.5rem 0;
  font-size: 0.95rem;
}

.error-tip {
  font-size: 0.85rem;
  color: var(--color-text-muted);
  font-style: italic;
}

/* =================== ACCIONES Y BOTONES =================== */
.checker-actions {
  display: flex;
  gap: 1rem;
  padding: 1rem 1.25rem;
  border-top: 1px solid var(--color-border);
  background-color: var(--color-bg-element-alt);
}

.action-button {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.5rem;
  padding: 0.6rem 1.25rem;
  background-color: var(--color-primary);
  color: var(--color-bg-main);
  border: none;
  border-radius: var(--border-radius-sm);
  font-size: 0.95rem;
  font-weight: 600;
  cursor: pointer;
  transition: all var(--transition-fast);
  text-decoration: none;
}

.action-button:hover:not(:disabled) {
  background-color: var(--color-primary-light);
  transform: translateY(-2px);
  box-shadow: var(--shadow-sm);
}

.action-button:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.action-button.secondary {
  background-color: var(--color-bg-main);
  color: var(--color-text-primary);
  border: 1px solid var(--color-border);
}

.action-button.secondary:hover {
  background-color: var(--color-bg-element-hover);
  border-color: var(--color-primary);
}

.button-icon {
  font-size: 1.1rem;
}

/* =================== ANIMACIONES =================== */
@keyframes pulse {
  from { opacity: 0.6; }
  to { opacity: 1; }
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

/* =================== MEDIA QUERIES =================== */
@media screen and (max-width: 600px) {
  .checker-actions {
    flex-direction: column;
  }
  
  .action-button {
    width: 100%;
  }
}
</style>