<!-- components/student-history/HistoryList.vue -->
<template>
  <div class="history-list">
    <div class="list-header">
      <h3 class="list-title">
        <span class="title-icon">📋</span>
        Evaluaciones
      </h3>

      <div class="filter-container">
        <div class="search-box">
          <input type="text" v-model="searchQuery" placeholder="Buscar evaluación..." class="search-input" />
          <span class="search-icon">🔍</span>
        </div>

        <select v-model="sortOption" class="sort-select">
          <option value="date_desc">Más reciente</option>
          <option value="date_asc">Más antiguo</option>
          <option value="score_desc">Mayor nota</option>
          <option value="score_asc">Menor nota</option>
        </select>
      </div>
    </div>

    <div v-if="isLoading" class="list-loading">
      <div class="loading-spinner"></div>
      <span>Cargando evaluaciones...</span>
    </div>

    <div v-else-if="filteredEvaluations.length === 0" class="list-empty">
      <div class="empty-icon">📝</div>
      <p v-if="searchQuery">No se encontraron evaluaciones con "{{ searchQuery }}"</p>
      <p v-else>No hay evaluaciones disponibles</p>
    </div>

    <div v-else class="evaluation-items">
      <div v-for="evaluation in filteredEvaluations" :key="evaluation.id || evaluation.evaluacion_id"
        class="evaluation-item" :class="{ 'inactive': !isEvaluationActive(evaluation) }"
        @click="selectEvaluation(evaluation)">
        <!-- Status icon y indicator -->
        <div class="item-status" :class="getScoreColorClass(getEvaluationScore(evaluation))">
          <div class="status-indicator">
            <span class="status-icon">{{ getStatusIcon(evaluation) }}</span>
          </div>
        </div>

        <!-- Main content -->
        <div class="item-content">
          <div class="item-title-row">
            <h4 class="item-title">{{ getEvaluationTitle(evaluation) }}</h4>
            <span class="item-score" :class="getScoreColorClass(getEvaluationScore(evaluation))">
              {{ formatScore(getEvaluationScore(evaluation)) }}
            </span>
          </div>

          <div class="item-meta">
            <span class="meta-item">
              <span class="meta-icon">📅</span>
              {{ formatDate(getEvaluationEndDate(evaluation)) }}
            </span>

            <span class="meta-item">
              <span class="meta-icon">⏱️</span>
              {{ formatTime(getEvaluationDuration(evaluation)) }}
            </span>

            <span class="meta-item">
              <span class="meta-icon">✅</span>
              {{ getCompletedExercises(evaluation) }}
            </span>
          </div>
        </div>

        <!-- Actions -->
        <div class="item-actions">
          <button v-if="isTeacherView" class="action-button delete-button" @click.stop="confirmDelete(evaluation)"
            title="Borrar evaluación">
            <span class="action-icon">🗑️</span>
          </button>

          <button class="action-button view-button" @click.stop="selectEvaluation(evaluation)" title="Ver detalles">
            <span class="action-icon">👁️</span>
          </button>
        </div>
      </div>
    </div>

    <!-- Delete confirmation modal -->
    <div v-if="showDeleteModal" class="delete-modal-overlay" @click.self="cancelDelete">
      <div class="delete-modal">
        <h3 class="modal-title">Confirmar eliminación</h3>
        <p class="modal-text">¿Estás seguro de que deseas eliminar la evaluación <strong>{{
          getEvaluationTitle(evaluationToDelete) }}</strong>?</p>
        <p class="modal-warning">Esta acción no se puede deshacer.</p>

        <div class="modal-actions">
          <button class="modal-button cancel" @click="cancelDelete">Cancelar</button>
          <button class="modal-button confirm" @click="deleteEvaluation">Eliminar</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, computed, watch } from 'vue';
import evaluationsService from '@/api/evaluationsService';

export default {
  name: 'HistoryList',
  props: {
    evaluations: {
      type: Array,
      required: true,
      default: () => []
    },
    isLoading: {
      type: Boolean,
      default: false
    },
    isTeacherView: {
      type: Boolean,
      default: false
    }
  },
  emits: ['select-evaluation', 'delete-evaluation', 'evaluation-deleted'],
  setup(props, { emit }) {
    const searchQuery = ref('');
    const sortOption = ref('date_desc');
    const showDeleteModal = ref(false);
    const evaluationToDelete = ref(null);

    // Funciones auxiliares para extraer propiedades de evaluación de forma segura
    const getEvaluationTitle = (evaluation) => {
      if (!evaluation) return 'Evaluación sin título';
      return evaluation.titulo || evaluation.evaluacion_titulo || 'Evaluación sin título';
    };

    const getEvaluationScore = (evaluation) => {
      if (!evaluation) return 0;

      // 1. Verificar puntaje_sobre_10 como número
      if (typeof evaluation.puntaje_sobre_10 === 'number') {
        return evaluation.puntaje_sobre_10;
      }

      // 2. Verificar puntaje_sobre_10 como string
      if (typeof evaluation.puntaje_sobre_10 === 'string' && !isNaN(parseFloat(evaluation.puntaje_sobre_10))) {
        return parseFloat(evaluation.puntaje_sobre_10);
      }

      // 3. Verificar en objeto detalles
      if (evaluation.detalles) {
        if (typeof evaluation.detalles.puntaje_sobre_10 === 'number') {
          return evaluation.detalles.puntaje_sobre_10;
        }

        if (typeof evaluation.detalles.puntaje_sobre_10 === 'string' &&
          !isNaN(parseFloat(evaluation.detalles.puntaje_sobre_10))) {
          return parseFloat(evaluation.detalles.puntaje_sobre_10);
        }

        // Verificar color_clase para calcular aproximado
        if (evaluation.detalles.color_clase) {
          switch (evaluation.detalles.color_clase) {
            case 'excellent': return 9.5;
            case 'good': return 7.5;
            case 'average': return 6.0;
            case 'poor': return 3.0;
          }
        }
      }

      // 4. Verificar formattedScore
      if (evaluation.formattedScore) {
        // Manejar formato "8.5/10"
        const match = /^([\d.]+)\/10$/.exec(evaluation.formattedScore);
        if (match) {
          return parseFloat(match[1]);
        }
        return parseFloat(evaluation.formattedScore) || 0;
      }

      // 5. Calcular desde puntaje total y máximo
      if (evaluation.puntaje_total !== undefined && evaluation.puntaje_maximo !== undefined &&
        evaluation.puntaje_maximo > 0) {
        return (evaluation.puntaje_total / evaluation.puntaje_maximo) * 10;
      }

      // 6. Intentar determinar desde color_clase
      if (evaluation.color_clase) {
        switch (evaluation.color_clase) {
          case 'excellent': return 9.5;
          case 'good': return 7.5;
          case 'average': return 6.0;
          case 'poor': return 3.0;
        }
      }

      // Si llegamos aquí, no se encontró puntaje válido
      return 0;
    };

    const getEvaluationEndDate = (evaluation) => {
      if (!evaluation) return null;

      // Prueba con varios campos de fecha posibles
      return evaluation.fecha_fin ||
        evaluation.fecha_almacenamiento ||
        (evaluation.detalles ? evaluation.detalles.fecha_fin : null);
    };



    // Obtener duración de evaluación - replicando enfoque de EvaluationCompleted
    const getEvaluationDuration = (evaluation) => {
      if (!evaluation) {
        console.log("getEvaluationDuration: evaluación no definida");
        return null;
      }

      console.log(`Obteniendo duración para evaluación ID: ${evaluation.id || evaluation.evaluacion_id}`, evaluation);

      // 1. Intentar leer tiempo_total directamente
      if (evaluation.tiempo_total && evaluation.tiempo_total !== 'null') {
        console.log(`Usando tiempo_total existente: ${evaluation.tiempo_total}`);
        return evaluation.tiempo_total;
      }

      // 2. Intentar calcular desde fechas
      const startDate = evaluation.fecha_inicio;
      const endDate = evaluation.fecha_fin || evaluation.fecha_almacenamiento;

      if (startDate && endDate) {
        try {
          const start = new Date(startDate);
          const end = new Date(endDate);
          const duration = end - start;

          if (!isNaN(duration) && duration > 0) {
            console.log(`Duración calculada desde fechas: ${duration}ms (${start} → ${end})`);
            return duration;
          }
        } catch (e) {
          console.warn("Error al calcular duración desde fechas:", e);
        }
      } else {
        console.log(`No se pudieron obtener fechas válidas: inicio=${startDate}, fin=${endDate}`);
      }

      // 3. Como último recurso, intentar leer desde localStorage (exactamente como EvaluationCompleted)
      try {
        const userId = localStorage.getItem('user_id') || 'anonymous';
        const evalId = evaluation.id || evaluation.evaluacion_id;

        console.log(`Buscando tiempos en localStorage para usuario ${userId}, evaluación ${evalId}`);

        // Primero intentar con formato específico para la evaluación
        let startTime = parseInt(localStorage.getItem(`evaluationStartTime_${userId}_${evalId}`) || '0');
        if (startTime === 0) {
          // Si no hay tiempo específico, intentar con el general
          startTime = parseInt(localStorage.getItem(`evaluationStartTime_${userId}`) || localStorage.getItem('evaluationStartTime') || '0');
        }

        const endTime = parseInt(localStorage.getItem(`evaluationEndTime_${userId}`) || '0');

        console.log(`Tiempos obtenidos: inicio=${startTime}, fin=${endTime}`);

        if (startTime > 0 && endTime > 0) {
          const duration = endTime - startTime;
          if (duration > 0) {
            console.log(`⏱️ Tiempo calculado desde localStorage: ${duration}ms`);
            return duration;
          }
        }
      } catch (e) {
        console.warn("Error al leer tiempos desde localStorage:", e);
      }

      console.log("No se pudo determinar la duración de la evaluación");
      return null;
    };


    const isEvaluationActive = (evaluation) => {
      if (!evaluation) return true;

      // Comprobar la bandera activa explícita
      if (evaluation.evaluacion_activa === false) return false;

      // Comprobar el campo de estado si existe
      if (evaluation.estado === 'finalizada' || evaluation.estado === 'expired') return false;

      return true;
    };

    // Filtrar y ordenar evaluaciones
    const filteredEvaluations = computed(() => {
      let result = [...props.evaluations];

      // Aplicar filtro de búsqueda
      if (searchQuery.value) {
        const query = searchQuery.value.toLowerCase();
        result = result.filter(evaluation => {
          const title = getEvaluationTitle(evaluation).toLowerCase();
          return title.includes(query);
        });
      }

      // Aplicar clasificación
      switch (sortOption.value) {
        case 'date_desc':
          result.sort((a, b) => {
            const dateA = new Date(getEvaluationEndDate(a) || 0);
            const dateB = new Date(getEvaluationEndDate(b) || 0);
            return dateB - dateA;
          });
          break;
        case 'date_asc':
          result.sort((a, b) => {
            const dateA = new Date(getEvaluationEndDate(a) || 0);
            const dateB = new Date(getEvaluationEndDate(b) || 0);
            return dateA - dateB;
          });
          break;
        case 'score_desc':
          result.sort((a, b) => getEvaluationScore(b) - getEvaluationScore(a));
          break;
        case 'score_asc':
          result.sort((a, b) => getEvaluationScore(a) - getEvaluationScore(b));
          break;
      }

      return result;
    });

    // Formato de fecha
    const formatDate = (dateString) => {
      if (!dateString) return 'No disponible';

      try {
        const date = new Date(dateString);
        if (isNaN(date.getTime())) return 'No disponible';

        return date.toLocaleDateString('es-ES', {
          day: '2-digit',
          month: 'short',
          year: 'numeric',
        });
      } catch (e) {
        console.warn('Error formatting date:', e);
        return 'No disponible';
      }
    };


    // Formatear tiempo - igual que en EvaluationCompleted
    const formatTime = (timeValue) => {
      console.log(`formatTime recibió: ${timeValue} (tipo: ${typeof timeValue})`);

      if (!timeValue) {
        return 'No disponible';
      }

      let milliseconds;

      // Si es ya un número, usarlo directamente
      if (typeof timeValue === 'number') {
        milliseconds = timeValue;
      }
      // Si es string que parece número, convertirlo
      else if (typeof timeValue === 'string' && !isNaN(parseInt(timeValue))) {
        milliseconds = parseInt(timeValue);
      }
      // Si es formato HH:MM:SS
      else if (typeof timeValue === 'string' && timeValue.includes(':')) {
        const parts = timeValue.split(':');
        if (parts.length === 3) {
          const hours = parseInt(parts[0]) || 0;
          const minutes = parseInt(parts[1]) || 0;
          const seconds = parseInt(parts[2]) || 0;
          milliseconds = (hours * 3600 + minutes * 60 + seconds) * 1000;
        } else {
          return timeValue; // No se pudo parsear, devolver como está
        }
      } else {
        return String(timeValue); // Otro formato, devolver como string
      }

      // Formatear igual que EvaluationCompleted
      const minutes = Math.floor(milliseconds / 60000);
      const seconds = Math.floor((milliseconds % 60000) / 1000);

      const formattedTime = minutes === 0 ? `${seconds} seg` : `${minutes}m ${seconds}s`;
      console.log(`Tiempo formateado: ${formattedTime} (${milliseconds}ms)`);

      return formattedTime;
    };

    /* Format time
    const formatTime = (timeString) => {
      if (!timeString) return 'No disponible';

      try {
        // 1. Si es un número o puede convertirse a número (milisegundos)
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

        // 2. Si es formato ISO (PT1H30M)
        if (typeof timeString === 'string' && timeString.startsWith('P')) {
          const hours = timeString.match(/(\d+)H/);
          const minutes = timeString.match(/(\d+)M/);
          const seconds = timeString.match(/(\d+)S/);

          let result = '';
          if (hours) result += `${hours[1]}h `;
          if (minutes) result += `${minutes[1]}m `;
          if (seconds) result += `${seconds[1]}s`;

          return result.trim() || 'No disponible';
        }

        // 3. Si es formato HH:MM:SS
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

        // Para cualquier otro formato, mostrar como está
        return String(timeString);
      } catch (e) {
        console.warn('Error al formatear tiempo:', e);
        return 'No disponible';
      }
    };
    */

    // Formato de puntuación
    const formatScore = (score) => {
      if (score === undefined || score === null) return 'N/A';
      const numScore = parseFloat(score);
      return isNaN(numScore) ? 'N/A' : numScore.toFixed(2);
    };

    // Obtener clase de color en función de la puntuación
    const getScoreColorClass = (score) => {
      if (!score) return 'poor';
      score = parseFloat(score);
      if (isNaN(score)) return 'poor';
      if (score >= 9) return 'excellent';
      if (score >= 7) return 'good';
      if (score >= 5) return 'average';
      return 'poor';
    };

    // Obtener el icono de estado en función de la puntuación
    const getStatusIcon = (evaluation) => {
      if (!isEvaluationActive(evaluation)) return '⚡'; // Cambiado de 🔄 a ⚡ para evaluaciones inactivas

      const score = getEvaluationScore(evaluation);
      if (score >= 9) return '💯'; // Cambiado de 🌟 a 💯 para puntuaciones excelentes
      if (score >= 7) return '👍'; // Cambiado de ⭐ a 👍 para puntuaciones buenas
      if (score >= 5) return '✓'; // Mantenido para puntuaciones aceptables
      return '❗'; // Cambiado de ✗ a ❗ para puntuaciones bajas
    };

    // Obtener cantidad de ejercicios completados
    const getCompletedExercises = (evaluation) => {
      if (!evaluation) return 'N/A';

      // Si tenemos contadores explícitos, se usan
      if (evaluation.completados_count !== undefined && evaluation.ejercicios_count !== undefined) {
        return `${evaluation.completados_count}/${evaluation.ejercicios_count}`;
      }

      // Intenta obtener de detalles
      if (evaluation.detalles) {
        if (evaluation.detalles.completados_count !== undefined &&
          evaluation.detalles.ejercicios_count !== undefined) {
          return `${evaluation.detalles.completados_count}/${evaluation.detalles.ejercicios_count}`;
        }
      }

      // Contar a partir de respuestas
      let respuestas = [];

      if (evaluation.respuestas && Array.isArray(evaluation.respuestas)) {
        respuestas = evaluation.respuestas;
      } else if (evaluation.detalles && evaluation.detalles.respuestas &&
        Array.isArray(evaluation.detalles.respuestas)) {
        respuestas = evaluation.detalles.respuestas;
      }

      if (respuestas.length > 0) {
        const completados = respuestas.filter(respuesta => respuesta.es_correcta).length;
        return `${completados}/${respuestas.length}`;
      }

      return 'N/A';
    };

    // Seleccionar evaluación
    const selectEvaluation = (evaluation) => {
      emit('select-evaluation', evaluation);
    };

    // Confirmar eliminación
    const confirmDelete = (evaluation) => {
      evaluationToDelete.value = evaluation;
      showDeleteModal.value = true;
    };

    // Cancelar la eliminación
    const cancelDelete = () => {
      evaluationToDelete.value = null;
      showDeleteModal.value = false;
    };

    // Borrar evaluación
    const deleteEvaluation = async () => {
      if (!evaluationToDelete.value) return;

      try {
        const evaluationId = evaluationToDelete.value.id ||
          evaluationToDelete.value.evaluacion_id;

        console.log(`Eliminando evaluación: ${evaluationId}`);

        if (!evaluationId) {
          throw new Error('ID de evaluación no disponible');
        }

        try {
          // Intentar eliminar de evaluaciones
          await evaluationsService.eliminarEvaluacion(evaluationId);
          console.log(`Evaluación ${evaluationId} eliminada correctamente`);
        } catch (apiError) {
          // Si falla, probablemente es porque solo existe en historial
          console.warn(`No se pudo eliminar la evaluación ${evaluationId} del servidor:`, apiError);
          alert("Esta evaluación solo existe en el historial y no se puede eliminar directamente.");
        }

        // Independientemente del resultado de la API, eliminar del estado local
        emit('evaluation-deleted', evaluationToDelete.value);

        // Cerrar modal
        showDeleteModal.value = false;
        evaluationToDelete.value = null;
      } catch (error) {
        console.error('Error al eliminar evaluación:', error);
        // Cerrar modal
        showDeleteModal.value = false;
        evaluationToDelete.value = null;
      }
    };

    // Reiniciar la búsqueda cuando cambien las evaluaciones
    watch(() => props.evaluations.length, () => {
      searchQuery.value = '';
    });

    return {
      searchQuery,
      sortOption,
      filteredEvaluations,
      showDeleteModal,
      evaluationToDelete,
      formatDate,
      formatTime,
      formatScore,
      getScoreColorClass,
      getStatusIcon,
      getCompletedExercises,
      selectEvaluation,
      confirmDelete,
      cancelDelete,
      deleteEvaluation,
      getEvaluationTitle,
      getEvaluationScore,
      getEvaluationEndDate,
      getEvaluationDuration,
      isEvaluationActive
    };
  }
};
</script>

<style scoped>
.history-list {
  background-color: #2A2A35;
  border-radius: 12px;
  padding: 1.2rem;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
  border: 1px solid #36363C;
  height: 100%;
  display: flex;
  flex-direction: column;
}

.list-header {
  display: flex;
  flex-direction: column;
  gap: 1rem;
  margin-bottom: 1.2rem;
  border-bottom: 1px solid #36363C;
  padding-bottom: 1rem;
}

.list-title {
  font-size: 1.1rem;
  font-weight: 600;
  color: #E0E0E0;
  margin: 0;
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.title-icon {
  color: #EBB300;
}

.filter-container {
  display: flex;
  gap: 0.8rem;
  width: 100%;
}

.search-box {
  flex: 1;
  position: relative;
}

.search-input {
  width: 100%;
  padding: 0.6rem 1rem 0.6rem 2.5rem;
  border-radius: 8px;
  background-color: #1F1F26;
  border: 1px solid #36363C;
  color: #E0E0E0;
  font-size: 0.9rem;
  transition: all 0.2s;
}

.search-input:focus {
  outline: none;
  border-color: #EBB300;
  box-shadow: 0 0 0 2px rgba(235, 179, 0, 0.2);
}

.search-icon {
  position: absolute;
  left: 0.8rem;
  top: 50%;
  transform: translateY(-50%);
  color: #9090A0;
  font-size: 0.9rem;
}

.sort-select {
  padding: 0.6rem 1rem;
  border-radius: 8px;
  background-color: #1F1F26;
  border: 1px solid #36363C;
  color: #E0E0E0;
  font-size: 0.9rem;
  cursor: pointer;
  transition: all 0.2s;
  appearance: none;
  background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='16' height='16' viewBox='0 0 24 24' fill='none' stroke='%239090A0' stroke-width='2' stroke-linecap='round' stroke-linejoin='round'%3E%3Cpath d='M6 9l6 6 6-6'/%3E%3C/svg%3E");
  background-repeat: no-repeat;
  background-position: right 0.7rem center;
  padding-right: 2.5rem;
}

.sort-select:focus {
  outline: none;
  border-color: #EBB300;
  box-shadow: 0 0 0 2px rgba(235, 179, 0, 0.2);
}

.evaluation-items {
  display: flex;
  flex-direction: column;
  gap: 0.8rem;
  overflow-y: auto;
  flex: 1;
  padding-right: 0.3rem;
}

.evaluation-items::-webkit-scrollbar {
  width: 6px;
}

.evaluation-items::-webkit-scrollbar-track {
  background: #1F1F26;
  border-radius: 3px;
}

.evaluation-items::-webkit-scrollbar-thumb {
  background: #36363C;
  border-radius: 3px;
}

.evaluation-items::-webkit-scrollbar-thumb:hover {
  background: #44444D;
}

.evaluation-item {
  display: flex;
  align-items: center;
  background-color: #25252D;
  border-radius: 10px;
  border: 1px solid #36363C;
  padding: 0.8rem 1rem;
  cursor: pointer;
  transition: all 0.2s;
  position: relative;
  overflow: hidden;
}

.evaluation-item:hover {
  transform: translateY(-3px);
  box-shadow: 0 6px 15px rgba(0, 0, 0, 0.2);
  border-color: #44444D;
}

.evaluation-item.inactive {
  opacity: 0.85;
  border-color: #36363C;
}

.item-status {
  margin-right: 1rem;
}

.status-indicator {
  width: 40px;
  height: 40px;
  border-radius: 6px; /* Reducido de 50% (círculo) a 6px (esquinas redondeadas) */
  display: flex;
  align-items: center;
  justify-content: center;
  background-color: #1F1F26;
  border: 2px solid;
  border-color: currentColor;
  font-size: 1.2rem;
}

.status-indicator.excellent {
  border-color: #4CAF50;
}

.status-indicator.good {
  border-color: #FFEB3B;
}

.status-indicator.average {
  border-color: #FFC107;
}

.status-indicator.poor {
  border-color: #F44336;
}

.item-content {
  flex: 1;
  min-width: 0;
}

.item-title-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 0.5rem;
}

.item-title {
  margin: 0;
  font-size: 1.05rem;
  font-weight: 600;
  color: #E0E0E0;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  flex: 1;
  margin-right: 1rem;
}

.item-score {
  font-size: 1.1rem;
  font-weight: 700;
  padding: 0.15rem 0.6rem;
  border-radius: 4px;
  background-color: #1F1F26;
}

.item-score.excellent {
  color: #4CAF50;
}

.item-score.good {
  color: #FFEB3B;
}

.item-score.average {
  color: #FFC107;
}

.item-score.poor {
  color: #F44336;
}

.item-meta {
  display: flex;
  gap: 1rem;
  font-size: 0.85rem;
  color: #9090A0;
}

.meta-item {
  display: flex;
  align-items: center;
  gap: 0.3rem;
}

.meta-icon {
  font-size: 0.9rem;
}

.item-actions {
  display: flex;
  gap: 0.5rem;
  margin-left: 1rem;
}

.action-button {
  width: 32px;
  height: 32px;
  border-radius: 4px; /* Reducido de 50% (círculo) a 4px (esquinas ligeramente redondeadas) */
  display: flex;
  align-items: center;
  justify-content: center;
  border: none;
  cursor: pointer;
  transition: all 0.2s;
  font-size: 0.9rem;
  background-color: #36363C;
  color: #E0E0E0;
}

.action-button:hover {
  transform: translateY(-2px);
}

.view-button:hover {
  background-color: #3F51B5;
  color: white;
}

.delete-button:hover {
  background-color: #D32F2F;
  color: white;
}

.list-loading,
.list-empty {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 3rem;
  color: #9090A0;
  text-align: center;
  flex: 1;
}

.loading-spinner {
  width: 40px;
  height: 40px;
  border: 4px solid #36363C;
  border-top-color: #EBB300;
  border-radius: 50%;
  animation: spin 1s linear infinite;
  margin-bottom: 1rem;
}

.empty-icon {
  font-size: 3rem;
  margin-bottom: 1rem;
  opacity: 0.5;
}

@keyframes spin {
  to {
    transform: rotate(360deg);
  }
}

/* Deletion modal */
.delete-modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-color: rgba(0, 0, 0, 0.6);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 1000;
  backdrop-filter: blur(4px);
}

.delete-modal {
  background-color: #25252D;
  border-radius: 12px;
  padding: 1.5rem;
  width: 90%;
  max-width: 400px;
  box-shadow: 0 10px 25px rgba(0, 0, 0, 0.3);
  border: 1px solid #36363C;
  animation: modalFadeIn 0.2s ease-out;
}

.modal-title {
  margin-top: 0;
  margin-bottom: 1rem;
  color: #E0E0E0;
  font-size: 1.2rem;
  border-bottom: 1px solid #36363C;
  padding-bottom: 0.8rem;
}

.modal-text {
  color: #E0E0E0;
  margin-bottom: 0.8rem;
}

.modal-warning {
  color: #F44336;
  margin-bottom: 1.5rem;
  font-size: 0.9rem;
}

.modal-actions {
  display: flex;
  justify-content: flex-end;
  gap: 1rem;
}

.modal-button {
  padding: 0.6rem 1.2rem;
  border-radius: 6px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s;
}

.modal-button.cancel {
  background-color: transparent;
  border: 1px solid #36363C;
  color: #E0E0E0;
}

.modal-button.confirm {
  background-color: #D32F2F;
  border: none;
  color: white;
}

.modal-button.cancel:hover {
  background-color: rgba(255, 255, 255, 0.05);
}

.modal-button.confirm:hover {
  background-color: #F44336;
}

@keyframes modalFadeIn {
  from {
    opacity: 0;
    transform: translateY(-10px);
  }

  to {
    opacity: 1;
    transform: translateY(0);
  }
}

/* Responsive */
@media (max-width: 768px) {
  .filter-container {
    flex-direction: column;
  }

  .item-meta {
    flex-wrap: wrap;
    gap: 0.5rem;
  }
}
</style>