<!-- components/common/PracticalLeftPanel.vue -->
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
/* Estilos globales para anular Bulma (sin scoped) */
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
  border-radius: var(--border-radius-sm, 6px);
}

/* Estilos globales necesarios para el renderizado del markdown */
.markdown-preview h1,
.markdown-preview h2,
.markdown-preview h3,
.markdown-preview h4,
.markdown-preview h5,
.markdown-preview h6 {
    color: var(--color-primary, #EBB300);
    margin-top: 1rem;
    margin-bottom: 0.5rem;
    font-weight: 600;
}

.markdown-preview h1 {
    font-size: 1.8rem;
    border-bottom: 1px solid var(--color-border, #36363c);
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
    color: var(--color-text, #efe8e8); /* Valor por defecto para tema claro */
}

/* Mejora para el texto en negrita - alta visibilidad en modo claro */
.markdown-preview strong {
    color: #ffffff; /* Negro para tema claro */
    font-weight: 700; /* Más bold */
}

/* En tema oscuro */
@media (prefers-color-scheme: dark) {
    .markdown-preview strong {
        color: #ffffff; /* Blanco para tema oscuro */
    }
    
    .markdown-preview p {
        color: var(--color-text, #FFFFFF);
    }
}

.markdown-preview a {
    color: #0066cc; /* Azul más visible en tema claro */
    text-decoration: none;
    border-bottom: 1px dotted #0066cc;
    transition: all 0.2s ease;
    cursor: pointer;
}

.markdown-preview a:hover {
    color: var(--color-primary, #EBB300);
    border-bottom-color: var(--color-primary, #EBB300);
    text-decoration: none;
}

.markdown-preview a:focus {
    outline: 2px solid var(--color-purple, #8A4FFF);
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
    border-left: 4px solid var(--color-purple, #8A4FFF);
    padding-left: 1rem;
    margin-left: 0;
    color: var(--color-text-secondary, #555);
    font-style: italic;
}

.markdown-preview hr {
    border: none;
    border-top: 1px solid var(--color-border, #36363c);
    margin: 1.5rem 0;
}

.markdown-preview img {
    max-width: 100%;
    border-radius: var(--border-radius, 8px);
    margin: 1rem 0;
}

/* Estilo para videos de YouTube */
.markdown-preview .video-container {
    position: relative;
    width: 100%;
    padding-bottom: 56.25%; /* Proporción 16:9 */
    margin: 1.5rem 0;
}

.markdown-preview .video-container iframe {
    position: absolute;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    border-radius: var(--border-radius, 8px);
    border: none;
}

/* Mejora para código en línea - compatible con tema claro */
.markdown-preview code {
    background-color: #e7e3e3; /* Gris claro para tema claro */
    color: #d14; /* Rojo más suave para tema claro */
    padding: 0.2rem 0.4rem;
    border-radius: 0.3rem;
    font-family: 'Fira Code', 'Consolas', monospace;
    border: 1px solid #e0e0e0;
}

/* Estilos para tema oscuro */
@media (prefers-color-scheme: dark) {
    .markdown-preview code {
        background-color: rgba(255, 255, 255, 0.3);
        color: #e06c75; /* Color similar al tema Atom One Dark */
        border-color: #444;
    }
}

.markdown-preview pre {
    margin: 1rem 0;
    border-radius: var(--border-radius, 8px);
    padding: 0;
    overflow: hidden;
}

/* Bloques de código compatibles con tema claro */
.markdown-preview pre code {
    display: block;
    padding: 1rem;
    overflow-x: auto;
    border-radius: 0;
    background-color: #f8f8f8; /* Fondo claro para tema claro */
    color: #333; /* Color de texto oscuro para tema claro */
    border: none;
}

/* Soporte para tema oscuro */
@media (prefers-color-scheme: dark) {
    .markdown-preview pre code {
        background-color: #282c34; /* Color de fondo de Atom One Dark */
        color: #abb2bf; /* Color de texto para tema oscuro */
    }
}

/* Estilos existentes de content-area para otros elementos */
.left-panel-wrapper .content-area h1,
.left-panel-wrapper .content-area h2,
.left-panel-wrapper .content-area h3,
.left-panel-wrapper .content-area h4,
.left-panel-wrapper .content-area h5,
.left-panel-wrapper .content-area h6 {
  color: var(--color-text-primary, #FFFFFF);
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
  background-color: #2a2a34;
  padding: 12px;
  border-radius: var(--border-radius-sm, 6px);
  overflow-x: auto;
  margin: 12px 0;
}

.left-panel-wrapper .content-area pre code {
  background-color: transparent;
  padding: 0;
  border-radius: 0;
}

.left-panel-wrapper .content-area a {
  color: var(--color-primary, #EBB300);
  text-decoration: none;
}

.left-panel-wrapper .content-area a:hover {
  text-decoration: underline;
}

.left-panel-wrapper .content-area blockquote {
  border-left: 4px solid var(--color-primary, #EBB300);
  padding-left: 16px;
  margin-left: 0;
  color: var(--color-text-secondary, #E0E0E0);
}

.left-panel-wrapper .content-area table {
  border-collapse: collapse;
  width: 100%;
  margin: 16px 0;
}

.left-panel-wrapper .content-area th,
.left-panel-wrapper .content-area td {
  border: 1px solid var(--color-border, #36363C);
  padding: 8px 12px;
}

.left-panel-wrapper .content-area th {
  background-color: var(--color-bg-element-alt, #25252A);
}

/* Estilos para scrollbar personalizado */
.custom-scrollbar {
  scrollbar-width: thin;
  scrollbar-color: rgba(54, 54, 60, 0.6) rgba(42, 42, 48, 0.1);
}

.custom-scrollbar::-webkit-scrollbar {
  width: 6px;
  height: 6px;
}

.custom-scrollbar::-webkit-scrollbar-track {
  background: rgba(42, 42, 48, 0.1);
  border-radius: 4px;
}

.custom-scrollbar::-webkit-scrollbar-thumb {
  background-color: rgba(54, 54, 60, 0.6);
  border-radius: 4px;
  transition: background-color 0.3s ease;
}

.custom-scrollbar::-webkit-scrollbar-thumb:hover {
  background-color: rgba(70, 70, 80, 0.8);
}
</style>

<style scoped>
.left-panel-wrapper {
  height: 100%;
  background-color: var(--color-bg-main, #1C1C21);
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

/* Pestañas */
.left-panel-tabs {
  background-color: var(--color-bg-element, #2A2A30);
  padding: 8px 16px 0;
}

.tabs-container {
  display: flex;
  gap: 2px;
}

.tab-button {
  padding: 10px 16px;
  background-color: #25252A;
  color: var(--color-text-secondary, #E0E0E0);
  border-top-left-radius: 8px;
  border-top-right-radius: 8px;
  font-weight: 500;
  font-size: 14px;
  transition: all 0.3s ease;
  display: flex;
  align-items: center;
  gap: 8px;
  border-bottom: 3px solid transparent;
}

.tab-button:hover {
  background-color: #2E2E38;
  color: var(--color-text-primary, #FFFFFF);
}

.tab-button.active {
  background-color: var(--color-bg-element, #2A2A30);
  color: var(--color-primary, #EBB300);
  border-bottom: 3px solid var(--color-primary, #EBB300);
}

.tab-icon {
  font-size: 16px;
}

/* Contenido del panel */
.panel-content {
  flex: 1;
  overflow-y: auto;
  background-color: var(--color-bg-element, #2A2A30);
  padding: 16px;
  border-radius: 0 0 8px 8px;
}

/* Instrucciones */
.exercise-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
}

.exercise-title {
  font-size: 1.4rem;
  color: var(--color-text-primary, #FFFFFF);
  font-weight: 600;
}

.exercise-points {
  background-color: var(--color-primary, #EBB300);
  color: #1C1C21;
  font-weight: 600;
  font-size: 14px;
  padding: 4px 10px;
  border-radius: 20px;
}

.section-card {
  background-color: var(--color-bg-element-alt, #25252A);
  border-radius: var(--border-radius, 8px);
  padding: 16px;
  margin-bottom: 16px;
  box-shadow: var(--shadow-sm, 0 2px 6px rgba(0, 0, 0, 0.1));
  border-left: 4px solid var(--color-primary, #EBB300);
}

.section-title {
  display: flex;
  align-items: center;
  font-size: 16px;
  color: var(--color-text-primary, #FFFFFF);
  margin-bottom: 10px;
  font-weight: 600;
}

.section-icon {
  margin-right: 8px;
  font-size: 18px;
}

.content-area {
  color: var(--color-text-secondary, #E0E0E0);
  line-height: 1.6;
}

.description-section {
  border-left-color: var(--color-info, #65B1C1);
}

.constraints-section {
  border-left-color: var(--color-warning, #FFBD2E);
}

.input-format-section {
  border-left-color: var(--color-primary, #EBB300);
}

.output-format-section {
  border-left-color: var(--color-secondary, #6B7280);
}

.credits-section {
  border-left-color: var(--color-success, #9DBEB6);
}

.input-format-list li {
  margin-bottom: 6px;
}

/* SECCIÓN PARA ETIQUETAS */
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
  background-color: var(--color-purple-dark, #6B3FC8);
  color: white;
  font-size: 0.8rem;
  font-weight: 500;
  border-radius: 20px;
  box-shadow: var(--shadow-sm, 0 2px 4px rgba(0, 0, 0, 0.1));
  transition: all 0.2s ease;
  white-space: nowrap;
}

.tag-badge:hover {
  transform: translateY(-2px);
  box-shadow: var(--shadow, 0 4px 6px rgba(0, 0, 0, 0.15));
  background-color: var(--color-purple, #8A4FFF);
}

/* Output panel */
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
  background-color: var(--color-bg-element-alt, #25252A);
  border-top-left-radius: var(--border-radius, 8px);
  border-top-right-radius: var(--border-radius, 8px);
}

.output-title {
  display: flex;
  align-items: center;
  font-weight: 600;
  color: var(--color-text-primary, #FFFFFF);
  font-size: 15px;
}

.output-icon {
  margin-right: 8px;
}

.clear-button {
  color: var(--color-text-secondary, #E0E0E0);
  width: 30px;
  height: 30px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.2s ease;
}

.clear-button:hover {
  background-color: rgba(255, 255, 255, 0.1);
  color: var(--color-text-primary, #FFFFFF);
}

.output-body {
  flex: 1;
  background-color: #1e1e24;
  border: 1px solid var(--color-border, #36363C);
  border-top: none;
  border-bottom-left-radius: var(--border-radius, 8px);
  border-bottom-right-radius: var(--border-radius, 8px);
  overflow-y: auto;
  padding: 16px;
}

.output-text pre {
  white-space: pre-wrap;
  word-break: break-word;
  color: var(--color-text-secondary, #E0E0E0);
  font-size: 14px;
  line-height: 1.5;
  background-color: #1f2229;
}

.output-formatted {
  color: var(--color-text-secondary, #E0E0E0);
  font-size: 14px;
  line-height: 1.5;
}

/* Resultados formateados */
.result-success {
  color: var(--color-success, #9DBEB6);
  font-weight: 600;
}

.result-error {
  color: var(--color-danger, #FF6B6B);
  font-weight: 600;
}

/* Estado vacío */
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
  color: var(--color-primary, #EBB300);
  margin-bottom: 20px;
  opacity: 0.8;
}

.empty-state h3 {
  font-size: 20px;
  color: var(--color-text-primary, #FFFFFF);
  margin-bottom: 12px;
}

.empty-state p {
  color: var(--color-text-secondary, #E0E0E0);
  max-width: 300px;
  margin: 0 auto;
}

.empty-state strong {
  color: var(--color-primary, #EBB300);
}

/* Responsive */
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

/* ESTILOS PARA STDERR */
.stderr-section {
  margin-top: 16px;
  padding: 12px;
  background-color: rgba(255, 107, 107, 0.1);
  border-left: 4px solid var(--color-danger, #FF6B6B);
  border-radius: var(--border-radius-sm, 6px);
}

.stderr-header {
  display: flex;
  align-items: center;
  margin-bottom: 8px;
  font-weight: 600;
  color: var(--color-danger, #FF6B6B);
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
  background-color: rgba(30, 30, 36, 0.8);
  padding: 10px;
  border-radius: 4px;
  color: #f8f8f2;
  white-space: pre-wrap;
  word-break: break-word;
  overflow-x: auto;
}

/* Estilos para el indicador de modo historia */
.history-mode-indicator {
  background-color: #1E1E28;
  padding: 0.5rem 1rem;
  border-radius: 8px;
  display: flex;
  align-items: center;
  gap: 0.5rem;
  margin-top: 5px;
  margin-bottom: 5px;
  margin-left: 3px;
  /* border-left: 3px solid var(--color-warning, #FFBD2E); */
  border: 1px solid #62442B;
  width: 350px;
}

.history-icon {
  font-size: 1.2rem;
}

.history-text {
  color: #FF9933;
  font-weight: 500;
  font-size: 0.9rem;
}
</style>