<!-- src/components/docentes/student-history/StatsCard.vue -->
<template>
  <div class="stats-card">
    <div class="card-header">
      <h3 class="card-title">
        <span class="title-icon">📈</span>
        Estadísticas Generales
      </h3>
    </div>
    
    <div class="card-body">
      <!-- Promedio total -->
      <div class="stat-item">
        <div class="stat-label">
          <span class="stat-icon">⭐</span>
          Promedio general
        </div>
        <div class="stat-value-container">
          <div class="stat-bar-container">
            <div class="stat-bar" :style="{ width: `${averageScore*10}%` }" :class="getScoreColorClass(averageScore)"></div>
          </div>
          <div class="stat-value" :class="getScoreColorClass(averageScore)">{{ averageScore.toFixed(1) }}</div>
        </div>
      </div>
      
      <!-- Tiempo promedio -->
      <div class="stat-item">
        <div class="stat-label">
          <span class="stat-icon">⏱️</span>
          Tiempo promedio
        </div>
        <div class="stat-value">{{ formattedAverageTime }}</div>
      </div>
      
      <!-- Número de evaluaciones -->
      <div class="stat-item">
        <div class="stat-label">
          <span class="stat-icon">📝</span>
          Evaluaciones
        </div>
        <div class="stat-value">{{ evaluations.length }}</div>
      </div>
      
      <!-- Tasa de éxito -->
      <div class="stat-item">
        <div class="stat-label">
          <span class="stat-icon">✅</span>
          Tasa de éxito
        </div>
        <div class="stat-value-container">
          <div class="stat-bar-container">
            <div class="stat-bar" :style="{ width: `${successRate}%` }" :class="getSuccessRateClass()"></div>
          </div>
          <div class="stat-value" :class="getSuccessRateClass()">{{ successRate }}%</div>
        </div>
      </div>
      
      <!-- Última evaluación -->
      <div class="stat-item" v-if="latestEvaluation">
        <div class="stat-label">
          <span class="stat-icon">📅</span>
          Última evaluación
        </div>
        <div class="stat-value">{{ formatDate(latestEvaluation.fecha_fin) }}</div>
      </div>
    </div>
    
    <!-- Histograma de puntuaciones -->
    <div class="chart-container" v-if="evaluations.length > 1">
      <canvas ref="histogramCanvas"></canvas>
    </div>
  </div>
</template>

<script>
import { ref, computed, onMounted, watch } from 'vue';
import Chart from 'chart.js/auto';

export default {
  name: 'StatsCard',
  props: {
    evaluations: {
      type: Array,
      required: true,
      default: () => []
    }
  },
  setup(props) {
    const histogramCanvas = ref(null);
    const histogramChart = ref(null);
    
    // Calcular promedio de puntuaciones
    const averageScore = computed(() => {
      if (!props.evaluations.length) return 0;
      
      const scores = props.evaluations.map(evaluation => {
        if (evaluation.puntaje_sobre_10 !== undefined) {
          return parseFloat(evaluation.puntaje_sobre_10) || 0;
        }
        if (evaluation.formattedScore !== undefined) {
          return parseFloat(evaluation.formattedScore) || 0;
        }
        return 0;
      });
      
      const validScores = scores.filter(score => !isNaN(score));
      if (validScores.length === 0) return 0;
      
      const sum = validScores.reduce((a, b) => a + b, 0);
      return sum / validScores.length;
    });
    
    // Calcular tiempo promedio - versión mejorada
    const averageTime = computed(() => {
      if (!props.evaluations.length) return 0;

      const validTimes = props.evaluations
        .map(evaluation => {
          // 1. Priorizar tiempo_total_ms si está disponible
          if (evaluation.tiempo_total_ms && evaluation.tiempo_total_ms > 0) {
            return evaluation.tiempo_total_ms;
          }

          // 2. Verificar en detalles adicionales
          if (evaluation.detalles_adicionales && evaluation.detalles_adicionales.tiempo_total_ms &&
            evaluation.detalles_adicionales.tiempo_total_ms > 0) {
            return evaluation.detalles_adicionales.tiempo_total_ms;
          }

          // 3. Si tiempo_total es un número, usarlo
          if (typeof evaluation.tiempo_total === 'number' && evaluation.tiempo_total > 0) {
            return evaluation.tiempo_total;
          }

          // 4. Fallback a tiempo_total parseado
          return parseTimeDuration(evaluation.tiempo_total);
        })
        .filter(time => time > 0);

      if (validTimes.length === 0) return 0;

      const sum = validTimes.reduce((acc, time) => acc + time, 0);
      return Math.round(sum / validTimes.length);
    });
    
    // Formatear tiempo promedio
    const formattedAverageTime = computed(() => {
      const time = averageTime.value;
      if (time === 0) return 'No disponible';
      
      const minutes = Math.floor(time / 60000);
      const seconds = Math.floor((time % 60000) / 1000);
      
      return minutes > 0 ? `${minutes}m ${seconds}s` : `${seconds}s`;
    });
    
    // Calcular tasa de éxito (ejercicios correctos / total)
    const successRate = computed(() => {
      let totalCorrect = 0;
      let totalExercises = 0;
      
      props.evaluations.forEach(evaluation => {
        // Intentar obtener completados_count y ejercicios_count
        if (evaluation.completados_count !== undefined && evaluation.ejercicios_count !== undefined) {
          totalCorrect += evaluation.completados_count;
          totalExercises += evaluation.ejercicios_count;
        }
        // Alternativamente, contar desde respuestas
        else if (evaluation.respuestas && Array.isArray(evaluation.respuestas)) {
          totalExercises += evaluation.respuestas.length;
          evaluation.respuestas.forEach(respuesta => {
            if (respuesta.es_correcta) {
              totalCorrect++;
            }
          });
        }
      });
      
      if (totalExercises === 0) return 0;
      return Math.round((totalCorrect / totalExercises) * 100);
    });
    
    // Obtener última evaluación realizada
    const latestEvaluation = computed(() => {
      if (!props.evaluations.length) return null;
      
      return props.evaluations.reduce((latest, current) => {
        const currentDate = new Date(current.fecha_fin || current.fecha_almacenamiento || 0);
        const latestDate = new Date(latest.fecha_fin || latest.fecha_almacenamiento || 0);
        
        return currentDate > latestDate ? current : latest;
      }, props.evaluations[0]);
    });
    
    // Parsear duración de tiempo
    const parseTimeDuration = (timeValue) => {
      if (!timeValue) return 0;

      // Si es un número (milisegundos), usarlo directamente
      if (typeof timeValue === 'number') {
        return timeValue;
      }

      // Si es string que parece número, convertirlo
      if (typeof timeValue === 'string' && !isNaN(parseInt(timeValue))) {
        return parseInt(timeValue);
      }

      // Si es formato HH:MM:SS o MM:SS, parsearlo
      if (typeof timeValue === 'string' && timeValue.includes(':')) {
        const parts = timeValue.split(':');
        if (parts.length === 3) {
          const hours = parseInt(parts[0]) || 0;
          const minutes = parseInt(parts[1]) || 0;
          const seconds = parseFloat(parts[2]) || 0;
          return (hours * 3600 + minutes * 60 + seconds) * 1000;
        } else if (parts.length === 2) {
          const minutes = parseInt(parts[0]) || 0;
          const seconds = parseFloat(parts[1]) || 0;
          return (minutes * 60 + seconds) * 1000;
        }
      }

      return 0;
    };
    
    // Formatear fecha
    const formatDate = (dateString) => {
      if (!dateString) return 'No disponible';
      
      try {
        const date = new Date(dateString);
        return date.toLocaleDateString('es-ES', {
          day: '2-digit',
          month: '2-digit',
          year: 'numeric',
        });
      } catch (e) {
        return 'No disponible';
      }
    };
    
    // Obtener clase de color según puntuación
    const getScoreColorClass = (score) => {
      if (score >= 9) return 'excellent';
      if (score >= 7) return 'good';
      if (score >= 5) return 'average';
      return 'poor';
    };
    
    // Obtener clase de color según tasa de éxito
    const getSuccessRateClass = () => {
      const rate = successRate.value;
      if (rate >= 80) return 'excellent';
      if (rate >= 60) return 'good';
      if (rate >= 40) return 'average';
      return 'poor';
    };
    
    // Crear histograma de puntuaciones
    const createHistogram = () => {
      if (!histogramCanvas.value || props.evaluations.length <= 1) return;

      // Obtener puntuaciones
      const scores = props.evaluations.map(evaluation => {
        if (evaluation.puntaje_sobre_10 !== undefined) {
          return parseFloat(evaluation.puntaje_sobre_10) || 0;
        }
        if (evaluation.formattedScore !== undefined) {
          return parseFloat(evaluation.formattedScore) || 0;
        }
        return 0;
      }).filter(score => !isNaN(score));

      if (scores.length <= 1) return;

      // Crear bins (0-2, 2-4, 4-6, 6-8, 8-10)
      const bins = [0, 0, 0, 0, 0];

      scores.forEach(score => {
        const binIndex = Math.min(Math.floor(score / 2), 4);
        bins[binIndex]++;
      });

      // Destruir gráfico anterior si existe
      if (histogramChart.value) {
        histogramChart.value.destroy();
      }

      // Obtener colores dinámicos del tema actual
      const style = getComputedStyle(document.documentElement);
      const textColor = style.getPropertyValue('--color-text-secondary').trim() || '#E0E0E0';
      const gridColor = style.getPropertyValue('--color-border').trim() || 'rgba(255, 255, 255, 0.1)';
      const bgColor = style.getPropertyValue('--color-bg-element').trim() || 'rgba(42, 42, 53, 0.9)';

      // Crear nuevo gráfico
      const ctx = histogramCanvas.value.getContext('2d');
      histogramChart.value = new Chart(ctx, {
        type: 'bar',
        data: {
          labels: ['0-2', '2-4', '4-6', '6-8', '8-10'],
          datasets: [{
            label: 'Distribución de puntuaciones',
            data: bins,
            backgroundColor: [
              'rgba(244, 67, 54, 0.5)',
              'rgba(255, 152, 0, 0.5)',
              'rgba(255, 235, 59, 0.5)',
              'rgba(76, 175, 80, 0.5)',
              'rgba(33, 150, 243, 0.5)'
            ],
            borderColor: [
              'rgba(244, 67, 54, 1)',
              'rgba(255, 152, 0, 1)',
              'rgba(255, 235, 59, 1)',
              'rgba(76, 175, 80, 1)',
              'rgba(33, 150, 243, 1)'
            ],
            borderWidth: 1
          }]
        },
        options: {
          responsive: true,
          maintainAspectRatio: false,
          scales: {
            y: {
              beginAtZero: true,
              ticks: {
                stepSize: 1,
                color: textColor  
              },
              grid: {
                color: gridColor  
              }
            },
            x: {
              ticks: {
                color: textColor  
              },
              grid: {
                color: gridColor  
              }
            }
          },
          plugins: {
            legend: {
              display: false
            },
            tooltip: {
              backgroundColor: bgColor,  
              titleColor: textColor,     
              bodyColor: textColor,      
              displayColors: false,
              callbacks: {
                label: function (context) {
                  return `${context.parsed.y} evaluación(es)`;
                }
              }
            }
          }
        }
      });
    };
    
    // Observar cambios en evaluaciones
    watch(() => props.evaluations, () => {
      setTimeout(() => {
        createHistogram();
      }, 500);
    }, { deep: true });
    
    onMounted(() => {
      setTimeout(() => {
        createHistogram();
      }, 500);
    });
    
    return {
      averageScore,
      formattedAverageTime,
      successRate,
      latestEvaluation,
      histogramCanvas,
      formatDate,
      getScoreColorClass,
      getSuccessRateClass
    };
  }
};
</script>

<style scoped>
/* =================== CONTENEDOR PRINCIPAL =================== */
.stats-card {
  background-color: var(--color-bg-element);
  border-radius: var(--border-radius-lg);
  padding: 1.2rem;
  margin-bottom: 1rem;
  box-shadow: var(--shadow);
  border: 1px solid var(--color-border);
  transition: transform var(--transition-fast), box-shadow var(--transition-fast);
}

.stats-card:hover {
  box-shadow: var(--shadow-lg);
}

/* =================== HEADER DE TARJETA =================== */
.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1.2rem;
  border-bottom: 1px solid var(--color-border);
  padding-bottom: 0.8rem;
}

.card-title {
  font-size: 1.1rem;
  font-weight: 600;
  color: var(--color-text-secondary);
  margin: 0;
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.title-icon {
  color: var(--color-primary);
}

/* =================== CUERPO DE TARJETA =================== */
.card-body {
  display: flex;
  flex-direction: column;
  gap: 1rem;
  margin-bottom: 1.2rem;
}

.stat-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  background-color: var(--color-bg-darker);
  padding: 0.8rem 1rem;
  border-radius: var(--border-radius);
  transition: background-color var(--transition-fast);
}

.stat-item:hover {
  background-color: var(--color-bg-element-hover);
}

/* =================== ETIQUETAS Y VALORES =================== */
.stat-label {
  display: flex;
  align-items: center;
  gap: 0.7rem;
  color: var(--color-text-secondary);
  font-weight: 500;
}

.stat-icon {
  font-size: 1.2rem;
  opacity: 0.9;
}

.stat-value {
  font-weight: 600;
  font-size: 1.1rem;
  color: var(--color-text-primary);
}

.stat-value-container {
  display: flex;
  align-items: center;
  gap: 0.7rem;
}

/* =================== BARRAS DE PROGRESO =================== */
.stat-bar-container {
  width: 100px;
  height: 8px;
  background-color: var(--color-bg-darker);
  border-radius: 4px;
  overflow: hidden;
}

.stat-bar {
  height: 100%;
  border-radius: 4px;
  transition: width 0.5s cubic-bezier(0.25, 1, 0.5, 1);
}

.stat-bar.excellent {
  background: linear-gradient(90deg, var(--color-score-excellent), #4CAF50);
}

.stat-bar.good {
  background: linear-gradient(90deg, var(--color-score-good), #FFEB3B);
}

.stat-bar.average {
  background: linear-gradient(90deg, var(--color-score-average), #FFC107);
}

.stat-bar.poor {
  background: linear-gradient(90deg, var(--color-score-poor), #F44336);
}

/* =================== COLORES DE VALORES POR ESTADO =================== */
.stat-value.excellent {
  color: var(--color-score-excellent);
}

.stat-value.good {
  color: var(--color-score-good);
}

.stat-value.average {
  color: var(--color-score-average);
}

.stat-value.poor {
  color: var(--color-score-poor);
}

/* =================== CONTENEDOR DE GRÁFICO =================== */
.chart-container {
  height: 180px;
  margin-top: 1rem;
  padding-top: 1rem;
  border-top: 1px solid var(--color-border);
}
</style>