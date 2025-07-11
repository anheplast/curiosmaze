<!-- components/EditorCodemirror.vue -->
<template>
  <div ref="editorContainer" 
       class="editor-wrapper"
       :class="{ 'is-full-screen': isFullScreen, 'read-only': readOnly }"
       @click="focusEditorIfNotReadOnly">
    
    <!-- Icono flotante para guardado automático -->
    <div class="save-icon" v-if="showSaveNotification">
      <span class="save-icon-symbol">💾</span>
    </div>

    <!-- Indicador de modo solo lectura -->
    <div v-if="readOnly" class="read-only-indicator">
      <span class="read-only-icon">🔒</span>
      <span class="read-only-text">Solo lectura</span>
    </div>
  </div>
</template>

<script>
import { ref, onMounted, onBeforeUnmount, inject, watch, nextTick, computed } from 'vue';
import { EditorView, basicSetup } from 'codemirror';
import { EditorState } from '@codemirror/state';

// Importar extensiones de lenguajes
import { python } from '@codemirror/lang-python';
import { javascript } from '@codemirror/lang-javascript';
import { java } from '@codemirror/lang-java';
import { cpp } from '@codemirror/lang-cpp';
import { rust } from '@codemirror/lang-rust';
import { go } from '@codemirror/lang-go';
import { sql } from '@codemirror/lang-sql';
import { php } from '@codemirror/lang-php';

import { autocompletion } from '@codemirror/autocomplete';
import { indentWithTab } from '@codemirror/commands';
import { bracketMatching } from '@codemirror/language';
import { highlightSelectionMatches } from '@codemirror/search';
import { keymap } from '@codemirror/view';
import { indentUnit } from '@codemirror/language';

// Importar temas
import { dracula } from '@uiw/codemirror-theme-dracula';
import { materialDark } from '@uiw/codemirror-theme-material';
import { nord } from '@uiw/codemirror-theme-nord';
import { solarizedDark } from '@uiw/codemirror-theme-solarized';
import { tokyoNight } from '@uiw/codemirror-theme-tokyo-night';
import { vscodeDark } from '@uiw/codemirror-theme-vscode';
import { oneDark } from '@codemirror/theme-one-dark';

// Mapeo de temas disponibles
const themes = {
  dracula: dracula,
  material: materialDark,
  nord: nord,
  solarized: solarizedDark,
  tokyo: tokyoNight,
  vscode: vscodeDark,
  onedark: oneDark
};

// NUEVO: Mapeo de lenguajes Judge0 ID -> CodeMirror extension
const languageMap = {
  // Python
  70: python, // Python 2.7.17
  71: python, // Python 3.8.1
  
  // JavaScript/TypeScript
  63: javascript, // JavaScript (Node.js 12.14.0)
  74: javascript, // TypeScript (3.7.4)
  
  // Java
  62: java, // Java (OpenJDK 13.0.1)
  
  // C/C++
  50: cpp, // C (GCC 9.2.0)
  48: cpp, // C (GCC 7.4.0)
  49: cpp, // C (GCC 8.3.0)
  75: cpp, // C (Clang 7.0.1)
  54: cpp, // C++ (GCC 9.2.0)
  52: cpp, // C++ (GCC 7.4.0)
  53: cpp, // C++ (GCC 8.3.0)
  76: cpp, // C++ (Clang 7.0.1)
  
  // Rust
  73: rust, // Rust (1.40.0)
  
  // Go
  60: go, // Go (1.13.5)
  
  // SQL
  82: sql, // SQL (SQLite 3.27.2)
  
  // PHP
  68: php, // PHP (7.4.1)
};


const getLanguageName = (langId) => {
  const parsedId = parseInt(langId);

  // Mapa de IDs a nombres de lenguaje
  const languageNames = {
    71: 'Python 3',
    70: 'Python 2',
    63: 'JavaScript',
    62: 'Java',
    54: 'C++',
    53: 'C++ (GCC 8.3.0)',
    52: 'C++ (GCC 7.4.0)',
    50: 'C',
    49: 'C (GCC 8.3.0)',
    48: 'C (GCC 7.4.0)',
    74: 'TypeScript',
    73: 'Rust',
    60: 'Go',
    68: 'PHP'
  };

  // Intentar obtener desde availableLanguages si existe
  if (availableLanguages.value && availableLanguages.value.length > 0) {
    const lang = availableLanguages.value.find(l => l.id === parsedId);
    if (lang) return lang.name;
  }

  // Sino, usar el mapa predefinido
  return languageNames[parsedId] || `Lenguaje ID ${parsedId}`;
};

// Función para obtener la extensión de lenguaje
const getLanguageExtension = (languageId) => {
  const langFunc = languageMap[languageId];
  if (langFunc) {
    return langFunc();
  }
  // Por defecto, usar Python si no se encuentra el lenguaje
  return python();
};

export default {
  name: 'CodeMirrorEditor',
  props: {
    isFullScreen: {
      type: Boolean,
      default: false
    },
    theme: {
      type: String,
      default: 'dracula',
      validator: (value) => Object.keys(themes).includes(value)
    },
    readOnly: {
      type: Boolean,
      default: false
    }
  },
  setup(props, { expose }) {
    // Estado del editor
    const editorInitialized = ref(false);
    const editorContainer = ref(null);
    const editor = ref(null);
    const content = ref('# Cargando código...');
    const showSaveNotification = ref(false);
    const saveTimeoutId = ref(null);
    const lastSaveTime = ref(0);

    const editorInstance = ref(null);
    
    // Estado para el lenguaje actual
    const currentLanguageId = ref(71); // Python por defecto

    const getLanguageName = (langId) => {
      const parsedId = parseInt(langId);

      // Mapa de IDs a nombres de lenguaje
      const languageNames = {
        71: 'Python 3',
        70: 'Python 2',
        63: 'JavaScript',
        62: 'Java',
        54: 'C++',
        53: 'C++ (GCC 8.3.0)',
        52: 'C++ (GCC 7.4.0)',
        50: 'C',
        49: 'C (GCC 8.3.0)',
        48: 'C (GCC 7.4.0)',
        74: 'TypeScript',
        73: 'Rust',
        60: 'Go',
        68: 'PHP'
      };

      // Intentar obtener desde availableLanguages si existe
      if (availableLanguages.value && availableLanguages.value.length > 0) {
        const lang = availableLanguages.value.find(l => l.id === parsedId);
        if (lang) return lang.name;
      }

      // Sino, usar el mapa predefinido
      return languageNames[parsedId] || `Lenguaje ID ${parsedId}`;
    };

    
    
    // Obtener contexto de ejercicios
    const exercises = inject('exercises', ref([]));
    const currentExerciseIndex = inject('currentExerciseIndex', ref(0));
    const isHistoryMode = inject('isHistoryMode', ref(false));
    
    // Computar el ejercicio actual
    const currentExercise = ref(null);
    
    // NUEVO: Función para cargar el lenguaje seleccionado desde localStorage
    const loadSelectedLanguage = () => {
      try {
        const savedLanguage = localStorage.getItem('selected_language_id');
        if (savedLanguage) {
          const langId = parseInt(savedLanguage);
          if (langId && langId !== currentLanguageId.value) {
            console.log(`Cargando lenguaje desde localStorage: ID ${langId}`);
            currentLanguageId.value = langId;
            return true;
          }
        }
      } catch (e) {
        console.warn('Error al cargar lenguaje desde localStorage:', e);
      }
      return false;
    };

    // Watcher para detectar cambios en el lenguaje seleccionado
    const watchLanguageChanges = () => {
      // Polling para detectar cambios en localStorage
      const checkLanguageChange = () => {
        try {
          if (isHistoryMode.value) {
            return;
          }

          const savedLanguage = localStorage.getItem('selected_language_id');
          if (savedLanguage) {
            const langId = parseInt(savedLanguage);
            if (langId && langId !== currentLanguageId.value) {
              console.log(`Cambio de lenguaje detectado: ${currentLanguageId.value} -> ${langId}`);
              currentLanguageId.value = langId;

              // Recrear editor con nuevo lenguaje
              if (editor.value && editorInitialized.value) {
                const currentContent = editor.value.state.doc.toString();

                // Importante: Si el contenido es una plantilla por defecto o está vacío,
                // cargar la plantilla específica para el nuevo lenguaje
                const isDefaultTemplate = isDefaultTemplateContent(currentContent);

                if (isDefaultTemplate) {
                  console.log("Detectada plantilla por defecto, cargando plantilla para nuevo lenguaje");
                  nextTick(() => {
                    if (currentExercise.value) {
                      loadCodeFromLocalStorage(currentExercise.value.id);
                    } else {
                      recreateEditor(currentContent);
                    }
                  });
                } else {
                  nextTick(() => {
                    recreateEditor(currentContent);
                  });
                }
              }
            }
          }
        } catch (e) {
          console.warn('Error al verificar cambio de lenguaje:', e);
        }
      };

      // Verificar cada 500ms
      const languageInterval = setInterval(checkLanguageChange, 500);

      // Limpiar al desmontar
      onBeforeUnmount(() => {
        clearInterval(languageInterval);
      });
    };
    
    // Verificar el modo historia para decidir si guardar o no
    const shouldSaveCode = computed(() => {
      return !props.readOnly && !isHistoryMode.value;
    });

    // Obtener clave consistente para guardar código
    const getExerciseCodeKey = (exerciseId) => {
      const userId = localStorage.getItem('user_id') || 'anonymous';
      const evalData = localStorage.getItem('currentEvaluation');
      let evaluationId = 'unknown';

      try {
        const parsedEvaluation = JSON.parse(evalData);  // Cambiado de 'eval' a 'parsedEvaluation'
        evaluationId = parsedEvaluation?.id || 'unknown';
      } catch (e) {
        console.warn('Error al parsear evaluación de localStorage');
      }

      return `exercise_code_${userId}_${evaluationId}_${exerciseId}`;
    };

    // Guardar código en localStorage
    const saveCodeToLocalStorage = (exerciseId = null) => {
      // Si estamos en modo solo lectura, no guardamos
      if (props.readOnly || isHistoryMode.value) {
        console.log('No se guarda código en modo solo lectura');
        return false;
      }

      const id = exerciseId || (currentExercise.value?.id);
      if (!id) return false;

      try {
        // Obtener el código actual del editor
        const currentCode = editor.value && editorInitialized.value
          ? editor.value.state.doc.toString()
          : content.value;

        // Usar la clave consistente con PracticalRightPanel
        const codeKey = getExerciseCodeKey(id);
        console.log('Guardando código con clave:', codeKey);
        localStorage.setItem(codeKey, currentCode);

        // NUEVO: Guardar también el lenguaje seleccionado para este ejercicio
        const languageKey = `exercise_language_${getCurrentUserId()}_${getEvaluationId()}_${id}`;
        localStorage.setItem(languageKey, currentLanguageId.value.toString());
        console.log(`Guardado lenguaje ${currentLanguageId.value} para ejercicio ${id}`);

        // Mostrar icono de guardado
        showSaveNotification.value = true;
        if (saveTimeoutId.value) clearTimeout(saveTimeoutId.value);
        saveTimeoutId.value = setTimeout(() => {
          showSaveNotification.value = false;
        }, 1000);

        return true;
      } catch (error) {
        console.error('Error al guardar código:', error);
        return false;
      }
    };
    
    // Mostrar icono de guardado brevemente
    const showSaveIcon = () => {
      // No mostrar icono en modo solo lectura
      if (props.readOnly || isHistoryMode.value) return;

      showSaveNotification.value = true;
      
      // Limpiar timeout anterior si existe
      if (saveTimeoutId.value) {
        clearTimeout(saveTimeoutId.value);
      }
      
      // Ocultar después de 1 segundo
      saveTimeoutId.value = setTimeout(() => {
        showSaveNotification.value = false;
      }, 1000);
    };
    
    // Cargar código desde localStorage 
    const loadCodeFromLocalStorage = (exerciseId = null) => {
      const id = exerciseId || currentExercise.value?.id;
      if (!id) return false;

      try {
        // EN MODO HISTORIAL: usar el código directamente del ejercicio
        if (isHistoryMode.value && currentExercise.value && currentExercise.value.codigo) {
          console.log('📚 Modo historial: cargando código desde ejercicio');
          setContent(currentExercise.value.codigo);
          return true;
        }

        // MODO NORMAL: usar localStorage
        const codeKey = getExerciseCodeKey(id);
        console.log('Buscando código con clave:', codeKey);
        const savedCode = localStorage.getItem(codeKey);

        // Cargar lenguaje guardado para este ejercicio (solo si NO es modo historial)
        if (!isHistoryMode.value) {
          const languageKey = `exercise_language_${getCurrentUserId()}_${getEvaluationId()}_${id}`;
          const savedLanguage = localStorage.getItem(languageKey);

          if (savedLanguage) {
            const langId = parseInt(savedLanguage);
            console.log(`Cargando lenguaje guardado para ejercicio ${id}: ${langId}`);

            // Actualizar lenguaje actual y localStorage general
            currentLanguageId.value = langId;
            localStorage.setItem('selected_language_id', langId.toString());
          } else {
            console.log(`No hay lenguaje guardado para ejercicio ${id}, manteniendo actual: ${currentLanguageId.value}`);
          }
        }

        if (savedCode) {
          console.log('Código encontrado:', savedCode.length, 'caracteres');
          setContent(savedCode);
          return true;
        }

        // Si no hay código guardado Y NO estamos en modo historial, buscar plantilla
        if (!isHistoryMode.value && currentExercise.value) {
          let template = '';
          let templateFound = false;

          console.log('Ejercicio actual:', currentExercise.value);
          console.log('Estructura del ejercicio:', Object.keys(currentExercise.value));

          // Buscar en templates_por_lenguaje directamente en el ejercicio
          if (!templateFound && currentExercise.value.templates_por_lenguaje) {
            const langIdStr = String(currentLanguageId.value);

            console.log('Buscando en templates_por_lenguaje del ejercicio');
            console.log('Templates disponibles:', currentExercise.value.templates_por_lenguaje);

            if (currentExercise.value.templates_por_lenguaje[langIdStr]) {
              template = currentExercise.value.templates_por_lenguaje[langIdStr];
              templateFound = true;
              console.log(`Plantilla encontrada en templates_por_lenguaje para lenguaje ID ${currentLanguageId.value}`);
            }
          }

          // Si no se encontró en templates_por_lenguaje, buscar en contenido.templates
          if (!templateFound && currentExercise.value.contenido) {
            const contenido = typeof currentExercise.value.contenido === 'object'
              ? currentExercise.value.contenido
              : {};

            console.log('Buscando en contenido.templates');

            if (contenido.templates && typeof contenido.templates === 'object') {
              const langIdStr = String(currentLanguageId.value);

              if (contenido.templates[langIdStr]) {
                template = contenido.templates[langIdStr];
                templateFound = true;
                console.log(`Plantilla específica para lenguaje ID ${currentLanguageId.value} encontrada en contenido.templates`);
              }
            }
          }

          // Si no se encuentra ninguna plantilla, generar por defecto según el lenguaje
          if (!templateFound) {
            template = generateDefaultTemplate(currentExercise.value);
            console.log('Usando plantilla por defecto generada');
          }

          // Establecer la plantilla
          setContent(template);

          // Guardar como código inicial, solo si no es modo solo lectura
          if (!props.readOnly && !isHistoryMode.value) {
            saveCodeToLocalStorage(id);
          }
          return true;
        }

        return false;
      } catch (error) {
        console.error('Error al cargar código:', error);
        return false;
      }
    };
    
    // Extraer plantilla del ejercicio
    const extractTemplate = (exercise) => {
      // Buscar template en diferentes lugares
      if (exercise.template && exercise.template.trim() !== '') {
        return exercise.template;
      } else if (exercise.contenido) {
        if (typeof exercise.contenido === 'object') {
          if (exercise.contenido.template && exercise.contenido.template.trim() !== '') {
            return exercise.contenido.template;
          }
        } else if (typeof exercise.contenido === 'string') {
          try {
            const parsed = JSON.parse(exercise.contenido);
            if (parsed.template && parsed.template.trim() !== '') {
              return parsed.template;
            }
          } catch (e) {
            console.warn('Error al parsear contenido:', e);
          }
        }
      }
    
      // Si no se encuentra plantilla, generar una por defecto
      return generateDefaultTemplate(exercise);
    };
    
    // Generar una plantilla por defecto
    const generateDefaultTemplate = (exercise) => {
      // Para cualquier lenguaje (incluido Python) solo mostrar un mensaje informativo
      const langName = getLanguageName(currentLanguageId.value);
      return `# No hay plantilla específica para ${langName} en este ejercicio\n# Por favor, implementa tu solución aquí`;
    };

    // Función auxiliar para detectar si el contenido es una plantilla por defecto
    const isDefaultTemplateContent = (content) => {
      if (!content || content.trim() === '') return true;

      // Patrones que indican plantillas por defecto
      const defaultPatterns = [
        /No hay plantilla específica para .* en este ejercicio/,
        /Por favor, implementa tu solución aquí/,
        /Tu código aquí/,
        /print\("Hello, World!"\)/
      ];

      return defaultPatterns.some(pattern => pattern.test(content));
    };

    // Métodos para manipular el editor
    const setContent = (newContent) => {
      if (!newContent) {
        console.warn('Contenido vacío, usando valor por defecto');
        newContent = '# Tu código aquí\n';
      }

      // Actualizar estado local
      content.value = newContent;
      console.log(`Estableciendo contenido (${newContent.length} caracteres)`);

      // Si el editor está inicializado, actualizar
      if (editor.value && editorInitialized.value) {
        try {
          // Debounce para evitar actualizaciones frecuentes
          if (window._editorUpdateTimeout) {
            clearTimeout(window._editorUpdateTimeout);
          }
          
          window._editorUpdateTimeout = setTimeout(() => {
            recreateEditor(newContent);
          }, 100);
        } catch (error) {
          console.error('Error al actualizar contenido:', error);
          nextTick(() => recreateEditor(newContent));
        }
      }
    };

    // Recrear editor con el contenido actual
    const recreateEditor = (contentToSet) => {
      if (!editorContainer.value) {
        console.error('Contenedor del editor no disponible');
        return;
      }
      
      try {
        console.log('Recreando editor...');
        
        // Destruir editor existente si hay uno
        if (editor.value) {
          editor.value.destroy();
        }

        // Crear nuevo estado con tema actual
        const startState = EditorState.create({
          doc: contentToSet,
          extensions: createEditorExtensions()
        });

        // Crear nuevo editor
        editor.value = new EditorView({
          state: startState,
          parent: editorContainer.value
        });

        // Marcar como inicializado
        editorInitialized.value = true;
        console.log('Editor recreado con éxito');
        console.log('Modo solo lectura:', props.readOnly);
      } catch (e) {
        console.error('Error al recrear editor:', e);
      }
    };

    // Obtener contenido actual
    const getContent = () => {
      if (editor.value && editorInitialized.value) {
        return editor.value.state.doc.toString();
      }
      return content.value;
    };

    // Enfocar el editor solo si no es de solo lectura
    const focusEditorIfNotReadOnly = () => {
      // No hacer nada si está en modo solo lectura - permite que el scroll funcione naturalmente
      if (props.readOnly || isHistoryMode.value) {
        return;
      }
      if (editor.value) {
        editor.value.focus();
      }
    };

    // Enfocar el editor
    const focusEditor = () => {
      if (!props.readOnly && !isHistoryMode.value && editor.value) {
        editor.value.focus();
      }
    };

    // MODIFICAR: Función createEditorExtensions para usar el lenguaje dinámico
    const createEditorExtensions = () => {
      // Obtener el tema seleccionado
      const themeExtension = themes[props.theme] || dracula;
      
      // NUEVO: Obtener extensión de lenguaje basada en ID actual
      const languageExtension = getLanguageExtension(currentLanguageId.value);
      
      console.log(`Creando editor con lenguaje ID: ${currentLanguageId.value}`);
      
      const extensions = [
        basicSetup,
        languageExtension, // CAMBIADO: usar extensión dinámica en lugar de python()
        themeExtension,
        autocompletion(),
        keymap.of([indentWithTab]),
        bracketMatching(),
        highlightSelectionMatches({
          highlightWordAroundCursor: true,
          minSelectionLength: 1,
          wholeWords: true
        }),
        indentUnit.of('    '),
        EditorView.lineWrapping,
        // Estado de solo lectura basado en prop o modo historia
        EditorView.editable.of(!(props.readOnly || isHistoryMode.value)),
        EditorView.theme({
          "&": {
            fontSize: "14px",
            height: "100%",
            width: "100%",
            fontFamily: "'Fira Code', 'Consolas', monospace"
          },
          ".cm-editor": {
            height: "100%",
            width: "100%",
            outline: "none"
          },
          ".cm-content": {
            height: "100%",
            padding: "10px"
          },
          ".cm-line": {
            padding: "0 5px",
            lineHeight: "1.6",
          },
          // Mejorar visibilidad del cursor
          ".cm-cursor": {
            borderLeftWidth: "2px",
            borderLeftColor: "#ffffff",
            borderRadius: "1px"
          },
          // Mejorar visibilidad de la selección
          ".cm-selectionBackground": {
            backgroundColor: "rgba(138, 79, 255, 0.4) !important",
            borderRadius: "2px"
          },
          // Mejorar visibilidad de parejas de corchetes
          ".cm-matchingBracket": {
            backgroundColor: "rgba(255, 153, 51, 0.3) !important",
            color: "#FFFFFF !important",
            outline: "1px solid #FF9933 !important"
          }
        }),
        EditorView.updateListener.of(update => {
          if (update.docChanged && !props.readOnly && !isHistoryMode.value) {
            // Actualizar contenido cuando cambie (solo si no es solo lectura)
            content.value = update.state.doc.toString();
            // Guardar cambios con debounce
            debouncedSave();
          }
        })
      ];
      return extensions;
    };

    // Debounce para guardar código
    let saveTimeout = null;
    const debouncedSave = () => {
      // No guardar en modo solo lectura
      if (props.readOnly || isHistoryMode.value) return;

      if (saveTimeout) clearTimeout(saveTimeout);
      saveTimeout = setTimeout(() => {
        saveCodeToLocalStorage(currentExercise.value?.id);
      }, 1000); // Reducido a 1 segundo
    };

    // Watcher para cambios en el lenguaje actual
    watch(currentLanguageId, (newLangId, oldLangId) => {
      console.log(`Lenguaje cambió de ${oldLangId} a ${newLangId}`);

      if (editor.value && editorInitialized.value && newLangId !== oldLangId) {
        // Verificar si hay código ya guardado para este lenguaje
        const exerciseId = currentExercise.value?.id;
        if (exerciseId) {
          const codeKey = getExerciseCodeKey(exerciseId);
          const savedCode = localStorage.getItem(codeKey);

          if (!savedCode && !props.readOnly && !isHistoryMode.value) {
            // Si no hay código guardado, cargar la plantilla para el nuevo lenguaje
            loadCodeFromLocalStorage(exerciseId);
          } else {
            // Si hay código guardado o estamos en modo solo lectura, solo actualizamos el editor
            const currentContent = editor.value.state.doc.toString();
            nextTick(() => {
              recreateEditor(currentContent);
            });
          }
        } else {
          // Si no hay ejercicio actual, solo actualizamos el editor
          const currentContent = editor.value.state.doc.toString();
          nextTick(() => {
            recreateEditor(currentContent);
          });
        }
      }
    });

    // Actualizar ejercicio actual basado en el índice
    watch([exercises, currentExerciseIndex], ([newExercises, newIndex], [oldExercises, oldIndex]) => {
      console.log(`Cambio detectado - ejercicios: ${newExercises?.length}, índice: ${newIndex}`);
      
      if (newExercises && newExercises.length > 0 && newIndex >= 0 && newIndex < newExercises.length) {
        const oldExerciseId = currentExercise.value?.id;
        const newExercise = newExercises[newIndex];
        
        // Si cambió el ejercicio, actualizar
        if (newExercise && (!currentExercise.value || newExercise.id !== oldExerciseId)) {
          console.log(`Ejercicio cambiado de ${oldExerciseId} a ${newExercise.id}`);
          
          // Guardar código actual si hay ejercicio anterior y no es modo solo lectura
          if (oldExerciseId && editorInitialized.value && !props.readOnly && !isHistoryMode.value) {
            saveCodeToLocalStorage(oldExerciseId);
          }
          
          // Actualizar ejercicio actual
          currentExercise.value = newExercise;
          
          // Cargar código del nuevo ejercicio
          loadCodeFromLocalStorage(newExercise.id);
        }
      }
    });
    
    // Observar cambios en props.readOnly e isHistoryMode
    watch([() => props.readOnly, isHistoryMode], ([newReadOnly, newHistoryMode]) => {
      console.log(`Cambio en modo lectura: readOnly=${newReadOnly}, historyMode=${newHistoryMode}`);
      
      nextTick(() => {
        if (editor.value && editorInitialized.value) {
          // Forzar actualización del editor
          const currentContent = editor.value.state.doc.toString();

          // Debounce para evitar problemas
          if (window._readOnlyTimeout) {
            clearTimeout(window._readOnlyTimeout);
          }

          window._readOnlyTimeout = setTimeout(() => {
            // Recrear el editor para aplicar el cambio de modo lectura
            recreateEditor(currentContent);
          }, 150);
        }
      });
    });
    
    // Observar cambios de tema
    watch(() => props.theme, (newTheme) => {
      console.log(`Cambiando tema a: ${newTheme}`);
      
      if (editor.value && editorInitialized.value) {
        // Guardar el contenido actual
        const currentContent = editor.value.state.doc.toString();
        
        // Recrear el editor con el nuevo tema
        nextTick(() => {
          recreateEditor(currentContent);
        });
      }
      
      // Guardar tema en localStorage
      try {
        localStorage.setItem('editor_theme', newTheme);
      } catch (e) {
        console.warn('No se pudo guardar el tema en localStorage:', e);
      }
    });
    
    // Exponemos métodos para componentes padres
    expose({
      setContent,
      getContent,
      focusEditor,
      loadCodeFromLocalStorage,
      isInitialized: () => editorInitialized.value,
      saveCurrentCode: () => {
        // Solo guardar si no es modo solo lectura
        if (!props.readOnly && !isHistoryMode.value) {
          return saveCodeToLocalStorage(currentExercise.value?.id);
        }
        return false;
      },
      isReadOnly: () => props.readOnly || isHistoryMode.value,
      getCurrentLanguage: () => currentLanguageId.value
    });

    // MODIFICAR: onMounted para inicializar lenguaje
    onMounted(() => {
      // NUEVO: Cargar lenguaje seleccionado
      loadSelectedLanguage();
      
      // NUEVO: Inicializar watcher de cambios de lenguaje
      watchLanguageChanges();
      
      // Inicializar editor
      nextTick(() => {
        try {
          console.log("Inicializando editor...");
          console.log("Modo solo lectura:", props.readOnly || isHistoryMode.value);
          console.log("Lenguaje inicial:", currentLanguageId.value);
          
          // Crear estado inicial
          const startState = EditorState.create({
            doc: content.value,
            extensions: createEditorExtensions()
          });

          // Crear editor
          editor.value = new EditorView({
            state: startState,
            parent: editorContainer.value
          });
          
          // Marcar como inicializado
          editorInitialized.value = true;
          console.log("Editor inicializado con éxito");
          
          // Actualizar ejercicio actual
          if (exercises.value && exercises.value.length > 0) {
            const idx = currentExerciseIndex.value >= 0 ? currentExerciseIndex.value : 0;
            currentExercise.value = exercises.value[idx];
            
            // Cargar código
            if (currentExercise.value) {
              loadCodeFromLocalStorage(currentExercise.value.id);
            }
          }
        } catch (error) {
          console.error('Error al inicializar editor:', error);
        }
      });

      // Configurar guardado periódico (solo si no es modo solo lectura)
      const saveInterval = setInterval(() => {
        if (!props.readOnly && !isHistoryMode.value && currentExercise.value && currentExercise.value.id) {
          saveCodeToLocalStorage(currentExercise.value.id);
        }
      }, 30000); // Cada 30 segundos
      
      // Limpiar intervalo al desmontar
      onBeforeUnmount(() => {
        clearInterval(saveInterval);
        
        // Guardar código final (solo si no es modo solo lectura)
        if (!props.readOnly && !isHistoryMode.value && currentExercise.value && editorInitialized.value) {
          saveCodeToLocalStorage(currentExercise.value.id);
        }
        
        // Limpiar timeouts
        if (saveTimeoutId.value) {
          clearTimeout(saveTimeoutId.value);
        }
        if (saveTimeout) {
          clearTimeout(saveTimeout);
        }
        if (window._editorUpdateTimeout) {
          clearTimeout(window._editorUpdateTimeout);
        }
        if (window._fullscreenTimeout) {
          clearTimeout(window._fullscreenTimeout);
        }
        if (window._readOnlyTimeout) {
          clearTimeout(window._readOnlyTimeout);
        }
        
        // Destruir editor
        if (editor.value) {
          editor.value.destroy();
        }
      });
    });

    // Función helper para obtener ID de usuario
    const getCurrentUserId = () => {
      return localStorage.getItem('user_id') || 'anonymous';
    };

    // Función helper para obtener ID de evaluación
    const getEvaluationId = () => {
      const evalData = localStorage.getItem('currentEvaluation');
      try {
        const parsedEvaluation = JSON.parse(evalData);
        return parsedEvaluation?.id || 'unknown';
      } catch (e) {
        return 'unknown';
      }
    };

    return {
      editorContainer,
      content,
      showSaveNotification,
      focusEditorIfNotReadOnly,
      currentLanguageId,
      isDefaultTemplateContent,
      getCurrentUserId,
      getEvaluationId
    };
  }
};
</script>

<style>
/* Estilos para elementos creados dinámicamente por CodeMirror */
.editor-wrapper :deep(.cm-editor) {
  height: 100%;
  width: 100%;
  border-radius: 8px;
  overflow: hidden;
  font-family: 'Fira Code', 'Consolas', monospace;
}

.editor-wrapper :deep(.cm-scroller) {
  font-family: 'Fira Code', 'Consolas', monospace;
  height: 100%;
  overflow-y: auto;
  padding: 10px 0;
}

.editor-wrapper :deep(.cm-content) {
  padding: 0 10px;
}

.editor-wrapper :deep(.cm-line) {
  padding-left: 5px;
  font-size: 14px;
  line-height: 1.5;
}

.editor-wrapper :deep(.cm-cursor) {
  border-left: 2px solid #FFFFFF !important;
  border-radius: 1px;
  animation: blink 1.2s step-end infinite;
}

.editor-wrapper :deep(.cm-activeLine) {
  background-color: rgba(255, 255, 255, 0.05) !important;
}

/* Mejora de visibilidad de selección */
.editor-wrapper :deep(.cm-selectionBackground) {
  background-color: rgba(138, 79, 255, 0.4) !important;
  border-radius: 2px;
}

.editor-wrapper :deep(.cm-selectionMatch) {
  background-color: rgba(255, 213, 79, 0.4) !important;
  border-radius: 2px;
}

.editor-wrapper :deep(.cm-matchingBracket) {
  outline: 1px solid #FF9933 !important;
  background-color: rgba(255, 153, 51, 0.3) !important;
  color: #FFFFFF !important;
  border-radius: 2px;
}

/* Animación del cursor */
@keyframes blink {
  from { opacity: 1; }
  50% { opacity: 0; }
  to { opacity: 1; }
}
</style>

<style scoped>
.editor-wrapper {
  height: 100%;
  width: 100%;
  position: relative;
  background-color: #131414;
  border-radius: 8px;
  overflow: hidden;
}

.editor-wrapper.is-full-screen {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  z-index: 9990;
  border-radius: 0;
  padding: 20px;
  background-color: var(--color-bg-main, #1C1C21);
}

/* Icono de guardado */
.save-icon {
  position: absolute;
  top: 10px;
  right: 10px;
  z-index: 100;
  background-color: rgba(0, 0, 0, 0.6);
  width: 32px;
  height: 32px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  pointer-events: none;
  animation: fadeInOut 1s ease-in-out;
  opacity: 0.8;
}

.save-icon-symbol {
  font-size: 16px;
  color: var(--color-primary, #EBB300);
}

@keyframes fadeInOut {
  0% {
    opacity: 0;
    transform: scale(0.8);
  }
  20% {
    opacity: 0.8;
    transform: scale(1);
  }
  80% {
    opacity: 0.8;
    transform: scale(1);
  }
  100% {
    opacity: 0;
    transform: scale(0.8);
  }
}

/* Estilos para modo solo lectura */
.read-only {
  position: relative;
}

.read-only::after {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-color: rgba(0, 0, 0, 0.15); /* Overlay más notorio */
  pointer-events: none; /* permite que el scroll pase a través */
  z-index: 50; /* Mayor z-index para asegurar que está por encima */
  cursor: not-allowed; /* Cursor que indica que no se puede editar */
}

.read-only :deep(.cm-editor) {
  opacity: 0.8; /* Ligera transparencia para indicar estado inactivo */
  pointer-events: auto; /* permite interacción con el scroll */
}

.read-only :deep(.cm-content) {
  pointer-events: none; /* bloquea edición del contenido */
}

.read-only :deep(.cm-scroller) {
  pointer-events: auto; /* permite scroll */
}

.read-only :deep(.cm-cursor) {
  display: none !important; /* Ocultar el cursor completamente */
}

/* Indicador de modo solo lectura - Movido a parte inferior derecha */
.read-only-indicator {
  position: absolute;
  bottom: 10px;
  right: 10px;
  background-color: rgba(30, 30, 40, 0.8);
  color: #FF9933;
  padding: 6px 10px;
  border-radius: 6px;
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 12px;
  z-index: 60;
  box-shadow: 0 2px 5px rgba(0, 0, 0, 0.2);
  border: 1px solid rgba(255, 153, 51, 0.3);
  pointer-events: none;
}

.read-only-icon {
  font-size: 14px;
}

.read-only-text {
  font-weight: 500;
}
</style>