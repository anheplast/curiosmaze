<!-- components/ManageEvaluations.vue -->
<template>
  <div class="manage-evaluations-wrapper">
    <div class="box form-container">
      <!-- Cabecera con título y botón de crear -->
      <div class="header-section">
        <div class="header-content">
          <h1 class="title is-3">Evaluaciones</h1>
          <p class="subtitle is-6">Administre sus evaluaciones y monitoree a los estudiantes.</p>
        </div>
        <div class="header-actions">
          <button class="button is-primary create-btn" @click="$router.push('/docente/dashboard/crear-evaluacion')">
            <span class="icon-plus">+</span>
            <span>Nueva Evaluación</span>
          </button>
        </div>
      </div>

      <!-- Filtros -->
      <div class="filters-section">
        <div class="filters-container" style="padding-top: 10px;">
          <div class="field has-addons search-container">
            <div class="control has-icons-left is-expanded">
              <input class="input" type="text" v-model="filtro" placeholder="Buscar evaluaciones..."
                @input="filtrarEvaluaciones" />
              <span class="icon is-small is-left">
                <i class="fas fa-search"></i>
              </span>
            </div>
          </div>

          <div class="filter-select-container">
            <div class="select is-fullwidth">
              <select v-model="filtroEstado" @change="filtrarEvaluaciones">
                <option value="todos">Todos los estados</option>
                <option value="activa">Activas</option>
                <option value="pendiente">Pendientes</option>
                <option value="finalizada">Finalizadas</option>
              </select>
            </div>
          </div>
        </div>
      </div>

      <!-- Estado de carga -->
      <div class="loading-container" v-if="cargando">
        <div class="loader"></div>
        <p>Cargando evaluaciones...</p>
      </div>

      <!-- Estado vacío -->
      <div class="empty-container" v-else-if="evaluacionesFiltradas.length === 0">
        <div class="empty-state">
          <div class="empty-icon">📋</div>
          <h2 class="title is-4">No hay evaluaciones</h2>
          <p v-if="filtro || filtroEstado !== 'todos'">
            No se encontraron evaluaciones con los filtros actuales.
            <a href="#" @click.prevent="limpiarFiltros">Limpiar filtros</a>
          </p>
          <p v-else>
            Aún no ha creado ninguna evaluación.
            <a href="#" @click.prevent="$router.push('/docente/dashboard/crear-evaluacion')">Crear nueva evaluación</a>
          </p>
        </div>
      </div>

      <!-- Tarjetas de evaluación -->
      <div class="evaluaciones-grid" v-else>
        <div v-for="evaluacion in evaluacionesFiltradas" :key="evaluacion.id" class="card evaluacion-card">
          <div class="card-header" :class="{ 
          'is-active': evaluacion.estado === 'activa',
          'is-pending': evaluacion.estado === 'pendiente',
          'is-finished': evaluacion.estado === 'finalizada'
        }">
            <div class="card-header-title">
              <span class="card-header-icon-left">
                <span v-if="evaluacion.estado === 'activa'">▶️</span>
                <span v-else-if="evaluacion.estado === 'pendiente'">⏱️</span>
                <span v-else-if="evaluacion.estado === 'finalizada'">✅</span>
              </span>
              <span class="estado-badge" :class="evaluacion.estado">{{ evaluacion.estado }}</span>
            </div>
            <div class="card-header-icon">
              <div class="card-action-btn-container">
                <button class="card-action-btn edit-btn" @click.stop="mostrarModalEditar(evaluacion)" title="Editar">
                  <span>✏️</span>
                </button>
              </div>
              <div class="card-action-btn-container">
                <button class="card-action-btn delete-btn" @click.stop="confirmarEliminar(evaluacion)" title="Eliminar">
                  <span>🗑️</span>
                </button>
              </div>
            </div>
          </div>

          <div class="card-content">
            <h2 class="title is-4 card-title">
              <span class="card-title-icon">📝</span>
              {{ evaluacion.titulo }}
            </h2>
            <p class="card-description">{{ evaluacion.descripcion || 'Sin descripción' }}</p>

            <div class="info-items">
              <div class="info-item">
                <span class="info-icon">📚</span>
                <span>{{ getCursoNombre(evaluacion.curso) }}</span>
              </div>
              <div class="info-item">
                <span class="info-icon">⏱️</span>
                <span>{{ evaluacion.duracion_minutos }} minutos</span>
              </div>
              <div class="info-item">
                <span class="info-icon">🕒</span>
                <span>Inicia: {{ formatDate(evaluacion.fecha_inicio) }}</span>
              </div>
              <!-- Fecha de finalización -->
              <div class="info-item">
                <span class="info-icon">🏁</span>
                <span>Finaliza: {{ getEndDate(evaluacion) }}</span>
              </div>
            </div>

            <div class="code-section">
              <div class="code-label">
                <span class="code-icon">🔑</span>
                Código de acceso:
              </div>
              <div class="code-display">
                <span class="code-value">{{ evaluacion.codigo_acceso }}</span>
                <button class="code-copy" @click.prevent.stop="copiarCodigo(evaluacion.codigo_acceso)">
                  <span>📋</span>
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Modal para Editar Evaluación -->
      <div class="modal" :class="{'is-active': modalEditarVisible}">
        <div class="modal-background" @click="cerrarModalEditar"></div>
        <div class="modal-card">
          <header class="modal-card-head">
            <p class="modal-card-title">
              <span class="modal-title-icon">✏️</span>
              Editar Evaluación
            </p>
            <button class="delete" aria-label="close" @click="cerrarModalEditar"></button>
          </header>

          <section class="modal-card-body">
            <div v-if="evaluacionEditando">
              <div class="field">
                <label class="label">Título</label>
                <div class="control">
                  <input class="input" type="text" v-model="evaluacionEditando.titulo" required>
                </div>
              </div>

              <div class="field">
                <label class="label">Descripción</label>
                <div class="control">
                  <textarea class="textarea" v-model="evaluacionEditando.descripcion"></textarea>
                </div>
              </div>

              <div class="columns">
                <div class="column">
                  <div class="field">
                    <label class="label">Curso</label>
                    <div class="control">
                      <div class="select is-fullwidth">
                        <select v-model="evaluacionEditando.curso" required>
                          <option value="" disabled selected>Seleccionar curso</option>
                          <option value="8">8vo de Básica</option>
                          <option value="9">9no de Básica</option>
                          <option value="10">10mo de Básica</option>
                          <option value="1">1ro de Bachillerato</option>
                          <option value="2">2do de Bachillerato</option>
                          <option value="3">3ro de Bachillerato</option>
                        </select>
                      </div>
                    </div>
                  </div>
                </div>

                <div class="column">
                  <div class="field">
                    <label class="label">Duración (minutos)</label>
                    <div class="control">
                      <input class="input" type="number" v-model.number="evaluacionEditando.duracion_minutos" min="1">
                    </div>
                  </div>
                </div>
              </div>

              <div class="field">
                <label class="label">Fecha y hora de inicio</label>
                <div class="columns">
                  <div class="column">
                    <div class="control">
                      <input class="input" type="date" v-model="fechaEdicion">
                    </div>
                  </div>
                  <div class="column">
                    <div class="control">
                      <input class="input" type="time" v-model="horaEdicion">
                    </div>
                  </div>
                </div>
              </div>

              <div class="field">
                <div class="control">
                  <label class="checkbox">
                    <input type="checkbox" v-model="evaluacionEditando.permitir_revision">
                    Permitir revisión de respuestas
                  </label>
                </div>
              </div>

              <div class="field">
                <div class="control">
                  <label class="checkbox">
                    <input type="checkbox" v-model="evaluacionEditando.mostrar_resultado">
                    Mostrar resultado al finalizar
                  </label>
                </div>
              </div>

              <div class="field">
                <div class="control">
                  <label class="checkbox">
                    <input type="checkbox" v-model="evaluacionEditando.orden_aleatorio">
                    Orden aleatorio de ejercicios
                  </label>
                </div>
              </div>
            </div>
          </section>

          <footer class="modal-card-foot">
            <div class="modal-buttons-container">
              <button class="button modal-close-btn" @click="cerrarModalEditar">Cancelar</button>
              <button class="button is-primary modal-save-btn" @click="guardarEdicion">Guardar Cambios</button>
            </div>
          </footer>
        </div>
      </div>

      <!-- Modal de Confirmación para Eliminar -->
      <div class="modal" :class="{'is-active': modalEliminarVisible}">
        <div class="modal-background" @click="cancelarEliminar"></div>
        <div class="modal-card delete-modal">
          <header class="modal-card-head">
            <p class="modal-card-title">
              <span class="modal-title-icon">🗑️</span>
              Confirmar Eliminación
            </p>
            <button class="delete" aria-label="close" @click="cancelarEliminar"></button>
          </header>

          <section class="modal-card-body">
            <div class="delete-warning">
              <div class="delete-warning-icon">⚠️</div>
              <p class="delete-message">
                ¿Está seguro que desea eliminar la evaluación
                <strong>{{ evaluacionEliminar?.titulo }}</strong>?
              </p>
              <p class="delete-note">
                Esta acción no se puede deshacer.
              </p>
            </div>
          </section>

          <footer class="modal-card-foot">
            <div class="modal-buttons-container">
              <button class="button modal-close-btn" @click="cancelarEliminar">Cancelar</button>
              <button class="button is-danger modal-delete-btn" @click="eliminarEvaluacion">
                <span class="delete-icon">🗑️</span>
                <span>Sí, eliminar</span>
              </button>
            </div>
          </footer>
        </div>
      </div>

    </div> <!-- Cierre del box form-container -->

    <!-- Notificación de éxito al eliminar -->
    <transition name="fade">
      <div v-if="mostrarNotificacion" class="custom-notification" :class="notificacionTipo">
        <button class="notification-close" @click="cerrarNotificacion">×</button>
        <div class="notification-header">
          <span class="notification-icon">{{ notificacionIcono }}</span>
          <span class="notification-title">{{ notificacionTitulo }}</span>
        </div>
        <div class="notification-content">
          {{ notificacionMensaje }}
        </div>
      </div>
    </transition>
  </div> <!-- Cierre del manage-evaluations-wrapper -->
</template>

<script>
import { ref, computed, onMounted, onBeforeUnmount, watch } from 'vue';
import { useRouter } from 'vue-router';
import evaluationsService from '@/api/evaluationsService';
import { useStore } from 'vuex';

export default {
  name: 'ManageEvaluations',
  setup() {
    const store = useStore();
    const router = useRouter();
    let estadosInterval = null;

    // Estados
    const evaluaciones = ref([]);
    const cargando = ref(true);
    const cursos = ref([]);

    // Filtros
    const filtro = ref('');
    const filtroEstado = ref('todos');

    // Modal estados
    const modalEliminarVisible = ref(false);
    const modalEditarVisible = ref(false);
    const evaluacionEliminar = ref(null);
    const evaluacionEditando = ref(null);
    const fechaEdicion = ref('');
    const horaEdicion = ref('');

    // Notificación
    const mostrarNotificacion = ref(false);
    const notificacionTitulo = ref('');
    const notificacionMensaje = ref('');
    const notificacionTipo = ref('is-success');
    const notificacionIcono = ref('✅');

    // Función para cargar evaluaciones
    const cargarEvaluaciones = async () => {
      cargando.value = true;
      try {
        console.log('Solicitando evaluaciones al servidor...');
        const responseEval = await evaluationsService.getEvaluaciones();
        if (responseEval.data) {
          console.log('Evaluaciones recibidas:', responseEval.data);
          // Verificar si data es un array 
          if (Array.isArray(responseEval.data)) {
            evaluaciones.value = responseEval.data;
          } else {
            console.warn('La respuesta no es un array:', responseEval.data);
            evaluaciones.value = [];
          }

          // Si el array está vacío, verificar si hay una evaluación guardada en localStorage
          if (evaluaciones.value.length === 0) {
            const lastCreatedEval = localStorage.getItem('_lastCreatedEvaluation');
            if (lastCreatedEval) {
              try {
                const evalData = JSON.parse(lastCreatedEval);
                evaluaciones.value = [evalData]; // Añadir la evaluación guardada
                console.log('Añadida evaluación desde localStorage:', evalData);
              } catch (e) {
                console.error('Error al parsear evaluación guardada:', e);
              }
            }
          } else {
            // Si hay evaluaciones, eliminar la guardada en localStorage
            localStorage.removeItem('_lastCreatedEvaluation');
          }

          // Asignar estado anterior para tracking de cambios
          evaluaciones.value.forEach(evaluacion => {
            evaluacion.estadoAnterior = evaluacion.estado;
          });

          // Si acabamos de crear una evaluación, actualizamos estados inmediatamente
          actualizarEstadosEvaluaciones();
        } else {
          console.warn('No se recibieron datos de evaluaciones');
          evaluaciones.value = [];
        }
      } catch (error) {
        console.error('Error al cargar evaluaciones:', error.response || error);
        // No mostrar alerta si estamos recargando automáticamente
        if (!window._isAutoReload) {
          mostrarNotificacionPersonalizada('Error', 'No se pudieron cargar las evaluaciones. Intente nuevamente.', 'is-danger', '❌');
        }
        evaluaciones.value = [];
      } finally {
        cargando.value = false;
        window._isAutoReload = false;
      }
    };

    // Función para cargar cursos
    const cargarCursos = async () => {
      try {
        // Obtener cursos desde la API
        const responseCursos = await evaluationsService.getCursos();
        if (responseCursos.data && responseCursos.data.length > 0) {
          cursos.value = responseCursos.data;
        } else {
          // Si no hay cursos en la API, usar datos estáticos
          cursos.value = [
            { id: '1', nombre: '1ro de Bachillerato' },
            { id: '2', nombre: '2do de Bachillerato' },
            { id: '3', nombre: '3ro de Bachillerato' },
            { id: '8', nombre: '8vo de Básica' },
            { id: '9', nombre: '9no de Básica' },
            { id: '10', nombre: '10mo de Básica' }
          ];
        }
      } catch (error) {
        console.error('Error al cargar cursos:', error);
        // Datos estáticos como fallback
        cursos.value = [
          { id: '1', nombre: '1ro de Bachillerato' },
          { id: '2', nombre: '2do de Bachillerato' },
          { id: '3', nombre: '3ro de Bachillerato' },
          { id: '8', nombre: '8vo de Básica' },
          { id: '9', nombre: '9no de Básica' },
          { id: '10', nombre: '10mo de Básica' }
        ];
      }
    };

    // Método para actualizar estados basados en la fecha actual
    const actualizarEstadosEvaluaciones = () => {
      const ahora = new Date();

      evaluaciones.value.forEach(evaluacion => {
        // Guardar estado anterior si no existe
        if (!evaluacion.estadoAnterior) {
          evaluacion.estadoAnterior = evaluacion.estado;
        }

        const fechaInicio = new Date(evaluacion.fecha_inicio);
        const fechaFin = new Date(fechaInicio);
        fechaFin.setMinutes(fechaFin.getMinutes() + evaluacion.duracion_minutos);

        let nuevoEstado = evaluacion.estado;

        if (fechaInicio > ahora) {
          nuevoEstado = 'pendiente';
        } else if (fechaFin < ahora) {
          nuevoEstado = 'finalizada';
        } else {
          nuevoEstado = 'activa';
        }

        // Solo actualizar si el estado cambió
        if (nuevoEstado !== evaluacion.estado) {
          console.log(`Cambio de estado para evaluación ${evaluacion.id}: ${evaluacion.estado} -> ${nuevoEstado}`);
          evaluacion.estado = nuevoEstado;
        }
      });
    };

    // Función para actualizar estados en el servidor
    const actualizarEstadosEnServidor = async () => {
      try {
        // Filtrar solo las evaluaciones que necesitan actualización de estado
        const evaluacionesActualizadas = evaluaciones.value.filter(evaluacion =>
          evaluacion.estadoAnterior && evaluacion.estadoAnterior !== evaluacion.estado
        );

        if (evaluacionesActualizadas.length > 0) {
          console.log('Actualizando estados de evaluaciones en servidor:', evaluacionesActualizadas.length);

          // Actualizar cada evaluación que cambió de estado
          for (const evaluacion of evaluacionesActualizadas) {
            console.log(`Actualizando evaluación ${evaluacion.id}: ${evaluacion.estadoAnterior} -> ${evaluacion.estado}`);

            await evaluationsService.actualizarEvaluacion(evaluacion.id, {
              estado: evaluacion.estado
            });

            // Actualizar estadoAnterior después de guardar en el servidor
            evaluacion.estadoAnterior = evaluacion.estado;
          }
        }
      } catch (error) {
        console.error('Error al actualizar estados en servidor:', error);
      }
    };

    // Función para mostrar notificaciones personalizadas
    const mostrarNotificacionPersonalizada = (titulo, mensaje, tipo = 'is-success', icono = '✅') => {
      notificacionTitulo.value = titulo;
      notificacionMensaje.value = mensaje;
      notificacionTipo.value = tipo;
      notificacionIcono.value = icono;
      mostrarNotificacion.value = true;
      
      // Ocultar la notificación después de 4 segundos
      setTimeout(() => {
        mostrarNotificacion.value = false;
      }, 4000);
    };

    const cerrarNotificacion = () => {
      mostrarNotificacion.value = false;
    };

    onMounted(async () => {
      await cargarEvaluaciones();
      await cargarCursos();

      // Ejecutar una primera actualización de estados
      actualizarEstadosEvaluaciones();

      // Configurar actualizaciones periódicas (cada minuto)
      estadosInterval = setInterval(() => {
        actualizarEstadosEvaluaciones();
        actualizarEstadosEnServidor();
      }, 60000); // Actualizar cada minuto
      
      // Vigilar cambios en la ruta
      window._isAutoReload = false;
      const unwatch = router.afterEach((to) => {
        // Si venimos de crear una evaluación y vamos a la lista de evaluaciones
        if (to.name === 'ManageEvaluations' &&
            (router.currentRoute.value.path.includes('crear-evaluacion') || localStorage.getItem('_reloadEvaluaciones'))) {
          window._isAutoReload = true;
          localStorage.removeItem('_reloadEvaluaciones');
          cargarEvaluaciones();
        }
      });
    });

    onBeforeUnmount(() => {
      // Limpiar los intervalos cuando el componente se desmonta
      if (estadosInterval) {
        clearInterval(estadosInterval);
      }
    });

    // Observador para actualizar estados cuando cambia la lista de evaluaciones
    watch(evaluaciones, () => {
      actualizarEstadosEvaluaciones();
    }, { immediate: true });
    
    // Evaluaciones filtradas
    const evaluacionesFiltradas = computed(() => {
      let resultado = evaluaciones.value;

      // Filtrar por texto
      if (filtro.value) {
        const termino = filtro.value.toLowerCase();
        resultado = resultado.filter(e =>
          e.titulo?.toLowerCase().includes(termino) ||
          e.descripcion?.toLowerCase().includes(termino) ||
          e.codigo_acceso?.toLowerCase().includes(termino)
        );
      }

      // Filtrar por estado
      if (filtroEstado.value !== 'todos') {
        resultado = resultado.filter(e => e.estado === filtroEstado.value);
      }

      // Ordenar primero por estado (activas primero) y luego por fecha (más recientes primero)
      resultado = [...resultado].sort((a, b) => {
        // Primero ordenar por estado - activas siempre primero
        if (a.estado !== b.estado) {
          if (a.estado === 'activa') return -1;
          if (b.estado === 'activa') return 1;
          if (a.estado === 'pendiente') return -1;
          if (b.estado === 'pendiente') return 1;
        }
        
        // Después ordenar por fecha de creación (más recientes primero)
        if (a.fecha_creacion && b.fecha_creacion) {
          return new Date(b.fecha_creacion) - new Date(a.fecha_creacion);
        }
        
        // Si no hay fecha, usar el ID como fallback (asumiendo que ID más alto = más reciente)
        return b.id - a.id;
      });

      return resultado;
    });

    // Acciones
    const limpiarFiltros = () => {
      filtro.value = '';
      filtroEstado.value = 'todos';
    };

    const copiarCodigo = (codigo) => {
      try {
        // Usar el API del portapapeles para copiar el texto
        navigator.clipboard.writeText(codigo)
          .then(() => {
            // Mostrar notificación de éxito
            mostrarNotificacionPersonalizada('Código copiado', 'El código ha sido copiado al portapapeles', 'is-info', '📋');
          })
          .catch(err => {
            console.error('Error al copiar al portapapeles:', err);
            // Intentar método alternativo
            fallbackCopyToClipboard(codigo);
          });
      } catch (error) {
        console.error('Error al acceder al portapapeles:', error);
        // Intentar método alternativo
        fallbackCopyToClipboard(codigo);
      }
    };
    
    // Método alternativo para copiar al portapapeles
    const fallbackCopyToClipboard = (text) => {
      const textArea = document.createElement('textarea');
      textArea.value = text;
      
      // Hacerlo invisible
      textArea.style.position = 'fixed';
      textArea.style.left = '-999999px';
      textArea.style.top = '-999999px';
      document.body.appendChild(textArea);
      
      // Seleccionar y copiar
      textArea.focus();
      textArea.select();
      
      try {
        const successful = document.execCommand('copy');
        document.body.removeChild(textArea);
        
        if (successful) {
          mostrarNotificacionPersonalizada('Código copiado', 'El código ha sido copiado al portapapeles', 'is-info', '📋');
        } else {
          mostrarNotificacionPersonalizada('Error', 'No se pudo copiar el código', 'is-warning', '⚠️');
        }
      } catch (err) {
        document.body.removeChild(textArea);
        mostrarNotificacionPersonalizada('Error', 'No se pudo copiar el código', 'is-warning', '⚠️');
      }
    };

    // Modal reemplazado para editar evaluación (ya no se abre un modal, ahorrar tiempo)
    const mostrarModalEditar = (evaluacion) => {
      // Guardar la evaluación en localStorage para acceder a ella en el componente de creación
      localStorage.setItem('evaluacionEditar', JSON.stringify(evaluacion));
      // Redirigir al componente de edición (no de creación)
      router.push(`/docente/dashboard/editar-evaluacion/${evaluacion.id}`);
    };

    const cerrarModalEditar = () => {
      modalEditarVisible.value = false;
      evaluacionEditando.value = null;
    };

    const guardarEdicion = async () => {
      if (!evaluacionEditando.value) return;
      
      try {
        // Combinar fecha y hora
        if (fechaEdicion.value && horaEdicion.value) {
          evaluacionEditando.value.fecha_inicio = `${fechaEdicion.value}T${horaEdicion.value}:00`;
        }
        
        // Guardar cambios en el servidor
        await evaluationsService.actualizarEvaluacion(evaluacionEditando.value.id, evaluacionEditando.value);
        
        // Actualizar en la lista local
        const index = evaluaciones.value.findIndex(e => e.id === evaluacionEditando.value.id);
        if (index !== -1) {
          evaluaciones.value[index] = { ...evaluaciones.value[index], ...evaluacionEditando.value };
        }
        
        // Mostrar notificación
        mostrarNotificacionPersonalizada('Evaluación actualizada', 'Los cambios se han guardado correctamente', 'is-success', '✅');
        
        // Cerrar modal
        modalEditarVisible.value = false;
        evaluacionEditando.value = null;
        
        // Recargar evaluaciones para reflejar los cambios de estado
        await cargarEvaluaciones();
      } catch (error) {
        console.error('Error al guardar edición:', error);
        mostrarNotificacionPersonalizada('Error', 'No se pudieron guardar los cambios', 'is-danger', '❌');
      }
    };

    // Modal para confirmar eliminación
    const confirmarEliminar = (evaluacion) => {
      evaluacionEliminar.value = evaluacion;
      modalEliminarVisible.value = true;
    };

    const cancelarEliminar = () => {
      modalEliminarVisible.value = false;
      evaluacionEliminar.value = null;
    };

    const eliminarEvaluacion = async () => {
      if (!evaluacionEliminar.value) return;
      
      try {
        await evaluationsService.eliminarEvaluacion(evaluacionEliminar.value.id);
        
        // Eliminar de la lista local
        evaluaciones.value = evaluaciones.value.filter(e => e.id !== evaluacionEliminar.value.id);
        
        // Cerrar modal
        modalEliminarVisible.value = false;
        
        // Mostrar notificación
        mostrarNotificacionPersonalizada(
          'Evaluación eliminada', 
          `La evaluación "${evaluacionEliminar.value.titulo}" ha sido eliminada correctamente`,
          'is-success',
          '✅'
        );
        
        evaluacionEliminar.value = null;
      } catch (error) {
        console.error('Error al eliminar:', error);
        mostrarNotificacionPersonalizada('Error', 'No se pudo eliminar la evaluación', 'is-danger', '❌');
      }
    };

    // Funciones de utilidad
    const formatDate = (dateString) => {
      if (!dateString) return '';

      try {
        const date = new Date(dateString);
        return date.toLocaleDateString('es-ES', {
          day: '2-digit',
          month: '2-digit',
          year: 'numeric',
          hour: '2-digit',
          minute: '2-digit'
        });
      } catch (error) {
        console.error('Error al formatear fecha:', error);
        return dateString;
      }
    };

    // Nueva función para obtener la fecha de finalización
    const getEndDate = (evaluacion) => {
      // Si ya existe fecha_fin, usarla directamente
      if (evaluacion.fecha_fin) {
        return formatDate(evaluacion.fecha_fin);
      }
      
      // Si no hay fecha_fin pero sí fecha_inicio y duración, calcular
      if (evaluacion.fecha_inicio && evaluacion.duracion_minutos) {
        const startDate = new Date(evaluacion.fecha_inicio);
        const endDate = new Date(startDate.getTime());
        endDate.setMinutes(endDate.getMinutes() + evaluacion.duracion_minutos);
        return formatDate(endDate);
      }
      
      return 'No definida';
    };

    const getCursoNombre = (cursoId) => {
      // Mapeo directo de IDs a nombres de curso
      const nombresCursos = {
        5: '8vo de Básica',
        6: '9no de Básica',
        7: '10mo de Básica',
        8: '1ro de Bachillerato',
        9: '2do de Bachillerato',
        10: '3ro de Bachillerato'
      };

      return nombresCursos[cursoId] || 'No asignado';
    };

    const filtrarEvaluaciones = () => {
      // La función existe para manejar eventos aunque la lógica está en el computed
    };

    return {
      evaluaciones,
      cargando,
      cursos,
      filtro,
      filtroEstado,
      evaluacionesFiltradas,
      modalEliminarVisible,
      modalEditarVisible,
      evaluacionEliminar,
      evaluacionEditando,
      fechaEdicion,
      horaEdicion,
      mostrarNotificacion,
      notificacionTitulo,
      notificacionMensaje,
      notificacionTipo,
      notificacionIcono,
      limpiarFiltros,
      copiarCodigo,
      fallbackCopyToClipboard,
      mostrarModalEditar,
      cerrarModalEditar,
      guardarEdicion,
      confirmarEliminar,
      cancelarEliminar,
      eliminarEvaluacion,
      formatDate,
      getEndDate, 
      getCursoNombre,
      filtrarEvaluaciones,
      cargarEvaluaciones,
      actualizarEstadosEvaluaciones,
      cerrarNotificacion
    };
  }
};
</script>

<style>
/* Estilos globales (sin scoped) para anular Bulma */
:root {
  --color-bg-main: #1C1C21;
  --color-bg-element: #2A2A30;
  --color-bg-element-alt: #25252A;
  --color-bg-element-hover: #32323A;
  --color-border: #36363c;
  --color-border-focus: #7E91FF;
  --color-text-primary: #ffffff;
  --color-text-secondary: #e0e0e0;
  --color-text-muted: #9090A0;
  
  /* Nueva paleta con color principal EBB300 */
  --color-primary: #EBB300;
  --color-primary-light: #FFD03F;
  --color-primary-dark: #C89500;
  --color-secondary: #6B7280;
  --color-success: #9DBEB6;
  --color-info: #65B1C1;
  --color-warning: #FFBD2E;
  --color-danger: #FF6B6B;
  
  --border-radius-lg: 12px;
  --border-radius: 8px;
  --border-radius-sm: 6px;
  --shadow-lg: 0 8px 16px rgba(0, 0, 0, 0.2);
  --shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
  --shadow-sm: 0 2px 6px rgba(0, 0, 0, 0.1);
  --transition-fast: 0.2s;
  --transition-smooth: 0.3s;
}

.manage-evaluations-wrapper .button {
  border-radius: var(--border-radius-sm);
  transition: all var(--transition-fast);
  font-weight: 600;
  padding: 0.75rem 1.25rem;
  height: auto;
  display: inline-flex;
  align-items: center;
  justify-content: center;
}

.manage-evaluations-wrapper .button.is-primary {
  background-color: #0078D7 !important;
  color: white !important;
  border: none !important;
}

.manage-evaluations-wrapper .button.is-primary:hover {
  background-color: #0f87e9 !important;
  transform: translateY(-2px);
  box-shadow: var(--shadow-sm);
}

.manage-evaluations-wrapper .modal-card-foot {
  justify-content: center !important;
  background-color: var(--color-bg-element-alt);
  border-top: 1px solid var(--color-border);
  padding: 1.5rem;
}

.modal-buttons-container {
  display: flex;
  justify-content: center;
  width: 100%;
  gap: 1.5rem;
}

.manage-evaluations-wrapper .modal-card-head {
  background-color: var(--color-primary);
  color: white;
  border-bottom: none;
}

.manage-evaluations-wrapper .modal-card-title {
  color: white;
  font-weight: 600;
  display: flex;
  align-items: center;
}

.manage-evaluations-wrapper .modal-card-body {
  background-color: var(--color-bg-element);
  color: var(--color-text-primary);
  padding: 1.5rem;
}

.manage-evaluations-wrapper .input,
.manage-evaluations-wrapper .textarea,
.manage-evaluations-wrapper .select select {
  background-color: var(--color-bg-element-alt);
  border: 1px solid var(--color-border);
  color: var(--color-text-primary);
  border-radius: var(--border-radius-sm);
}

.manage-evaluations-wrapper .input:focus,
.manage-evaluations-wrapper .textarea:focus,
.manage-evaluations-wrapper .select select:focus {
  border-color: var(--color-primary);
  box-shadow: 0 0 0 2px rgba(156, 106, 222, 0.25);
}

.manage-evaluations-wrapper .modal {
  z-index: 100;
}

.manage-evaluations-wrapper .modal-background {
  background-color: rgba(10, 10, 10, 0.7);
}

/* Transiciones */
.fade-enter-active, .fade-leave-active {
  transition: opacity 0.3s, transform 0.3s;
}

.fade-enter-from, .fade-leave-to {
  opacity: 0;
  transform: translateY(-10px);
}
</style>

<style scoped>
/* Diseño general */
.manage-evaluations-wrapper {
  padding: 1.5rem;
  margin-left: 10px; /* Espacio para el sidebar colapsado */
  background-color: var(--color-bg-main);
  color: var(--color-text-primary);
  min-height: 100vh;
}

.form-container {
  background-color: var(--color-bg-main);
  border-radius: var(--border-radius-lg);
  border-top: 4px solid var(--color-primary);
  box-shadow: var(--shadow-lg);
  width: 100%;
  margin: 0 auto;
  padding: 2rem;
}

/* Cabecera */
.header-section {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 2rem;
  flex-wrap: wrap;
  gap: 1rem;
}

.header-content .title {
  color: var(--color-text-primary);
  margin-bottom: 0.5rem;
  font-weight: 600;
}

.header-content .subtitle {
  color: var(--color-text-secondary);
  margin-top: 0;
}

.create-btn {
  background-color: var(--color-primary) !important;
  color: var(--color-bg-main) !important;
  border: none !important;
  font-weight: 600;
  transition: transform 0.2s, box-shadow 0.2s;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
  font-size: 1rem;
  display: inline-flex;
  align-items: center;
  padding: 0.75rem 1.5rem;
}

.icon-plus {
  margin-right: 0.75rem;
  font-size: 1.5rem;
  font-weight: bold;
  line-height: 1;
}

.create-btn:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 8px rgba(235, 179, 0, 0.3);
  background-color: var(--color-primary-light) !important;
}

/* Filtros */
.filters-section {
  background-color: var(--color-bg-element);
  border-radius: var(--border-radius);
  padding: 1.25rem;
  margin-bottom: 2rem;
  display: flex;
  flex-wrap: wrap;
  gap: 1rem;
  align-items: center;
  border-left: 4px solid var(--color-primary);
  box-shadow: var(--shadow-sm);
}

.filters-container {
  display: flex;
  width: 100%;
  /* align-items: center; */
  gap: 1rem;
}

.search-container {
  flex-grow: 2;
  min-width: 200px;
  width: 65%;
}

.search-container .input {
  background-color: var(--color-bg-main);
  border: 1px solid var(--color-border);
  padding-left: 2.5rem;
  height: 2.5rem;
  width: 100%;
}

.search-container .icon.is-small.is-left {
  font-size: 1.25rem;
  color: var(--color-primary);
}

.filter-select-container {
  flex-grow: 1;
  min-width: 200px;
  width: 35%;
}

.filter-select-container .select {
  width: 100%;
}

.filter-select-container select {
  background-color: var(--color-bg-main);
  border: 1px solid var(--color-border);
  height: 2.5rem;
  padding: 0 1rem;
  width: 100%;
  color: var(--color-text-primary);
}

/* Loader */
.loading-container {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 4rem 0;
  color: var(--color-text-secondary);
}

.loader {
  border: 4px solid var(--color-bg-element);
  border-top: 4px solid var(--color-primary);
  border-radius: 50%;
  width: 40px;
  height: 40px;
  animation: spin 1s linear infinite;
  margin-bottom: 1rem;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

/* Estado vacío */
.empty-container {
  display: flex;
  justify-content: center;
  align-items: center;
  padding: 4rem 0;
}

.empty-state {
  text-align: center;
  max-width: 500px;
  padding: 2.5rem;
  background-color: var(--color-bg-element);
  border-radius: var(--border-radius);
  border: 2px dashed var(--color-border);
  box-shadow: var(--shadow-sm);
}

.empty-icon {
  font-size: 3rem;
  margin-bottom: 1.5rem;
  color: var(--color-primary);
  display: inline-block;
}

.empty-state .title {
  color: var(--color-text-primary);
  margin-bottom: 1rem;
}

.empty-state p {
  color: var(--color-text-secondary);
  margin-bottom: 1rem;
}

.empty-state a {
  color: var(--color-primary);
  font-weight: 600;
  text-decoration: underline;
}

/* Grid de tarjetas */
.evaluaciones-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(320px, 1fr));
  gap: 1.5rem;
}

.evaluacion-card {
  border-radius: var(--border-radius);
  overflow: hidden;
  box-shadow: var(--shadow);
  display: flex;
  flex-direction: column;
  background-color: var(--color-bg-element);
  border: 1px solid var(--color-border);
  height: 100%;
  transition: border-color var(--transition-fast), box-shadow var(--transition-fast);
}

.evaluacion-card:hover {
  border-color: var(--color-primary-light);
  box-shadow: var(--shadow-lg);
}

/* Cabecera de tarjeta */
.card-header {
  position: relative;
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0.75rem 1rem;
}

.card-header.is-active {
  background-color: rgba(156, 106, 222, 0.1);
  border-bottom: 3px solid var(--color-primary);
}

.card-header.is-pending {
  background-color: rgba(255, 189, 46, 0.1);
  border-bottom: 3px solid var(--color-warning);
}

.card-header.is-finished {
  background-color: rgba(157, 190, 182, 0.1);
  border-bottom: 3px solid var(--color-success);
}

.card-header-icon-left {
  margin-right: 0.5rem;
  font-size: 1.25rem;
}

.estado-badge {
  font-weight: 600;
  text-transform: capitalize;
  padding: 0.3em 0.8em;
  border-radius: 20px;
  font-size: 0.85rem;
  display: inline-flex;
  align-items: center;
}

.estado-badge.activa {
  background-color: var(--color-primary);
  color: white;
}

.estado-badge.pendiente {
  background-color: var(--color-warning);
  color: var(--color-bg-main);
}

.estado-badge.finalizada {
  background-color: var(--color-success);
  color: var(--color-bg-main);
}

.card-header-icon {
  display: flex;
  gap: 0.3rem;
}

.card-action-btn-container {
  width: 32px;
  height: 32px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: var(--border-radius-sm);
  border: 1px solid var(--color-border);
  background-color: var(--color-bg-element-alt);
  transition: all var(--transition-fast);
  margin: 0 3px;
}

.card-action-btn-container:hover {
  border-color: var(--color-primary);
  background-color: var(--color-bg-element-hover);
  transform: translateY(-2px);
  box-shadow: var(--shadow-sm);
}

.card-action-btn {
  background: none;
  border: none;
  width: 100%;
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  font-size: 1rem;
}

.card-action-btn.edit-btn {
  color: var(--color-text-primary);
}

.card-action-btn.delete-btn {
  color: var(--color-danger);
}

/* Contenido de tarjeta */
.card-content {
  flex-grow: 1;
  padding: 1.5rem;
  overflow-y: auto;
}

.card-title {
  font-size: 1.4rem !important;
  margin-bottom: 1rem !important;
  color: var(--color-text-primary) !important;
  display: flex;
  align-items: center;
}

.card-title-icon {
  margin-right: 0.75rem;
  color: var(--color-primary);
  font-size: 1.25rem;
}

.card-description {
  color: var(--color-text-secondary);
  margin-bottom: 1.25rem;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
  text-overflow: ellipsis;
  line-height: 1.5;
  font-size: 0.95rem;
}

.info-items {
  margin-bottom: 1.25rem;
  background-color: var(--color-bg-element-alt);
  border-radius: var(--border-radius-sm);
  padding: 1rem;
}

.info-item {
  display: flex;
  align-items: center;
  margin-bottom: 0.5rem;
  font-size: 0.95rem;
  color: var(--color-text-secondary);
}

.info-item:last-child {
  margin-bottom: 0;
}

.info-icon {
  margin-right: 0.75rem;
  font-size: 1.1rem;
}

/* Sección código */
.code-section {
  background-color: var(--color-bg-main);
  color: var(--color-text-primary);
  border-radius: var(--border-radius-sm);
  padding: 1rem;
  margin-top: 1rem;
  border: 1px solid var(--color-border);
}

.code-label {
  font-size: 0.85rem;
  color: var(--color-text-secondary);
  margin-bottom: 0.5rem;
  display: flex;
  align-items: center;
}

.code-icon {
  margin-right: 0.5rem;
  font-size: 1rem;
}

.code-display {
  display: flex;
  justify-content: space-between;
  align-items: center;
  background-color: rgba(156, 106, 222, 0.1);
  border-radius: var(--border-radius-sm);
  padding: 0.5rem 0.75rem;
}

.code-value {
  font-family: 'Courier New', monospace;
  font-size: 1.1rem;
  font-weight: 600;
  color: var(--color-primary);
  letter-spacing: 1px;
}

.code-copy {
  background: none;
  border: none;
  color: var(--color-text-secondary);
  cursor: pointer;
  transition: color 0.2s;
  font-size: 1.1rem;
}

.code-copy:hover {
  color: var(--color-primary);
}

/* Modal de Confirmación */
.modal-title-icon {
  margin-right: 0.75rem;
  font-size: 1.25rem;
}

/* Botones del modal */
.modal-close-btn, .modal-save-btn {
  min-width: 140px;
  padding: 0.75rem 1.5rem;
  font-weight: 600;
  border-radius: var(--border-radius-sm);
  margin: 0 10px; /* Añadir margen para separarlos */
}

.modal-close-btn {
  background-color: var(--color-bg-element);
  color: var(--color-text-primary);
  border: 1px solid var(--color-border);
}

.modal-save-btn {
  background-color: var(--color-primary);
  color: var(--color-bg-main);
  border: none;
}

.modal-save-btn:hover {
  background-color: var(--color-primary-dark);
  transform: translateY(-2px);
  box-shadow: var(--shadow-sm);
}

/* Modal eliminar */
.delete-modal .modal-card-head {
  background-color: var(--color-danger);
}

.delete-warning {
  text-align: center;
  padding: 1rem;
}

.delete-warning-icon {
  font-size: 3rem;
  color: var(--color-danger);
  margin-bottom: 1rem;
}

.delete-message {
  font-size: 1.1rem;
  margin-bottom: 1rem;
  color: var(--color-text-primary);
}

.delete-note {
  color: var(--color-danger);
  font-size: 0.9rem;
}

.modal-delete-btn {
  background-color: var(--color-danger) !important;
  display: flex;
  align-items: center;
}

.delete-icon {
  margin-right: 0.5rem;
}

/* Notificación personalizada */
.custom-notification {
  position: fixed;
  top: 20px;
  right: 20px;
  background-color: var(--color-bg-element);
  border-left: 4px solid var(--color-primary);
  color: var(--color-text-primary);
  padding: 1.25rem;
  border-radius: var(--border-radius);
  box-shadow: var(--shadow-lg);
  z-index: 1000;
  width: 320px;
  animation: slideIn 0.3s ease-out;
}

.custom-notification.is-success {
  border-left-color: var(--color-success);
}

.custom-notification.is-danger {
  border-left-color: var(--color-danger);
}

.custom-notification.is-warning {
  border-left-color: var(--color-warning);
}

.custom-notification.is-info {
  border-left-color: var(--color-info);
}

.notification-close {
  position: absolute;
  top: 12px;
  right: 12px;
  background: none;
  border: none;
  color: var(--color-text-secondary);
  cursor: pointer;
  font-size: 1.25rem;
  line-height: 1;
}

.notification-header {
  display: flex;
  align-items: center;
  margin-bottom: 0.75rem;
}

.notification-icon {
  margin-right: 0.5rem;
  font-size: 1.25rem;
}

.notification-title {
  font-weight: 600;
  font-size: 1.1rem;
}

.notification-content {
  font-size: 0.95rem;
  color: var(--color-text-secondary);
  line-height: 1.5;
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

/* Para dispositivos móviles */
@media screen and (max-width: 768px) {
  .manage-evaluations-wrapper {
    margin-left: 0;
    padding: 1rem;
  }
  
  .header-section {
    flex-direction: column;
    align-items: flex-start;
  }
  
  .header-actions {
    width: 100%;
  }
  
  .create-btn {
    width: 100%;
  }
  
  .filters-section {
    flex-direction: column;
  }
  
  .filters-container {
    flex-direction: column;
    gap: 0.75rem;
  }
  
  .search-container, 
  .filter-select-container {
    width: 100%;
    max-width: 100%;
  }
  
  .evaluaciones-grid {
    grid-template-columns: 1fr;
  }
}

body.light-theme .manage-evaluations-wrapper .input::placeholder {
  color: #6b7280;
}

@media (prefers-color-scheme: light) {
  .manage-evaluations-wrapper .input::placeholder {
    color: #6b7280;
  }
}

.manage-evaluations-wrapper .label {
  color: var(--color-text-primary);
}

/* Para tema claro */
@media (prefers-color-scheme: light) {
  .manage-evaluations-wrapper .label {
    color: #d5dae4;
  }
}

/* Si usas clase de tema */
.light-theme .manage-evaluations-wrapper .label {
  color: #374151;
}

@media (prefers-color-scheme: light) {
  .delete-message strong {
    color: #f5f1f1 !important; /* Color oscuro para tema claro */
  }
}

/* Si se usa clase de tema */
.light-theme .delete-message strong {
  color: #fbfbfb !important; /* Color oscuro para tema claro */
}

</style>