<!-- src/components/docentes/crear-ejercicio/CreateExercise.vue -->
<template>
  <div class="create-exercise-wrapper">
    <div class="form-container">
      <header class="header">
        <div class="header-content">
          <div class="header-text">
            <h1 class="title is-3">{{ isEditing ? 'Editar Ejercicio' : 'Crear Ejercicio' }}</h1>
            <p class="subtitle is-5">¡Diseña ejercicios didácticos para evaluar las habilidades de programación de tus
              estudiantes!</p>
          </div>
          <div class="header-icon">
            <span class="icon-container">
              <i class="fas">{{ isEditing ? '🔎' : '📝' }}</i>
            </span>
          </div>
        </div>
      </header>

      <!-- Mostrar estado de carga mientras se obtiene la información del ejercicio en modo edición -->
      <div class="loading-container" v-if="isEditing && loading">
        <div class="loading-circle"></div>
        <p class="has-text-centered mt-4">Cargando datos del ejercicio...</p>
      </div>

      <form class="form" @submit.prevent="submitForm" v-else>
        <!-- Title Section -->
        <div class="form-group">
          <label class="form-label" for="title">
            <i class="icon-prefix">📝</i> Título
          </label>
          <input class="form-input" id="title" placeholder="Nombre descriptivo y conciso del ejercicio"
            v-model="form.title" name="title">
          <span class="helper-text">Debe ser claro y específico sobre lo que el estudiante debe implementar</span>
        </div>

        <!-- Description Section with Markdown Preview -->
        <MarkdownEditor v-model="form.description" />

        <!-- Points Section -->
        <div class="form-group">
          <label class="form-label" for="points">
            <i class="icon-prefix">🏆</i> Puntos
          </label>
          <input class="form-input" id="points" placeholder="30" type="number" v-model="form.points" name="points">
          <span class="helper-text">Valor asignado a este ejercicio en la evaluación</span>
        </div>

        <!-- Difficulty Section -->
        <div class="form-group">
          <label class="form-label" for="difficulty">
            <i class="icon-prefix">📊</i> Dificultad
          </label>
          <div class="select-container">
            <select class="form-input" id="difficulty" v-model="form.difficulty" name="difficulty">
              <option value="facil">Fácil</option>
              <option value="intermedio">Intermedio</option>
              <option value="dificil">Difícil</option>
            </select>
          </div>
          <span class="helper-text">Nivel de complejidad que representa para el estudiante</span>
        </div>

        <!-- Etiquetas simplificadas -->
        <div class="form-group tags-section">
          <label class="form-label" for="tags">
            <i class="icon-prefix">🏷️</i> Etiquetas
          </label>

          <div class="tags-input-container">
            <input class="form-input" id="tags"
              placeholder="Ingresa etiquetas separadas por comas (ej: algoritmos, arrays, ciclos)" v-model="tagsInput"
              @keydown.enter.prevent="processTagsFromInput">
          </div>

          <!-- Etiquetas seleccionadas -->
          <div class="selected-tags-container" v-if="form.tags.length > 0">
            <div v-for="(tag, index) in form.tags" :key="tag" class="tag-item">
              <span>{{ tag }}</span>
              <button class="tag-remove" @click.prevent="removeTag(index)">×</button>
            </div>
          </div>

          <span class="helper-text">Añade etiquetas para categorizar el ejercicio (Ej: "algoritmos", "arreglos",
            "recursión")</span>
        </div>

        <!-- Credit Section -->
        <div class="form-group">
          <label class="form-label" for="credit">
            <i class="icon-prefix">🔗</i> Créditos/Fuente
          </label>
          <input class="form-input" id="credit" placeholder="Ej: Adaptado de Project Euler" v-model="form.credit"
            name="credit" @keydown.enter.prevent>
          <span class="helper-text">Si el ejercicio fue adaptado de otra fuente, indica la referencia original</span>
        </div>

        <!-- Constraints Section -->
        <div class="form-group">
          <label class="form-label" for="constraints">
            <i class="icon-prefix">🧩</i> Restricciones
          </label>
          <textarea class="form-textarea" id="constraints" placeholder="Ej: 1 ≤ n ≤ 1000, valores no negativos"
            v-model="form.constraints" name="constraints" rows="3"></textarea>
          <span class="helper-text">Especifica límites de valores, condiciones o requisitos que debe cumplir la
            solución</span>
        </div>

        <!-- Pista para el estudiante -->
        <div class="form-group">
          <label class="form-label" for="hint">
            <i class="icon-prefix">💡</i> Pista para el estudiante
          </label>
          <textarea class="form-textarea" id="hint"
            placeholder="Sugerencia opcional que ayude a enfocar la solución sin resolverla completamente"
            v-model="form.hint" name="hint" rows="3"></textarea>
          <span class="helper-text">Esta pista estará disponible si el estudiante la solicita durante la
            evaluación</span>
        </div>

        <!-- Multi-item Sections -->
        <div class="accordion-sections">
          <!-- Input Format Section with Accordion -->
          <div class="accordion-item">
            <div class="accordion-header" @click="toggleSection('inputFormat')">
              <h3 class="accordion-title">
                <i class="icon-prefix">⌨️</i> Formato de Entrada
              </h3>
              <span class="accordion-icon">{{ openSections.inputFormat ? '📂' : '📁' }}</span>
            </div>
            <div class="accordion-content" v-if="openSections.inputFormat">
              <p class="section-hint">Describe cómo se proporcionarán los datos al programa (a través de input(),
                parámetros de función, etc.)</p>
              <div class="multi-input-container">
                <div v-for="(format, index) in form.inputFormats" :key="`input-format-${index}`"
                  class="multi-input-item">
                  <textarea class="form-textarea"
                    placeholder="Ej: Primer línea: entero n (número de elementos). Segunda línea: n enteros separados por espacios"
                    v-model="form.inputFormats[index]" rows="3"></textarea>
                  <button type="button" @click.prevent="removeInputFormat(index)" class="delete-button">
                    <span class="sr-only">Eliminar</span>
                    <span class="delete-icon">🗑️</span>
                  </button>
                </div>
                <button type="button" @click.prevent="addInputFormat" class="add-button">
                  <i>➕</i> Agregar Formato de Entrada
                </button>
              </div>
            </div>
          </div>

          <!-- Output Format Section -->
          <div class="accordion-item">
            <div class="accordion-header" @click="toggleSection('outputFormat')">
              <h3 class="accordion-title">
                <i class="icon-prefix">🖥️</i> Formato de Salida
              </h3>
              <span class="accordion-icon">{{ openSections.outputFormat ? '📂' : '📁' }}</span>
            </div>
            <div class="accordion-content" v-if="openSections.outputFormat">
              <p class="section-hint">Especifica exactamente cómo debe mostrarse el resultado (valores, formato, orden)
              </p>
              <textarea class="form-textarea" id="output_format"
                placeholder="Ej: Un entero único que representa la suma de todos los elementos"
                v-model="form.outputFormat" name="output_format" rows="3"></textarea>
            </div>
          </div>

          <!-- Casos de prueba -->
          <div class="accordion-item">
            <div class="accordion-header" @click="toggleSection('samples')">
              <h3 class="accordion-title">
                <i class="icon-prefix">📋</i> Casos de Prueba
              </h3>
              <span class="accordion-icon">{{ openSections.samples ? '📂' : '📁' }}</span>
            </div>
            <div class="accordion-content" v-if="openSections.samples">
              <p class="section-hint">Define ejemplos concretos con datos de entrada y resultados esperados para que el
                estudiante entienda qué debe hacer</p>
              <div class="samples-container">
                <!-- Sample Test Cards -->
                <div v-for="(_, index) in form.sampleInputs" :key="`sample-${index}`" class="sample-card">
                  <div class="sample-card-header">
                    <h4 class="sample-card-title">
                      <i class="icon-prefix">🔍</i> Caso de prueba #{{ index + 1 }}
                    </h4>
                    <button type="button" @click.prevent="removeSampleSet(index)" class="delete-button">
                      <span class="sr-only">Eliminar</span>
                      <span class="delete-icon">🗑️</span>
                    </button>
                  </div>

                  <div class="sample-card-content">
                    <div class="sample-input">
                      <label class="sample-label">
                        <i class="icon-prefix">➡️</i> Entrada:
                      </label>
                      <textarea class="form-textarea" placeholder="Datos que recibirá la función o programa"
                        v-model="form.sampleInputs[index]" rows="3"></textarea>
                    </div>

                    <div class="sample-output">
                      <label class="sample-label">
                        <i class="icon-prefix">⬅️</i> Resultado Esperado:
                      </label>
                      <textarea class="form-textarea" placeholder="Lo que debe devolver o imprimir el programa"
                        v-model="form.sampleOutputs[index]" rows="3"></textarea>
                    </div>

                    <!--
                    <div class="sample-explanation">
                      <label class="sample-label">
                        <i class="icon-prefix">💡</i> Explicación:
                      </label>
                      <textarea class="form-textarea"
                        placeholder="Explica cómo se llega a este resultado ( 👷‍♂️ En desarrollo... )"
                        v-model="form.sampleExplanations[index]" rows="3"></textarea>
                    </div>
                    -->

                  </div>
                </div>

                <button type="button" @click.prevent="addSampleSet" class="add-button">
                  <i>➕</i> Agregar Caso de Prueba
                </button>
              </div>
            </div>
          </div>


          <!-- Plantilla por lenguaje -->
          <div class="accordion-item">
            <div class="accordion-header" @click="toggleSection('templates')">
              <h3 class="accordion-title">
                <i class="icon-prefix">📋</i> Plantillas por Lenguaje
              </h3>
              <span class="accordion-icon">{{ openSections.templates ? '📂' : '📁' }}</span>
            </div>
            <div class="accordion-content" v-if="openSections.templates">
              <p class="section-hint">Define plantillas específicas para cada lenguaje de programación</p>

              <!-- Selector de lenguaje para plantillas -->
              <div class="language-selector-container">
                <label class="form-label" for="template-language-selector">
                  <i class="icon-prefix">🌐</i> Lenguaje para plantilla:
                </label>
                <select id="template-language-selector" v-model="selectedLanguageForTemplate" class="language-select"
                  @change="handleTemplateLanguageChange">
                  <option v-for="lang in availableLanguages" :key="lang.id" :value="lang.id">
                    {{ lang.name }}
                  </option>
                </select>
                <span class="language-count" v-if="availableLanguages.length">
                  ({{ availableLanguages.length }} lenguajes disponibles)
                </span>
              </div>

              <div class="template-container">
                <div class="template-editor">
                  <label class="form-label">Plantilla para {{ getCurrentLanguageName(selectedLanguageForTemplate)
                    }}:</label>
                  <textarea class="form-textarea" v-model="templatesForLanguages[selectedLanguageForTemplate]"
                    :placeholder="getTemplatePlaceholder(selectedLanguageForTemplate)" rows="15"></textarea>
                  <span class="helper-text">Esta plantilla se mostrará automáticamente cuando el estudiante seleccione
                    este lenguaje</span>
                </div>

                <div class="template-info">
                  <h4>Plantillas definidas:</h4>
                  <div class="language-tag-container">
                    <span v-for="(template, langId) in templatesForLanguages" :key="langId" class="language-tag"
                      :class="{ 'active': template.trim().length > 0 }" :title="getLanguageName(langId)"
                      @click="selectedLanguageForTemplate = parseInt(langId)">
                      {{ getLanguageShortName(langId) }}
                    </span>
                  </div>
                  <p class="template-info-text">
                    Haz clic en un lenguaje para editar su plantilla. Las plantillas vacías mostrarán un mensaje
                    predeterminado al estudiante.
                  </p>
                </div>
              </div>
            </div>
          </div>

          <!-- Tests Avanzados -->
          <div class="accordion-item">
            <div class="accordion-header" @click="toggleSection('advancedTests')">
              <h3 class="accordion-title">
                <i class="icon-prefix">🧪</i> Tests Avanzados
              </h3>
              <span class="accordion-icon">{{ openSections.advancedTests ? '📂' : '📁' }}</span>
            </div>
            <div class="accordion-content" v-if="openSections.advancedTests">
              <p class="section-hint">Define tests automatizados para diferentes lenguajes que verificarán si la
                solución del estudiante es correcta</p>

              <!-- Selector de lenguaje para tests -->
              <div class="language-selector-container">
                <label class="form-label" for="language-selector">
                  <i class="icon-prefix">🌐</i> Lenguaje para tests:
                </label>
                <select id="language-selector" v-model="selectedLanguageForTests" class="language-select"
                  @change="handleLanguageChange">
                  <option v-for="lang in availableLanguages" :key="lang.id" :value="lang.id">
                    {{ lang.name }}
                  </option>
                </select>
                <span class="language-count" v-if="availableLanguages.length">
                  ({{ availableLanguages.length }} lenguajes disponibles)
                </span>
              </div>

              <div class="test-container">
                <div class="test-editor">
                  <label class="form-label">Código de prueba para {{ getCurrentLanguageName() }}:</label>
                  <textarea class="form-textarea" v-model="testsForLanguages[selectedLanguageForTests]"
                    :placeholder="getTestPlaceholder(selectedLanguageForTests)" rows="15"></textarea>
                  <span class="helper-text">Estos tests pueden incluir casos básicos, límite y de rendimiento para
                    evaluar completamente la solución</span>
                </div>

                <div class="test-template-info">
                  <h4>Tipos de Tests compatibles (probados) con Judge0:</h4>
                  <ul class="test-types-list">
                    <li><strong>Tests de Entrada/Salida Estándar</strong>: Evalúan si el código produce exactamente la
                      salida esperada para una entrada dada. Son ideales para problemas de programación competitiva y
                      educativos.</li>
                    
                  </ul>
                  <p>Judge0 ejecuta el código en un entorno aislado, compara la salida generada con la salida esperada y
                    determina si la solución es correcta o no.</p>

                  <div class="supported-languages">
                    <span class="supported-label">Lenguajes con tests:</span>
                    <div class="language-tag-container">
                      <span v-for="(test, langId) in testsForLanguages" :key="langId" class="language-tag"
                        :class="{ 'active': test.trim().length > 0 }" :title="getLanguageName(langId)">
                        {{ getLanguageShortName(langId) }}
                      </span>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>

        <div class="form-actions">
          <button class="submit-button" type="submit">
            <i>{{ isEditing ? '🔄' : '🚀' }}</i> {{ isEditing ? 'Actualizar Ejercicio' : 'Crear Ejercicio' }}
          </button>
        </div>
      </form>
    </div>

    <!-- Notificación de éxito/error con auto-desvanecimiento -->
    <transition name="fade">
      <div v-if="notification.show" :class="['notification', `notification-${notification.type}`]">
        <button class="notification-close" @click="closeNotification">×</button>
        <div class="notification-header">
          <span class="notification-icon">{{ notification.type === 'success' ? '✓' : '⚠️' }}</span>
          <span class="notification-title">{{ notification.title }}</span>
        </div>
        <div class="notification-content">
          <p>{{ notification.message }}</p>
        </div>
        <div class="notification-actions" v-if="notification.type === 'success'">
          <button class="notification-button" @click="verEjercicios">Ver ejercicios</button>
        </div>
      </div>
    </transition>
  </div>
</template>

<script>
import MarkdownEditor from '@/components/docentes/crear-ejercicio/MarkdownEditor.vue';

import { defineComponent, ref, computed, onMounted, onBeforeUnmount, watch } from 'vue';
import judge0Service from '@/services/judge0Service';
import { marked } from 'marked';
import DOMPurify from 'dompurify';
import exercisesService from '@/api/exercisesService';
import { useStore } from 'vuex';
import evaluationsService from '@/api/evaluationsService';
import { useRouter, useRoute } from 'vue-router';
//import DevelopmentOverlay from './DevelopmentOverlay.vue';


export default defineComponent({
  components: {
    MarkdownEditor
  },
  name: 'CreateExercise',
  setup() {
    const store = useStore();
    const router = useRouter();
    const route = useRoute();
    const ejercicios = ref([]);
    const cursos = ref([]);

    const availableLanguages = ref([]);
    const selectedLanguageForTests = ref(71); // Python 3 por defecto
    const testsForLanguages = ref({
      '71': '' // Inicializar con Python vacío
    });

    const selectedLanguageForTemplate = ref(71); // Python 3 por defecto
    const templatesForLanguages = ref({
      '71': '' // Inicializar con Python vacío
    });


    const configureMarkdown = () => {
      // Configurar renderer personalizado
      const renderer = new marked.Renderer();

      // Corregir el procesamiento de enlaces
      renderer.link = function (href, title, text) {
        // Asegurar que href y text estén en el orden correcto
        if (!href) href = '#';

        const safeHref = href;
        const safeTitle = title || '';

        // Crear enlace con atributos adecuados
        return `<a href="${safeHref}" target="_blank" rel="noopener noreferrer" title="${safeTitle}" data-external="true">${text}</a>`;
      };

      // Aplicar configuración a marked
      marked.use({
        renderer: renderer,
        gfm: true,
        breaks: true,
        headerIds: true,
        headerPrefix: 'heading-'
      });

      // Configurar DOMPurify para permitir enlaces externos
      DOMPurify.addHook('afterSanitizeAttributes', function (node) {
        if (node.tagName === 'A') {
          node.setAttribute('target', '_blank');
          node.setAttribute('rel', 'noopener noreferrer');
          node.setAttribute('data-external', 'true');
        }
      });
    };

    // Función para cargar lenguajes disponibles desde Judge0
    const loadAvailableLanguages = async () => {
      try {
        console.log("Cargando lenguajes disponibles para tests...");
        const judge0Url = import.meta.env.VITE_JUDGE0_API_URL;
        if (!judge0Url) {
          console.error("URL de Judge0 no configurada");
          return;
        }

        const apiUrl = judge0Url.endsWith('/') ? `${judge0Url}languages` : `${judge0Url}/languages`;
        console.log("Solicitando lenguajes desde:", apiUrl);

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

        // Ordenar lenguajes populares al principio
        const popularIds = [71, 63, 62, 54, 50]; // Python, JavaScript, Java, C++, C
        languages.sort((a, b) => {
          const aPopular = popularIds.includes(a.id);
          const bPopular = popularIds.includes(b.id);

          if (aPopular && !bPopular) return -1;
          if (!aPopular && bPopular) return 1;
          return 0;
        });

        availableLanguages.value = languages;
        console.log(`Lenguajes disponibles cargados: ${availableLanguages.value.length}`);

        // Inicializar tests para lenguajes populares
        popularIds.forEach(id => {
          if (!testsForLanguages.value[id]) {
            testsForLanguages.value[id] = '';
          }
        });

      } catch (error) {
        console.error('Error al cargar lenguajes:', error);
      }
    };

    // Caché para markdown renderizado
    const markdownCache = new Map();
    
    // Sistema de notificaciones 

    const notification = ref({
      show: false,
      type: 'success', // success o error
      title: '',
      message: '',
      timer: null
    });
    
    const loading = ref(false);
    
    // Determinar si estamos en modo edición
    const exerciseId = ref(null);
    const isEditing = computed(() => !!exerciseId.value);
    
    // Detectar si hay un ID de ejercicio en la ruta para edición
    onMounted(() => {
      configureMarkdown();
      loadAvailableLanguages();
      if (route.query.edit_id) {
        exerciseId.value = route.query.edit_id;
        loadExerciseData(exerciseId.value);
      }
    });
    
    // Variable para etiquetas ingresadas como texto
    const tagsInput = ref('');
    
    const form = ref({
      title: '',
      description: '',
      points: 30,
      difficulty: 'facil',
      credit: '',
      constraints: '',
      outputFormat: '',
      inputFormats: [''],
      sampleOutputs: [''],
      sampleInputs: [''],
      sampleExplanations: [''],
      advancedTests: '', 
      hint: '',
      type: 'practico',
      tags: [] // Propiedad para las etiquetas
    });

    // Método para procesar las etiquetas desde el input
    const processTagsFromInput = () => {
      if (!tagsInput.value.trim()) return;
      
      // Dividir por comas y procesar cada etiqueta
      const tagsList = tagsInput.value.split(',')
        .map(tag => tag.trim())
        .filter(tag => tag); // Eliminar tags vacíos
      
      // Agregar tags únicos (evitar duplicados)
      tagsList.forEach(tag => {
        if (!form.value.tags.includes(tag)) {
          form.value.tags.push(tag);
        }
      });
      
      // Limpiar el input
      tagsInput.value = '';
    };
    
    // Método para eliminar una etiqueta
    const removeTag = (index) => {
      form.value.tags.splice(index, 1);
    };
    
    // Sistema de notificaciones
    const showNotification = (type, title, message, timeout = 5000) => {
      // Limpiar cualquier timer existente
      if (notification.value.timer) {
        clearTimeout(notification.value.timer);
      }
      
      // Configurar la notificación
      notification.value = {
        show: true,
        type,
        title,
        message,
        timer: null
      };
      
      // Establecer temporizador para auto-cerrar
      notification.value.timer = setTimeout(() => {
        closeNotification();
      }, timeout);
    };
    
    const closeNotification = () => {
      if (notification.value.timer) {
        clearTimeout(notification.value.timer);
      }
      notification.value.show = false;
    };
    
    // Cargar datos del ejercicio para edición
    const loadExerciseData = async (id) => {
      if (!id) return;

      loading.value = true;
      try {
        const response = await exercisesService.getEjercicio(id);
        const exercise = response.data;

        if (!exercise) {
          console.error(`No se encontró el ejercicio con ID ${id}`);
          showNotification('error', 'Error al cargar', 'No se encontró el ejercicio solicitado');
          loading.value = false;
          return;
        }

        // Mapear datos del ejercicio al formulario
        form.value.title = exercise.titulo || '';
        form.value.description = exercise.descripcion || '';
        form.value.points = exercise.puntaje || 30;
        form.value.difficulty = exercise.dificultad || 'facil';
        form.value.credit = exercise.credito || '';
        form.value.type = exercise.tipo || 'practico';

        // Cargar etiquetas
        form.value.tags = exercise.etiquetas || [];

        // Procesar contenido JSON
        if (exercise.contenido) {
          const contenido = typeof exercise.contenido === 'string'
            ? JSON.parse(exercise.contenido)
            : exercise.contenido;

          form.value.constraints = contenido.restricciones || '';
          form.value.hint = contenido.pista || '';
          form.value.outputFormat = contenido.formato_salida || '';
          // Eliminar: form.value.template = contenido.template || '';

          // Cargar plantillas por lenguaje
          if (contenido.templates && typeof contenido.templates === 'object') {
            templatesForLanguages.value = contenido.templates;
            console.log('Plantillas por lenguaje cargadas:', Object.keys(templatesForLanguages.value).length);
          }

          // Procesar formatos de entrada
          if (contenido.formatos_entrada && Array.isArray(contenido.formatos_entrada)) {
            form.value.inputFormats = contenido.formatos_entrada.length > 0
              ? [...contenido.formatos_entrada]
              : [''];
          }

          // Procesar ejemplos
          if (contenido.ejemplos && Array.isArray(contenido.ejemplos)) {
            if (contenido.ejemplos.length > 0) {
              form.value.sampleInputs = contenido.ejemplos.map(e => e.entrada || '');
              form.value.sampleOutputs = contenido.ejemplos.map(e => e.salida || '');
              form.value.sampleExplanations = contenido.ejemplos.map(e => e.explicacion || '');
            }
          }
        }

        // Cargar tests por lenguaje
        if (exercise.tests_avanzados) {
          if (typeof exercise.tests_avanzados === 'object' && !Array.isArray(exercise.tests_avanzados)) {
            testsForLanguages.value = exercise.tests_avanzados;
            console.log('Tests por lenguaje cargados:', Object.keys(testsForLanguages.value).length);
          } else {
            // Convertir formato antiguo
            testsForLanguages.value = { '71': exercise.tests_avanzados || '' };
            console.log('Tests antiguos convertidos a formato por lenguaje');
          }
        }

        // Abrir secciones del acordeón para facilitar la edición
        openSections.value = {
          ...openSections.value,
          inputFormat: true,
          outputFormat: true,
          samples: true,
          templates: true  // Abre la sección de plantillas por lenguaje automáticamente
        };

        showNotification('success', 'Ejercicio cargado', 'Los datos del ejercicio se han cargado correctamente');

      } catch (error) {
        console.error('Error al cargar los datos del ejercicio:', error);
        showNotification('error', 'Error', 'Ocurrió un error al cargar los datos del ejercicio');
      } finally {
        loading.value = false;
      }
    };

    const resetForm = () => {
      form.value = {
        title: '',
        description: '',
        points: 30,
        difficulty: 'facil',
        credit: '',
        constraints: '',
        outputFormat: '',
        inputFormats: [''],
        sampleOutputs: [''],
        sampleInputs: [''],
        sampleExplanations: [''],
        //template: '',
        advancedTests: '',
        hint: '',
        type: 'practico',
        tags: []
      };
      
      // Limpiar input de etiquetas
      tagsInput.value = '';

       // Limpiar templates y tests por lenguaje
      templatesForLanguages.value = { '71': '' };
      testsForLanguages.value = { '71': '' };
    };

    // Control de secciones desplegables
    const openSections = ref({
      inputFormat: false,
      outputFormat: false,
      samples: false,
      advancedTests: false,
      templates: false // Sección para plantillas por lenguaje
    });

    const toggleSection = (section) => {
      openSections.value[section] = !openSections.value[section];
    };

    // Refs para editor y vista previa
    const editorRef = ref(null);
    const previewRef = ref(null);
    
    // Variables para sincronización de scroll mejorada
    let isScrolling = false;
    let scrollRatio = 0;
    let scrollRAF = null;
    let resizeObserver = null;
    
    // Caché y memoización para renderizado de markdown
    const markdownDescription = computed(() => {
      try {
        const description = form.value.description;
        if (!description) return '';
        
        // Usar caché para evitar re-renderizar el mismo contenido
        if (markdownCache.has(description)) {
          return markdownCache.get(description);
        }
        
        const renderedHTML = DOMPurify.sanitize(marked(description));
        markdownCache.set(description, renderedHTML);
        
        return renderedHTML;
      } catch (error) {
        console.error('Error al procesar markdown:', error);
        return '';
      }
    });

    // Controlador de scroll con requestAnimationFrame
    const handleEditorScroll = (event) => {
      if (isScrolling) return;
      
      const editor = editorRef.value;
      const preview = previewRef.value;
      
      if (!editor || !preview) return;
      
      // Calcular la proporción de desplazamiento
      const scrollHeight = editor.scrollHeight - editor.clientHeight;
      const currentPosition = editor.scrollTop;
      
      if (scrollHeight <= 0) return;
      
      // Calcular el ratio de scroll
      scrollRatio = currentPosition / scrollHeight;
      
      // Usar requestAnimationFrame para mejor rendimiento
      if (scrollRAF) {
        cancelAnimationFrame(scrollRAF);
      }
      
      scrollRAF = requestAnimationFrame(() => {
        const previewScrollHeight = preview.scrollHeight - preview.clientHeight;
        if (previewScrollHeight > 0) {
          isScrolling = true;
          preview.scrollTop = scrollRatio * previewScrollHeight;
          
          // Restablecer el bloqueo después de un breve retraso
          setTimeout(() => {
            isScrolling = false;
          }, 50);
        }
        scrollRAF = null;
      });
    };

    // Optimización para actualizar altura de la vista previa
    const updatePreviewHeight = () => {
      requestAnimationFrame(() => {
        const editor = editorRef.value;
        const preview = previewRef.value;
        
        if (editor && preview) {
          preview.style.height = `${editor.clientHeight}px`;
        }
      });
    };

    // Handlers para formato de entrada
    const addInputFormat = () => {
      form.value.inputFormats.push('');
    };

    const removeInputFormat = (index) => {
      form.value.inputFormats.splice(index, 1);
      if (form.value.inputFormats.length === 0) {
        form.value.inputFormats.push('');
      }
    };

    // Handlers para casos de prueba
    const addSampleSet = () => {
      form.value.sampleInputs.push('');
      form.value.sampleOutputs.push('');
      form.value.sampleExplanations.push('');
    };

    const removeSampleSet = (index) => {
      form.value.sampleInputs.splice(index, 1);
      form.value.sampleOutputs.splice(index, 1);
      form.value.sampleExplanations.splice(index, 1);
      
      if (form.value.sampleInputs.length === 0) {
        addSampleSet();
      }
    };

    // Funciones para la navegación
    const verEjercicios = () => {
      closeNotification();
      router.push('/docente/dashboard/repositorio-ejercicios');
    };

    const submitForm = async () => {
      try {
        // Procesar cualquier etiqueta restante en el campo de entrada
        if (tagsInput.value.trim()) {
          processTagsFromInput();
        }

        // Validaciones básicas
        if (!form.value.title.trim()) {
          showNotification('error', 'Error de validación', 'El título del ejercicio es obligatorio');
          return;
        }

        if (!form.value.description.trim()) {
          showNotification('error', 'Error de validación', 'La descripción del ejercicio es obligatoria');
          return;
        }

        // Preparar los datos del ejercicio para la API
        const ejercicioData = {
          titulo: form.value.title,
          descripcion: form.value.description,
          puntaje: form.value.points,
          tipo: 'practico',
          dificultad: form.value.difficulty,
          credito: form.value.credit,
          contenido: {
            restricciones: form.value.constraints,
            pista: form.value.hint,
            formato_salida: form.value.outputFormat,
            formatos_entrada: form.value.inputFormats,
            ejemplos: form.value.sampleInputs.map((input, index) => ({
              entrada: input,
              salida: form.value.sampleOutputs[index] || '',
              explicacion: form.value.sampleExplanations[index] || ''
            })),
            
            // Guardar las plantillas por lenguaje
            templates: templatesForLanguages.value,
            etiquetas: form.value.tags
          },
          // Guardar los tests por lenguaje directamente en tests_avanzados
          tests_avanzados: testsForLanguages.value,
          etiquetas: form.value.tags,
          templates_por_lenguaje: templatesForLanguages.value,
          tests_por_lenguaje: testsForLanguages.value,
          creador: store.getters['auth/userId']
        };

        console.log(`${isEditing.value ? "Actualizando" : "Enviando"} ejercicio:`, ejercicioData);

        let response;
        if (isEditing.value) {
          // Actualizar ejercicio
          response = await exercisesService.actualizarEjercicio(exerciseId.value, ejercicioData);
          showNotification('success', 'Ejercicio actualizado', 'El ejercicio se ha actualizado correctamente');
        } else {
          // Crear nuevo ejercicio
          response = await exercisesService.crearEjercicio(ejercicioData);
          showNotification('success', 'Ejercicio creado', 'El ejercicio se ha creado y está listo para usarse en evaluaciones');
          resetForm(); // Limpiar el formulario solo si fue creación
        }

        return response.data;
      } catch (error) {
        console.error(`Error al ${isEditing.value ? "actualizar" : "crear"} ejercicio:`, error);

        // Preparar mensaje de error detallado
        let errorMsg = `No se pudo ${isEditing.value ? "actualizar" : "crear"} el ejercicio.`;

        if (error.response && error.response.data) {
          errorMsg += ' Detalles: ';
          if (typeof error.response.data === 'object') {
            Object.entries(error.response.data).forEach(([key, value]) => {
              errorMsg += `${key}: ${value} `;
            });
          } else {
            errorMsg += error.response.data;
          }
        }

        showNotification('error', 'Error', errorMsg);
      }
    };

    // Sincronizar altura inicial y configurar observer
    onMounted(async () => {
      try {
        // Obtener ejercicios desde la API
        const responseEjercicios = await exercisesService.getEjercicios();
        if (responseEjercicios.data) {
          ejercicios.value = responseEjercicios.data;
        } else {
          ejercicios.value = [];
        }

        // Datos de cursos para ejemplo
        cursos.value = [
          { id: '1', nombre: 'Primero' },
          { id: '2', nombre: 'Segundo' },
          { id: '3', nombre: 'Tercero' },
          { id: '4', nombre: 'Cuarto' },
          { id: '5', nombre: 'Quinto' },
          { id: '6', nombre: 'Sexto' }
        ];
      } catch (error) {
        console.error('Error al cargar datos:', error);
        showNotification('error', 'Error de carga', 'No se pudieron cargar datos necesarios');
      }

      // Configurar observer para sincronizar alturas
      updatePreviewHeight();
      window.addEventListener('resize', updatePreviewHeight);
      
      if (window.ResizeObserver) {
        resizeObserver = new ResizeObserver(updatePreviewHeight);
        if (editorRef.value) {
          resizeObserver.observe(editorRef.value);
        }
      }
    });

    onBeforeUnmount(() => {
      // Limpiar observadores y event listeners
      if (resizeObserver) {
        resizeObserver.disconnect();
      }
      
      window.removeEventListener('resize', updatePreviewHeight);
      
      if (scrollRAF) {
        cancelAnimationFrame(scrollRAF);
      }
      
      // Limpiar cualquier timer de notificación
      if (notification.value.timer) {
        clearTimeout(notification.value.timer);
      }
    });

    // Manejar clics en enlaces de la vista previa (para el componente CreateExercise)
    const handlePreviewLinkClick = (event) => {
      const anchor = event.target.closest('a');
      if (anchor && anchor.hasAttribute('data-external')) {
        event.preventDefault();
        event.stopPropagation();

        const href = anchor.getAttribute('href');
        if (href && href !== '#') {
          window.open(href, '_blank', 'noopener,noreferrer');
        }

        return false;
      }
    };


    // Función para obtener el nombre del lenguaje seleccionado
    const getCurrentLanguageName = () => {
      const lang = availableLanguages.value.find(l => l.id === selectedLanguageForTests.value);
      return lang ? lang.name : `Lenguaje ID: ${selectedLanguageForTests.value}`;
    };

    // Función para obtener el nombre de un lenguaje por ID
    const getLanguageName = (langId) => {
      const parsedId = parseInt(langId);
      const lang = availableLanguages.value.find(l => l.id === parsedId);
      return lang ? lang.name : `Lenguaje ID: ${langId}`;
    };

    // Función para obtener un nombre corto del lenguaje
    const getLanguageShortName = (langId) => {
      const parsedId = parseInt(langId);

      // Mapeo personalizado para lenguajes principales (mantener consistencia)
      const nameMap = {
        71: 'Python', // Python 3.8.1
        70: 'Python 2', // Python 2.7.17
        63: 'JS', // JavaScript (Node)
        62: 'Java', // OpenJDK
        54: 'C++', // GCC 9.2.0
        53: 'C++ 8.3', // GCC 8.3.0
        52: 'C++ 7.4', // GCC 7.4.0
        76: 'C++ Clang', // Clang
        50: 'C', // GCC 9.2.0
        49: 'C 8.3', // GCC 8.3.0
        48: 'C 7.4', // GCC 7.4.0
        75: 'C Clang', // Clang
        51: 'C#', // Mono
        74: 'TypeScript',
        66: 'Octave',
        58: 'Erlang',
        55: 'Lisp',
        86: 'Clojure',
        46: 'Bash',
        45: 'Assembly',
        47: 'Basic',
        77: 'COBOL',
        79: 'Obj-C', // Objective-C
        82: 'SQL',
        84: 'VB.NET', // Visual Basic.Net
      };

      // Si existe en el mapeo predefinido, usarlo
      if (nameMap[parsedId]) {
        return nameMap[parsedId];
      }

      // Si no está en el mapeo, obtener el nombre completo
      const lang = availableLanguages.value.find(l => l.id === parsedId);

      if (!lang) {
        return `ID:${langId}`;
      }

      const fullName = lang.name;

      // Extraer nombre principal y versión
      const match = fullName.match(/^(.*?)(?:\s+\((.*?)\))?$/);
      if (match) {
        const [_, baseName, version] = match;

        // Acortar nombres largos
        let shortName = baseName.split(' ')[0];

        // Para lenguajes con compiladores específicos, añadir indicador
        if (version) {
          // Detectar compilador o versión distintiva
          if (version.includes('GCC')) {
            const gccVersion = version.match(/\d+\.\d+\.\d+/);
            if (gccVersion) {
              const majorMinor = gccVersion[0].split('.').slice(0, 2).join('.');
              return `${shortName} ${majorMinor}`;
            }
          } else if (version.includes('Clang')) {
            return `${shortName} Clang`;
          } else if (version.match(/^\d/)) {
            // Si la versión empieza con un número, usar la versión principal
            const mainVersion = version.split('.')[0];
            return `${shortName} ${mainVersion}`;
          }
        }

        return shortName;
      }

      // Si todo falla, devolver el nombre del lenguaje
      return fullName.length > 10 ? fullName.substring(0, 9) + '…' : fullName;
    };

    // Manejar cambio de lenguaje seleccionado
    const handleLanguageChange = () => {
      console.log(`Lenguaje para tests cambiado a: ${getCurrentLanguageName()} (ID: ${selectedLanguageForTests.value})`);

      // Inicializar tests para este lenguaje si no existe
      if (!testsForLanguages.value[selectedLanguageForTests.value]) {
        testsForLanguages.value[selectedLanguageForTests.value] = '';
      }
    };

    // Método de manejo de lenguajes
    const handleTemplateLanguageChange = () => {
      console.log(`Lenguaje para plantilla cambiado a: ${getCurrentLanguageName(selectedLanguageForTemplate.value)} (ID: ${selectedLanguageForTemplate.value})`);

      // Inicializar plantilla para este lenguaje si no existe
      if (!templatesForLanguages.value[selectedLanguageForTemplate.value]) {
        templatesForLanguages.value[selectedLanguageForTemplate.value] = '';
      }
    };


    // Método para obtener placeholder según el lenguaje
    const getTemplatePlaceholder = (langId) => {
      switch (parseInt(langId)) {
        case 71: // Python
          return `# Función para restar dos números
def restar(a, b):
    # Tu código aquí
    pass

# Puedes probar tu función
if __name__ == "__main__":
    print(restar(5, 3))`;
        case 50: // C (GCC 9.2.0)
          return `#include <stdio.h>

// Función para restar dos números
int restar(int a, int b) {
    // Tu código aquí
    return 0;
}

int main() {
    printf("%d\\n", restar(5, 3));
    return 0;
}`;
        case 63: // JavaScript
          return `// Función para restar dos números
function restar(a, b) {
    // Tu código aquí
    return 0;
}

// Prueba de la función
console.log(restar(5, 3));`;
        default:
          return `// Plantilla para ${getLanguageName(langId)}
// Implementa una función que reste dos números`;
      }
    };

    // Obtener placeholder según el lenguaje
    const getTestPlaceholder = (langId) => {
      switch (parseInt(langId)) {
        case 71: // Python
          return `# Tests para verificar la solución en Python
def run_tests():
    # Casos básicos
    test(suma_numeros([1, 2, 3]), 6, 'Suma de números positivos')
    test(suma_numeros([]), 0, 'Lista vacía')
    
    # Casos límite
    test(suma_numeros([-1, -2, -3]), -6, 'Suma de números negativos')
    
# Función auxiliar para tests
def test(actual, expected, message=''):
    if actual == expected:
        print(f'✓ CORRECTO: {message}')
    else:
        print(f'✗ INCORRECTO: {message}')
        print(f'  Esperado: {expected}')
        print(f'  Obtenido: {actual}')

# Ejecutar tests
run_tests()`;
        case 63: // JavaScript
          return `// Tests para verificar la solución en JavaScript
function runTests() {
    // Casos básicos
    test(sumaNumeros([1, 2, 3]), 6, 'Suma de números positivos');
    test(sumaNumeros([]), 0, 'Lista vacía');
    
    // Casos límite
    test(sumaNumeros([-1, -2, -3]), -6, 'Suma de números negativos');
}

// Función auxiliar para tests
function test(actual, expected, message = '') {
    if (actual === expected) {
        console.log(\`✓ CORRECTO: \${message}\`);
    } else {
        console.log(\`✗ INCORRECTO: \${message}\`);
        console.log(\`  Esperado: \${expected}\`);
        console.log(\`  Obtenido: \${actual}\`);
    }
}

// Ejecutar tests
runTests();`;
        case 62: // Java
          return `// Tests para verificar la solución en Java
public class TestRunner {
    public static void main(String[] args) {
        // Casos básicos
        test(sumaNumeros(new int[]{1, 2, 3}), 6, "Suma de números positivos");
        test(sumaNumeros(new int[]{}), 0, "Lista vacía");
        
        // Casos límite
        test(sumaNumeros(new int[]{-1, -2, -3}), -6, "Suma de números negativos");
        
        System.out.println("Resultado: " + resultadoTests + "/" + totalTests + " pruebas pasadas");
    }
    
    static int resultadoTests = 0;
    static int totalTests = 0;
    
    public static void test(int actual, int expected, String message) {
        totalTests++;
        if (actual == expected) {
            resultadoTests++;
            System.out.println("✓ CORRECTO: " + message);
        } else {
            System.out.println("✗ INCORRECTO: " + message);
            System.out.println("  Esperado: " + expected);
            System.out.println("  Obtenido: " + actual);
        }
    }
}`;
        default:
          return `// Tests para verificar la solución
// Añade los tests específicos para este lenguaje aquí`;
      }
    };


    return {
      form,
      openSections,
      toggleSection,
      markdownDescription,
      addInputFormat,
      handlePreviewLinkClick,
      removeInputFormat,
      addSampleSet,
      removeSampleSet,
      submitForm,
      resetForm,
      editorRef,
      previewRef,
      handleEditorScroll,
      isEditing,
      loading,
      
      // Sistema de notificaciones
      notification,
      showNotification,
      closeNotification,
      verEjercicios,
      
      // Sistema de etiquetas
      tagsInput,
      processTagsFromInput,
      removeTag,

      // Soporte para tests en múltiples lenguajes
      availableLanguages,
      selectedLanguageForTests,
      testsForLanguages,
      getCurrentLanguageName,
      getLanguageName,
      getLanguageShortName,
      handleLanguageChange,
      getTestPlaceholder,

      // Para la plantilla del codigo
      selectedLanguageForTemplate,
      templatesForLanguages,
      handleTemplateLanguageChange,
      getTemplatePlaceholder
    };
  }
});
</script>

<style>
/* =================== ESTILOS GLOBALES (SIN SCOPED) =================== */
.fade-enter-active,
.fade-leave-active {
  transition: opacity var(--transition-smooth), transform var(--transition-smooth);
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
  transform: translateY(-10px);
}

.create-exercise-wrapper .button,
.create-exercise-wrapper .input,
.create-exercise-wrapper .textarea,
.create-exercise-wrapper .select select {
  background-color: var(--color-bg-main);
  border: 2px solid var(--color-bg-element-hover);
  border-radius: var(--border-radius);
  color: var(--color-text-primary);
  box-shadow: none;
}

.create-exercise-wrapper .button:hover {
  background-color: var(--color-primary);
  color: var(--color-bg-main);
}

.create-exercise-wrapper .button:focus,
.create-exercise-wrapper .input:focus,
.create-exercise-wrapper .textarea:focus,
.create-exercise-wrapper .select select:focus {
  border-color: var(--color-secondary);
  box-shadow: 0 0 0 3px rgba(138, 79, 255, 0.25);
}

.create-exercise-wrapper .label {
  color: var(--color-text-primary);
  font-weight: bold;
}

.create-exercise-wrapper .help {
  color: var(--color-text-muted);
}

.create-exercise-wrapper .select select option {
  background-color: var(--color-bg-main);
  color: var(--color-text-primary);
}

.create-exercise-wrapper .box {
  background-color: var(--color-bg-element);
  border-radius: var(--border-radius-lg);
  box-shadow: var(--shadow-lg);
}

.create-exercise-wrapper .title,
.create-exercise-wrapper .subtitle {
  color: inherit;
}

.create-exercise-wrapper .loading-container {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 4rem 0;
  color: var(--color-text-primary);
}

.create-exercise-wrapper .loading-circle {
  width: 50px;
  height: 50px;
  border: 5px solid var(--color-bg-element);
  border-top: 5px solid var(--color-primary);
  border-radius: 50%;
  animation: spin 1s linear infinite;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}
</style>

<style scoped>
/* =================== CONTENEDOR PRINCIPAL =================== */
.create-exercise-wrapper {
  background-color: var(--color-bg-main);
  min-height: 100vh;
  color: var(--color-text-primary);
  display: flex;
  justify-content: center;
  width: 100%;
  padding: 1rem;
  box-sizing: border-box;
  font-family: 'Poppins', 'Segoe UI', sans-serif;
  position: relative;
}

.form-container {
  width: 100%;
  max-width: 1200px;
  padding: 2rem;
  background-color: var(--color-bg-main);
  border-radius: var(--border-radius-lg);
  border-top: 4px solid var(--color-primary);
  box-shadow: var(--shadow-lg);
  will-change: transform;
  overflow: visible;
}

/* =================== HEADER =================== */
.header {
  margin-bottom: 2.5rem;
  padding-bottom: 1.5rem;
  border-bottom: 1px solid var(--color-border);
}

.header-content {
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.header-text {
  flex: 1;
}

.header-text .title {
  margin-bottom: 0.5rem;
  font-weight: 600;
  color: var(--color-text-primary);
  font-size: 1.8rem;
}

.header-text .subtitle {
  color: var(--color-text-secondary);
  font-weight: 400;
  max-width: 80%;
  font-size: 1.2rem;
}

.header-icon {
  margin-left: 1.5rem;
}

.icon-container {
  background-color: var(--color-primary);
  color: var(--color-bg-main);
  width: 64px;
  height: 64px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: var(--border-radius);
  font-size: 2rem;
  box-shadow: 0 2px 8px rgba(235, 179, 0, 0.3);
  border: 2px solid var(--color-primary-light);
}

/* =================== FORMULARIO =================== */
.form {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}

.form-group {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
  margin-bottom: 0.5rem;
}

.form-label {
  font-size: 1.15rem;
  font-weight: 600;
  display: flex;
  align-items: center;
  color: var(--color-text-primary);
  margin-bottom: 0.3rem;
}

.icon-prefix {
  margin-right: 0.5rem;
  color: var(--color-secondary);
  font-size: 1.1rem;
}

.helper-text {
  font-size: 0.9rem;
  color: var(--color-text-muted);
  margin-top: 0.25rem;
  font-style: italic;
}

.form-input, 
.form-textarea {
  width: 100%;
  padding: 0.75rem;
  background-color: var(--color-bg-element);
  border: 1px solid var(--color-border);
  border-radius: var(--border-radius);
  color: var(--color-text-primary);
  font-size: 1.05rem;
  transition: all var(--transition-fast);
  resize: vertical;
}

.form-input:focus, 
.form-textarea:focus {
  outline: none;
  border-color: var(--color-secondary);
  box-shadow: 0 0 0 3px rgba(138, 79, 255, 0.25);
}

.form-input::placeholder, 
.form-textarea::placeholder {
  color: var(--color-text-disabled);
}

/* =================== SECCIÓN DE MARKDOWN =================== */
.markdown-form-group {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
  margin-bottom: 1.5rem;
}

.markdown-container {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 1rem;
  min-height: 300px;
  height: auto;
}

.input-wrapper, 
.preview-wrapper {
  display: flex;
  flex-direction: column;
  position: relative;
}

.preview-label {
  position: absolute;
  top: -0.9rem;
  right: 1rem;
  background-color: var(--color-secondary);
  color: var(--color-text-primary);
  padding: 0.2rem 0.6rem;
  border-radius: 1rem;
  font-size: 0.75rem;
  z-index: 5;
  font-weight: bold;
}

.markdown-container .form-textarea, 
.markdown-container .markdown-preview {
  min-height: 300px;
  height: auto;
  overflow-y: auto;
  resize: vertical;
}

.markdown-preview {
  background-color: var(--color-bg-element);
  border: 1px solid var(--color-border);
  border-radius: var(--border-radius);
  padding: 0.75rem;
  overflow-y: auto;
}

.markdown-preview h1, 
.markdown-preview h2, 
.markdown-preview h3 {
  color: var(--color-primary);
  margin-top: 1rem;
  margin-bottom: 0.5rem;
}

.markdown-preview code {
  background-color: var(--color-bg-darker);
  padding: 0.2rem 0.4rem;
  border-radius: 0.3rem;
  font-family: monospace;
}

.markdown-preview pre {
  background-color: var(--color-bg-darker);
  padding: 1rem;
  border-radius: 0.5rem;
  overflow-x: auto;
}

/* =================== ACORDEÓN =================== */
.accordion-sections {
  display: flex;
  flex-direction: column;
  gap: 1rem;
  margin: 1.5rem 0;
}

.accordion-item {
  border: 1px solid var(--color-border);
  border-radius: var(--border-radius);
  overflow: hidden;
  transition: all var(--transition-fast);
}

.accordion-item:hover {
  border-color: var(--color-secondary);
}

.accordion-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1rem;
  background-color: var(--color-bg-element);
  cursor: pointer;
  user-select: none;
}

.accordion-title {
  font-size: 1.15rem;
  font-weight: 600;
  margin: 0;
  display: flex;
  align-items: center;
  color: var(--color-text-primary);
}

.accordion-icon {
  font-size: 1.35rem;
  color: var(--color-primary);
}

.section-hint {
  color: var(--color-text-muted);
  font-size: 0.95rem;
  margin-bottom: 1rem;
  font-style: italic;
}

.accordion-content {
  padding: 1.25rem;
  background-color: var(--color-bg-main);
}

/* =================== ENTRADAS MÚLTIPLES =================== */
.multi-input-container {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.multi-input-item {
  display: flex;
  gap: 0.5rem;
}

.delete-button {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 2.5rem;
  height: 2.5rem;
  border-radius: 50%;
  background-color: var(--color-coral);
  color: var(--color-text-primary);
  border: none;
  cursor: pointer;
  transition: all var(--transition-fast);
}

.delete-button:hover {
  background-color: var(--color-error);
  transform: translateY(-2px);
}

.delete-icon {
  font-size: 1.25rem;
}

.sr-only {
  position: absolute;
  width: 1px;
  height: 1px;
  padding: 0;
  margin: -1px;
  overflow: hidden;
  clip: rect(0, 0, 0, 0);
  white-space: nowrap;
  border-width: 0;
}

/* =================== EJEMPLOS DE PRUEBA =================== */
.samples-container {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}

.sample-card {
  border: 1px solid var(--color-border);
  border-radius: var(--border-radius);
  overflow: hidden;
  transition: all var(--transition-fast);
}

.sample-card:hover {
  border-color: var(--color-teal);
  box-shadow: 0 4px 10px rgba(62, 207, 178, 0.15);
}

.sample-card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0.75rem 1rem;
  background-color: var(--color-bg-element);
}

.sample-card-title {
  font-size: 1.15rem;
  font-weight: 600;
  margin: 0;
  display: flex;
  align-items: center;
  color: var(--color-text-primary);
}

.sample-card-content {
  padding: 1.25rem;
  display: flex;
  flex-direction: column;
  gap: 1.25rem;
  background-color: var(--color-bg-element-alt);
}

.sample-label {
  display: flex;
  align-items: center;
  font-size: 1.05rem;
  font-weight: 500;
  margin-bottom: 0.4rem;
  color: var(--color-text-secondary);
}

/* =================== BOTONES =================== */
.add-button {
  padding: 0.7rem 1.25rem;
  background-color: var(--color-secondary-dark);
  color: var(--color-text-primary);
  border: none;
  border-radius: var(--border-radius);
  font-size: 1rem;
  font-weight: 600;
  cursor: pointer;
  transition: all var(--transition-fast);
  align-self: flex-start;
  margin-top: 0.75rem;
  display: flex;
  align-items: center;
  gap: 0.5rem;
  box-shadow: var(--shadow-sm);
}

.add-button:hover {
  background-color: var(--color-secondary);
  transform: translateY(-2px);
  box-shadow: var(--shadow);
}

.form-actions {
  display: flex;
  justify-content: flex-end;
  margin-top: 2rem;
  border-top: 1px solid var(--color-border);
  padding-top: 1.5rem;
}

.submit-button {
  padding: 0.85rem 2.25rem;
  background-color: var(--color-primary);
  color: var(--color-bg-main);
  border: none;
  border-radius: var(--border-radius);
  font-size: 1.2rem;
  font-weight: 700;
  cursor: pointer;
  transition: all var(--transition-smooth);
  display: flex;
  align-items: center;
  gap: 0.5rem;
  box-shadow: var(--shadow);
}

.submit-button:hover {
  background-color: var(--color-primary-light);
  transform: translateY(-3px);
  box-shadow: var(--shadow-lg);
}

/* =================== SECCIÓN DE TESTS =================== */
.test-container {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 1rem;
}

.test-template-info {
  background-color: var(--color-bg-element);
  padding: 15px;
  border-radius: var(--border-radius);
  font-size: 0.9rem;
}

.test-template-info h4 {
  color: var(--color-primary);
  margin-bottom: 10px;
}

.test-types-list {
  list-style: disc;
  padding-left: 1.5rem;
  margin-bottom: 1rem;
}

.test-types-list li {
  margin-bottom: 0.5rem;
}

.test-types-list strong {
  color: var(--color-teal);
}

.language-selector-container {
  margin-bottom: 1.5rem;
  display: flex;
  align-items: center;
  gap: 12px;
  flex-wrap: wrap;
}

.language-select {
  background-color: var(--color-bg-element-hover);
  color: var(--color-text-secondary);
  border: 1px solid var(--color-bg-element-active);
  border-radius: var(--border-radius);
  padding: 8px 12px;
  font-size: 14px;
  appearance: none;
  padding-right: 28px;
  cursor: pointer;
  transition: all var(--transition-smooth) ease;
  min-width: 200px;
  position: relative;
  background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24' width='24' height='24'%3E%3Cpath fill='none' d='M0 0h24v24H0z'/%3E%3Cpath d='M12 15l-5-5h10l-5 5z' fill='rgba(255,255,255,0.5)'/%3E%3C/svg%3E");
  background-repeat: no-repeat;
  background-position: right 8px center;
}

.language-select:hover {
  background-color: var(--color-bg-element-active);
  color: var(--color-text-primary);
  border-color: var(--color-secondary);
}

.language-select:focus {
  outline: none;
  box-shadow: 0 0 0 2px rgba(138, 79, 255, 0.3);
  border-color: var(--color-secondary);
}

.language-count {
  font-size: 0.9rem;
  color: var(--color-text-muted);
}

.supported-languages {
  margin-top: 1.5rem;
  padding-top: 1rem;
  border-top: 1px solid var(--color-border);
}

.supported-label {
  display: block;
  font-size: 0.9rem;
  color: var(--color-text-secondary);
  margin-bottom: 0.5rem;
}

.language-tag-container {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
  margin-top: 8px;
}

.language-tag {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  padding: 4px 10px;
  background-color: var(--color-bg-element-hover);
  border-radius: 12px;
  font-size: 0.8rem;
  color: var(--color-text-muted);
  border: 1px solid var(--color-border);
  max-width: 100px;
  min-width: 40px;
  height: 24px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  margin: 3px;
  transition: all var(--transition-fast) ease;
}

.language-tag.active {
  background-color: var(--color-secondary-dark);
  color: var(--color-text-primary);
  border-color: var(--color-secondary);
  font-weight: 500;
}

.language-tag:hover {
  transform: translateY(-1px);
  box-shadow: var(--shadow-sm);
}

/* =================== ETIQUETAS =================== */
.tags-section {
  margin-bottom: 1.5rem;
}

.tags-input-container {
  position: relative;
  margin-bottom: 0.5rem;
}

.selected-tags-container {
  display: flex;
  flex-wrap: wrap;
  gap: 0.5rem;
  margin-top: 0.75rem;
}

.tag-item {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.35rem 0.75rem;
  background-color: var(--color-secondary-dark);
  color: var(--color-text-primary);
  border-radius: 2rem;
  font-size: 0.85rem;
  font-weight: 500;
  transition: all var(--transition-fast);
}

.tag-item:hover {
  background-color: var(--color-secondary);
  transform: translateY(-2px);
  box-shadow: var(--shadow-sm);
}

.tag-remove {
  background: none;
  border: none;
  color: var(--color-text-primary);
  font-size: 1.2rem;
  cursor: pointer;
  line-height: 1;
  padding: 0;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: transform var(--transition-fast);
}

.tag-remove:hover {
  transform: scale(1.2);
}

/* =================== NOTIFICACIONES =================== */
.notification {
  position: fixed;
  top: 20px;
  right: 20px;
  background-color: var(--color-bg-element);
  border-left: 4px solid var(--color-primary);
  color: var(--color-text-primary);
  padding: 1.5rem;
  border-radius: var(--border-radius-lg);
  box-shadow: var(--shadow-lg);
  z-index: 1000;
  width: 350px;
  animation: slideIn var(--transition-smooth) ease-out;
}

.notification-success {
  border-left-color: var(--color-success);
}

.notification-error {
  border-left-color: var(--color-error);
}

.notification-warning {
  border-left-color: var(--color-warning);
}

.notification-info {
  border-left-color: var(--color-info);
}

.notification-header {
  display: flex;
  align-items: center;
  margin-bottom: 1rem;
}

.notification-icon {
  width: 24px;
  height: 24px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1rem;
  margin-right: 0.75rem;
}

.notification-success .notification-icon {
  background-color: var(--color-success);
  color: var(--color-bg-main);
}

.notification-error .notification-icon {
  background-color: var(--color-error);
  color: var(--color-text-primary);
}

.notification-title {
  font-weight: 600;
  font-size: 1.25rem;
  color: var(--color-text-primary);
}

.notification-content {
  margin-bottom: 1rem;
  font-size: 1.05rem;
  color: var(--color-text-secondary);
  line-height: 1.5;
}

.notification-actions {
  display: flex;
  justify-content: flex-end;
}

.notification-button {
  padding: 0.6rem 1.2rem;
  background-color: var(--color-teal);
  color: var(--color-bg-main);
  border: none;
  border-radius: var(--border-radius);
  font-weight: 600;
  font-size: 1rem;
  cursor: pointer;
  transition: all var(--transition-fast);
}

.notification-success .notification-button {
  background-color: var(--color-success);
}

.notification-error .notification-button {
  background-color: var(--color-bg-lighter);
  color: var(--color-text-primary);
}

.notification-button:hover {
  filter: brightness(1.1);
  transform: translateY(-2px);
}

.notification-close {
  position: absolute;
  top: 12px;
  right: 12px;
  background: none;
  border: none;
  color: var(--color-text-muted);
  font-size: 1.5rem;
  cursor: pointer;
  transition: color var(--transition-fast);
}

.notification-close:hover {
  color: var(--color-text-primary);
}

/* =================== ANIMACIONES =================== */
@keyframes slideIn {
  from {
    transform: translateX(100%);
    opacity: 0;
  }
  to {
    transform: translateX(0);
    opacity: 1;
  }
}

/* =================== RESPONSIVE =================== */
@media (max-width: 1024px) {
  .form-container {
    max-width: 95%;
  }
  
  .test-container {
    grid-template-columns: 1fr;
  }

  .markdown-container {
    grid-template-columns: 1fr;
  }
}

@media (max-width: 768px) {
  .create-exercise-wrapper {
    padding: 1rem;
  }
  
  .form-container {
    padding: 1.5rem;
  }
  
  .header-content {
    flex-direction: column;
  }
  
  .header-text {
    text-align: center;
    margin-bottom: 1rem;
  }
  
  .header-text .title,
  .header-text .subtitle {
    max-width: 100%;
  }
}

@media (max-width: 640px) {
  .form-container {
    padding: 1rem;
  }
  
  .submit-button {
    width: 100%;
    justify-content: center;
  }
  
  .notification {
    width: calc(100% - 40px);
    right: 20px;
  }
}
</style>