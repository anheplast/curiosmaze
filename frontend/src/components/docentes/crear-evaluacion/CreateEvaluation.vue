<!-- src/components/docentes/crear-evaluacion/CreateEvaluation.vue -->
<template>
  <!-- Wrapper principal con clase única para aislar estilos -->
  <div class="curiosmaze-create-eval-wrapper">
    <div class="cm-create-eval-container">
      <div class="cm-form-container">
        <div class="cm-header">
          <div class="cm-header-content">
            <div class="cm-header-text">
              <h1 class="cm-title">{{ pageTitle }}</h1>
              <p class="cm-subtitle">Complete la información necesaria para crear una evaluación para sus estudiantes.
              </p>
            </div>
            <div class="cm-header-icon">
              <span class="cm-icon-container">
                <i class="cm-fas">✏️</i>
              </span>
            </div>
          </div>
        </div>

        <form @submit.prevent="intentarCrearEvaluacion">
          <div class="cm-field">
            <label class="cm-label">Título de la Evaluación *</label>
            <div class="cm-control">
              <input class="cm-input" type="text" v-model="evaluacion.titulo"
                placeholder="Ej: Examen Final de Matemáticas" required />
            </div>
          </div>

          <div class="cm-field">
            <label class="cm-label">Descripción</label>
            <div class="cm-control">
              <textarea class="cm-textarea" v-model="evaluacion.descripcion"
                placeholder="Describa brevemente el contenido de la evaluación" rows="3"></textarea>
            </div>
          </div>

          <div class="cm-columns">
            <div class="cm-column">
              <div class="cm-field">
                <label class="cm-label">Duración (minutos) *</label>
                <div class="cm-control cm-has-icons-right">
                  <input class="cm-input" type="number" v-model="evaluacion.duracion" min="1" placeholder="60" required />
                  <span class="cm-icon cm-is-small cm-is-right">
                    <span>⏱️</span>
                  </span>
                </div>
              </div>
            </div>
          </div>

          <div class="cm-columns">
            <div class="cm-column">
              <div class="cm-field">
                <label class="cm-label">Fecha de Inicio *</label>
                <div class="cm-control cm-has-icons-right">
                  <input class="cm-input" type="date" v-model="evaluacion.fecha" required />
                  <span class="cm-icon cm-is-small cm-is-right">
                    <span>📅</span>
                  </span>
                </div>
              </div>
            </div>
            <div class="cm-column">
              <div class="cm-field">
                <label class="cm-label">Hora de Inicio *</label>
                <div class="cm-control cm-has-icons-right">
                  <input class="cm-input" type="time" v-model="evaluacion.hora" required />
                  <span class="cm-icon cm-is-small cm-is-right">
                    <span>🕒</span>
                  </span>
                </div>
              </div>
            </div>
          </div>

          <!-- SECCIÓN DE EJERCICIOS -->
          <div class="cm-field cm-ejercicios-field">
            <div class="cm-ejercicios-section-header">
              <div class="cm-header-left">
                <div class="cm-icon-wrapper">
                  <span class="cm-ejercicios-icon">📝</span>
                </div>
                <label class="cm-label cm-ejercicios-label">Seleccione ejercicios para la evaluación *</label>
              </div>
            </div>
            <div class="cm-ejercicios-controls">
              <div class="cm-filter-bar">
                <!-- Búsqueda de ejercicios -->
                <div class="cm-search-control">
                  <div class="cm-control cm-has-icons-left">
                    <input class="cm-input cm-search-input" type="text" v-model="filtroEjercicios"
                      placeholder="Buscar ejercicios..." />
                    <span class="cm-icon cm-is-small cm-is-left">
                      <span>🔍</span>
                    </span>
                  </div>
                </div>

                <!-- Filtro por dificultad -->
                <div class="cm-difficulty-filter">
                  <div class="cm-control">
                    <div class="cm-select cm-is-small">
                      <select v-model="filtroDificultad" @change="filtrarEjercicios">
                        <option value="all">Todas las dificultades</option>
                        <option value="facil">Fácil</option>
                        <option value="intermedio">Intermedio</option>
                        <option value="dificil">Difícil</option>
                      </select>
                    </div>
                  </div>
                </div>

                <!-- Botón para limpiar filtros -->
                <div class="cm-clean-filter">
                  <button type="button" class="cm-button cm-is-small cm-is-outlined" @click="limpiarFiltros">
                    <span>Limpiar</span>
                  </button>
                </div>
              </div>

              <!-- Contador de seleccionados -->
              <div class="cm-selected-counter" style="margin-left: 10px;"
                :class="{ 'cm-has-exercises': ejerciciosSeleccionados.length > 0 }">
                <span class="cm-counter-badge">{{ ejerciciosSeleccionados.length }}</span>
                <span class="cm-counter-text">Ejercicios seleccionados</span>
              </div>
            </div>

            <!-- Grid de ejercicios -->
            <div class="cm-ejercicios-grid">
              <div v-if="ejerciciosFiltrados.length === 0" class="cm-no-ejercicios">
                <div class="cm-has-text-centered">
                  <span class="cm-empty-icon">📚</span>
                  <p class="cm-mt-3 cm-has-text-weight-medium">No hay ejercicios disponibles.</p>
                  <a href="#" class="cm-button cm-is-primary cm-is-small cm-is-outlined cm-mt-3"
                    @click.prevent="$router.push('/docente/dashboard/crear-ejercicio')">
                    Crear nuevos ejercicios
                  </a>
                </div>
              </div>
              <div v-else class="cm-ejercicios-cards">
                <div v-for="ejercicio in ejerciciosFiltrados" :key="ejercicio.id" class="cm-ejercicio-card"
                  :class="{ 'cm-is-selected': ejerciciosSeleccionados.includes(ejercicio.id) }">
                  <div class="cm-card-header" :class="getDifficultyClass(ejercicio.dificultad)">
                    <div class="cm-difficulty-badge">
                      <span class="cm-difficulty-icon">
                        {{ getDifficultyIcon(ejercicio.dificultad) }}
                      </span>
                      {{ getDifficultyLabel(ejercicio.dificultad) }}
                    </div>
                    <div class="cm-exercise-type">
                      <span class="cm-type-icon">{{ ejercicio.tipo === 'practico' ? '🔨' : '🧠' }}</span>
                      {{ ejercicio.tipo === 'practico' ? 'Práctico' : 'Teórico' }}
                    </div>
                  </div>

                  <div class="cm-card-body" @click="toggleEjercicio(ejercicio.id)">
                    <h3 class="cm-card-title">{{ ejercicio.titulo }}</h3>
                    <p class="cm-card-description">{{ truncateText(ejercicio.descripcion, 100) }}</p>

                    <div class="cm-card-footer">
                      <div class="cm-card-meta">
                        <span class="cm-meta-item cm-points">
                          <span class="cm-meta-icon">⭐</span>
                          {{ ejercicio.puntaje || 1 }} pts
                        </span>
                      </div>

                      <div class="cm-card-actions">
                        <button type="button" class="cm-action-btn cm-view" title="Ver detalles"
                          @click.stop="verDetalles(ejercicio)">
                          <span>👁️</span>
                        </button>
                        <div class="cm-checkbox-wrapper" @click.stop>
                          <input type="checkbox" :id="'ejercicio-' + ejercicio.id"
                            :checked="ejerciciosSeleccionados.includes(ejercicio.id)"
                            @change="toggleEjercicio(ejercicio.id)" />
                          <label :for="'ejercicio-' + ejercicio.id"></label>
                        </div>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>

          <!-- SECCIÓN DE OPCIONES ADICIONALES -->
          <div class="cm-options-section">
            <div class="cm-columns">
              <div class="cm-column cm-is-8">
                <div class="cm-options-container">
                  <div class="cm-options-header">
                    <span class="cm-options-icon">⚙️</span>
                    <h4 class="cm-is-size-5 cm-has-text-weight-semibold">Opciones adicionales</h4>
                  </div>
                  <div class="cm-options-content">
                    <div class="cm-field">
                      <div class="cm-control cm-option-item">
                        <label class="cm-checkbox">
                          <input type="checkbox" v-model="evaluacion.permitirRevision" />
                          <span class="cm-option-label">Permitir revisión de respuestas</span>
                        </label>
                        <small class="cm-option-description">Los estudiantes podrán revisar sus respuestas antes de
                          finalizar</small>
                      </div>
                    </div>
                    <div class="cm-field">
                      <div class="cm-control cm-option-item">
                        <label class="cm-checkbox">
                          <input type="checkbox" v-model="evaluacion.mostrarResultado" />
                          <span class="cm-option-label">Mostrar resultado al finalizar</span>
                        </label>
                        <small class="cm-option-description">Muestra el puntaje final al terminar la evaluación</small>
                      </div>
                    </div>
                    <div class="cm-field">
                      <div class="cm-control cm-option-item">
                        <label class="cm-checkbox">
                          <input type="checkbox" v-model="evaluacion.aleatorio" />
                          <span class="cm-option-label">Orden aleatorio de preguntas</span>
                        </label>
                        <small class="cm-option-description">Presenta ejercicios en diferente orden para cada
                          estudiante</small>
                      </div>
                    </div>
                  </div>
                </div>
              </div>

              <div class="cm-column cm-is-4">
                <div class="cm-puntaje-box">
                  <div class="cm-puntaje-header">
                    <span class="cm-puntaje-icon">🏆</span>
                    <h4 class="cm-is-size-5 cm-has-text-weight-semibold">Puntaje total</h4>
                  </div>
                  <div class="cm-puntaje-content">
                    <div class="cm-puntaje-display">
                      <span class="cm-puntaje-value">{{ puntajeTotal }}</span>
                      <span class="cm-puntaje-unit">puntos</span>
                    </div>
                    <div class="cm-puntaje-progress">
                      <progress class="cm-progress cm-is-warning" :value="puntajeTotal" max="100"></progress>
                    </div>
                    <p class="cm-puntaje-info">El puntaje se calcula automáticamente<br>según los ejercicios
                      seleccionados
                    </p>
                  </div>
                </div>
              </div>
            </div>
          </div>

          <div class="cm-form-actions">
            <div class="cm-field cm-is-grouped cm-is-grouped-right">
              <div class="cm-control">
                <button type="button" class="cm-button cm-is-medium cm-is-dark" @click="cancelar">
                  <span>Cancelar</span>
                </button>
              </div>
              <div class="cm-control">
                <button type="button" class="cm-button cm-is-warning cm-is-medium"
                  :class="{ 'cm-is-loading': enviando }" @click="intentarCrearEvaluacion" :disabled="enviando">
                  <span class="cm-icon" v-if="!enviando">✅</span>
                  <span v-if="enviando">{{ isEditMode ? 'Actualizando...' : 'Creando...' }}</span>
                  <span v-else>{{ buttonText }}</span>
                </button>
              </div>
            </div>
            <p class="cm-form-help-text cm-has-text-centered" v-if="!formValido">
              Complete todos los campos requeridos (*) y seleccione al menos un ejercicio para continuar
            </p>
          </div>
        </form>
      </div>
    </div>

    <!-- Modal de detalles de ejercicio -->
    <div class="cm-modal" :class="{ 'cm-is-active': mostrarDetallesModal }">
      <div class="cm-modal-background" @click="cerrarDetallesModal"></div>
      <div class="cm-modal-card cm-details-modal">
        <header class="cm-modal-card-head cm-details-modal-head"
          :class="ejercicioSeleccionado ? getDifficultyClass(ejercicioSeleccionado.dificultad) : ''">
          <p class="cm-modal-card-title">
            {{ ejercicioSeleccionado ? ejercicioSeleccionado.titulo : 'Detalles del Ejercicio' }}
          </p>
          <button class="cm-delete" aria-label="close" @click="cerrarDetallesModal"></button>
        </header>
        <section class="cm-modal-card-body" v-if="ejercicioSeleccionado">
          <!-- Información principal y etiquetas -->
          <div class="cm-tags cm-mb-4">
            <span class="cm-tag cm-is-medium" :class="getDifficultyTagClass(ejercicioSeleccionado.dificultad)">
              <span class="cm-tag-icon">{{ getDifficultyIcon(ejercicioSeleccionado.dificultad) }}</span>
              {{ getDifficultyLabel(ejercicioSeleccionado.dificultad) }}
            </span>
            <span class="cm-tag cm-is-medium"
              :class="ejercicioSeleccionado.tipo === 'practico' ? 'cm-is-info' : 'cm-is-success'">
              <span class="cm-tag-icon">{{ ejercicioSeleccionado.tipo === 'practico' ? '🔨' : '🧠' }}</span>
              {{ ejercicioSeleccionado.tipo === 'practico' ? 'Práctico' : 'Teórico' }}
            </span>
            <span class="cm-tag cm-is-medium cm-is-primary">
              <span class="cm-tag-icon">⭐</span> {{ ejercicioSeleccionado.puntaje || '1' }} pts
            </span>
          </div>

          <!-- Secciones en acordeón -->
          <div class="cm-exercise-accordion">
            <!-- Descripción -->
            <div class="cm-accordion-item">
              <div class="cm-accordion-header" @click="toggleExerciseSection('description')">
                <h3 class="cm-accordion-title">
                  <span class="cm-accordion-title-icon">📄</span> Descripción
                </h3>
                <span class="cm-accordion-icon">{{ openExerciseSections.description ? '−' : '+' }}</span>
              </div>
              <div class="cm-accordion-content" v-if="openExerciseSections.description">
                <div class="cm-content cm-description-content"
                  v-html="renderMarkdown(ejercicioSeleccionado.descripcion)">
                </div>
              </div>
            </div>

            <!-- Información general -->
            <div class="cm-accordion-item">
              <div class="cm-accordion-header" @click="toggleExerciseSection('general')">
                <h3 class="cm-accordion-title">
                  <span class="cm-accordion-title-icon">ℹ️</span> Información General
                </h3>
                <span class="cm-accordion-icon">{{ openExerciseSections.general ? '−' : '+' }}</span>
              </div>
              <div class="cm-accordion-content" v-if="openExerciseSections.general">
                <div class="cm-general-info">
                  <div class="cm-info-item">
                    <span class="cm-info-label">Creador:</span>
                    <span class="cm-info-value">{{ ejercicioSeleccionado.creador_nombre || 'Desconocido' }}</span>
                  </div>
                  <div class="cm-info-item">
                    <span class="cm-info-label">Fecha de creación:</span>
                    <span class="cm-info-value">{{ formatDate(ejercicioSeleccionado.fecha_creacion) }}</span>
                  </div>
                  <div class="cm-info-item">
                    <span class="cm-info-label">Puntos:</span>
                    <span class="cm-info-value">{{ ejercicioSeleccionado.puntaje || '1' }}</span>
                  </div>
                  <div class="cm-info-item">
                    <span class="cm-info-label">Tipo:</span>
                    <span class="cm-info-value">{{ ejercicioSeleccionado.tipo === 'practico' ? 'Práctico' : 'Teórico'
                      }}</span>
                  </div>
                  <div class="cm-info-item">
                    <span class="cm-info-label">Dificultad:</span>
                    <span class="cm-info-value">{{ getDifficultyLabel(ejercicioSeleccionado.dificultad) }}</span>
                  </div>
                  <div class="cm-info-item" v-if="ejercicioSeleccionado.credito">
                    <span class="cm-info-label">Fuente/Crédito:</span>
                    <span class="cm-info-value">{{ ejercicioSeleccionado.credito }}</span>
                  </div>
                </div>
              </div>
            </div>

            <div class="cm-info-item">
              <span class="cm-info-label">Etiquetas:</span>
              <div class="cm-info-value cm-tags-container">
                <span v-if="getTags(ejercicioSeleccionado).length === 0" class="cm-no-tags">Sin etiquetas</span>
                <span v-for="(tag, index) in getTags(ejercicioSeleccionado)" :key="index" class="cm-tag-badge">
                  {{ tag }}
                </span>
              </div>
            </div>

            <!-- Restricciones -->
            <div class="cm-accordion-item" v-if="getRestrictions(ejercicioSeleccionado)">
              <div class="cm-accordion-header" @click="toggleExerciseSection('restrictions')">
                <h3 class="cm-accordion-title">
                  <span class="cm-accordion-title-icon">🧩</span> Restricciones
                </h3>
                <span class="cm-accordion-icon">{{ openExerciseSections.restrictions ? '−' : '+' }}</span>
              </div>
              <div class="cm-accordion-content" v-if="openExerciseSections.restrictions">
                <div class="cm-content cm-markdown-content"
                  v-html="renderMarkdown(getRestrictions(ejercicioSeleccionado))">
                </div>
              </div>
            </div>

            <!-- Formato de Entrada -->
            <div class="cm-accordion-item" v-if="getInputFormats(ejercicioSeleccionado).length > 0">
              <div class="cm-accordion-header" @click="toggleExerciseSection('inputFormat')">
                <h3 class="cm-accordion-title">
                  <span class="cm-accordion-title-icon">⌨️</span> Formato de Entrada
                </h3>
                <span class="cm-accordion-icon">{{ openExerciseSections.inputFormat ? '−' : '+' }}</span>
              </div>
              <div class="cm-accordion-content" v-if="openExerciseSections.inputFormat">
                <div class="cm-content">
                  <div v-for="(format, index) in getInputFormats(ejercicioSeleccionado)" :key="index">
                    <div class="cm-markdown-content" v-html="renderMarkdown(format)"></div>
                    <hr v-if="index < getInputFormats(ejercicioSeleccionado).length - 1">
                  </div>
                </div>
              </div>
            </div>

            <!-- Formato de Salida -->
            <div class="cm-accordion-item" v-if="getOutputFormat(ejercicioSeleccionado)">
              <div class="cm-accordion-header" @click="toggleExerciseSection('outputFormat')">
                <h3 class="cm-accordion-title">
                  <span class="cm-accordion-title-icon">🖥️</span> Formato de Salida
                </h3>
                <span class="cm-accordion-icon">{{ openExerciseSections.outputFormat ? '−' : '+' }}</span>
              </div>
              <div class="cm-accordion-content" v-if="openExerciseSections.outputFormat">
                <div class="cm-content cm-markdown-content"
                  v-html="renderMarkdown(getOutputFormat(ejercicioSeleccionado))">
                </div>
              </div>
            </div>

            <!-- Ejemplos -->
            <div class="cm-accordion-item" v-if="getExamples(ejercicioSeleccionado).length > 0">
              <div class="cm-accordion-header" @click="toggleExerciseSection('examples')">
                <h3 class="cm-accordion-title">
                  <span class="cm-accordion-title-icon">🧪</span> Ejemplos
                </h3>
                <span class="cm-accordion-icon">{{ openExerciseSections.examples ? '−' : '+' }}</span>
              </div>
              <div class="cm-accordion-content" v-if="openExerciseSections.examples">
                <div class="cm-samples-container">
                  <div v-for="(example, index) in getExamples(ejercicioSeleccionado)" :key="index"
                    class="cm-sample-card">
                    <div class="cm-sample-card-header">
                      <h4 class="cm-sample-card-title">
                        <span class="cm-sample-icon">🧪</span> Ejemplo #{{ index + 1 }}
                      </h4>
                    </div>
                    <div class="cm-sample-card-content">
                      <div class="cm-sample-input">
                        <label class="cm-sample-label">
                          <span class="cm-sample-label-icon">➡️</span> Entrada:
                        </label>
                        <div class="cm-code-box">{{ example.entrada || 'N/A' }}</div>
                      </div>
                      <div class="cm-sample-output">
                        <label class="cm-sample-label">
                          <span class="cm-sample-label-icon">⬅️</span> Salida:
                        </label>
                        <div class="cm-code-box">{{ example.salida || 'N/A' }}</div>
                      </div>
                      <div class="cm-sample-explanation" v-if="example.explicacion">
                        <label class="cm-sample-label">
                          <span class="cm-sample-label-icon">💡</span> Explicación:
                        </label>
                        <div class="cm-markdown-content" v-html="renderMarkdown(example.explicacion)"></div>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </div>

            <!-- Plantilla de Código -->
            <div class="cm-accordion-item" v-if="ejercicioSeleccionado.tipo === 'practico'">
              <div class="cm-accordion-header" @click="toggleExerciseSection('template')">
                <h3 class="cm-accordion-title">
                  <span class="cm-accordion-title-icon">💻</span> Plantilla de Código
                </h3>
                <span class="cm-accordion-icon">{{ openExerciseSections.template ? '−' : '+' }}</span>
              </div>
              <div class="cm-accordion-content" v-if="openExerciseSections.template">
                <div class="cm-code-preview">
                  <pre><code>{{ getTemplateCode(ejercicioSeleccionado) }}</code></pre>
                </div>
              </div>
            </div>
          </div>
        </section>
        <footer class="cm-modal-card-foot cm-details-modal-foot">
          <div class="cm-modal-buttons-container">
            <button type="button" class="cm-button cm-is-primary" @click="seleccionarEjercicioDeModal"
              :class="{ 'cm-is-active': ejerciciosSeleccionados.includes(ejercicioSeleccionado?.id) }">
              <span v-if="ejerciciosSeleccionados.includes(ejercicioSeleccionado?.id)">
                <span class="cm-icon">✓</span> Seleccionado
              </span>
              <span v-else>
                <span class="cm-icon">+</span> Seleccionar
              </span>
            </button>
            <button type="button" class="cm-button cm-is-outlined" @click="cerrarDetallesModal">Cerrar</button>
          </div>
        </footer>
      </div>
    </div>

    <!-- Notificación de éxito -->
    <transition name="cm-fade">
      <div v-if="mostrarNotificacion" class="cm-success-notification">
        <button class="cm-success-notification-close" @click="cerrarNotificacion">×</button>
        <div class="cm-success-notification-header">
          <span class="cm-success-notification-icon">✓</span>
          <span class="cm-success-notification-title">
            {{ isEditMode ? 'Evaluación actualizada con éxito' : 'Evaluación creada con éxito' }}
          </span>
        </div>
        <div class="cm-success-notification-content">
          La evaluación ha sido creada correctamente. Comparta el siguiente código con sus estudiantes:
        </div>
        <div class="cm-success-notification-code">
          {{ codigoAcceso }}
        </div>
      </div>
    </transition>

    <!-- Notificación de error -->
    <transition name="cm-fade">
      <div v-if="mostrarErrorNotificacion" class="cm-error-notification">
        <button class="cm-error-notification-close" @click="cerrarErrorNotificacion">×</button>
        <div class="cm-error-notification-header">
          <span class="cm-error-notification-icon">⚠️</span>
          <span class="cm-error-notification-title">Errores en el formulario</span>
        </div>
        <div class="cm-error-notification-content">
          Por favor, corrija los siguientes errores:
        </div>
        <ul class="cm-error-notification-list">
          <li v-for="(error, index) in erroresFormulario" :key="index">{{ error }}</li>
        </ul>
      </div>
    </transition>
  </div>
</template>

<script>
import { ref, computed, onMounted, onUnmounted, watch } from 'vue';
import { useRouter, useRoute } from 'vue-router';
import { useStore } from 'vuex';
import { marked } from 'marked';
import DOMPurify from 'dompurify';

import exercisesService from '@/api/exercisesService';
import evaluationsService from '@/api/evaluationsService';

// Configuración de marked para mejor rendimiento
marked.setOptions({
  gfm: true,
  breaks: true,
  sanitize: false, // Usaremos DOMPurify para sanitización
  smartLists: true,
  smartypants: false
});

// Caché para markdown renderizado
const markdownCache = new Map();

export default {
  name: 'CreateEvaluation',
  setup() {
    const router = useRouter();
    const store = useStore();

    const route = useRoute();
    const isEditMode = computed(() => !!route.params.id);
    const pageTitle = computed(() => isEditMode.value ? 'Editar Evaluación' : 'Crear Nueva Evaluación');
    const buttonText = computed(() => isEditMode.value ? 'Actualizar Evaluación' : 'Crear Evaluación');

    // Estado del formulario
    const evaluacion = ref({
      titulo: '',
      descripcion: '',
      duracion: 60,
      fecha: '',
      hora: '',
      permitirRevision: true,
      mostrarResultado: true,
      aleatorio: false
    });

    // Ejercicios
    const ejercicios = ref([]);
    const filtroEjercicios = ref('');
    const filtroDificultad = ref('all');
    const ejerciciosSeleccionados = ref([]);
    const ejercicioSeleccionado = ref(null);
    const enviando = ref(false);

    // Estado para modales y notificaciones
    const mostrarNotificacion = ref(false);
    const mostrarDetallesModal = ref(false);
    const codigoAcceso = ref('');

    // Temporizador para ocultar notificaciones
    const errorNotificationTimer = ref(null);

    // Estado para notificaciones de error
    const mostrarErrorNotificacion = ref(false);
    const erroresFormulario = ref([]);

    // Estado para acordeón en modal de detalles
    const openExerciseSections = ref({
      description: true,
      general: true,
      restrictions: false,
      inputFormat: false,
      outputFormat: false,
      examples: false,
      template: false
    });


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

      return [];
    };

    // Calcular puntaje total
    const puntajeTotal = computed(() => {
      let total = 0;
      ejerciciosSeleccionados.value.forEach(id => {
        const ejercicio = ejercicios.value.find(e => e.id === id);
        if (ejercicio) {
          total += ejercicio.puntaje || 0;
        }
      });
      return total;
    });

    // Renderizar markdown con caché
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
        console.error('Error al procesar markdown:', error);
        return text;
      }
    };

    // Filtrar ejercicios
    const filtrarEjercicios = () => {
      // La función es llamada cuando cambia el filtro de dificultad
      // La lógica real se maneja en el computed ejerciciosFiltrados
    };

    // Limpiar todos los filtros
    const limpiarFiltros = () => {
      filtroEjercicios.value = '';
      filtroDificultad.value = 'all';
    };

    // Ver si estamos filtrando
    const estamosFiltrando = computed(() => {
      return filtroEjercicios.value !== '' || filtroDificultad.value !== 'all';
    });

    // Observar cambios en el filtro de texto
    watch(filtroEjercicios, () => {
      // Nada que hacer aquí, el computed ejerciciosFiltrados ya maneja esto
    });

    // Filtrar ejercicios por búsqueda y dificultad
    const ejerciciosFiltrados = computed(() => {
      if (!ejercicios.value.length) return [];

      let resultado = [...ejercicios.value];

      // Filtrar por texto de búsqueda
      if (filtroEjercicios.value) {
        const termino = filtroEjercicios.value.toLowerCase();
        resultado = resultado.filter(
          e => e.titulo?.toLowerCase().includes(termino) ||
            e.descripcion?.toLowerCase().includes(termino)
        );
      }

      // Filtrar por dificultad
      if (filtroDificultad.value !== 'all') {
        resultado = resultado.filter(e => e.dificultad === filtroDificultad.value);
      }

      return resultado;
    });

    // Validar formulario
    const formValido = computed(() => {
      return (
        evaluacion.value.titulo.trim() !== '' &&
        evaluacion.value.duracion > 0 &&
        evaluacion.value.fecha !== '' &&
        evaluacion.value.hora !== '' &&
        ejerciciosSeleccionados.value.length > 0
      );
    });

    // Cargar ejercicios y cursos al montar el componente
    onMounted(async () => {
      try {
        // Verificar si estamos en modo edición
        if (isEditMode.value) {
          // Intentar cargar desde localStorage primero (más rápido)
          const storedEval = localStorage.getItem('evaluacionEditar');
          if (storedEval) {
            const evalData = JSON.parse(storedEval);


            // Llenar el formulario con los datos
            evaluacion.value = {
              titulo: evalData.titulo || '',
              descripcion: evalData.descripcion || '',
              duracion: evalData.duracion_minutos || 60,
              permitirRevision: evalData.permitir_revision !== undefined ? evalData.permitir_revision : true,
              mostrarResultado: evalData.mostrar_resultado !== undefined ? evalData.mostrar_resultado : true,
              aleatorio: evalData.orden_aleatorio || false
            };

            // Cargar fecha y hora
            if (evalData.fecha_inicio) {
              const fecha = new Date(evalData.fecha_inicio);
              evaluacion.value.fecha = fecha.toISOString().split('T')[0];
              evaluacion.value.hora = fecha.toTimeString().substring(0, 5);
            }

            // Esperar a que se carguen los ejercicios antes de seleccionarlos
            setTimeout(() => {
              // Si hay ejercicios en la evaluación, seleccionarlos
              if (evalData.ejercicios && Array.isArray(evalData.ejercicios)) {
                ejerciciosSeleccionados.value = [...evalData.ejercicios];
              }
            }, 500);
          } else {
            // Si no está en localStorage, cargar desde la API
            const response = await evaluationsService.getDetallesEvaluacion(route.params.id);
            if (response && response.data) {
              // Aquí mapearíamos los datos de la API
              console.log('Datos cargados desde API:', response.data);
              // El mapeo dependerá de la estructura de tu API
            }
          }
        }

        // Obtener ejercicios desde la API (código original)
        const responseEjercicios = await exercisesService.getEjercicios();
        if (responseEjercicios.data) {
          ejercicios.value = responseEjercicios.data.map(exercise => {
            // Establecer dificultad por defecto si no existe
            if (!exercise.dificultad) {
              exercise.dificultad = (exercise.contenido && exercise.contenido.dificultad)
                ? exercise.contenido.dificultad
                : 'intermedio';
            }
            return exercise;
          });
        } else {
          ejercicios.value = [];
        }

      } catch (error) {
        console.error('Error al cargar datos:', error);
      }
    });

    onUnmounted(() => {
      if (errorNotificationTimer.value) {
        clearTimeout(errorNotificationTimer.value);
        errorNotificationTimer.value = null;
      }
    });

    // Métodos para gestionar los ejercicios y el modal
    const toggleEjercicio = (id) => {
      const index = ejerciciosSeleccionados.value.indexOf(id);
      if (index === -1) {
        ejerciciosSeleccionados.value.push(id);
      } else {
        ejerciciosSeleccionados.value.splice(index, 1);
      }
    };

    // Métodos para el modal de detalles
    const verDetalles = (ejercicio) => {
      ejercicioSeleccionado.value = { ...ejercicio };
      // Resetear el estado de las secciones abiertas
      openExerciseSections.value = {
        description: true,
        general: true,
        restrictions: false,
        inputFormat: false,
        outputFormat: false,
        examples: false,
        template: false
      };
      mostrarDetallesModal.value = true;
    };

    const cerrarDetallesModal = () => {
      mostrarDetallesModal.value = false;
      ejercicioSeleccionado.value = null;
    };

    const seleccionarEjercicioDeModal = () => {
      if (ejercicioSeleccionado.value) {
        toggleEjercicio(ejercicioSeleccionado.value.id);
      }
    };

    const toggleExerciseSection = (section) => {
      openExerciseSections.value[section] = !openExerciseSections.value[section];
    };

    // Crear evaluación
    const crearEvaluacion = async () => {
      enviando.value = true;

      try {
        // Formatear datos
        const fechaHora = `${evaluacion.value.fecha}T${evaluacion.value.hora}:00`;

        // Determinar el estado inicial basado en la fecha
        const fechaActual = new Date();
        const fechaInicio = new Date(fechaHora);
        let estado = 'pendiente';

        if (fechaInicio <= fechaActual) {
          estado = 'activa';
        }


        // Asegurarse de que los nombres de campos coincidan exactamente con lo que el backend espera
        const datosEvaluacion = {
          titulo: evaluacion.value.titulo,
          descripcion: evaluacion.value.descripcion,
          duracion_minutos: evaluacion.value.duracion,
          fecha_inicio: fechaHora,
          permitir_revision: evaluacion.value.permitirRevision,
          mostrar_resultado: evaluacion.value.mostrarResultado,
          orden_aleatorio: evaluacion.value.aleatorio,
          ejercicios: ejerciciosSeleccionados.value,
          puntaje_total: puntajeTotal.value,
          puntaje_aprobacion: 60, // Valor por defecto si no se especifica
          estado: estado
          // El backend manejará el creador utilizando el token de autenticación
        };

        // Enviar a la API
        const response = await evaluationsService.crearEvaluacion(datosEvaluacion);

        if (response.data) {
          // Guardar la evaluación creada en localStorage para acceso posterior
          localStorage.setItem('_reloadEvaluaciones', 'true');
          localStorage.setItem('_lastCreatedEvaluation', JSON.stringify(response.data));

          // Mostrar notificación personalizada
          codigoAcceso.value = response.data.codigo_acceso;
          mostrarNotificacion.value = true;

          // Cerrar notificación de error si estaba abierta
          if (mostrarErrorNotificacion.value) {
            cerrarErrorNotificacion();
          }

          // Redirigir después de un retraso corto
          setTimeout(() => {
            router.push('/docente/dashboard/evaluaciones');
          }, 3000);
        }
      } catch (error) {
        console.error('Error al crear evaluación:', error);
        const errores = [];
        let mensajeError = 'Ocurrió un error al crear la evaluación.';

        if (error.response && error.response.data) {
          if (error.response.data.message) {
            mensajeError = error.response.data.message;
            errores.push(mensajeError);
          } else if (typeof error.response.data === 'object') {
            // Formatar errores de objeto a cadena legible
            for (const campo in error.response.data) {
              const mensaje = Array.isArray(error.response.data[campo])
                ? error.response.data[campo].join('. ')
                : error.response.data[campo];
              errores.push(`${campo}: ${mensaje}`);
            }
          }
        } else {
          errores.push(mensajeError);
        }

        // Mostrar los errores en la notificación con temporizador
        mostrarErrorConTemporizador(errores);
      } finally {
        enviando.value = false;
      }
    };

    // Actualizar evaluación
    const actualizarEvaluacion = async () => {
      enviando.value = true;

      try {
        // Formatear datos
        const fechaHora = `${evaluacion.value.fecha}T${evaluacion.value.hora}:00`;

        // Usar directamente el ID seleccionado, asegurando que sea un entero
        const cursoId = parseInt(evaluacion.value.curso);

        // Asegurarse de que los nombres de campos coincidan exactamente con lo que el backend espera
        const datosEvaluacion = {
          titulo: evaluacion.value.titulo,
          descripcion: evaluacion.value.descripcion,
          curso: cursoId,
          duracion_minutos: evaluacion.value.duracion,
          fecha_inicio: fechaHora,
          permitir_revision: evaluacion.value.permitirRevision,
          mostrar_resultado: evaluacion.value.mostrarResultado,
          orden_aleatorio: evaluacion.value.aleatorio,
          ejercicios: ejerciciosSeleccionados.value,
          puntaje_total: puntajeTotal.value,
          puntaje_aprobacion: 60
        };

        console.log("Datos formateados para enviar:", JSON.stringify(datosEvaluacion));

        // Enviar a la API
        const response = await evaluationsService.actualizarEvaluacion(route.params.id, datosEvaluacion);

        if (response.data) {
          // El resto del código permanece igual...
          localStorage.removeItem('evaluacionEditar');
          localStorage.setItem('_reloadEvaluaciones', 'true');
          mostrarNotificacion.value = true;
          codigoAcceso.value = response.data.codigo_acceso || '';
          if (mostrarErrorNotificacion.value) {
            cerrarErrorNotificacion();
          }
          setTimeout(() => {
            router.push('/docente/dashboard/evaluaciones');
          }, 3000);
        }
      } catch (error) {
        console.error('Error al actualizar evaluación:', error);
      } finally {
        enviando.value = false;
      }
    };


    const cancelar = () => {
      if (confirm('¿Está seguro que desea cancelar? Los cambios no se guardarán.')) {
        router.push('/dashboard');
      }
    };

    const cerrarNotificacion = () => {
      mostrarNotificacion.value = false;
    };

    const cerrarErrorNotificacion = () => {
      // Limpiar el temporizador si existe
      if (errorNotificationTimer.value) {
        clearTimeout(errorNotificationTimer.value);
        errorNotificationTimer.value = null;
      }
      mostrarErrorNotificacion.value = false;
      erroresFormulario.value = [];
    };

    const mostrarErrorConTemporizador = (errores) => {
      // Actualizar errores y mostrar notificación
      erroresFormulario.value = errores;
      mostrarErrorNotificacion.value = true;

      // Limpiar temporizador anterior si existe
      if (errorNotificationTimer.value) {
        clearTimeout(errorNotificationTimer.value);
      }

      // Establecer un nuevo temporizador (5 segundos)
      errorNotificationTimer.value = setTimeout(() => {
        mostrarErrorNotificacion.value = false;
        erroresFormulario.value = [];
        errorNotificationTimer.value = null;
      }, 5000); // 5000 ms = 5 segundos
    };


    const intentarCrearEvaluacion = () => {
      // Validar el formulario
      const errores = [];

      if (!evaluacion.value.titulo.trim()) {
        errores.push('El título de la evaluación es obligatorio');
      }

      if (!evaluacion.value.duracion || evaluacion.value.duracion <= 0) {
        errores.push('La duración debe ser mayor a 0 minutos');
      }

      if (!evaluacion.value.fecha) {
        errores.push('La fecha de inicio es obligatoria');
      }

      if (!evaluacion.value.hora) {
        errores.push('La hora de inicio es obligatoria');
      }

      if (ejerciciosSeleccionados.value.length === 0) {
        errores.push('Debe seleccionar al menos un ejercicio');
      }

      // Si hay errores, mostrar notificación y detener
      if (errores.length > 0) {
        mostrarErrorConTemporizador(errores);

        // Hacer scroll al inicio para ver la notificación
        window.scrollTo({ top: 0, behavior: 'smooth' });
        return;
      }

      // Si no hay errores, proceder con la creación o actualización
      if (isEditMode.value) {
        actualizarEvaluacion();
      } else {
        crearEvaluacion();
      }
    };


    // Métodos de utilidad
    const truncateText = (text, maxLength) => {
      if (!text) return '';
      if (text.length <= maxLength) return text;
      return text.substring(0, maxLength) + '...';
    };

    const formatDate = (dateString) => {
      if (!dateString) return 'Fecha desconocida';

      const date = new Date(dateString);
      return date.toLocaleDateString('es-ES', {
        year: 'numeric',
        month: 'long',
        day: 'numeric'
      });
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
        case 'facil': return 'cm-difficulty-easy';
        case 'intermedio': return 'cm-difficulty-medium';
        case 'dificil': return 'cm-difficulty-hard';
        default: return 'cm-difficulty-medium';
      }
    };

    const getDifficultyTagClass = (difficulty) => {
      switch (difficulty) {
        case 'facil': return 'cm-is-success';
        case 'intermedio': return 'cm-is-primary';
        case 'dificil': return 'cm-is-danger';
        default: return 'cm-is-primary';
      }
    };

    const getDifficultyIcon = (difficulty) => {
      switch (difficulty) {
        case 'facil': return '🌱';
        case 'intermedio': return '🏆';
        case 'dificil': return '🔥';
        default: return '🏆';
      }
    };

    // Funciones para extraer datos del ejercicio seleccionado para el modal
    const getRestrictions = (exercise) => {
      if (exercise?.contenido && exercise.contenido.restricciones) {
        return exercise.contenido.restricciones;
      }
      return '';
    };

    const getInputFormats = (exercise) => {
      if (exercise?.contenido && exercise.contenido.formatos_entrada && Array.isArray(exercise.contenido.formatos_entrada)) {
        return exercise.contenido.formatos_entrada.filter(format => format && format.trim() !== '');
      }
      return [];
    };

    const getOutputFormat = (exercise) => {
      if (exercise?.contenido && exercise.contenido.formato_salida) {
        return exercise.contenido.formato_salida;
      }
      return '';
    };

    const getExamples = (exercise) => {
      if (exercise?.contenido && exercise.contenido.ejemplos && Array.isArray(exercise.contenido.ejemplos)) {
        return exercise.contenido.ejemplos;
      }
      return [];
    };

    const getTemplateCode = (exercise) => {
      if (exercise?.contenido && exercise.contenido.template) {
        return exercise.contenido.template;
      } else if (exercise?.template) {
        return exercise.template;
      }
      return 'print("Hello, World!")';
    };

    return {
      evaluacion,
      ejercicios,
      filtroEjercicios,
      filtroDificultad,
      ejerciciosSeleccionados,
      ejercicioSeleccionado,
      puntajeTotal,
      formValido,
      ejerciciosFiltrados,
      enviando,
      mostrarNotificacion,
      mostrarDetallesModal,
      openExerciseSections,
      codigoAcceso,
      estamosFiltrando,
      filtrarEjercicios,
      limpiarFiltros,
      renderMarkdown,
      toggleEjercicio,
      verDetalles,
      cerrarDetallesModal,
      seleccionarEjercicioDeModal,
      toggleExerciseSection,
      intentarCrearEvaluacion,
      crearEvaluacion,
      isEditMode,
      pageTitle,
      buttonText,
      actualizarEvaluacion,
      cancelar,
      cerrarNotificacion,
      mostrarErrorNotificacion,
      erroresFormulario,
      cerrarErrorNotificacion,
      errorNotificationTimer,
      mostrarErrorConTemporizador,
      truncateText,
      formatDate,
      getDifficultyLabel,
      getDifficultyClass,
      getDifficultyTagClass,
      getDifficultyIcon,
      getRestrictions,
      getInputFormats,
      getTags,
      getOutputFormat,
      getExamples,
      getTemplateCode
    };
  }
};
</script>

<style>
/* =================== ESTILOS GLOBALES (SIN SCOPED) =================== */
.curiosmaze-create-eval-wrapper .cm-fade-enter-active,
.curiosmaze-create-eval-wrapper .cm-fade-leave-active {
  transition: opacity var(--transition-smooth), transform var(--transition-smooth);
}

.curiosmaze-create-eval-wrapper .cm-fade-enter-from,
.curiosmaze-create-eval-wrapper .cm-fade-leave-to {
  opacity: 0;
  transform: translateY(-10px);
}
</style>

<style scoped>
/* =================== CONTENEDOR PRINCIPAL =================== */
.curiosmaze-create-eval-wrapper {
  background-color: var(--color-bg-main);
  min-height: 100vh;
  color: var(--color-text-primary);
  padding: 2rem 1rem;
  display: flex;
  justify-content: center;
  width: 100%;
  font-family: 'Poppins', 'Segoe UI', sans-serif;
}

.curiosmaze-create-eval-wrapper .cm-create-eval-container {
  width: 100%;
  max-width: 1200px;
}

.curiosmaze-create-eval-wrapper .cm-form-container {
  width: 100%;
  background-color: var(--color-bg-main);
  border-radius: var(--border-radius-lg);
  border-top: 4px solid var(--color-primary);
  box-shadow: var(--shadow-lg);
  padding: 2rem;
  will-change: transform;
  margin-bottom: 2rem;
}

/* =================== HEADER =================== */
.curiosmaze-create-eval-wrapper .cm-header {
  margin-bottom: 2.5rem;
  padding-bottom: 1.5rem;
  border-bottom: 1px solid var(--color-border);
}

.curiosmaze-create-eval-wrapper .cm-header-content {
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.curiosmaze-create-eval-wrapper .cm-header-text {
  flex: 1;
}

.curiosmaze-create-eval-wrapper .cm-header-text .cm-title {
  margin-bottom: 0.5rem;
  font-weight: 600;
  color: var(--color-text-primary);
  font-size: 1.8rem;
}

.curiosmaze-create-eval-wrapper .cm-header-text .cm-subtitle {
  color: var(--color-text-secondary);
  font-weight: 400;
  max-width: 80%;
  font-size: 1.2rem;
}

.curiosmaze-create-eval-wrapper .cm-header-icon {
  margin-left: 1.5rem;
}

.curiosmaze-create-eval-wrapper .cm-icon-container {
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

/* =================== FORMULARIOS E INPUTS =================== */
.curiosmaze-create-eval-wrapper .cm-input,
.curiosmaze-create-eval-wrapper .cm-textarea,
.curiosmaze-create-eval-wrapper .cm-select select {
  background-color: var(--color-bg-element);
  border: 1px solid var(--color-border);
  color: var(--color-text-primary);
  box-shadow: none;
  transition: border-color var(--transition-fast), box-shadow var(--transition-fast);
  width: 100%;
  padding: 0.5rem 0.75rem;
  font-size: 1rem;
  line-height: 1.5;
  border-radius: var(--border-radius-sm);
}

.curiosmaze-create-eval-wrapper .cm-input:focus,
.curiosmaze-create-eval-wrapper .cm-textarea:focus,
.curiosmaze-create-eval-wrapper .cm-select select:focus {
  border-color: var(--color-primary);
  box-shadow: 0 0 0 2px rgba(235, 179, 0, 0.2);
  outline: none;
}

.curiosmaze-create-eval-wrapper .cm-select {
  position: relative;
  width: 100%;
}

.curiosmaze-create-eval-wrapper .cm-select select {
  appearance: none;
  padding-right: 2.5rem;
  background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='24' height='24' viewBox='0 0 24 24' fill='none' stroke='white' stroke-width='2' stroke-linecap='round' stroke-linejoin='round'%3E%3Cpolyline points='6 9 12 15 18 9'%3E%3C/polyline%3E%3C/svg%3E");
  background-repeat: no-repeat;
  background-position: right 0.5rem center;
  background-size: 1.25rem;
}

.curiosmaze-create-eval-wrapper .cm-label {
  color: var(--color-text-primary);
  font-weight: 600;
  margin-bottom: 0.5rem;
  display: block;
}

.curiosmaze-create-eval-wrapper .cm-field {
  margin-bottom: 1.5rem;
}

.curiosmaze-create-eval-wrapper .cm-control {
  position: relative;
}

/* =================== ICONOS =================== */
.curiosmaze-create-eval-wrapper .cm-icon.cm-is-small {
  position: absolute;
  top: 0;
  height: 100%;
  width: 2.5rem;
  display: flex;
  align-items: center;
  justify-content: center;
  pointer-events: none;
}

.curiosmaze-create-eval-wrapper .cm-icon.cm-is-right {
  right: 0;
}

.curiosmaze-create-eval-wrapper .cm-icon.cm-is-left {
  left: 0;
}

.curiosmaze-create-eval-wrapper .cm-has-icons-right .cm-input {
  padding-right: 2.5rem;
}

.curiosmaze-create-eval-wrapper .cm-has-icons-left .cm-input {
  padding-left: 2.5rem;
}

.curiosmaze-create-eval-wrapper .cm-icon {
  opacity: 100% !important;
}

/* =================== LAYOUT DE COLUMNAS =================== */
.curiosmaze-create-eval-wrapper .cm-columns {
  display: flex;
  flex-wrap: wrap;
  margin-left: -0.75rem;
  margin-right: -0.75rem;
  margin-top: -0.75rem;
}

.curiosmaze-create-eval-wrapper .cm-columns:last-child {
  margin-bottom: -0.75rem;
}

.curiosmaze-create-eval-wrapper .cm-column {
  padding: 0.75rem;
  flex: 1 0 0%;
}

.curiosmaze-create-eval-wrapper .cm-column.cm-is-8 {
  flex: 0 0 66.66667%;
  max-width: 66.66667%;
}

.curiosmaze-create-eval-wrapper .cm-column.cm-is-4 {
  flex: 0 0 33.33333%;
  max-width: 33.33333%;
}

/* =================== SECCIÓN DE EJERCICIOS =================== */
.curiosmaze-create-eval-wrapper .cm-ejercicios-field {
  margin-top: 2.5rem;
  margin-bottom: 2.5rem;
  border: 1px solid var(--color-border);
  border-radius: var(--border-radius);
  overflow: hidden;
  background-color: var(--color-bg-element);
}

.curiosmaze-create-eval-wrapper .cm-ejercicios-section-header {
  display: flex;
  align-items: center;
  padding: 1.25rem 1.5rem;
  border-bottom: 2px solid var(--color-border);
  background-color: var(--color-bg-element-alt);
}

.curiosmaze-create-eval-wrapper .cm-header-left {
  display: flex;
  align-items: center;
}

.curiosmaze-create-eval-wrapper .cm-icon-wrapper {
  width: 40px;
  height: 40px;
  background-color: var(--color-primary);
  border-radius: var(--border-radius-sm);
  display: flex;
  align-items: center;
  justify-content: center;
  margin-right: 1rem;
  box-shadow: var(--shadow-sm);
}

.curiosmaze-create-eval-wrapper .cm-ejercicios-icon {
  font-size: 1.5rem;
  color: var(--color-bg-main);
}

.curiosmaze-create-eval-wrapper .cm-ejercicios-label {
  margin-bottom: 0;
  font-size: 1.1rem;
}

/* =================== CONTROLES DE EJERCICIOS =================== */
.curiosmaze-create-eval-wrapper .cm-ejercicios-controls {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1rem 1.5rem;
  background-color: var(--color-bg-element-alt);
  border-bottom: 1px solid var(--color-border);
}

.curiosmaze-create-eval-wrapper .cm-filter-bar {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  flex-wrap: wrap;
  flex: 1;
}

.curiosmaze-create-eval-wrapper .cm-search-control {
  flex: 1;
  min-width: 200px;
}

.curiosmaze-create-eval-wrapper .cm-search-input {
  background-color: var(--color-bg-main);
  border: 1px solid var(--color-border);
  color: var(--color-text-primary);
  box-shadow: none;
  height: 2.25rem;
}

.curiosmaze-create-eval-wrapper .cm-search-input:focus {
  border-color: var(--color-primary);
  box-shadow: 0 0 0 1px rgba(235, 179, 0, 0.3);
}

.curiosmaze-create-eval-wrapper .cm-difficulty-filter {
  min-width: 150px;
}

.curiosmaze-create-eval-wrapper .cm-difficulty-filter .cm-select select {
  background-color: var(--color-bg-main);
  border: 1px solid var(--color-border);
  color: var(--color-text-primary);
  height: 2.25rem;
  font-size: 1rem;
}

.curiosmaze-create-eval-wrapper .cm-selected-counter {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  font-size: 0.9rem;
  color: var(--color-text-muted);
  padding: 0.5rem 1rem;
  border-radius: var(--border-radius);
  border: 1px solid transparent;
}

.curiosmaze-create-eval-wrapper .cm-selected-counter.cm-has-exercises {
  background-color: rgba(235, 179, 0, 0.1);
  border: 1px solid rgba(235, 179, 0, 0.2);
  color: var(--color-primary);
}

.curiosmaze-create-eval-wrapper .cm-counter-badge {
  display: flex;
  align-items: center;
  justify-content: center;
  height: 24px;
  width: 24px;
  border-radius: 50%;
  background-color: var(--color-primary);
  color: var(--color-bg-main);
  font-weight: 600;
}

/* =================== BOTONES =================== */
.curiosmaze-create-eval-wrapper .cm-button {
  cursor: pointer;
  justify-content: center;
  padding: 0.5em 1em;
  text-align: center;
  white-space: nowrap;
  border-radius: var(--border-radius-sm);
  font-size: 1rem;
  height: auto;
  border: 1px solid transparent;
  background-color: var(--color-bg-element);
  color: var(--color-text-primary);
  transition: all var(--transition-fast);
  display: inline-flex;
  align-items: center;
}

.curiosmaze-create-eval-wrapper .cm-button:hover {
  background-color: var(--color-bg-element-hover);
}

.curiosmaze-create-eval-wrapper .cm-button.cm-is-primary {
  background-color: var(--color-info);
  color: var(--color-text-primary);
}

.curiosmaze-create-eval-wrapper .cm-button.cm-is-warning {
  background-color: var(--color-primary);
  color: var(--color-bg-main);
}

.curiosmaze-create-eval-wrapper .cm-button.cm-is-dark {
  background-color: var(--color-bg-element-alt);
  color: var(--color-text-primary);
}

.curiosmaze-create-eval-wrapper .cm-button.cm-is-outlined {
  background-color: transparent;
  border-color: var(--color-border);
}

.curiosmaze-create-eval-wrapper .cm-button.cm-is-small {
  font-size: 0.85rem;
  padding: 0.25em 0.75em;
}

.curiosmaze-create-eval-wrapper .cm-button.cm-is-medium {
  font-size: 1.1rem;
  padding: 0.625em 1.25em;
}

.curiosmaze-create-eval-wrapper .cm-clean-filter .cm-button {
  background-color: var(--color-bg-main);
  border: 1px solid var(--color-border);
  color: var(--color-text-secondary);
  height: 2.25rem;
  padding: 0 1rem;
}

.curiosmaze-create-eval-wrapper .cm-clean-filter .cm-button:hover {
  background-color: var(--color-bg-element-hover);
  transform: none;
  box-shadow: none;
}

/* =================== GRID Y TARJETAS DE EJERCICIOS =================== */
.curiosmaze-create-eval-wrapper .cm-ejercicios-grid {
  max-height: 450px;
  overflow-y: auto;
  background-color: var(--color-bg-main);
  padding: 1.25rem;
}

.curiosmaze-create-eval-wrapper .cm-no-ejercicios {
  padding: 3rem 2rem;
  background-color: var(--color-bg-element-alt);
  border-radius: var(--border-radius);
  text-align: center;
}

.curiosmaze-create-eval-wrapper .cm-empty-icon {
  font-size: 3rem;
  color: var(--color-primary);
  margin-bottom: 1rem;
  display: block;
}

.curiosmaze-create-eval-wrapper .cm-ejercicios-cards {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
  gap: 1.25rem;
}

.curiosmaze-create-eval-wrapper .cm-ejercicio-card {
  background-color: var(--color-bg-element);
  border: 1px solid var(--color-border);
  border-radius: var(--border-radius);
  overflow: hidden;
  transition: all var(--transition-fast) ease;
  position: relative;
  height: 100%;
  display: flex;
  flex-direction: column;
  box-shadow: var(--shadow-sm);
}

.curiosmaze-create-eval-wrapper .cm-ejercicio-card:hover {
  transform: translateY(-4px);
  box-shadow: var(--shadow);
}

.curiosmaze-create-eval-wrapper .cm-ejercicio-card.cm-is-selected {
  border-color: var(--color-primary);
  box-shadow: 0 0 0 2px var(--color-primary);
}

.curiosmaze-create-eval-wrapper .cm-ejercicio-card .cm-card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0.75rem 1rem;
  color: var(--color-text-primary);
}

.curiosmaze-create-eval-wrapper .cm-ejercicio-card .cm-card-header.cm-difficulty-easy {
  background: linear-gradient(135deg, var(--color-success), var(--color-success-dark));
}

.curiosmaze-create-eval-wrapper .cm-ejercicio-card .cm-card-header.cm-difficulty-medium {
  background: linear-gradient(135deg, var(--color-primary), var(--color-primary-dark));
}

.curiosmaze-create-eval-wrapper .cm-ejercicio-card .cm-card-header.cm-difficulty-hard {
  background: linear-gradient(135deg, var(--color-error), var(--color-error-dark));
}

.curiosmaze-create-eval-wrapper .cm-difficulty-badge,
.curiosmaze-create-eval-wrapper .cm-exercise-type {
  font-size: 0.8rem;
  font-weight: 500;
  display: flex;
  align-items: center;
  gap: 0.35rem;
}

.curiosmaze-create-eval-wrapper .cm-ejercicio-card .cm-card-body {
  padding: 1rem;
  display: flex;
  flex-direction: column;
  flex-grow: 1;
  cursor: pointer;
}

.curiosmaze-create-eval-wrapper .cm-ejercicio-card .cm-card-title {
  font-size: 1rem;
  font-weight: 600;
  margin-bottom: 0.5rem;
  color: var(--color-text-primary);
  line-height: 1.4;
}

.curiosmaze-create-eval-wrapper .cm-ejercicio-card .cm-card-description {
  font-size: 0.9rem;
  color: var(--color-text-secondary);
  flex: 1;
  line-height: 1.5;
  margin-bottom: 0.75rem;
}

.curiosmaze-create-eval-wrapper .cm-ejercicio-card .cm-card-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0.75rem 1rem;
  background-color: var(--color-bg-element-alt);
  border-top: 1px solid var(--color-border);
  margin-top: auto;
}

.curiosmaze-create-eval-wrapper .cm-card-meta {
  display: flex;
  gap: 1rem;
}

.curiosmaze-create-eval-wrapper .cm-meta-item {
  font-size: 0.85rem;
  display: flex;
  align-items: center;
  gap: 0.35rem;
  color: var(--color-text-secondary);
}

.curiosmaze-create-eval-wrapper .cm-meta-item.cm-points {
  color: var(--color-primary);
  font-weight: 500;
}

.curiosmaze-create-eval-wrapper .cm-card-actions {
  display: flex;
  align-items: center;
  gap: 0.75rem;
}

.curiosmaze-create-eval-wrapper .cm-action-btn {
  background: none;
  border: none;
  font-size: 1.1rem;
  cursor: pointer;
  padding: 0.25rem;
  display: flex;
  align-items: center;
  justify-content: center;
  color: var(--color-text-secondary);
  transition: color var(--transition-fast) ease;
}

.curiosmaze-create-eval-wrapper .cm-action-btn.cm-view:hover {
  color: var(--color-info);
}

/* =================== CHECKBOX =================== */
.curiosmaze-create-eval-wrapper .cm-checkbox-wrapper {
  position: relative;
  width: 24px;
  height: 24px;
}

.curiosmaze-create-eval-wrapper .cm-checkbox-wrapper input[type="checkbox"] {
  position: absolute;
  opacity: 0;
  cursor: pointer;
  height: 0;
  width: 0;
}

.curiosmaze-create-eval-wrapper .cm-checkbox-wrapper label {
  position: absolute;
  top: 0;
  left: 0;
  height: 24px;
  width: 24px;
  background-color: var(--color-bg-main);
  border: 2px solid var(--color-border);
  border-radius: 4px;
  cursor: pointer;
  transition: all var(--transition-fast) ease;
}

.curiosmaze-create-eval-wrapper .cm-checkbox-wrapper input[type="checkbox"]:checked~label {
  background-color: var(--color-primary);
  border-color: var(--color-primary);
}

.curiosmaze-create-eval-wrapper .cm-checkbox-wrapper label:after {
  content: "";
  position: absolute;
  display: none;
  left: 7px;
  top: 3px;
  width: 6px;
  height: 12px;
  border: solid var(--color-text-primary);
  border-width: 0 2px 2px 0;
  transform: rotate(45deg);
}

.curiosmaze-create-eval-wrapper .cm-checkbox-wrapper input[type="checkbox"]:checked~label:after {
  display: block;
}

.curiosmaze-create-eval-wrapper .cm-checkbox-wrapper:hover label {
  border-color: var(--color-primary);
}

/* =================== TAGS =================== */
.curiosmaze-create-eval-wrapper .cm-ejercicio-card .cm-tag {
  padding: 0.3em 0.75em;
  border-radius: 16px;
  font-size: 0.8rem;
  font-weight: 500;
  display: flex;
  align-items: center;
  gap: 0.3em;
}

.curiosmaze-create-eval-wrapper .cm-tag-icon {
  margin-right: 0.25rem;
}

.curiosmaze-create-eval-wrapper .cm-tag.cm-is-success {
  background-color: var(--color-success);
  color: var(--color-text-primary);
}

.curiosmaze-create-eval-wrapper .cm-tag.cm-is-primary {
  background-color: var(--color-primary);
  color: var(--color-bg-main);
}

.curiosmaze-create-eval-wrapper .cm-tag.cm-is-danger {
  background-color: var(--color-error);
  color: var(--color-text-primary);
}

.curiosmaze-create-eval-wrapper .cm-tag.cm-is-info {
  background-color: var(--color-info);
  color: var(--color-text-primary);
}

.curiosmaze-create-eval-wrapper .cm-tags-container {
  display: flex;
  flex-wrap: wrap;
  gap: 0.5rem;
}

.curiosmaze-create-eval-wrapper .cm-tag-badge {
  background-color: var(--color-secondary-dark);
  color: var(--color-text-primary);
  padding: 0.2rem 0.5rem;
  border-radius: 4px;
  font-size: 0.8rem;
  font-weight: 500;
}

.curiosmaze-create-eval-wrapper .cm-no-tags {
  color: var(--color-text-muted);
  font-style: italic;
}

/* =================== MODAL =================== */
.curiosmaze-create-eval-wrapper .cm-modal-card {
  max-width: 800px;
  width: 90%;
  max-height: 90vh;
  margin: 0 auto;
  display: flex;
  flex-direction: column;
  background-color: var(--color-bg-main);
  color: var(--color-text-primary);
  border-radius: var(--border-radius-lg);
  overflow: hidden;
  box-shadow: var(--shadow-lg);
  border-top: 4px solid var(--color-primary);
}

.curiosmaze-create-eval-wrapper .cm-modal-card-head {
  background-color: var(--color-bg-element);
  color: var(--color-text-primary);
  border-bottom: 1px solid var(--color-border);
  padding: 1.25rem;
}

.curiosmaze-create-eval-wrapper .cm-modal-card-head.cm-difficulty-easy {
  background: linear-gradient(135deg, var(--color-success), var(--color-success-dark));
}

.curiosmaze-create-eval-wrapper .cm-modal-card-head.cm-difficulty-medium {
  background: linear-gradient(135deg, var(--color-primary), var(--color-primary-dark));
}

.curiosmaze-create-eval-wrapper .cm-modal-card-head.cm-difficulty-hard {
  background: linear-gradient(135deg, var(--color-error), var(--color-error-dark));
}

.curiosmaze-create-eval-wrapper .cm-modal-card-title {
  color: var(--color-text-primary);
  font-weight: 600;
  font-size: 1.4rem;
}

.curiosmaze-create-eval-wrapper .cm-modal-card-body {
  flex-grow: 1;
  overflow-y: auto;
  padding: 1.75rem;
  background-color: var(--color-bg-main);
}

.curiosmaze-create-eval-wrapper .cm-modal-card-foot {
  background-color: var(--color-bg-element);
  border-top: 1px solid var(--color-border);
  padding: 1rem 1.5rem;
  display: flex;
  justify-content: flex-end;
}

.curiosmaze-create-eval-wrapper .cm-modal-buttons-container {
  display: flex;
  gap: 0.75rem;
}

.curiosmaze-create-eval-wrapper .cm-modal {
  display: none;
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  z-index: 1000;
  align-items: center;
  justify-content: center;
}

.curiosmaze-create-eval-wrapper .cm-modal.cm-is-active {
  display: flex;
}

.curiosmaze-create-eval-wrapper .cm-modal-background {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background-color: rgba(0, 0, 0, 0.75);
  z-index: -1;
}

.curiosmaze-create-eval-wrapper .cm-delete {
  background-color: rgba(0, 0, 0, 0.2);
  border: none;
  border-radius: 290486px;
  cursor: pointer;
  display: inline-block;
  height: 20px;
  position: relative;
  vertical-align: top;
  width: 20px;
}

.curiosmaze-create-eval-wrapper .cm-delete::before,
.curiosmaze-create-eval-wrapper .cm-delete::after {
  background-color: var(--color-text-primary);
  content: "";
  display: block;
  left: 50%;
  position: absolute;
  top: 50%;
  transform: translateX(-50%) translateY(-50%) rotate(45deg);
  transform-origin: center center;
}

.curiosmaze-create-eval-wrapper .cm-delete::before {
  height: 2px;
  width: 50%;
}

.curiosmaze-create-eval-wrapper .cm-delete::after {
  height: 50%;
  width: 2px;
}

/* =================== MARKDOWN =================== */
.curiosmaze-create-eval-wrapper .cm-markdown-content {
  line-height: 1.6;
  color: var(--color-text-primary);
}

.curiosmaze-create-eval-wrapper .cm-description-content {
  font-size: 1.05rem;
  padding: 0.5rem;
}

.curiosmaze-create-eval-wrapper .cm-markdown-content h1,
.curiosmaze-create-eval-wrapper .cm-markdown-content h2,
.curiosmaze-create-eval-wrapper .cm-markdown-content h3 {
  color: var(--color-primary);
  margin-top: 1rem;
  margin-bottom: 0.5rem;
  font-weight: 600;
}

.curiosmaze-create-eval-wrapper .cm-markdown-content h1 {
  font-size: 1.5rem;
  border-bottom: 1px solid var(--color-border);
  padding-bottom: 0.5rem;
}

.curiosmaze-create-eval-wrapper .cm-markdown-content h2 {
  font-size: 1.3rem;
}

.curiosmaze-create-eval-wrapper .cm-markdown-content h3 {
  font-size: 1.1rem;
}

.curiosmaze-create-eval-wrapper .cm-markdown-content code {
  background-color: var(--color-bg-darker);
  padding: 0.2rem 0.4rem;
  border-radius: 0.3rem;
  font-family: monospace;
  font-size: 0.9em;
  color: var(--color-text-secondary);
}

.curiosmaze-create-eval-wrapper .cm-markdown-content pre {
  background-color: var(--color-bg-darker);
  padding: 1rem;
  border-radius: 0.5rem;
  overflow-x: auto;
  margin: 1rem 0;
  border: 1px solid var(--color-border);
}

.curiosmaze-create-eval-wrapper .cm-markdown-content pre code {
  background-color: transparent;
  padding: 0;
  border-radius: 0;
}

.curiosmaze-create-eval-wrapper .cm-markdown-content p {
  margin-bottom: 1rem;
}

.curiosmaze-create-eval-wrapper .cm-markdown-content strong {
  color: var(--color-primary);
  font-weight: 600;
}

.curiosmaze-create-eval-wrapper .cm-markdown-content em {
  font-style: italic;
}

.curiosmaze-create-eval-wrapper .cm-markdown-content ul,
.curiosmaze-create-eval-wrapper .cm-markdown-content ol {
  padding-left: 1.5rem;
  margin-bottom: 1rem;
  margin-top: 0.5rem;
}

.curiosmaze-create-eval-wrapper .cm-markdown-content li {
  margin-bottom: 0.5rem;
}

.curiosmaze-create-eval-wrapper .cm-markdown-content a {
  color: var(--color-primary);
  text-decoration: underline;
}

.curiosmaze-create-eval-wrapper .cm-markdown-content blockquote {
  border-left: 3px solid var(--color-primary);
  padding-left: 1rem;
  margin-left: 0;
  color: var(--color-text-secondary);
  font-style: italic;
  margin-bottom: 1rem;
}

/* =================== ACORDEÓN =================== */
.curiosmaze-create-eval-wrapper .cm-exercise-accordion {
  display: flex;
  flex-direction: column;
  gap: 1rem;
  margin-top: 1.5rem;
}

.curiosmaze-create-eval-wrapper .cm-accordion-item {
  border: 1px solid var(--color-border);
  border-radius: var(--border-radius-sm);
  overflow: hidden;
  box-shadow: var(--shadow-sm);
  background-color: var(--color-bg-element-alt);
}

.curiosmaze-create-eval-wrapper .cm-accordion-header {
  padding: 1rem 1.25rem;
  display: flex;
  justify-content: space-between;
  align-items: center;
  background-color: var(--color-bg-element);
  cursor: pointer;
  user-select: none;
  transition: background-color var(--transition-fast) ease;
}

.curiosmaze-create-eval-wrapper .cm-accordion-header:hover {
  background-color: var(--color-bg-element-hover);
}

.curiosmaze-create-eval-wrapper .cm-accordion-title {
  margin: 0;
  font-size: 1.1rem;
  font-weight: 600;
  color: var(--color-text-primary);
  display: flex;
  align-items: center;
  gap: 0.75rem;
}

.curiosmaze-create-eval-wrapper .cm-accordion-title-icon {
  font-size: 1.3rem;
  color: var(--color-primary);
}

.curiosmaze-create-eval-wrapper .cm-accordion-icon {
  font-size: 1.5rem;
  font-weight: bold;
  color: var(--color-primary);
  transition: transform var(--transition-fast) ease;
}

.curiosmaze-create-eval-wrapper .cm-accordion-content {
  padding: 1.5rem;
  background-color: var(--color-bg-main);
  border-top: 1px solid var(--color-border);
}

.curiosmaze-create-eval-wrapper .cm-general-info {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(250px, 1fr));
  gap: 0.75rem;
}

.curiosmaze-create-eval-wrapper .cm-info-item {
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
}

.curiosmaze-create-eval-wrapper .cm-info-label {
  font-size: 0.8rem;
  color: var(--color-text-muted);
  font-weight: 500;
}

.curiosmaze-create-eval-wrapper .cm-info-value {
  font-size: 0.95rem;
  color: var(--color-text-primary);
}

/* =================== EJEMPLOS =================== */
.curiosmaze-create-eval-wrapper .cm-samples-container {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.curiosmaze-create-eval-wrapper .cm-sample-card {
  border: 1px solid var(--color-border);
  border-radius: var(--border-radius-sm);
  overflow: hidden;
  margin-bottom: 1rem;
  box-shadow: var(--shadow-sm);
  background-color: var(--color-bg-element-alt);
}

.curiosmaze-create-eval-wrapper .cm-sample-card-header {
  padding: 0.9rem 1.25rem;
  background-color: var(--color-bg-element);
  border-bottom: 1px solid var(--color-border);
}

.curiosmaze-create-eval-wrapper .cm-sample-card-title {
  margin: 0;
  font-size: 1rem;
  font-weight: 600;
  color: var(--color-text-primary);
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.curiosmaze-create-eval-wrapper .cm-sample-icon {
  color: var(--color-primary);
  font-size: 1.1rem;
}

.curiosmaze-create-eval-wrapper .cm-sample-card-content {
  padding: 1.25rem;
  display: flex;
  flex-direction: column;
  gap: 1.25rem;
  background-color: var(--color-bg-main);
}

.curiosmaze-create-eval-wrapper .cm-sample-label {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  font-size: 0.95rem;
  font-weight: 500;
  color: var(--color-text-secondary);
  margin-bottom: 0.5rem;
}

.curiosmaze-create-eval-wrapper .cm-sample-label-icon {
  font-size: 1.1rem;
  color: var(--color-primary);
}

.curiosmaze-create-eval-wrapper .cm-code-box,
.curiosmaze-create-eval-wrapper .cm-code-preview {
  background-color: var(--color-bg-element-alt);
  padding: 1rem;
  border-radius: var(--border-radius-sm);
  font-family: monospace;
  white-space: pre-wrap;
  font-size: 0.95rem;
  color: var(--color-text-primary);
  overflow-x: auto;
  border: 1px solid var(--color-border);
  line-height: 1.5;
}

.curiosmaze-create-eval-wrapper .cm-code-preview pre {
  margin: 0;
  font-family: monospace;
}

/* =================== OPCIONES ADICIONALES =================== */
.curiosmaze-create-eval-wrapper .cm-options-section {
  margin: 3rem 0;
  padding: 1.5rem 0;
  border-top: 1px solid var(--color-border);
  border-bottom: 1px solid var(--color-border);
}

.curiosmaze-create-eval-wrapper .cm-options-container {
  background-color: var(--color-bg-element);
  border-radius: var(--border-radius);
  padding: 1.75rem;
  height: 100%;
  border-left: 4px solid var(--color-primary);
  box-shadow: var(--shadow-sm);
}

.curiosmaze-create-eval-wrapper .cm-options-header {
  display: flex;
  align-items: center;
  margin-bottom: 1.5rem;
}

.curiosmaze-create-eval-wrapper .cm-options-icon {
  font-size: 1.5rem;
  margin-right: 0.75rem;
  color: var(--color-primary);
}

.curiosmaze-create-eval-wrapper .cm-options-content {
  padding-left: 0.5rem;
}

.curiosmaze-create-eval-wrapper .cm-option-item {
  margin-bottom: 1.25rem;
  display: flex;
  flex-direction: column;
}

.curiosmaze-create-eval-wrapper .cm-option-item:last-child {
  margin-bottom: 0;
}

.curiosmaze-create-eval-wrapper .cm-option-item .cm-checkbox {
  display: flex;
  align-items: center;
  cursor: pointer;
  user-select: none;
}

.curiosmaze-create-eval-wrapper .cm-option-item input[type="checkbox"] {
  margin-right: 0.75rem;
  transform: scale(1.2);
}

.curiosmaze-create-eval-wrapper .cm-option-label {
  font-weight: 500;
  color: var(--color-text-primary);
  margin-left: 0.5rem;
}

.curiosmaze-create-eval-wrapper .cm-option-description {
  color: var(--color-text-muted);
  font-size: 0.85rem;
  margin-top: 0.25rem;
  margin-left: 2rem;
}

/* =================== PUNTAJE =================== */
.curiosmaze-create-eval-wrapper .cm-puntaje-box {
  background-color: var(--color-bg-element);
  border-radius: var(--border-radius);
  padding: 1.75rem;
  height: 100%;
  box-shadow: var(--shadow-sm);
  border-top: 4px solid var(--color-primary);
}

.curiosmaze-create-eval-wrapper .cm-puntaje-header {
  display: flex;
  align-items: center;
  margin-bottom: 1.25rem;
}

.curiosmaze-create-eval-wrapper .cm-puntaje-icon {
  font-size: 1.5rem;
  margin-right: 0.75rem;
  color: var(--color-primary);
}

.curiosmaze-create-eval-wrapper .cm-puntaje-content {
  text-align: center;
}

.curiosmaze-create-eval-wrapper .cm-puntaje-display {
  display: flex;
  align-items: baseline;
  justify-content: center;
  margin-bottom: 1rem;
}

.curiosmaze-create-eval-wrapper .cm-puntaje-value {
  font-size: 2.5rem;
  font-weight: 700;
  color: var(--color-primary);
  line-height: 1;
}

.curiosmaze-create-eval-wrapper .cm-puntaje-unit {
  font-size: 1.1rem;
  color: var(--color-text-secondary);
  margin-left: 0.5rem;
}

.curiosmaze-create-eval-wrapper .cm-puntaje-progress {
  margin-bottom: 1rem;
}

.curiosmaze-create-eval-wrapper .cm-puntaje-progress .cm-progress {
  height: 0.75rem;
  border-radius: 0.5rem;
  width: 100%;
  overflow: hidden;
  -webkit-appearance: none;
  appearance: none;
  background-color: var(--color-bg-main);
  border: none;
}

.curiosmaze-create-eval-wrapper .cm-puntaje-progress .cm-progress::-webkit-progress-bar {
  background-color: var(--color-bg-main);
}

.curiosmaze-create-eval-wrapper .cm-puntaje-progress .cm-progress::-webkit-progress-value {
  background-color: var(--color-primary);
}

.curiosmaze-create-eval-wrapper .cm-puntaje-progress .cm-progress::-moz-progress-bar {
  background-color: var(--color-primary);
}

.curiosmaze-create-eval-wrapper .cm-puntaje-info {
  color: var(--color-text-muted);
  font-size: 0.9rem;
  line-height: 1.5;
}

/* =================== ACCIONES DE FORMULARIO =================== */
.curiosmaze-create-eval-wrapper .cm-form-actions {
  margin-top: 2.5rem;
  padding-top: 1.5rem;
  border-top: 1px solid var(--color-border);
}

.curiosmaze-create-eval-wrapper .cm-form-help-text {
  margin-top: 1rem;
  color: var(--color-text-muted);
  font-size: 0.9rem;
  text-align: center;
}

.curiosmaze-create-eval-wrapper .cm-field.cm-is-grouped {
  display: flex;
  justify-content: flex-start;
  gap: 0.75rem;
}

.curiosmaze-create-eval-wrapper .cm-field.cm-is-grouped.cm-is-grouped-right {
  justify-content: flex-end;
}

/* =================== NOTIFICACIONES =================== */
.curiosmaze-create-eval-wrapper .cm-success-notification {
  position: fixed;
  top: 20px;
  right: 20px;
  background-color: var(--color-bg-element);
  border-left: 4px solid var(--color-teal);
  color: var(--color-text-primary);
  padding: 1.5rem;
  border-radius: var(--border-radius);
  box-shadow: var(--shadow-lg);
  z-index: 1000;
  width: 350px;
  animation: cmSlideIn var(--transition-smooth) ease-out;
}

.curiosmaze-create-eval-wrapper .cm-success-notification-header {
  display: flex;
  align-items: center;
  margin-bottom: 1rem;
}

.curiosmaze-create-eval-wrapper .cm-success-notification-icon {
  background-color: var(--color-teal);
  color: var(--color-bg-main);
  width: 24px;
  height: 24px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1rem;
  margin-right: 0.75rem;
}

.curiosmaze-create-eval-wrapper .cm-success-notification-title {
  font-weight: 600;
  font-size: 1.25rem;
  color: var(--color-text-primary);
}

.curiosmaze-create-eval-wrapper .cm-success-notification-content {
  margin-bottom: 1rem;
  font-size: 1.05rem;
  color: var(--color-text-secondary);
  line-height: 1.5;
}

.curiosmaze-create-eval-wrapper .cm-success-notification-code {
  background-color: var(--color-bg-main);
  padding: 1rem;
  text-align: center;
  font-size: 1.5rem;
  font-weight: 700;
  color: var(--color-primary);
  border-radius: var(--border-radius-sm);
  letter-spacing: 2px;
  margin-bottom: 0.5rem;
  border: 1px dashed var(--color-border);
}

.curiosmaze-create-eval-wrapper .cm-success-notification-close {
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

.curiosmaze-create-eval-wrapper .cm-success-notification-close:hover {
  color: var(--color-text-primary);
}

.curiosmaze-create-eval-wrapper .cm-error-notification {
  position: fixed;
  top: 20px;
  right: 20px;
  background-color: var(--color-bg-element);
  border-left: 4px solid var(--color-error);
  color: var(--color-text-primary);
  padding: 1.5rem;
  border-radius: var(--border-radius);
  box-shadow: var(--shadow-lg);
  z-index: 1000;
  width: 350px;
  animation: cmSlideIn var(--transition-smooth) ease-out;
}

.curiosmaze-create-eval-wrapper .cm-error-notification-header {
  display: flex;
  align-items: center;
  margin-bottom: 1rem;
}

.curiosmaze-create-eval-wrapper .cm-error-notification-icon {
  background-color: var(--color-error);
  color: var(--color-bg-main);
  width: 24px;
  height: 24px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1rem;
  margin-right: 0.75rem;
}

.curiosmaze-create-eval-wrapper .cm-error-notification-title {
  font-weight: 600;
  font-size: 1.25rem;
  color: var(--color-text-primary);
}

.curiosmaze-create-eval-wrapper .cm-error-notification-content {
  margin-bottom: 0.75rem;
  font-size: 1.05rem;
  color: var(--color-text-secondary);
  line-height: 1.5;
}

.curiosmaze-create-eval-wrapper .cm-error-notification-list {
  background-color: var(--color-bg-main);
  padding: 1rem 1rem 1rem 2rem;
  border-radius: var(--border-radius-sm);
  border: 1px solid var(--color-error-bg);
}

.curiosmaze-create-eval-wrapper .cm-error-notification-list li {
  color: var(--color-error);
  margin-bottom: 0.5rem;
  font-size: 0.95rem;
}

.curiosmaze-create-eval-wrapper .cm-error-notification-list li:last-child {
  margin-bottom: 0;
}

.curiosmaze-create-eval-wrapper .cm-error-notification-close {
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

.curiosmaze-create-eval-wrapper .cm-error-notification-close:hover {
  color: var(--color-text-primary);
}

/* =================== CLASES DE UTILIDAD =================== */
.curiosmaze-create-eval-wrapper .cm-mb-4 {
  margin-bottom: 1rem;
}

.curiosmaze-create-eval-wrapper .cm-mt-3 {
  margin-top: 0.75rem;
}

.curiosmaze-create-eval-wrapper .cm-has-text-centered {
  text-align: center;
}

.curiosmaze-create-eval-wrapper .cm-has-text-weight-semibold {
  font-weight: 600;
}

.curiosmaze-create-eval-wrapper .cm-has-text-weight-medium {
  font-weight: 500;
}

.curiosmaze-create-eval-wrapper .cm-is-size-5 {
  font-size: 1.25rem;
}

/* =================== ANIMACIONES =================== */
@keyframes cmSlideIn {
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
@media screen and (max-width: 768px) {
  .curiosmaze-create-eval-wrapper .cm-ejercicios-cards {
    grid-template-columns: 1fr;
  }

  .curiosmaze-create-eval-wrapper .cm-ejercicios-controls {
    flex-direction: column;
    align-items: stretch;
    gap: 0.75rem;
  }

  .curiosmaze-create-eval-wrapper .cm-filter-bar {
    width: 100%;
    flex-direction: column;
    gap: 0.5rem;
  }

  .curiosmaze-create-eval-wrapper .cm-general-info {
    grid-template-columns: 1fr;
  }

  .curiosmaze-create-eval-wrapper .cm-header-content {
    flex-direction: column;
    text-align: center;
  }

  .curiosmaze-create-eval-wrapper .cm-header-text {
    margin-bottom: 1.5rem;
  }

  .curiosmaze-create-eval-wrapper .cm-header-text .cm-subtitle {
    max-width: 100%;
  }

  .curiosmaze-create-eval-wrapper .cm-icon-container {
    margin: 0 auto;
  }

  .curiosmaze-create-eval-wrapper .cm-options-section .cm-columns {
    flex-direction: column;
  }

  .curiosmaze-create-eval-wrapper .cm-options-section .cm-column.cm-is-4 {
    margin-top: 1.5rem;
    max-width: 100%;
  }

  .curiosmaze-create-eval-wrapper .cm-puntaje-box {
    max-width: 100%;
  }

  .curiosmaze-create-eval-wrapper .cm-difficulty-filter,
  .curiosmaze-create-eval-wrapper .cm-clean-filter {
    width: 100%;
  }

  .curiosmaze-create-eval-wrapper .cm-column {
    flex: 0 0 100%;
    max-width: 100%;
  }
}

@media screen and (max-width: 640px) {
  .curiosmaze-create-eval-wrapper {
    padding: 1rem 0.5rem;
  }

  .curiosmaze-create-eval-wrapper .cm-form-container {
    padding: 1.5rem 1rem;
  }

  .curiosmaze-create-eval-wrapper .cm-options-container,
  .curiosmaze-create-eval-wrapper .cm-puntaje-box {
    padding: 1.25rem;
  }

  .curiosmaze-create-eval-wrapper .cm-form-actions .cm-button {
    width: 100%;
    margin-bottom: 0.5rem;
  }

  .curiosmaze-create-eval-wrapper .cm-form-actions .cm-field.cm-is-grouped {
    display: block;
  }

  .curiosmaze-create-eval-wrapper .cm-form-actions .cm-control {
    width: 100%;
    margin-right: 0 !important;
  }
}


/* =================== TAGS MEJORADOS =================== */
.curiosmaze-create-eval-wrapper .cm-tag {
  padding: 0.4em 0.9em;
  border-radius: var(--border-radius);
  font-size: 0.85rem;
  font-weight: 600;
  display: flex;
  align-items: center;
  gap: 0.4em;
  border: 2px solid transparent;
  box-shadow: var(--shadow-sm);
  transition: all var(--transition-fast);
}

.curiosmaze-create-eval-wrapper .cm-tag.cm-is-medium {
  font-size: 0.9rem;
  padding: 0.5em 1em;
}

.curiosmaze-create-eval-wrapper .cm-tag.cm-is-success {
  background-color: var(--color-success-bg);
  color: var(--color-success);
  border-color: var(--color-success);
}

.curiosmaze-create-eval-wrapper .cm-tag.cm-is-primary {
  background-color: rgba(235, 179, 0, 0.15);
  color: var(--color-primary);
  border-color: var(--color-primary);
}

.curiosmaze-create-eval-wrapper .cm-tag.cm-is-danger {
  background-color: var(--color-error-bg);
  color: var(--color-error);
  border-color: var(--color-error);
}

.curiosmaze-create-eval-wrapper .cm-tag.cm-is-info {
  background-color: var(--color-info-bg);
  color: var(--color-info);
  border-color: var(--color-info);
}

.curiosmaze-create-eval-wrapper .cm-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 0.75rem;
  align-items: center;
}

/* =================== BOTÓN CERRAR MODAL CORREGIDO =================== */
.curiosmaze-create-eval-wrapper .cm-delete {
  background-color: rgba(0, 0, 0, 0.2);
  border: none;
  border-radius: 50%;
  cursor: pointer;
  display: inline-block;
  height: 24px;
  position: absolute;
  top: 1rem;
  right: 1rem;
  vertical-align: top;
  width: 24px;
  transition: all var(--transition-fast);
}

.curiosmaze-create-eval-wrapper .cm-delete:hover {
  background-color: rgba(255, 255, 255, 0.2);
  transform: scale(1.1);
}

.curiosmaze-create-eval-wrapper .cm-delete::before,
.curiosmaze-create-eval-wrapper .cm-delete::after {
  background-color: var(--color-text-primary);
  content: "";
  display: block;
  left: 50%;
  position: absolute;
  top: 50%;
  transform: translateX(-50%) translateY(-50%) rotate(45deg);
  transform-origin: center center;
}

.curiosmaze-create-eval-wrapper .cm-delete::before {
  height: 2px;
  width: 60%;
}

.curiosmaze-create-eval-wrapper .cm-delete::after {
  height: 60%;
  width: 2px;
}
</style>