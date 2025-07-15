<!-- src/components/Common/resolucion-ejercicios/PracticalRightPanel.vue -->
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

        <!-- Selector de lenguajes -->
        <div v-if="isLanguageSelectorEnabled && !isHistoryMode" class="language-selector">
          <select v-model="selectedLanguage" class="language-select" @change="changeLanguage">
            <option disabled value="">-- Seleccionar lenguaje --</option>
            <option v-for="lang in availableLanguages" :key="lang.id" :value="lang.id">
              {{ lang.name }}
            </option>
          </select>
        </div>

        <!-- Indicador de lenguaje en modo historial -->
        <div v-if="isHistoryMode" class="language-indicator">
          <span class="language-label">Lenguaje:</span>
          <span class="language-name">{{ getLanguageName(selectedLanguage) }}</span>
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
        <EditorCodemirror ref="editorRef" :is-full-screen="isFullScreen" :theme="selectedTheme"
          :read-only="isHistoryMode" />
      </div>

      <div class="panel-footer" :class="{ 'is-hidden': isFullScreen }">
        <!-- Botones de ayuda (helper buttons) - Sección de Pista y Reiniciar -->
        <div class="helper-buttons">
          <button class="helper-button hint-button" title="Ver pista" @click="toggleHintModal"
            :disabled="isHistoryMode">
            <span class="helper-icon">💡</span>
            <span class="helper-text">PISTA</span>
          </button>

          <button class="helper-button reset-button" title="Reiniciar código" @click="resetCode"
            :disabled="isHistoryMode">
            <span class="helper-icon">🔄</span>
            <span class="helper-text">REINICIAR</span>
          </button>
        </div>

        <!-- Botones de acción (TEST y ENVIAR) -->
        <div class="action-buttons">
          <button class="action-button test-button" @click="runTest"
            :disabled="isHistoryMode || isTestExecuting || !currentExercise || isExerciseComplete || testCooldown.isActive"
            :title="isHistoryMode ? 'Modo solo lectura' :
              testCooldown.isActive ? `Bloqueado por uso excesivo - ${formatCooldownTime()}` :
                (isExerciseComplete ? 'Ejercicio ya completado' : 'Probar solución')"
            :class="{ 'cooldown-active': testCooldown.isActive }">
            <span class="button-icon" :class="{ 'rotating': isTestExecuting }">🧪</span>
            <span v-if="testCooldown.isActive">{{ formatCooldownTime() }}</span>
            <span v-else-if="isExerciseComplete">✓</span>
            <span v-else-if="isTestExecuting">EJECUTANDO...</span>
            <span v-else>TEST</span>
          </button>

          <button class="action-button submit-button" @click="submitCode"
            :disabled="isHistoryMode || isSubmitExecuting || !currentExercise">
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
import EditorCodemirror from '../../codemirror-editor/EditorCodemirror.vue';
import judge0Service from '@/services/judge0Service';
import evaluationsService from '@/api/evaluationsService';
import settingsService from '@/api/settingsService';

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
    const availableLanguages = ref([]);
    const selectedLanguage = ref(71); // Python 3 por defecto
    const isLanguageSelectorEnabled = ref(false);

    const isDevelopment = ref(false);

    // Sistema de cooldown para el botón TEST
    const testCooldown = ref({
      isActive: false,
      remainingTime: 0,
      clickCount: 0,
      lastClickTime: 0,
      violations: 0, // 0, 1, 2 para 1min, 3min, 5min respectivamente
      blockDurations: [60, 180, 300] // 1min, 3min, 5min en segundos
    });

    const cooldownInterval = ref(null);


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

    // Función para cargar los lenguajes disponibles
    const loadAvailableLanguages = async () => {
      try {
        console.log("Intentando cargar lenguajes disponibles...");
        const judge0Url = import.meta.env.VITE_JUDGE0_API_URL;
        if (!judge0Url) {
          console.error("URL de Judge0 no configurada");
          return;
        }

        // Verificar que la URL termine correctamente
        const apiUrl = judge0Url.endsWith('/') ? `${judge0Url}languages` : `${judge0Url}/languages`;
        console.log("Haciendo fetch a:", apiUrl);

        const response = await fetch(apiUrl);

        if (!response.ok) {
          console.error("Error al cargar lenguajes:", response.status, response.statusText);
          return;
        }

        const languages = await response.json();

        if (!Array.isArray(languages)) {
          console.error("Respuesta inesperada:", languages);
          return;
        }

        console.log('Lenguajes disponibles cargados:', languages.length);
        console.log('Primer lenguaje:', languages[0]);

        // Asignar directamente a availableLanguages
        availableLanguages.value = languages;

        // Ordenar lenguajes populares al principio
        const popularIds = [71, 63, 62, 54, 50]; // Python, JavaScript, Java, C++, C
        availableLanguages.value.sort((a, b) => {
          const aPopular = popularIds.includes(a.id);
          const bPopular = popularIds.includes(b.id);

          if (aPopular && !bPopular) return -1;
          if (!aPopular && bPopular) return 1;
          return 0;
        });

        // Registrar los lenguajes cargados para debug
        console.log("Lenguajes disponibles:", availableLanguages.value.map(l => `${l.id}: ${l.name}`).join(', '));
      } catch (error) {
        console.error('Error al cargar lenguajes:', error);
      }
    };

    // Función para obtener nombre del lenguaje
    const getLanguageName = (langId) => {
      const parsedId = parseInt(langId);

      // En modo historial, primero intentar cargar desde Judge0 si están disponibles
      if (isHistoryMode.value && availableLanguages.value && availableLanguages.value.length > 0) {
        const lang = availableLanguages.value.find(l => l.id === parsedId);
        if (lang) {
          return lang.name;
        }
      }

      // Mapa de IDs a nombres de lenguaje (actualizado con Judge0)
      const languageNames = {
        71: 'Python (3.8.1)',
        70: 'Python (2.7.17)',
        63: 'JavaScript (Node.js 12.14.0)',
        62: 'Java (OpenJDK 13.0.1)',
        54: 'C++ (GCC 9.2.0)',
        53: 'C++ (GCC 8.3.0)',
        52: 'C++ (GCC 7.4.0)',
        50: 'C (GCC 9.2.0)',
        49: 'C (GCC 8.3.0)',
        48: 'C (GCC 7.4.0)',
        74: 'TypeScript (3.7.4)',
        73: 'Rust (1.40.0)',
        60: 'Go (1.13.5)',
        68: 'PHP (7.4.1)',
        51: 'C# (Mono 6.6.0.161)',
        72: 'Ruby (2.7.0)',
        80: 'R (4.0.0)',
        78: 'Kotlin (1.3.70)',
        59: 'Fortran (GFortran 9.2.0)',
        75: 'C (Clang 7.0.1)',
        76: 'C++ (Clang 7.0.1)'
      };

      return languageNames[parsedId] || `Lenguaje ID ${parsedId}`;
    };



    const changeLanguage = () => {

      // BLOQUEAR cambios de lenguaje en modo historial
      if (isHistoryMode.value) {
        console.log('❌ Cambio de lenguaje bloqueado en modo historial');
        return;
      }

      // Verificar si hay código escrito antes de cambiar
      if (editorRef.value && editorRef.value.getContent) {
        const currentCode = editorRef.value.getContent().trim();

        // Si hay código escrito, mostrar confirmación
        if (currentCode && currentCode.length > 0) {
          // Verificar que no sea solo una plantilla por defecto
          const isDefaultTemplate = currentCode.includes('# Tu código aquí') ||
            currentCode.includes('// Tu código aquí') ||
            currentCode.includes('No hay plantilla específica') ||
            currentCode.includes('Por favor, implementa tu solución aquí');

          if (!isDefaultTemplate) {
            showConfirmation(
              '¿Estás seguro de cambiar el lenguaje? Perderás el código que has escrito.',
              () => {
                // Usuario confirmó, proceder con el cambio
                performLanguageChange();
              },
              () => {
                // Usuario canceló, revertir selección
                const savedLanguage = localStorage.getItem('selected_language_id');
                if (savedLanguage) {
                  selectedLanguage.value = parseInt(savedLanguage);
                }
                showNotification('Cambio de lenguaje cancelado', 'info');
              }
            );
            return; // No continuar con el cambio inmediatamente
          }
        }
      }

      // Si no hay código o es plantilla por defecto, cambiar directamente
      performLanguageChange();
    };

    // Función auxiliar para realizar el cambio de lenguaje
    const performLanguageChange = () => {
      console.log(`Lenguaje cambiado a ID: ${selectedLanguage.value}`);

      // Guardar en localStorage
      localStorage.setItem('selected_language_id', selectedLanguage.value);

      if (currentExercise.value) {
        const userId = getCurrentUserId();
        const evaluationData = localStorage.getItem('currentEvaluation')
          ? JSON.parse(localStorage.getItem('currentEvaluation'))
          : null;
        const evaluationId = evaluationData?.id || 'unknown';
        const exerciseLanguageKey = `exercise_language_${userId}_${evaluationId}_${currentExercise.value.id}`;

        localStorage.setItem(exerciseLanguageKey, selectedLanguage.value.toString());
        console.log(`🔧 Lenguaje ${selectedLanguage.value} guardado para ejercicio ${currentExercise.value.id}`);
      }

      console.log('=== DEBUG EJERCICIO FRONTEND ===');
      console.log('Ejercicio completo:', JSON.stringify(currentExercise.value, null, 2));
      console.log('¿Tiene templates_por_lenguaje?:', !!currentExercise.value.templates_por_lenguaje);
      console.log('Templates por lenguaje:', currentExercise.value.templates_por_lenguaje);
      console.log('¿Tiene template (no debería)?:', !!currentExercise.value.template);
      console.log('==================================');

      // Verificar si necesitamos recargar la plantilla
      if (editorRef.value && currentExercise.value) {
        const exerciseId = currentExercise.value.id;

        // Construir clave del código
        const codeKey = getExerciseCodeKey(exerciseId);

        // Importante: SIEMPRE borrar el código guardado al cambiar de lenguaje
        localStorage.removeItem(codeKey);
        console.log(`Borrado código guardado para cargar plantilla del lenguaje ${selectedLanguage.value}`);

        // Cargar directamente la plantilla específica para el nuevo lenguaje
        try {
          // Primero, intentar obtener la plantilla específica del ejercicio actual
          let template = '';
          let templateFound = false;

          console.log('Ejercicio actual:', currentExercise.value);
          console.log('Estructura completa del ejercicio:', Object.keys(currentExercise.value));

          // Buscar directamente en templates_por_lenguaje
          if (currentExercise.value.templates_por_lenguaje &&
            typeof currentExercise.value.templates_por_lenguaje === 'object') {
            const langIdStr = String(selectedLanguage.value);

            console.log('Buscando en templates_por_lenguaje para lenguaje:', langIdStr);
            console.log('Templates disponibles:', currentExercise.value.templates_por_lenguaje);

            if (currentExercise.value.templates_por_lenguaje[langIdStr]) {
              template = currentExercise.value.templates_por_lenguaje[langIdStr];
              templateFound = true;
              console.log(`Plantilla encontrada en templates_por_lenguaje para lenguaje ID ${selectedLanguage.value}`);
            }
          }

          // Luego buscar en contenido.templates (por compatibilidad)
          if (!templateFound && currentExercise.value.contenido) {
            const contenido = typeof currentExercise.value.contenido === 'object'
              ? currentExercise.value.contenido
              : {};

            console.log('Buscando en contenido.templates');

            if (contenido.templates && typeof contenido.templates === 'object') {
              const langIdStr = String(selectedLanguage.value);

              if (contenido.templates[langIdStr]) {
                template = contenido.templates[langIdStr];
                templateFound = true;
                console.log(`Plantilla específica para lenguaje ID ${selectedLanguage.value} encontrada en contenido.templates`);
              }
            }
          }

          // Si no se encontró plantilla, generar una por defecto
          if (!templateFound) {
            const langName = availableLanguages.value.find(l => l.id === selectedLanguage.value)?.name ||
              `Lenguaje ID ${selectedLanguage.value}`;
            const comentario = selectedLanguage.value === 71 ? '#' : '//';
            template = `${comentario} No hay plantilla específica para ${langName} en este ejercicio\n${comentario} Por favor, implementa tu solución aquí`;
            console.log('Usando plantilla por defecto generada');
          }

          // Establecer directamente el contenido en el editor
          if (editorRef.value && editorRef.value.setContent) {
            editorRef.value.setContent(template);
            console.log("Plantilla cargada directamente en el editor");

            // Guardar el nuevo código
            if (editorRef.value.saveCurrentCode) {
              setTimeout(() => {
                editorRef.value.saveCurrentCode();
                console.log("Nuevo código guardado en localStorage");
              }, 100);
            }
          } else {
            console.warn("No se puede acceder al método setContent del editor");
          }
        } catch (e) {
          console.error("Error al cargar plantilla:", e);
        }
      }

      // Mostrar notificación si está disponible
      const selectedLang = availableLanguages.value.find(lang => lang.id === selectedLanguage.value);
      const langName = selectedLang ? selectedLang.name : `ID: ${selectedLanguage.value}`;

      if (notificationRef?.value?.showNotification) {
        notificationRef.value.showNotification(`Lenguaje cambiado a: ${langName}`, 'info');
      }
    };



    // Función para verificar si el selector está habilitado
    const checkLanguageSelectorEnabled = async () => {
      console.log("🔧 Verificando configuración del selector de lenguajes desde servidor...");

      try {
        // SIEMPRE consultar al servidor primero
        const response = await settingsService.getLanguageSelectorConfig();

        if (response.data.success) {
          const enabled = response.data.language_selector_enabled;
          const defaultLang = response.data.default_language_id || 71;

          isLanguageSelectorEnabled.value = enabled;

          console.log(`🎛️ Configuración desde servidor: ${enabled ? 'HABILITADO' : 'DESHABILITADO'}`);
          console.log(`🐍 Lenguaje por defecto: ${defaultLang}`);

          // Configurar lenguaje
          if (enabled) {
            // Si está habilitado, usar el lenguaje guardado o el por defecto
            const savedLanguage = localStorage.getItem('selected_language_id');
            selectedLanguage.value = savedLanguage ? parseInt(savedLanguage) : defaultLang;

            // Cargar lenguajes disponibles solo si está habilitado
            await loadAvailableLanguages();
          } else {
            // Si está deshabilitado, usar Python por defecto y no cargar lenguajes
            selectedLanguage.value = defaultLang;
            availableLanguages.value = []; // Limpiar lenguajes para ahorrar memoria
          }

          // Sincronizar localStorage
          localStorage.setItem('language_selector_enabled', enabled.toString());
          localStorage.setItem('selected_language_id', selectedLanguage.value.toString());

        } else {
          throw new Error('Configuración no válida desde servidor');
        }
      } catch (error) {
        console.error('❌ Error al obtener configuración desde servidor:', error);
        console.log('🔄 Usando configuración de emergencia (DESHABILITADO)');

        // Configuración de emergencia: DESHABILITADO
        isLanguageSelectorEnabled.value = false;
        selectedLanguage.value = 71; // Python por defecto
        availableLanguages.value = [];

        // NO usar localStorage como fallback para evitar configuraciones obsoletas
        localStorage.setItem('language_selector_enabled', 'false');
        localStorage.setItem('selected_language_id', '71');
      }
    };

    const setupConfigListener = () => {
      console.log("📡 Configurando listener de cambios de configuración...");

      // Escuchar eventos de cambio de configuración
      const handleConfigChange = async (event) => {
        console.log("📡 Evento de cambio de configuración recibido:", event.detail);

        // Re-verificar configuración desde servidor
        await checkLanguageSelectorEnabled();
      };

      // Escuchar el evento personalizado del AdminHome
      window.addEventListener('language-selector-config-changed', handleConfigChange);

      // NO escuchar localStorage para evitar configuraciones obsoletas
      // Solo el servidor es la fuente de verdad

      // Verificar configuración cada 30 segundos como respaldo
      const configInterval = setInterval(async () => {
        try {
          const response = await settingsService.getLanguageSelectorConfig();
          if (response.data.success) {
            const serverEnabled = response.data.language_selector_enabled;

            if (serverEnabled !== isLanguageSelectorEnabled.value) {
              console.log("🔄 Cambio de configuración detectado desde servidor");
              await checkLanguageSelectorEnabled();
            }
          }
        } catch (error) {
          // Silenciar errores del polling para no saturar los logs
        }
      }, 30000); // 30 segundos

      // Limpiar al desmontar
      onBeforeUnmount(() => {
        window.removeEventListener('language-selector-config-changed', handleConfigChange);
        clearInterval(configInterval);
      });
    };

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
          console.log(`Código eliminado para ejercicio ${exerciseId}`);

          // Buscar la plantilla específica para el lenguaje actual
          let template = '';
          let templateFound = false;

          if (currentExercise.value.contenido) {
            const contenido = typeof currentExercise.value.contenido === 'object'
              ? currentExercise.value.contenido
              : JSON.parse(currentExercise.value.contenido || '{}');

            // Buscar en templates por lenguaje
            if (contenido.templates && contenido.templates[selectedLanguage.value]) {
              template = contenido.templates[selectedLanguage.value];
              templateFound = true;
              console.log(`Restablecida plantilla para lenguaje ID ${selectedLanguage.value}`);
            }
            // Si no hay plantilla para este lenguaje pero hay una para Python
            else if (contenido.templates && contenido.templates['71'] && selectedLanguage.value !== 71) {
              const langName = availableLanguages.value.find(l => l.id === selectedLanguage.value)?.name ||
                `Lenguaje ID ${selectedLanguage.value}`;
              template = `// No hay plantilla específica para ${langName} en este ejercicio\n// Por favor, implementa tu solución aquí`;
              templateFound = true;
            }
            // Usar plantilla general como fallback
            else if (contenido.template) {
              template = contenido.template;
              templateFound = true;
            }
          }

          // Si no se encontró plantilla, generar una por defecto
          if (!templateFound) {
            const langName = availableLanguages.value.find(l => l.id === selectedLanguage.value)?.name ||
              `Lenguaje ID ${selectedLanguage.value}`;
            // Usar # para Python, // para otros lenguajes
            const comentario = selectedLanguage.value === 71 ? '#' : '//';
            template = `${comentario} No hay plantilla específica para ${langName} en este ejercicio\n${comentario} Por favor, implementa tu solución aquí`;
          }

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
      // Verificar cooldown antes de ejecutar
      if (!checkTestCooldown()) {
        handleTestCooldownClick();
        return;
      }

      if (isHistoryMode.value) return;

      if (!editorRef.value || !currentExercise.value) {
        console.error("No se puede ejecutar la prueba: faltan referencias necesarias");
        return;
      }

      if (!selectedLanguage.value) {
        console.error("No hay lenguaje seleccionado");
        if (leftPanelRef && leftPanelRef.value) {
          leftPanelRef.value.setTestResults("Error: No se ha seleccionado un lenguaje de programación");
          leftPanelRef.value.activateOutputTab();
        }
        isTestExecuting.value = false;
        return;
      }

      // Que lenguaje de programacion?
      console.log(`Ejecutando codigo con language ID: ${selectedLanguage.value}`);

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
            const testResult = await judge0Service.executeCode(
              codigo_completo,
              "", // input
              "", // expected output
              selectedLanguage.value // ID del lenguaje
            );

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

            const verification = await judge0Service.verificarEjemplos(
              code,
              ejemplos,
              selectedLanguage.value // ID del lenguaje
            );

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
            const resultado = await judge0Service.executeCode(
              code,
              "", // input
              "", // expected output
              selectedLanguage.value // ID del lenguaje
            );

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

        // Emitir evento para notificar cambio de estado
        window.dispatchEvent(new CustomEvent('exercise-status-changed', {
          detail: {
            exerciseId: exerciseId,
            userId: userId,
            isCompleted: isCompleted
          }
        }));

        // Emitir evento de compatibilidad para checkAllExercisesCompleted
        if (isCompleted) {
          window.dispatchEvent(new CustomEvent('exercise-completed', {
            detail: { exerciseId: exerciseId }
          }));
        }
      }
    }

    const extractTestCode = (exercise) => {
      let testCode = null;

      if (exercise.tests_avanzados) {
        // Si tests_avanzados es un objeto, buscar tests para el lenguaje actual
        if (typeof exercise.tests_avanzados === 'object' && !Array.isArray(exercise.tests_avanzados)) {
          testCode = exercise.tests_avanzados[selectedLanguage.value];

          // Si no hay tests para este lenguaje, intentar con Python (71) como fallback
          if (!testCode && selectedLanguage.value !== 71) {
            testCode = exercise.tests_avanzados['71'];
            console.log("No hay tests para el lenguaje seleccionado, usando tests de Python como alternativa");
          }
        } else {
          // Compatibilidad con el formato anterior (string)
          testCode = exercise.tests_avanzados;
        }
      } else if (exercise.contenido) {
        // Buscando en contenido
        if (typeof exercise.contenido === 'object') {
          if (exercise.contenido.tests_avanzados) {
            if (typeof exercise.contenido.tests_avanzados === 'object' && !Array.isArray(exercise.contenido.tests_avanzados)) {
              testCode = exercise.contenido.tests_avanzados[selectedLanguage.value];

              // Fallback a Python
              if (!testCode && selectedLanguage.value !== 71) {
                testCode = exercise.contenido.tests_avanzados['71'];
                console.log("No hay tests para el lenguaje seleccionado en contenido, usando tests de Python como alternativa");
              }
            } else {
              testCode = exercise.contenido.tests_avanzados;
            }
          }
        } else if (typeof exercise.contenido === 'string') {
          try {
            const parsed = JSON.parse(exercise.contenido);
            if (parsed.tests_avanzados) {
              if (typeof parsed.tests_avanzados === 'object' && !Array.isArray(parsed.tests_avanzados)) {
                testCode = parsed.tests_avanzados[selectedLanguage.value];

                // Fallback a Python
                if (!testCode && selectedLanguage.value !== 71) {
                  testCode = parsed.tests_avanzados['71'];
                  console.log("No hay tests para el lenguaje seleccionado en contenido JSON, usando tests de Python como alternativa");
                }
              } else {
                testCode = parsed.tests_avanzados;
              }
            }
          } catch (e) {
            console.warn('Error al parsear contenido para tests:', e);
          }
        }
      }

      // Añadir funciones auxiliares si es necesario, adaptadas por lenguaje
      if (testCode) {
        // Para Python
        if (selectedLanguage.value === 71 &&
          !testCode.includes('def ejecutar_tests_avanzados') &&
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
        // Para JavaScript
        else if (selectedLanguage.value === 63 && !testCode.includes('function ejecutarTestsAvanzados') && !testCode.includes('function test(')) {
          const auxiliarFunction = `
// Función auxiliar para ejecutar pruebas avanzadas (añadida automáticamente)
function ejecutarTestsAvanzados(func, casosPrueba, mostrarDetalle = true) {
    /**
     * Ejecuta una serie de pruebas para una función.
     * 
     * @param {Function} func - La función a probar
     * @param {Array} casosPrueba - Lista de tuplas [entrada, salidaEsperada]
     * @param {boolean} mostrarDetalle - Si es true, muestra el detalle de cada caso
     * @return {number} Número de pruebas pasadas
     */
    let pruebasPasadas = 0;
    const totalPruebas = casosPrueba.length;
    
    console.log(\`Ejecutando \${totalPruebas} pruebas:\`);
    
    for (let i = 0; i < casosPrueba.length; i++) {
        try {
            const [entrada, esperado] = casosPrueba[i];
            let resultado;
            
            // Si la entrada es un array, usar spread operator
            if (Array.isArray(entrada)) {
                resultado = func(...entrada);
            } else {
                resultado = func(entrada);
            }
            
            if (JSON.stringify(resultado) === JSON.stringify(esperado)) {
                pruebasPasadas++;
                if (mostrarDetalle) {
                    console.log(\`✓ CORRECTO - Prueba \${i+1}: con entrada \${JSON.stringify(entrada)} se obtuvo \${JSON.stringify(resultado)}\`);
                }
            } else {
                if (mostrarDetalle) {
                    console.log(\`✗ INCORRECTO - Prueba \${i+1}: con entrada \${JSON.stringify(entrada)}\`);
                    console.log(\`  Se esperaba: \${JSON.stringify(esperado)}\`);
                    console.log(\`  Se obtuvo: \${JSON.stringify(resultado)}\`);
                }
            }
        } catch (e) {
            if (mostrarDetalle) {
                console.log(\`✗ ERROR - Prueba \${i+1}: con entrada \${JSON.stringify(casosPrueba[i][0])}\`);
                console.log(\`  Error: \${e.message}\`);
            }
        }
    }
    
    console.log(\`Resultado: \${pruebasPasadas}/\${totalPruebas} pruebas pasadas\`);
    return pruebasPasadas;
}

// Función auxiliar para pruebas individuales
function test(actual, expected, message = "") {
    if (JSON.stringify(actual) === JSON.stringify(expected)) {
        console.log(\`✓ CORRECTO: \${message}\`);
        return true;
    } else {
        console.log(\`✗ INCORRECTO: \${message}\`);
        console.log(\`  Esperado: \${JSON.stringify(expected)}\`);
        console.log(\`  Obtenido: \${JSON.stringify(actual)}\`);
        return false;
    }
}
      `;

          testCode = auxiliarFunction + "\n\n" + testCode;
        }
        // Para Java
        else if (selectedLanguage.value === 62 && !testCode.includes('class TestRunner')) {
          // Si el código Java no tiene una clase TestRunner principal
          if (!testCode.includes('public static void main') && !testCode.trim().startsWith('public class')) {
            const auxiliarFunction = `
// Clase auxiliar para ejecutar pruebas (añadida automáticamente)
public class TestRunner {
    public static void main(String[] args) {
        // El código de prueba debe estar debajo de esta línea
        System.out.println("Ejecutando pruebas...");
        
        // Declaración para registro de resultados
        int resultadoTests = 0;
        int totalTests = 0;
`;

            const closingCode = `
        // Mostrar resumen de resultados
        System.out.println("Resultado: " + resultadoTests + "/" + totalTests + " pruebas pasadas");
    }
    
    // Función auxiliar para pruebas
    public static boolean test(Object actual, Object expected, String message) {
        if (actual.equals(expected)) {
            System.out.println("✓ CORRECTO: " + message);
            return true;
        } else {
            System.out.println("✗ INCORRECTO: " + message);
            System.out.println("  Esperado: " + expected);
            System.out.println("  Obtenido: " + actual);
            return false;
        }
    }
}`;

            testCode = auxiliarFunction + "\n\n" + testCode + "\n\n" + closingCode;
          }
        }
      }

      // Añadir mensajes de log para depuración
      if (testCode) {
        console.log(`Tests cargados para lenguaje ID: ${selectedLanguage.value}`);
      } else {
        console.log(`No se encontraron tests para el lenguaje ID: ${selectedLanguage.value}`);
      }

      return testCode;
    };


    // Métodos del sistema de cooldown
    const checkTestCooldown = () => {
      const now = Date.now();
      const tenSecondsAgo = now - 10000; // 10 segundos en millisegundos

      // Limpiar clics antiguos (más de 10 segundos)
      if (testCooldown.value.lastClickTime < tenSecondsAgo) {
        testCooldown.value.clickCount = 0;
      }

      // Verificar si está en cooldown activo
      if (testCooldown.value.isActive) {
        return false; // Bloqueado
      }

      // Registrar el clic actual
      testCooldown.value.clickCount++;
      testCooldown.value.lastClickTime = now;

      // Verificar si se ha superado el límite de clics
      if (testCooldown.value.clickCount >= 10) {
        activateTestCooldown();
        return false;
      }

      return true; // Permitir ejecución
    };

    const activateTestCooldown = () => {
      const violationLevel = Math.min(testCooldown.value.violations, 2);
      const duration = testCooldown.value.blockDurations[violationLevel];

      testCooldown.value.isActive = true;
      testCooldown.value.remainingTime = duration;
      testCooldown.value.clickCount = 0;
      testCooldown.value.violations++;

      // Mostrar notificación de bloqueo
      const minutes = Math.floor(duration / 60);
      const seconds = duration % 60;
      const timeText = seconds > 0 ? `${minutes}m ${seconds}s` : `${minutes}m`;

      showNotification(
        `🚫 Botón TEST bloqueado por ${timeText} debido a uso excesivo. Espera entre cada ejecución.`,
        'warning'
      );

      // Iniciar countdown
      cooldownInterval.value = setInterval(() => {
        testCooldown.value.remainingTime--;

        if (testCooldown.value.remainingTime <= 0) {
          testCooldown.value.isActive = false;
          clearInterval(cooldownInterval.value);
          cooldownInterval.value = null;

          showNotification('✅ Botón TEST desbloqueado. Recuerda esperar entre ejecuciones.', 'success');
        }
      }, 1000);
    };

    const formatCooldownTime = () => {
      const minutes = Math.floor(testCooldown.value.remainingTime / 60);
      const seconds = testCooldown.value.remainingTime % 60;
      return `${minutes}:${seconds.toString().padStart(2, '0')}`;
    };

    const handleTestCooldownClick = () => {
      if (testCooldown.value.isActive) {
        const timeLeft = formatCooldownTime();
        showNotification(
          `⏱️ Botón bloqueado por uso excesivo. Tiempo restante: ${timeLeft}`,
          'warning'
        );
      }
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

        // Obtener userId usando la función
        const userId = getCurrentUserId();

        // CORREGIDO: Obtener evaluationId con múltiples fuentes de respaldo
        let evaluationIdFinal = null;
        let evaluationData = null;

        // 1. Primero intentar desde la inyección evaluation
        if (evaluation.value && evaluation.value.id) {
          evaluationIdFinal = evaluation.value.id;
          evaluationData = evaluation.value;
          console.log(`📝 ID de evaluación obtenido desde inyección: ${evaluationIdFinal}`);
        }

        // 2. Si no se encuentra, intentar desde localStorage
        if (!evaluationIdFinal) {
          const storedEvaluation = localStorage.getItem('currentEvaluation');
          if (storedEvaluation) {
            try {
              const parsedEvaluation = JSON.parse(storedEvaluation);
              if (parsedEvaluation && parsedEvaluation.id) {
                evaluationIdFinal = parsedEvaluation.id;
                evaluationData = parsedEvaluation;
                console.log(`📝 ID de evaluación obtenido desde localStorage: ${evaluationIdFinal}`);
              }
            } catch (parseError) {
              console.error("Error al parsear evaluación de localStorage:", parseError);
            }
          }
        }

        // 3. Si aún no se encuentra, intentar desde la URL/router
        if (!evaluationIdFinal) {
          const routeEvaluationId = router.currentRoute.value.params.evaluationId ||
            router.currentRoute.value.query.evaluationId;
          if (routeEvaluationId) {
            evaluationIdFinal = routeEvaluationId;
            evaluationData = { id: routeEvaluationId };
            console.log(`📝 ID de evaluación obtenido desde ruta: ${evaluationIdFinal}`);
          }
        }

        // Verificar que tenemos un ID válido
        if (!evaluationIdFinal) {
          // Mostrar información de debug
          console.error("🚨 DEBUG - No se pudo determinar el ID de evaluación:");
          console.error("- evaluation.value:", evaluation.value);
          console.error("- localStorage currentEvaluation:", localStorage.getItem('currentEvaluation'));
          console.error("- router params:", router.currentRoute.value.params);
          console.error("- router query:", router.currentRoute.value.query);

          throw new Error("No se pudo determinar el ID de la evaluación actual. Por favor, recarga la página e intenta nuevamente.");
        }

        // Procesar ejercicios para envío
        for (const ejercicio of exercises.value) {
          if (!ejercicio || !ejercicio.id) {
            console.warn(`Ejercicio sin ID detectado:`, ejercicio);
            continue;
          }

          // CORREGIDO: Usar la misma lógica que EditorCodemirror.vue para generar la clave
          const getConsistentCodeKey = (exerciseId) => {
            const userId = localStorage.getItem('user_id') || 'anonymous';
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

          // CORREGIDO: Buscar código con múltiples claves posibles
          const codeKey = getConsistentCodeKey(ejercicio.id);
          let codigo = localStorage.getItem(codeKey) || "";

          // Si no se encuentra con la clave principal, intentar con claves alternativas
          if (!codigo) {
            const alternativeKeys = [
              `exercise_code_${userId}_${evaluationIdFinal}_${ejercicio.id}`,
              `exercise_code_${userId}_unknown_${ejercicio.id}`,
              `exercise_code_${userId}_${ejercicio.id}`,
              `exercise_code_anonymous_${evaluationIdFinal}_${ejercicio.id}`,
              `exercise_code_anonymous_unknown_${ejercicio.id}`
            ];

            for (const altKey of alternativeKeys) {
              codigo = localStorage.getItem(altKey);
              if (codigo) {
                console.log(`📝 Código encontrado con clave alternativa: ${altKey}`);
                break;
              }
            }
          }

          // Si aún no hay código, intentar obtenerlo directamente del editor si es el ejercicio actual
          if (!codigo && currentExerciseIndex.value !== undefined &&
            exercises.value[currentExerciseIndex.value]?.id === ejercicio.id &&
            editorRef.value) {
            try {
              // Guardar el código actual del editor antes de enviarlo
              if (editorRef.value.saveCurrentCode) {
                editorRef.value.saveCurrentCode();
              }
              // Intentar obtenerlo nuevamente después de guardarlo
              codigo = localStorage.getItem(codeKey) || "";

              if (codigo) {
                console.log(`📝 Código obtenido del editor actual para ejercicio ${ejercicio.id}`);
              }
            } catch (e) {
              console.warn('Error al obtener código del editor:', e);
            }
          }

          // Buscar lenguaje con múltiples claves posibles
          let languageId = 71; // Python por defecto
          const languageKeys = [
            `exercise_language_${userId}_${evaluationIdFinal}_${ejercicio.id}`,
            `exercise_language_${userId}_unknown_${ejercicio.id}`,
            `exercise_language_${userId}_${ejercicio.id}`
          ];

          for (const langKey of languageKeys) {
            const savedLanguage = localStorage.getItem(langKey);
            if (savedLanguage) {
              languageId = parseInt(savedLanguage);
              console.log(`📝 Lenguaje encontrado con clave: ${langKey} = ${languageId}`);
              break;
            }
          }

          // Si aún no se encuentra y es el ejercicio actual, intentar obtener del estado actual
          if (languageId === 71 && currentExerciseIndex.value !== undefined &&
            exercises.value[currentExerciseIndex.value]?.id === ejercicio.id) {
            if (selectedLanguage.value && selectedLanguage.value !== 71) {
              languageId = selectedLanguage.value;
              console.log(`📝 Usando lenguaje del ejercicio actual: ${languageId}`);
            }
          }


          console.log(`Ejercicio ID: ${ejercicio.id}, Título: ${ejercicio.titulo || 'Sin título'}`);
          console.log(`- Código encontrado: ${codigo ? 'Sí' : 'No'} (${codigo?.length || 0} caracteres)`);
          console.log(`- Clave utilizada: ${codeKey}`);
          console.log(`- Lenguaje: ${languageId}`);

          const codigoFinal = codigo || generateDefaultTemplate(ejercicio);

          ejerciciosParaEnviar.push({
            ejercicio_id: ejercicio.id,
            codigo: codigoFinal,
            language_id: languageId
          });

          console.log(`✅ Ejercicio ID ${ejercicio.id} añadido para envío (${codigoFinal.length} caracteres)`);
        }

        if (ejerciciosParaEnviar.length === 0) {
          throw new Error("No hay ejercicios para enviar. Algo está mal con la carga de ejercicios.");
        }

        console.log(`🧮 Total de ejercicios preparados para envío: ${ejerciciosParaEnviar.length}`);
        console.log(`📝 Evaluación ID final: ${evaluationIdFinal}, Título: ${evaluationData?.titulo || evaluationData?.title || 'Sin título'}`);

        // Verificar disponibilidad de Judge0
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

        console.log(`🚀 Enviando batch de ${ejerciciosParaEnviar.length} ejercicios para evaluación ${evaluationIdFinal}`);

        // Enviar batch
        const response = await evaluationsService.submitBatch({
          evaluacion_id: evaluationIdFinal,
          ejercicios: ejerciciosParaEnviar,
          useJudge0: true
        }, exercises.value);

        console.log("✅ Respuesta del procesamiento batch recibida:", response.data);

        if (response.data && response.data.success) {
          console.log("🔍 Guardando puntuaciones para usuario", userId);
          console.log("Total score:", response.data.total_puntaje);
          console.log("Max score:", response.data.puntaje_maximo);
          console.log("Scaled score:", response.data.puntaje_sobre_10);

          // Guardar resultados en localStorage
          localStorage.setItem(`evaluation_total_score_${userId}`, response.data.total_puntaje);
          localStorage.setItem(`evaluation_max_score_${userId}`, response.data.puntaje_maximo);
          localStorage.setItem(`evaluation_scaled_score_${userId}`, response.data.puntaje_sobre_10);
          localStorage.setItem(`evaluation_raw_results_${userId}`, JSON.stringify(response.data));
          localStorage.setItem(`evaluationEndTime_${userId}`, Date.now().toString());

          // Guardar ID de evaluación completada para la página de resultados
          localStorage.setItem('completedEvaluationId', evaluationIdFinal);

          if (leftPanelRef && leftPanelRef.value) {
            const resultSummary = createResultSummary(response.data);
            leftPanelRef.value.setTestResults(resultSummary);
          }

          // Procesar resultados individuales
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
            console.log(`🏁 Finalizando evaluación con ID: ${evaluationIdFinal}`);
            await evaluationsService.finishEvaluation(evaluationIdFinal);
            console.log("✅ Evaluación finalizada correctamente");
          } catch (finishError) {
            console.error("Error al finalizar evaluación:", finishError);
          }

          // Redirigir después de un breve delay
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
      // Para cualquier lenguaje (incluido Python) solo mostrar un mensaje informativo
      const langName = availableLanguages.value.find(l => l.id === selectedLanguage.value)?.name ||
        `Lenguaje ID ${selectedLanguage.value}`;
      return `# No hay plantilla específica para ${langName} en este ejercicio\n# Por favor, implementa tu solución aquí`;
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

      // Inicializar la variable de entorno
      try {
        isDevelopment.value = import.meta.env.DEV || false;
      } catch (e) {
        isDevelopment.value = false;
      }

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


      // Verificar configuración desde servidor PRIMERO
      console.log("🔧 Cargando configuración del selector de lenguajes...");
      await checkLanguageSelectorEnabled();

      // ESPECÍFICO PARA MODO HISTORIAL: Cargar lenguajes de Judge0 para mostrar nombres correctos
      if (isHistoryMode.value) {
        console.log("🔧 Modo historial: cargando lenguajes de Judge0 para nombres correctos...");
        try {
          await loadAvailableLanguages();
          console.log(`✅ Lenguajes cargados para historial: ${availableLanguages.value.length}`);
        } catch (error) {
          console.error("Error al cargar lenguajes para historial:", error);
        }
      }


      // Configurar listener de cambios
      setupConfigListener();

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

      checkLanguageSelectorEnabled();


      // Cargar lenguaje desde historial si estamos en modo historial
      if (isHistoryMode.value && currentExercise.value) {
        console.log('🔍 Modo historial detectado, cargando lenguaje desde ejercicio');

        // Intentar obtener el lenguaje desde el ejercicio del historial
        if (currentExercise.value.language_id) {
          selectedLanguage.value = currentExercise.value.language_id;
          console.log(`📝 Lenguaje fijado desde historial: ${selectedLanguage.value}`);
        } else {
          // Si no hay language_id, usar Python por defecto
          selectedLanguage.value = 71;
          console.log('⚠️ No se encontró lenguaje en historial, usando Python por defecto');
        }

        // NO permitir cambios posteriores
        localStorage.setItem('selected_language_id', selectedLanguage.value.toString());
      }

      // Cargar lenguajes independientemente
      try {
        console.log("Cargando lenguajes disponibles...");
        await loadAvailableLanguages();
        console.log(`Se cargaron ${availableLanguages.value.length} lenguajes`);
      } catch (error) {
        console.error("Error al cargar lenguajes:", error);
      }

      // Si está habilitado, inicializar correctamente
      if (isLanguageSelectorEnabled.value) {
        console.log("Selector de lenguajes HABILITADO - debería mostrarse");
      } else {
        console.log("Selector de lenguajes DESHABILITADO - no se mostrará");
      }
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

      // Limpiar cooldown
      if (cooldownInterval.value) {
        clearInterval(cooldownInterval.value);
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


    // Watcher para cambiar lenguaje automáticamente cuando cambia el ejercicio
    watch(currentExercise, (newExercise, oldExercise) => {
      if (newExercise && newExercise.id !== oldExercise?.id) {

        console.log('🔄 EJERCICIO CAMBIÓ:', {
          anterior: oldExercise?.id,
          nuevo: newExercise.id,
          modoHistorial: isHistoryMode.value,
          ejercicioCompleto: newExercise
        });

        // MODO HISTORIAL: obtener lenguaje desde el ejercicio
        if (isHistoryMode.value) {
          console.log('🔍 HISTORIAL DEBUG - Ejercicio completo:', newExercise);
          console.log('🔍 HISTORIAL DEBUG - ID:', newExercise.id);
          console.log('🔍 HISTORIAL DEBUG - language_id:', newExercise.language_id);
          console.log('🔍 HISTORIAL DEBUG - codigo:', newExercise.codigo);
          console.log('🔍 HISTORIAL DEBUG - template:', newExercise.template);
          console.log('🔍 HISTORIAL DEBUG - contenido:', newExercise.contenido);

          // Verificar todas las fuentes posibles de código
          let codigoParaDetectar = '';

          if (newExercise.codigo) {
            codigoParaDetectar = newExercise.codigo;
            console.log('🔍 HISTORIAL DEBUG - Usando newExercise.codigo');
          } else if (newExercise.template) {
            codigoParaDetectar = newExercise.template;
            console.log('🔍 HISTORIAL DEBUG - Usando newExercise.template');
          } else if (newExercise.contenido && newExercise.contenido.template) {
            codigoParaDetectar = newExercise.contenido.template;
            console.log('🔍 HISTORIAL DEBUG - Usando newExercise.contenido.template');
          }

          console.log('🔍 HISTORIAL DEBUG - Código final para detectar:', codigoParaDetectar);

          // DETECCIÓN DE LENGUAJE basada en el código
          let detectedLanguage = 71; // Python por defecto

          // Detectar JavaScript (mejorado)
          if (codigoParaDetectar.includes('console.log') ||
            codigoParaDetectar.includes('function') ||
            codigoParaDetectar.includes('let ') ||
            codigoParaDetectar.includes('const ') ||
            codigoParaDetectar.includes('var ') ||
            codigoParaDetectar.includes('document.') ||
            codigoParaDetectar.includes('window.') ||
            codigoParaDetectar.includes('alert(') ||
            codigoParaDetectar.includes('=>') ||
            codigoParaDetectar.includes('console.')) {
            detectedLanguage = 63; // JavaScript
            console.log('🔍 HISTORIAL DEBUG - Detectado JavaScript');
          }
          // Detectar Java (mejorado)
          else if (codigoParaDetectar.includes('public class') ||
            codigoParaDetectar.includes('system.out.print') ||
            codigoParaDetectar.includes('public static void main') ||
            codigoParaDetectar.includes('string[]') ||
            codigoParaDetectar.includes('system.out.println')) {
            detectedLanguage = 62; // Java
            console.log('🔍 HISTORIAL DEBUG - Detectado Java');
          }
          // Detectar C++ (mejorado)
          else if (codigoParaDetectar.includes('#include') ||
            codigoParaDetectar.includes('std::') ||
            codigoParaDetectar.includes('cout') ||
            codigoParaDetectar.includes('cin') ||
            codigoParaDetectar.includes('namespace std')) {
            detectedLanguage = 54; // C++
            console.log('🔍 HISTORIAL DEBUG - Detectado C++');
          }
          // Detectar C (mejorado)
          else if ((codigoParaDetectar.includes('#include') && codigoParaDetectar.includes('printf')) ||
            codigoParaDetectar.includes('scanf') ||
            codigoParaDetectar.includes('main()')) {
            detectedLanguage = 50; // C
            console.log('🔍 HISTORIAL DEBUG - Detectado C');
          }
          // Python - verificar patrones específicos
          else if (codigoParaDetectar.includes('print(') ||
            codigoParaDetectar.includes('def ') ||
            codigoParaDetectar.includes('import ') ||
            codigoParaDetectar.includes('from ') ||
            codigoParaDetectar.includes('elif') ||
            codigoParaDetectar.includes('range(')) {
            detectedLanguage = 71; // Python
            console.log('🔍 HISTORIAL DEBUG - Detectado Python');
          }
          // Por defecto mantener Python
          else {
            detectedLanguage = 71; // Python
            console.log('🔍 HISTORIAL DEBUG - Detectado Python (por defecto)');
          }

          // Usar language_id si existe, sino el detectado
          let finalLanguage = detectedLanguage;

          // Solo usar language_id original si:
          // 1. No se pudo detectar nada (detectedLanguage es 71 por defecto), Y
          // 2. Existe un language_id específico diferente de Python
          if (detectedLanguage === 71 && newExercise.language_id && newExercise.language_id !== 71) {
            finalLanguage = newExercise.language_id;
            console.log(`🔍 HISTORIAL DEBUG - Usando language_id original porque no se detectó nada específico`);
          } else if (detectedLanguage !== 71) {
            console.log(`🔍 HISTORIAL DEBUG - Usando lenguaje detectado porque hay evidencia clara en el código`);
          }

          console.log(`🔍 HISTORIAL DEBUG - Lenguaje final: ${finalLanguage}`);
          console.log(`🔍 HISTORIAL DEBUG - Original language_id: ${newExercise.language_id}`);
          console.log(`🔍 HISTORIAL DEBUG - Detectado: ${detectedLanguage}`);

          selectedLanguage.value = finalLanguage;

          // Actualizar localStorage para mantener consistencia
          localStorage.setItem('selected_language_id', selectedLanguage.value.toString());

          // IMPORTANTE: Forzar actualización del editor con el código correcto
          nextTick(() => {
            if (editorRef.value && newExercise.codigo) {
              console.log('🔄 FORZANDO actualización del editor con código del ejercicio');
              editorRef.value.setContent(newExercise.codigo);
            }
          });

          return;
        }

        // MODO NORMAL: cargar lenguaje guardado para este ejercicio
        const userId = getCurrentUserId();
        const evaluationData = localStorage.getItem('currentEvaluation')
          ? JSON.parse(localStorage.getItem('currentEvaluation'))
          : null;
        const evaluationId = evaluationData?.id || 'unknown';

        const languageKey = `exercise_language_${userId}_${evaluationId}_${newExercise.id}`;
        const savedLanguage = localStorage.getItem(languageKey);

        if (savedLanguage) {
          const langId = parseInt(savedLanguage);
          console.log(`Cambiando automáticamente al lenguaje ${langId} para ejercicio ${newExercise.id}`);
          selectedLanguage.value = langId;
          localStorage.setItem('selected_language_id', langId.toString());
        } else {
          console.log(`No hay lenguaje guardado para ejercicio ${newExercise.id}, manteniendo: ${selectedLanguage.value}`);
        }
      }
    }, { immediate: false });


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
      isDevelopment,
      availableLanguages,
      selectedLanguage,
      isLanguageSelectorEnabled,
      changeLanguage,
      getLanguageName,
      testCooldown,
      formatCooldownTime,
      handleTestCooldownClick,
    };
  }
};
</script>

<style>
/* =================== ESTILOS GLOBALES Y OVERRIDES =================== */
.right-panel-wrapper button {
  margin: 0;
  cursor: pointer;
  transition: all var(--transition-fast);
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

body.overflow-hidden {
  overflow: hidden;
}
</style>

<style scoped>
/* =================== CONTENEDOR PRINCIPAL =================== */
.right-panel-wrapper {
  height: 100%;
  display: flex;
  flex-direction: column;
  background-color: var(--color-bg-main);
  width: 50%;
  flex: 0 0 50%;
  max-width: 50%;
}

.right-panel-wrapper.is-full-screen {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  z-index: 9999;
  background-color: var(--color-bg-main);
  width: 100%;
  flex: none;
  max-width: 100%;
}

.right-panel-wrapper.history-mode {
  border-top: 4px solid var(--color-accent-blue);
  position: relative;
}

.right-panel-wrapper.history-mode::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  pointer-events: none;
  background: linear-gradient(to bottom, rgba(76, 76, 255, 0.05), transparent 10%);
  z-index: 1;
}

.practical-right-panel {
  display: flex;
  flex-direction: column;
  height: 100%;
  position: relative;
}

/* =================== HEADER DEL PANEL =================== */
.panel-header {
  background-color: var(--color-bg-element);
  padding: 10px 16px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  height: 50px;
  border-bottom: 1px solid var(--color-border);
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
  color: var(--color-primary);
}

.header-title h3 {
  font-size: 16px;
  color: var(--color-text-primary);
}

/* =================== BOTONES DE EXPANSIÓN =================== */
.expand-button {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 34px;
  height: 34px;
  border-radius: var(--border-radius);
  background-color: var(--color-bg-element-hover);
  color: var(--color-text-secondary);
  transition: all var(--transition-smooth);
  z-index: 10000;
}

.expand-button:hover {
  background-color: var(--color-bg-element-active);
  transform: scale(1.05);
  color: var(--color-text-primary);
}

.expand-button-fixed {
  position: fixed;
  top: 15px;
  right: 15px;
  width: 34px;
  height: 34px;
  border-radius: var(--border-radius);
  background-color: var(--color-bg-element-hover);
  color: var(--color-text-secondary);
  border: none;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  transition: all var(--transition-smooth);
  z-index: 10000;
  box-shadow: var(--shadow-lg);
}

.expand-button-fixed:hover {
  background-color: var(--color-bg-lighter);
  transform: scale(1.05);
}

/* =================== CONTENEDOR DEL EDITOR =================== */
.editor-container {
  flex: 1;
  overflow: hidden;
  margin: 10px;
  border-radius: var(--border-radius);
  background-color: var(--color-bg-element);
  box-shadow: var(--shadow-sm);
}

.is-full-screen .editor-container {
  margin: 0;
  border-radius: 0;
  height: calc(100% - 50px);
}

/* =================== FOOTER DEL PANEL =================== */
.panel-footer {
  background-color: var(--color-bg-element);
  padding: 8px 16px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  height: 64px;
  border-top: 1px solid var(--color-border);
}

.panel-footer.is-hidden {
  display: none;
}

/* =================== BOTONES AUXILIARES =================== */
.helper-buttons {
  display: flex;
  gap: 8px;
}

.helper-button {
  background-color: var(--color-bg-element-hover);
  border-radius: var(--border-radius);
  padding: 8px 12px;
  display: flex;
  align-items: center;
  gap: 6px;
  color: var(--color-text-secondary);
  font-size: 14px;
  font-weight: 500;
  border: 1px solid var(--color-border-light);
  transition: all var(--transition-smooth);
}

.helper-button:hover:not(:disabled) {
  background-color: var(--color-bg-element-active);
  color: var(--color-text-primary);
  box-shadow: var(--shadow-sm);
  border-color: var(--color-border-hover);
}

.helper-button:disabled,
.action-button:disabled {
  opacity: 0.6 !important;
  cursor: not-allowed !important;
  background-color: var(--color-bg-element) !important;
  transform: none !important;
  box-shadow: none !important;
  border-color: var(--color-bg-element) !important;
  color: var(--color-text-disabled) !important;
}

.helper-icon {
  font-size: 16px;
}

/* =================== BOTONES DE ACCIÓN =================== */
.action-buttons {
  display: flex;
  gap: 12px;
}

.action-button {
  padding: 8px 12px;
  border-radius: var(--border-radius);
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
  transition: all var(--transition-smooth);
}

.action-button:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.button-icon {
  font-size: 16px;
}

/* Botón TEST */
.test-button {
  background-color: var(--color-btn-test);
  color: var(--color-text-primary);
  border-color: var(--color-btn-test-border);
}

.test-button:hover:not(:disabled) {
  background-color: var(--color-btn-test-hover);
  box-shadow: var(--shadow);
}

.test-button:disabled:not(.is-loading) {
  background-color: var(--color-btn-test-success);
  color: white;
  border-color: var(--color-btn-test-success);
}

.test-button.cooldown-active {
  background-color: var(--color-btn-cooldown) !important;
  border-color: var(--color-btn-cooldown-border) !important;
  color: var(--color-btn-cooldown-text) !important;
  cursor: not-allowed !important;
  opacity: 0.8 !important;
}

.test-button.cooldown-active:hover {
  background-color: var(--color-btn-cooldown) !important;
  transform: none !important;
}

.test-button.cooldown-active .button-icon {
  animation: none !important;
}

/* Botón ENVIAR */
.submit-button {
  background-color: var(--color-btn-submit);
  color: var(--color-text-primary);
  border-color: var(--color-btn-submit-border);
}

.submit-button:hover:not(:disabled) {
  background-color: var(--color-btn-submit-hover);
  box-shadow: var(--shadow);
}

/* =================== MODALES =================== */
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
  animation: fadeIn var(--transition-fast) ease-out;
}

.modal-card {
  background-color: var(--color-bg-element);
  border-radius: var(--border-radius);
  width: 90%;
  max-width: 450px;
  box-shadow: var(--shadow-xl);
  animation: slideIn var(--transition-smooth) ease-out;
}

.modal-header {
  background-color: var(--color-primary);
  color: var(--color-bg-main);
  padding: 16px 20px;
  border-top-left-radius: var(--border-radius);
  border-top-right-radius: var(--border-radius);
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
  color: var(--color-bg-main);
  cursor: pointer;
  width: 30px;
  height: 30px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 50%;
  transition: all var(--transition-fast);
}

.modal-close:hover {
  background-color: rgba(0, 0, 0, 0.1);
}

.modal-body {
  padding: 20px;
  color: var(--color-text-primary);
}

.modal-body p {
  line-height: 1.6;
  margin-bottom: 16px;
}

.modal-body .warning-message {
  background-color: var(--color-warning-bg);
  border-left: 4px solid var(--color-warning);
  padding: 12px 16px;
  border-radius: var(--border-radius-sm);
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 16px;
}

.modal-body .success-message {
  background-color: var(--color-success-bg);
  border-left: 4px solid var(--color-success);
  padding: 12px 16px;
  border-radius: var(--border-radius-sm);
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 16px;
}

.warning-icon,
.success-icon {
  font-size: 20px;
}

.modal-footer {
  padding: 16px 20px;
  display: flex;
  justify-content: center;
  gap: 16px;
  border-top: 1px solid var(--color-border);
}

.modal-button {
  padding: 12px 24px;
  border-radius: var(--border-radius);
  font-weight: 600;
  font-size: 14px;
  min-width: 120px;
  transition: all var(--transition-smooth);
  background-color: var(--color-primary);
  color: var(--color-bg-main);
  border: 2px solid var(--color-primary);
  box-shadow: var(--shadow);
  cursor: pointer;
}

.modal-button:hover {
  background-color: var(--color-primary-light);
  border-color: var(--color-primary-light);
  transform: translateY(-2px);
  box-shadow: var(--shadow-lg);
}

.modal-button:active {
  transform: translateY(0);
  box-shadow: var(--shadow);
}

.modal-button:focus {
  outline: none;
  box-shadow: 0 0 0 3px rgba(235, 179, 0, 0.3);
}

.cancel-button {
  background-color: var(--color-bg-element-hover);
  color: var(--color-text-primary);
  border: 1px solid var(--color-border-light);
}

.cancel-button:hover {
  background-color: var(--color-bg-element-active);
}

.confirm-button {
  background-color: var(--color-primary);
  color: var(--color-bg-main);
  border: none;
}

.confirm-button:hover {
  background-color: var(--color-primary-light);
  box-shadow: var(--shadow-lg);
}

/* =================== SELECTORES =================== */
.theme-selector {
  margin-right: 10px;
  margin-left: auto;
  position: relative;
}

.theme-select {
  background-color: var(--color-bg-element-hover);
  color: var(--color-text-secondary);
  border: 1px solid var(--color-border-light);
  border-radius: var(--border-radius);
  padding: 6px 10px;
  font-size: 14px;
  appearance: none;
  padding-right: 28px;
  cursor: pointer;
  transition: all var(--transition-smooth);
}

.theme-select:hover:not(:disabled) {
  background-color: var(--color-bg-element-active);
  color: var(--color-text-primary);
}

.theme-select:focus {
  outline: none;
  box-shadow: 0 0 0 2px rgba(235, 179, 0, 0.3);
}

.theme-select:disabled {
  opacity: 0.8;
  cursor: not-allowed;
}

.theme-selector::after {
  content: "▼";
  font-size: 10px;
  color: var(--color-text-secondary);
  position: absolute;
  right: 10px;
  top: 50%;
  transform: translateY(-50%);
  pointer-events: none;
}

.language-selector {
  display: flex;
  align-items: center;
  margin-right: 10px;
  position: relative;
}

.language-select {
  background-color: var(--color-bg-element-hover);
  color: var(--color-text-secondary);
  border: 1px solid var(--color-border-light);
  border-radius: var(--border-radius);
  padding: 6px 10px;
  font-size: 14px;
  appearance: none;
  padding-right: 28px;
  cursor: pointer;
  transition: all var(--transition-smooth);
  min-width: 150px;
  max-width: 200px;
}

.language-select:hover:not(:disabled) {
  background-color: var(--color-bg-element-active);
  color: var(--color-text-primary);
  border-color: var(--color-primary);
}

.language-select:focus {
  outline: none;
  box-shadow: 0 0 0 2px rgba(235, 179, 0, 0.3);
  border-color: var(--color-primary);
}

.language-selector::after {
  content: "▼";
  font-size: 10px;
  color: var(--color-text-secondary);
  position: absolute;
  right: 10px;
  top: 50%;
  transform: translateY(-50%);
  pointer-events: none;
}

.language-count {
  font-size: 12px;
  color: var(--color-text-muted);
  margin-left: 5px;
}

.language-selector-debug {
  display: flex;
  align-items: center;
  margin-right: 10px;
  font-size: 14px;
  color: var(--color-text-muted);
}

.language-indicator {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 6px 12px;
  background-color: rgba(76, 76, 255, 0.1);
  border: 1px solid var(--color-accent-blue);
  border-radius: var(--border-radius);
  font-size: 14px;
  margin-right: 5px;
}

.language-label {
  color: var(--color-text-muted);
  font-weight: 500;
}

.language-name {
  color: var(--color-accent-blue);
  font-weight: 600;
}

/* =================== INDICADORES ESPECIALES =================== */
.history-mode-indicator {
  position: absolute;
  top: 60px;
  right: 20px;
  background-color: rgba(0, 0, 0, 0.7);
  color: var(--color-primary-light);
  padding: 8px 12px;
  border-radius: var(--border-radius);
  display: flex;
  align-items: center;
  gap: 8px;
  z-index: 999;
  box-shadow: var(--shadow-lg);
  pointer-events: none;
  animation: fadeInDown 0.5s ease-out;
  border: 1px solid var(--color-accent-blue);
}

.mode-icon {
  font-size: 18px;
}

.mode-text {
  font-size: 14px;
  font-weight: 500;
}

/* =================== ANIMACIONES DE CARGA =================== */
.button-icon.rotating {
  display: inline-block;
  animation: rotate 1.2s linear infinite;
}

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

/* =================== KEYFRAMES =================== */
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

@keyframes rotate {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
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

/* =================== MEDIA QUERIES =================== */
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

  .helper-text,
  .action-text {
    display: none;
  }

  .helper-button,
  .action-button {
    padding: 8px;
    width: 36px;
    height: 36px;
    justify-content: center;
  }

  .modal-card {
    width: 95%;
  }

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

  .language-select {
    width: 100px;
    font-size: 12px;
    min-width: auto;
  }

  .language-selector {
    margin-right: 5px;
  }

  .language-count {
    display: none;
  }

  .loading-dots {
    height: 16px;
  }

  .loading-dots .dot {
    width: 4px;
    height: 4px;
  }
}

@media (min-width: 769px) {
  .right-panel-wrapper {
    width: 50%;
    flex: 0 0 50%;
    max-width: 50%;
  }
}

span {
  font-weight: bold;
}
</style>