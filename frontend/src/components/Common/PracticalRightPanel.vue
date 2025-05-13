<!-- components/Common/PracticalRightPanel.vue -->
<template>
  <div class="right-panel-wrapper" :class="{ 'is-full-screen': isFullScreen, 'history-mode': isHistoryMode }">
    <div class="practical-right-panel">
      <div class="panel-header">
        <div class="header-title">
          <span class="header-icon">💻</span>
          <h3>Código: <span v-if="currentExercise">Ejercicio {{ currentExerciseNumber }}</span></h3>
        </div>

        <!-- Selector de temas -->
        <div class="theme-selector">
          <select v-model="selectedTheme" class="theme-select" @change="changeTheme">
            <option value="dracula">Dracula</option>
            <option value="material">Material Dark</option>
            <option value="nord">Nord</option>
            <option value="solarized">Solarized Dark</option>
            <option value="tokyo">Tokyo Night</option>
            <option value="vscode">VS Code Dark</option>
            <option value="onedark">One Dark</option>
          </select>
        </div>

        <!-- Botón expandir -->
        <button class="expand-button" @click="toggleFullScreen">
          <svg v-if="!isFullScreen" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor">
            <path d="M8 3H5a2 2 0 0 0-2 2v3m18 0V5a2 2 0 0 0-2-2h-3m0 18h3a2 2 0 0 0 2-2v-3M3 16v3a2 2 0 0 0 2 2h3"
              stroke-width="2" stroke-linecap="round" stroke-linejoin="round" />
          </svg>
          <svg v-else width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor">
            <path d="M4 14h6m0 0v6m0-6-7 7m17-11h-6m0 0V4m0 6 7-7" stroke-width="2" stroke-linecap="round"
              stroke-linejoin="round" />
          </svg>
        </button>
      </div>
      
      <!-- Contenedor del editor -->
      <div class="editor-container">
        <EditorCodemirror 
          ref="editorRef" 
          :is-full-screen="isFullScreen" 
          :theme="selectedTheme"
          :read-only="isHistoryMode" 
        />
      </div>

      <div class="panel-footer" :class="{ 'is-hidden': isFullScreen }">
        <!-- Botones de ayuda (helper buttons) - Sección de Pista y Reiniciar -->
        <div class="helper-buttons">
          <button 
            class="helper-button hint-button" 
            title="Ver pista" 
            @click="toggleHintModal"
            :disabled="isHistoryMode">
            <span class="helper-icon">💡</span>
            <span class="helper-text">PISTA</span>
          </button>

          <button 
            class="helper-button reset-button" 
            title="Reiniciar código" 
            @click="resetCode"
            :disabled="isHistoryMode">
            <span class="helper-icon">🔄</span>
            <span class="helper-text">REINICIAR</span>
          </button>
        </div>
        
        <!-- Botones de acción (TEST y ENVIAR) -->
        <div class="action-buttons">
          <button 
            class="action-button test-button" 
            @click="runTest"
            :disabled="isHistoryMode || isTestExecuting || !currentExercise || isExerciseComplete"
            :title="isHistoryMode ? 'Modo solo lectura' : (isExerciseComplete ? 'Ejercicio ya completado' : 'Probar solución')"
          >
            <span class="button-icon" :class="{ 'rotating': isTestExecuting }">🧪</span>
            <span v-if="isExerciseComplete">✓</span>
            <span v-else-if="isTestExecuting">EJECUTANDO...</span>
            <span v-else>TEST</span>
          </button>

          <button 
            class="action-button submit-button" 
            @click="submitCode"
            :disabled="isHistoryMode || isSubmitExecuting || !currentExercise"
          >
            <span v-if="isSubmitExecuting" class="loading-dots">
              <span class="dot"></span>
              <span class="dot"></span>
              <span class="dot"></span>
            </span>
            <template v-else>
              <span class="button-icon">📤</span>
              ENVIAR
            </template>
          </button>
        </div>
      </div>

      <!-- Botón flotante solo visible en modo pantalla completa -->
      <button v-if="isFullScreen" class="expand-button-fixed" @click="toggleFullScreen">
        <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor">
          <path d="M4 14h6m0 0v6m0-6-7 7m17-11h-6m0 0V4m0 6 7-7" stroke-width="2" stroke-linecap="round"
            stroke-linejoin="round" />
        </svg>
      </button>

      <!-- Modal de pistas -->
      <div class="modal-overlay" v-if="showHintModal" @click.self="toggleHintModal">
        <div class="modal-card hint-modal">
          <div class="modal-header">
            <h3>
              <span class="modal-icon">💡</span>
              Pista
            </h3>
          </div>
          <div class="modal-body">
            <p>{{ hintContent }}</p>
          </div>
          <div class="modal-footer">
            <button class="modal-button" @click="toggleHintModal">Entendido</button>
          </div>
        </div>
      </div>

      <!-- Modal de confirmación para enviar -->
      <div class="modal-overlay" v-if="showSubmitModal" @click.self="toggleSubmitModal">
        <div class="modal-card submit-modal">
          <div class="modal-header">
            <h3>
              <span class="modal-icon">🚀</span>
              Confirmar envío
            </h3>
            <button class="modal-close" @click="toggleSubmitModal">&times;</button>
          </div>
          <div class="modal-body">
            <p>
              ¿Estás seguro de enviar tu solución? Esta acción no se puede deshacer.
            </p>
            <p v-if="pendingExercisesCount > 0" class="warning-message">
              <span class="warning-icon">⚠️</span>
              Aún te quedan {{ pendingExercisesCount }} ejercicio(s) por completar.
              Puedes seguir trabajando en ellos antes de enviar.
            </p>
            <div v-if="completedExercisesCount > 0" class="success-message">
              <span class="success-icon">✅</span>
              Has completado {{ completedExercisesCount }} de {{ exercises.length }} ejercicios con éxito.
            </div>
          </div>
          <div class="modal-footer">
            <button class="modal-button cancel-button" @click="toggleSubmitModal">Cancelar</button>
            <button class="modal-button confirm-button" @click="confirmSubmit">Confirmar envío</button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, inject, onMounted, onBeforeUnmount, computed, watch, nextTick, defineExpose } from 'vue';
import { useRouter } from 'vue-router';
import EditorCodemirror from '../EditorCodemirror.vue';
import judge0Service from '@/services/judge0Service';
import evaluationsService from '@/api/evaluationsService';

export default {
  name: 'PracticalRightPanel',
  components: {
    EditorCodemirror
  },
  setup() {
    const router = useRouter();
    const editorRef = ref(null);
    const isFullScreen = ref(false);
    const showHintModal = ref(false);
    const showSubmitModal = ref(false);
    const isTestExecuting = ref(false);
    const isSubmitExecuting = ref(false);
    const hintContent = ref('');
    
    // Inyecciones
    const isHistoryMode = inject('isHistoryMode', ref(false));
    const exercises = inject('exercises', ref([]));
    const currentExerciseIndex = inject('currentExerciseIndex', ref(0));
    const evaluation = inject('evaluation', ref(null)); //  Asegúrar de inyectar evaluation
    const leftPanelRef = inject('leftPanelRef', null);
    const notificationRef = inject('notificationRef', null);
    const markExerciseCompleted = inject('markExerciseCompleted', () => {
      console.warn('markExerciseCompleted no disponible');
    });

    console.log("Modo Historia inicializado:", isHistoryMode.value);

    // Función para mostrar notificaciones
    const showNotification = (message, type = 'info', duration = 3000) => {
      if (notificationRef?.value?.showNotification) {
        notificationRef.value.showNotification(message, type, duration);
      } else {
        console.warn('Sistema de notificaciones no disponible');
        alert(message);
      }
    };

    const showConfirmation = (message, onConfirm, onCancel = null, options = {}) => {
      if (notificationRef?.value?.showConfirmation) {
        notificationRef.value.showConfirmation(message, onConfirm, onCancel, options);
      } else {
        console.warn('Sistema de confirmación no disponible');
        if (confirm(message)) {
          onConfirm?.();
        } else {
          onCancel?.();
        }
      }
    };

    // Funciones de utilidad
    const getCurrentUserId = () => {
      return localStorage.getItem('user_id') || 'anonymous';
    };

    const getExerciseStatusKey = (exerciseId) => {
      const userId = getCurrentUserId();
      const evaluationId = evaluation.value?.id || 'unknown';
      return `exercise_status_${userId}_${evaluationId}_${exerciseId}`;
    };

    const getExerciseCodeKey = (exerciseId) => {
      const userId = localStorage.getItem('user_id') || 'anonymous';
      const evalData = localStorage.getItem('currentEvaluation');
      const evaluationId = evalData ? JSON.parse(evalData)?.id : 'unknown';
      return `exercise_code_${userId}_${evaluationId}_${exerciseId}`;
    };

    const getScoresKey = () => {
      const userId = getCurrentUserId();
      const evaluationId = evaluation.value?.id || 'unknown';
      return `evaluation_exercise_scores_${userId}_${evaluationId}`;
    };

    // Función para limpiar estados antiguos
    const cleanOldStates = () => {
      const userId = getCurrentUserId();
      const evaluationId = evaluation.value?.id;
      
      if (evaluationId && exercises.value?.length > 0) {
        console.log(`🧹 Limpiando estados antiguos para evaluación ${evaluationId}`);
        
        exercises.value.forEach(exercise => {
          if (!exercise?.id) return;

          // Claves antiguas sin evaluationId
          const oldStatusKey = `exercise_status_${userId}_${exercise.id}`;
          const oldCodeKey = `exercise_code_${userId}_${exercise.id}`;
          
          // Remover claves antiguas
          localStorage.removeItem(oldStatusKey);
          
          // También limpiar el nuevo formato para esta evaluación
          const statusKey = getExerciseStatusKey(exercise.id);
          localStorage.removeItem(statusKey);

          console.log(`Limpiado estado para ejercicio ${exercise.id}`);
        });
        
        // Limpiar lista de ejercicios completados (formato antiguo)
        const oldCompletedKey = `completed_exercises_${userId}`;
        localStorage.removeItem(oldCompletedKey);
        
        console.log(`✅ Limpieza completada para evaluación ${evaluationId}`);
      }
    };

    // Método para reiniciar los estados completamente
    const resetEvaluationStates = () => {
      const userId = getCurrentUserId();
      const evaluationId = evaluation.value?.id;
      
      if (!evaluationId) return;
      
      console.log(`🔄 Reiniciando estados para evaluación ${evaluationId}`);
      
      // Reiniciar todos los estados de esta evaluación
      if (exercises.value?.length > 0) {
        exercises.value.forEach(exercise => {
          const statusKey = getExerciseStatusKey(exercise.id);
          localStorage.removeItem(statusKey);
        });
      }
      
      // Reiniciar lista de ejercicios completados
      const completedKey = `completed_exercises_${userId}_${evaluationId}`;
      localStorage.removeItem(completedKey);
      
      // Reiniciar puntuaciones
      const scoresKey = getScoresKey();
      localStorage.removeItem(scoresKey);
      
      console.log(`✅ Estados reiniciados para evaluación ${evaluationId}`);
    };

    // Llamar a limpieza inmediatamente cuando se monte o cambie la evaluación
    watch([evaluation, exercises], ([newEvaluation, newExercises]) => {
      if (newEvaluation?.id && newExercises?.length > 0) {
        cleanOldStates();
      }
    }, { immediate: true });

    // Computed properties
    const currentExercise = computed(() => {
      if (!exercises.value || exercises.value.length === 0) {
        return null;
      }
      
      if (currentExerciseIndex.value >= exercises.value.length) {
        return exercises.value[0];
      }
      
      return exercises.value[currentExerciseIndex.value];
    });

    const isExerciseComplete = computed(() => {
      if (!currentExercise.value) return false;
      
      const status = getExerciseStatus(currentExercise.value.id);
      return status === 'completed';
    });

    // Estado para el tema seleccionado
    const selectedTheme = ref(localStorage.getItem('editor_theme') || 'dracula');
    
    const changeTheme = () => {
      console.log(`Tema cambiado a: ${selectedTheme.value}`);
    };

    const currentExerciseNumber = computed(() => {
      return `${currentExerciseIndex.value + 1}`;
    });

    const pendingExercisesCount = computed(() => {
      if (!exercises.value) return 0;
      
      return exercises.value.filter(ex => {
        const status = getExerciseStatus(ex.id);
        return status !== 'completed';
      }).length;
    });

    const completedExercisesCount = computed(() => {
      if (!exercises.value) return 0;
      
      return exercises.value.filter(ex => {
        const status = getExerciseStatus(ex.id);
        return status === 'completed';
      }).length;
    });
    
    // Obtener estado de un ejercicio desde localStorage
    const getExerciseStatus = (exerciseId) => {
      if (!exerciseId) return 'pending';
      
      const statusKey = getExerciseStatusKey(exerciseId);
      const status = localStorage.getItem(statusKey);
      
      // DEBUG: verificar claves antiguas
      const userId = getCurrentUserId();
      const oldKey = `exercise_status_${userId}_${exerciseId}`;
      const oldStatus = localStorage.getItem(oldKey);
      
      if (oldStatus) {
        console.warn(`⚠️ Encontrada clave antigua para ejercicio ${exerciseId}. Limpiando...`);
        localStorage.removeItem(oldKey);
      }
      
      return status || 'pending';
    };
    
    // Toggle modales
    const toggleHintModal = () => {
      if (isHistoryMode.value) return;
      
      showHintModal.value = !showHintModal.value;
      
      if (showHintModal.value && currentExercise.value) {
        console.log('Extrayendo pista del ejercicio:', currentExercise.value);
        hintContent.value = extractHint(currentExercise.value);
        console.log('Pista extraída:', hintContent.value);
      }
    };
    
    const extractHint = (exercise) => {
      console.log('=== DETALLES DEL EJERCICIO ===');
      console.log('Ejercicio completo:', JSON.stringify(exercise, null, 2));
      console.log('Campos disponibles:', Object.keys(exercise));

      if (exercise.pista) {
        return exercise.pista;
      }

      if (exercise.contenido) {
        if (typeof exercise.contenido === 'object') {
          console.log('Campos en contenido:', Object.keys(exercise.contenido));
          console.log('Valor de pista en contenido:', exercise.contenido.pista);
          return exercise.contenido.pista || exercise.contenido.hint || 'No hay pistas disponibles para este ejercicio.';
        } else if (typeof exercise.contenido === 'string') {
          try {
            const parsed = JSON.parse(exercise.contenido);
            return parsed.pista || parsed.hint || 'No hay pistas disponibles para este ejercicio.';
          } catch (e) {
            console.warn('Error al parsear contenido:', e);
          }
        }
      }
      return 'No hay pistas disponibles para este ejercicio.';
    };
    
    const toggleSubmitModal = () => {
      if (isHistoryMode.value) return;
      
      showSubmitModal.value = !showSubmitModal.value;
    };
    
    const toggleFullScreen = () => {
      console.log("Cambiando estado de pantalla completa:", !isFullScreen.value);
      isFullScreen.value = !isFullScreen.value;

      const handleEscapeKey = (e) => {
        if (e.key === 'Escape' && isFullScreen.value) {
          isFullScreen.value = false;
          document.removeEventListener('keydown', handleEscapeKey);
        }
      };

      if (isFullScreen.value) {
        document.addEventListener('keydown', handleEscapeKey);
        document.body.classList.add('overflow-hidden');
      } else {
        document.removeEventListener('keydown', handleEscapeKey);
        document.body.classList.remove('overflow-hidden');
      }

      nextTick(() => {
        if (editorRef.value && !isHistoryMode.value) {
          editorRef.value.focusEditor();
        }
      });
    };
    
    const resetCode = () => {
      if (isHistoryMode.value) return;
      
      if (!currentExercise.value || !editorRef.value) return;
      
      showConfirmation(
        '¿Está seguro que desea reiniciar el código? Perderá todos los cambios.',
        () => {
          const exerciseId = currentExercise.value.id;
          // Eliminar código con la clave correcta
          const codeKey = getExerciseCodeKey(exerciseId);
          localStorage.removeItem(codeKey);
          
          const template = extractTemplate(currentExercise.value);
          
          if (editorRef.value) {
            editorRef.value.setContent(template);
            
            if (editorRef.value.saveCurrentCode) {
              editorRef.value.saveCurrentCode();
            }
          }
          
          showNotification('Código reiniciado correctamente', 'success');
        },
        () => showNotification('Operación cancelada', 'info')
      );
    };
    
    const extractTemplate = (exercise) => {
      if (exercise.template && exercise.template.trim() !== '') {
        console.log('Usando plantilla definida directamente en el ejercicio');
        return exercise.template;
      } else if (exercise.contenido) {
        if (typeof exercise.contenido === 'object') {
          if (exercise.contenido.template && exercise.contenido.template.trim() !== '') {
            console.log('Usando plantilla definida en el objeto contenido');
            return exercise.contenido.template;
          }
        } else if (typeof exercise.contenido === 'string') {
          try {
            const parsed = JSON.parse(exercise.contenido);
            if (parsed.template && parsed.template.trim() !== '') {
              console.log('Usando plantilla definida en el JSON contenido');
              return parsed.template;
            }
          } catch (e) {
            console.warn('Error al parsear contenido:', e);
          }
        }
      }
    
      console.log('No se encontró plantilla definida, usando plantilla por defecto');
      return generateDefaultTemplate(exercise);
    };
    
    const getCompletedExercises = () => {
      try {
        const userId = getCurrentUserId();
        const evaluationId = evaluation.value?.id || 'unknown';
        const stored = localStorage.getItem(`completed_exercises_${userId}_${evaluationId}`);
        if (stored) {
          return JSON.parse(stored);
        }
      } catch (e) {
        console.warn('Error al leer ejercicios completados:', e);
      }

      return [];
    };

    const corregirFormatoEntradas = (ejemplos) => {
      if (!ejemplos || !Array.isArray(ejemplos)) return ejemplos;

      return ejemplos.map(ejemplo => {
        if (!ejemplo || typeof ejemplo !== 'object') return ejemplo;

        let nuevaEntrada = ejemplo.entrada;

        if (typeof nuevaEntrada === 'string') {
          const matchDobles = nuevaEntrada.match(/^"([^"]*)"$/);
          const matchSimples = nuevaEntrada.match(/^'([^']*)'$/);

          if (matchDobles) {
            nuevaEntrada = matchDobles[1];
            console.log(`Corrigiendo entrada con comillas dobles: "${ejemplo.entrada}" -> "${nuevaEntrada}"`);
          } else if (matchSimples) {
            nuevaEntrada = matchSimples[1];
            console.log(`Corrigiendo entrada con comillas simples: "${ejemplo.entrada}" -> "${nuevaEntrada}"`);
          }
        }

        return {
          ...ejemplo,
          entrada: nuevaEntrada
        };
      });
    };

    const prepararEjemplosPrueba = (ejercicio) => {
      if (!ejercicio) return { ejemplos: [] };

      let contenido = ejercicio.contenido;
      if (typeof contenido === 'string') {
        try {
          contenido = JSON.parse(contenido);
        } catch (e) {
          contenido = {};
        }
      }

      if (!contenido || typeof contenido !== 'object') {
        contenido = {};
      }

      let ejemplos = contenido.ejemplos || [];
      if (!Array.isArray(ejemplos)) {
        ejemplos = [];
      }

      ejemplos = ejemplos.map(ejemplo => {
        return {
          entrada: ejemplo.entrada || "",
          salida: ejemplo.salida || ""
        };
      });

      return { ...ejercicio, contenido: { ...contenido, ejemplos } };
    };

    const runTest = async () => {
      if (isHistoryMode.value) return;
      
      if (!editorRef.value || !currentExercise.value) {
        console.error("No se puede ejecutar la prueba: faltan referencias necesarias");
        return;
      }

      isTestExecuting.value = true;

      try {
        if (!editorRef.value.isInitialized()) {
          console.warn("El editor no está inicializado, esperando...");
          await new Promise(resolve => setTimeout(resolve, 500));
          if (!editorRef.value.isInitialized()) {
            isTestExecuting.value = false;
            if (leftPanelRef && leftPanelRef.value) {
              leftPanelRef.value.setTestResults("Error: El editor no está listo. Por favor, recargue la página.");
            }
            return;
          }
        }

        const code = editorRef.value.getContent();

        if (editorRef.value.saveCurrentCode && !isHistoryMode.value) {
          editorRef.value.saveCurrentCode();
        }

        let results = `Ejecutando prueba para: ${currentExercise.value.titulo || 'Ejercicio'}\n\n`;

        const availability = await judge0Service.checkAvailability();
        if (!availability.isAvailable) {
          results += `⚠️ ${availability.message}\n\n`;
          results += `No es posible ejecutar el código en este momento. El servicio Judge0 no está disponible.\n`;
          results += `Puedes seguir editando tu código y guardándolo. Intenta ejecutarlo más tarde.\n`;

          if (leftPanelRef && leftPanelRef.value) {
            leftPanelRef.value.setTestResults(results);
            leftPanelRef.value.activateOutputTab();
          }
          isTestExecuting.value = false;
          return;
        }

        const testCode = extractTestCode(currentExercise.value);
        let isSuccess = false;

        if (testCode) {
          console.log("Usando tests avanzados");
          try {
            const codigo_completo = code + "\n\n" + testCode;
            const testResult = await judge0Service.executeCode(codigo_completo);

            if (!testResult.success) {
              results += `Error al ejecutar las pruebas: ${testResult.error || 'Error desconocido'}\n`;
              if (testResult.stdout) {
                results += `\nSalida:\n${testResult.stdout}\n`;
              }
              if (testResult.stderr) {
                results += `\nError de ejecución (stderr):\n${testResult.stderr}\n`;
              }
              if (testResult.compile_output) {
                results += `\nError de compilación:\n${testResult.compile_output}\n`;
              }
            } else {
              results += testResult.stdout || "No se generó salida visible";

              if (testResult.stderr) {
                results += `\n\nError de ejecución (stderr):\n${testResult.stderr}\n`;
              }

              const regex = /Resultado:\s*(\d+)\/(\d+)\s*pruebas\s*pasadas/;
              const match = testResult.stdout.match(regex);

              if (match) {
                const passingTests = parseInt(match[1]);
                const totalTests = parseInt(match[2]);

                results += `\n\nResumen: ${passingTests} de ${totalTests} pruebas pasadas.\n`;

                if (passingTests === totalTests) {
                  results += `\n🎯 ¡Excelente! Has pasado todas las pruebas.`;
                  isSuccess = true;
                } else {
                  const failedTests = totalTests - passingTests;
                  results += `\n⚠️ No pasaste todas las pruebas (${failedTests} fallidas).\n\n`;
                  results += `Sugerencias para corregir tu solución:\n`;
                  results += `• Revisa cuidadosamente los casos que fallan\n`;
                  results += `• Comprueba si tu código maneja correctamente todos los escenarios\n`;
                  results += `• Verifica que los tipos de datos de entrada y salida sean correctos\n`;
                  results += `• Asegúrate de que tu función devuelva exactamente lo que se pide\n`;
                }
              } else {
                const correctCount = (testResult.stdout.match(/✓ CORRECTO/g) || []).length;
                const incorrectCount = (testResult.stdout.match(/✗ INCORRECTO/g) || []).length +
                  (testResult.stdout.match(/✗ ERROR/g) || []).length;
                const totalCount = correctCount + incorrectCount || 1;

                results += `\n\nResumen: ${correctCount} de ${totalCount} pruebas pasadas.\n`;

                if (correctCount === totalCount && incorrectCount === 0) {
                  results += `\n🎯 ¡Excelente! Has pasado todas las pruebas.`;
                  isSuccess = true;
                } else {
                  results += `\n⚠️ No pasaste todas las pruebas.\n`;
                }
              }
            }
          } catch (testError) {
            console.error('Error ejecutando tests avanzados:', testError);
            results += `Error al ejecutar tests avanzados: ${testError.message || 'Error desconocido'}\n`;
          }
        }
        else if (currentExercise.value.ejemplos && currentExercise.value.ejemplos.length > 0) {
          console.log("Usando ejemplos para prueba");
          try {
            const ejemplos = corregirFormatoEntradas(currentExercise.value.ejemplos);

            const verification = await judge0Service.verificarEjemplos(code, ejemplos);

            if (verification.success) {
              results += `### Resultados de la ejecución: ###\n\n`;

              for (const resultado of verification.resultados) {
                results += `--- Caso ${resultado.ejemplo} ---\n`;
                results += `Entrada: ${resultado.entrada}\n`;
                results += `Salida esperada: ${resultado.salidaEsperada}\n`;
                results += `Tu salida: ${resultado.salidaReal}\n`;

                if (resultado.esCorrecto) {
                  results += `✅ ¡Correcto!\n`;
                } else {
                  results += `❌ Incorrecto\n`;

                  if (resultado.salidaEsperada && resultado.salidaReal) {
                    const esperadoTrim = resultado.salidaEsperada.trim();
                    const realTrim = resultado.salidaReal.trim();

                    if (esperadoTrim === realTrim) {
                      results += `  ⚠️ Las salidas parecen iguales pero pueden tener espacios o saltos de línea extras\n`;
                    } else if (esperadoTrim.includes(realTrim)) {
                      results += `  ⚠️ Tu salida está incompleta: falta contenido adicional\n`;
                    } else if (realTrim.includes(esperadoTrim)) {
                      results += `  ⚠️ Tu salida contiene texto adicional que no debería estar\n`;
                    } else if (esperadoTrim.toLowerCase() === realTrim.toLowerCase()) {
                      results += `  ⚠️ Verifica mayúsculas y minúsculas en tu respuesta\n`;
                    }
                  }
                }

                if (resultado.error) {
                  results += `Error: ${resultado.error}\n`;
                }
                if (resultado.stderr) {
                  results += `\nError de ejecución (stderr):\n${resultado.stderr}\n`;
                }

                results += `Tiempo: ${resultado.tiempo || '0'}s\n\n`;
              }

              results += `\n### Resumen ###\n`;
              results += `Total de casos: ${verification.totalEjemplos}\n`;
              results += `Casos correctos: ${verification.casosCorrectos}\n`;
              results += `Porcentaje de éxito: ${verification.porcentajeExito.toFixed(2)}%\n`;

              if (verification.casosCorrectos === verification.totalEjemplos) {
                isSuccess = true;
                results += `\n🎯 ¡Excelente! Has pasado todos los ejemplos (${verification.casosCorrectos}/${verification.totalEjemplos}).`;
              } else {
                results += `\n⚠️ Tu solución tiene errores. Revisa los siguientes aspectos:\n`;
                results += `• Comprueba que estás entendiendo correctamente el problema\n`;
                results += `• Verifica el formato exacto de la salida (espacios, saltos de línea, etc.)\n`;
                results += `• Examina tu lógica para los casos que fallan\n\n`;
                results += `🔄 Corrige tu código y vuelve a intentarlo`;
              }
            } else {
              results += `Error en la verificación: ${verification.message || 'Error desconocido'}\n`;
            }
          } catch (verificationError) {
            console.error('Error verificando ejemplos:', verificationError);
            results += `Error al verificar ejemplos: ${verificationError.message || 'Error desconocido'}\n`;
          }
        }
        else {
          console.log("Ejecutando código sin pruebas específicas");
          try {
            const resultado = await judge0Service.executeCode(code);

            if (resultado.success) {
              results += `✅ Ejecución exitosa\n\n`;
              results += `Salida:\n${resultado.stdout || 'No se generó salida visible'}`;

              if (resultado.stderr) {
                results += `\n\nMensajes de error (stderr):\n${resultado.stderr}`;
              }

              results += `\nTiempo: ${resultado.time}s`;

              isSuccess = true;
            } else {
              results += `❌ Error en la ejecución\n\n`;
              if (resultado.stderr) {
                results += `Error de ejecución (stderr):\n${resultado.stderr}\n`;
              } else if (resultado.compile_output) {
                results += `Error de compilación:\n${resultado.compile_output}\n`;
              } else {
                results += `Error desconocido`;
              }
            }
          } catch (executeError) {
            console.error('Error ejecutando código:', executeError);
            results += `Error al ejecutar código: ${executeError.message || 'Error desconocido'}\n`;
          }
        }

        if (currentExercise.value) {
          localStorage.setItem(`exercise_results_${currentExercise.value.id}`, results);
        }

        if (isSuccess && currentExercise.value && !isHistoryMode.value) {
          markExerciseCompleted(currentExercise.value.id);
          updateExerciseStatus(true);

          saveExerciseScore(
            currentExercise.value.id,
            currentExercise.value.puntaje || 10,
            currentExercise.value.puntaje || 10
          );

          results += `\n\n🎉 ¡Ejercicio completado correctamente! Puedes continuar con el siguiente.`;
        }

        if (leftPanelRef && leftPanelRef.value) {
          leftPanelRef.value.setTestResults(results);
          leftPanelRef.value.activateOutputTab();
        } else {
          console.error("No se pudo acceder al panel izquierdo");
          showNotification('Error: No se pueden mostrar los resultados', 'error');
        }
      } catch (error) {
        console.error('Error al ejecutar prueba:', error);

        if (leftPanelRef && leftPanelRef.value) {
          leftPanelRef.value.setTestResults(`Error al ejecutar la prueba: ${error.message}`);
          leftPanelRef.value.activateOutputTab();
        } else {
          showNotification(`Error al ejecutar la prueba: ${error.message}`, 'error');
        }
      } finally {
        isTestExecuting.value = false;
      }
    };

    const updateExerciseStatus = (isCompleted) => {
      console.log(`Actualizando estado del ejercicio: ${isCompleted ? 'completado' : 'pendiente'}`);

      if (currentExercise.value && currentExercise.value.id) {
        const userId = getCurrentUserId();
        const exerciseId = currentExercise.value.id;
        const evaluationId = evaluation.value?.id || 'unknown';
        const statusKey = getExerciseStatusKey(exerciseId);

        if (isCompleted) {
          localStorage.setItem(statusKey, 'completed');

          try {
            let completedExercises = [];
            const completedKey = `completed_exercises_${userId}_${evaluationId}`;
            const stored = localStorage.getItem(completedKey);
            if (stored) {
              completedExercises = JSON.parse(stored);
            }

            if (!completedExercises.includes(exerciseId)) {
              completedExercises.push(exerciseId);
              localStorage.setItem(completedKey, JSON.stringify(completedExercises));
              console.log(`Ejercicio ${exerciseId} agregado a completados del usuario ${userId} en evaluación ${evaluationId}`);
            }
          } catch (e) {
            console.warn('Error al actualizar ejercicios completados:', e);
          }
        } else {
          localStorage.removeItem(statusKey);

          try {
            let completedExercises = [];
            const completedKey = `completed_exercises_${userId}_${evaluationId}`;
            const stored = localStorage.getItem(completedKey);
            if (stored) {
              completedExercises = JSON.parse(stored);

              const index = completedExercises.indexOf(exerciseId);
              if (index > -1) {
                completedExercises.splice(index, 1);
                localStorage.setItem(completedKey, JSON.stringify(completedExercises));
                console.log(`Ejercicio ${exerciseId} eliminado de completados del usuario ${userId} en evaluación ${evaluationId}`);
              }
            }
          } catch (e) {
            console.warn('Error al actualizar ejercicios completados:', e);
          }
        }

        window.dispatchEvent(new CustomEvent('exercise-status-changed', {
          detail: {
            exerciseId: exerciseId,
            userId: userId,
            isCompleted: isCompleted
          }
        }));
      }
    }
    
    const extractTestCode = (exercise) => {
      let testCode = null;

      if (exercise.tests_avanzados) {
        testCode = exercise.tests_avanzados;
      } else if (exercise.contenido) {
        if (typeof exercise.contenido === 'object') {
          testCode = exercise.contenido.tests_avanzados;
        } else if (typeof exercise.contenido === 'string') {
          try {
            const parsed = JSON.parse(exercise.contenido);
            testCode = parsed.tests_avanzados;
          } catch (e) {
            console.warn('Error al parsear contenido para tests:', e);
          }
        }
      }

      if (testCode) {
        if (!testCode.includes('def ejecutar_tests_avanzados') &&
          !testCode.includes('function ejecutar_tests_avanzados')) {

          const auxiliarFunction = `
# Función auxiliar para ejecutar pruebas avanzadas (añadida automáticamente)
def ejecutar_tests_avanzados(func, casos_prueba, mostrar_detalle=True):
    """
    Ejecuta una serie de pruebas para una función.
    
    Args:
        func: La función a probar
        casos_prueba: Lista de tuplas (entrada, salida_esperada)
        mostrar_detalle: Si es True, muestra el detalle de cada caso
    
    Returns:
        int: Número de pruebas pasadas
    """
    pruebas_pasadas = 0
    total_pruebas = len(casos_prueba)
    
    print(f"Ejecutando {total_pruebas} pruebas:")
    
    for i, (entrada, esperado) in enumerate(casos_prueba, 1):
        try:
            # Si la entrada es una tupla, desempaquetar para llamar a la función
            if isinstance(entrada, tuple):
                resultado = func(*entrada)
            else:
                resultado = func(entrada)
                
            if resultado == esperado:
                pruebas_pasadas += 1
                if mostrar_detalle:
                    print(f"✓ CORRECTO - Prueba {i}: con entrada {entrada} se obtuvo {resultado}")
            else:
                if mostrar_detalle:
                    print(f"✗ INCORRECTO - Prueba {i}: con entrada {entrada}")
                    print(f"  Se esperaba: {esperado}")
                    print(f"  Se obtuvo: {resultado}")
        except Exception as e:
            if mostrar_detalle:
                print(f"✗ ERROR - Prueba {i}: con entrada {entrada}")
                print(f"  Error: {str(e)}")
    
    print(f"Resultado: {pruebas_pasadas}/{total_pruebas} pruebas pasadas")
    return pruebas_pasadas
      `;

          testCode = auxiliarFunction + "\n\n" + testCode;
        }
      }

      return testCode;
    };
    
    const submitCode = async () => {
      if (isHistoryMode.value) return;
      
      if (!editorRef.value || !currentExercise.value) return;

      try {
        const availability = await judge0Service.checkAvailability();
        if (!availability.isAvailable) {
          if (leftPanelRef && leftPanelRef.value) {
            leftPanelRef.value.setTestResults(`⚠️ ${availability.message}\n\nNo es posible enviar el código en este momento. El servicio Judge0 no está disponible.`);
            leftPanelRef.value.activateOutputTab();
          } else {
            showNotification("El servicio Judge0 no está disponible en este momento. Intente más tarde.", 'warning');
          }
          return;
        }
      } catch (error) {
        console.error("Error al verificar disponibilidad de Judge0:", error);
      }

      toggleSubmitModal();
    };


    const confirmSubmit = async () => {
      if (isHistoryMode.value) return;

      if (!editorRef.value || !currentExercise.value) return;

      toggleSubmitModal();
      isSubmitExecuting.value = true;

      try {
        if (editorRef.value.saveCurrentCode) {
          editorRef.value.saveCurrentCode();
          console.log("Código actual guardado");
        }

        if (leftPanelRef && leftPanelRef.value) {
          leftPanelRef.value.setTestResults("Procesando evaluación con Judge0. Por favor espere...");
          leftPanelRef.value.activateOutputTab();
        }

        console.log("🔍 Preparando envío de TODOS los ejercicios de la evaluación");
        console.log(`Total de ejercicios en exercises.value: ${exercises.value?.length || 0}`);

        const ejerciciosParaEnviar = [];

        for (const ejercicio of exercises.value) {
          if (!ejercicio || !ejercicio.id) {
            console.warn(`Ejercicio sin ID detectado:`, ejercicio);
            continue;
          }

          // Usar la clave correcta para obtener el código
          const codeKey = getExerciseCodeKey(ejercicio.id);
          const codigo = localStorage.getItem(codeKey) || "";

          console.log(`Ejercicio ID: ${ejercicio.id}, Título: ${ejercicio.titulo || 'Sin título'}`);
          console.log(`- Código encontrado: ${codigo ? 'Sí' : 'No'} (${codigo?.length || 0} caracteres)`);

          const codigoFinal = codigo || generateDefaultTemplate(ejercicio);

          ejerciciosParaEnviar.push({
            ejercicio_id: ejercicio.id,
            codigo: codigoFinal
          });

          console.log(`✅ Ejercicio ID ${ejercicio.id} añadido para envío (${codigoFinal.length} caracteres)`);
        }

        if (ejerciciosParaEnviar.length === 0) {
          throw new Error("No hay ejercicios para enviar. Algo está mal con la carga de ejercicios.");
        }

        console.log(`🧮 Total de ejercicios preparados para envío: ${ejerciciosParaEnviar.length}`);

        const evaluationData = localStorage.getItem('currentEvaluation')
          ? JSON.parse(localStorage.getItem('currentEvaluation'))
          : null;

        if (!evaluationData || !evaluationData.id) {
          throw new Error("No se pudo determinar el ID de la evaluación actual");
        }

        const evaluationId = evaluationData.id;
        console.log(`📝 Evaluación ID: ${evaluationId}, Título: ${evaluationData.titulo || evaluationData.title || 'Sin título'}`);

        console.log("🔄 Verificando disponibilidad de Judge0...");
        try {
          const judge0Status = await evaluationsService.checkJudge0Status();

          if (!judge0Status.isAvailable) {
            console.error("❌ Judge0 no disponible:", judge0Status.message);
            throw new Error(`El servicio Judge0 no está disponible: ${judge0Status.message}`);
          }
          console.log("✅ Judge0 disponible, procediendo con envío");
        } catch (judge0Error) {
          console.error("Error verificando Judge0:", judge0Error);
          throw new Error("No se pudo verificar la disponibilidad de Judge0");
        }

        console.log(`🚀 Enviando batch de ${ejerciciosParaEnviar.length} ejercicios para evaluación ${evaluationId}`);

        const response = await evaluationsService.submitBatch({
          evaluacion_id: evaluationId,
          ejercicios: ejerciciosParaEnviar,
          useJudge0: true
        }, exercises.value);


        console.log("✅ Respuesta del procesamiento batch recibida:", response.data);

        if (response.data && response.data.success) {
          const userId = getCurrentUserId();

          console.log("🔍 Guardando puntuaciones para usuario", userId);
          console.log("Total score:", response.data.total_puntaje);
          console.log("Max score:", response.data.puntaje_maximo);
          console.log("Scaled score:", response.data.puntaje_sobre_10);

          localStorage.setItem(`evaluation_total_score_${userId}`, response.data.total_puntaje);
          localStorage.setItem(`evaluation_max_score_${userId}`, response.data.puntaje_maximo);
          localStorage.setItem(`evaluation_scaled_score_${userId}`, response.data.puntaje_sobre_10);
          localStorage.setItem(`evaluation_raw_results_${userId}`, JSON.stringify(response.data));
          localStorage.setItem(`evaluationEndTime_${userId}`, Date.now().toString());

          if (leftPanelRef && leftPanelRef.value) {
            const resultSummary = createResultSummary(response.data);
            leftPanelRef.value.setTestResults(resultSummary);
          }

          if (response.data.resultados && Array.isArray(response.data.resultados)) {
            response.data.resultados.forEach(resultado => {
              if (resultado.ejercicio_id) {
                saveExerciseScore(
                  resultado.ejercicio_id,
                  resultado.puntaje_obtenido || 0,
                  resultado.puntaje_maximo || 0
                );
                console.log(`Procesando resultado de ejercicio ${resultado.ejercicio_id}:`, resultado);

                if (resultado.success && resultado.es_correcto) {
                  console.log(`✅ Marcando ejercicio ${resultado.ejercicio_id} como completado`);
                  markExerciseCompleted(resultado.ejercicio_id);
                }
              }
            });
          }

          // Finalizar la evaluación en el backend
          try {
            console.log("🏁 Finalizando evaluación en el backend...");
            await evaluationsService.finishEvaluation(evaluationId);
            console.log("✅ Evaluación finalizada correctamente");
          } catch (finishError) {
            console.error("Error al finalizar evaluación:", finishError);
          }

          // Redirigir inmediatamente después de un breve delay
          setTimeout(() => {
            console.log("📤 Redirigiendo a evaluación completada...");
            router.push('/evaluacion-completada');
          }, 800);

        } else {
          let errorMessage = response.data?.message || "Ocurrió un error al procesar la evaluación";

          if (response.data?.judge0Error) {
            errorMessage = `Error en Judge0: ${response.data.judge0Error}. Por favor, intente nuevamente.`;
          }

          if (leftPanelRef && leftPanelRef.value) {
            leftPanelRef.value.setTestResults(`Error: ${errorMessage}`);
          }
        }
      } catch (error) {
        console.error('Error al procesar evaluación con Judge0:', error);

        let errorMessage = error.message || "Ocurrió un error al procesar la evaluación";

        if (errorMessage.includes("Judge0")) {
          errorMessage = `El servicio de evaluación (Judge0) no está disponible en este momento. 
Por favor, guarde su código e intente nuevamente más tarde.`;
        }

        if (leftPanelRef && leftPanelRef.value) {
          leftPanelRef.value.setTestResults(`Error: ${errorMessage}`);
        }
      } finally {
        isSubmitExecuting.value = false;
      }
    };

    const generateDefaultTemplate = (exercise) => {
      let template = '# ' + (exercise.titulo || 'Ejercicio') + '\n\n';

      if (exercise.tipo === 'practico') {
        template += 'def solucion():\n';
        template += '    # Tu código aquí\n';
        template += '    return\n\n';
        template += '# No modifiques esta parte\n';
        template += 'if __name__ == "__main__":\n';
        template += '    print(solucion())\n';
      } else {
        template += '# Tu código aquí\n';
      }

      return template;
    };

    const createResultSummary = (data) => {
      let summary = `# Resumen de Evaluación\n\n`;

      summary += `## Puntuación Final: ${data.puntaje_sobre_10}/10\n`;
      summary += `Puntos obtenidos: ${data.total_puntaje} de ${data.puntaje_maximo}\n\n`;

      summary += `## Resultados por Ejercicio\n\n`;

      data.resultados.forEach((resultado, index) => {
        const ejercicio = exercises.value.find(e => e.id === resultado.ejercicio_id);
        const titulo = ejercicio ? ejercicio.titulo : `Ejercicio ${index + 1}`;

        summary += `### ${titulo}\n`;
        if (resultado.success) {
          if (resultado.es_correcto) {
            summary += `✅ Completado correctamente\n`;
          } else {
            summary += `❌ Incorrecto\n`;
          }

          if (resultado.casos_correctos !== undefined) {
            summary += `${resultado.casos_correctos} de ${resultado.total_casos} casos correctos\n`;
          }

          summary += `Puntuación: ${resultado.puntaje_obtenido} de ${resultado.puntaje_maximo} puntos\n`;
        } else {
          summary += `❌ ${resultado.message || "Error en la ejecución"}\n`;
        }

        summary += `\n`;
      });

      return summary;
    };
    
    const saveExerciseScore = (exerciseId, score, maxScore) => {
      if (isHistoryMode.value) return false;
      
      try {
        const scoresKey = getScoresKey();
        let scores = {};

        const savedScores = localStorage.getItem(scoresKey);
        if (savedScores) {
          scores = JSON.parse(savedScores);
        }

        scores[exerciseId] = {
          score: score,
          maxScore: maxScore,
          timestamp: new Date().toISOString()
        };

        localStorage.setItem(scoresKey, JSON.stringify(scores));

        console.log(`Guardada puntuación para usuario ${getCurrentUserId()}, ejercicio ${exerciseId}: ${score}/${maxScore}`);
        return true;
      } catch (error) {
        console.error('Error al guardar puntuación:', error);
        return false;
      }
    };

    const verifyDataPersistence = () => {
      const userId = getCurrentUserId();
      const totalScore = localStorage.getItem(`evaluation_total_score_${userId}`);
      const scaledScore = localStorage.getItem(`evaluation_scaled_score_${userId}`);

      console.log("⚠️ Verificación de persistencia:");
      console.log("Usuario:", userId);
      console.log("Total score persistido:", totalScore);
      console.log("Scaled score persistido:", scaledScore);

      if (!totalScore) {
        console.log("🔍 Buscando bajo otras claves posibles...");
        for (let i = 0; i < localStorage.length; i++) {
          const key = localStorage.key(i);
          if (key.includes("evaluation_")) {
            console.log(`Clave encontrada: ${key} = ${localStorage.getItem(key)}`);
          }
        }
      }
    };

    const finishEvaluation = async () => {
      if (isHistoryMode.value) return;
      
      try {
        verifyDataPersistence();

        const userId = getCurrentUserId();
        localStorage.setItem(`evaluationEndTime_${userId}`, Date.now().toString());

        const evaluationId = localStorage.getItem('currentEvaluation') ?
          JSON.parse(localStorage.getItem('currentEvaluation')).id : null;

        if (evaluationId) {
          await evaluationsService.finishEvaluation(evaluationId);
        }

        router.push('/evaluacion-completada');
      } catch (error) {
        console.error('Error al finalizar evaluación:', error);
        showNotification('Hubo un error al finalizar la evaluación, pero tus resultados han sido guardados.', 'warning');
        router.push('/evaluacion-completada');
      }
    };

    const checkHistoryMode = () => {
      console.log("Verificando modo historial...", isHistoryMode.value);
      
      if (isHistoryMode.value) {
        console.log("En modo historial. Deshabilitando botones de interacción.");
      }
    };

    const startEvaluation = async (evaluation) => {
      try {
        const response = await evaluationsService.getDetallesEvaluacion(evaluation.id);
        
        localStorage.setItem('currentEvaluation', JSON.stringify(response.data));
        
        const userId = getCurrentUserId();
        localStorage.setItem(`evaluationStartTime_${userId}`, Date.now().toString());
        
        console.log('✅ Evaluación iniciada con datos completos:', response.data);
        
        return response.data;
      } catch (error) {
        console.error('Error al iniciar evaluación:', error);
        showNotification('Error al cargar los detalles de la evaluación', 'error');
        throw error;
      }
    };
    
    onMounted(async () => {
      const userId = getCurrentUserId();
      const evaluationId = evaluation.value?.id;

      console.log("PracticalRightPanel montado con usuario:", userId);
      console.log("Evaluación ID:", evaluationId);
      console.log("Estado modo historia:", isHistoryMode.value);

      // Limpiar estados previos para esta evaluación
      if (evaluationId && exercises.value && exercises.value.length > 0) {
        console.log(`Limpiando estados previos para evaluación ${evaluationId}`);

        exercises.value.forEach(ex => {
          if (ex.id) {
            // Claves antiguas sin evaluationId
            const oldStatusKey = `exercise_status_${userId}_${ex.id}`;
            localStorage.removeItem(oldStatusKey);
            
            // Nueva clave con evaluationId
            const statusKey = getExerciseStatusKey(ex.id);
            localStorage.removeItem(statusKey);
          }
        });
      }

      // Guardar tiempo de inicio para esta evaluación
      if (evaluationId) {
        localStorage.setItem(`evaluationStartTime_${userId}_${evaluationId}`, Date.now().toString());
      }

      // Cargar evaluación actual si existe
      const currentEvaluation = localStorage.getItem('currentEvaluation');
      if (currentEvaluation) {
        try {
          await startEvaluation(JSON.parse(currentEvaluation));
        } catch (error) {
          console.error('Error al reiniciar evaluación:', error);
        }
      }

      // Verificar estado inicial de modo historia
      checkHistoryMode();

      // Manejar eventos de teclado
      const handleKeyDown = (e) => {
        if (e.key === 'ArrowLeft' || e.key === 'ArrowRight') {
          e.preventDefault();
          console.log(`Navegación con flecha ${e.key} bloqueada`);
        }

        if (e.key === 'Enter' && e.ctrlKey && !isHistoryMode.value && !isExerciseComplete.value && !isTestExecuting.value) {
          e.preventDefault();
          console.log('Atajo Ctrl+Enter detectado - ejecutando test');
          runTest();
        }
      };

      document.addEventListener('keydown', handleKeyDown);
      window.keyboardHandlerRef = handleKeyDown;

      window.addEventListener('exercise-completed', (event) => {
        if (currentExercise.value && event.detail.exerciseId === currentExercise.value.id) {
          isExerciseComplete.value = true;
        }
      });
    });
    
    onBeforeUnmount(() => {
      if (!isHistoryMode.value && editorRef.value && editorRef.value.saveCurrentCode && currentExercise.value) {
        editorRef.value.saveCurrentCode();
      }

      if (isFullScreen.value) {
        document.body.classList.remove('overflow-hidden');
      }

      window.removeEventListener('exercise-completed', () => { });

      if (window.keyboardHandlerRef) {
        document.removeEventListener('keydown', window.keyboardHandlerRef);
        delete window.keyboardHandlerRef;
      }
    });

    watch(isHistoryMode, (newValue) => {
      console.log("Cambio en modo Historia detectado:", newValue);
      checkHistoryMode();
    });


    defineExpose({
      updateExerciseStatus,
      submitCode,
      runTest,
      startEvaluation,
      resetEvaluationStates,
      cleanOldStates,
      confirmSubmit,
      editorRef
    });
    
    
    return {
      editorRef,
      hintContent,
      isFullScreen,
      toggleFullScreen,
      resetCode,
      runTest,
      submitCode,
      confirmSubmit,
      isTestExecuting,
      isSubmitExecuting,
      showHintModal,
      showSubmitModal,
      toggleHintModal,
      toggleSubmitModal,
      currentExercise,
      getCurrentUserId,
      startEvaluation,
      getExerciseCodeKey,
      getExerciseStatusKey,
      currentExerciseIndex,
      exercises,
      currentExerciseNumber,
      isExerciseComplete,
      pendingExercisesCount,
      completedExercisesCount,
      selectedTheme,
      changeTheme,
      isHistoryMode,
    };
  }
};
</script>

<style>
/* Estilos globales para anular Bulma */
.right-panel-wrapper button {
  margin: 0;
  cursor: pointer;
  transition: all var(--transition-fast, 0.2s);
}

.right-panel-wrapper .button {
  height: auto;
  padding: 0;
  line-height: normal;
  background-color: transparent;
  border: none;
  color: inherit;
}

.right-panel-wrapper h3 {
  margin: 0;
  padding: 0;
  font-weight: 600;
}

/* Clase para cuando está en pantalla completa */
body.overflow-hidden {
  overflow: hidden;
}
</style>

<style scoped>
.right-panel-wrapper {
  height: 100%;
  display: flex;
  flex-direction: column;
  background-color: var(--color-bg-main, #1C1C21);
  width: 50%;
  flex: 0 0 50%;
  max-width: 50%;
}

/* Estilos para pantalla completa */
.right-panel-wrapper.is-full-screen {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  z-index: 9999;
  background-color: var(--color-bg-main, #1C1C21);
  width: 100%;
  flex: none;
  max-width: 100%;
}

/* Nuevos estilos para el modo historial */
.right-panel-wrapper.history-mode {
  border-top: 4px solid #4C4CFF; /* Borde azul destacado para indicar modo historial */
  position: relative;
}

.right-panel-wrapper.history-mode::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  pointer-events: none; /* Permite que los clicks pasen a través */
  background: linear-gradient(to bottom, rgba(76, 76, 255, 0.05), transparent 10%);
  z-index: 1;
}

.practical-right-panel {
  display: flex;
  flex-direction: column;
  height: 100%;
  position: relative;
}

/* Encabezado del panel */
.panel-header {
  background-color: var(--color-bg-element, #2A2A30);
  padding: 10px 16px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  height: 50px;
  border-bottom: 1px solid var(--color-border, #36363C);
  z-index: 1000;
  position: relative;
}

.header-title {
  display: flex;
  align-items: center;
  gap: 8px;
}

.header-icon {
  font-size: 18px;
  color: var(--color-primary, #EBB300);
}

.header-title h3 {
  font-size: 16px;
  color: var(--color-text-primary, #FFFFFF);
}

/* Botón de expandir en header */
.expand-button {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 34px;
  height: 34px;
  border-radius: 8px;
  background-color: #32323A;
  color: var(--color-text-secondary, #E0E0E0);
  transition: all 0.3s ease;
  z-index: 10000;
}

.expand-button:hover {
  background-color: #3A3A45;
  transform: scale(1.05);
  color: var(--color-text-primary, #FFFFFF);
}

/* Botón flotante para pantalla completa */
.expand-button-fixed {
  position: fixed;
  top: 15px;
  right: 15px;
  width: 34px;
  height: 34px;
  border-radius: 8px;
  background-color: #32323A;
  color: var(--color-text-secondary, #E0E0E0);
  border: none;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  transition: all 0.3s ease;
  z-index: 10000;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.3);
}

.expand-button-fixed:hover {
  background-color: #45455A;
  transform: scale(1.05);
}

/* Contenedor del editor */
.editor-container {
  flex: 1;
  overflow: hidden;
  margin: 10px;
  border-radius: var(--border-radius, 8px);
  background-color: var(--color-bg-element, #2A2A30);
  box-shadow: var(--shadow-sm, 0 2px 6px rgba(0, 0, 0, 0.1));
}

/* Estilos para el editor en pantalla completa */
.is-full-screen .editor-container {
  margin: 0;
  border-radius: 0;
  height: calc(100% - 50px);
}

/* Footer del panel */
.panel-footer {
  background-color: var(--color-bg-element, #2A2A30);
  padding: 8px 16px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  height: 64px;
  border-top: 1px solid var(--color-border, #36363C);
}

.panel-footer.is-hidden {
  display: none;
}

/* Botones auxiliares */
.helper-buttons {
  display: flex;
  gap: 8px;
}

.helper-button {
  background-color: #32323A;
  border-radius: 8px;
  padding: 8px 12px;
  display: flex;
  align-items: center;
  gap: 6px;
  color: var(--color-text-secondary, #E0E0E0);
  font-size: 14px;
  font-weight: 500;
  border: 1px solid #3A3A48;
  transition: all 0.3s ease;
}

.helper-button:hover:not(:disabled) {
  background-color: #3A3A48;
  /* transform: translateY(-2px); */
  color: var(--color-text-primary, #FFFFFF);
  box-shadow: var(--shadow-sm, 0 2px 6px rgba(0, 0, 0, 0.1));
  border-color: #6795DE;
}

/* Estilo para botones deshabilitados - Modo Historia */
.helper-button:disabled, .action-button:disabled {
  opacity: 0.6 !important;
  cursor: not-allowed !important;
  background-color: #2A2A30 !important;
  transform: none !important;
  box-shadow: none !important;
  border-color: #2A2A30 !important;
  color: #757580 !important;
}

.helper-icon {
  font-size: 16px;
}

/* Botones de acción con tamaño uniforme */
.action-buttons {
  display: flex;
  gap: 12px;
}

.action-button {
  padding: 8px 12px;
  border-radius: 8px;
  font-weight: 600;
  font-size: 14px;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  width: auto;
  min-width: 100px;
  height: 38px;
  border: 1px solid transparent;
}

.action-button:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.button-icon {
  font-size: 16px;
}

/* Botón de TEST con nuevo color */
.test-button {
  background-color: #121216;
    color: #FFFFFF;
    border-color: #00B294;
}

.test-button:hover:not(:disabled) {
  background-color: #34495E; /* Azul oscuro más claro al pasar el mouse */
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.2);
}

/* Estilo especial para test completo */
.test-button:disabled:not(.is-loading) {
  background-color: #27AE60; /* Verde para indicar éxito */
  color: white;
  border-color: #27AE60;
}

/* Botón de ENVIAR en verde */
.submit-button {
  background-color: #1262553d;
  color: white;
  border-color: #30a755;
}

.submit-button:hover:not(:disabled) {
  background-color: #2D7D46; /* Verde oscuro más claro al pasar el mouse */
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.2);
}

/* Modales */
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-color: rgba(0, 0, 0, 0.7);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
  animation: fadeIn 0.2s ease-out;
}

.modal-card {
  background-color: var(--color-bg-element, #2A2A30);
  border-radius: var(--border-radius, 8px);
  width: 90%;
  max-width: 450px;
  box-shadow: var(--shadow-lg, 0 8px 16px rgba(0, 0, 0, 0.2));
  animation: slideIn 0.3s ease-out;
}

.modal-header {
  background-color: var(--color-primary, #EBB300);
  color: #1C1C21;
  padding: 16px 20px;
  border-top-left-radius: var(--border-radius, 8px);
  border-top-right-radius: var(--border-radius, 8px);
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.modal-header h3 {
  font-size: 18px;
  display: flex;
  align-items: center;
  gap: 8px;
}

.modal-icon {
  font-size: 20px;
}

.modal-close {
  font-size: 24px;
  background: none;
  border: none;
  color: #1C1C21;
  cursor: pointer;
  width: 30px;
  height: 30px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 50%;
  transition: all 0.2s ease;
}

.modal-close:hover {
  background-color: rgba(0, 0, 0, 0.1);
}

.modal-body {
  padding: 20px;
  color: var(--color-text-primary, #FFFFFF);
}

.modal-body p {
  line-height: 1.6;
  margin-bottom: 16px;
}

.modal-body .warning-message {
  background-color: rgba(255, 189, 46, 0.1);
  border-left: 4px solid var(--color-warning, #FFBD2E);
  padding: 12px 16px;
  border-radius: 4px;
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 16px;
}

.modal-body .success-message {
  background-color: rgba(46, 139, 87, 0.1);
  border-left: 4px solid var(--color-success, #2E8B57);
  padding: 12px 16px;
  border-radius: 4px;
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 16px;
}

.warning-icon, .success-icon {
  font-size: 20px;
}

.modal-footer {
  padding: 16px 20px;
  display: flex;
  justify-content: center;
  gap: 16px;
  border-top: 1px solid var(--color-border, #36363C);
}

.modal-button {
  padding: 10px 20px;
  border-radius: 8px;
  font-weight: 600;
  font-size: 14px;
  min-width: 120px;
  transition: all 0.3s ease;
}

.modal-button:hover {
  transform: translateY(-2px);
}

.cancel-button {
  background-color: #32323A;
  color: var(--color-text-primary, #FFFFFF);
  border: 1px solid #3A3A48;
}

.cancel-button:hover {
  background-color: #3A3A48;
}

.confirm-button {
  background-color: var(--color-primary, #EBB300);
  color: #1C1C21;
  border: none;
}

.confirm-button:hover {
  background-color: var(--color-primary-light, #FFD03F);
  box-shadow: 0 4px 12px rgba(235, 179, 0, 0.3);
}

/* Animaciones */
@keyframes fadeIn {
  from { opacity: 0; }
  to { opacity: 1; }
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

/* Media queries */
@media (max-width: 768px) {
  .action-button {
    min-width: 80px;
    padding: 8px;
  }
  
  .action-button span:not(.button-icon) {
    display: none;
  }
  
  .button-icon {
    font-size: 18px;
    margin: 0;
  }

  
  .helper-text, .action-text {
    display: none;
  }
  
  .helper-button, .action-button {
    padding: 8px;
    width: 36px;
    height: 36px;
    justify-content: center;
  }
  
  .modal-card {
    width: 95%;
  }
}

@media (min-width: 769px) {
  .right-panel-wrapper {
    width: 50%;
    flex: 0 0 50%;
    max-width: 50%;
  }
}

/* Animaciones para los botones */
.button-icon.rotating {
  display: inline-block;
  animation: rotate 1.2s linear infinite;
}

@keyframes rotate {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
}

/* Animación de puntos cargando */
.loading-dots {
  display: inline-flex;
  align-items: center;
  gap: 4px;
  height: 20px;
}

.loading-dots .dot {
  width: 6px;
  height: 6px;
  background-color: currentColor;
  border-radius: 50%;
  display: inline-block;
  animation: dot-pulse 1.4s infinite ease-in-out;
}

.loading-dots .dot:nth-child(2) {
  animation-delay: 0.2s;
}

.loading-dots .dot:nth-child(3) {
  animation-delay: 0.4s;
}

@keyframes dot-pulse {
  0%, 100% {
    transform: scale(0.8);
    opacity: 0.6;
  }
  50% {
    transform: scale(1.2);
    opacity: 1;
  }
}

/* Ajustes para los estados de los botones */
.test-button:disabled {
  opacity: 0.8;
}

.test-button:disabled.is-success {
  background-color: #27AE60;
  opacity: 1;
}

.submit-button:disabled {
  opacity: 0.8;
}

/* Ajustes responsivos */
@media (max-width: 768px) {
  .loading-dots {
    height: 16px;
  }
  
  .loading-dots .dot {
    width: 4px;
    height: 4px;
  }
}

/* Estilos para el selector de temas */
.theme-selector {
  margin-right: 10px; 
  margin-left: auto; 
  position: relative;
}

.theme-select {
  background-color: #32323A;
  color: var(--color-text-secondary, #E0E0E0);
  border: 1px solid #3A3A45;
  border-radius: 8px;
  padding: 6px 10px;
  font-size: 14px;
  appearance: none;
  padding-right: 28px;
  cursor: pointer;
  transition: all 0.3s ease;
}

.theme-select:hover:not(:disabled) {
  background-color: #3A3A45;
  color: var(--color-text-primary, #FFFFFF);
}

.theme-select:focus {
  outline: none;
  box-shadow: 0 0 0 2px rgba(235, 179, 0, 0.3);
}

.theme-select:disabled {
  opacity: 0.8;
  cursor: not-allowed;
}

/* Flecha personalizada para el select */
.theme-selector::after {
  content: "▼";
  font-size: 10px;
  color: var(--color-text-secondary, #E0E0E0);
  position: absolute;
  right: 10px;
  top: 50%;
  transform: translateY(-50%);
  pointer-events: none;
}

/* Adaptación del panel header para el nuevo elemento */
.panel-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

/* Media queries para adaptar a móviles */
@media (max-width: 768px) {
  .theme-select {
    width: 40px;
    padding-left: 8px;
    padding-right: 20px;
    font-size: 12px;
    overflow: hidden;
    text-overflow: ellipsis;
  }
  
  .theme-selector::after {
    right: 6px;
  }
}

/* Indicador de modo historial */
.history-mode-indicator {
  position: absolute;
  top: 60px;
  right: 20px;
  background-color: rgba(0, 0, 0, 0.7);
  color: #FFD03F;
  padding: 8px 12px;
  border-radius: 8px;
  display: flex;
  align-items: center;
  gap: 8px;
  z-index: 999;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.3);
  pointer-events: none; /* Para que no interfiera con la interacción */
  animation: fadeInDown 0.5s ease-out;
  border: 1px solid #4C4CFF;
}

.mode-icon {
  font-size: 18px;
}

.mode-text {
  font-size: 14px;
  font-weight: 500;
}

/* Animación de aparición para el indicador */
@keyframes fadeInDown {
  from {
    opacity: 0;
    transform: translateY(-20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}
</style>