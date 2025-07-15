<!-- src/views/EvaluationHistoryView.vue -->
<template>
  <div class="history-page">
    <!-- Botón para volver atrás - Actualizado para ser como LoginEvaluationView -->
    <button class="back-button" @click="goBack" title="Volver al dashboard">
      <i class="fas fa-arrow-left"></i>
    </button>

    <div class="history-container">
      <!-- Cabecera con datos del estudiante -->
      <div class="page-header">
        <h1 class="page-title">
          <span class="title-icon">📚</span>
          {{ isTeacherView ? `Historial de: ${studentName}` : 'Tu Historial de Evaluaciones' }}
        </h1>
        
        <div class="header-stats" v-if="evaluations.length > 0">
          <div class="stat-pill">
            <span class="stat-icon">📝</span>
            <span class="stat-value">{{ evaluations.length }}</span>
            <span class="stat-label">Evaluaciones</span>
          </div>
          
          <div class="stat-pill">
            <span class="stat-icon">⭐</span>
            <span class="stat-value">{{ averageScore.toFixed(1) }}</span>
            <span class="stat-label">Promedio</span>
          </div>
        </div>
      </div>
      
      <!-- Estado de carga -->
      <div v-if="loading" class="loading-state">
        <div class="loading-spinner"></div>
        <p>Cargando historial de evaluaciones...</p>
      </div>
      
      <!-- Estado de error -->
      <div v-else-if="error" class="error-state">
        <div class="error-icon">⚠️</div>
        <h3>Error al cargar historial</h3>
        <p>{{ error }}</p>
        <button class="retry-button" @click="loadEvaluations">Reintentar</button>
      </div>
      
      <!-- Estado vacío -->
      <div v-else-if="evaluations.length === 0" class="empty-state">
        <div class="empty-icon">📋</div>
        <h3>No hay evaluaciones disponibles</h3>
        <p>Completa evaluaciones para ver tu historial aquí.</p>
        <button class="back-button-alt" @click="goBack">Volver al inicio</button>
      </div>
      
      <!-- Contenido principal cuando hay evaluaciones -->
      <div v-else class="main-content">
        <div class="content-columns">
          <!-- Columna izquierda - Tarjetas de estadísticas y habilidades -->
          <div class="left-column">
            <!-- Tarjeta de estadísticas -->
            <StatsCard :evaluations="evaluations" />
            
            <!-- Gráfico de habilidades 
                ELIMINADO! 
            -->
             
            
          </div>
          
          <!-- Columna derecha - Lista de evaluaciones -->
          <div class="right-column">
            <HistoryList 
              :evaluations="evaluations"
              :is-loading="false"
              :is-teacher-view="isTeacherView"
              @select-evaluation="selectEvaluation"
              @evaluation-deleted="handleEvaluationDeleted"
            />
          </div>
        </div>
      </div>
    </div>
    
    <!-- Modal de detalles -->
    <EvaluationDetailsModal 
      v-if="selectedEvaluation"
      :evaluation="selectedEvaluation"
      @close="closeDetails"
      @view-full="viewFullEvaluation"
    />
  </div>
</template>

<script>
import { ref, computed, onMounted, watch } from 'vue';
import { useRouter, useRoute } from 'vue-router';
import evaluationsService from '@/api/evaluationsService';

// Componentes
import StatsCard from '@/components/docentes/student-history/StatsCard.vue';
import SkillsChart from '@/components/docentes/student-history/SkillsChart.vue';
import HistoryList from '@/components/docentes/student-history/HistoryList.vue';
import EvaluationDetailsModal from '@/components/docentes/student-history/EvaluationDetailsModal.vue';

export default {
  name: 'EvaluationHistoryView',
  components: {
    StatsCard,
    SkillsChart,
    HistoryList,
    EvaluationDetailsModal
  },
  setup() {
    const router = useRouter();
    const route = useRoute();

    // Estado principal
    const evaluations = ref([]);
    const loading = ref(true);
    const error = ref('');
    const selectedEvaluation = ref(null);

    // Parámetros de vista
    const isTeacherView = ref(false);
    const studentName = ref('');
    const studentId = ref(null);
    
    // Calcular estadísticas
    const averageScore = computed(() => {
      if (!evaluations.value.length) return 0;
      
      const scores = evaluations.value.map(evaluation => {
        // Intentar obtener la puntuación de diferentes fuentes
        if (evaluation.puntaje_sobre_10 !== undefined) {
          return parseFloat(evaluation.puntaje_sobre_10) || 0;
        }
        if (evaluation.formattedScore !== undefined) {
          // Si es "8.5/10", extraer solo el número
          const match = /^([\d.]+)\/10$/.exec(evaluation.formattedScore);
          if (match) {
            return parseFloat(match[1]);
          }
          return parseFloat(evaluation.formattedScore) || 0;
        }
        // Calcula si tiene puntaje_total y puntaje_maximo
        if (evaluation.puntaje_total !== undefined && 
            evaluation.evaluacion_puntaje_total !== undefined && 
            evaluation.evaluacion_puntaje_total > 0) {
          return (evaluation.puntaje_total / evaluation.evaluacion_puntaje_total) * 10;
        }
        return 0;
      });
      
      const validScores = scores.filter(score => !isNaN(score));
      if (validScores.length === 0) return 0;
      
      const sum = validScores.reduce((a, b) => a + b, 0);
      return sum / validScores.length;
    });
    
    // Comprueba si se esta en rol docente
    const checkViewMode = () => {
      const queryMode = route.query.mode;
      const storageMode = localStorage.getItem('view_mode');
      
      if (queryMode === 'teacher' || storageMode === 'teacher') {
        isTeacherView.value = true;
        studentId.value = route.query.student_id || localStorage.getItem('view_student_id');
        studentName.value = route.query.student_name || localStorage.getItem('view_student_name') || 'Estudiante';
        
        // Guardar información en localStorage para persistencia
        localStorage.setItem('view_mode', 'teacher');
        localStorage.setItem('view_student_id', studentId.value);
        localStorage.setItem('view_student_name', studentName.value);
        
        console.log(`🔍 Modo docente detectado. Estudiante: ${studentName.value} (ID: ${studentId.value})`);
      } else {
        // Limpiar variables de modo docente
        localStorage.removeItem('view_mode');
        localStorage.removeItem('view_student_id');
        localStorage.removeItem('view_student_name');
      }
    };
    
    // Procesar datos de evaluación para asegurar formato correcto
    const processEvaluationData = (rawEvaluation) => {
      // Extraer propiedades necesarias con valores por defecto seguros
      const evaluation = { ...rawEvaluation };

      // Asegurar ID único
      evaluation.id = evaluation.id || `temp_${Date.now()}_${Math.random()}`;
      
      // Asegurar evaluacion_id (para navegación)
      evaluation.evaluacion_id = evaluation.evaluacion_id || evaluation.id;
      
      // Asegurar puntaje_sobre_10 como número
      let puntajeSobre10 = 0;
      
      if (evaluation.puntaje_sobre_10 !== undefined) {
        puntajeSobre10 = parseFloat(evaluation.puntaje_sobre_10) || 0;
      } else if (evaluation.puntaje_total !== undefined && 
                evaluation.evaluacion_puntaje_total !== undefined && 
                evaluation.evaluacion_puntaje_total > 0) {
        puntajeSobre10 = (evaluation.puntaje_total / evaluation.evaluacion_puntaje_total) * 10;
      }
      
      evaluation.puntaje_sobre_10 = puntajeSobre10;

      // Asegurar tiempo_total_ms si está disponible
      if (evaluation.tiempo_total_ms && evaluation.tiempo_total_ms > 0) {
        evaluation.tiempo_total = evaluation.tiempo_total_ms;
      } else if (evaluation.detalles && evaluation.detalles.tiempo_total_ms && evaluation.detalles.tiempo_total_ms > 0) {
        evaluation.tiempo_total = evaluation.detalles.tiempo_total_ms;
      }
      
      // Añade propiedades formateadas para compatibilidad
      evaluation.formattedScore = `${puntajeSobre10.toFixed(1)}/10`;
      evaluation.formattedScoreDisplay = puntajeSobre10.toFixed(1);
      
      // Determinar color_clase basándose en la puntuación
      if (!evaluation.color_clase) {
        let colorClase = 'poor';
        if (puntajeSobre10 >= 9) colorClase = 'excellent';
        else if (puntajeSobre10 >= 7) colorClase = 'good';
        else if (puntajeSobre10 >= 5) colorClase = 'average';
        
        evaluation.color_clase = colorClase;
      }
      
      // Asegurar que respuestas sea un array
      if (!Array.isArray(evaluation.respuestas)) {
        // Intentar extraer respuestas del objeto detalles
        if (evaluation.detalles && Array.isArray(evaluation.detalles.respuestas)) {
          evaluation.respuestas = evaluation.detalles.respuestas;
        } else {
          evaluation.respuestas = [];
        }
      }
      
      // Intentar extraer etiquetas de los ejercicios o respuestas
      if (evaluation.respuestas) {
        evaluation.respuestas.forEach(respuesta => {
          if (respuesta.contenido && respuesta.contenido.etiquetas) {
            // Ya tenemos etiquetas, no hacer nada
          } else if (typeof respuesta.contenido === 'string') {
            try {
              const contenidoParsed = JSON.parse(respuesta.contenido);
              if (contenidoParsed.etiquetas) {
                // Añadir etiquetas directamente a la respuesta para facilitar extracción
                respuesta.etiquetas = contenidoParsed.etiquetas;
              }
            } catch (e) {
              // Ignorar errores al parsear JSON
            }
          }
        });
      }
      
      // Asegurar que está marcada como activa a menos que se indique lo contrario
      evaluation.evaluacion_activa = evaluation.evaluacion_activa !== false;
      
      return evaluation;
    };
    
    // Cargar evaluaciones desde el API con reintentos
    const loadEvaluations = async (retryCount = 0) => {
      loading.value = true;
      error.value = '';

      try {
        // Determinar qué estudiante cargar
        const targetStudentId = isTeacherView.value ? studentId.value : null;
        console.log(`🔍 Cargando evaluaciones ${isTeacherView.value ? `para estudiante: ${targetStudentId}` : 'para usuario actual'}`);

        const response = await evaluationsService.getHistorialEvaluaciones(targetStudentId);
        console.log("📊 Respuesta del historial:", response.data);

        // Validar la estructura de la respuesta
        if (response.data && response.data.success) {
          // Obtener historial y asegurarse de que sea un array
          const historial = Array.isArray(response.data.historial) 
                          ? response.data.historial 
                          : [];
          
          // Procesar cada evaluación para asegurar propiedades necesarias
          evaluations.value = historial
            .filter(item => item && (item.id || item.evaluacion_id)) // Filtrar entradas inválidas
            .map(item => processEvaluationData(item));
            
          console.log(`✅ Se cargaron ${evaluations.value.length} evaluaciones`);

          if (evaluations.value.length > 0) {
            processEvaluationTimes();
          }
        } else {
          evaluations.value = [];
          if (response.data && response.data.message) {
            error.value = response.data.message;
          } else {
            error.value = 'No se pudieron cargar las evaluaciones. Formato de respuesta inválido.';
          }
        }
      } catch (err) {
        console.error('Error al cargar evaluaciones:', err);
        
        // Implementar reintento con backoff exponencial
        if (retryCount < 3) {
          console.log(`Reintentando carga (intento ${retryCount + 1}/3)...`);
          setTimeout(() => {
            loadEvaluations(retryCount + 1);
          }, 1000 * Math.pow(2, retryCount)); // 1s, 2s, 4s
          return;
        }
        
        error.value = 'No se pudieron cargar las evaluaciones. Por favor, intenta nuevamente.';
        evaluations.value = [];
      } finally {
        loading.value = false;
      }
    };
    
    // Seleccionar evaluación para ver detalles
    const selectEvaluation = (evaluation) => {
      console.log('Mostrando detalles para evaluación:', evaluation.id || evaluation.evaluacion_id);
      selectedEvaluation.value = evaluation;
      
      // Guardar ID en localStorage para uso posterior
      if (evaluation.id) {
        localStorage.setItem('view_historial_id', evaluation.id);
      }
    };
    
    // Cerrar modal de detalles
    const closeDetails = () => {
      selectedEvaluation.value = null;
    };
    
    // Ver evaluación completa
    const viewFullEvaluation = (evaluationId) => {
      console.log('Solicitando ver evaluación completa:', evaluationId);
      
      if (!evaluationId) {
        console.error('No se puede ver la evaluación: ID no proporcionado');
        return;
      }

      // Guardar información que estamos en modo historial
      localStorage.setItem('view_mode', 'history');
      localStorage.setItem('view_evaluation_id', evaluationId);

      // Cerrar el modal
      selectedEvaluation.value = null;

      // Navegar a la vista de evaluación
      router.push({
        path: '/resolucion-ejercicios-practicos',
        query: {
          evaluation_id: evaluationId,
          historial_id: localStorage.getItem('view_historial_id'),
          mode: 'history'
        }
      });
    };
    
    // Manejar eliminación de evaluación
    const handleEvaluationDeleted = (deletedEvaluation) => {
      console.log('Evaluación eliminada:', deletedEvaluation.id);
      
      // Actualizar lista de evaluaciones
      evaluations.value = evaluations.value.filter(
        evaluation => evaluation.id !== deletedEvaluation.id && 
                     evaluation.evaluacion_id !== deletedEvaluation.id
      );
    };
    
    // Volver a la página anterior (actualizado para ser como LoginEvaluationView)
    const goBack = () => {
      // Limpiar variables de sesión
      localStorage.removeItem('view_mode');
      localStorage.removeItem('view_evaluation_id');
      localStorage.removeItem('view_historial_id');
      
      if (isTeacherView.value) {
        router.push('/docente/dashboard');
      } else {
        router.push('/estudiante/dashboard');
      }
    };
    
    // Observar cambios en modo de visualización
    watch([() => route.query.mode, () => route.query.student_id], () => {
      checkViewMode();
      loadEvaluations();
    });

    onMounted(() => {
      console.log('EvaluationHistoryView montado');
      checkViewMode();
      loadEvaluations();
    });

    // Función para procesar tiempos de todas las evaluaciones
    const processEvaluationTimes = () => {
      console.log(`Procesando tiempos para ${evaluations.value.length} evaluaciones...`);

      evaluations.value.forEach((evaluation, index) => {
        console.log(`\n=== Evaluación #${index + 1} ===`);
        console.log(`ID: ${evaluation.id || evaluation.evaluacion_id}`);
        console.log(`Título: ${evaluation.titulo || evaluation.evaluacion_titulo}`);
        console.log(`tiempo_total actual: ${evaluation.tiempo_total}`);

        // Verificar si existe tiempo_total
        if (!evaluation.tiempo_total || evaluation.tiempo_total === 'null') {
          console.log("Tiempo no disponible, calculando...");

          // Primero intenta calcular desde fechas
          if (evaluation.fecha_inicio && evaluation.fecha_fin) {
            try {
              const start = new Date(evaluation.fecha_inicio);
              const end = new Date(evaluation.fecha_fin);
              const duration = end - start;

              if (!isNaN(duration) && duration > 0) {
                console.log(`Duración calculada desde fechas: ${duration}ms`);
                evaluation.tiempo_total = duration;
              }
            } catch (e) {
              console.warn("Error al calcular desde fechas:", e);
            }
          } else {
            console.log(`No hay fechas para calcular tiempo: inicio=${evaluation.fecha_inicio}, fin=${evaluation.fecha_fin}`);
          }

          // Segundo si no se pudo calcular desde fechas, intentar desde localStorage
          if (!evaluation.tiempo_total || evaluation.tiempo_total === 'null') {
            const userId = localStorage.getItem('user_id') || 'anonymous';
            const evalId = evaluation.id || evaluation.evaluacion_id;

            if (evalId) {
              console.log(`Buscando en localStorage para evaluación ${evalId}`);

              const startTime = parseInt(localStorage.getItem(`evaluationStartTime_${userId}_${evalId}`) ||
                localStorage.getItem(`evaluationStartTime_${userId}`) || '0');
              const endTime = parseInt(localStorage.getItem(`evaluationEndTime_${userId}`) || '0');

              if (startTime > 0 && endTime > 0) {
                const duration = endTime - startTime;
                if (duration > 0) {
                  console.log(`⏱️ Tiempo calculado desde localStorage: ${duration}ms`);
                  evaluation.tiempo_total = duration;
                }
              } else {
                console.log(`No se encontraron tiempos en localStorage: inicio=${startTime}, fin=${endTime}`);
              }
            }
          }

          console.log(`tiempo_total final: ${evaluation.tiempo_total}`);
        }
      });

      console.log("Procesamiento de tiempos completado.");
    };

    // Método auxiliar para calcular tiempo de evaluación cuando no está disponible
    const calculateEvaluationDuration = (evaluation) => {
      if (!evaluation) return null;

      if (evaluation.tiempo_total && evaluation.tiempo_total !== 'null') {
        return evaluation.tiempo_total;
      }

      // Calcular desde fechas
      if (evaluation.fecha_inicio && evaluation.fecha_fin) {
        try {
          const start = new Date(evaluation.fecha_inicio);
          const end = new Date(evaluation.fecha_fin);
          const duration = end - start;
          if (!isNaN(duration) && duration > 0) {
            console.log(`Duración calculada para evaluación ${evaluation.id || evaluation.evaluacion_id}: ${duration}ms`);
            // Actualizar el tiempo_total de la evaluación
            evaluation.tiempo_total = duration;
            return duration;
          }
        } catch (e) {
          console.warn('Error al calcular duración desde fechas:', e);
        }
      }

      // Buscar en localStorage
      try {
        const userId = localStorage.getItem('user_id') || 'anonymous';
        const evalId = evaluation.evaluacion_id || evaluation.id;

        if (evalId) {
          const startTime = parseInt(localStorage.getItem(`evaluationStartTime_${userId}_${evalId}`) ||
            localStorage.getItem(`evaluationStartTime_${userId}`) || '0');
          const endTime = parseInt(localStorage.getItem(`evaluationEndTime_${userId}`) || '0');

          if (startTime > 0 && endTime > 0) {
            const duration = endTime - startTime;
            if (duration > 0) {
              console.log(`Duración recuperada desde localStorage: ${duration}ms`);
              // Actualizar el tiempo_total de la evaluación
              evaluation.tiempo_total = duration;
              return duration;
            }
          }
        }
      } catch (e) {
        console.warn('Error al recuperar duración desde localStorage:', e);
      }

      return null;
    };

    // Asegurarse de que las evaluaciones tengan un tiempo_total válido
    watch(() => evaluations.value, (newEvaluations) => {
      if (newEvaluations && newEvaluations.length > 0) {
        newEvaluations.forEach(evaluation => {
          if (!evaluation.tiempo_total || evaluation.tiempo_total === 'null') {
            evaluation.tiempo_total = calculateEvaluationDuration(evaluation);
          }
        });
      }
    }, { deep: true, immediate: true });

    // Observar cambios en evaluaciones para procesar tiempos
    watch(() => evaluations.value.length, () => {
      if (evaluations.value.length > 0) {
        processEvaluationTimes();
      }
    });


    window.debugEvaluationTimes = function () {
      const evaluations = document.querySelector('vue-app').__vue_app__.config.globalProperties.$store.state.evaluations || [];

      console.log(`==== DEBUG TIEMPOS DE EVALUACIÓN (${evaluations.length} evaluaciones) ====`);

      evaluations.forEach((evaluation, index) => {
        console.log(`\n-- Evaluación #${index + 1} --`);
        console.log(`ID: ${evaluation.id || evaluation.evaluacion_id}`);
        console.log(`Título: ${evaluation.titulo || evaluation.evaluacion_titulo}`);
        console.log(`tiempo_total: ${evaluation.tiempo_total}`);
        console.log(`fecha_inicio: ${evaluation.fecha_inicio}`);
        console.log(`fecha_fin: ${evaluation.fecha_fin}`);

        // Intentar calcular desde fechas
        if (evaluation.fecha_inicio && evaluation.fecha_fin) {
          try {
            const start = new Date(evaluation.fecha_inicio);
            const end = new Date(evaluation.fecha_fin);
            const duration = end - start;
            console.log(`Duración calculada desde fechas: ${duration}ms`);
          } catch (e) {
            console.log(`Error al calcular tiempo: ${e.message}`);
          }
        }

        // Buscar en localStorage
        const userId = localStorage.getItem('user_id') || 'anonymous';
        const evalId = evaluation.id || evaluation.evaluacion_id;

        if (evalId) {
          const startTimeKey = `evaluationStartTime_${userId}_${evalId}`;
          const startTime = localStorage.getItem(startTimeKey);

          const endTimeKey = `evaluationEndTime_${userId}`;
          const endTime = localStorage.getItem(endTimeKey);

          console.log(`localStorage - Claves: ${startTimeKey}, ${endTimeKey}`);
          console.log(`localStorage - Valores: inicio=${startTime}, fin=${endTime}`);

          if (startTime && endTime) {
            const duration = parseInt(endTime) - parseInt(startTime);
            console.log(`Duración calculada desde localStorage: ${duration}ms`);
          }
        }
      });

      console.log("\n==== FIN DEBUG TIEMPOS ====");
    };

    console.log("Función debugEvaluationTimes disponible. Ejecuta window.debugEvaluationTimes() para diagnosticar problemas con los tiempos.");



    return {
      evaluations,
      loading,
      error,
      selectedEvaluation,
      isTeacherView,
      studentName,
      averageScore,
      selectEvaluation,
      closeDetails,
      viewFullEvaluation,
      loadEvaluations,
      goBack,
      handleEvaluationDeleted,
      calculateEvaluationDuration,
      debugEvaluationTimes
    };
  }
};
</script>

<style scoped>
/* =================== CONTENEDOR PRINCIPAL =================== */
.history-page {
  min-height: 100vh;
  background-color: var(--color-bg-main);
  padding: 2rem;
  color: var(--color-text-secondary);
  font-family: Arial, sans-serif;
}

.history-container {
  max-width: 1200px;
  margin: 0 auto;
  padding-top: 3rem;
}

/* =================== BOTÓN VOLVER ATRÁS =================== */
.back-button {
  position: absolute;
  top: 1.5rem;
  left: 1.5rem;
  background-color: var(--color-bg-element);
  color: var(--color-text-muted);
  border: 1px solid var(--color-border);
  cursor: pointer;
  width: 40px;
  height: 40px;
  border-radius: var(--border-radius);
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all var(--transition-smooth) ease;
  font-size: 1.25rem;
  z-index: 100;
  box-shadow: var(--shadow-sm);
}

.back-button:hover {
  color: var(--color-info);
  background-color: var(--color-info-bg);
  border-color: var(--color-info);
  transform: translateY(-2px);
  box-shadow: var(--shadow);
}

/* =================== ENCABEZADO DE LA PÁGINA =================== */
.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 2rem;
  flex-wrap: wrap;
  gap: 1rem;
}

.page-title {
  font-size: 1.8rem;
  margin: 0;
  color: var(--color-text-primary);
  display: flex;
  align-items: center;
  gap: 0.8rem;
}

.title-icon {
  color: var(--color-primary);
}

/* =================== ESTADÍSTICAS DEL HEADER =================== */
.header-stats {
  display: flex;
  gap: 1rem;
}

.stat-pill {
  background-color: var(--color-bg-element-alt);
  padding: 0.6rem 1rem;
  border-radius: 30px;
  display: flex;
  align-items: center;
  gap: 0.5rem;
  border: 1px solid var(--color-border);
}

.stat-icon {
  font-size: 1.1rem;
  color: var(--color-primary);
}

.stat-value {
  font-weight: 600;
  color: var(--color-text-primary);
}

.stat-label {
  color: var(--color-text-muted);
  font-size: 0.9rem;
}

/* =================== CONTENIDO PRINCIPAL =================== */
.main-content {
  animation: fadeIn var(--transition-smooth) ease-in-out;
}

.content-columns {
  display: grid;
  grid-template-columns: minmax(300px, 1fr) 2fr;
  gap: 1.5rem;
}

/* =================== ESTADO DE CARGA =================== */
.loading-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 4rem 2rem;
  color: var(--color-text-muted);
  background-color: var(--color-bg-element-alt);
  border-radius: var(--border-radius-lg);
  border: 1px solid var(--color-border);
}

.loading-spinner {
  width: 50px;
  height: 50px;
  border: 5px solid var(--color-border);
  border-top-color: var(--color-primary);
  border-radius: 50%;
  animation: spin 1s linear infinite;
  margin-bottom: 1.5rem;
}

/* =================== ESTADO DE ERROR =================== */
.error-state {
  text-align: center;
  padding: 3rem 2rem;
  background-color: var(--color-bg-element-alt);
  border-radius: var(--border-radius-lg);
  border: 1px solid var(--color-border);
}

.error-icon {
  font-size: 3rem;
  color: var(--color-error);
  margin-bottom: 1rem;
}

.error-state h3 {
  color: var(--color-text-primary);
  margin-bottom: 1rem;
}

.retry-button {
  background-color: var(--color-primary);
  color: var(--color-bg-main);
  border: none;
  padding: 0.8rem 1.5rem;
  border-radius: var(--border-radius);
  font-weight: 600;
  cursor: pointer;
  margin-top: 1rem;
  transition: all var(--transition-fast);
}

.retry-button:hover {
  background-color: var(--color-primary-light);
  transform: translateY(-2px);
}

/* =================== ESTADO VACÍO =================== */
.empty-state {
  text-align: center;
  padding: 4rem 2rem;
  background-color: var(--color-bg-element-alt);
  border-radius: var(--border-radius-lg);
  border: 1px solid var(--color-border);
}

.empty-icon {
  font-size: 4rem;
  color: var(--color-text-muted);
  margin-bottom: 1.5rem;
  opacity: 0.5;
}

.empty-state h3 {
  color: var(--color-text-primary);
  margin-bottom: 0.5rem;
}

.empty-state p {
  color: var(--color-text-muted);
  margin-bottom: 2rem;
}

.back-button-alt {
  background-color: var(--color-bg-element-alt);
  color: var(--color-text-secondary);
  border: 1px solid var(--color-border);
  padding: 0.8rem 1.5rem;
  border-radius: var(--border-radius);
  font-weight: 600;
  cursor: pointer;
  transition: all var(--transition-fast);
}

.back-button-alt:hover {
  background-color: var(--color-bg-element-hover);
  transform: translateY(-2px);
}

/* =================== ANIMACIONES =================== */
@keyframes spin {
  to { 
    transform: rotate(360deg); 
  }
}

@keyframes fadeIn {
  from { 
    opacity: 0; 
  }
  to { 
    opacity: 1; 
  }
}

/* =================== MEDIA QUERIES =================== */
@media (max-width: 992px) {
  .content-columns {
    grid-template-columns: 1fr;
  }
  
  .page-header {
    flex-direction: column;
    align-items: flex-start;
  }
  
  .header-stats {
    width: 100%;
    justify-content: flex-start;
  }
}

@media (max-width: 768px) {
  .history-page {
    padding: 1rem;
  }
  
  .history-container {
    padding-top: 4rem;
  }
  
  .page-title {
    font-size: 1.5rem;
  }
}

@media (max-width: 576px) {
  .stat-pill {
    flex-direction: column;
    padding: 0.5rem;
    align-items: center;
  }
  
  .header-stats {
    gap: 0.5rem;
  }
}
</style>