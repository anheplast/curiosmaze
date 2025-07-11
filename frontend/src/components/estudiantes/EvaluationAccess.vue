<!-- components/EvaluationAccess.vue Estudiantes ingresan a la evaluacion -->
<template>
  <div class="access-container">
    <div class="access-card">
      <div class="card-header">
        <div class="logo-container">
          <img src="../../public/logo/Logo-CuriosMaze-40x40.png" alt="Logo de CuriosMaze" class="logo" />
        </div>
        <h1 class="title">Acceso a Evaluación</h1>
      </div>
      
      <div class="student-info">
        <span class="student-icon">👤</span>
        <h2>Estudiante: <span class="student-name">{{ studentName }}</span></h2>
      </div>

      <!-- Paso 1: Introducir clave de acceso -->
      <div v-if="!evaluationLoaded" class="access-step">
        <div class="instructions">
          <div class="instruction-icon">🔑</div>
          <p>Ingresa la clave de acceso proporcionada por tu profesor para comenzar tu evaluación.</p>
        </div>
        
        <div class="access-form">
          <label for="accessKey">
            <span class="form-icon">🔐</span>
            Clave de acceso:
          </label>
          <div class="input-container" :class="{ 'has-error': hasError }">
            <input 
              type="password" 
              id="accessKey" 
              v-model="accessKey" 
              placeholder="Ej: XYZ123" 
              @keyup.enter="validateAccess"
              :disabled="isLoading"
            />
          </div>
          <p v-if="hasError" class="error-message">
            <span class="error-icon">⚠️</span>
            {{ errorMessage }}
          </p>
        </div>
        
        <div class="actions">
          <button @click="validateAccess" class="access-button" :disabled="isLoading || !accessKey">
            <span class="button-icon">{{ isLoading ? '⏳' : '✅' }}</span>
            {{ isLoading ? 'Validando...' : 'Validar Clave' }}
          </button>
        </div>
      </div>

      <!-- Paso 2: Mostrar información de la evaluación -->
      <div v-else class="evaluation-step">
        <div class="evaluation-info">
          <div class="evaluation-header">
            <span class="evaluation-icon">📝</span>
            <h3>{{ evaluationData.title }}</h3>
          </div>
          
          <div class="info-details">
            <div class="info-item">
              <span class="info-icon">⏱️</span>
              <p><strong>Duración:</strong> {{ evaluationData.duration }} minutos</p>
            </div>
            
            <!-- Añadido: Mostrar fechas de inicio y fin -->
            <div class="info-item">
              <span class="info-icon">🕒</span>
              <p><strong>Inicia:</strong> {{ formatDateTime(evaluationData.startDate) }}</p>
            </div>
            
            <div class="info-item" v-if="evaluationData.closeDate">
              <span class="info-icon">📅</span>
              <p><strong>Finaliza:</strong> {{ formatDateTime(evaluationData.closeDate) }}</p>
            </div>
            
            <!-- Añadido: Mostrar estado actual de la evaluación -->
            <div class="info-item">
              <span class="info-icon">📊</span>
              <p>
                <strong>Estado:</strong> 
                <span class="estado-badge" :class="evaluationState.class">
                  {{ evaluationState.label }}
                </span>
              </p>
            </div>
            
            <div class="info-item description">
              <span class="info-icon">📋</span>
              <p><strong>Descripción:</strong> {{ evaluationData.description || 'No hay descripción disponible' }}</p>
            </div>
          </div>
        </div>
        
        <div class="instructions ready" :class="{'disabled': !canStartEvaluation}">
          <div class="instruction-icon" :class="{'pulse': canStartEvaluation}">
            {{ canStartEvaluation ? '🚀' : '⏳' }}
          </div>
          <div>
            <p v-if="!canStartEvaluation" class="hint warning">
              {{ evaluationStateMessage }}
            </p>
            <p v-else class="hint">
              Una vez que ingreses, el cronómetro comenzará automáticamente.
            </p>
            <p v-if="canStartEvaluation" class="ready-text">¿Estás listo para comenzar?</p>
          </div>
        </div>
        
        <div class="actions dual">
          <button 
            @click="startEvaluation" 
            class="start-button"
            :disabled="!canStartEvaluation || isLoading"
            :class="{'disabled': !canStartEvaluation}"
          >
            <span class="button-icon">{{ isLoading ? '⏳' : '▶️' }}</span>
            {{ isLoading ? 'Cargando...' : 'Comenzar Evaluación' }}
          </button>
          <button @click="resetAccess" class="cancel-button" :disabled="isLoading">
            <span class="button-icon">↩️</span>
            Cambiar clave
          </button>
        </div>
      </div>
      
    </div>
  </div>
</template>
  
<script>
import { ref, computed, onMounted, watch, onBeforeUnmount } from 'vue';
import { useStore } from 'vuex';
import { useRouter } from 'vue-router';
import evaluationsService from '@/api/evaluationsService';

export default {
  name: 'EvaluationAccess',
  setup() {
    const store = useStore();
    const router = useRouter();

    // Estados
    const accessKey = ref('');
    const hasError = ref(false);
    const errorMessage = ref('');
    const studentName = ref('');
    const isLoading = ref(false);
    const evaluationLoaded = ref(false);
    const evaluationData = ref({
      id: null,
      title: '',
      duration: 0,
      attempts: 1,
      startDate: '',
      closeDate: '',
      description: '',
      state: ''
    });

    // Cargar datos del estudiante al montar el componente
    onMounted(() => {
      // Obtener nombre del estudiante del store
      studentName.value = store.getters['auth/userName'] || 'Estudiante';

      // Verificar que el usuario sea estudiante
      const userRole = store.getters['auth/userRole'];
      if (userRole !== 'estudiante') {
        router.push('/');
      }
      
      // Iniciar reloj para actualizar estados
      startStatusClock();
    });
    
    // Reloj para actualizar el estado de la evaluación cada minuto
    let statusInterval = null;
    const startStatusClock = () => {
      // Actualizar inmediatamente
      updateEvaluationState();
      
      // Luego actualizar cada minuto
      statusInterval = setInterval(() => {
        updateEvaluationState();
      }, 60000); // cada minuto
    };
    
    // Limpiar el intervalo cuando el componente se destruye
    onBeforeUnmount(() => {
      if (statusInterval) {
        clearInterval(statusInterval);
      }
    });

    // Validar código de acceso
    const validateAccess = async () => {
      if (!accessKey.value) {
        hasError.value = true;
        errorMessage.value = 'Por favor, ingresa la clave de acceso.';
        return;
      }

      try {
        isLoading.value = true;
        hasError.value = false;

        console.log('Validando código de acceso:', accessKey.value);

        // Usar el servicio de evaluaciones
        const response = await evaluationsService.validarCodigoAcceso(accessKey.value);
        const data = response.data;

        console.log('Respuesta de validación:', data);

        if (data && data.valid) {
          // Asegurarnos de interpretar las fechas correctamente ajustando la zona horaria
          const now = new Date();
          
          const startDateStr = data.evaluation.fecha_inicio;
          const endDateStr = data.evaluation.fecha_fin;
          
          console.log('Fecha de inicio (string):', startDateStr);
          console.log('Fecha de fin (string):', endDateStr || 'No establecida');
          
          // Parseamos las fechas aplicando el ajuste de zona horaria
          const startDate = parseDateFromBackend(startDateStr);
          const endDate = endDateStr ? parseDateFromBackend(endDateStr) : null;
          
          console.log('Fecha de inicio (ajustada):', startDate);
          console.log('Fecha de fin (ajustada):', endDate || 'No establecida');
          console.log('Fecha actual:', now);
          
          // Actualizar datos de la evaluación
          evaluationData.value = {
            id: data.evaluation.id,
            title: data.evaluation.titulo || 'Evaluación',
            duration: data.evaluation.duracion_minutos || 60,
            attempts: data.evaluation.attempts || 1,
            startDate: startDate,
            closeDate: endDate,
            description: data.evaluation.descripcion || '',
            ejercicios: data.evaluation.ejercicios || [],
            state: data.evaluation.estado || 'pendiente',
            // Guardar strings originales también por si acaso
            startDateStr: startDateStr,
            endDateStr: endDateStr
          };

          // Guardar información detallada sobre la evaluación
          const evaluationToStore = {
            ...data.evaluation,
            title: data.evaluation.titulo,
            duration: data.evaluation.duracion_minutos
          };

          // Guardar código para reutilización
          localStorage.setItem('temp_access_code', accessKey.value);
          localStorage.setItem('currentEvaluation', JSON.stringify(evaluationToStore));

          // Determinar si la evaluación está disponible
          updateEvaluationState();
          
          // Mostrar la información de la evaluación
          evaluationLoaded.value = true;
        } else {
          hasError.value = true;
          
          // Aquí corregimos el mensaje de error si contiene una fecha y hora incorrecta
          if (data && data.error) {
            // Verificar si el mensaje contiene una fecha en formato "dd/mm/yyyy a las HH:MM"
            const dateTimeRegex = /(\d{2}\/\d{2}\/\d{4}) a las (\d{2}:\d{2})/;
            const match = data.error.match(dateTimeRegex);
            
            if (match) {
              // Extraer la fecha y hora del mensaje
              const dateStr = match[1]; // "dd/mm/yyyy"
              const timeStr = match[2]; // "HH:MM"
              
              // Convertir la hora aplicando un ajuste por zona horaria (-5 horas)
              const [hours, minutes] = timeStr.split(':').map(Number);
              let adjustedHours = hours - 5; // Ajuste de 5 horas (UTC-5)
              
              // Manejar el cambio de día si es necesario
              let adjustedDateStr = dateStr;
              if (adjustedHours < 0) {
                adjustedHours += 24;
                // Necesitaríamos restar un día a la fecha, pero se omite por simplicidad
              }
              
              // Formatear la hora ajustada
              const adjustedTimeStr = `${adjustedHours.toString().padStart(2, '0')}:${minutes.toString().padStart(2, '0')}`;
              
              // Reemplazar la hora en el mensaje original
              errorMessage.value = data.error.replace(timeStr, adjustedTimeStr);
              console.log('Mensaje de error original:', data.error);
              console.log('Mensaje de error ajustado:', errorMessage.value);
            } else {
              errorMessage.value = data.error;
            }
          } else {
            errorMessage.value = 'Clave de acceso incorrecta o evaluación no disponible.';
          }
        }
      } catch (error) {
        console.error('Error al validar código de acceso:', error);
        hasError.value = true;
        
        // Manejar errores 403 que contienen mensajes con fechas de manera similar
        if (error.response && error.response.data) {
          const errorData = error.response.data;
          
          if (errorData.error) {
            // Verificar si el mensaje contiene una fecha en formato "dd/mm/yyyy a las HH:MM"
            const dateTimeRegex = /(\d{2}\/\d{2}\/\d{4}) a las (\d{2}:\d{2})/;
            const match = errorData.error.match(dateTimeRegex);
            
            if (match) {
              // Extraer la fecha y hora del mensaje
              const dateStr = match[1]; // "dd/mm/yyyy"
              const timeStr = match[2]; // "HH:MM"
              
              // Convertir la hora aplicando un ajuste por zona horaria (-5 horas)
              const [hours, minutes] = timeStr.split(':').map(Number);
              let adjustedHours = hours - 5; // Ajuste de 5 horas (UTC-5)
              
              // Manejar el cambio de día si es necesario
              let adjustedDateStr = dateStr;
              if (adjustedHours < 0) {
                adjustedHours += 24;
                // Necesitaríamos restar un día a la fecha, pero lo omitimos por simplicidad
              }
              
              // Formatear la hora ajustada
              const adjustedTimeStr = `${adjustedHours.toString().padStart(2, '0')}:${minutes.toString().padStart(2, '0')}`;
              
              // Reemplazar la hora en el mensaje original
              errorMessage.value = errorData.error.replace(timeStr, adjustedTimeStr);
              console.log('Mensaje de error original:', errorData.error);
              console.log('Mensaje de error ajustado:', errorMessage.value);
            } else {
              errorMessage.value = errorData.error;
            }
          } else {
            errorMessage.value = 'Error al conectar con el servidor. Por favor, intenta nuevamente.';
          }
        } else {
          errorMessage.value = 'Error al conectar con el servidor. Por favor, intenta nuevamente.';
        }
      } finally {
        isLoading.value = false;
      }
    };
    
    // Función para parsear fechas del backend 
    const parseDateFromBackend = (dateString) => {
      if (!dateString) return null;
      
      try {
        // Crear fecha desde la cadena ISO
        const date = new Date(dateString);
        console.log('Fecha parseada:', date, 'desde string:', dateString);
        return date;
      } catch (e) {
        console.error('Error al parsear fecha:', e);
        return new Date(dateString);
      }
    };
    
    // Estado de la evaluación (computed)
    const evaluationState = computed(() => {
      if (!evaluationData.value || !evaluationData.value.startDate) {
        return { label: 'No disponible', class: 'inactive' };
      }
      
      const now = new Date();
      const startDate = evaluationData.value.startDate;
      let endDate = evaluationData.value.closeDate;
      
      // Si hay duración pero no hay fecha de fin explícita, calcularla
      if (!endDate && evaluationData.value.duration) {
        // Crear una nueva fecha basada en startDate
        endDate = new Date(startDate.getTime());
        // Añadir la duración en minutos
        endDate.setMinutes(endDate.getMinutes() + evaluationData.value.duration);
        console.log('Fecha de fin calculada desde duración:', endDate);
      }
      
      console.log('------------ CÁLCULO DE ESTADO ------------');
      console.log('Fecha/hora actual:', now.toLocaleString());
      console.log('Fecha/hora inicio:', startDate.toLocaleString());
      console.log('Fecha/hora fin:', endDate ? endDate.toLocaleString() : 'No especificada');
      
      // Calcular diferencias para debugging
      if (startDate) {
        const msTillStart = startDate.getTime() - now.getTime();
        console.log(`Tiempo hasta inicio: ${Math.round(msTillStart/1000/60)} minutos`);
      }
      
      if (endDate) {
        const msSinceEnd = now.getTime() - endDate.getTime();
        console.log(`Tiempo desde finalización: ${Math.round(msSinceEnd/1000/60)} minutos`);
      }
      
      // Verificación manual para debug
      const isPending = startDate > now;
      const isFinished = endDate && now > endDate;
      const isActive = !isPending && !isFinished;
      
      console.log('¿Está pendiente?', isPending);
      console.log('¿Está finalizada?', isFinished);
      console.log('¿Está activa?', isActive);
      
      // Determinar estado
      if (isPending) {
        return { label: 'Pendiente', class: 'pending' };
      } else if (isFinished) {
        return { label: 'Finalizada', class: 'finished' };
      } else {
        return { label: 'Activa', class: 'active' };
      }
    });
    
    // Mensaje de estado según disponibilidad
    const evaluationStateMessage = computed(() => {
      if (!evaluationData.value.startDate) return 'Información de evaluación no disponible';
      
      const now = new Date();
      const startDate = evaluationData.value.startDate;
      let endDate = evaluationData.value.closeDate;
      
      // Si hay duración pero no hay fecha de fin explícita, calcularla
      if (!endDate && evaluationData.value.duration) {
        // Crear una nueva fecha basada en startDate
        endDate = new Date(startDate.getTime());
        // Añadir la duración en minutos
        endDate.setMinutes(endDate.getMinutes() + evaluationData.value.duration);
      }
      
      // Verificación manual para debug
      const isPending = startDate > now;
      const isFinished = endDate && now > endDate;
      
      if (isPending) {
        return `Esta evaluación aún no está disponible. Comienza el ${formatDateTime(startDate)}.`;
      } else if (isFinished) {
        return `Esta evaluación ya ha finalizado el ${formatDateTime(endDate)}.`;
      }
      
      return '';
    });
    
    // Determinar si se puede iniciar la evaluación
    const canStartEvaluation = computed(() => {
      if (!evaluationData.value.startDate) return false;
      
      const now = new Date();
      const startDate = evaluationData.value.startDate;
      let endDate = evaluationData.value.closeDate;
      
      // Si hay duración pero no hay fecha de fin explícita, calcularla
      if (!endDate && evaluationData.value.duration) {
        // Crear una nueva fecha basada en startDate
        endDate = new Date(startDate.getTime());
        // Añadir la duración en minutos
        endDate.setMinutes(endDate.getMinutes() + evaluationData.value.duration);
      }
      
      // Verificación manual para debugging
      const isAfterStart = now >= startDate;
      const isBeforeEnd = !endDate || now <= endDate;
      const canStart = isAfterStart && isBeforeEnd;
      
      console.log('¿Después del inicio?', isAfterStart);
      console.log('¿Antes del fin?', isBeforeEnd);
      console.log('¿Puede comenzar?', canStart);
      
      // Solo permitir iniciar si la evaluación está activa (ya comenzó pero no ha terminado)
      return canStart;
    });
    
    // Función para actualizar el estado de la evaluación
    const updateEvaluationState = () => {
      if (!evaluationData.value.id) return;
      
      const now = new Date();
      const startDate = evaluationData.value.startDate;
      let endDate = evaluationData.value.closeDate;
      
      // Si hay duración pero no hay fecha de fin explícita, calcularla
      if (!endDate && evaluationData.value.duration) {
        // Crear una nueva fecha basada en startDate
        endDate = new Date(startDate.getTime());
        // Añadir la duración en minutos
        endDate.setMinutes(endDate.getMinutes() + evaluationData.value.duration);
        evaluationData.value.closeDate = endDate; // Guardar la fecha calculada
      }
      
      console.log('Actualizando estado:');
      console.log('Ahora:', now.toLocaleString());
      console.log('Inicio:', startDate.toLocaleString());
      console.log('Fin:', endDate ? endDate.toLocaleString() : 'No especificada');
      
      // Verificación manual para debugging
      const isPending = startDate > now;
      const isFinished = endDate && now > endDate;
      const isActive = !isPending && !isFinished;
      
      console.log('¿Está pendiente?', isPending);
      console.log('¿Está finalizada?', isFinished);
      console.log('¿Está activa?', isActive);
      
      // Actualizar estado basado en las fechas
      if (isPending) {
        evaluationData.value.state = 'pendiente';
      } else if (isFinished) {
        evaluationData.value.state = 'finalizada';
      } else {
        evaluationData.value.state = 'activa';
      }
      
      console.log('Estado actualizado:', evaluationData.value.state);
    };

    // Comenzar la evaluación
    const startEvaluation = async () => {
      if (!evaluationData.value.id) {
        hasError.value = true;
        errorMessage.value = 'No se pudo iniciar la evaluación. Información incompleta.';
        return;
      }
      
      // Forzar una actualización del estado antes de comenzar
      updateEvaluationState();
      
      // Verificar nuevamente que la evaluación esté disponible
      if (!canStartEvaluation.value) {
        hasError.value = true;
        errorMessage.value = evaluationStateMessage.value;
        console.log('No se puede iniciar la evaluación:', evaluationStateMessage.value);
        return;
      }

      try {
        isLoading.value = true;
        console.log('Iniciando evaluación ID:', evaluationData.value.id);

        // Si el usuario está autenticado, registrar inscripción
        if (store.getters['auth/isAuthenticated']) {
          try {
            console.log('Inscribiendo estudiante en evaluación...');
            // Inscribir al estudiante en la evaluación
            const inscriptionResponse = await evaluationsService.inscribirEstudiante(
              evaluationData.value.id,
              { codigo: accessKey.value }
            );
            console.log('Respuesta de inscripción:', inscriptionResponse.data);
          } catch (inscriptionError) {
            console.warn('Error al inscribir estudiante:', inscriptionError);
            // Si el error contiene un mensaje específico sobre la evaluación finalizada o no disponible
            if (inscriptionError.response && inscriptionError.response.data && inscriptionError.response.data.error) {
              hasError.value = true;
              errorMessage.value = inscriptionError.response.data.error;
              isLoading.value = false;
              return; // Detener el proceso si hay un error crítico
            }
            // Continuar aunque falle la inscripción por otros motivos
          }
        }

        // Guardar hora de inicio
        const startTime = new Date().getTime();
        localStorage.setItem('evaluationStartTime', startTime);
        console.log('Hora de inicio guardada:', new Date(startTime).toLocaleString());

        // Redirigir a la vista de ejercicios
        console.log('Redirigiendo a ejercicios con ID:', evaluationData.value.id);
        router.push({
          name: 'PracticalExercises',
          query: { evaluation_id: evaluationData.value.id }
        });
      } catch (error) {
        console.error('Error al iniciar evaluación:', error);
        hasError.value = true;
        errorMessage.value = 'Error al iniciar la evaluación: ' + (error.message || 'Intente nuevamente');
      } finally {
        isLoading.value = false;
      }
    };

    // Resetear para cambiar la clave
    const resetAccess = () => {
      accessKey.value = '';
      evaluationLoaded.value = false;
      hasError.value = false;
      errorMessage.value = '';
    };
    
    // Formatear fecha y hora sin conversiones de zona horaria
    const formatDateTime = (date) => {
      if (!date) return 'No definida';
      
      try {
        // Usamos toLocaleString directamente con la fecha ya parseada correctamente
        return date.toLocaleString('es-ES', {
          day: '2-digit',
          month: '2-digit',
          year: 'numeric',
          hour: '2-digit',
          minute: '2-digit'
        });
      } catch (e) {
        console.error('Error al formatear fecha:', e);
        // Fallback por si hay error
        return date.toString();
      }
    };

    return {
      accessKey,
      hasError,
      errorMessage,
      studentName,
      evaluationData,
      validateAccess,
      isLoading,
      evaluationLoaded,
      startEvaluation,
      resetAccess,
      evaluationState,
      evaluationStateMessage,
      canStartEvaluation,
      formatDateTime
    };
  }
}
</script>
  
<style scoped>
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
  
  /* Paleta de colores con EBB300 como color principal */
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

.access-container {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 100vh;
  background-color: #1C1C21;
  padding: 20px;
  color: var(--color-text-primary);
}

.access-card {
  width: 100%;
  max-width: 600px;
  background-color: #2A2A30;
  border-radius: var(--border-radius-lg);
  box-shadow: var(--shadow-lg);
  padding: 2rem;
  position: relative;
  overflow: hidden;
  border-top: 5px solid var(--color-primary);
}

.card-header {
  display: flex;
  align-items: center;
  margin-bottom: 1.5rem;
  border-bottom: 1px solid var(--color-border);
  padding-bottom: 1rem;
}

.logo-container {
  margin-right: 1.5rem;
  width: 60px;
  height: 60px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 10px;
}

.logo {
  width: 40px;
  height: auto;
}

.title {
  color: var(--color-text-primary);
  margin: 0;
  font-size: 1.8rem;
  font-weight: 600;
  display: flex;
  align-items: center;
  padding-left: 50px;
}

.title-icon {
  margin-right: 0.75rem;
  font-size: 1.5rem;
}

.student-info {
  margin-bottom: 1.5rem;
  display: flex;
  align-items: center;
  background-color: rgba(235, 179, 0, 0.1);
  padding: 0.75rem;
  border-radius: var(--border-radius);
  border-left: 4px solid var(--color-primary);
}

.student-icon {
  font-size: 1.5rem;
  margin-right: 1rem;
}

.student-info h2 {
  font-size: 1.2rem;
  color: var(--color-text-secondary);
  font-weight: 500;
  margin: 0;
}

.student-name {
  color: var(--color-primary);
  font-weight: 600;
}

.access-step, .evaluation-step {
  margin-bottom: 1.25rem;
}

.instructions {
  display: flex;
  align-items: flex-start;
  margin-bottom: 1rem;
  background-color: var(--color-bg-element-alt);
  padding: 1rem;
  border-radius: var(--border-radius);
  border-left: 4px solid var(--color-info);
}

.instructions.ready {
  border-left-color: var(--color-success);
  background-color: rgba(157, 190, 182, 0.1);
  align-items: center;
}

.instructions.ready.disabled {
  border-left-color: var(--color-warning);
  background-color: rgba(255, 189, 46, 0.1);
}

.instruction-icon {
  font-size: 1.75rem;
  margin-right: 0.75rem;
  color: var(--color-info);
}

.instructions.ready .instruction-icon {
  color: var(--color-success);
}

.instructions.ready.disabled .instruction-icon {
  color: var(--color-warning);
}

.instructions p {
  color: var(--color-text-secondary);
  margin: 0.15rem 0;
  font-size: 0.92rem;
  line-height: 1.4;
}

.hint {
  color: var(--color-primary-light);
  font-weight: 500;
}

.hint.warning {
  color: var(--color-warning);
}

.ready-text {
  font-size: 1.1rem;
  color: var(--color-text-primary);
  font-weight: 600;
  margin-top: 0.35rem;
}

.access-form {
  margin-bottom: 1.25rem;
}

.access-form label {
  display: flex;
  align-items: center;
  margin-bottom: 0.5rem;
  color: var(--color-text-primary);
  font-weight: 500;
}

.form-icon {
  margin-right: 0.5rem;
  font-size: 1.25rem;
}

.input-container {
  position: relative;
  margin-bottom: 0.5rem;
}

.input-container input {
  width: 100%;
  padding: 1rem 1.25rem;
  background-color: var(--color-bg-main);
  border: 1px solid var(--color-border);
  border-radius: var(--border-radius);
  color: var(--color-text-primary);
  font-size: 1rem;
  transition: all var(--transition-fast);
}

.input-container input:focus {
  outline: none;
  border-color: var(--color-primary);
  box-shadow: 0 0 0 3px rgba(235, 179, 0, 0.15);
}

.input-container input:disabled {
  opacity: 0.7;
  cursor: not-allowed;
}

.input-container.has-error input {
  border-color: var(--color-danger);
  box-shadow: 0 0 0 3px rgba(255, 107, 107, 0.15);
}

.error-message {
  display: flex;
  align-items: center;
  color: var(--color-danger);
  font-size: 0.9rem;
  margin-top: 0.5rem;
  background-color: rgba(255, 107, 107, 0.1);
  padding: 0.75rem;
  border-radius: var(--border-radius-sm);
  border-left: 3px solid var(--color-danger);
}

.error-icon {
  margin-right: 0.5rem;
  font-size: 1.1rem;
}

.actions {
  display: flex;
  justify-content: center;
  margin-bottom: 1rem;
}

.actions.dual {
  display: flex;
  gap: 1rem;
}

.access-button, .start-button, .cancel-button {
  font-family: inherit;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 0.9rem 1.75rem;
  border-radius: var(--border-radius);
  font-size: 1rem;
  font-weight: 600;
  cursor: pointer;
  transition: all var(--transition-fast);
  border: none;
  min-width: 180px;
}

.button-icon {
  margin-right: 0.75rem;
  font-size: 1.1rem;
}

.access-button {
  background-color: var(--color-primary);
  color: #121212;
  box-shadow: 0 4px 8px rgba(235, 179, 0, 0.25);
}

.access-button:hover:not([disabled]) {
  background-color: var(--color-primary-light);
  transform: translateY(-2px);
  box-shadow: 0 6px 12px rgba(235, 179, 0, 0.3);
}

.access-button[disabled] {
  background-color: #4A4A55;
  color: #9090A0;
  cursor: not-allowed;
  box-shadow: none;
}

.start-button {
  background-color: var(--color-success);
  color: #121212;
  box-shadow: 0 4px 8px rgba(157, 190, 182, 0.25);
}

.start-button:hover:not([disabled]) {
  background-color: #8CB0A8;
  transform: translateY(-2px);
  box-shadow: 0 6px 12px rgba(157, 190, 182, 0.3);
}

.start-button[disabled], .start-button.disabled {
  background-color: #4A4A55;
  color: #9090A0;
  cursor: not-allowed;
  box-shadow: none;
  transform: none;
}

.cancel-button {
  background-color: transparent;
  color: var(--color-text-secondary);
  border: 1px solid var(--color-border);
  flex: 1;
}

.cancel-button:hover:not([disabled]) {
  background-color: var(--color-bg-element-hover);
  color: var(--color-text-primary);
  border-color: var(--color-text-secondary);
}

.cancel-button[disabled] {
  opacity: 0.7;
  cursor: not-allowed;
}

.evaluation-info {
  background-color: var(--color-bg-element-alt);
  border-radius: var(--border-radius);
  padding: 1.25rem;
  margin-bottom: 1rem;
  border-top: 3px solid var(--color-primary);
  box-shadow: var(--shadow-sm);
}

.evaluation-header {
  display: flex;
  align-items: center;
  margin-bottom: 0.75rem;
  padding-bottom: 0.5rem;
  border-bottom: 1px solid var(--color-border);
}

.evaluation-icon {
  font-size: 1.5rem;
  margin-right: 0.75rem;
  color: var(--color-primary);
}

.evaluation-header h3 {
  color: var(--color-primary);
  margin: 0;
  font-size: 1.3rem;
}

.info-details {
  display: flex;
  flex-direction: column;
  gap: 0.35rem;
}

.info-item {
  display: flex;
  align-items: flex-start;
}

.info-icon {
  margin-right: 0.75rem;
  font-size: 1.1rem;
  padding-top: 0.2rem;
}

.info-item p {
  margin: 0;
  font-size: 0.95rem;
  color: var(--color-text-secondary);
  flex: 1;
  word-break: break-word;
  overflow-wrap: break-word;
  max-width: 100%;
}

.info-item strong {
  color: var(--color-text-primary);
  margin-right: 0.25rem;
}

/* Estados de evaluación */
.estado-badge {
  display: inline-block;
  padding: 0.25rem 0.5rem;
  border-radius: 0.25rem;
  font-size: 0.85rem;
  font-weight: 600;
}

.estado-badge.active {
  background-color: rgba(157, 190, 182, 0.2);
  color: var(--color-success);
}

.estado-badge.pending {
  background-color: rgba(255, 189, 46, 0.2);
  color: var(--color-warning);
}

.estado-badge.finished {
  background-color: rgba(255, 107, 107, 0.2);
  color: var(--color-danger);
}

.estado-badge.inactive {
  background-color: rgba(107, 114, 128, 0.2);
  color: var(--color-secondary);
}

/* Animaciones */
.pulse {
  animation: pulse 2s infinite;
}

@keyframes pulse {
  0% {
    transform: scale(1);
  }
  50% {
    transform: scale(1.1);
  }
  100% {
    transform: scale(1);
  }
}

/* Responsive */
@media (max-width: 480px) {
  .access-card {
    padding: 1.5rem;
  }
  
  .card-header {
    flex-direction: column;
    text-align: center;
  }
  
  .logo-container {
    margin-right: 0;
    margin-bottom: 1rem;
  }
  
  .student-info {
    flex-direction: column;
    text-align: center;
  }
  
  .student-icon {
    margin-right: 0;
    margin-bottom: 0.5rem;
  }
  
  .instructions {
    flex-direction: column;
    text-align: center;
  }
  
  .instruction-icon {
    margin-right: 0;
    margin-bottom: 0.75rem;
  }
  
  .actions.dual {
    flex-direction: column;
  }
  
  .info-item {
    flex-direction: column;
    align-items: center;
    text-align: center;
  }
  
  .info-icon {
    margin-right: 0;
    margin-bottom: 0.5rem;
  }
}

/* Mejora para la descripción */
.info-item.description p {
  word-break: break-word;
  overflow-wrap: break-word;
  max-height: 120px;
  overflow-y: auto;
  max-width: 100%;
  padding-right: 8px;
  scrollbar-width: thin;
  scrollbar-color: rgba(54, 54, 60, 0.5) transparent;
}

/* Estilo para scrollbar en navegadores webkit */
.info-item.description p::-webkit-scrollbar {
  width: 3px;
}

.info-item.description p::-webkit-scrollbar-track {
  background: transparent; /* Fondo transparente */
}

.info-item.description p::-webkit-scrollbar-thumb {
  background-color: rgba(54, 54, 60, 0.5); /* Color semitransparente */
  border-radius: 10px; /* Bordes más redondeados */
}

.info-item.description p::-webkit-scrollbar-thumb:hover {
  background-color: rgba(126, 145, 255, 0.4); /* Efecto hover sutil */
}

</style>