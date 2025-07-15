<!-- src/components/Common/resolucion-ejercicios/PracticalLeftPanel.vue -->
<template>
  <div class="left-panel-wrapper">

    <div v-if="isHistoryMode" class="history-mode-indicator">
      <span class="history-icon">🕒</span>
      <span class="history-text">Modo historial - Solo lectura</span>
    </div>

    <div class="practical-left-panel">
      <div class="left-panel-tabs">
        <div class="tabs-container">
          <button class="tab-button" :class="{ 'active': activeTab === 'instructions' }"
            @click="activeTab = 'instructions'">
            <span class="tab-icon">📝</span>
            <span class="tab-text">Instrucciones</span>
          </button>
          <button class="tab-button" :class="{ 'active': activeTab === 'output' }" @click="activeTab = 'output'">
            <span class="tab-icon">📊</span>
            <span class="tab-text">Output</span>
          </button>
        </div>
      </div>

      <div class="panel-content custom-scrollbar">
        <!-- Panel de Instrucciones -->
        <div class="instructions-panel" v-show="activeTab === 'instructions'">
          <!-- Contenido de instrucciones -->
          <div v-if="currentExercise" class="exercise-instructions">
            <div class="exercise-header">
              <h2 class="exercise-title">{{ currentExercise.titulo || 'Sin título' }}</h2>
              <span class="exercise-points">{{ currentExercise.puntaje || 10 }} pts</span>
            </div>

            <!-- Descripción del ejercicio - siempre visible -->
            <div class="section-card description-section">
              <div class="markdown-preview content-area" v-html="markdownDescription"></div>
            </div>

            <!-- Restricciones - solo visible si hay contenido -->
            <div v-if="hasRestrictions" class="section-card constraints-section">
              <h3 class="section-title">
                <span class="section-icon">⚠️</span>
                Restricciones
              </h3>
              <p class="content-area">{{ currentExercise.restricciones }}</p>
            </div>

            <!-- Formato de entrada - solo visible si hay contenido -->
            <div v-if="hasInputFormats" class="section-card input-format-section">
              <h3 class="section-title">
                <span class="section-icon">📥</span>
                Formato de entrada
              </h3>
              <ul class="input-format-list content-area">
                <li v-for="(format, idx) in currentExercise.formatos_entrada" :key="idx">
                  {{ format }}
                </li>
              </ul>
            </div>

            <!-- Formato de salida - solo visible si hay contenido -->
            <div v-if="hasOutputFormat" class="section-card output-format-section">
              <h3 class="section-title">
                <span class="section-icon">📤</span>
                Formato de salida
              </h3>
              <p class="content-area">{{ currentExercise.formato_salida }}</p>
            </div>

            <!-- Créditos/Fuente -->
            <div v-if="currentExercise && currentExercise.credito" class="section-card credits-section">
              <h3 class="section-title">
                <span class="section-icon">🔗</span>
                Créditos/Fuente
              </h3>
              <p class="content-area">{{ currentExercise.credito }}</p>
            </div>

            <!-- ETIQUETAS -->
            <div v-if="hasEtiquetas" class="tags-container">
              <div 
                v-for="(tag, index) in currentExerciseTags" 
                :key="`tag-${index}`"
                class="tag-badge"
              >
                {{ tag }}
              </div>
            </div>
          </div>

          <div v-else class="empty-state">
            <div class="empty-icon">📋</div>
            <h3>Cargando ejercicio...</h3>
            <p v-if="exercises.length === 0">No hay ejercicios disponibles para esta evaluación.</p>
          </div>
        </div>

        <!-- Panel de Output - incluye stderr -->
        <div class="output-panel" v-show="activeTab === 'output'">
          <div v-if="getTestResultsForCurrentExercise" class="output-content">
            <div class="output-header">
              <div class="output-title">
                <span class="output-icon">🖥️</span>
                Resultado de ejecución
              </div>
              <button class="clear-button" @click="clearResultsForCurrentExercise" title="Limpiar resultados">
                <svg width="18" height="18" viewBox="0 0 24 24" fill="currentColor">
                  <path
                    d="M19 6.41L17.59 5 12 10.59 6.41 5 5 6.41 10.59 12 5 17.59 6.41 19 12 13.41 17.59 19 19 17.59 13.41 12z" />
                </svg>
              </button>
            </div>

            <div class="output-body custom-scrollbar">
              <!-- Bloque principal de salida -->
              <div v-if="shouldDisplayAsText" class="output-text">
                <pre>{{ getTestResultsForCurrentExercise }}</pre>
              </div>
              
              <div v-else class="output-formatted">
                <!-- Parte normal de resultados -->
                <div v-html="formattedResults"></div>
                
                <!-- Sección de errores stderr -->
                <div v-if="hasStderr" class="stderr-section">
                  <div class="stderr-header">
                    <span class="stderr-icon">⚠️</span>
                    <span class="stderr-title">Error de ejecución (stderr)</span>
                  </div>
                  <pre class="stderr-content">{{ getStderrContent }}</pre>
                </div>
              </div>
            </div>
          </div>
          <div v-else class="empty-state">
            <div class="empty-icon">🔄</div>
            <h3>No hay resultados disponibles</h3>
            <p>Ejecute su código con el botón <strong>TEST</strong> para ver la salida.</p>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, inject, computed, onMounted, watch, onBeforeUnmount, getCurrentInstance, nextTick } from 'vue';
import { marked } from 'marked';
import DOMPurify from 'dompurify';

// Configuración para Marked v4+
const configureMarked = () => {
  const renderer = new marked.Renderer();
  
  // Destructuring del token para obtener href, title y text
  renderer.link = function ({ href, title, text }) {
    const safeHref = href || '#';
    const titleAttr = title ? ` title="${title}"` : '';
    return `<a href="${safeHref}"${titleAttr} target="_blank" rel="noopener noreferrer">${text}</a>`;
  };
  
  marked.use({ 
    renderer,
    gfm: true,
    breaks: true,
    headerIds: true,
    headerPrefix: 'heading-'
  });
};

// Caché para markdown renderizado
const markdownCache = new Map();

export default {
  name: 'PracticalLeftPanel',
  setup() {
    const instance = getCurrentInstance();
    
    const activeTab = ref('instructions');
    const exercises = inject('exercises', ref([]));
    const currentExerciseIndex = inject('currentExerciseIndex', ref(0));

    const isHistoryMode = inject('isHistoryMode', ref(false));
    
    // Guardamos los resultados por ejercicio en un Map
    // resultsMap también contiene stderr
    const resultsMap = ref(new Map());

    // Función auxiliar para parsear JSON de forma segura
    const parseJsonSafely = (jsonString) => {
      try {
        return typeof jsonString === 'string' ? JSON.parse(jsonString) : {};
      } catch (e) {
        console.error('Error al parsear JSON:', e);
        return {};
      }
    };

    // Obtener créditos del ejercicio
    const getCredits = computed(() => {
      console.log('Getting credits for:', currentExercise.value);
      console.log('credito field:', currentExercise.value?.credito);

      if (!currentExercise.value) return '';
      
      if (currentExercise.value.credito) {
        return currentExercise.value.credito;
      }
      
      if (currentExercise.value.contenido) {
        const contenido = typeof currentExercise.value.contenido === 'object'
          ? currentExercise.value.contenido
          : parseJsonSafely(currentExercise.value.contenido);
        
        return contenido.credito || '';
      }
      
      return '';
    });

    // Verificar si hay etiquetas
    const hasEtiquetas = computed(() => {
      if (!currentExercise.value) return false;

      // Verificar etiquetas directas
      if (Array.isArray(currentExercise.value.etiquetas) &&
        currentExercise.value.etiquetas.length > 0) {
        return true;
      }

      // Verificar en contenido (debug adicional)
      if (currentExercise.value.contenido) {
        console.log('Verificando etiquetas en contenido:', currentExercise.value.contenido);
        const contenido = typeof currentExercise.value.contenido === 'object'
          ? currentExercise.value.contenido
          : parseJsonSafely(currentExercise.value.contenido);

        return !!(contenido?.etiquetas?.length);
      }

      return false;
    });

    // Solo una declaración de hasCredits
    const hasCredits = computed(() => {
      const hasCredito = currentExercise.value &&
        currentExercise.value.credito &&
        currentExercise.value.credito.trim() !== '';

      console.log('¿Tiene crédito?', hasCredito, 'Valor:', currentExercise.value?.credito);
      return hasCredito;
    });

    // Obtener etiquetas del ejercicio
    const currentExerciseTags = computed(() => {
      console.log('Getting tags for:', currentExercise.value);
      console.log('etiquetas field:', currentExercise.value?.etiquetas);

      if (!currentExercise.value) return [];
      
      // Primero verificar etiquetas directas
      if (Array.isArray(currentExercise.value.etiquetas)) {
        return currentExercise.value.etiquetas;
      }
      
      // Luego buscar en contenido
      if (currentExercise.value.contenido) {
        const contenido = typeof currentExercise.value.contenido === 'object'
          ? currentExercise.value.contenido
          : parseJsonSafely(currentExercise.value.contenido);
        
        return Array.isArray(contenido?.etiquetas) ? contenido.etiquetas : [];
      }
      
      return [];
    });
    
    // Computar el ejercicio actual
    const currentExercise = computed(() => {
      if (!exercises.value || exercises.value.length === 0) {
        console.warn('No hay ejercicios disponibles');
        return null;
      }
      
      if (currentExerciseIndex.value >= exercises.value.length) {
        console.warn('Índice de ejercicio fuera de rango:', currentExerciseIndex.value);
        return exercises.value[0]; // Devolver el primer ejercicio como fallback
      }
      
      return exercises.value[currentExerciseIndex.value];
    });
    
    // Verificadores
    const hasRestrictions = computed(() => {
      return currentExercise.value && 
             currentExercise.value.restricciones && 
             currentExercise.value.restricciones.trim() !== '';
    });
    
    const hasOutputFormat = computed(() => {
      return currentExercise.value && 
             currentExercise.value.formato_salida && 
             currentExercise.value.formato_salida.trim() !== '';
    });
    
    const hasInputFormats = computed(() => {
      return currentExercise.value && 
             currentExercise.value.formatos_entrada && 
             Array.isArray(currentExercise.value.formatos_entrada) && 
             currentExercise.value.formatos_entrada.length > 0 &&
             currentExercise.value.formatos_entrada.some(format => format && format.trim() !== '');
    });

    // Obtener resultados para el ejercicio actual
    const getTestResultsForCurrentExercise = computed(() => {
      if (!currentExercise.value) return '';
      
      const exerciseId = currentExercise.value.id;
      if (!exerciseId) return '';
      
      const resultData = resultsMap.value.get(exerciseId);
      return resultData ? resultData.text : '';
    });
    
    // Verificar si hay stderr para el ejercicio actual
    const hasStderr = computed(() => {
      if (!currentExercise.value) return false;
      
      const exerciseId = currentExercise.value.id;
      if (!exerciseId) return false;
      
      const resultData = resultsMap.value.get(exerciseId);
      return resultData && resultData.stderr && resultData.stderr.trim() !== '';
    });
    
    // Obtener contenido stderr del ejercicio actual
    const getStderrContent = computed(() => {
      if (!currentExercise.value) return '';
      
      const exerciseId = currentExercise.value.id;
      if (!exerciseId) return '';
      
      const resultData = resultsMap.value.get(exerciseId);
      return resultData && resultData.stderr ? resultData.stderr : '';
    });
    
    // Verificar si los resultados deben mostrarse como texto plano
    const shouldDisplayAsText = computed(() => {
      if (!currentExercise.value) return true;
      
      const exerciseId = currentExercise.value.id;
      if (!exerciseId) return true;
      
      const resultData = resultsMap.value.get(exerciseId);
      return resultData ? resultData.isPlainText : true;
    });
    
    // Formatear descripción usando markdown
    const markdownDescription = computed(() => {
      if (!currentExercise.value || !currentExercise.value.descripcion) {
        return '';
      }

      try {
        const description = currentExercise.value.descripcion;

        // Configurar marked con la función moderna
        configureMarked();

        // Ejecutar el renderizado
        const renderedHTML = DOMPurify.sanitize(marked.parse(description));

        // Agregar event listener para enlaces en setup o onMounted
        nextTick(() => {
          const container = document.querySelector('.markdown-preview');
          if (container) {
            container.addEventListener('click', (e) => {
              const link = e.target.closest('a');
              if (link) {
                e.preventDefault();
                const href = link.getAttribute('href');
                if (href && href !== '#') {
                  window.open(href, '_blank');
                }
              }
            });
          }
        });

        return renderedHTML;
      } catch (error) {
        console.error('Error al procesar markdown:', error);
        return currentExercise.value.descripcion;
      }
    });
    
    // Formatear los resultados para destacar colores
    const formattedResults = computed(() => {
      const results = getTestResultsForCurrentExercise.value;
      if (!results) return '';
      
      try {
        // Si los resultados ya tienen formato HTML (contiene tags), devolverlos como están
        if (results.includes('<div') || 
            results.includes('<span') || 
            results.includes('<pre')) {
          return results;
        }
        
        // Destacar resultados CORRECTO/INCORRECTO y añadir colores
        let formatted = results
          .replace(/✓ CORRECTO/g, '<span class="result-success">✓ CORRECTO</span>')
          .replace(/✗ INCORRECTO/g, '<span class="result-error">✗ INCORRECTO</span>')
          .replace(/Error/g, '<span class="result-error">Error</span>')
          .replace(/Excelente/g, '<span class="result-success">¡Excelente!</span>')
          .replace(/✅/g, '<span class="result-success">✅</span>')
          .replace(/❌/g, '<span class="result-error">❌</span>');
        
        // Convertir saltos de línea en <br>
        formatted = formatted.replace(/\n/g, '<br>');
        
        return formatted;
      } catch (error) {
        console.error('Error al formatear resultados:', error);
        return results; // Devolver texto sin formato como fallback
      }
    });
    
    
    const setTestResults = (results) => {
      console.log('PracticalLeftPanel: recibiendo resultados de tipo', typeof results);

      if (!currentExercise.value) {
        console.warn('No se pueden guardar resultados: no hay ejercicio actual');
        return;
      }

      const exerciseId = currentExercise.value.id;
      if (!exerciseId) {
        console.warn('No se pueden guardar resultados: el ejercicio no tiene ID');
        return;
      }

      let resultText = '';
      let stderrContent = '';
      let isPlainText = true;

      // Procesar resultados basados en el tipo
      if (typeof results === 'string') {
        resultText = results;

        // Intentar detectar y separar stderr del texto
        const stderrMatch = results.match(/Error de ejecución \(stderr\):\s*([\s\S]*?)(?:\n\n|$)/);
        if (stderrMatch && stderrMatch[1]) {
          stderrContent = stderrMatch[1].trim();
          // Eliminar stderr del texto principal para evitar duplicación
          resultText = results.replace(/Error de ejecución \(stderr\):\s*[\s\S]*?(?:\n\n|$)/, '');
        }

        // Determinar si es texto plano o HTML/formateado
        isPlainText = !(results.includes('CORRECTO') ||
          results.includes('INCORRECTO') ||
          results.includes('<div') ||
          results.includes('<span'));
      } else if (typeof results === 'object' && results !== null) {
        // Si recibimos un objeto (posiblemente de la API)
        resultText = results.message || results.stdout || 'Ejecución completada';

        // Extraer stderr explícitamente si existe en el objeto
        if (results.stderr) {
          stderrContent = results.stderr;
        }

        // Determinar formato
        isPlainText = !(resultText.includes('CORRECTO') ||
          resultText.includes('INCORRECTO') ||
          resultText.includes('<div') ||
          resultText.includes('<span'));
      }

      // Guardar resultados para este ejercicio con stderr
      resultsMap.value.set(exerciseId, {
        text: resultText,
        stderr: stderrContent,
        isPlainText: isPlainText
      });

      // Cambiar a la pestaña de output automáticamente
      activeTab.value = 'output';
    };

    // Método para limpiar los resultados del ejercicio actual
    const clearResultsForCurrentExercise = () => {
      if (!currentExercise.value) return;
      
      const exerciseId = currentExercise.value.id;
      if (!exerciseId) return;
      
      resultsMap.value.delete(exerciseId);
    };
    
    // Activar la pestaña de output
    const activateOutputTab = () => {
      console.log('PracticalLeftPanel: activando pestaña de output');
      activeTab.value = 'output';
    };
    
    // Exponer métodos públicos al componente padre
    if (instance) {
      Object.assign(instance.exposed = instance.exposed || {}, {
        setTestResults,
        activateOutputTab
      });
    }
    
    onMounted(() => {
      configureMarked()
      console.log('PracticalLeftPanel montado con', exercises.value?.length || 0, 'ejercicios disponibles');
    });
    
    onBeforeUnmount(() => {
      // Limpiar mapa al desmontar
      resultsMap.value.clear();
    });
    
    return {
      activeTab,
      exercises,
      currentExercise,
      currentExerciseIndex,
      markdownDescription,
      hasInputFormats,
      hasRestrictions,
      hasOutputFormat,
      hasCredits,
      getCredits,
      hasEtiquetas,
      currentExerciseTags,
      getTestResultsForCurrentExercise,
      formattedResults,
      shouldDisplayAsText,
      clearResultsForCurrentExercise,
      setTestResults,
      activateOutputTab,
      hasStderr,
      getStderrContent,
      isHistoryMode
    };
  }
};
</script>

<style>
/* =================== ESTILOS GLOBALES Y OVERRIDES =================== */
.left-panel-wrapper button {
  background: none;
  border: none;
  cursor: pointer;
  padding: 0;
}

.left-panel-wrapper h2, 
.left-panel-wrapper h3 {
  margin: 0;
  padding: 0;
}

.left-panel-wrapper ul, 
.left-panel-wrapper ol {
  margin: 0;
  padding-left: 18px;
}

.left-panel-wrapper pre {
  margin: 0;
  font-family: 'Fira Code', Consolas, Monaco, 'Courier New', monospace;
  border-radius: var(--border-radius-sm);
}

/* =================== MARKDOWN PREVIEW STYLES =================== */
.markdown-preview h1,
.markdown-preview h2,
.markdown-preview h3,
.markdown-preview h4,
.markdown-preview h5,
.markdown-preview h6 {
  color: var(--color-primary);
  margin-top: 1rem;
  margin-bottom: 0.5rem;
  font-weight: 600;
}

.markdown-preview h1 {
  font-size: 1.8rem;
  border-bottom: 1px solid var(--color-border);
  padding-bottom: 0.3rem;
}

.markdown-preview h2 {
  font-size: 1.5rem;
}

.markdown-preview h3 {
  font-size: 1.3rem;
}

.markdown-preview p {
  margin-bottom: 1rem;
  color: var(--color-text-primary);
}

.markdown-preview strong {
  color: var(--color-text-primary);
  font-weight: 700;
}

.markdown-preview a {
  color: var(--color-info);
  text-decoration: none;
  border-bottom: 1px dotted var(--color-info);
  transition: all var(--transition-fast);
  cursor: pointer;
}

.markdown-preview a:hover {
  color: var(--color-primary);
  border-bottom-color: var(--color-primary);
  text-decoration: none;
}

.markdown-preview a:focus {
  outline: 2px solid var(--color-secondary);
  outline-offset: 2px;
}

.markdown-preview ul,
.markdown-preview ol {
  margin-left: 1.5rem;
  margin-bottom: 1rem;
}

.markdown-preview ul li,
.markdown-preview ol li {
  margin-bottom: 0.5rem;
}

.markdown-preview blockquote {
  border-left: 4px solid var(--color-secondary);
  padding-left: 1rem;
  margin-left: 0;
  color: var(--color-text-secondary);
  font-style: italic;
}

.markdown-preview hr {
  border: none;
  border-top: 1px solid var(--color-border);
  margin: 1.5rem 0;
}

.markdown-preview img {
  max-width: 100%;
  border-radius: var(--border-radius);
  margin: 1rem 0;
}

.markdown-preview .video-container {
  position: relative;
  width: 100%;
  padding-bottom: 56.25%;
  margin: 1.5rem 0;
}

.markdown-preview .video-container iframe {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  border-radius: var(--border-radius);
  border: none;
}

.markdown-preview code {
  background-color: var(--color-bg-element-hover);
  color: var(--color-error);
  padding: 0.2rem 0.4rem;
  border-radius: 0.3rem;
  font-family: 'Fira Code', 'Consolas', monospace;
  border: 1px solid var(--color-border);
}

.markdown-preview pre {
  margin: 1rem 0;
  border-radius: var(--border-radius);
  padding: 0;
  overflow: hidden;
}

.markdown-preview pre code {
  display: block;
  padding: 1rem;
  overflow-x: auto;
  border-radius: 0;
  background-color: var(--color-editor-bg);
  color: var(--color-text-secondary);
  border: none;
}

/* =================== CONTENT AREA STYLES =================== */
.left-panel-wrapper .content-area h1,
.left-panel-wrapper .content-area h2,
.left-panel-wrapper .content-area h3,
.left-panel-wrapper .content-area h4,
.left-panel-wrapper .content-area h5,
.left-panel-wrapper .content-area h6 {
  color: var(--color-text-primary);
  margin-top: 16px;
  margin-bottom: 8px;
}

.left-panel-wrapper .content-area ul,
.left-panel-wrapper .content-area ol {
  padding-left: 24px;
  margin-bottom: 16px;
}

.left-panel-wrapper .content-area p {
  margin-bottom: 16px;
}

.left-panel-wrapper .content-area code {
  padding: 2px 6px;
  border-radius: 4px;
  font-family: 'Fira Code', Consolas, Monaco, 'Courier New', monospace;
  font-size: 0.9em;
}

.left-panel-wrapper .content-area pre {
  background-color: var(--color-bg-element-active);
  padding: 12px;
  border-radius: var(--border-radius-sm);
  overflow-x: auto;
  margin: 12px 0;
}

.left-panel-wrapper .content-area pre code {
  background-color: transparent;
  padding: 0;
  border-radius: 0;
}

.left-panel-wrapper .content-area a {
  color: var(--color-primary);
  text-decoration: none;
}

.left-panel-wrapper .content-area a:hover {
  text-decoration: underline;
}

.left-panel-wrapper .content-area blockquote {
  border-left: 4px solid var(--color-primary);
  padding-left: 16px;
  margin-left: 0;
  color: var(--color-text-secondary);
}

.left-panel-wrapper .content-area table {
  border-collapse: collapse;
  width: 100%;
  margin: 16px 0;
}

.left-panel-wrapper .content-area th,
.left-panel-wrapper .content-area td {
  border: 1px solid var(--color-border);
  padding: 8px 12px;
}

.left-panel-wrapper .content-area th {
  background-color: var(--color-bg-element-alt);
}

/* =================== SCROLLBAR PERSONALIZADO =================== */
.custom-scrollbar {
  scrollbar-width: thin;
  scrollbar-color: var(--color-border-light) var(--color-bg-element);
}

.custom-scrollbar::-webkit-scrollbar {
  width: 6px;
  height: 6px;
}

.custom-scrollbar::-webkit-scrollbar-track {
  background: var(--color-bg-element);
  border-radius: 4px;
}

.custom-scrollbar::-webkit-scrollbar-thumb {
  background-color: var(--color-border-light);
  border-radius: 4px;
  transition: background-color var(--transition-smooth);
}

.custom-scrollbar::-webkit-scrollbar-thumb:hover {
  background-color: var(--color-border);
}
</style>

<style scoped>
/* =================== CONTENEDOR PRINCIPAL =================== */
.left-panel-wrapper {
  height: 100%;
  background-color: var(--color-bg-main);
  display: flex;
  flex-direction: column;
  width: 50%;
  flex: 0 0 50%;
  max-width: 50%;
}

.practical-left-panel {
  display: flex;
  flex-direction: column;
  height: 100%;
}

/* =================== SISTEMA DE PESTAÑAS =================== */
.left-panel-tabs {
  background-color: var(--color-bg-element);
  padding: 8px 16px 0;
}

.tabs-container {
  display: flex;
  gap: 2px;
}

.tab-button {
  padding: 10px 16px;
  background-color: var(--color-bg-element-alt);
  color: var(--color-text-secondary);
  border-top-left-radius: var(--border-radius);
  border-top-right-radius: var(--border-radius);
  font-weight: 500;
  font-size: 14px;
  transition: all var(--transition-smooth);
  display: flex;
  align-items: center;
  gap: 8px;
  border-bottom: 3px solid transparent;
}

.tab-button:hover {
  background-color: var(--color-bg-element-hover);
  color: var(--color-text-primary);
}

.tab-button.active {
  background-color: var(--color-bg-element);
  color: var(--color-primary);
  border-bottom: 3px solid var(--color-primary);
}

.tab-icon {
  font-size: 16px;
}

/* =================== CONTENIDO DEL PANEL =================== */
.panel-content {
  flex: 1;
  overflow-y: auto;
  background-color: var(--color-bg-element);
  padding: 16px;
  border-radius: 0 0 var(--border-radius) var(--border-radius);
}

/* =================== HEADER DEL EJERCICIO =================== */
.exercise-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
}

.exercise-title {
  font-size: 1.4rem;
  color: var(--color-text-primary);
  font-weight: 600;
}

.exercise-points {
  background-color: var(--color-primary);
  color: var(--color-bg-main);
  font-weight: 600;
  font-size: 14px;
  padding: 4px 10px;
  border-radius: 20px;
}

/* =================== TARJETAS DE SECCIÓN =================== */
.section-card {
  background-color: var(--color-bg-element-alt);
  border-radius: var(--border-radius);
  padding: 16px;
  margin-bottom: 16px;
  box-shadow: var(--shadow-sm);
  border-left: 4px solid var(--color-primary);
}

.section-title {
  display: flex;
  align-items: center;
  font-size: 16px;
  color: var(--color-text-primary);
  margin-bottom: 10px;
  font-weight: 600;
}

.section-icon {
  margin-right: 8px;
  font-size: 18px;
}

.content-area {
  color: var(--color-text-secondary);
  line-height: 1.6;
}

/* =================== VARIACIONES DE SECCIONES =================== */
.description-section {
  border-left-color: var(--color-info);
}

.constraints-section {
  border-left-color: var(--color-warning);
}

.input-format-section {
  border-left-color: var(--color-primary);
}

.output-format-section {
  border-left-color: var(--color-text-muted);
}

.credits-section {
  border-left-color: var(--color-success);
}

.input-format-list li {
  margin-bottom: 6px;
}

/* =================== SISTEMA DE ETIQUETAS =================== */
.tags-container {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  margin-top: 16px;
  margin-bottom: 16px;
  padding: 0 4px;
}

.tag-badge {
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 6px 12px;
  background-color: var(--color-secondary-dark);
  color: white;
  font-size: 0.8rem;
  font-weight: 500;
  border-radius: 20px;
  box-shadow: var(--shadow-sm);
  transition: all var(--transition-fast);
  white-space: nowrap;
}

.tag-badge:hover {
  transform: translateY(-2px);
  box-shadow: var(--shadow);
  background-color: var(--color-secondary);
}

/* =================== PANEL DE OUTPUT =================== */
.output-content {
  height: 100%;
  display: flex;
  flex-direction: column;
}

.output-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px 16px;
  background-color: var(--color-bg-element-alt);
  border-top-left-radius: var(--border-radius);
  border-top-right-radius: var(--border-radius);
}

.output-title {
  display: flex;
  align-items: center;
  font-weight: 600;
  color: var(--color-text-primary);
  font-size: 15px;
}

.output-icon {
  margin-right: 8px;
}

.clear-button {
  color: var(--color-text-secondary);
  width: 30px;
  height: 30px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all var(--transition-fast);
}

.clear-button:hover {
  background-color: var(--color-bg-element-hover);
  color: var(--color-text-primary);
}

.output-body {
  flex: 1;
  background-color: var(--color-bg-darker);
  border: 1px solid var(--color-border);
  border-top: none;
  border-bottom-left-radius: var(--border-radius);
  border-bottom-right-radius: var(--border-radius);
  overflow-y: auto;
  padding: 16px;
}

.output-text pre {
  white-space: pre-wrap;
  word-break: break-word;
  color: var(--color-text-secondary);
  font-size: 14px;
  line-height: 1.5;
  background-color: var(--color-editor-bg);
}

.output-formatted {
  color: var(--color-text-secondary);
  font-size: 14px;
  line-height: 1.5;
}

/* =================== RESULTADOS FORMATEADOS =================== */
.result-success {
  color: var(--color-success);
  font-weight: 600;
}

.result-error {
  color: var(--color-error);
  font-weight: 600;
}

/* =================== ESTADO VACÍO =================== */
.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 48px 0;
  text-align: center;
  height: 80%;
}

.empty-icon {
  font-size: 4rem;
  color: var(--color-primary);
  margin-bottom: 20px;
  opacity: 0.8;
}

.empty-state h3 {
  font-size: 20px;
  color: var(--color-text-primary);
  margin-bottom: 12px;
}

.empty-state p {
  color: var(--color-text-secondary);
  max-width: 300px;
  margin: 0 auto;
}

.empty-state strong {
  color: var(--color-primary);
}

/* =================== SECCIÓN STDERR =================== */
.stderr-section {
  margin-top: 16px;
  padding: 12px;
  background-color: var(--color-error-bg);
  border-left: 4px solid var(--color-error);
  border-radius: var(--border-radius-sm);
}

.stderr-header {
  display: flex;
  align-items: center;
  margin-bottom: 8px;
  font-weight: 600;
  color: var(--color-error);
}

.stderr-icon {
  font-size: 16px;
  margin-right: 8px;
}

.stderr-title {
  font-size: 14px;
}

.stderr-content {
  font-family: 'Fira Code', Consolas, Monaco, 'Courier New', monospace;
  font-size: 13px;
  line-height: 1.5;
  background-color: var(--color-bg-darker);
  padding: 10px;
  border-radius: 4px;
  color: var(--color-text-primary);
  white-space: pre-wrap;
  word-break: break-word;
  overflow-x: auto;
}

/* =================== INDICADOR MODO HISTORIA =================== */
.history-mode-indicator {
  background-color: var(--color-history-mode);
  padding: 0.5rem 1rem;
  border-radius: var(--border-radius);
  display: flex;
  align-items: center;
  gap: 0.5rem;
  margin: 5px 3px;
  border: 1px solid var(--color-warning-dark);
  width: 350px;
}

.history-icon {
  font-size: 1.2rem;
}

.history-text {
  color: var(--color-warning);
  font-weight: 500;
  font-size: 0.9rem;
}

/* =================== MEDIA QUERIES =================== */
@media (max-width: 768px) {
  .panel-content {
    padding: 12px;
  }
  
  .exercise-title {
    font-size: 1.2rem;
  }
  
  .tab-button {
    padding: 8px 12px;
    font-size: 13px;
  }
  
  .tab-text {
    display: none;
  }
  
  .section-card, .example-card {
    padding: 12px;
  }
  
  .tags-container {
    justify-content: center;
  }
}

@media (min-width: 769px) {
  .columns.is-gapless.main-content {
    display: flex;
    width: 100%;
  }
  
  .left-panel-wrapper {
    width: 50%;
    flex: 0 0 50%;
    max-width: 50%;
  }
}
</style>