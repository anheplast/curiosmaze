<!-- components/Common/ExercisesNavbar.vue -->
<template>
  <div class="exercises-navbar-wrapper">
    <nav class="exercises-navbar">
      <div class="navbar-start">
        <div class="logo-container">
          <img src="/logo/Logo-CuriosMaze-40x40.png" alt="Logo" class="logo-image">
          <h1 class="logo-text" v-if="evaluation">{{ evaluation.title || 'Evaluación' }}</h1>
        </div>
      </div>

      <div class="navbar-center">
        <button class="nav-button prev-button" @click="goToPreviousExercise" :disabled="currentExerciseIndex === 0">
          <svg width="16" height="16" viewBox="0 0 24 24" fill="currentColor">
            <path d="M15.41 7.41L14 6l-6 6 6 6 1.41-1.41L10.83 12z" />
          </svg>
          <span>Anterior</span>
        </button>

        <div class="exercise-counter">
          <span class="counter-icon">📝</span>
          <span class="counter-text">Ejercicio {{ currentExerciseIndex + 1 }} de {{ exercisesCount }}</span>
        </div>

        <button class="nav-button next-button" @click="goToNextExercise"
          :disabled="currentExerciseIndex === exercisesCount - 1">
          <span>Siguiente</span>
          <svg width="16" height="16" viewBox="0 0 24 24" fill="currentColor">
            <path d="M10 6L8.59 7.41 13.17 12l-4.58 4.59L10 18l6-6z" />
          </svg>
        </button>
      </div>

      <div class="navbar-end">
        <div class="timer-container">
          <div class="timer-label">{{ isHistoryMode ? 'Finalizada' : 'Tiempo restante' }}</div>
          <div class="timer-display" :class="{
            'warning': isTimeAlmostUp,
            'critical': isTimeAlmostFinished,
            'blinking': isLastSeconds
          }">
            <div class="timer-icon">⏱️</div>
            <div class="timer-value">{{ timeRemaining }}</div>
          </div>
        </div>
      </div>
    </nav>
  </div>
</template>

<script>
import { ref, onMounted, onUnmounted, inject, computed, watch } from 'vue';
import { useRouter } from 'vue-router';

export default {
  name: 'ExercisesNavbar',
  setup() {
    const router = useRouter();
    const timeRemaining = ref('00:00:00');
    const evaluation = inject('evaluation', ref(null));
    const exercises = inject('exercises', ref([]));
    const currentExerciseIndex = inject('currentExerciseIndex', ref(0));
    const selectExercise = inject('selectExercise', () => { });
    const finishEvaluation = inject('finishEvaluation', null);
    const notificationRef = inject('notificationRef', ref(null));

    // Agregar: viewMode e isHistoryMode
    const viewMode = inject('viewMode', ref('normal'));
    const isHistoryMode = inject('isHistoryMode', ref(false));

    // Función para mostrar notificaciones
    const showNotification = (message, type = 'info', duration = 3000) => {
      if (notificationRef?.value?.showNotification) {
        notificationRef.value.showNotification(message, type, duration);
      } else {
        // Fallback silencioso si no está disponible
        console.log(`Notificación: ${message} (tipo: ${type})`);
      }
    };

    // Estados para el cronómetro
    const isTimeAlmostUp = ref(false);     // 10% del tiempo restante
    const isTimeAlmostFinished = ref(false); // Para cambiar a rojo
    const isLastSeconds = ref(false);      // Para los últimos 10 segundos
    const totalDuration = ref(0);          // Duración total en milisegundos

    // Actualizar tiempo restante
    const updateTimeRemaining = () => {
      // Verificar si estamos en modo historial
      if (isHistoryMode.value || viewMode.value === 'history') {
        console.log('ExercisesNavbar: Modo historial detectado, no se actualiza tiempo');
        timeRemaining.value = '00:00:00';
        isTimeAlmostUp.value = false;
        isTimeAlmostFinished.value = false;
        isLastSeconds.value = false;
        return;
      }

      if (!evaluation.value) return;

      try {
        // Usar una precisión mayor para evitar discrepancias
        const precision = 1000; // milisegundos

        const startTime = new Date(evaluation.value.fecha_inicio || evaluation.value.startDate).getTime();
        let endTime;

        // Determinar la fecha de fin
        if (evaluation.value.fecha_fin || evaluation.value.endDate) {
          endTime = new Date(evaluation.value.fecha_fin || evaluation.value.endDate).getTime();
        } else if (evaluation.value.duration || evaluation.value.duracion_minutos) {
          const minutes = evaluation.value.duration || evaluation.value.duracion_minutos;
          endTime = startTime + (minutes * 60 * 1000);
        } else {
          console.error("No se pudo determinar la duración de la evaluación");
          return;
        }

        // Redondear a segundos completos para evitar discrepancias
        const now = Math.floor(new Date().getTime() / precision) * precision;
        const adjustedEndTime = Math.floor(endTime / precision) * precision;

        // Verificar si aún no comienza la evaluación
        if (now < startTime) {
          timeRemaining.value = "Pendiente";
          return;
        }

        const timeLeft = adjustedEndTime - now;

        // Manejar tiempo agotado
        if (timeLeft <= 0) {
          timeRemaining.value = '00:00:00';
          isTimeAlmostUp.value = true;
          isTimeAlmostFinished.value = true;
          isLastSeconds.value = false;

          if (router.currentRoute.value.path !== '/evaluacion-completada') {
            // Nueva función showNotification
            showNotification('⏰ Tiempo agotado', 'warning');

            if (finishEvaluation) {
              finishEvaluation();
            } else {
              router.push('/evaluacion-completada');
            }
          }
          return;
        }

        // Calcular porcentajes y estados
        const totalDuration = adjustedEndTime - startTime;
        const percentageLeft = (timeLeft / totalDuration) * 100;

        isTimeAlmostUp.value = percentageLeft <= 10;
        isLastSeconds.value = timeLeft <= 10000;
        isTimeAlmostFinished.value = percentageLeft <= 5;

        // Formatear tiempo restante
        const hours = Math.floor(timeLeft / 3600000);
        const minutes = Math.floor((timeLeft % 3600000) / 60000);
        const seconds = Math.floor((timeLeft % 60000) / 1000);

        timeRemaining.value = `${String(hours).padStart(2, '0')}:${String(minutes).padStart(2, '0')}:${String(seconds).padStart(2, '0')}`;
      } catch (error) {
        console.error("Error al calcular tiempo restante:", error);
        timeRemaining.value = "Error";
      }
    };

    // Ir al ejercicio anterior
    const goToPreviousExercise = () => {
      if (currentExerciseIndex.value > 0) {
        selectExercise(currentExerciseIndex.value - 1);
      }
    };

    // Ir al ejercicio siguiente
    const goToNextExercise = () => {
      if (currentExerciseIndex.value < exercises.value.length - 1) {
        selectExercise(currentExerciseIndex.value + 1);
      }
    };

    // Manejar navegación con teclado
    const handleKeyNavigation = (e) => {
      // Si estamos en un input o textarea, no interceptar
      if (e.target.tagName === 'INPUT' || e.target.tagName === 'TEXTAREA') {
        return;
      }

      if (e.key === 'ArrowLeft') {
        goToPreviousExercise();
      } else if (e.key === 'ArrowRight') {
        goToNextExercise();
      }
    };

    let clockInterval;

    onMounted(() => {
      updateTimeRemaining();

      // Modificado: No iniciar intervalo si estamos en modo historial
      if (!isHistoryMode.value && viewMode.value !== 'history') {
        clockInterval = setInterval(updateTimeRemaining, 1000);
      }

      // Registrar navegación con teclado
      //document.addEventListener('keydown', handleKeyNavigation);
    });

    onUnmounted(() => {
      if (clockInterval) {
        clearInterval(clockInterval);
      }

      //document.removeEventListener('keydown', handleKeyNavigation);
    });

    // Observar cambios en la evaluación para actualizar datos
    watch(evaluation, (newEval) => {
      if (newEval && !isHistoryMode.value && viewMode.value !== 'history') {
        updateTimeRemaining();
      }
    });

    return {
      timeRemaining,
      isTimeAlmostUp,
      isTimeAlmostFinished,
      isLastSeconds,
      evaluation,
      goToPreviousExercise,
      goToNextExercise,
      currentExerciseIndex,
      exercisesCount: computed(() => exercises.value.length),
      isHistoryMode
    };
  }
};
</script>

<style>
/* Estilos globales para anular Bulma (sin scoped) */
.exercises-navbar-wrapper button {
  background: none;
  border: none;
  cursor: pointer;
  margin: 0;
  padding: 0;
}

.exercises-navbar-wrapper h1 {
  margin: 0;
  padding: 0;
  font-size: 1rem;
  font-weight: 600;
}

.exercises-navbar-wrapper img {
  max-height: none;
}

.exercises-navbar-wrapper nav {
  min-height: auto;
}
</style>

<style scoped>
.exercises-navbar-wrapper {
  width: 100%;
  background-color: var(--color-bg-main, #1C1C21);
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.2);
  position: relative;
  z-index: 10;
}

.exercises-navbar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0 24px;
  height: 56px;
  width: 100%;
  /* max-width: 1400px; */
  /* margin: 0 auto; */
}

/* Logo y título */
.navbar-start {
  display: flex;
  align-items: center;
  flex: 0 0 auto;
  /* No crecer ni encogerse */
}

.logo-container {
  display: flex;
  align-items: center;
  gap: 10px;
}

.logo-image {
  width: 32px;
  height: 32px;
  object-fit: contain;
}

.logo-text {
  color: var(--color-text-primary, #FFFFFF);
  font-size: 16px;
  max-width: 200px;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

/* Navegación central */
.navbar-center {
  display: flex;
  align-items: center;
  gap: 16px;
  flex: 1;
  /* Ocupa el espacio restante */
  justify-content: center;
  /* Centra el contenido */
}

.nav-button {
  display: flex;
  align-items: center;
  gap: 6px;
  color: var(--color-text-secondary, #E0E0E0);
  font-size: 14px;
  padding: 6px 12px;
  border-radius: 20px;
  transition: all 0.3s ease;
  background-color: #32323A;
}

.nav-button:hover:not(:disabled) {
  background-color: #3A3A48;
  color: var(--color-text-primary, #FFFFFF);
  transform: translateY(-2px);
}

.nav-button:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.prev-button {
  padding-left: 10px;
}

.next-button {
  padding-right: 10px;
}

.exercise-counter {
  display: flex;
  align-items: center;
  gap: 8px;
  color: var(--color-text-secondary, #E0E0E0);
  font-size: 14px;
  background-color: #32323A;
  padding: 6px 12px;
  border-radius: 20px;
}

.counter-icon {
  font-size: 16px;
}

/* Timer */
.navbar-end {
  display: flex;
  align-items: center;
  flex: 0 0 auto;
  /* No crecer ni encogerse */
}

.timer-container {
  display: flex;
  align-items: center;
  gap: 8px;
}

.timer-label {
  color: var(--color-text-secondary, #E0E0E0);
  font-size: 14px;
}

.timer-display {
  background-color: var(--color-primary, #EBB300);
  color: #1C1C21;
  padding: 6px 12px;
  border-radius: 5px;
  font-family: 'Fira Code', monospace;
  font-weight: 600;
  letter-spacing: 1px;
  display: flex;
  align-items: center;
  gap: 8px;
  box-shadow: 0 2px 4px rgba(235, 179, 0, 0.3);
  transition: all 0.3s ease;
}

/* Estados del cronómetro */
.timer-display.warning {
  background-color: var(--color-warning, #FFBD2E);
}

.timer-display.critical {
  background-color: var(--color-danger, #FF6B6B);
  color: white;
}

.timer-display.blinking {
  animation: blink 1s infinite alternate;
}

.timer-icon {
  font-size: 16px;
}

.timer-value {
  font-size: 14px;
}

/* Animaciones */
@keyframes blink {
  from {
    opacity: 1;
    transform: scale(1);
  }

  to {
    opacity: 0.7;
    transform: scale(1.05);
  }
}

/* Responsive */
@media (max-width: 768px) {
  .exercises-navbar {
    padding: 0 12px;
    /* Padding mínimo en móvil */
    height: 50px;
  }

  .logo-text {
    max-width: 100px;
    font-size: 14px;
  }

  .nav-button {
    padding: 4px 8px;
  }

  .nav-button span {
    display: none;
  }

  .exercise-counter {
    padding: 4px 8px;
  }

  .counter-text {
    max-width: 120px;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
  }

  .timer-label {
    display: none;
  }

  .timer-display {
    padding: 4px 8px;
  }
}
</style>