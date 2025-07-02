<!-- views/PracticalExercises.vue -->
<template>
  <div class="practical-exercises-wrapper">
    <exercises-navbar></exercises-navbar>

    <div class="loading-overlay" v-if="loading">
      <div class="loading-spinner"></div>
      <p>Cargando evaluación...</p>
    </div>

    <div class="error-overlay" v-else-if="error">
      <div class="error-container">
        <h2><i class="fas fa-exclamation-triangle"></i> Error</h2>
        <p>{{ error }}</p>
        <button class="button" @click="retryLoading">Intentar nuevamente</button>
        <button class="button is-secondary" @click="goBack">Volver</button>
      </div>
    </div>

    <div class="exercise-layout" v-if="!loading && !error && exercises.length > 0">
      <!-- Paneles principales -->
      <div class="columns is-gapless main-content">
        <practical-left-panel ref="leftPanelRef"></practical-left-panel>
        <practical-right-panel ref="rightPanelRef"></practical-right-panel>
      </div>
    </div>

    <!-- Modal de carga para acción específica -->
    <div class="modal-overlay" v-if="processingAction">
      <div class="loading-container">
        <div class="loading-spinner"></div>
        <p>{{ processingMessage }}</p>
      </div>
    </div>

    <!-- Sistema de notificaciones -->
    <notification-system ref="notificationRef"></notification-system>
  </div>
</template>

<script>
import { ref, onMounted, provide, watch, onBeforeUnmount, nextTick, computed, inject } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import evaluationsService from '@/api/evaluationsService';
import { useStore } from 'vuex';

// Componentes
import ExercisesNavbar from '@/components/Common/ExercisesNavbar.vue';
import PracticalLeftPanel from '@/components/Common/PracticalLeftPanel.vue';
import PracticalRightPanel from '@/components/Common/PracticalRightPanel.vue';
import NotificationSystem from '@/components/Common/NotificationSystem.vue';

export default {
  name: 'PracticalExercises',
  components: {
    ExercisesNavbar,
    PracticalLeftPanel,
    PracticalRightPanel,
    NotificationSystem
  },
  setup() {
    const route = useRoute();
    const router = useRouter();
    const store = useStore();

    const leftPanelRef = ref(null);
    const rightPanelRef = ref(null);
    const notificationRef = inject('notificationRef', ref(null));

    const getCurrentUserId = () => {
      return localStorage.getItem('user_id') || 'anonymous';
    };

    const showNotification = (message, type = 'info', duration = 3000) => {
      if (notificationRef?.value?.showNotification) {
        notificationRef.value.showNotification(message, type, duration);
      } else {
        console.log(message);
      }
    };

    const checkEvaluationTime = () => {
      if (leftPanelRef.value?.checkEvaluationTime) {
        leftPanelRef.value.checkEvaluationTime();
      } else {
        console.log('leftPanelRef no está disponible');
      }
    };

    const viewMode = ref(route.query.mode || localStorage.getItem('view_mode') || 'normal');
    const isHistoryMode = computed(() => {
      const routeMode = route.query.mode === 'history';
      const localMode = localStorage.getItem('view_mode') === 'history';
      const currentMode = viewMode.value === 'history';

      const isHistory = routeMode || localMode || currentMode;

      if (isHistory) {
        console.log('Modo historial detectado:', { routeMode, localMode, currentMode });
      }

      return isHistory;
    });

    // Estados principales
    const evaluationId = ref(route.query.evaluation_id);
    const evaluation = ref(null);
    const exercises = ref([]);
    const currentExerciseIndex = ref(0);
    const loading = ref(true);
    const error = ref('');
    const processingAction = ref(false);
    const processingMessage = ref('');
    const isProcessingJudge0 = ref(false); // Flag para evitar procesos paralelos

    // Intervalos y timers
    let autoSaveInterval = null;
    let timerInterval = null;

    console.log('PracticalExercises: ID de evaluación obtenido de la URL:', evaluationId.value);

    // Muestra el overlay de procesamiento
    const showProcessing = (message) => {
      processingMessage.value = message || 'Procesando...';
      processingAction.value = true;
    };

    // Oculta el overlay de procesamiento
    const hideProcessing = () => {
      processingAction.value = false;
    };

    // Carga evaluacion y ejercicios
    const loadEvaluationData = async () => {
      loading.value = true;
      error.value = '';

      try {
        // Verifica si esta en modo historial
        if (isHistoryMode.value) {
          const historialId = route.query.historial_id;
          if (!historialId) {
            // Si no hay historial_id en query, lo obtiene de localStorage
            const historialId = localStorage.getItem('view_historial_id');
            if (!historialId) {
              throw new Error('No se especificó ID de historial');
            }
          }

          console.log('Cargando evaluación desde historial ID:', historialId);
          const response = await evaluationsService.getEvaluacionHistorial(historialId);

          if (response.data && response.data.success) {
            const historialData = response.data.evaluacion;

            // Adapta datos para el formato esperado
            evaluation.value = {
              id: historialData.id,
              titulo: historialData.titulo,
              descripcion: historialData.descripcion,
              duracion_minutos: 0, // Establece una duración en 0 para historial
              fecha_inicio: historialData.fecha_inicio,
              fecha_fin: historialData.fecha_fin,
              codigo_acceso: historialData.codigo_acceso,
              estado: 'finalizada',
              permitir_revision: true,
              mostrar_resultado: true,
              orden_aleatorio: false,
              puntaje_total: historialData.puntaje_total,
              puntaje_aprobacion: historialData.puntaje_aprobacion,
              creador: historialData.creador,
              tiempo_total: response.data.tiempo_total
            };

            // Procesar ejercicios desde historial
            exercises.value = historialData.ejercicios.map(ej => ({
              ...ej,
              // Asegura que el codigo se cargue
              template: ej.codigo,
              language_id: ej.language_id || 71, // Python por defecto
              contenido: {
                restricciones: ej.restricciones || '',
                formato_salida: ej.formato_salida || '',
                formatos_entrada: ej.formatos_entrada || [],
                ejemplos: ej.ejemplos || [],
                template: ej.codigo,
                tests_avanzados: ej.tests_avanzados,
                pista: ej.pista || '',
                etiquetas: ej.etiquetas || []
              }
            }));

            // Guarda el codigo en localStorage para que el editor los cargue
            exercises.value.forEach(ejercicio => {
              const userId = store.getters['auth/userId'];
              if (ejercicio.codigo) {
                localStorage.setItem(`exercise_code_${userId}_${ejercicio.id}`, ejercicio.codigo);
                localStorage.setItem(`exercise_status_${userId}_${ejercicio.id}`, 'completed');
              }
            });

            loading.value = false;
          } else {
            throw new Error('No se pudo cargar la evaluación del historial');
          }
        } else {
          // Codigo original para evaluaciones activas
          const storedEvaluation = localStorage.getItem('currentEvaluation');

          if (storedEvaluation) {
            try {
              const parsedEvaluation = JSON.parse(storedEvaluation);
              evaluation.value = parsedEvaluation;
              await loadExercisesFromAPI(parsedEvaluation.id);
            } catch (e) {
              console.error('Error al parsear evaluación de localStorage:', e);
              error.value = 'Error al cargar datos guardados de la evaluación';
              await fetchEvaluationData();
            }
          } else if (evaluationId.value) {
            await fetchEvaluationData();
          } else {
            error.value = 'No se pudo determinar qué evaluación cargar';
            loading.value = false;
          }
        }
      } catch (e) {
        console.error('Error general al cargar evaluación:', e);
        error.value = 'Error al cargar la evaluación: ' + (e.message || 'Error desconocido');
        loading.value = false;
      }
    };

    // Carga evaluacion desde la API usando getDetallesEvaluacion
    const fetchEvaluationData = async () => {
      if (!evaluationId.value) {
        error.value = 'ID de evaluación no especificado';
        loading.value = false;
        return;
      }

      try {
        console.log('Obteniendo detalles de evaluación ID:', evaluationId.value);

        // Usa directamente getDetallesEvaluacion que incluye los ejercicios
        const response = await evaluationsService.getDetallesEvaluacion(evaluationId.value);

        if (!response || !response.data) {
          throw new Error('No se recibieron datos de la evaluación');
        }

        console.log('Datos de evaluación recibidos:', response.data);
        evaluation.value = {
          ...response.data,
          title: response.data.titulo,
          duration: response.data.duracion_minutos
        };

        // Actualiza localStorage con los datos mas actuales
        localStorage.setItem('currentEvaluation', JSON.stringify(evaluation.value));

        // Registra la hora de inicio si no existe
        if (!localStorage.getItem('evaluationStartTime')) {
          localStorage.setItem('evaluationStartTime', new Date().getTime());
        }

        // Los ejercicios ya vienen incluidos en la respuesta
        if (response.data.ejercicios && Array.isArray(response.data.ejercicios)) {
          console.log('Ejercicios recibidos en la respuesta:', response.data.ejercicios.length);
          exercises.value = await processExercises(response.data.ejercicios);
          loading.value = false;
        } else {
          console.warn('La evaluación no tiene ejercicios asociados');
          error.value = 'Esta evaluación no tiene ejercicios asociados';
          loading.value = false;
        }
      } catch (e) {
        console.error('Error al obtener detalles de la evaluación:', e);

        // Intenta con el endpoint de validación de código como alternativa
        try {
          const accessCode = localStorage.getItem('evaluation_access_code');
          if (accessCode) {
            const result = await tryAlternativeLoading(accessCode);
            if (result) return; // Si fue exitoso, salimos
          }
        } catch (altError) {
          console.error('Error en carga alternativa:', altError);
        }

        // Si llegamos aquí, ningún método funcionó
        error.value = e.response?.data?.message ||
          'Error al cargar la evaluación. Por favor, intenta nuevamente.';
        loading.value = false;
      }
    };

    // Método alternativo utilizando simple-validar-codigo
    const tryAlternativeLoading = async (accessCode) => {
      console.log('Intentando carga alternativa con código:', accessCode);
      const response = await evaluationsService.validarCodigoAcceso(accessCode);

      if (response.data && response.data.valid) {
        console.log('Datos obtenidos mediante validación de código:', response.data);

        // Guarda datos básicos
        evaluation.value = {
          ...response.data.evaluation,
          title: response.data.evaluation.titulo,
          duration: response.data.evaluation.duracion_minutos
        };

        // Actualiza localStorage
        localStorage.setItem('currentEvaluation', JSON.stringify(evaluation.value));

        // Intenta cargar ejercicios con nueva implementación
        if (response.data.evaluation.id) {
          await loadExercisesFromAPI(response.data.evaluation.id);
          return true;
        }
      }

      return false;
    };

    // Carga ejercicios de la evaluación usando /evaluaciones/:id/detalles/
    const loadExercisesFromAPI = async (evalId) => {
      try {
        console.log('Cargando ejercicios mediante detalles de evaluación ID:', evalId);

        // Usa el endpoint de detalles para obtener todo en una sola llamada
        const response = await evaluationsService.getDetallesEvaluacion(evalId);
        console.log('Respuesta completa de detalles:', response.data);

        if (response.data && response.data.ejercicios) {
          console.log('Ejercicios obtenidos de detalles:', response.data.ejercicios.length);

          if (!response.data.ejercicios || response.data.ejercicios.length === 0) {
            error.value = 'Esta evaluación no tiene ejercicios asignados. Por favor, contacta a tu profesor.';
            exercises.value = [];
          } else {
            try {
              const processedExercises = await processExercises(response.data.ejercicios);
              console.log('Ejercicios procesados:', processedExercises);
              exercises.value = processedExercises;
            } catch (processingError) {
              console.error('Error al procesar ejercicios:', processingError);
              error.value = 'Error al procesar los ejercicios: ' + processingError.message;
              exercises.value = [];
            }
          }
        } else {
          error.value = 'No se encontraron ejercicios para esta evaluación.';
          exercises.value = [];
        }

        loading.value = false;
      } catch (e) {
        console.error('Error al cargar ejercicios desde API:', e);
        error.value = 'Error al cargar los ejercicios: ' + (e.message || e);
        loading.value = false;
        exercises.value = [];
      }
    };

    // Procesa ejercicios y añade pistas por defecto
    const processExercises = async (ejerciciosData) => {
      if (!ejerciciosData || ejerciciosData.length === 0) {
        error.value = 'Esta evaluación no tiene ejercicios asignados.';
        return [];
      }

      console.log('Procesando ejercicios:', ejerciciosData.length);

      return ejerciciosData.map(ejercicio => {
        // Verifica si es un objeto directo o tiene subcampos
        let ejercicioObj = ejercicio;
        if (ejercicio.ejercicio_detalle) {
          ejercicioObj = ejercicio.ejercicio_detalle;
        } else if (ejercicio.ejercicio) {
          ejercicioObj = ejercicio.ejercicio;
        }

        // Asegura que tiene todas las propiedades necesarias
        const ejercicioProcesado = {
          id: ejercicioObj.id,
          titulo: ejercicioObj.titulo || 'Sin título',
          descripcion: ejercicioObj.descripcion || '',
          tipo: ejercicioObj.tipo || 'practico',
          puntaje: ejercicioObj.puntaje || 10,
          restricciones: ejercicioObj.restricciones || '',
          formato_salida: ejercicioObj.formato_salida || '',
          formatos_entrada: Array.isArray(ejercicioObj.formatos_entrada) ? ejercicioObj.formatos_entrada : [],
          ejemplos: Array.isArray(ejercicioObj.ejemplos) ? ejercicioObj.ejemplos : [],
          template: ejercicioObj.template || null,
          tests_avanzados: ejercicioObj.tests_avanzados || null,
          contenido: ejercicioObj.contenido || {},
          pista: ejercicioObj.pista || '',
          etiquetas: ejercicioObj.etiquetas || [],
          credito: ejercicioObj.credito || '',
          
        };

        // En modo historial, preservar lenguaje usado
        if (isHistoryMode.value) {
          // Buscar el language_id en los detalles del historial si existe
          const historialData = localStorage.getItem('currentEvaluation');
          if (historialData) {
            try {
              const parsedHistorial = JSON.parse(historialData);
              if (parsedHistorial.respuestas) {
                const respuestaEjercicio = parsedHistorial.respuestas.find(r => r.ejercicio_id === ejercicioProcesado.id);
                if (respuestaEjercicio && respuestaEjercicio.language_id) {
                  ejercicioProcesado.language_id = respuestaEjercicio.language_id;
                  console.log(`🔧 Language ID ${respuestaEjercicio.language_id} asignado a ejercicio ${ejercicioProcesado.id} desde historial`);
                } else {
                  ejercicioProcesado.language_id = 71; // Python por defecto
                  console.log(`⚠️ No se encontró language_id para ejercicio ${ejercicioProcesado.id}, usando Python por defecto`);
                }
              }
            } catch (e) {
              console.warn('Error al parsear historial para language_id:', e);
              ejercicioProcesado.language_id = 71;
            }
          } else {
            ejercicioProcesado.language_id = 71;
          }
        }

        // Después de procesar cada ejercicio
        console.log('Ejercicio procesado:', {
          id: ejercicioProcesado.id,
          titulo: ejercicioProcesado.titulo,
          pista: ejercicioProcesado.pista,
          etiquetas: ejercicioProcesado.etiquetas,
          credito: ejercicioProcesado.credito,
          contenido: ejercicioProcesado.contenido
        });

        // Si el contenido es una string JSON, intentar parsearlo
        if (typeof ejercicioProcesado.contenido === 'string') {
          try {
            ejercicioProcesado.contenido = JSON.parse(ejercicioProcesado.contenido);
          } catch (e) {
            console.warn('Error al parsear contenido JSON del ejercicio:', e);
          }
        }

        // Mover propiedades desde contenido si están allí y no en el nivel principal
        if (ejercicioProcesado.contenido) {
          // Para cada propiedad potencial en contenido, verificar si ya existe a nivel principal
          const propiedades = ['restricciones', 'formato_salida', 'formatos_entrada', 'ejemplos', 'template', 'tests_avanzados', 'pista'];

          propiedades.forEach(prop => {
            if (!ejercicioProcesado[prop] && ejercicioProcesado.contenido[prop]) {
              ejercicioProcesado[prop] = ejercicioProcesado.contenido[prop];
            }
          });
        }

        // Añade pista por defecto si no existe
        if (!ejercicioProcesado.pista) {
          ejercicioProcesado.pista = ''; // Vacío si no hay pista
        }

        return ejercicioProcesado;
      });
    };

    // Seleccionar ejercicio
    const selectExercise = (index) => {
      if (index >= 0 && index < exercises.value.length) {
        console.log('Cambiando al ejercicio:', index);
        currentExerciseIndex.value = index;

        // Guarda el ejercicio actual antes de cambiar
        if (rightPanelRef.value && rightPanelRef.value.editorRef &&
          rightPanelRef.value.editorRef.saveCurrentCode) {
          rightPanelRef.value.editorRef.saveCurrentCode();
        }

        // Fuerza la actualización del estado del nuevo ejercicio 
        // después de un pequeño retraso para que los componentes se actualicen
        setTimeout(() => {
          if (rightPanelRef.value) {
            const exerciseId = exercises.value[index].id;
            const isCompleted = localStorage.getItem(`exercise_status_${exerciseId}`) === 'completed';

            // Actualiza el estado visualmente
            if (rightPanelRef.value.updateExerciseStatus) {
              rightPanelRef.value.updateExerciseStatus(isCompleted);
            }
          }
        }, 100);
      }
    };

    // Marca un ejercicio como completado
    const markExerciseCompleted = (exerciseId) => {
      if (!exerciseId) return;

      console.log(`markExerciseCompleted llamado para ejercicio ${exerciseId} - considerando usar updateExerciseStatus`);

      // Solo verificar si todos están completados
      checkAllExercisesCompleted();
    };

    // Verifica si todos los ejercicios están completados
    const checkAllExercisesCompleted = () => {
      if (!exercises.value || exercises.value.length === 0) return;

      const userId = getCurrentUserId();
      const evaluationId = evaluation.value?.id || 'unknown';

      const allCompleted = exercises.value.every(exercise => {
        const statusKey = `exercise_status_${userId}_${evaluationId}_${exercise.id}`;
        return localStorage.getItem(statusKey) === 'completed';
      });

      if (allCompleted) {
        console.log('¡Todos los ejercicios están completados!');

        // Muestra notificación
        setTimeout(() => {
          if (notificationRef.value?.showConfirmation) {
            notificationRef.value.showConfirmation(
              '¡Felicidades! Has completado todos los ejercicios. ¿Deseas finalizar la evaluación ahora?',
              () => finishEvaluation(),
              () => {
                if (notificationRef.value?.showNotification) {
                  notificationRef.value.showNotification('Puedes continuar revisando tus respuestas', 'info');
                }
              }
            );
          }
        }, 1000);
      }
    };

    // Valida tiempo restante y finaliza cuando se acabe
    const checkRemainingTime = () => {
      console.log('⏱️ [CHECK-TIME] Verificando tiempo restante...');

      // NUEVA VERIFICACIÓN: No verificar tiempo en modo historial
      if (isHistoryMode.value || viewMode.value === 'history') {
        console.log('⏱️ [CHECK-TIME] Modo historial detectado, omitiendo verificación de tiempo');
        return;
      }

      // Evita procesos paralelos
      if (isProcessingJudge0.value) {
        console.log('⏱️ [CHECK-TIME] Ya estamos procesando con Judge0, esperando...');
        return;
      }

      // Obtiene datos de la evaluación
      const evaluationData = evaluation.value || (localStorage.getItem('currentEvaluation') ?
        JSON.parse(localStorage.getItem('currentEvaluation')) : null);

      if (!evaluationData) {
        console.warn("No hay datos de evaluación disponibles para verificar tiempo");
        return;
      }

      // Calcula el tiempo basado en la fecha de la evaluación o BD
      let startTime, endTime;

      // Primero intenta usar las fechas directas de la evaluación
      if (evaluationData.fecha_inicio) {
        startTime = new Date(evaluationData.fecha_inicio).getTime();
      } else if (evaluationData.startDate) {
        startTime = new Date(evaluationData.startDate).getTime();
      } else {
        // Usa tiempo almacenado localmente
        startTime = parseInt(localStorage.getItem('evaluationStartTime') || '0');
      }

      // Si no hay tiempo de inicio, no se puede calcular
      if (!startTime) {
        console.warn("No se pudo determinar tiempo de inicio de la evaluación");
        return;
      }

      // Calcula tiempo de finalización
      if (evaluationData.fecha_fin) {
        endTime = new Date(evaluationData.fecha_fin).getTime();
      } else if (evaluationData.endDate) {
        endTime = new Date(evaluationData.endDate).getTime();
      } else if (evaluationData.duracion_minutos || evaluationData.duration) {
        const duration = evaluationData.duracion_minutos || evaluationData.duration;
        endTime = startTime + (duration * 60 * 1000);
      } else {
        console.warn("No se pudo determinar duración de la evaluación");
        return;
      }

      // Verifica tiempo actual
      const now = new Date().getTime();
      const timeLeft = endTime - now;

      // Ajusta diseño según el tiempo restante
      if (timeLeft <= 60000) { // Último minuto
        document.body.classList.add('time-critical');
      }

      // Si no hay tiempo restante, finaliza automáticamente
      if (timeLeft <= 0) {
        console.log('🚨 [CHECK-TIME] Tiempo agotado, iniciando finalización automática');

        // Primero detiene todos los intervalos - evitar futuras ejecuciones paralelas
        if (timerInterval) {
          clearInterval(timerInterval);
          timerInterval = null;
          console.log('🔄 [CHECK-TIME] Intervalo de tiempo detenido');
        }

        if (autoSaveInterval) {
          clearInterval(autoSaveInterval);
          autoSaveInterval = null;
          console.log('🔄 [CHECK-TIME] Intervalo de autoguardado detenido');
        }

        // Verifica si ya esta en la página de finalización
        if (router.currentRoute.value.path !== '/evaluacion-completada') {
          // Muestra notificacion al usuario
          if (notificationRef.value?.showNotification) {
            notificationRef.value.showNotification('⏰ Tiempo agotado. Tu evaluación será procesada automáticamente.', 'warning', 0);
          } else {
            alert('El tiempo ha terminado. Tu evaluación será procesada automáticamente.');
          }

          // Intenta guardar el código actual antes de finalizar
          if (rightPanelRef.value && rightPanelRef.value.editorRef &&
            rightPanelRef.value.editorRef.saveCurrentCode) {
            rightPanelRef.value.editorRef.saveCurrentCode();
          }

          // INICIAR PROCESO DE FINALIZACIÓN
          // Se usa directamente la función, NO un setTimeout
          autoFinishEvaluation();
        }
      }
    };



    const autoFinishEvaluation = async () => {
      console.log('🕒 [AUTO-FINISH] Inicio - Tiempo agotado');

      // ASEGURA QUE SOLO SE EJECUTE UNA VEZ - SEMÁFORO DE PREVENCIÓN
      if (isProcessingJudge0.value) {
        console.log('🚫 [AUTO-FINISH] Ya estamos procesando con Judge0');
        return;
      }

      // ACTIVAR SEMÁFORO - PREVIENE EJECUCIONES PARALELAS
      isProcessingJudge0.value = true;

      // Verifica si ya estamos procesando UI
      if (processingAction.value) {
        // Asegura de actualizar el mensaje si ya estaba visible
        processingMessage.value = 'Procesando evaluación, por favor espere...';
      } else {
        // Mostrar UI de procesamiento
        showProcessing('Procesando evaluación, por favor espere...');
      }

      try {
        const updateProgress = (message) => {
          console.log(`📝 [AUTO-FINISH] Progress: ${message}`);
          processingMessage.value = message;
        };

        // PASO 1: Guardar código actual
        updateProgress('Guardando código actual...');

        if (rightPanelRef.value?.editorRef?.saveCurrentCode) {
          rightPanelRef.value.editorRef.saveCurrentCode();
          console.log('💾 [AUTO-FINISH] Código actual guardado');
        }

        // Pequeña pausa para asegurar que el almacenamiento local se complete
        await new Promise(resolve => setTimeout(resolve, 7000));

        // PASO 2: Recopilar todos los códigos de ejercicios
        updateProgress('Recopilando todos los ejercicios...');

        // CORREGIDO: Definir userId al principio de la función
        const userId = getCurrentUserId();

        // USAR LA MISMA CLAVE QUE EditorCodemirror
        const getExerciseCodeKey = (exerciseId) => {
          const evalData = localStorage.getItem('currentEvaluation');
          let evaluationId = 'unknown';

          try {
            const parsedEvaluation = JSON.parse(evalData);
            evaluationId = parsedEvaluation?.id || 'unknown';
          } catch (e) {
            console.warn('Error al parsear evaluación de localStorage');
          }

          return `exercise_code_${userId}_${evaluationId}_${exerciseId}`;
        };

        const ejerciciosParaEnviar = [];
        const evaluationId = evaluation.value?.id || 'unknown';

        for (const ejercicio of exercises.value) {
          if (!ejercicio || !ejercicio.id) {
            console.warn(`Ejercicio sin ID detectado:`, ejercicio);
            continue;
          }

          const codeKey = getExerciseCodeKey(ejercicio.id);
          const codigo = localStorage.getItem(codeKey) || "";

          // CORREGIDO: userId ya está definido arriba
          const languageKey = `exercise_language_${userId}_${evaluationId}_${ejercicio.id}`;
          const savedLanguage = localStorage.getItem(languageKey);
          const languageId = savedLanguage ? parseInt(savedLanguage) : 71; // Python por defecto

          console.log(`[AUTO-FINISH] Ejercicio ${ejercicio.id}: ${codigo.length} caracteres, lenguaje: ${languageId}`);

          ejerciciosParaEnviar.push({
            ejercicio_id: ejercicio.id,
            codigo: codigo,
            language_id: languageId
          });
        }

        if (ejerciciosParaEnviar.length === 0) {
          throw new Error('No hay ejercicios con código para enviar');
        }

        console.log(`✅ [AUTO-FINISH] Total ejercicios recopilados: ${ejerciciosParaEnviar.length}`);

        // PASO 3: Verifica disponibilidad de Judge0
        updateProgress('Verificando disponibilidad de Judge0...');

        let judge0Available = true;
        try {
          const judge0Status = await evaluationsService.checkJudge0Status();

          if (!judge0Status.isAvailable) {
            console.error("❌ Judge0 no disponible:", judge0Status.message);
            judge0Available = false;
          } else {
            console.log("✅ Judge0 disponible, procediendo con envío");
          }
        } catch (judge0Error) {
          console.error("Error verificando Judge0:", judge0Error);
          judge0Available = false;
        }

        // PASO 4: Finalizar en backend PRIMERO (crucial)
        updateProgress('Finalizando evaluación en el servidor...');
        try {
          await evaluationsService.finishEvaluation(evaluation.value.id);
          console.log("✅ [AUTO-FINISH] Evaluación finalizada correctamente en el servidor");
        } catch (finishError) {
          console.error("Error al finalizar evaluación en servidor:", finishError);
          // Continuamos incluso si hay error
        }

        // PASO 5: Enviar a Judge0 y ESPERAR resultados (solo si Judge0 disponible)
        let resultado = null;
        if (judge0Available) {
          updateProgress('Enviando ejercicios a Judge0 para calificación...');
          console.log(`🚀 [AUTO-FINISH] Enviando batch de ${ejerciciosParaEnviar.length} ejercicios para evaluación ${evaluation.value.id}`);

          try {
            // Espera a que submitBatch complete totalmente
            resultado = await evaluationsService.submitBatch({
              evaluacion_id: evaluation.value.id,
              ejercicios: ejerciciosParaEnviar,
              useJudge0: true
            }, exercises.value);

            console.log('✅ [AUTO-FINISH] Resultado recibido de Judge0:', resultado.data);
          } catch (judgeError) {
            console.error("Error en proceso Judge0:", judgeError);
            // Continuamos con proceso en caso de error
          }
        }

        // PASO 6: Guarda resultados de forma MANUAL si no esta funcionando Judge0
        updateProgress('Guardando resultados y códigos...');

        let totalScore = 0;
        let maxScore = 0;
        let scaledScore = 0;

        if (resultado && resultado.data && resultado.data.success) {
          // Usa resultados de Judge0 si los tenemos
          totalScore = resultado.data.total_puntaje || 0;
          maxScore = resultado.data.puntaje_maximo || 0;
          scaledScore = resultado.data.puntaje_sobre_10 || 0;
        } else {
          // Calcula un resultado básico -> mostrar 0 si no hay Judge0
          maxScore = exercises.value.reduce((sum, ej) => sum + (ej.puntaje || 10), 0);
          scaledScore = 0;
        }

        // GUARDA DE MANERA SECUENCIAL - IMPORTANTE
        await new Promise(resolve => {
          // 1. Guarda puntuaciones - userId ya está definido
          localStorage.setItem(`evaluation_total_score_${userId}`, totalScore);
          localStorage.setItem(`evaluation_max_score_${userId}`, maxScore);
          localStorage.setItem(`evaluation_scaled_score_${userId}`, scaledScore);
          localStorage.setItem(`evaluationEndTime_${userId}`, Date.now().toString());

          // 2. Guarda datos raw
          if (resultado && resultado.data) {
            localStorage.setItem(`evaluation_raw_results_${userId}`, JSON.stringify(resultado.data));
          } else {
            // Crea un objeto de resultados básico
            const resultadosBasicos = {
              success: true,
              total_puntaje: totalScore,
              puntaje_maximo: maxScore,
              puntaje_sobre_10: scaledScore,
              ejercicios: ejerciciosParaEnviar
            };
            localStorage.setItem(`evaluation_raw_results_${userId}`, JSON.stringify(resultadosBasicos));
          }

          console.log('💾 [AUTO-FINISH] Puntuaciones guardadas:', {
            total: totalScore,
            max: maxScore,
            scaled: scaledScore
          });

          // 3. Guarda código en formato antiguo
          for (const ejercicio of ejerciciosParaEnviar) {
            if (ejercicio.ejercicio_id && ejercicio.codigo) {
              localStorage.setItem(`exercise_code_${userId}_${ejercicio.ejercicio_id}`, ejercicio.codigo);
              console.log(`💾 [AUTO-FINISH] Guardado código formato antiguo: ${ejercicio.ejercicio_id}`);
            }
          }

          // 4. Guarda el ID de la evaluación
          if (evaluation.value?.id) {
            localStorage.setItem('completedEvaluationId', evaluation.value.id);
            localStorage.setItem(`completedEvaluationId_${userId}`, evaluation.value.id);
            console.log(`ID de evaluación ${evaluation.value.id} guardado para usuario ${userId}`);
          }

          // Confirma que se han guardado todos los datos
          setTimeout(resolve, 500);
        });

        // ASEGURA QUE LOS DATOS SE HAN GUARDADO
        const verificarDatos = () => {
          const storedScore = localStorage.getItem(`evaluation_scaled_score_${userId}`);
          const storedId = localStorage.getItem('completedEvaluationId');
          const storedRaw = localStorage.getItem(`evaluation_raw_results_${userId}`);

          return storedScore && storedId && storedRaw;
        };

        // Verificación explícita
        if (!verificarDatos()) {
          console.warn("⚠️ [AUTO-FINISH] Datos no verificados, esperando más tiempo...");
          await new Promise(resolve => setTimeout(resolve, 1000));
        }

        // PASO 7: Espera antes de redireccionar
        updateProgress('Completado. Redirigiendo a resultados...');
        await new Promise(resolve => setTimeout(resolve, 3000)); // Aumentado a 3 segundos

        // PASO 8: Redirigir a resultados
        localStorage.setItem(`redirect_ready_${userId}`, 'true');
        router.push({
          name: 'EvaluationCompleted',
          query: {
            evaluation_id: evaluation.value?.id,
            ts: Date.now() // Forzar nueva carga
          }
        });

      } catch (error) {
        console.error('❌ [AUTO-FINISH] Error en finalización automática:', error);

        // CORREGIDO: definir userId aquí también
        const userId = getCurrentUserId();
        localStorage.setItem(`evaluation_error_${userId}`, 'true');
        localStorage.setItem(`evaluationEndTime_${userId}`, Date.now().toString());

        // Guardar ID de evaluación incluso si hay error
        if (evaluation.value?.id) {
          localStorage.setItem('completedEvaluationId', evaluation.value.id);
        }

        // Intentar redireccionar con error
        await new Promise(resolve => setTimeout(resolve, 1000));
        router.push({
          name: 'EvaluationCompleted',
          query: {
            evaluation_id: evaluation.value?.id,
            error: 'true'
          }
        });

      } finally {
        // DESACTIVAR SEMÁFORO
        isProcessingJudge0.value = false;

        // Ocultar overlay
        if (router.currentRoute.value.path !== '/evaluacion-completada') {
          hideProcessing();
        }
      }
    };



    // Reintenta carga de datos
    const retryLoading = () => {
      loadEvaluationData();
    };

    // Volver a la pantalla anterior
    const goBack = () => {
      // Usa el sistema de confirmación
      if (notificationRef.value?.showConfirmation) {
        notificationRef.value.showConfirmation(
          '¿Estás seguro de que quieres salir? Perderás tu progreso si no has guardado.',
          () => router.push('/evaluation-access'),
          () => {
            if (notificationRef.value?.showNotification) {
              notificationRef.value.showNotification('Continúa con tu evaluación', 'info');
            }
          }
        );
      } else {
        // Fallback si no hay sistema de notificaciones
        router.push('/evaluation-access');
      }
    };

    // Registra inicio de evaluación
    const registerEvaluationStart = async () => {
      if (!evaluation.value?.id) return;

      const userId = store.getters['auth/userId'];
      if (!userId) return;

      try {
        console.log('Registrando inicio de evaluación:', evaluation.value.id, userId);

        // Intenta inscribir al estudiante de forma explícita
        try {
          const accessCode = localStorage.getItem('evaluation_access_code') ||
            localStorage.getItem('temp_access_code');

          if (accessCode) {
            await evaluationsService.inscribirEstudiante(evaluation.value.id, {
              codigo: accessCode
            });

            console.log('Estudiante inscrito correctamente en la evaluación');
          }
        } catch (inscriptionError) {
          console.warn('Error al inscribir estudiante (posiblemente ya inscrito):', inscriptionError);
        }

        // Guarda el código de acceso para futuros intentos
        const accessCode = localStorage.getItem('temp_access_code');
        if (accessCode) {
          localStorage.setItem('evaluation_access_code', accessCode);
          localStorage.removeItem('temp_access_code');
        }
      } catch (e) {
        console.error('Error al registrar inicio de evaluación:', e);
      }
    };

    // Finaliza la evaluación
    const finishEvaluation = async () => {
      try {
        showProcessing("Finalizando evaluación...");

        // Calcula la puntuación total
        calculateTotalScore();

        // Guarda timestamp de finalización y ID de evaluación
        const userId = getCurrentUserId();
        localStorage.setItem(`evaluationEndTime_${userId}`, Date.now().toString());

        // Guarda ID de evaluación usando userId como clave
        if (evaluation.value?.id) {
          // Guarda en formato tradicional y específico por usuario
          localStorage.setItem('completedEvaluationId', evaluation.value.id);
          localStorage.setItem(`completedEvaluationId_${userId}`, evaluation.value.id);
          console.log(`ID de evaluación ${evaluation.value.id} guardado para usuario ${userId}`);
        }

        // Llama a la API para registrar finalización
        try {
          if (evaluation.value?.id) {
            await evaluationsService.finishEvaluation(evaluation.value.id);
          }
        } catch (finishError) {
          console.warn('Error al finalizar evaluación en API:', finishError);
        }

        // Navega a la página de resultados con evaluation_id
        hideProcessing();

        // Usa SOLO query para el ID (no params)
        router.push({
          name: 'EvaluationCompleted',
          query: { evaluation_id: evaluation.value?.id }
        });
      } catch (error) {
        console.error('Error al finalizar evaluación:', error);
        hideProcessing();

        if (notificationRef.value?.showNotification) {
          notificationRef.value.showNotification('Hubo un error al finalizar la evaluación, pero tus resultados han sido guardados.', 'warning');
        }

        // Si hay un error, pasa el ID correctamente en SOLO query
        router.push({
          name: 'EvaluationCompleted',
          query: { evaluation_id: evaluation.value?.id }
        });
      }
    };

    // Calcula la puntuación total de todos los ejercicios
    const calculateTotalScore = () => {
      const scoresKey = 'evaluation_exercise_scores';
      const savedScores = localStorage.getItem(scoresKey);

      if (!savedScores) return 0;

      try {
        const scores = JSON.parse(savedScores);
        let totalScore = 0;
        let totalMaxScore = 0;

        // Suma puntuaciones
        Object.values(scores).forEach(item => {
          totalScore += item.score || 0;
          totalMaxScore += item.maxScore || 0;
        });

        // Convierte a escala de 10
        let scaledScore = totalMaxScore > 0 ? (totalScore / totalMaxScore) * 10 : 0;
        scaledScore = parseFloat(scaledScore.toFixed(2));

        // Guarda en localStorage
        localStorage.setItem('evaluation_total_score', totalScore);
        localStorage.setItem('evaluation_max_score', totalMaxScore);
        localStorage.setItem('evaluation_scaled_score', scaledScore);

        console.log(`Puntuación calculada: ${totalScore}/${totalMaxScore} - Escala 10: ${scaledScore}`);
        return scaledScore;
      } catch (error) {
        console.error('Error al calcular puntuación total:', error);
        return 0;
      }
    };

    const setupAutoSave = () => {
      // No configurar auto-guardado en modo historial
      if (isHistoryMode.value || viewMode.value === 'history') {
        console.log('Modo historial detectado - NO se configura auto-guardado');
        return;
      }

      // Verifica y guardar cada minuto
      autoSaveInterval = setInterval(() => {
        // Verifica tiempo restante (solo si no es modo historial)
        if (!isHistoryMode.value && viewMode.value !== 'history') {
          checkRemainingTime();
        }

        // Guarda estado actual si hay un panel derecho con editor (solo si no es modo historial)
        if (!isHistoryMode.value && viewMode.value !== 'history' &&
          rightPanelRef.value && rightPanelRef.value.editorRef &&
          rightPanelRef.value.editorRef.saveCurrentCode) {
          rightPanelRef.value.editorRef.saveCurrentCode();
          console.log('Auto-guardado activado');
        }
      }, 60000); // Cada minuto
    };

    // Expone datos y métodos a los componentes hijos
    provide('viewMode', viewMode);
    provide('isHistoryMode', isHistoryMode);
    provide('evaluation', evaluation);
    provide('exercises', exercises);
    provide('currentExerciseIndex', currentExerciseIndex);
    provide('selectExercise', selectExercise);
    provide('markExerciseCompleted', markExerciseCompleted);
    provide('leftPanelRef', leftPanelRef);
    provide('rightPanelRef', rightPanelRef); // Nuevo
    provide('finishEvaluation', finishEvaluation);

    // Proveer notificationRef en lugar de los métodos directamente
    provide('notificationRef', notificationRef);

    const saveCurrentState = () => {
      if (rightPanelRef.value?.editorRef?.saveCurrentCode) {
        rightPanelRef.value.editorRef.saveCurrentCode();
      }
    };

    // También provee los métodos wrapper para compatibilidad
    provide('showNotification', (message, type = 'info', duration = 3000) => {
      if (notificationRef.value?.showNotification) {
        notificationRef.value.showNotification(message, type, duration);
      } else {
        console.warn('Notification system not ready, using alert:', message);
        alert(message);
      }
    });

    provide('showConfirmation', (message, onConfirm, onCancel = null, options = {}) => {
      if (notificationRef.value?.showConfirmation) {
        notificationRef.value.showConfirmation(message, onConfirm, onCancel, options);
      } else {
        console.warn('Confirmation system not ready, using confirm:', message);
        if (confirm(message)) {
          onConfirm?.();
        } else {
          onCancel?.();
        }
      }
    });

    // Observa cambios en el ID de evaluación
    watch(evaluationId, (newId) => {
      if (newId && newId !== evaluation.value?.id) {
        console.log('ID de evaluación cambió, recargando datos');
        loadEvaluationData();
      }
    });

    watch(() => route.query.mode, (newMode) => {
      if (newMode) {
        console.log('Cambio de modo detectado en ruta:', newMode);
        viewMode.value = newMode;

        if (newMode === 'history') {
          localStorage.setItem('view_mode', 'history');
        }
      }
    }, { immediate: true });

    // Observar cambios en el modo historial para detener intervalos
    watch(isHistoryMode, (newIsHistory, oldIsHistory) => {
      console.log('Cambio en modo historial detectado:', { antes: oldIsHistory, ahora: newIsHistory });

      if (newIsHistory && !oldIsHistory) {
        // Cambió a modo historial - detener todos los intervalos
        console.log('Cambiando a modo historial - deteniendo intervalos');

        if (timerInterval) {
          clearInterval(timerInterval);
          timerInterval = null;
          console.log('Intervalo de tiempo detenido por cambio a modo historial');
        }

        if (autoSaveInterval) {
          clearInterval(autoSaveInterval);
          autoSaveInterval = null;
          console.log('Intervalo de auto-guardado detenido por cambio a modo historial');
        }

        // Actualizar localStorage
        localStorage.setItem('view_mode', 'history');
      } else if (!newIsHistory && oldIsHistory) {
        // Cambió de modo historial a modo normal - reiniciar intervalos si es necesario
        console.log('Cambiando de modo historial a modo normal - reiniciando intervalos');

        if (!timerInterval && evaluation.value) {
          timerInterval = setInterval(checkRemainingTime, 1000);
          console.log('Intervalo de tiempo reiniciado');
        }

        if (!autoSaveInterval) {
          setupAutoSave();
          console.log('Auto-guardado reiniciado');
        }

        // Limpiar localStorage
        localStorage.removeItem('view_mode');
      }
    }, { immediate: true });

    onMounted(async () => {
      nextTick(() => {
        if (leftPanelRef.value) {
          console.log('Panel izquierdo montado correctamente');
        }
        if (rightPanelRef.value) {
          console.log('Panel derecho montado correctamente');
        }
      });

      console.log('PracticalExercises montado, iniciando carga de datos');
      await loadEvaluationData();

      // Verificar modo historial
      if (isHistoryMode.value || viewMode.value === 'history') {
        console.log('Modo historial activado para evaluación ID:', evaluationId.value);
        // Configuraciones especiales para modo historial
        // Esto impedirá cualquier modificación o envío
        localStorage.setItem('view_mode', 'history');
      }

      // Registrar inicio de evaluación y configurar auto-guardado
      nextTick(() => {
        // Verificar que el sistema de notificaciones esté disponible
        if (notificationRef.value) {
          console.log('Sistema de notificaciones montado correctamente');
          console.log('Métodos disponibles:', {
            showNotification: !!notificationRef.value.showNotification,
            showConfirmation: !!notificationRef.value.showConfirmation
          });
        } else {
          console.error('NotificationSystem no está disponible');
        }

        registerEvaluationStart();
        setupAutoSave();

        // MODIFICADO: Solo iniciar verificación de tiempo si NO estamos en modo historial
        if (!isHistoryMode.value && viewMode.value !== 'history') {
          console.log('Iniciando verificación de tiempo para evaluación activa');
          timerInterval = setInterval(checkRemainingTime, 1000);
        } else {
          console.log('Modo historial detectado - NO se inicia verificación de tiempo');
        }

        // Asegurar que los ejercicios se cargan correctamente
        console.log(`Cargados ${exercises.value.length} ejercicios`);

        // Forzar una limpieza del localStorage si es necesario
        const shouldReset = localStorage.getItem('reset_exercises_cache');
        if (shouldReset === 'true') {
          console.log('Limpiando caché de ejercicios');
          exercises.value.forEach(ex => {
            localStorage.removeItem(`exercise_code_${ex.id}`);
            localStorage.removeItem(`exercise_status_${ex.id}`);
          });
          localStorage.removeItem('reset_exercises_cache');
        }

        // Si hay ejercicios disponibles, seleccionar el primero explícitamente
        if (exercises.value.length > 0) {
          console.log('Seleccionando el primer ejercicio explícitamente');
          currentExerciseIndex.value = 0;
          selectExercise(0);
        }
      });
    });

    const loadExerciseDetails = async () => {
      if (!evaluationId.value) {
        console.error('No hay ID de evaluación válido');
        return;
      }

      try {
        console.log(`Cargando ejercicios mediante detalles de evaluación ID: ${evaluationId.value}`);
        const response = await evaluationsService.getDetallesEvaluacion(evaluationId.value);
        console.log('Respuesta completa de detalles:', response.data);

        // Verificar si hay ejercicios
        if (response.data && response.data.ejercicios) {
          console.log('Ejercicios obtenidos de detalles:', response.data.ejercicios.length);

          // Log detallado para depuración de etiquetas
          response.data.ejercicios.forEach(ejercicio => {
            console.log('\n==== DETALLE DE EJERCICIO ====');
            console.log('ID:', ejercicio.id);
            console.log('Título:', ejercicio.titulo);

            // Verificar etiquetas directamente
            if (ejercicio.etiquetas) {
              console.log('Etiquetas directas:', ejercicio.etiquetas);
            } else {
              console.log('No tiene etiquetas directas');
            }

            // Verificar etiquetas en contenido
            if (ejercicio.contenido) {
              const contenido = typeof ejercicio.contenido === 'string'
                ? JSON.parse(ejercicio.contenido)
                : ejercicio.contenido;

              if (contenido && contenido.etiquetas) {
                console.log('Etiquetas en contenido:', contenido.etiquetas);
              } else {
                console.log('No tiene etiquetas en contenido');
              }
            } else {
              console.log('No tiene contenido');
            }
            console.log('============================\n');
          });

          exercises.value = [...response.data.ejercicios];
          console.log('Ejercicios procesados:', exercises.value);

          // Actualizar evaluación actual
          currentEvaluation.value = {
            id: response.data.id,
            title: response.data.titulo,
            description: response.data.descripcion,
            duration: response.data.duracion_minutos,
            startDate: response.data.fecha_inicio,
            endDate: response.data.fecha_fin,
            accessCode: response.data.codigo_acceso,
            showResults: response.data.mostrar_resultado,
            allowReview: response.data.permitir_revision,
            randomOrder: response.data.orden_aleatorio
          };

          // Guardar en localStorage
          localStorage.setItem('current_evaluation', JSON.stringify(currentEvaluation.value));
        } else {
          console.error('No se encontraron ejercicios en la respuesta de detalles');
        }
      } catch (error) {
        console.error('Error al cargar detalles de la evaluación:', error);
      }
    };

    // Añadir función de diagnóstico global
    window.diagnosticarEtiquetas = () => {
      const leftPanel = document.querySelector('[data-component="PracticalLeftPanel"]')?.__vueParentComponent?.ctx;

      if (!leftPanel) {
        console.error('No se pudo encontrar el componente PracticalLeftPanel');
        return;
      }

      const currentExercise = leftPanel.currentExercise;

      console.log('\n===== DIAGNÓSTICO DE ETIQUETAS =====');
      console.log('Ejercicio actual:', currentExercise?.titulo);

      if (!currentExercise) {
        console.error('No hay ejercicio actual');
        return;
      }

      console.log('Propiedades del ejercicio:', Object.keys(currentExercise));

      // Verificar etiquetas directas
      if (currentExercise.etiquetas) {
        console.log('Etiquetas directas:', currentExercise.etiquetas);
      } else {
        console.log('No tiene etiquetas directas');
      }

      // Verificar etiquetas en contenido
      if (currentExercise.contenido) {
        let contenido;
        try {
          contenido = typeof currentExercise.contenido === 'string'
            ? JSON.parse(currentExercise.contenido)
            : currentExercise.contenido;

          console.log('Contenido parseado:', contenido);

          if (contenido && contenido.etiquetas) {
            console.log('Etiquetas en contenido:', contenido.etiquetas);
          } else {
            console.log('No tiene etiquetas en contenido');
          }
        } catch (e) {
          console.error('Error al parsear contenido:', e);
        }
      } else {
        console.log('No tiene contenido');
      }

      // Verificar funciones del componente
      console.log('hasEtiquetas():', leftPanel.hasEtiquetas);
      console.log('currentExerciseTags:', leftPanel.currentExerciseTags);

      console.log('===================================\n');
    };

    // Manejar eventos de navegación
    const handleBeforeLeaveNavigation = (e) => {
      // Solo manejar navegaciones no controladas por Vue Router
      if (window.location.pathname === '/practical-exercises') {
        e.preventDefault();
        e.returnValue = '';

        // Usar el sistema de confirmación si está disponible
        if (notificationRef.value?.showConfirmation) {
          notificationRef.value.showConfirmation(
            '¿Estás seguro de que quieres abandonar la evaluación? Tu progreso se perderá.',
            () => {
              window.removeEventListener('beforeunload', handleBeforeLeaveNavigation);
              window.location.href = '/evaluation-access';
            },
            () => {
              // Si el usuario decidió quedarse, no hacer nada
            }
          );
        }

        return '';
      }
    };

    // Interceptar navegación con teclado
    const handleKeyPress = (e) => {
      // Prevenir retroceso con tecla Backspace fuera de campos editables
      if (e.key === 'Backspace' &&
        !['INPUT', 'TEXTAREA'].includes(e.target.tagName)) {
        e.preventDefault();
      }

      // Previene la navegación con Alt + Izquierda/Derecha
      if (e.altKey && (e.key === 'ArrowLeft' || e.key === 'ArrowRight')) {
        e.preventDefault();
        e.stopPropagation();
      }
    };

    onBeforeUnmount(() => {
      // Limpiar intervalos
      if (autoSaveInterval) clearInterval(autoSaveInterval);
      if (timerInterval) clearInterval(timerInterval);

      // Guardar el código actual antes de desmontar
      if (rightPanelRef.value && rightPanelRef.value.editorRef &&
        rightPanelRef.value.editorRef.saveCurrentCode) {
        rightPanelRef.value.editorRef.saveCurrentCode();
      }

      // Remover event listeners
      window.removeEventListener('beforeunload', handleBeforeLeaveNavigation);
      document.removeEventListener('keydown', handleKeyPress);
    });

    return {
      evaluation,
      exercises,
      currentExerciseIndex,
      loading,
      error,
      selectExercise,
      retryLoading,
      goBack,
      leftPanelRef,
      rightPanelRef,
      loadExerciseDetails,
      processingAction,
      processingMessage,
      viewMode,
      isHistoryMode,
      notificationRef
    };
  }
};
</script>

<style>
/* Variables globales para todo el sistema */
:root {
  /* Colores base */
  --color-bg-main: #1C1C21;
  --color-bg-element: #2A2A30;
  --color-bg-element-alt: #25252A;
  --color-bg-element-hover: #32323A;
  --color-border: #36363c;
  --color-border-focus: #7E91FF;
  --color-text-primary: #ffffff;
  --color-text-secondary: #e0e0e0;
  --color-text-muted: #9090A0;

  /* Colores de la paleta */
  --color-primary: #EBB300;
  --color-primary-light: #FFD03F;
  --color-primary-dark: #C89500;
  --color-secondary: #6B7280;
  --color-success: #9DBEB6;
  --color-info: #65B1C1;
  --color-warning: #FFBD2E;
  --color-danger: #FF6B6B;

  /* Otros */
  --border-radius-lg: 12px;
  --border-radius: 8px;
  --border-radius-sm: 6px;
  --shadow-lg: 0 8px 16px rgba(0, 0, 0, 0.2);
  --shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
  --shadow-sm: 0 2px 6px rgba(0, 0, 0, 0.1);
  --transition-fast: 0.2s;
  --transition-smooth: 0.3s;
}
</style>

<style scoped>
.practical-exercises-wrapper {
  display: flex;
  flex-direction: column;
  height: 100vh;
  background-color: var(--color-bg-main, #1C1C21);
}

.exercise-layout {
  display: flex;
  flex-direction: column;
  height: calc(100vh - 56px);
}

.main-content {
  flex: 1;
  margin: 0;
  overflow: hidden;
}

.columns {
  flex-grow: 1;
  margin: 0;
}

.loading-overlay,
.error-overlay,
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-color: rgba(28, 28, 33, 0.9);
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  z-index: 1000;
}

.loading-spinner {
  width: 50px;
  height: 50px;
  border: 5px solid #333;
  border-radius: 50%;
  border-top-color: var(--color-primary, #EBB300);
  animation: spin 1s linear infinite;
  margin-bottom: 20px;
}

@keyframes spin {
  to {
    transform: rotate(360deg);
  }
}

.error-container,
.loading-container {
  background-color: var(--color-bg-element, #2A2A30);
  padding: 30px;
  border-radius: var(--border-radius, 8px);
  text-align: center;
  max-width: 500px;
  width: 90%;
  box-shadow: var(--shadow, 0 4px 12px rgba(0, 0, 0, 0.15));
}

.loading-container {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
}

.error-container h2 {
  color: var(--color-primary, #EBB300);
  margin-bottom: 15px;
  font-size: 1.5rem;
}

.error-container p,
.loading-container p {
  color: var(--color-text-primary, #FFFFFF);
  margin-bottom: 20px;
}

.error-container .button {
  background-color: var(--color-primary, #EBB300);
  color: var(--color-bg-main, #1C1C21);
  border: none;
  padding: 10px 16px;
  border-radius: var(--border-radius-sm, 6px);
  margin: 5px;
  cursor: pointer;
  font-weight: 600;
  transition: all var(--transition-fast, 0.2s) ease;
}

.error-container .button:hover {
  background-color: var(--color-primary-light, #FFD03F);
  transform: translateY(-2px);
}

.error-container .button.is-secondary {
  background-color: var(--color-bg-element-alt, #25252A);
  color: var(--color-text-primary, #FFFFFF);
  border: 1px solid var(--color-border, #36363c);
}

.error-container .button.is-secondary:hover {
  background-color: var(--color-bg-element-hover, #32323A);
}

/* Estilos de tiempo agotado de la evaluacion */
.processing-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-color: rgba(0, 0, 0, 0.8);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 9999;
  animation: fadeIn 0.3s ease;
}

.processing-modal {
  background-color: #2A2A35;
  border-radius: 12px;
  padding: 2rem;
  min-width: 300px;
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.3);
  border: 1px solid #FFD03F;
  text-align: center;
  animation: slideIn 0.3s ease;
}

.processing-content h3 {
  color: #FFD03F;
  margin: 1rem 0;
  font-size: 1.5rem;
}

.processing-content p {
  color: #E0E0E0;
  margin-bottom: 1.5rem;
}

.timer-spinner {
  width: 50px;
  height: 50px;
  border: 4px solid #36363C;
  border-top-color: #FFD03F;
  border-radius: 50%;
  margin: 0 auto;
  animation: spin 1s linear infinite;
}

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

@keyframes slideIn {
  from {
    transform: translateY(-20px);
    opacity: 0;
  }

  to {
    transform: translateY(0);
    opacity: 1;
  }
}
</style>