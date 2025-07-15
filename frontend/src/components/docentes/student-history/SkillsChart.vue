<!-- src/components/docentes/student-history/SkillsChart.vue -->
<template>
  <div class="skills-chart-container">
    <div class="chart-header">
      <h3 class="chart-title">
        <span class="chart-icon">📊</span>
        Análisis de Desempeño
      </h3>
      
      <button @click="openModal" class="view-charts-button">
        <span class="button-icon">📈</span>
        Ver Gráficas
      </button>
    </div>
    
    <div v-if="loading" class="chart-loading">
      <div class="chart-spinner"></div>
      <span>Generando análisis...</span>
    </div>
    
    <div v-if="error" class="chart-error">
      <div class="error-icon">⚠️</div>
      <p>{{ error }}</p>
      <button class="retry-button" @click="generateCharts">Reintentar</button>
    </div>
  </div>
  
  <!-- Modal fuera del componente para renderizarse a nivel de body -->
  <Teleport to="body">
    <div v-if="showModal" class="chart-modal-overlay" @click.self="closeModal">
      <div class="chart-modal">
        <div class="modal-header">
          <h2>Análisis Detallado de Desempeño</h2>
          <button class="close-button" @click="closeModal">✕</button>
        </div>
        
        <div class="modal-content">
          <!-- Gráfico de progreso temporal (línea) -->
          <div class="chart-item-large">
            <h4 class="chart-subtitle">Progreso en el Tiempo</h4>
            <div class="chart-canvas-container-large">
              <canvas ref="progressChart"></canvas>
            </div>
          </div>

          <!-- Gráfico de rendimiento por categoría -->
          <div class="chart-item-large">
            <h4 class="chart-subtitle">Rendimiento por Categoría</h4>
            <div class="chart-canvas-container-large">
              <canvas ref="performanceChart"></canvas>
            </div>
          </div>
        </div>
      </div>
    </div>
  </Teleport>
</template>

<script>
import { ref, computed, onMounted, watch, nextTick } from 'vue';
import Chart from 'chart.js/auto';

export default {
  name: 'SkillsChart',
  props: {
    evaluations: {
      type: Array,
      required: true,
      default: () => []
    }
  },
  setup(props) {
    const loading = ref(true);
    const error = ref('');
    const progressChart = ref(null);
    const performanceChart = ref(null);
    const showModal = ref(false);
    let progressChartInstance = null;
    let performanceChartInstance = null;
    
    const openModal = async () => {
      showModal.value = true;
      // Esperamos a que el DOM se actualice antes de renderizar las gráficas
      await nextTick();
      // Regenerar las gráficas para adaptarlas al nuevo tamaño
      generateCharts();
    };
    
    const closeModal = () => {
      showModal.value = false;
    };
    
    // Extraer etiquetas de ejercicios
    const extractTagsFromExercise = (ejercicio) => {
      let etiquetas = [];
      
      console.log("Extrayendo etiquetas de ejercicio:", ejercicio.ejercicio_id || ejercicio.id);
      
      // 1. Direct etiquetas property
      if (ejercicio.etiquetas) {
        console.log("  Encontradas etiquetas directas:", ejercicio.etiquetas);
        if (Array.isArray(ejercicio.etiquetas)) {
          etiquetas = etiquetas.concat(ejercicio.etiquetas);
        } else if (typeof ejercicio.etiquetas === 'string') {
          try {
            const parsed = JSON.parse(ejercicio.etiquetas);
            if (Array.isArray(parsed)) {
              etiquetas = etiquetas.concat(parsed);
            } else {
              etiquetas.push(ejercicio.etiquetas);
            }
          } catch {
            etiquetas.push(ejercicio.etiquetas);
          }
        }
      }
      
      // 2. Check contenido.etiquetas
      if (ejercicio.contenido) {
        console.log("  Revisando contenido:", typeof ejercicio.contenido);
        
        if (typeof ejercicio.contenido === 'object' && ejercicio.contenido.etiquetas) {
          console.log("  Encontradas etiquetas en contenido objeto:", ejercicio.contenido.etiquetas);
          if (Array.isArray(ejercicio.contenido.etiquetas)) {
            etiquetas = etiquetas.concat(ejercicio.contenido.etiquetas);
          } else {
            etiquetas.push(ejercicio.contenido.etiquetas);
          }
        } else if (typeof ejercicio.contenido === 'string') {
          try {
            const contenidoParsed = JSON.parse(ejercicio.contenido);
            if (contenidoParsed.etiquetas) {
              console.log("  Encontradas etiquetas en contenido parseado:", contenidoParsed.etiquetas);
              if (Array.isArray(contenidoParsed.etiquetas)) {
                etiquetas = etiquetas.concat(contenidoParsed.etiquetas);
              } else {
                etiquetas.push(contenidoParsed.etiquetas);
              }
            }
          } catch (e) {
            console.log("  Error al parsear contenido:", e.message);
          }
        }
      }
      
      console.log("  Etiquetas extraídas final:", etiquetas);
      return etiquetas;
    };
    
    // Obtener todas las etiquetas únicas
    const getTagsFromEvaluations = () => {
      const allTags = new Set();
      
      console.log("Procesando evaluaciones para extraer etiquetas...");
      console.log("Total evaluaciones:", props.evaluations.length);
      
      props.evaluations.forEach(evaluation => {
        console.log("Procesando evaluación:", evaluation.id, evaluation.titulo);
        
        // Try to get exercises from various sources
        let ejercicios = [];
        
        // 1. Check respuestas array
        if (evaluation.respuestas && Array.isArray(evaluation.respuestas)) {
          console.log("- Encontradas respuestas:", evaluation.respuestas.length);
          ejercicios = ejercicios.concat(evaluation.respuestas);
        }
        
        // 2. Check detalles.respuestas array
        if (evaluation.detalles && evaluation.detalles.respuestas && 
            Array.isArray(evaluation.detalles.respuestas)) {
          console.log("- Encontradas respuestas en detalles:", evaluation.detalles.respuestas.length);
          ejercicios = ejercicios.concat(evaluation.detalles.respuestas);
        }
        
        // 3. Check ejercicios array
        if (evaluation.ejercicios && Array.isArray(evaluation.ejercicios)) {
          console.log("- Encontrados ejercicios directos:", evaluation.ejercicios.length);
          ejercicios = ejercicios.concat(evaluation.ejercicios);
        }
        
        console.log("- Total ejercicios encontrados:", ejercicios.length);
        
        // 4. Check detalles_adicionales.respuestas
        if (evaluation.detalles_adicionales && evaluation.detalles_adicionales.respuestas && 
            Array.isArray(evaluation.detalles_adicionales.respuestas)) {
          console.log("- Encontradas respuestas en detalles_adicionales:", evaluation.detalles_adicionales.respuestas.length);
          ejercicios = ejercicios.concat(evaluation.detalles_adicionales.respuestas);
        }
        
        ejercicios.forEach(ejercicio => {
          // Extract tags from various possible sources
          const etiquetas = extractTagsFromExercise(ejercicio);
          
          // Add found tags to the set
          etiquetas.forEach(tag => {
            if (tag && typeof tag === 'string' && tag.trim() !== '') {
              allTags.add(tag.trim());
            }
          });
        });
      });
      
      // Si no hay etiquetas, agregar etiquetas por defecto
      if (allTags.size === 0) {
        console.log("No se encontraron etiquetas, usando etiquetas por defecto");
        ['Variables', 'Ciclos', 'Condicionales', 'Funciones', 'Algoritmos'].forEach(tag => allTags.add(tag));
      }
      
      const finalTags = Array.from(allTags);
      console.log("Etiquetas finales encontradas:", finalTags);
      return finalTags;
    };
    
    // Calcular puntuaciones por etiqueta
    const calculateSkillScores = () => {
      const tags = getTagsFromEvaluations();
      
      // Iniciar contadores
      const tagScores = {};
      const tagAttempts = {};
      
      tags.forEach(tag => {
        tagScores[tag] = 0;
        tagAttempts[tag] = 0;
      });
      
      // Calcular puntuaciones
      props.evaluations.forEach(evaluation => {
        let ejercicios = [];
        
        // Reunir ejercicios de todas las fuentes posibles
        if (evaluation.respuestas && Array.isArray(evaluation.respuestas)) {
          ejercicios = ejercicios.concat(evaluation.respuestas);
        }
        
        if (evaluation.detalles && evaluation.detalles.respuestas && 
            Array.isArray(evaluation.detalles.respuestas)) {
          ejercicios = ejercicios.concat(evaluation.detalles.respuestas);
        }
        
        if (evaluation.ejercicios && Array.isArray(evaluation.ejercicios)) {
          ejercicios = ejercicios.concat(evaluation.ejercicios);
        }
        
        if (evaluation.detalles_adicionales && evaluation.detalles_adicionales.respuestas && 
            Array.isArray(evaluation.detalles_adicionales.respuestas)) {
          ejercicios = ejercicios.concat(evaluation.detalles_adicionales.respuestas);
        }
        
        ejercicios.forEach(ejercicio => {
          // Obtener etiquetas del ejercicio
          const etiquetas = extractTagsFromExercise(ejercicio);
          
          // Para cada etiqueta, incrementar el contador y calcular la puntuación
          etiquetas.forEach(tag => {
            if (tag && tagAttempts.hasOwnProperty(tag)) {
              tagAttempts[tag]++;
              
              // Si el ejercicio es correcto, añada a la puntuación
              if (ejercicio.es_correcta) {
                tagScores[tag]++;
              }
            }
          });
        });
      });
      
      // Calcular porcentajes
      const percentages = {};
      tags.forEach(tag => {
        percentages[tag] = tagAttempts[tag] > 0 
          ? Math.round((tagScores[tag] / tagAttempts[tag]) * 100) 
          : 0;
      });
      
      // Si no hay datos reales, generar datos ficticios
      if (Object.values(tagAttempts).every(value => value === 0)) {
        tags.forEach(tag => {
          tagAttempts[tag] = 1;
          tagScores[tag] = Math.random() * 0.7 + 0.1; // Valor entre 0.1 y 0.8
          percentages[tag] = Math.round(tagScores[tag] * 100);
        });
      }
      
      return {
        tags,
        percentages,
        attempts: tagAttempts,
        scores: tagScores
      };
    };
    
    // Calcular progreso en el tiempo
    const calculateTimeProgress = () => {
      if (props.evaluations.length === 0) {
        // Si no hay evaluaciones, crear datos de ejemplo
        const today = new Date();
        const dates = [];
        const scores = [];
        
        // Crear 5 fechas en el pasado
        for (let i = 4; i >= 0; i--) {
          const date = new Date(today);
          date.setDate(date.getDate() - i * 7); // Cada 7 días
          dates.push(date.toISOString().split('T')[0]);
          scores.push(Math.min(10, Math.max(1, 5 + (Math.random() * 4 - 2)))); // Valores entre 3 y 7
        }
        
        return { dates, scores };
      }
      
      // Si hay solo una evaluación, crear un punto adicional
      if (props.evaluations.length === 1) {
        const evaluation = props.evaluations[0];
        const fecha = evaluation.fecha_fin || evaluation.fecha_almacenamiento;
        if (fecha) {
          const date = new Date(fecha);
          const prevDate = new Date(date);
          prevDate.setDate(prevDate.getDate() - 10);
          
          // Obtener puntuación
          let score = 0;
          if (evaluation.puntaje_sobre_10 !== undefined) {
            score = parseFloat(evaluation.puntaje_sobre_10);
          } else if (evaluation.formattedScore) {
            const match = /^([\d.]+)\/10$/.exec(evaluation.formattedScore);
            if (match) {
              score = parseFloat(match[1]);
            }
          }
          
          return {
            dates: [prevDate.toISOString().split('T')[0], date.toISOString().split('T')[0]],
            scores: [Math.max(1, score - 2), score] // El punto anterior tiene un puntaje menor
          };
        }
      }
      
      // Ordenar evaluaciones por fecha
      const sortedEvals = [...props.evaluations].sort((a, b) => {
        const dateA = new Date(a.fecha_fin || a.fecha_almacenamiento || 0);
        const dateB = new Date(b.fecha_fin || b.fecha_almacenamiento || 0);
        return dateA - dateB;
      });
      
      // Extraer fechas y puntuaciones
      const dates = [];
      const scores = [];
      
      sortedEvals.forEach(evaluation => {
        const fecha = evaluation.fecha_fin || evaluation.fecha_almacenamiento;
        if (fecha) {
          const date = new Date(fecha);
          dates.push(date.toISOString().split('T')[0]); // YYYY-MM-DD
          
          // Obtener puntuación sobre 10
          let score = 0;
          if (evaluation.puntaje_sobre_10 !== undefined) {
            score = parseFloat(evaluation.puntaje_sobre_10);
          } else if (evaluation.formattedScore) {
            const match = /^([\d.]+)\/10$/.exec(evaluation.formattedScore);
            if (match) {
              score = parseFloat(match[1]);
            }
          }
          
          scores.push(score);
        }
      });
      
      return {
        dates,
        scores
      };
    };
    
    // Renderizar gráfico de progreso temporal
    const renderProgressChart = (timeData) => {
      // Verificar que el canvas existe
      if (!progressChart.value) {
        console.error("Canvas para gráfico de progreso no encontrado");
        return;
      }
      
      const ctx = progressChart.value.getContext('2d');
      if (!ctx) {
        console.error("No se pudo obtener el contexto 2D del canvas");
        return;
      }
      
      // Destruir instancia anterior si existe
      if (progressChartInstance) {
        progressChartInstance.destroy();
      }
      
      // Crear nueva instancia
      progressChartInstance = new Chart(ctx, {
        type: 'line',
        data: {
          labels: timeData.dates,
          datasets: [{
            label: 'Puntuación (0-10)',
            data: timeData.scores,
            borderColor: '#65B1C1',
            backgroundColor: 'rgba(101, 177, 193, 0.2)',
            tension: 0.2,
            fill: true,
            pointBackgroundColor: '#EBB300',
            pointBorderColor: '#1C1C21',
            pointRadius: 5,
            pointHoverRadius: 7
          }]
        },
        options: {
          responsive: true,
          maintainAspectRatio: false,
          plugins: {
            legend: {
              labels: {
                color: '#E0E0E0',
                font: {
                  size: 14
                }
              }
            },
            tooltip: {
              backgroundColor: '#1C1C21',
              titleColor: '#EBB300',
              bodyColor: '#E0E0E0',
              borderColor: '#36363C',
              borderWidth: 1,
              padding: 12,
              bodyFont: {
                size: 14
              },
              titleFont: {
                size: 16
              }
            }
          },
          scales: {
            y: {
              beginAtZero: true,
              max: 10,
              grid: {
                color: 'rgba(54, 54, 60, 0.5)'
              },
              ticks: {
                color: '#9090A0',
                font: {
                  size: 12
                }
              },
              title: {
                display: true,
                text: 'Puntuación',
                color: '#E0E0E0',
                font: {
                  size: 14
                }
              }
            },
            x: {
              grid: {
                color: 'rgba(54, 54, 60, 0.5)'
              },
              ticks: {
                color: '#9090A0',
                font: {
                  size: 12
                }
              },
              title: {
                display: true,
                text: 'Fecha',
                color: '#E0E0E0',
                font: {
                  size: 14
                }
              }
            }
          },
          animation: {
            duration: 1000,
            easing: 'easeOutQuart'
          }
        }
      });
    };
    
    // Renderizar gráfico de desempeño por categoría
    const renderPerformanceChart = (skillsData) => {
      // Verificar que el canvas existe
      if (!performanceChart.value) {
        console.error("Canvas para gráfico de rendimiento no encontrado");
        return;
      }
      
      const ctx = performanceChart.value.getContext('2d');
      if (!ctx) {
        console.error("No se pudo obtener el contexto 2D del canvas");
        return;
      }
      
      // Destruir instancia anterior si existe
      if (performanceChartInstance) {
        performanceChartInstance.destroy();
      }
      
      // Colores para las barras
      const barColors = [
        'rgba(235, 179, 0, 0.7)',   // Amarillo
        'rgba(101, 177, 193, 0.7)',  // Azul
        'rgba(106, 168, 79, 0.7)',   // Verde
        'rgba(224, 102, 102, 0.7)',  // Rojo
        'rgba(180, 142, 173, 0.7)'   // Púrpura
      ];
      
      // Asegurar que tenemos suficientes colores
      while (barColors.length < skillsData.tags.length) {
        barColors.push(...barColors.slice(0, skillsData.tags.length - barColors.length));
      }
      
      // Crear nueva instancia
      performanceChartInstance = new Chart(ctx, {
        type: 'bar',
        data: {
          labels: skillsData.tags,
          datasets: [{
            label: 'Porcentaje de Dominio',
            data: Object.values(skillsData.percentages),
            backgroundColor: barColors.slice(0, skillsData.tags.length),
            borderColor: '#1C1C21',
            borderWidth: 1,
            borderRadius: 6
          }]
        },
        options: {
          responsive: true,
          maintainAspectRatio: false,
          plugins: {
            legend: {
              display: false
            },
            tooltip: {
              backgroundColor: '#1C1C21',
              titleColor: '#EBB300',
              bodyColor: '#E0E0E0',
              borderColor: '#36363C',
              borderWidth: 1,
              padding: 12,
              bodyFont: {
                size: 14
              },
              titleFont: {
                size: 16
              },
              callbacks: {
                label: function(context) {
                  return `Dominio: ${context.raw}%`;
                }
              }
            }
          },
          scales: {
            y: {
              beginAtZero: true,
              max: 100,
              grid: {
                color: 'rgba(54, 54, 60, 0.5)'
              },
              ticks: {
                color: '#9090A0',
                font: {
                  size: 12
                },
                callback: function(value) {
                  return value + '%';
                }
              },
              title: {
                display: true,
                text: 'Porcentaje de Dominio',
                color: '#E0E0E0',
                font: {
                  size: 14
                }
              }
            },
            x: {
              grid: {
                display: false
              },
              ticks: {
                color: '#9090A0',
                font: {
                  size: 12
                }
              },
              title: {
                display: true,
                text: 'Categorías',
                color: '#E0E0E0',
                font: {
                  size: 14
                }
              }
            }
          },
          animation: {
            duration: 1000,
            easing: 'easeOutBounce'
          }
        }
      });
    };
    
    // Generar gráficos
    const generateCharts = async () => {
      if (!showModal.value) {
        // Si el modal no está abierto, solo preparamos los datos pero no renderizamos
        loading.value = false;
        return;
      }
      
      loading.value = true;
      error.value = '';
      
      try {
        console.log("Generando análisis de habilidades...");
        
        // Calcular datos para gráficos
        const timeData = calculateTimeProgress();
        const skillsData = calculateSkillScores();
        
        // Esperar al siguiente ciclo de renderizado y un pequeño delay
        await nextTick();
        await new Promise(resolve => setTimeout(resolve, 200));
        
        // Renderizar gráficos solo si los canvas existen
        if (progressChart.value && performanceChart.value) {
          renderProgressChart(timeData);
          renderPerformanceChart(skillsData);
        } else {
          console.error("Los elementos canvas no están disponibles");
          error.value = "Error al renderizar gráficos: Canvas no disponibles";
        }
        
        loading.value = false;
      } catch (e) {
        console.error("Error generando gráficos:", e);
        error.value = "No se pudieron generar los gráficos: " + e.message;
        loading.value = false;
      }
    };
    
    // Observar cambios en las evaluaciones
    watch(() => props.evaluations, () => {
      console.log('Evaluaciones actualizadas para gráficos:', props.evaluations.length);
      // Preparar datos pero no renderizar hasta que se abra el modal
      loading.value = false;
    }, { deep: true });
    
    // Observar el estado del modal
    watch(() => showModal.value, (newVal) => {
      if (newVal) {
        // Si el modal se abre, se generan las gráficas
        generateCharts();
      }
    });
    
    onMounted(() => {
      console.log('SkillsChart montado, esperando acción del usuario para generar gráficos');
      // Espera a que el usuario abra el modal
      loading.value = false;
    });
    
    return {
      loading,
      error,
      progressChart,
      performanceChart,
      showModal,
      openModal,
      closeModal,
      generateCharts
    };
  }
};
</script>

<style scoped>
.skills-chart-container {
  background-color: #2A2A35;
  border-radius: 12px;
  padding: 1.2rem;
  margin-bottom: 1rem;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
  border: 1px solid #36363C;
  transition: transform 0.2s, box-shadow 0.2s;
  overflow: hidden;
  height: 90px;
}

.skills-chart-container:hover {
  /* transform: translateY(-5px); */
  box-shadow: 0 8px 20px rgba(0, 0, 0, 0.25);
}

.chart-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1rem;
  padding-bottom: 0.8rem;
}

.chart-title {
  font-size: 1.1rem;
  font-weight: 600;
  color: #E0E0E0;
  margin: 0;
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.chart-icon {
  color: #EBB300;
}

.view-charts-button {
  background-color: #65B1C1;
  color: #1C1C21;
  border: none;
  padding: 0.5rem 1rem;
  border-radius: 6px;
  font-weight: 600;
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: 0.5rem;
  transition: all 0.2s;
}

.button-icon {
  font-size: 1.1rem;
}

.view-charts-button:hover {
  background-color: #78C5D5;
  transform: translateY(-2px);
  box-shadow: 0 4px 8px rgba(101, 177, 193, 0.3);
}

.chart-subtitle {
  font-size: 1.1rem;
  font-weight: 500;
  color: #B0B0C0;
  margin: 1rem 0;
  text-align: center;
}

.chart-loading, .chart-empty, .chart-error {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  height: 150px;
  color: #9090A0;
  text-align: center;
}

.chart-spinner {
  width: 40px;
  height: 40px;
  border: 4px solid #36363C;
  border-top-color: #EBB300;
  border-radius: 50%;
  animation: spin 1s linear infinite;
  margin-bottom: 1rem;
}

.error-icon {
  font-size: 3rem;
  margin-bottom: 1rem;
  opacity: 0.5;
  color: #FF5252;
}

.retry-button {
  margin-top: 1rem;
  background-color: #EBB300;
  color: #1C1C21;
  border: none;
  padding: 0.5rem 1rem;
  border-radius: 6px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s;
}

.retry-button:hover {
  background-color: #FFD03F;
  transform: translateY(-2px);
}

/* Estilos para el modal */
.chart-modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  width: 100vw;
  height: 100vh;
  background-color: rgba(0, 0, 0, 0.8);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 9999;
  animation: fadeIn 0.3s ease;
}

.chart-modal {
  width: 90%;
  max-width: 1200px;
  max-height: 90vh;
  background-color: #1F1F26;
  border-radius: 12px;
  box-shadow: 0 8px 30px rgba(0, 0, 0, 0.3);
  display: flex;
  flex-direction: column;
  overflow: hidden;
  animation: modalSlideIn 0.4s ease;
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1.2rem 1.5rem;
  background-color: #25252D;
  border-bottom: 1px solid #36363C;
}

.modal-header h2 {
  color: #E0E0E0;
  margin: 0;
  font-size: 1.5rem;
  display: flex;
  align-items: center;
  gap: 0.8rem;
}

.close-button {
  background: none;
  border: none;
  color: #9090A0;
  font-size: 1.5rem;
  cursor: pointer;
  padding: 0.5rem;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 50%;
  transition: all 0.2s;
}

.close-button:hover {
  color: #E0E0E0;
  background-color: rgba(255, 255, 255, 0.1);
}

.modal-content {
  padding: 1.5rem;
  overflow-y: auto;
  display: flex;
  flex-direction: column;
  gap: 2rem;
  margin-left: 0px;
  margin-right: 0px;
  /* Estilo personalizado para la barra de desplazamiento */
  scrollbar-width: thin;
  scrollbar-color: #36363C #1F1F26;
}

/* Estilo de barra de desplazamiento para Chrome, Edge y Safari */
.modal-content::-webkit-scrollbar {
  width: 6px;
}

.modal-content::-webkit-scrollbar-track {
  background: #1F1F26;
}

.modal-content::-webkit-scrollbar-thumb {
  background-color: #36363C;
  border-radius: 10px;
  border: 2px solid #1F1F26;
}

.modal-content::-webkit-scrollbar-thumb:hover {
  background-color: #4a4a54;
}

.chart-item-large {
  background-color: #2A2A35;
  border-radius: 10px;
  padding: 1.2rem;
  border: 1px solid #36363C;
  width: 100%;
}

.chart-canvas-container-large {
  width: 100%;
  height: 400px;
  position: relative;
}

@keyframes fadeIn {
  from { opacity: 0; }
  to { opacity: 1; }
}

@keyframes modalSlideIn {
  from { 
    opacity: 0;
    transform: translateY(50px);
  }
  to { 
    opacity: 1;
    transform: translateY(0);
  }
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

/* Para pantallas más grandes */
@media (min-width: 992px) {
  .chart-canvas-container-large {
    height: 500px;
  }
}

/* Para pantallas pequeñas */
@media (max-width: 768px) {
  .chart-modal {
    width: 95%;
    max-height: 95vh;
  }
  
  .modal-header h2 {
    font-size: 1.2rem;
  }
  
  .chart-canvas-container-large {
    height: 300px;
  }
}
</style>