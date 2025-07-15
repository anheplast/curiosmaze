<!-- src/components/docentes/student-history/EvaluationDetailsModal.vue -->
<template>
  <div class="details-modal-overlay" @click.self="$emit('close')">
    <div class="details-modal" :class="getScoreColorClass()">
      <div class="modal-header" :class="getScoreColorClass()">
        <h3 class="modal-title">{{ evaluation.titulo || 'Detalles de evaluación' }}</h3>
        <button class="close-button" @click="$emit('close')">×</button>
      </div>

      <div class="modal-content">
        <!-- Resumen de evaluación -->
        <div class="evaluation-summary">
          <div class="summary-grid">
            <div class="score-card" :class="getScoreColorClass()">
              <div class="score-value">{{ formatScore() }}</div>
              <div class="score-label">{{ getScoreLabel() }}</div>
              <!--<div class="total-points">{{ getTotalScore() }} pts</div>-->
            </div>
            
            <div class="meta-card">
              <div class="meta-item">
                <div class="meta-icon">📅</div>
                <div class="meta-content">
                  <div class="meta-label">Fecha</div>
                  <div class="meta-value">{{ formatDate(evaluation.fecha_fin) }}</div>
                </div>
              </div>
              
              <div class="meta-item">
                <div class="meta-icon">⏱️</div>
                <div class="meta-content">
                  <div class="meta-label">Duración</div>
                  <div class="meta-value">{{ formatTime(evaluation.tiempo_total) }}</div>
                </div>
              </div>
              
              <div class="meta-item">
                <div class="meta-icon">✅</div>
                <div class="meta-content">
                  <div class="meta-label">Ejercicios completados</div>
                  <div class="meta-value">{{ getCompletedCount() }}</div>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- Lista de ejercicios -->
        <div class="exercises-section">
          <h4 class="section-title">
            <span class="section-icon">📝</span>
            Ejercicios
          </h4>

          <div class="exercises-list">
            <div v-for="(ejercicio, index) in getExercises()" :key="index" class="exercise-item"
              :class="[ejercicio.es_correcta ? 'correct' : 'incorrect', 'exercise-' + index]">
              <div class="exercise-header">
                <div class="exercise-status">
                  <span class="status-icon">{{ ejercicio.es_correcta ? '✓' : '✗' }}</span>
                </div>
                <div class="exercise-title">
                  {{ ejercicio.titulo || ejercicio.ejercicio_titulo || `Ejercicio ${index + 1}` }}
                </div>
                <div class="exercise-score">
                  {{ ejercicio.puntaje_obtenido || 0 }}/{{ ejercicio.puntaje_maximo || ejercicio.puntaje || 30 }}
                </div>
              </div>

              <div class="exercise-content">
                <div v-if="ejercicio.descripcion" class="exercise-description">
                  {{ ejercicio.descripcion }}
                </div>

                <div v-if="ejercicio.etiquetas && ejercicio.etiquetas.length > 0" class="exercise-tags">
                  <span v-for="(tag, tagIndex) in ejercicio.etiquetas" :key="tagIndex" class="exercise-tag">
                    {{ tag }}
                  </span>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <div class="modal-footer">
        <button class="action-button secondary" @click="$emit('close')">
          Cerrar
        </button>
        <button class="action-button primary" @click="viewFullEvaluation">
          <span class="button-icon">🔍</span>
          Ver evaluación completa
        </button>
      </div>
    </div>
  </div>
</template>

<script>
import { computed } from 'vue';

export default {
  name: 'EvaluationDetailsModal',
  props: {
    evaluation: {
      type: Object,
      required: true
    }
  },
  emits: ['close', 'view-full'],
  setup(props, { emit }) {
    // Obtener ejercicios/respuestas de la evaluación
    const getExercises = () => {
      console.log('🔍 getExercises - Evaluación completa:', props.evaluation);

      // 1. Buscar en respuestas directas
      if (props.evaluation.respuestas && Array.isArray(props.evaluation.respuestas) && props.evaluation.respuestas.length > 0) {
        console.log('✅ Encontradas respuestas directas:', props.evaluation.respuestas.length);
        return props.evaluation.respuestas;
      }

      // 2. Buscar en detalles.respuestas  
      if (props.evaluation.detalles?.respuestas && Array.isArray(props.evaluation.detalles.respuestas) && props.evaluation.detalles.respuestas.length > 0) {
        console.log('✅ Encontradas respuestas en detalles:', props.evaluation.detalles.respuestas.length);
        return props.evaluation.detalles.respuestas;
      }

      // 3. Buscar en detalles_adicionales.respuestas
      if (props.evaluation.detalles_adicionales?.respuestas && Array.isArray(props.evaluation.detalles_adicionales.respuestas) && props.evaluation.detalles_adicionales.respuestas.length > 0) {
        console.log('✅ Encontradas respuestas en detalles_adicionales:', props.evaluation.detalles_adicionales.respuestas.length);
        return props.evaluation.detalles_adicionales.respuestas;
      }

      // 4. Buscar en ejercicios directos
      if (props.evaluation.ejercicios && Array.isArray(props.evaluation.ejercicios) && props.evaluation.ejercicios.length > 0) {
        console.log('✅ Encontrados ejercicios directos:', props.evaluation.ejercicios.length);
        return props.evaluation.ejercicios;
      }

      // 5. FALLBACK: Intentar reconstruir desde localStorage
      console.log('🔄 Intentando reconstruir ejercicios desde localStorage...');
      try {
        const userId = localStorage.getItem('user_id') || 'anonymous';
        const evalId = props.evaluation.evaluacion_id || props.evaluation.id;

        if (evalId) {
          const rawResults = localStorage.getItem(`evaluation_raw_results_${userId}`);
          if (rawResults) {
            const parsed = JSON.parse(rawResults);
            if (parsed.resultados && Array.isArray(parsed.resultados)) {
              console.log('✅ Ejercicios reconstruidos desde localStorage:', parsed.resultados.length);
              return parsed.resultados.map(resultado => ({
                ejercicio_id: resultado.ejercicio_id,
                id: resultado.ejercicio_id,
                titulo: `Ejercicio ${resultado.ejercicio_id}`,
                ejercicio_titulo: `Ejercicio ${resultado.ejercicio_id}`,
                es_correcta: resultado.es_correcto || false,
                puntaje_obtenido: resultado.puntaje_obtenido || 0,
                puntaje_maximo: resultado.puntaje_maximo || 30,
                puntaje: resultado.puntaje_maximo || 30
              }));
            }
          }
        }
      } catch (e) {
        console.warn('Error reconstruyendo desde localStorage:', e);
      }

      console.log('❌ No se encontraron ejercicios en ninguna fuente');
      return [];
    };
    
    // Calcular conteo de ejercicios completados
    const getCompletedCount = () => {
      const exercises = getExercises();

      if (exercises && exercises.length > 0) {
        const completados = exercises.filter(ej => ej.es_correcta || ej.es_correcto).length;
        return `${completados}/${exercises.length}`;
      }

      // Fallback: usar propiedades directas
      if (props.evaluation.completados_count !== undefined && props.evaluation.ejercicios_count !== undefined) {
        return `${props.evaluation.completados_count}/${props.evaluation.ejercicios_count}`;
      }

      // Fallback: usar detalles_adicionales
      if (props.evaluation.detalles_adicionales) {
        const detalles = props.evaluation.detalles_adicionales;
        if (detalles.ejercicios_count !== undefined) {
          // Calcular completados basado en que tiene ejercicios pero respuestas vacías = 0 completados
          const completados = (detalles.respuestas && detalles.respuestas.length > 0) ?
            detalles.respuestas.filter(r => r.es_correcta).length : 0;
          return `${completados}/${detalles.ejercicios_count || 0}`;
        }
      }

      return 'Sin ejercicios';
    };
    
    // Formatear puntuación
    const formatScore = () => {
      let score = 0;

      // 1. Verificar puntaje_sobre_10 directo
      if (props.evaluation.puntaje_sobre_10 !== undefined) {
        score = parseFloat(props.evaluation.puntaje_sobre_10) || 0;
      }
      // 2. Verificar en detalles
      else if (props.evaluation.detalles?.puntaje_sobre_10 !== undefined) {
        score = parseFloat(props.evaluation.detalles.puntaje_sobre_10) || 0;
      }
      // 3. Verificar formattedScore
      else if (props.evaluation.formattedScore) {
        const match = /^([\d.]+)\/10$/.exec(props.evaluation.formattedScore);
        if (match) {
          score = parseFloat(match[1]);
        }
      }
      // 4. Calcular desde puntaje_total/puntaje_maximo
      else if (props.evaluation.puntaje_total !== undefined && props.evaluation.puntaje_maximo !== undefined && props.evaluation.puntaje_maximo > 0) {
        score = (props.evaluation.puntaje_total / props.evaluation.puntaje_maximo) * 10;
      }

      return score.toFixed(2);
    };
    
    // Obtener clase de color según puntuación
    const getScoreColorClass = () => {
      let score = 0;
      
      if (props.evaluation.puntaje_sobre_10 !== undefined) {
        score = parseFloat(props.evaluation.puntaje_sobre_10);
      } else if (props.evaluation.formattedScore !== undefined) {
        score = parseFloat(props.evaluation.formattedScore);
      } else if (props.evaluation.color_clase) {
        return props.evaluation.color_clase;
      }
      
      if (score >= 9) return 'excellent';
      if (score >= 7) return 'good';
      if (score >= 5) return 'average';
      return 'poor';
    };
    
    // Obtener etiqueta de puntuación
    const getScoreLabel = () => {
      let score = 0;
      
      if (props.evaluation.puntaje_sobre_10 !== undefined) {
        score = parseFloat(props.evaluation.puntaje_sobre_10);
      } else if (props.evaluation.formattedScore !== undefined) {
        score = parseFloat(props.evaluation.formattedScore);
      }
      
      // Si hay una etiqueta definida, usarla
      if (props.evaluation.formattedScoreDisplay && 
          typeof props.evaluation.formattedScoreDisplay !== 'object') {
        return props.evaluation.formattedScoreDisplay;
      }
      
      if (score >= 9) return '¡Excelente!';
      if (score >= 7) return '¡Muy bien!';
      if (score >= 5) return 'Aprobado';
      return 'Necesita mejorar';
    };
    
    // Formatear fecha
    const formatDate = (dateString) => {
      if (!dateString) return 'No disponible';
      
      try {
        const date = new Date(dateString);
        return date.toLocaleDateString('es-ES', {
          day: '2-digit',
          month: 'long',
          year: 'numeric'
        });
      } catch (e) {
        return 'No disponible';
      }
    };

    // Formatear tiempo
    const formatTime = (timeValue) => {
      console.log(`formatTime recibió: ${timeValue} (tipo: ${typeof timeValue})`);

      if (!timeValue) {
        console.log("Sin valor de tiempo, calculando desde localStorage");
        // Intentar calcular desde localStorage como hace EvaluationCompleted
        try {
          const userId = localStorage.getItem('user_id') || 'anonymous';
          const evalId = evaluation.value?.evaluacion_id || evaluation.value?.id;

          if (evalId) {
            console.log(`Buscando tiempo para evaluación ${evalId}, usuario ${userId}`);

            const startTime = parseInt(localStorage.getItem(`evaluationStartTime_${userId}_${evalId}`) ||
              localStorage.getItem(`evaluationStartTime_${userId}`) || '0');
            const endTime = parseInt(localStorage.getItem(`evaluationEndTime_${userId}`) || '0');

            console.log(`Tiempos encontrados: inicio=${startTime}, fin=${endTime}`);

            if (startTime > 0 && endTime > 0) {
              const duration = endTime - startTime;
              if (duration > 0) {
                console.log(`⏱️ Tiempo calculado desde localStorage: ${duration}ms`);

                const minutes = Math.floor(duration / 60000);
                const seconds = Math.floor((duration % 60000) / 1000);

                const formattedTime = minutes === 0 ? `${seconds} seg` : `${minutes}m ${seconds}s`;
                console.log(`Tiempo formateado: ${formattedTime}`);

                return formattedTime;
              }
            }
          }
        } catch (e) {
          console.warn('Error al recuperar tiempo desde localStorage:', e);
        }

        return 'No disponible';
      }

      let milliseconds;

      // Si es ya un número, usarlo directamente
      if (typeof timeValue === 'number') {
        milliseconds = timeValue;
      }
      // Si es formato HH:MM:SS o string numérico
      else if (typeof timeValue === 'string') {
        milliseconds = parseTimeDuration(timeValue);
      } else {
        return 'No disponible';
      }

      // Formatear igual que EvaluationCompleted
      const minutes = Math.floor(milliseconds / 60000);
      const seconds = Math.floor((milliseconds % 60000) / 1000);

      const formattedTime = minutes === 0 ? `${seconds} seg` : `${minutes}m ${seconds}s`;
      console.log(`Tiempo formateado: ${formattedTime} (${milliseconds}ms)`);

      return formattedTime;
    };
    
    /* Formatear tiempo
    const formatTime = (timeString) => {
      if (!timeString) return 'No disponible';

      try {
        // Si es un número o puede convertirse a número (milisegundos)
        if (!isNaN(timeString) || (typeof timeString === 'string' && !isNaN(parseInt(timeString)))) {
          const durationMs = Number(timeString);
          const minutes = Math.floor(durationMs / 60000);
          const seconds = Math.floor((durationMs % 60000) / 1000);

          if (minutes > 0) {
            return `${minutes}m ${seconds}s`;
          } else {
            return `${seconds}s`;
          }
        }

        // Si es formato HH:MM:SS
        if (typeof timeString === 'string') {
          const parts = timeString.split(':');
          if (parts.length === 3) {
            const hours = parseInt(parts[0]) || 0;
            const minutes = parseInt(parts[1]) || 0;
            const seconds = parseInt(parts[2]) || 0;

            if (hours > 0) {
              return `${hours}h ${minutes}m ${seconds}s`;
            } else if (minutes > 0) {
              return `${minutes}m ${seconds}s`;
            } else {
              return `${seconds}s`;
            }
          }
        }

        // Si no se pudo procesar, intentar extraer duración de localStorage
        try {
          const userId = localStorage.getItem('user_id') || 'anonymous';
          const evalId = evaluation.value?.evaluacion_id || evaluation.value?.id;

          if (evalId) {
            const startTime = parseInt(localStorage.getItem(`evaluationStartTime_${userId}_${evalId}`) ||
              localStorage.getItem(`evaluationStartTime_${userId}`) || '0');
            const endTime = parseInt(localStorage.getItem(`evaluationEndTime_${userId}`) || '0');

            if (startTime > 0 && endTime > 0) {
              const duration = endTime - startTime;
              if (duration > 0) {
                const minutes = Math.floor(duration / 60000);
                const seconds = Math.floor((duration % 60000) / 1000);
                return minutes > 0 ? `${minutes}m ${seconds}s` : `${seconds}s`;
              }
            }
          }
        } catch (e) {
          console.warn('Error al recuperar tiempo desde localStorage:', e);
        }

        return String(timeString);
      } catch (e) {
        console.warn('Error al formatear tiempo:', e);
        return 'No disponible';
      }
    };
    */
    
    // Ver evaluación completa
    const viewFullEvaluation = () => {
      console.log('Solicitando ver evaluación completa');

      let evaluationId = props.evaluation.evaluacion_id || props.evaluation.id;

      if (!evaluationId) {
        console.error('No se encontró ID de evaluación para la vista completa');
        return;
      }

      // Guardar ID del historial para recuperación
      if (props.evaluation.id) {
        localStorage.setItem('view_historial_id', props.evaluation.id);
      }

      emit('view-full', evaluationId);
    };


    // Obtener puntuación total en puntos
    const getTotalScore = () => {
      if (props.evaluation.puntaje_total !== undefined) {
        return `${props.evaluation.puntaje_total}/${props.evaluation.puntaje_maximo || 100}`;
      }
      
      if (props.evaluation.detalles?.puntaje_total !== undefined) {
        return `${props.evaluation.detalles.puntaje_total}/${props.evaluation.detalles.puntaje_maximo || 100}`;
      }
      
      return 'N/A';
    };


    // Función auxiliar para parsear duración de tiempo (idéntica a EvaluationCompleted)
    const parseTimeDuration = (timeString) => {
      console.log(`parseTimeDuration recibió: ${timeString}`);

      if (!timeString) return 0;

      // Si es formato HH:MM:SS
      const parts = timeString.split(':');
      if (parts.length === 3) {
        const hours = parseInt(parts[0]) || 0;
        const minutes = parseInt(parts[1]) || 0;
        const seconds = parseInt(parts[2]) || 0;
        const milliseconds = (hours * 3600 + minutes * 60 + seconds) * 1000;
        console.log(`Tiempo convertido de HH:MM:SS: ${milliseconds}ms`);
        return milliseconds;
      }

      // Si ya es un número en string
      if (!isNaN(timeString)) {
        const milliseconds = parseInt(timeString);
        console.log(`Tiempo ya es número: ${milliseconds}ms`);
        return milliseconds;
      }

      console.log("No se pudo parsear tiempo");
      return 0;
    };
    
    return {
      getExercises,
      getCompletedCount,
      formatScore,
      getScoreColorClass,
      getScoreLabel,
      formatDate,
      formatTime,
      viewFullEvaluation,
      getTotalScore,
    };
  }
};
</script>

<style scoped>
/* =================== OVERLAY Y CONTENEDOR PRINCIPAL =================== */
.details-modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-color: rgba(0, 0, 0, 0.7);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 1000;
  padding: 1rem;
  backdrop-filter: blur(4px);
}

.details-modal {
  background-color: var(--color-bg-element-alt);
  border-radius: var(--border-radius-lg);
  width: 90%;
  max-width: 800px;
  max-height: 90vh;
  box-shadow: var(--shadow-xl);
  display: flex;
  flex-direction: column;
  border: 1px solid var(--color-border);
  overflow: hidden;
  animation: modalEnter 0.3s ease-out;
}

.details-modal.excellent {
  border-color: var(--color-score-excellent);
}

.details-modal.good {
  border-color: var(--color-score-good);
}

.details-modal.average {
  border-color: var(--color-score-average);
}

.details-modal.poor {
  border-color: var(--color-score-poor);
}

/* =================== HEADER DEL MODAL =================== */
.modal-header {
  padding: 1.2rem 1.5rem;
  display: flex;
  justify-content: space-between;
  align-items: center;
  border-bottom: 1px solid var(--color-border);
  background-color: var(--color-bg-darker);
}

.modal-header.excellent {
  background: linear-gradient(90deg, var(--color-bg-darker), rgba(76, 175, 80, 0.15));
  border-bottom: 1px solid rgba(76, 175, 80, 0.3);
}

.modal-header.good {
  background: linear-gradient(90deg, var(--color-bg-darker), rgba(255, 235, 59, 0.15));
  border-bottom: 1px solid rgba(255, 235, 59, 0.3);
}

.modal-header.average {
  background: linear-gradient(90deg, var(--color-bg-darker), rgba(255, 193, 7, 0.15));
  border-bottom: 1px solid rgba(255, 193, 7, 0.3);
}

.modal-header.poor {
  background: linear-gradient(90deg, var(--color-bg-darker), rgba(244, 67, 54, 0.15));
  border-bottom: 1px solid rgba(244, 67, 54, 0.3);
}

.modal-title {
  margin: 0;
  font-size: 1.3rem;
  color: var(--color-text-secondary);
  font-weight: 600;
}

.close-button {
  background: none;
  border: none;
  font-size: 1.8rem;
  line-height: 1;
  color: var(--color-text-muted);
  cursor: pointer;
  transition: color var(--transition-fast);
  padding: 0;
  margin: 0;
  width: 32px;
  height: 32px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.close-button:hover {
  color: var(--color-text-secondary);
}

/* =================== CONTENIDO DEL MODAL =================== */
.modal-content {
  padding: 1.5rem;
  overflow-y: auto;
  flex: 1;
  margin-left: 0px;
  margin-right: 0px;
}

.modal-content::-webkit-scrollbar,
.exercises-list::-webkit-scrollbar {
  width: 4px;
}

.modal-content::-webkit-scrollbar-track,
.exercises-list::-webkit-scrollbar-track {
  background: transparent;
}

.modal-content::-webkit-scrollbar-thumb,
.exercises-list::-webkit-scrollbar-thumb {
  background: rgba(150, 150, 160, 0.3);
  border-radius: 2px;
}

.modal-content::-webkit-scrollbar-thumb:hover,
.exercises-list::-webkit-scrollbar-thumb:hover {
  background: rgba(150, 150, 160, 0.5);
}

/* =================== RESUMEN DE EVALUACIÓN =================== */
.evaluation-summary {
  margin-bottom: 2rem;
}

.summary-grid {
  display: grid;
  grid-template-columns: 130px 1fr;
  gap: 1.5rem;
}

.score-card {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  background-color: var(--color-bg-darker);
  border-radius: 10px;
  padding: 1.5rem 1rem;
  box-shadow: var(--shadow);
  border-left: 4px solid;
}

.score-card.excellent {
  border-color: var(--color-score-excellent);
}

.score-card.good {
  border-color: var(--color-score-good);
}

.score-card.average {
  border-color: var(--color-score-average);
}

.score-card.poor {
  border-color: var(--color-score-poor);
}

.score-value {
  font-size: 2.2rem;
  font-weight: 700;
  color: var(--color-text-primary);
  text-align: center;
  line-height: 1;
  margin-bottom: 0.5rem;
}

.score-label {
  font-size: 0.9rem;
  color: var(--color-text-muted);
  text-align: center;
  font-weight: 500;
}

.total-points {
  font-size: 0.8rem;
  color: var(--color-text-muted);
  margin-top: 0.5rem;
  text-align: center;
}

/* =================== METADATOS =================== */
.meta-card {
  display: flex;
  flex-direction: column;
  gap: 0.8rem;
  background-color: var(--color-bg-darker);
  border-radius: 10px;
  padding: 1.2rem;
}

.meta-item {
  display: flex;
  align-items: center;
  gap: 1rem;
  padding: 0.5rem;
  border-radius: var(--border-radius);
  transition: background-color var(--transition-fast);
}

.meta-item:hover {
  background-color: var(--color-bg-element-hover);
}

.meta-icon {
  font-size: 1.2rem;
  background-color: rgba(235, 179, 0, 0.1);
  color: var(--color-primary);
  width: 38px;
  height: 38px;
  border-radius: var(--border-radius);
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.meta-content {
  flex: 1;
}

.meta-label {
  font-size: 0.8rem;
  color: var(--color-text-muted);
  margin-bottom: 0.2rem;
}

.meta-value {
  font-size: 1rem;
  color: var(--color-text-secondary);
  font-weight: 500;
}

/* =================== SECCIÓN DE EJERCICIOS =================== */
.exercises-section {
  margin-top: 0.5rem;
}

.section-title {
  font-size: 1.1rem;
  color: var(--color-text-secondary);
  margin-bottom: 1.2rem;
  display: flex;
  align-items: center;
  gap: 0.6rem;
  border-bottom: 1px solid var(--color-border);
  padding-bottom: 0.8rem;
}

.section-icon {
  color: var(--color-primary);
}

.exercises-list {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(340px, 1fr));
  gap: 1rem;
  max-height: 400px;
  overflow-y: auto;
  padding-right: 0.5rem;
}

/* =================== ÍTEMS DE EJERCICIOS =================== */
.exercise-item {
  background-color: var(--color-bg-darker);
  border-radius: 10px;
  overflow: hidden;
  display: flex;
  flex-direction: column;
  box-shadow: var(--shadow-sm);
  transition: transform var(--transition-fast), box-shadow var(--transition-fast);
  border: 1px solid var(--color-border);
}

.exercise-item:hover {
  transform: translateY(-3px);
  box-shadow: var(--shadow-lg);
}

.exercise-item.correct {
  border-left: 4px solid var(--color-score-excellent);
}

.exercise-item.incorrect {
  border-left: 4px solid var(--color-score-poor);
}

.exercise-header {
  display: flex;
  align-items: center;
  padding: 1rem 1.2rem;
  gap: 0.8rem;
  background-color: var(--color-bg-darkest);
  border-bottom: 1px solid var(--color-border-light);
}

.exercise-status {
  width: 28px;
  height: 28px;
  border-radius: var(--border-radius-sm);
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.correct .exercise-status {
  background-color: rgba(76, 175, 80, 0.15);
  color: var(--color-score-excellent);
}

.incorrect .exercise-status {
  background-color: rgba(244, 67, 54, 0.15);
  color: var(--color-score-poor);
}

.exercise-title {
  flex: 1;
  font-weight: 600;
  color: var(--color-text-secondary);
  font-size: 0.95rem;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.exercise-score {
  font-weight: 600;
  color: var(--color-text-muted);
  font-size: 0.9rem;
  padding: 0.2rem 0.5rem;
  background-color: var(--color-bg-darkest);
  border-radius: 4px;
  min-width: 48px;
  text-align: center;
}

.exercise-content {
  display: flex;
  flex-direction: column;
  padding: 1rem;
  flex: 1;
}

.exercise-description {
  color: var(--color-text-muted);
  font-size: 0.9rem;
  margin-bottom: 0.8rem;
  line-height: 1.5;
}

.exercise-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 0.4rem;
  margin-top: auto;
}

.exercise-tag {
  background-color: rgba(235, 179, 0, 0.1);
  color: var(--color-primary);
  padding: 0.15rem 0.5rem;
  border-radius: 4px;
  font-size: 0.75rem;
  font-weight: 500;
}

/* =================== FOOTER DEL MODAL =================== */
.modal-footer {
  padding: 1.2rem 1.5rem;
  display: flex;
  justify-content: flex-end;
  gap: 1rem;
  border-top: 1px solid var(--color-border);
  background-color: var(--color-bg-darker);
}

.action-button {
  padding: 0.7rem 1.2rem;
  border-radius: var(--border-radius);
  font-weight: 600;
  cursor: pointer;
  transition: all var(--transition-fast);
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.action-button.secondary {
  background-color: transparent;
  border: 1px solid var(--color-border);
  color: var(--color-text-secondary);
}

.action-button.primary {
  background-color: var(--color-info);
  border: none;
  color: var(--color-text-primary);
}

.action-button.secondary:hover {
  background-color: var(--color-bg-element-hover);
  transform: translateY(-2px);
}

.action-button.primary:hover {
  background-color: var(--color-info-dark);
  transform: translateY(-2px);
}

.button-icon {
  font-size: 1rem;
}

/* =================== ANIMACIONES =================== */
@keyframes modalEnter {
  from {
    opacity: 0;
    transform: translateY(20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

/* =================== RESPONSIVE =================== */
@media (max-width: 768px) {
  .summary-grid {
    grid-template-columns: 1fr;
  }
  
  .score-card {
    max-width: 100%;
  }
  
  .exercises-list {
    grid-template-columns: 1fr;
  }
}
</style>