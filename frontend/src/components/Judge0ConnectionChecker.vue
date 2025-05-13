<!-- components/Judge0ConnectionChecker.vue -->
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
.judge0-checker {
  margin-bottom: 1.5rem;
  width: 100%;
}

.checker-card {
  background-color: var(--color-bg-element, #2a2a30);
  border-radius: var(--border-radius, 8px);
  box-shadow: var(--shadow, 0 4px 12px rgba(0, 0, 0, 0.15));
  overflow: hidden;
  border: 2px solid var(--color-border, #36363c);
  transition: box-shadow 0.3s ease;
}

.checker-card:hover {
  box-shadow: var(--shadow-lg, 0 8px 16px rgba(0, 0, 0, 0.2));
}

.checker-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1rem 1.25rem;
  background-color: var(--color-bg-element-alt, #25252A);
  border-bottom: 1px solid var(--color-border, #36363c);
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
  color: var(--color-text-primary, #fff);
  font-size: 1.2rem;
  font-weight: 600;
}

.status-indicator {
  width: 12px;
  height: 12px;
  border-radius: 50%;
  display: inline-block;
}

.status-indicator.unknown {
  background-color: #888;
}

.status-indicator.checking {
  background-color: var(--color-warning, #FFBD2E);
  animation: pulse 1s infinite alternate;
}

.status-indicator.connected {
  background-color: var(--color-success, #9DBEB6);
}

.status-indicator.error {
  background-color: var(--color-danger, #FF6B6B);
}

.checker-content {
  padding: 1.25rem;
  color: var(--color-text-primary, #e0e0e0);
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
  color: var(--color-success, #9DBEB6);
}

.status-message.checking {
  color: var(--color-warning, #FFBD2E);
}

.status-message.error {
  color: var(--color-danger, #FF6B6B);
}

.loading-spinner {
  display: inline-block;
  width: 16px;
  height: 16px;
  border: 2px solid rgba(255, 255, 255, 0.2);
  border-radius: 50%;
  border-top-color: var(--color-warning, #FFBD2E);
  animation: spin 1s ease-in-out infinite;
}

/* Información de conexión */
.connection-info {
  background-color: var(--color-bg-element-alt, #25252A);
  border-radius: var(--border-radius-sm, 6px);
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
  color: var(--color-text-secondary, #9090A0);
  min-width: 80px;
}

.info-value {
  color: var(--color-primary, #EBB300);
  font-family: monospace;
  word-break: break-all;
}

/* Sección de detalles */
.details-section {
  margin-top: 1.25rem;
  border: 1px solid var(--color-border, #36363c);
  border-radius: var(--border-radius-sm, 6px);
  overflow: hidden;
}

.details-header {
  display: flex;
  justify-content: center;
  align-items: center;
  padding: 0.75rem;
  background-color: var(--color-bg-element-alt, #25252A);
  cursor: pointer;
  user-select: none;
  transition: background-color 0.2s ease;
  font-weight: 500;
}

.details-header:hover {
  background-color: var(--color-bg-element-hover, #32323A);
}

.details-content {
  padding: 1rem;
  background-color: var(--color-bg-main, #1C1C21);
  overflow-x: auto;
  max-height: 250px;
  overflow-y: auto;
}

.details-content pre {
  margin: 0;
  font-family: monospace;
  font-size: 0.85rem;
  color: var(--color-text-secondary, #e0e0e0);
  background-color: #1B1B1F;
}

/* Mensajes de error */
.error-message {
  margin-top: 1.25rem;
  padding: 1rem;
  background-color: rgba(255, 107, 107, 0.1);
  border-left: 3px solid var(--color-danger, #FF6B6B);
  border-radius: var(--border-radius-sm, 6px);
}

.error-message h4 {
  margin: 0 0 0.5rem 0;
  color: var(--color-danger, #FF6B6B);
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
  color: var(--color-text-muted, #9090A0);
  font-style: italic;
}

/* Acciones */
.checker-actions {
  display: flex;
  gap: 1rem;
  padding: 1rem 1.25rem;
  border-top: 1px solid var(--color-border, #36363c);
  background-color: var(--color-bg-element-alt, #25252A);
}

.action-button {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.5rem;
  padding: 0.6rem 1.25rem;
  background-color: var(--color-primary, #EBB300);
  color: var(--color-bg-main, #1C1C21);
  border: none;
  border-radius: var(--border-radius-sm, 6px);
  font-size: 0.95rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s ease;
  text-decoration: none;
}

.action-button:hover:not(:disabled) {
  background-color: var(--color-primary-light, #FFD03F);
  transform: translateY(-2px);
  box-shadow: var(--shadow-sm, 0 2px 6px rgba(0, 0, 0, 0.1));
}

.action-button:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.action-button.secondary {
  background-color: var(--color-bg-main, #1C1C21);
  color: var(--color-text-primary, #ffffff);
  border: 1px solid var(--color-border, #36363c);
}

.action-button.secondary:hover {
  background-color: var(--color-bg-element-hover, #32323A);
  border-color: var(--color-primary, #EBB300);
}

.button-icon {
  font-size: 1.1rem;
}

/* Animaciones */
@keyframes pulse {
  from { opacity: 0.6; }
  to { opacity: 1; }
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

/* Responsive */
@media screen and (max-width: 600px) {
  .checker-actions {
    flex-direction: column;
  }
  
  .action-button {
    width: 100%;
  }
}
</style>