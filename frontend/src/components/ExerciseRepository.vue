<!-- components/ExerciseRepository.vue -->
<template>
  <div class="exercise-repository-wrapper">
    <div class="exercise-repository">
      <!-- Cabecera con título y descripción -->
      <div class="repository-header custom-header">
        <h1 class="title is-3 has-text-weight-bold mb-4">
          <i class="fas fa-book mr-3"></i>Banco de Ejercicios
        </h1>
        <p class="subtitle is-6 has-text-grey mt-3 mb-5">Explora y gestiona tu colección de ejercicios para evaluaciones</p>
      </div>

      <!-- Panel de filtros y búsqueda -->
      <div class="filter-panel box">
        <div class="field has-addons">
          <div class="control has-icons-left is-expanded">
            <input 
              class="input is-medium search-input" 
              type="text" 
              v-model="searchQuery" 
              placeholder="Buscar por título, descripción, contenido..." 
              @input="filterExercises"
            >
            <span class="icon is-left">
              <i class="fas fa-search"></i>
            </span>
          </div>
          <div class="control">
            <button class="button is-medium clean-button" :class="isFiltering ? 'is-active' : ''" @click="clearFilters">
              <span class="icon">
                <i class="fas fa-times"></i>
              </span>
              <span>Limpiar</span>
            </button>
          </div>
        </div>

        <div class="filter-controls columns is-multiline mt-2">
          <div class="column is-3-desktop is-6-tablet">
            <div class="field">
              <label class="label is-small">Dificultad</label>
              <div class="control">
                <div class="select is-fullwidth">
                  <select v-model="difficultyFilter" @change="filterExercises">
                    <option value="all">Todas las dificultades</option>
                    <option value="facil">Fácil</option>
                    <option value="intermedio">Intermedio</option>
                    <option value="dificil">Difícil</option>
                  </select>
                </div>
              </div>
            </div>
          </div>
          <div class="column is-3-desktop is-6-tablet">
            <div class="field">
              <label class="label is-small">Tipo</label>
              <div class="control">
                <div class="select is-fullwidth">
                  <select v-model="typeFilter" @change="filterExercises">
                    <option value="all">Todos los tipos</option>
                    <option value="practico">Práctico</option>
                    <option value="teorico">Teórico</option>
                  </select>
                </div>
              </div>
            </div>
          </div>
          <div class="column is-6-desktop is-12-tablet">
            <div class="field">
              <label class="label is-small">Creador</label>
              <div class="control">
                <div class="select">
                  <select v-model="creatorFilter" @change="filterExercises">
                    <option value="all">Todos los creadores</option>
                    <option value="mine">Mis ejercicios</option>
                    <option v-for="creator in uniqueCreators" :key="creator.id" :value="creator.id">
                      {{ creator.nombre }}
                    </option>
                  </select>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Estado de carga -->
      <div class="loading-container" v-if="loading">
        <div class="loading-circle"></div>
        <p class="has-text-centered mt-4">Cargando ejercicios...</p>
      </div>

      <!-- Estado vacío -->
      <div class="empty-state" v-else-if="filteredExercises.length === 0">
        <div class="box has-text-centered py-6">
          <span class="icon is-large">
            <i class="fas fa-folder-open fa-3x has-text-grey-light"></i>
          </span>
          <h2 class="title is-4 mt-4">No se encontraron ejercicios</h2>
          <p class="subtitle is-6 has-text-grey mt-2" v-if="isFiltering">
            No hay ejercicios que coincidan con los filtros seleccionados
          </p>
          <p class="subtitle is-6 has-text-grey mt-2" v-else>
            Aún no hay ejercicios creados en el sistema
          </p>
          <div class="buttons is-centered mt-4">
            <button class="button is-primary" @click="clearFilters" v-if="isFiltering">
              <span class="icon">
                <i class="fas fa-times"></i>
              </span>
              <span>Limpiar filtros</span>
            </button>
            <button class="button is-primary" @click="navigateToCreateExercise" v-else>
              <span class="icon">
                <i class="fas fa-plus"></i>
              </span>
              <span>Crear nuevo ejercicio</span>
            </button>
          </div>
        </div>
      </div>

      <!-- Grid de ejercicios -->
      <div class="exercises-grid columns is-multiline" v-else>
        <div v-for="exercise in filteredExercises" :key="exercise.id" class="column is-3-widescreen is-4-desktop is-6-tablet">
          <div class="exercise-card">
            <div class="card-header" :class="getDifficultyClass(exercise.dificultad)">
              <div class="difficulty-badge">
                <i :class="getDifficultyIcon(exercise.dificultad)"></i>
                {{ getDifficultyLabel(exercise.dificultad) }}
              </div>
              <div class="exercise-type">
                <i :class="exercise.tipo === 'practico' ? 'fas fa-code' : 'fas fa-book'"></i>
                {{ exercise.tipo === 'practico' ? 'Práctico' : 'Teórico' }}
              </div>
            </div>
            
            <div class="card-body">
              <h3 class="card-title">{{ exercise.titulo }}</h3>
              <p class="card-description">{{ truncateText(exercise.descripcion, 120) }}</p>
              
              <div class="tags">
                <span class="tag" v-for="(tag, index) in getTags(exercise)" :key="index">
                  {{ tag }}
                </span>
              </div>
            </div>
            
            <div class="card-footer">
              <div class="meta-info">
                <span class="meta-item" title="Creador">
                  <i class="fas fa-user"></i> {{ exercise.creador_nombre || 'Desconocido' }}
                </span>
                <span class="meta-item" title="Puntaje">
                  <i class="fas fa-star"></i> {{ exercise.puntaje || '1' }} pts
                </span>
              </div>
              
              <div class="card-actions">
                <button class="action-btn view" title="Ver detalles" @click="openExerciseDetails(exercise)">
                  <i class="fas fa-eye"></i>
                </button>
                <button class="action-btn edit" title="Editar ejercicio" @click="editExercise(exercise)">
                  <i class="fas fa-pencil-alt"></i>
                </button>
                <button class="action-btn delete" title="Eliminar ejercicio" @click="confirmDelete(exercise)">
                  <i class="fas fa-trash"></i>
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Paginación -->
      <div class="pagination-wrapper" v-if="filteredExercises.length > 0">
        <nav class="pagination is-centered is-small custom-pagination" role="navigation" aria-label="pagination">
          <ul class="pagination-list">
            <li>
              <a class="pagination-link pagination-previous" :class="{ 'is-disabled': currentPage === 1 }" 
                 :disabled="currentPage === 1" @click="currentPage > 1 && currentPage--">
                <span class="nav-icon">&#8592;</span>
                <span class="pagination-text">Anterior</span>
              </a>
            </li>
            
            <li v-for="page in paginationItems" :key="page.value">
              <a 
                v-if="page.type === 'page'" 
                class="pagination-link" 
                :class="{ 'is-current': page.value === currentPage }"
                @click="currentPage = page.value"
              >
                {{ page.value }}
              </a>
              <span v-else class="pagination-ellipsis">&hellip;</span>
            </li>
            
            <li>
              <a class="pagination-link pagination-next" :class="{ 'is-disabled': currentPage === totalPages }" 
                 :disabled="currentPage === totalPages" @click="currentPage < totalPages && currentPage++">
                <span class="pagination-text">Siguiente</span>
                <span class="nav-icon">&#8594;</span>
              </a>
            </li>
          </ul>
        </nav>
      </div>

      <!-- Modal de vista previa de ejercicio (Azul celeste) -->
      <div class="modal" :class="{ 'is-active': showDetailsModal }">
        <div class="modal-background" @click="showDetailsModal = false"></div>
        <div class="modal-card details-modal">
          <header class="modal-card-head details-modal-head" :class="selectedExercise ? getDifficultyClass(selectedExercise.dificultad) : ''">
            <p class="modal-card-title">
              {{ selectedExercise ? selectedExercise.titulo : 'Detalles del Ejercicio' }}
            </p>
            <button class="delete" aria-label="close" @click="showDetailsModal = false"></button>
          </header>
          <section class="modal-card-body" v-if="selectedExercise">
            <!-- Información principal y etiquetas -->
            <div class="tags mb-4">
              <span class="tag is-medium" :class="getDifficultyTagClass(selectedExercise.dificultad)">
                <i :class="getDifficultyIcon(selectedExercise.dificultad)" class="mr-1"></i>
                {{ getDifficultyLabel(selectedExercise.dificultad) }}
              </span>
              <span class="tag is-medium" :class="selectedExercise.tipo === 'practico' ? 'is-info' : 'is-success'">
                <i :class="selectedExercise.tipo === 'practico' ? 'fas fa-code' : 'fas fa-book'" class="mr-1"></i>
                {{ selectedExercise.tipo === 'practico' ? 'Práctico' : 'Teórico' }}
              </span>
              <span class="tag is-medium is-primary">
                <i class="fas fa-star mr-1"></i> {{ selectedExercise.puntaje || '1' }} pts
              </span>
            </div>
            
            <!-- Secciones en acordeón -->
            <div class="exercise-accordion">
              <!-- Descripción -->
              <div class="accordion-item">
                <div class="accordion-header" @click="toggleExerciseSection('description')">
                  <h3 class="accordion-title">
                    <i class="fas fa-align-left icon-prefix"></i> Descripción
                  </h3>
                  <span class="accordion-icon">{{ openExerciseSections.description ? '−' : '+' }}</span>
                </div>
                <div class="accordion-content" v-if="openExerciseSections.description">
                  <div class="content markdown-content" v-html="renderMarkdown(selectedExercise.descripcion)"></div>
                </div>
              </div>
              
              <!-- Información general -->
              <div class="accordion-item">
                <div class="accordion-header" @click="toggleExerciseSection('general')">
                  <h3 class="accordion-title">
                    <i class="fas fa-info-circle icon-prefix"></i> Información General
                  </h3>
                  <span class="accordion-icon">{{ openExerciseSections.general ? '−' : '+' }}</span>
                </div>
                <div class="accordion-content" v-if="openExerciseSections.general">
                  <div class="general-info">
                    <div class="info-item">
                      <span class="info-label">Creador:</span>
                      <span class="info-value">{{ selectedExercise.creador_nombre || 'Desconocido' }}</span>
                    </div>
                    <div class="info-item">
                      <span class="info-label">Fecha de creación:</span>
                      <span class="info-value">{{ formatDate(selectedExercise.fecha_creacion) }}</span>
                    </div>
                    <div class="info-item">
                      <span class="info-label">Puntos:</span>
                      <span class="info-value">{{ selectedExercise.puntaje || '1' }}</span>
                    </div>
                    <div class="info-item">
                      <span class="info-label">Tipo:</span>
                      <span class="info-value">{{ selectedExercise.tipo === 'practico' ? 'Práctico' : 'Teórico' }}</span>
                    </div>
                    <div class="info-item">
                      <span class="info-label">Dificultad:</span>
                      <span class="info-value">{{ getDifficultyLabel(selectedExercise.dificultad) }}</span>
                    </div>
                    <div class="info-item" v-if="selectedExercise.credito">
                      <span class="info-label">Fuente/Crédito:</span>
                      <span class="info-value">{{ selectedExercise.credito }}</span>
                    </div>
                    <div class="info-item">
                      <span class="info-label">Etiquetas:</span>
                      <div class="info-value tags">
                        <span v-if="getTags(selectedExercise).length === 0" class="has-text-grey-light">Sin etiquetas</span>
                        <span class="tag" v-for="(tag, index) in getTags(selectedExercise)" :key="index">
                          {{ tag }}
                        </span>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
              
              <!-- Restricciones -->
              <div class="accordion-item" v-if="getRestrictions(selectedExercise)">
                <div class="accordion-header" @click="toggleExerciseSection('restrictions')">
                  <h3 class="accordion-title">
                    <i class="fas fa-puzzle-piece icon-prefix"></i> Restricciones
                  </h3>
                  <span class="accordion-icon">{{ openExerciseSections.restrictions ? '−' : '+' }}</span>
                </div>
                <div class="accordion-content" v-if="openExerciseSections.restrictions">
                  <div class="content">
                    <p>{{ getRestrictions(selectedExercise) }}</p>
                  </div>
                </div>
              </div>
              
              <!-- Pista -->
              <div class="accordion-item" v-if="getHint(selectedExercise)">
                <div class="accordion-header" @click="toggleExerciseSection('hint')">
                  <h3 class="accordion-title">
                    <i class="fas fa-lightbulb icon-prefix"></i> Pista
                  </h3>
                  <span class="accordion-icon">{{ openExerciseSections.hint ? '−' : '+' }}</span>
                </div>
                <div class="accordion-content" v-if="openExerciseSections.hint">
                  <div class="content">
                    <p>{{ getHint(selectedExercise) }}</p>
                  </div>
                </div>
              </div>
              
              <!-- Formato de Entrada -->
              <div class="accordion-item" v-if="getInputFormats(selectedExercise).length > 0">
                <div class="accordion-header" @click="toggleExerciseSection('inputFormat')">
                  <h3 class="accordion-title">
                    <i class="fas fa-keyboard icon-prefix"></i> Formato de Entrada
                  </h3>
                  <span class="accordion-icon">{{ openExerciseSections.inputFormat ? '−' : '+' }}</span>
                </div>
                <div class="accordion-content" v-if="openExerciseSections.inputFormat">
                  <div class="content">
                    <div v-for="(format, index) in getInputFormats(selectedExercise)" :key="index">
                      <p>{{ format }}</p>
                      <hr v-if="index < getInputFormats(selectedExercise).length - 1">
                    </div>
                  </div>
                </div>
              </div>
              
              <!-- Formato de Salida -->
              <div class="accordion-item" v-if="getOutputFormat(selectedExercise)">
                <div class="accordion-header" @click="toggleExerciseSection('outputFormat')">
                  <h3 class="accordion-title">
                    <i class="fas fa-laptop-code icon-prefix"></i> Formato de Salida
                  </h3>
                  <span class="accordion-icon">{{ openExerciseSections.outputFormat ? '−' : '+' }}</span>
                </div>
                <div class="accordion-content" v-if="openExerciseSections.outputFormat">
                  <div class="content">
                    <p>{{ getOutputFormat(selectedExercise) }}</p>
                  </div>
                </div>
              </div>
              
              <!-- Ejemplos -->
              <div class="accordion-item" v-if="getExamples(selectedExercise).length > 0">
                <div class="accordion-header" @click="toggleExerciseSection('examples')">
                  <h3 class="accordion-title">
                    <i class="fas fa-flask icon-prefix"></i> Ejemplos
                  </h3>
                  <span class="accordion-icon">{{ openExerciseSections.examples ? '−' : '+' }}</span>
                </div>
                <div class="accordion-content" v-if="openExerciseSections.examples">
                  <div class="samples-container">
                    <div v-for="(example, index) in getExamples(selectedExercise)" :key="index" class="sample-card">
                      <div class="sample-card-header">
                        <h4 class="sample-card-title">
                          <i class="fas fa-vial icon-prefix"></i> Ejemplo #{{ index + 1 }}
                        </h4>
                      </div>
                      <div class="sample-card-content">
                        <div class="sample-input">
                          <label class="sample-label">
                            <i class="fas fa-arrow-right icon-prefix"></i> Entrada:
                          </label>
                          <div class="code-box">{{ example.entrada || 'N/A' }}</div>
                        </div>
                        <div class="sample-output">
                          <label class="sample-label">
                            <i class="fas fa-arrow-left icon-prefix"></i> Salida:
                          </label>
                          <div class="code-box">{{ example.salida || 'N/A' }}</div>
                        </div>
                        <div class="sample-explanation" v-if="example.explicacion">
                          <label class="sample-label">
                            <i class="fas fa-lightbulb icon-prefix"></i> Explicación:
                          </label>
                          <p>{{ example.explicacion }}</p>
                        </div>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
              
              <!-- Plantilla de Código -->
              <div class="accordion-item" v-if="selectedExercise.tipo === 'practico'">
                <div class="accordion-header" @click="toggleExerciseSection('template')">
                  <h3 class="accordion-title">
                    <i class="fas fa-code icon-prefix"></i> Plantilla de Código
                  </h3>
                  <span class="accordion-icon">{{ openExerciseSections.template ? '−' : '+' }}</span>
                </div>
                <div class="accordion-content" v-if="openExerciseSections.template">
                  <div class="code-preview">
                    <pre><code>{{ getTemplateCode(selectedExercise) }}</code></pre>
                  </div>
                </div>
              </div>
              
              <!-- Tests Avanzados -->
              <div class="accordion-item" v-if="getAdvancedTests(selectedExercise)">
                <div class="accordion-header" @click="toggleExerciseSection('advancedTests')">
                  <h3 class="accordion-title">
                    <i class="fas fa-vial icon-prefix"></i> Tests Avanzados
                  </h3>
                  <span class="accordion-icon">{{ openExerciseSections.advancedTests ? '−' : '+' }}</span>
                </div>
                <div class="accordion-content" v-if="openExerciseSections.advancedTests">
                  <div class="code-preview">
                    <pre><code>{{ getAdvancedTests(selectedExercise) }}</code></pre>
                  </div>
                </div>
              </div>
            </div>
          </section>
          <footer class="modal-card-foot details-modal-foot">
            <div class="modal-buttons-container">
              <button class="button is-primary" @click="editExercise(selectedExercise)">
                <span class="icon">
                  <i class="fas fa-pencil-alt"></i>
                </span>
                <span>Editar</span>
              </button>
              <button class="button is-outlined" @click="showDetailsModal = false">Cerrar</button>
            </div>
          </footer>
        </div>
      </div>

      <!-- Modal de confirmación para eliminar -->
      <div class="modal" :class="{ 'is-active': showDeleteModal }">
        <div class="modal-background" @click="showDeleteModal = false"></div>
        <div class="modal-card delete-modal">
          <header class="modal-card-head delete-modal-head">
            <p class="modal-card-title">Confirmar eliminación</p>
            <button class="delete" aria-label="close" @click="showDeleteModal = false"></button>
          </header>
          <section class="modal-card-body">
            <div class="content">
              <h3>¿Está seguro de eliminar este ejercicio?</h3>
              <p>Va a eliminar el ejercicio: <strong>{{ exerciseToDelete?.titulo }}</strong></p>
              <p class="has-text-danger">
                <i class="fas fa-exclamation-triangle mr-2"></i>
                Esta acción no se puede deshacer y podría afectar a evaluaciones existentes.
              </p>
            </div>
          </section>
          <footer class="modal-card-foot delete-modal-foot">
            <div class="modal-buttons-container">
              <button class="button is-danger" @click="deleteExercise">
                <span class="icon">
                  <i class="fas fa-trash"></i>
                </span>
                <span>Eliminar</span>
              </button>
              <button class="button is-outlined" @click="showDeleteModal = false">Cancelar</button>
            </div>
          </footer>
        </div>
      </div>
      
      <!-- Notificación de eliminación exitosa -->
      <transition name="fade">
        <div v-if="showDeleteNotification" class="delete-notification">
          <div class="delete-notification-icon">
            <i class="fas fa-check-circle"></i>
          </div>
          <div class="delete-notification-content">
            <div class="delete-notification-title">Ejercicio eliminado</div>
            <div class="delete-notification-message">
              "{{ deletedExerciseTitle }}" ha sido eliminado exitosamente.
            </div>
          </div>
          <button class="delete-notification-close" @click="cerrarNotificacion">×</button>
        </div>
      </transition>
    </div>
  </div>
</template>

<script>
import { ref, computed, onMounted, watch } from 'vue';
import { useRouter } from 'vue-router';
import { useStore } from 'vuex';
import exercisesService from '@/api/exercisesService';
import { marked } from 'marked';
import DOMPurify from 'dompurify';

export default {
  name: 'ExerciseRepository',
  setup() {
    const router = useRouter();
    const store = useStore();
    const userId = computed(() => store.getters['auth/userId']);
    const userRole = computed(() => store.getters['auth/userRole']);
    
    // Configuración de marked para mejor rendimiento
    marked.setOptions({
      gfm: true,
      breaks: true,
      sanitize: false, // Usaremos DOMPurify para sanitización
      smartLists: true,
      smartypants: false
    });
    
    // Caché para markdown renderizado (movido dentro del setup)
    const markdownCache = new Map();
    
    // Estado del componente
    const exercises = ref([]);
    const loading = ref(true);
    const searchQuery = ref('');
    const difficultyFilter = ref('all');
    const typeFilter = ref('all');
    const creatorFilter = ref('all');
    const currentPage = ref(1);
    const exercisesPerPage = ref(8);
    
    // Modales
    const showDeleteModal = ref(false);
    const exerciseToDelete = ref(null);
    const showDetailsModal = ref(false);
    const selectedExercise = ref(null);
    
    // Control de secciones del ejercicio
    const openExerciseSections = ref({
      description: true,
      general: true,
      restrictions: false,
      hint: false,
      inputFormat: false,
      outputFormat: false,
      examples: false,
      template: false,
      advancedTests: false
    });
    
    const toggleExerciseSection = (section) => {
      openExerciseSections.value[section] = !openExerciseSections.value[section];
    };
    
    // Notificación de eliminación
    const showDeleteNotification = ref(false);
    const deletedExerciseTitle = ref('');
    
    // Cargar ejercicios
    const loadExercises = async () => {
      loading.value = true;
      try {
        const response = await exercisesService.getEjercicios();
        if (response.data) {
          exercises.value = response.data.map(exercise => {
            // Establecer dificultad por defecto si no existe
            if (!exercise.dificultad) {
              exercise.dificultad = (exercise.contenido && exercise.contenido.dificultad) 
                ? exercise.contenido.dificultad 
                : 'intermedio';
            }
            return exercise;
          });
        }
      } catch (error) {
        console.error('Error al cargar ejercicios:', error);
      } finally {
        loading.value = false;
      }
    };
    
    // Filtrar ejercicios
    const filterExercises = () => {
      currentPage.value = 1; // Resetear a la primera página al filtrar
    };
    
    // Determinar si se están aplicando filtros
    const isFiltering = computed(() => {
      return searchQuery.value !== '' || 
             difficultyFilter.value !== 'all' || 
             typeFilter.value !== 'all' || 
             creatorFilter.value !== 'all';
    });
    
    // Limpiar filtros
    const clearFilters = () => {
      searchQuery.value = '';
      difficultyFilter.value = 'all';
      typeFilter.value = 'all';
      creatorFilter.value = 'all';
    };
    
    // Observar cambios en los filtros para actualizar la paginación
    watch([searchQuery, difficultyFilter, typeFilter, creatorFilter], () => {
      currentPage.value = 1;
    });
    
    // Ejercicios filtrados
    const filteredExercisesAll = computed(() => {
      let result = [...exercises.value];
      
      // Filtrar por búsqueda
      if (searchQuery.value) {
        const query = searchQuery.value.toLowerCase();
        result = result.filter(ex => 
          ex.titulo?.toLowerCase().includes(query) ||
          ex.descripcion?.toLowerCase().includes(query) ||
          (ex.contenido && typeof ex.contenido === 'object' && 
           JSON.stringify(ex.contenido).toLowerCase().includes(query))
        );
      }
      
      // Filtrar por dificultad
      if (difficultyFilter.value !== 'all') {
        result = result.filter(ex => ex.dificultad === difficultyFilter.value);
      }
      
      // Filtrar por tipo
      if (typeFilter.value !== 'all') {
        result = result.filter(ex => ex.tipo === typeFilter.value);
      }
      
      // Filtrar por creador
      if (creatorFilter.value === 'mine') {
        result = result.filter(ex => ex.creador === userId.value);
      } else if (creatorFilter.value !== 'all') {
        result = result.filter(ex => ex.creador === creatorFilter.value);
      }
      
      return result;
    });
    
    // Ejercicios paginados
    const filteredExercises = computed(() => {
      const startIndex = (currentPage.value - 1) * exercisesPerPage.value;
      const endIndex = startIndex + exercisesPerPage.value;
      return filteredExercisesAll.value.slice(startIndex, endIndex);
    });
    
    // Total de páginas
    const totalPages = computed(() => {
      return Math.ceil(filteredExercisesAll.value.length / exercisesPerPage.value) || 1;
    });
    
    // Función para generar los items de paginación
    const paginationItems = computed(() => {
      const items = [];
      const maxVisiblePages = 5;
      
      if (totalPages.value <= maxVisiblePages) {
        // Mostrar todas las páginas si son pocas
        for (let i = 1; i <= totalPages.value; i++) {
          items.push({ type: 'page', value: i });
        }
      } else {
        // Siempre mostrar la primera página
        items.push({ type: 'page', value: 1 });
        
        // Calcular el rango de páginas a mostrar
        let startPage = Math.max(2, currentPage.value - Math.floor(maxVisiblePages / 2) + 1);
        let endPage = Math.min(totalPages.value - 1, startPage + maxVisiblePages - 3);
        
        if (startPage > 2) {
          items.push({ type: 'ellipsis' });
        }
        
        // Páginas intermedias
        for (let i = startPage; i <= endPage; i++) {
          items.push({ type: 'page', value: i });
        }
        
        if (endPage < totalPages.value - 1) {
          items.push({ type: 'ellipsis' });
        }
        
        // Siempre mostrar la última página
        items.push({ type: 'page', value: totalPages.value });
      }
      
      return items;
    });
    
    // Lista de creadores únicos (mejorado para excluir al usuario actual)
    const uniqueCreators = computed(() => {
      const creators = {};
      exercises.value.forEach(ex => {
        // Solo incluir creadores que no sean el usuario actual
        if (ex.creador && ex.creador_nombre && ex.creador !== userId.value) {
          creators[ex.creador] = {
            id: ex.creador,
            nombre: ex.creador_nombre
          };
        }
      });
      return Object.values(creators);
    });
    
    // Renderizador de Markdown mejorado
    const renderMarkdown = (text) => {
      if (!text) return '';
      
      // Usar caché para evitar re-renderizar el mismo contenido
      if (markdownCache.has(text)) {
        return markdownCache.get(text);
      }
      
      try {
        const renderedHTML = DOMPurify.sanitize(marked(text));
        markdownCache.set(text, renderedHTML);
        return renderedHTML;
      } catch (error) {
        console.error('Error al renderizar markdown:', error);
        return text; // En caso de error, devolver el texto original
      }
    };
    
    // Funciones de utilidad
    const formatDate = (dateString) => {
      if (!dateString) return 'Fecha desconocida';
      
      const date = new Date(dateString);
      return date.toLocaleDateString('es-ES', {
        year: 'numeric',
        month: 'long',
        day: 'numeric'
      });
    };
    
    const truncateText = (text, maxLength) => {
      if (!text) return '';
      if (text.length <= maxLength) return text;
      return text.substring(0, maxLength) + '...';
    };
    
    const getDifficultyLabel = (difficulty) => {
      switch (difficulty) {
        case 'facil': return 'Fácil';
        case 'intermedio': return 'Intermedio';
        case 'dificil': return 'Difícil';
        default: return 'Intermedio';
      }
    };
    
    const getDifficultyClass = (difficulty) => {
      switch (difficulty) {
        case 'facil': return 'is-easy';
        case 'intermedio': return 'is-medium';
        case 'dificil': return 'is-hard';
        default: return 'is-medium';
      }
    };
    
    const getDifficultyTagClass = (difficulty) => {
      switch (difficulty) {
        case 'facil': return 'is-success';
        case 'intermedio': return 'is-primary';
        case 'dificil': return 'is-danger';
        default: return 'is-primary';
      }
    };
    
    const getDifficultyIcon = (difficulty) => {
      switch (difficulty) {
        case 'facil': return 'fas fa-seedling';
        case 'intermedio': return 'fas fa-award';
        case 'dificil': return 'fas fa-fire';
        default: return 'fas fa-award';
      }
    };
    
    const getTags = (exercise) => {
      if (!exercise) return [];

      // 1. Intentar obtener etiquetas directamente
      if (exercise.etiquetas && Array.isArray(exercise.etiquetas)) {
        return exercise.etiquetas;
      }

      // 2. Intentar obtener del contenido si existe
      if (exercise.contenido) {
        let contenido;
        try {
          contenido = typeof exercise.contenido === 'string'
            ? JSON.parse(exercise.contenido)
            : exercise.contenido;
        } catch (e) {
          console.error('Error al parsear contenido:', e);
          return [];
        }

        if (contenido && contenido.etiquetas && Array.isArray(contenido.etiquetas)) {
          return contenido.etiquetas;
        }
      }

      // 3. Si no hay etiquetas, devolver array vacío
      return [];
    };
    
    const getTemplateCode = (exercise) => {
      if (exercise.contenido && exercise.contenido.template) {
        return exercise.contenido.template;
      } else if (exercise.template) {
        return exercise.template;
      }
      return 'print("Hello, World!")';
    };

    const getRestrictions = (exercise) => {
      if (exercise.contenido && exercise.contenido.restricciones) {
        return exercise.contenido.restricciones;
      }
      return '';
    };

    const getHint = (exercise) => {
      if (exercise.contenido && exercise.contenido.pista) {
        return exercise.contenido.pista;
      }
      return '';
    };

    const getInputFormats = (exercise) => {
      if (exercise.contenido && exercise.contenido.formatos_entrada && Array.isArray(exercise.contenido.formatos_entrada)) {
        return exercise.contenido.formatos_entrada.filter(format => format && format.trim() !== '');
      }
      return [];
    };

    const getOutputFormat = (exercise) => {
      if (exercise.contenido && exercise.contenido.formato_salida) {
        return exercise.contenido.formato_salida;
      }
      return '';
    };

    const getExamples = (exercise) => {
      if (exercise.contenido && exercise.contenido.ejemplos && Array.isArray(exercise.contenido.ejemplos)) {
        return exercise.contenido.ejemplos;
      }
      return [];
    };

    const getAdvancedTests = (exercise) => {
      if (exercise.contenido && exercise.contenido.tests_avanzados) {
        return exercise.contenido.tests_avanzados;
      }
      return '';
    };
    
    // Cerrar notificación de eliminación
    const cerrarNotificacion = () => {
      showDeleteNotification.value = false;
    };
    
    // Abrir modal de detalles
    const openExerciseDetails = (exercise) => {
      selectedExercise.value = { ...exercise };
      // Resetear el estado de las secciones abiertas
      openExerciseSections.value = {
        description: true,
        general: true,
        restrictions: false,
        hint: false,
        inputFormat: false,
        outputFormat: false,
        examples: false,
        template: false,
        advancedTests: false
      };
      showDetailsModal.value = true;
    };
    
    // Acciones
    const confirmDelete = (exercise) => {
      exerciseToDelete.value = exercise;
      showDeleteModal.value = true;
    };
    
    const deleteExercise = async () => {
      if (!exerciseToDelete.value) return;
      
      try {
        await exercisesService.eliminarEjercicio(exerciseToDelete.value.id);
        
        // Guardar el título para la notificación
        deletedExerciseTitle.value = exerciseToDelete.value.titulo;
        
        // Actualizar la lista de ejercicios
        exercises.value = exercises.value.filter(ex => ex.id !== exerciseToDelete.value.id);
        showDeleteModal.value = false;
        exerciseToDelete.value = null;
        
        // Mostrar notificación
        showDeleteNotification.value = true;
        
        // Ocultar notificación después de 3 segundos
        setTimeout(() => {
          showDeleteNotification.value = false;
        }, 3000);
        
        // Ajustar página actual si es necesario
        if (filteredExercises.value.length === 0 && currentPage.value > 1) {
          currentPage.value--;
        }
      } catch (error) {
        console.error('Error al eliminar ejercicio:', error);
        alert('Ocurrió un error al eliminar el ejercicio. Por favor, intente nuevamente.');
      }
    };
    
    // Función de edición mejorada para redirigir a CreateExercise con el ID del ejercicio
    const editExercise = (exercise) => {
      // Cerrar el modal de detalles si está abierto
      showDetailsModal.value = false;

      // Verificar que el ejercicio tenga todas las propiedades necesarias
      const exerciseToEdit = { ...exercise };

      // Asegurarse de que las etiquetas estén presentes
      if (!exerciseToEdit.etiquetas) {
        exerciseToEdit.etiquetas = getTags(exercise);
      }

      // Determinar la ruta de redirección basada en el rol
      const basePath = userRole.value === 'admin'
        ? '/admin/dashboard/crear-ejercicio'
        : '/docente/dashboard/crear-ejercicio';

      // Navegar a la ruta con el parámetro de ID del ejercicio
      try {
        console.log("Editando ejercicio:", exerciseToEdit.id, "con etiquetas:", exerciseToEdit.etiquetas);
        router.push({
          path: basePath,
          query: { edit_id: exerciseToEdit.id }
        });
      } catch (error) {
        console.error("Error al navegar a la edición:", error);
        alert("No se pudo navegar a la página de edición. Por favor, inténtelo nuevamente.");
      }
    };

    
    const navigateToCreateExercise = () => {
      if (userRole.value === 'admin') {
        router.push('/admin/dashboard/crear-ejercicio');
      } else {
        router.push('/docente/dashboard/crear-ejercicio');
      }
    };
    
    // Cargar ejercicios al montar el componente
    onMounted(() => {
      loadExercises();
    });
    
    return {
      exercises,
      loading,
      searchQuery,
      difficultyFilter,
      typeFilter,
      creatorFilter,
      currentPage,
      filteredExercises,
      totalPages,
      paginationItems,
      isFiltering,
      uniqueCreators,
      showDeleteModal,
      exerciseToDelete,
      showDetailsModal,
      selectedExercise,
      showDeleteNotification,
      deletedExerciseTitle,
      openExerciseSections,
      toggleExerciseSection,
      filterExercises,
      clearFilters,
      formatDate,
      truncateText,
      getDifficultyLabel,
      getDifficultyClass,
      getDifficultyTagClass,
      getDifficultyIcon,
      getTags,
      getTemplateCode,
      getRestrictions,
      getHint,
      getInputFormats,
      getOutputFormat,
      getExamples,
      getAdvancedTests,
      renderMarkdown,
      openExerciseDetails,
      confirmDelete,
      deleteExercise,
      editExercise,
      navigateToCreateExercise,
      cerrarNotificacion
    };
  }
};
</script>

<style scoped>


/* Todos los estilos prefijados con el wrapper para asegurar aislamiento */
.exercise-repository-wrapper {
  position: relative;
  max-width: 100%;
  width: 100%;
}

.exercise-repository-wrapper .exercise-repository {
  position: relative;
  padding: 1.5rem;
  max-width: 1600px;
  margin: 0 auto;
  font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Oxygen-Sans, Ubuntu, Cantarell, "Helvetica Neue", sans-serif;
  background-color: #1C1C21; /* Fondo oscuro para el contenedor principal */
  border-radius: 12px;
  box-shadow: 0 5px 20px rgba(0, 0, 0, 0.15);
  color: #f0f0f0; /* Texto claro para fondo oscuro */
  border-top: 4px solid #EBB300; /* Borde superior como en CreateExercise */
}

/* ---- Estilos para los elementos Bulma dentro del wrapper ---- */

/* Encabezados y botones */
.exercise-repository-wrapper .custom-header {
  margin-bottom: 2.5rem;
  color: #f0f0f0;
}

.exercise-repository-wrapper .repository-header {
  margin-bottom: 1.5rem;
}

.exercise-repository-wrapper .repository-header .title {
  color: #f0f0f0;
}

.exercise-repository-wrapper .repository-header .subtitle {
  color: #b0b0b0;
}

.exercise-repository-wrapper .button {
  border-radius: 4px;
  transition: all 0.3s ease;
  background-color: #3a3a45;
  color: #f0f0f0;
  border-color: #444450;
}

.exercise-repository-wrapper .button:hover {
  transform: translateY(-2px);
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.3);
  background-color: #444450;
}

.exercise-repository-wrapper .button.is-primary {
  background-color: #EBB300;
  color: #1C1C21;
  border-color: transparent;
}

.exercise-repository-wrapper .button.is-primary:hover {
  background-color: #ffc107;
}

.exercise-repository-wrapper .button.is-danger {
  background-color: #d81b60;
  color: #fff;
}

.exercise-repository-wrapper .button.is-danger:hover {
  background-color: #e91e63;
}

.exercise-repository-wrapper .button.is-outlined {
  background-color: transparent;
  color: #f0f0f0;
  border-color: #f0f0f0;
}

/* Filtros y buscador */
.exercise-repository-wrapper .filter-panel {
  margin-bottom: 2rem;
  background-color: #2a2a35; /* Fondo oscuro que combina con #1C1C21 */
  border-radius: 8px;
  box-shadow: 0 3px 10px rgba(0, 0, 0, 0.2);
  border-top: 3px solid #EBB300;
  padding: 1.25rem;
  color: #f0f0f0; /* Texto claro */
}

.exercise-repository-wrapper .filter-panel .label {
  color: #d0d0d0;
}

.exercise-repository-wrapper .filter-panel .select select {
  background-color: #3a3a45;
  color: #f0f0f0;
  border-color: #444450;
}

.exercise-repository-wrapper .filter-panel .select::after {
  border-color: #EBB300 !important;
}

.exercise-repository-wrapper .search-input {
  border: 1px solid #444450;
  box-shadow: none;
  transition: border-color 0.2s ease;
  background-color: #3a3a45;
  color: #f0f0f0;
}

.exercise-repository-wrapper .search-input:focus {
  border-color: #EBB300;
  box-shadow: 0 0 0 1px rgba(235, 179, 0, 0.3);
}

.exercise-repository-wrapper .search-input::placeholder {
  color: #a0a0a0;
}

.exercise-repository-wrapper .clean-button {
  background-color: #3a3a45;
  color: #d0d0d0;
  border: 1px solid #444450;
  transition: background-color 0.2s ease, color 0.2s ease;
}

.exercise-repository-wrapper .clean-button.is-active {
  background-color: #EBB300;
  color: #1C1C21;
  border-color: #EBB300;
}

.exercise-repository-wrapper .clean-button:hover {
  transform: none;
  box-shadow: none;
}

/* Estado de carga */
.exercise-repository-wrapper .loading-container {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 4rem 0;
  color: #f0f0f0;
}

.exercise-repository-wrapper .loading-circle {
  width: 50px;
  height: 50px;
  border: 5px solid #3a3a45;
  border-top: 5px solid #EBB300;
  border-radius: 50%;
  animation: spin 1s linear infinite;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

/* Estado vacio */
.exercise-repository-wrapper .empty-state .box {
  background-color: #2a2a35;
  color: #f0f0f0;
  border: 1px solid #3a3a45;
}

.exercise-repository-wrapper .empty-state .title {
  color: #f0f0f0;
}

.exercise-repository-wrapper .empty-state .subtitle {
  color: #b0b0b0;
}

/* Tarjetas de ejercicios */
.exercise-repository-wrapper .exercise-card {
  background: #2a2a35; /* Fondo oscuro para las tarjetas */
  border-radius: 12px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.2);
  overflow: hidden;
  height: 100%;
  display: flex;
  flex-direction: column;
  border: 1px solid #3a3a45;
  position: relative;
  color: #f0f0f0;
  transition: transform 0.3s ease, box-shadow 0.3s ease;
}

.exercise-repository-wrapper .exercise-card:hover {
  transform: translateY(-5px);
  box-shadow: 0 8px 20px rgba(0, 0, 0, 0.25);
  border-color: #EBB300;
}

.exercise-repository-wrapper .card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1rem;
  color: white;
}

.exercise-repository-wrapper .card-header.is-easy {
  background: linear-gradient(135deg, #52bd94, #3a9d79);
}

.exercise-repository-wrapper .card-header.is-medium {
  background: linear-gradient(135deg, #EBB300, #d19f00);
}

.exercise-repository-wrapper .card-header.is-hard {
  background: linear-gradient(135deg, #e74c3c, #c0392b);
}

.exercise-repository-wrapper .difficulty-badge, 
.exercise-repository-wrapper .exercise-type {
  font-size: 0.8rem;
  font-weight: 500;
  display: flex;
  align-items: center;
  gap: 0.3rem;
}

.exercise-repository-wrapper .card-body {
  padding: 1.25rem;
  flex-grow: 1;
  display: flex;
  flex-direction: column;
}

.exercise-repository-wrapper .card-title {
  font-size: 1.1rem;
  font-weight: 600;
  margin-bottom: 0.5rem;
  color: #f0f0f0;
}

.exercise-repository-wrapper .card-description {
  font-size: 0.9rem;
  color: #b0b0b0;
  flex-grow: 1;
  margin-bottom: 1rem;
}

.exercise-repository-wrapper .tags {
  display: flex;
  flex-wrap: wrap;
  gap: 0.3rem;
  margin-top: auto;
}

.exercise-repository-wrapper .tag {
  background-color: #3a3a45;
  color: #d0d0d0;
  font-size: 0.7rem;
  padding: 0.25rem 0.5rem;
  border-radius: 4px;
}

.exercise-repository-wrapper .card-footer {
  padding: 1rem;
  border-top: 1px solid #3a3a45;
  display: flex;
  justify-content: space-between;
  align-items: center;
  background-color: #252530;
}

.exercise-repository-wrapper .meta-info {
  display: flex;
  flex-direction: column;
  gap: 0.3rem;
}

.exercise-repository-wrapper .meta-item {
  font-size: 0.75rem;
  color: #b0b0b0;
  display: flex;
  align-items: center;
  gap: 0.3rem;
}

.exercise-repository-wrapper .card-actions {
  display: flex;
  gap: 0.4rem;
}

/* Botones de acción */
.exercise-repository-wrapper .action-btn {
  width: 32px !important;
  height: 32px !important;
  min-width: 32px;
  min-height: 32px;
  max-width: 32px;
  max-height: 32px;
  border-radius: 4px; /* Cuadrados en lugar de redondos */
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 0.9rem;
  border: none;
  cursor: pointer;
  transition: all 0.2s ease;
  color: white;
  line-height: 1;
  padding: 0;
}

.exercise-repository-wrapper .action-btn i {
  font-size: 14px; /* Tamaño estandarizado para todos los iconos */
}

.exercise-repository-wrapper .action-btn.view {
  background-color: #4569b3; /* Azul más fuerte */
}

.exercise-repository-wrapper .action-btn.edit {
  background-color: #2c9678; /* Verde más intenso */
}

.exercise-repository-wrapper .action-btn.delete {
  background-color: #d81b60; /* Rojo intenso */
}

.exercise-repository-wrapper .action-btn:hover {
  transform: scale(1.05);
  opacity: 0.9;
}

/* Paginación */
.exercise-repository-wrapper .pagination-wrapper {
  margin-top: 2rem;
  padding: 1rem 0;
}

.exercise-repository-wrapper .custom-pagination {
  display: flex;
  justify-content: center;
}

.exercise-repository-wrapper .custom-pagination .pagination-list {
  display: flex;
  align-items: center;
  list-style: none;
  padding: 0;
  margin: 0;
}

.exercise-repository-wrapper .custom-pagination .pagination-link {
  min-width: 2.5rem;
  height: 2.5rem;
  margin: 0 0.15rem;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 4px;
  border: 1px solid #3a3a45;
  background-color: #2a2a35;
  color: #d0d0d0;
  text-decoration: none;
}

.exercise-repository-wrapper .pagination-link.pagination-previous,
.exercise-repository-wrapper .pagination-link.pagination-next {
  background-color: #4569b3;
  color: white;
  border-color: #3a5998;
  display: flex;
  align-items: center;
  padding: 0 1rem;
  gap: 0.5rem;
  cursor: pointer;
  transition: background-color 0.3s ease;
}

.exercise-repository-wrapper .pagination-link.pagination-previous:hover,
.exercise-repository-wrapper .pagination-link.pagination-next:hover {
  background-color: #5579c3;
}

.exercise-repository-wrapper .pagination-link.pagination-previous.is-disabled,
.exercise-repository-wrapper .pagination-link.pagination-next.is-disabled {
  background-color: #3a3a45;
  color: #7a7a8c;
  border-color: #444450;
  opacity: 0.7;
}

.exercise-repository-wrapper .pagination-text {
  font-size: 0.85rem;
  font-weight: 500;
}

.exercise-repository-wrapper .nav-icon {
  font-size: 1.2rem;
  font-weight: bold;
}

.exercise-repository-wrapper .pagination-ellipsis {
  color: #b0b0b0;
}

.exercise-repository-wrapper .custom-pagination .pagination-link.is-current {
  background-color: #4569b3;
  border-color: #3a5998;
  color: white;
}

/* Modales */
.exercise-repository-wrapper .modal-card {
  border-radius: 8px;
  overflow: hidden;
}

.exercise-repository-wrapper .details-modal .details-modal-head {
  background-color: #38B2AC !important;
  color: white !important;
  border-bottom: none !important;
}

.exercise-repository-wrapper .details-modal .details-modal-foot {
  background-color: #2A4365;
  border-top: none;
  justify-content: flex-end;
  padding: 1.5rem;
}

.exercise-repository-wrapper .delete-modal .delete-modal-head {
  background-color: #C71C5C !important;
  color: white !important;
  border-bottom: none !important;
}

.exercise-repository-wrapper .delete-modal .delete-modal-foot {
  background-color: #2D3748;
  border-top: none;
  justify-content: flex-end;
  padding: 1.5rem;
}

.exercise-repository-wrapper .modal-buttons-container {
  display: flex;
  justify-content: flex-end;
  gap: 1rem;
  width: 100%;
}

/* Notificacion */
.exercise-repository-wrapper .delete-notification {
  position: fixed;
  bottom: 2rem;
  right: 2rem;
  background-color: #2D3748;
  color: white;
  border-radius: 8px;
  box-shadow: 0 8px 16px rgba(0, 0, 0, 0.2);
  padding: 1rem;
  display: flex;
  align-items: center;
  width: 350px;
  z-index: 100;
  border-left: 4px solid #38B2AC;
  animation: slideIn 0.5s ease;
}

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

.exercise-repository-wrapper .delete-notification-icon {
  font-size: 2rem;
  color: #38B2AC;
  margin-right: 1rem;
}

.exercise-repository-wrapper .delete-notification-content {
  flex: 1;
}

.exercise-repository-wrapper .delete-notification-title {
  font-weight: bold;
  font-size: 1.1rem;
  margin-bottom: 0.25rem;
}

.exercise-repository-wrapper .delete-notification-message {
  font-size: 0.9rem;
  color: #E2E8F0;
}

.exercise-repository-wrapper .delete-notification-close {
  background: none;
  border: none;
  color: #A0AEC0;
  font-size: 1.25rem;
  cursor: pointer;
  padding: 0.25rem 0.5rem;
  margin-left: 0.5rem;
  align-self: flex-start;
}

.exercise-repository-wrapper .delete-notification-close:hover {
  color: white;
}

.fade-enter-active, .fade-leave-active {
  transition: opacity 0.5s, transform 0.5s;
}

.fade-enter-from, .fade-leave-to {
  opacity: 0;
  transform: translateX(30px);
}

/* Acordeon detalles ejercicio */
.exercise-repository-wrapper .exercise-accordion {
  display: flex;
  flex-direction: column;
  gap: 1rem;
  margin: 1rem 0;
}

.exercise-repository-wrapper .accordion-item {
  border: 1px solid #444450;
  border-radius: 8px;
  overflow: hidden;
  transition: all 0.3s ease;
}

.exercise-repository-wrapper .accordion-item:hover {
  border-color: #4569b3;
}

.exercise-repository-wrapper .accordion-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1rem;
  background-color: #2a2a35;
  cursor: pointer;
  user-select: none;
}

.exercise-repository-wrapper .accordion-title {
  margin: 0;
  font-weight: 600;
  font-size: 1.05rem;
  display: flex;
  align-items: center;
  color: #f0f0f0;
}

.exercise-repository-wrapper .icon-prefix {
  margin-right: 0.5rem;
  color: #38B2AC; /* Color celeste para los iconos */
  font-size: 1rem;
}

.exercise-repository-wrapper .accordion-icon {
  font-size: 1.25rem;
  color: #38B2AC;
  font-weight: bold;
}

.exercise-repository-wrapper .accordion-content {
  padding: 1.25rem;
  background-color: #1C1C21;
  border-top: 1px solid #444450;
}

/* Información general */
.exercise-repository-wrapper .general-info {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
}

.exercise-repository-wrapper .info-item {
  display: flex;
  gap: 0.5rem;
}

.exercise-repository-wrapper .info-label {
  font-weight: 600;
  min-width: 140px;
  color: #b0b0b0;
}

.exercise-repository-wrapper .info-value {
  color: #f0f0f0;
}

/* Código y ejemplos */
.exercise-repository-wrapper .code-preview {
  background-color: #1C1C21;
  color: #f8f8f2;
  padding: 1rem;
  border-radius: 4px;
  overflow-x: auto;
  font-family: 'Fira Code', 'Consolas', monospace;
  border: 1px solid #383844;
}

.exercise-repository-wrapper .code-preview pre {
  margin: 0;
  white-space: pre-wrap;
}

.exercise-repository-wrapper .code-box {
  background-color: #1C1C21;
  color: #f8f8f2;
  padding: 0.75rem;
  border-radius: 4px;
  font-family: 'Fira Code', 'Consolas', monospace;
  border: 1px solid #383844;
  white-space: pre-wrap;
}

/* Ejemplos */
.exercise-repository-wrapper .samples-container {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.exercise-repository-wrapper .sample-card {
  border: 1px solid #444450;
  border-radius: 6px;
  overflow: hidden;
  margin-bottom: 1rem;
}

.exercise-repository-wrapper .sample-card:hover {
  border-color: #444450;
  box-shadow: 0 4px 10px rgba(62, 207, 178, 0.15);
}

.exercise-repository-wrapper .sample-card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0.75rem 1rem;
  background-color: #2a2a35;
}

.exercise-repository-wrapper .sample-card-title {
  margin: 0;
  font-size: 1rem;
  font-weight: 600;
  color: #f0f0f0;
}

.exercise-repository-wrapper .sample-card-content {
  padding: 1rem;
  display: flex;
  flex-direction: column;
  gap: 1rem;
  background-color: rgba(42, 42, 48, 0.5);
}

.exercise-repository-wrapper .sample-label {
  display: flex;
  align-items: center;
  font-size: 0.9rem;
  font-weight: 500;
  margin-bottom: 0.4rem;
  color: #b0b0b0;
}

/* Corregir iconos */
.exercise-repository-wrapper .fas, 
.exercise-repository-wrapper .fa, 
.exercise-repository-wrapper .fa-solid, 
.exercise-repository-wrapper .far, 
.exercise-repository-wrapper .fa-regular, 
.exercise-repository-wrapper .fab, 
.exercise-repository-wrapper .fa-brands {
  font-family: 'Font Awesome 6 Free', 'Font Awesome 5 Free', 'FontAwesome' !important;
  font-weight: 900;
}

.exercise-repository-wrapper .fas.fa-book.mr-3 {
  color: #DEA900;
}

.exercise-repository-wrapper .icon {
  opacity: 100% !important;
}

/* Media queries */
@media screen and (max-width: 1024px) {
  .exercise-repository-wrapper .form-container {
    max-width: 95%;
  }
}

@media screen and (max-width: 768px) {
  .exercise-repository-wrapper {
    padding: 1rem;
  }
  
  .exercise-repository-wrapper .form-container {
    padding: 1.5rem;
  }
  
  .exercise-repository-wrapper .header-content {
    flex-direction: column;
  }
  
  .exercise-repository-wrapper .header-text {
    text-align: center;
    margin-bottom: 1rem;
  }
  
  .exercise-repository-wrapper .header-text .title,
  .exercise-repository-wrapper .header-text .subtitle {
    max-width: 100%;
  }
  
  .exercise-repository-wrapper .markdown-container,
  .exercise-repository-wrapper .test-container {
    grid-template-columns: 1fr;
  }
  
  .exercise-repository-wrapper .info-item {
    flex-direction: column;
    gap: 0.25rem;
  }
  
  .exercise-repository-wrapper .info-label {
    min-width: auto;
  }
}

@media screen and (max-width: 640px) {
  .exercise-repository-wrapper .form-container {
    padding: 1rem;
  }
  
  .exercise-repository-wrapper .submit-button {
    width: 100%;
    justify-content: center;
  }
}

/* Estilos para tema claro del navegador */
@media (prefers-color-scheme: light) {
  .exercise-repository-wrapper .delete-modal .modal-card-body {
    background-color: #ffffff;
    color: #1a1a1a;
  }
  
  .exercise-repository-wrapper .delete-modal .modal-card-body h3 {
    color: #1a1a1a;
  }
  
  .exercise-repository-wrapper .delete-modal .modal-card-body p {
    color: #1a1a1a;
  }
  
  .exercise-repository-wrapper .delete-modal .modal-card-body strong {
    color: #000000;
  }
  
  .exercise-repository-wrapper .delete-modal .modal-card-body .has-text-danger {
    color: #d63384 !important;
  }
  
  .exercise-repository-wrapper .delete-modal .modal-card-body .fas.fa-exclamation-triangle {
    color: #d63384;
  }
}
</style>