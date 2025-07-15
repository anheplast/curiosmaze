<!-- src/components/docentes/repositorio-ejercicios/ExerciseRepository.vue -->
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
/* =================== CONTENEDOR PRINCIPAL =================== */
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
  background-color: var(--color-bg-main);
  border-radius: var(--border-radius-lg);
  box-shadow: var(--shadow-lg);
  color: var(--color-text-primary);
  border-top: 4px solid var(--color-primary);
}

/* =================== HEADER Y TÍTULOS =================== */
.exercise-repository-wrapper .custom-header {
  margin-bottom: 2.5rem;
  color: var(--color-text-primary);
}

.exercise-repository-wrapper .repository-header {
  margin-bottom: 1.5rem;
}

.exercise-repository-wrapper .repository-header .title {
  color: var(--color-text-primary);
}

.exercise-repository-wrapper .repository-header .subtitle {
  color: var(--color-text-secondary);
}

/* =================== BOTONES GENERALES =================== */
.exercise-repository-wrapper .button {
  border-radius: var(--border-radius-sm);
  transition: all var(--transition-smooth) ease;
  background-color: var(--color-bg-element-hover);
  color: var(--color-text-primary);
  border-color: var(--color-border-light);
}

.exercise-repository-wrapper .button:hover {
  transform: translateY(-2px);
  box-shadow: var(--shadow);
  background-color: var(--color-border-light);
}

.exercise-repository-wrapper .button.is-primary {
  background-color: var(--color-primary);
  color: var(--color-bg-main);
  border-color: transparent;
}

.exercise-repository-wrapper .button.is-primary:hover {
  background-color: var(--color-primary-light);
}

.exercise-repository-wrapper .button.is-danger {
  background-color: var(--color-error);
  color: var(--color-text-primary);
}

.exercise-repository-wrapper .button.is-danger:hover {
  background-color: var(--color-error-light);
}

.exercise-repository-wrapper .button.is-outlined {
  background-color: transparent;
  color: var(--color-text-primary);
  border-color: var(--color-text-primary);
}

/* =================== PANEL DE FILTROS =================== */
.exercise-repository-wrapper .filter-panel {
  margin-bottom: 2rem;
  background-color: var(--color-bg-element);
  border-radius: var(--border-radius);
  box-shadow: var(--shadow-sm);
  border-top: 3px solid var(--color-primary);
  padding: 1.25rem;
  color: var(--color-text-primary);
}

.exercise-repository-wrapper .filter-panel .label {
  color: var(--color-text-secondary);
}

.exercise-repository-wrapper .filter-panel .select select {
  background-color: var(--color-bg-element-hover);
  color: var(--color-text-primary);
  border-color: var(--color-border-light);
}

.exercise-repository-wrapper .filter-panel .select::after {
  border-color: var(--color-primary) !important;
}

.exercise-repository-wrapper .search-input {
  border: 1px solid var(--color-border-light);
  box-shadow: none;
  transition: border-color var(--transition-fast) ease;
  background-color: var(--color-bg-element-hover);
  color: var(--color-text-primary);
}

.exercise-repository-wrapper .search-input:focus {
  border-color: var(--color-primary);
  box-shadow: 0 0 0 1px rgba(235, 179, 0, 0.3);
}

.exercise-repository-wrapper .search-input::placeholder {
  color: var(--color-text-muted);
}

.exercise-repository-wrapper .clean-button {
  background-color: var(--color-bg-element-hover);
  color: var(--color-text-secondary);
  border: 1px solid var(--color-border-light);
  transition: background-color var(--transition-fast) ease, color var(--transition-fast) ease;
}

.exercise-repository-wrapper .clean-button.is-active {
  background-color: var(--color-primary);
  color: var(--color-bg-main);
  border-color: var(--color-primary);
}

.exercise-repository-wrapper .clean-button:hover {
  transform: none;
  box-shadow: none;
}

/* =================== ESTADOS DE CARGA Y VACÍO =================== */
.exercise-repository-wrapper .loading-container {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 4rem 0;
  color: var(--color-text-primary);
}

.exercise-repository-wrapper .loading-circle {
  width: 50px;
  height: 50px;
  border: 5px solid var(--color-bg-element-hover);
  border-top: 5px solid var(--color-primary);
  border-radius: 50%;
  animation: spin 1s linear infinite;
}

.exercise-repository-wrapper .empty-state .box {
  background-color: var(--color-bg-element);
  color: var(--color-text-primary);
  border: 1px solid var(--color-bg-element-hover);
}

.exercise-repository-wrapper .empty-state .title {
  color: var(--color-text-primary);
}

.exercise-repository-wrapper .empty-state .subtitle {
  color: var(--color-text-secondary);
}

/* =================== TARJETAS DE EJERCICIOS =================== */
.exercise-repository-wrapper .exercise-card {
  background: var(--color-bg-element);
  border-radius: var(--border-radius-lg);
  box-shadow: var(--shadow);
  overflow: hidden;
  height: 100%;
  display: flex;
  flex-direction: column;
  border: 1px solid var(--color-bg-element-hover);
  position: relative;
  color: var(--color-text-primary);
  transition: transform var(--transition-smooth) ease, box-shadow var(--transition-smooth) ease;
}

.exercise-repository-wrapper .exercise-card:hover {
  transform: translateY(-5px);
  box-shadow: var(--shadow-lg);
  border-color: var(--color-primary);
}

.exercise-repository-wrapper .card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1rem;
  color: var(--color-text-primary);
}

.exercise-repository-wrapper .card-header.is-easy {
  background: linear-gradient(135deg, var(--color-success), var(--color-success-dark));
}

.exercise-repository-wrapper .card-header.is-medium {
  background: linear-gradient(135deg, var(--color-primary), var(--color-primary-dark));
}

.exercise-repository-wrapper .card-header.is-hard {
  background: linear-gradient(135deg, var(--color-error), var(--color-error-dark));
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
  color: var(--color-text-primary);
}

.exercise-repository-wrapper .card-description {
  font-size: 0.9rem;
  color: var(--color-text-secondary);
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
  background-color: var(--color-bg-element-hover);
  color: var(--color-text-secondary);
  font-size: 0.7rem;
  padding: 0.25rem 0.5rem;
  border-radius: var(--border-radius-sm);
}

.exercise-repository-wrapper .card-footer {
  padding: 1rem;
  border-top: 1px solid var(--color-bg-element-hover);
  display: flex;
  justify-content: space-between;
  align-items: center;
  background-color: var(--color-bg-element-alt);
}

.exercise-repository-wrapper .meta-info {
  display: flex;
  flex-direction: column;
  gap: 0.3rem;
}

.exercise-repository-wrapper .meta-item {
  font-size: 0.75rem;
  color: var(--color-text-secondary);
  display: flex;
  align-items: center;
  gap: 0.3rem;
}

.exercise-repository-wrapper .card-actions {
  display: flex;
  gap: 0.4rem;
}

/* =================== BOTONES DE ACCIÓN =================== */
.exercise-repository-wrapper .action-btn {
  width: 32px !important;
  height: 32px !important;
  min-width: 32px;
  min-height: 32px;
  max-width: 32px;
  max-height: 32px;
  border-radius: var(--border-radius-sm);
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 0.9rem;
  border: none;
  cursor: pointer;
  transition: all var(--transition-fast) ease;
  color: var(--color-text-primary);
  line-height: 1;
  padding: 0;
}

.exercise-repository-wrapper .action-btn i {
  font-size: 14px;
}

.exercise-repository-wrapper .action-btn.view {
  background-color: var(--color-info);
}

.exercise-repository-wrapper .action-btn.edit {
  background-color: var(--color-success);
}

.exercise-repository-wrapper .action-btn.delete {
  background-color: var(--color-error);
}

.exercise-repository-wrapper .action-btn:hover {
  transform: scale(1.05);
  opacity: 0.9;
}

/* =================== PAGINACIÓN =================== */
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
  border-radius: var(--border-radius-sm);
  border: 1px solid var(--color-bg-element-hover);
  background-color: var(--color-bg-element);
  color: var(--color-text-secondary);
  text-decoration: none;
}

.exercise-repository-wrapper .pagination-link.pagination-previous,
.exercise-repository-wrapper .pagination-link.pagination-next {
  background-color: var(--color-info);
  color: var(--color-text-primary);
  border-color: var(--color-info-dark);
  display: flex;
  align-items: center;
  padding: 0 1rem;
  gap: 0.5rem;
  cursor: pointer;
  transition: background-color var(--transition-smooth) ease;
}

.exercise-repository-wrapper .pagination-link.pagination-previous:hover,
.exercise-repository-wrapper .pagination-link.pagination-next:hover {
  background-color: var(--color-info-light);
}

.exercise-repository-wrapper .pagination-link.pagination-previous.is-disabled,
.exercise-repository-wrapper .pagination-link.pagination-next.is-disabled {
  background-color: var(--color-bg-element-hover);
  color: var(--color-text-disabled);
  border-color: var(--color-border-light);
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
  color: var(--color-text-secondary);
}

.exercise-repository-wrapper .custom-pagination .pagination-link.is-current {
  background-color: var(--color-info);
  border-color: var(--color-info-dark);
  color: var(--color-text-primary);
}

/* =================== MODALES =================== */
.exercise-repository-wrapper .modal-card {
  border-radius: var(--border-radius);
  overflow: hidden;
}

.exercise-repository-wrapper .details-modal .details-modal-head {
  background-color: var(--color-teal) !important;
  color: var(--color-text-primary) !important;
  border-bottom: none !important;
}

.exercise-repository-wrapper .details-modal .details-modal-foot {
  background-color: var(--color-bg-element);
  border-top: none;
  justify-content: flex-end;
  padding: 1.5rem;
}

.exercise-repository-wrapper .delete-modal .delete-modal-head {
  background-color: var(--color-error) !important;
  color: var(--color-text-primary) !important;
  border-bottom: none !important;
}

.exercise-repository-wrapper .delete-modal .delete-modal-foot {
  background-color: var(--color-bg-element-alt);
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

/* =================== NOTIFICACIONES =================== */
.exercise-repository-wrapper .delete-notification {
  position: fixed;
  bottom: 2rem;
  right: 2rem;
  background-color: var(--color-bg-element-alt);
  color: var(--color-text-primary);
  border-radius: var(--border-radius);
  box-shadow: var(--shadow-lg);
  padding: 1rem;
  display: flex;
  align-items: center;
  width: 350px;
  z-index: 100;
  border-left: 4px solid var(--color-teal);
  animation: slideIn 0.5s ease;
}

.exercise-repository-wrapper .delete-notification-icon {
  font-size: 2rem;
  color: var(--color-teal);
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
  color: var(--color-text-secondary);
}

.exercise-repository-wrapper .delete-notification-close {
  background: none;
  border: none;
  color: var(--color-text-muted);
  font-size: 1.25rem;
  cursor: pointer;
  padding: 0.25rem 0.5rem;
  margin-left: 0.5rem;
  align-self: flex-start;
}

.exercise-repository-wrapper .delete-notification-close:hover {
  color: var(--color-text-primary);
}

/* =================== ACORDEÓN =================== */
.exercise-repository-wrapper .exercise-accordion {
  display: flex;
  flex-direction: column;
  gap: 1rem;
  margin: 1rem 0;
}

.exercise-repository-wrapper .accordion-item {
  border: 1px solid var(--color-border-light);
  border-radius: var(--border-radius);
  overflow: hidden;
  transition: all var(--transition-smooth) ease;
}

.exercise-repository-wrapper .accordion-item:hover {
  border-color: var(--color-info);
}

.exercise-repository-wrapper .accordion-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1rem;
  background-color: var(--color-bg-element);
  cursor: pointer;
  user-select: none;
}

.exercise-repository-wrapper .accordion-title {
  margin: 0;
  font-weight: 600;
  font-size: 1.05rem;
  display: flex;
  align-items: center;
  color: var(--color-text-primary);
}

.exercise-repository-wrapper .icon-prefix {
  margin-right: 0.5rem;
  color: var(--color-teal);
  font-size: 1rem;
}

.exercise-repository-wrapper .accordion-icon {
  font-size: 1.25rem;
  color: var(--color-teal);
  font-weight: bold;
}

.exercise-repository-wrapper .accordion-content {
  padding: 1.25rem;
  background-color: var(--color-bg-main);
  border-top: 1px solid var(--color-border-light);
}

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
  color: var(--color-text-secondary);
}

.exercise-repository-wrapper .info-value {
  color: var(--color-text-primary);
}

/* =================== CÓDIGO Y EJEMPLOS =================== */
.exercise-repository-wrapper .code-preview {
  background-color: var(--color-bg-main);
  color: var(--color-text-primary);
  padding: 1rem;
  border-radius: var(--border-radius-sm);
  overflow-x: auto;
  font-family: 'Fira Code', 'Consolas', monospace;
  border: 1px solid var(--color-border);
}

.exercise-repository-wrapper .code-preview pre {
  margin: 0;
  white-space: pre-wrap;
}

.exercise-repository-wrapper .code-box {
  background-color: var(--color-bg-main);
  color: var(--color-text-primary);
  padding: 0.75rem;
  border-radius: var(--border-radius-sm);
  font-family: 'Fira Code', 'Consolas', monospace;
  border: 1px solid var(--color-border);
  white-space: pre-wrap;
}

.exercise-repository-wrapper .samples-container {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.exercise-repository-wrapper .sample-card {
  border: 1px solid var(--color-border-light);
  border-radius: var(--border-radius-sm);
  overflow: hidden;
  margin-bottom: 1rem;
}

.exercise-repository-wrapper .sample-card:hover {
  border-color: var(--color-border-light);
  box-shadow: 0 4px 10px rgba(62, 207, 178, 0.15);
}

.exercise-repository-wrapper .sample-card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0.75rem 1rem;
  background-color: var(--color-bg-element);
}

.exercise-repository-wrapper .sample-card-title {
  margin: 0;
  font-size: 1rem;
  font-weight: 600;
  color: var(--color-text-primary);
}

.exercise-repository-wrapper .sample-card-content {
  padding: 1rem;
  display: flex;
  flex-direction: column;
  gap: 1rem;
  background-color: var(--color-bg-element-alt);
}

.exercise-repository-wrapper .sample-label {
  display: flex;
  align-items: center;
  font-size: 0.9rem;
  font-weight: 500;
  margin-bottom: 0.4rem;
  color: var(--color-text-secondary);
}

/* =================== ICONOS =================== */
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
  color: var(--color-primary-dark);
}

.exercise-repository-wrapper .icon {
  opacity: 100% !important;
}

/* =================== ANIMACIONES =================== */
@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
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

.fade-enter-active, .fade-leave-active {
  transition: opacity var(--transition-slow), transform var(--transition-slow);
}

.fade-enter-from, .fade-leave-to {
  opacity: 0;
  transform: translateX(30px);
}

/* =================== RESPONSIVE =================== */
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
</style>