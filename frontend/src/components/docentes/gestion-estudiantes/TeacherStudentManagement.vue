<!-- src/components/docentes/gestion-estudiantes/TeacherStudentManagement.vue -->
<template>
  <div class="student-management-wrapper">
    <div class="box form-container">
      <!-- Cabecera con título y descripción -->
      <div class="header-section">
        <div class="header-content">
          <h1 class="title is-3">Gestión de Estudiantes</h1>
          <p class="subtitle is-6">Administre y visualice la información de sus estudiantes.</p>
        </div>
      </div>

      <!-- Filtros y búsqueda -->
      <div class="filters-section">
        <div class="filters-container">
          <div class="field has-addons search-container">
            <div class="control has-icons-left is-expanded">
              <input class="input" type="text" v-model="searchQuery"
                placeholder="Buscar estudiante..." @input="filterStudents" />
              <span class="icon is-small is-left">
                <span>🔍</span>
              </span>
            </div>
          </div>

          <div class="filter-select-container">
            <div class="select is-fullwidth">
              <select v-model="selectedCourse">
                <option value="">Todos los cursos</option>
                <option value="8">8vo de Básica</option>
                <option value="9">9no de Básica</option>
                <option value="10">10mo de Básica</option>
                <option value="1">1ro de Bachillerato</option>
                <option value="2">2do de Bachillerato</option>
                <option value="3">3ro de Bachillerato</option>
              </select>
            </div>
          </div>

          <div class="filter-select-container">
            <div class="select is-fullwidth">
              <select v-model="selectedParallel">
                <option value="">Todos los paralelos</option>
                <option v-for="letra in paralelos" :key="letra" :value="letra">
                  {{ letra }}
                </option>
              </select>
            </div>
          </div>
        </div>
      </div>

      <!-- Estado de carga -->
      <div class="loading-container" v-if="isLoading">
        <div class="loader"></div>
        <p>Cargando estudiantes...</p>
      </div>

      <!-- Estado de error -->
      <div v-else-if="errorState.hasError" class="error-container">
        <div class="error-icon">⚠️</div>
        <h2 class="error-title">{{ errorState.message }}</h2>
        <p class="error-message">{{ errorState.details }}</p>
        <div class="error-actions">
          <button class="button retry-btn" @click="loadStudents">
            <span class="button-icon">🔄</span>
            <span>Reintentar</span>
          </button>
          <button v-if="errorState.isAuthError" class="button auth-btn" @click="refreshToken">
            <span class="button-icon">🔑</span>
            <span>Actualizar autenticación</span>
          </button>
        </div>
      </div>

      <!-- Estado vacío -->
      <div class="empty-container" v-else-if="filteredStudents.length === 0">
        <div class="empty-state">
          <div class="empty-icon">👥</div>
          <h2 class="title is-4">No hay estudiantes</h2>
          <p v-if="searchQuery">
            No se encontraron estudiantes con la búsqueda actual.
            <a href="#" @click.prevent="clearSearch">Limpiar búsqueda</a>
          </p>
          <p v-else>
            No hay estudiantes para este curso y paralelo.
            <a href="#" @click.prevent="suggestAction">¿Qué puedo hacer?</a>
          </p>
        </div>
      </div>

      <!-- Tabla de estudiantes simplificada -->
      <div class="students-table-container" v-else>
        <table class="students-table">
          <thead>
            <tr>
              <th class="student-col">Nombres</th>
              <th class="apellidos-col">Apellidos</th>
              <th class="id-col">Número de identidad</th>
              <th class="curso-col">Curso</th>
              <th class="paralelo-col">Paralelo</th>
              <th class="actions-col">Acciones</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="student in filteredStudents" :key="student.id">
              <td class="student-col">
                <div class="student-info">
                  <span class="student-icon">{{ student.genero === 'femenino' ? '👩‍🎓' : '👨‍🎓' }}</span>
                  <span>{{ student.nombres || 'No registrado' }}</span>
                </div>
              </td>
              <td>{{ student.apellidos || 'No registrado' }}</td>
              <td>
                <span class="icon-text">
                  <span class="icon">🆔</span>
                  <span class="id-text">{{ student.identificacion || 'No registrado' }}</span>
                </span>
              </td>
              <td>
                <span class="icon-text">
                  <span class="icon">📚</span>
                  <span>{{ getCursoNombre(student.curso) }}</span>
                </span>
              </td>
              <td>
                <span class="icon-text">
                  <span class="icon">🏫</span>
                  <span>{{ student.paralelo || '-' }}</span>
                </span>
              </td>
              <td class="actions-col">
                <button class="action-button" @click="viewStudentPerformance(student)">
                  <span class="icon">📈</span>
                  <span>Rendimiento</span>
                </button>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <!-- Modal de rendimiento del estudiante -->
    <div class="modal" :class="{ 'is-active': showStudentModal }">
      <div class="modal-background" @click="showStudentModal = false"></div>
      <div class="modal-card">
        <header class="modal-card-head">
          <p class="modal-card-title">
            <span class="modal-title-icon">📊</span>
            {{ selectedStudent ? `Rendimiento de ${selectedStudent.nombres} ${selectedStudent.apellidos}` : 'Rendimiento del Estudiante' }}
          </p>
          <button class="delete" aria-label="close" @click="showStudentModal = false"></button>
        </header>

        <section class="modal-card-body" v-if="selectedStudent">
          <!-- Información de contacto - simplificada -->
          <div class="student-contact-info">
            <div class="contact-item">
              <span class="contact-icon">📧</span>
              <span class="contact-value">{{ selectedStudent.email || 'No disponible' }}</span>
            </div>
          </div>
          
          <!-- Contenido de Rendimiento -->
          <div class="performance-stats">
            <div class="stat-box">
              <div class="stat-icon">📈</div>
              <div class="stat-value">{{ getStudentAverageGrade(selectedStudent.id) }}</div>
              <div class="stat-label">Promedio general</div>
            </div>

            <div class="stat-box">
              <div class="stat-icon">🎯</div>
              <div class="stat-value">{{ calculateCompletionRate(selectedStudent.id) }}%</div>
              <div class="stat-label">Tasa de finalización</div>
            </div>

            <div class="stat-box">
              <div class="stat-icon">⭐</div>
              <div class="stat-value">{{ calculateBestScore(selectedStudent.id) }}</div>
              <div class="stat-label">Mejor puntuación</div>
            </div>
          </div>

          <h3 class="section-title">Evaluaciones recientes</h3>
          <div class="evaluations-list">
            <div class="no-data" v-if="!getStudentEvaluations(selectedStudent.id).length">
              <p>No hay evaluaciones recientes para mostrar.</p>
            </div>
            <div v-else v-for="(evaluation, index) in getStudentEvaluations(selectedStudent.id)" :key="index"
              class="evaluation-item">
              <div class="evaluation-header">
                <div class="evaluation-name">{{ evaluation.title }}</div>
                <div class="evaluation-score" :class="getScoreClass(evaluation.score)">
                  {{ evaluation.score }}/10
                </div>
              </div>
              <div class="evaluation-date">{{ formatDate(evaluation.date) }}</div>
              <progress class="progress" :value="evaluation.score * 10" max="100"
                :class="getScoreClass(evaluation.score)">
              </progress>
              <div class="evaluation-actions">
                <button class="button details-button" @click="openEvaluationDetails(evaluation)">
                  <span class="icon">🔍</span>
                  <span>Ver detalles</span>
                </button>
              </div>
            </div>
          </div>
        </section>

        <footer class="modal-card-foot">
          <button class="button" @click="showStudentModal = false">Cerrar</button>
        </footer>
      </div>
    </div>

    <!-- Notificación de éxito -->
    <transition name="fade">
      <div v-if="notification.show" class="custom-notification" :class="notification.type">
        <button class="notification-close" @click="closeNotification">×</button>
        <div class="notification-header">
          <span class="notification-icon">{{ notification.icon }}</span>
          <span class="notification-title">{{ notification.title }}</span>
        </div>
        <div class="notification-content">
          {{ notification.message }}
        </div>
      </div>
    </transition>
  </div>
</template>

<script>
import { ref, computed, onMounted, reactive, watch } from 'vue';
import studentsService from '@/api/studentsService';
import authService from '@/api/authService';
import { useStore } from 'vuex';
import { useRouter } from 'vue-router';
import axiosInstance from '@/api/axios';

export default {
  name: 'TeacherStudentManagement',
  setup() {
    const store = useStore();
    const router = useRouter();

    const token = ref('');
    const userId = ref('');
    const userRole = ref('');
    const userName = ref('');

    // Estados generales
    const isLoading = ref(false);
    const students = ref([]);
    const searchQuery = ref('');

    // Estado de error
    const errorState = ref({
      hasError: false,
      message: '',
      details: '',
      isAuthError: false
    });

    // Los paralelos como array simple de letras
    const paralelos = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M'];

    // Valores iniciales y para selectores
    const selectedCourse = ref('');  // Valor por defecto vacío para mostrar todos
    const selectedParallel = ref(''); // Valor por defecto vacío para mostrar todos

    // Estados para modales
    const showStudentModal = ref(false);
    const selectedStudent = ref(null);

    // Notificaciones
    const notification = reactive({
      show: false,
      icon: '✅',
      title: '',
      message: '',
      type: 'is-success',
      timeout: null
    });

    // Estudiantes filtrados con búsqueda mejorada
    const filteredStudents = computed(() => {
      let resultado = students.value;

      // Filtrar por texto
      if (searchQuery.value) {
        const query = searchQuery.value.toLowerCase();
        resultado = resultado.filter(student => {
          return (
            (student.nombres && student.nombres.toLowerCase().includes(query)) ||
            (student.apellidos && student.apellidos.toLowerCase().includes(query)) ||
            (student.identificacion && student.identificacion.toLowerCase().includes(query)) ||
            (student.email && student.email.toLowerCase().includes(query)) ||
            (`${student.nombres || ''} ${student.apellidos || ''}`.toLowerCase().includes(query)) ||
            (`${student.apellidos || ''} ${student.nombres || ''}`.toLowerCase().includes(query))
          );
        });
      }

      // Filtrar por curso seleccionado
      if (selectedCourse.value) {
        resultado = resultado.filter(student => student.curso === selectedCourse.value);
      }

      // Filtrar por paralelo seleccionado
      if (selectedParallel.value) {
        resultado = resultado.filter(student => student.paralelo === selectedParallel.value);
      }

      return resultado;
    });

    // Obtener URL base del API
    const getApiBaseUrl = () => {
      const baseURL = axiosInstance.defaults.baseURL || import.meta.env.VITE_API_URL;
      return baseURL;
    };

    // Verificar token y autenticación
    const checkAuthentication = () => {
      console.log("Verificando autenticación:");
      console.log(`- Token presente: ${!!token.value}`);
      console.log(`- Rol de usuario: ${userRole.value}`);

      if (!token.value) {
        errorState.value = {
          hasError: true,
          message: 'No se ha iniciado sesión',
          details: 'Por favor, inicie sesión para acceder a esta página',
          isAuthError: true
        };
        return false;
      }

      if (userRole.value !== 'docente' && userRole.value !== 'admin') {
        errorState.value = {
          hasError: true,
          message: 'Acceso restringido',
          details: 'Solo los docentes pueden acceder a esta sección',
          isAuthError: true
        };
        return false;
      }

      // Validar que el token Bearer se envía correctamente
      const authHeader = axiosInstance.defaults.headers.common['Authorization'];
      console.log(`- Encabezado de autorización: ${authHeader || 'No configurado'}`);

      // Si no hay encabezado de autorización o no comienza con "Bearer ", configurarlo
      if (!authHeader || !authHeader.startsWith('Bearer ')) {
        console.log("- Configurando encabezado de autorización");
        axiosInstance.defaults.headers.common['Authorization'] = `Bearer ${token.value}`;
      }

      return true;
    };

    // Refrescar token (simular reconexión para casos de token caducado)
    const refreshToken = async () => {
      try {
        showNotificationMessage(
          'Información',
          'Actualizando autenticación...',
          'is-info',
          '🔄'
        );

        // Obtener perfil del usuario (esto puede ayudar a refrescar cookies/sesión)
        const response = await authService.getUserProfile();

        console.log("Perfil de usuario actualizado:", response.data);

        // Recargar estudiantes después de actualizar la autenticación
        await loadStudents();

        showNotificationMessage(
          'Éxito',
          'Autenticación actualizada correctamente',
          'is-success',
          '✅'
        );
      } catch (error) {
        console.error("Error al actualizar autenticación:", error);

        showNotificationMessage(
          'Error',
          'No se pudo actualizar la autenticación. Redirigiendo a la página de inicio de sesión...',
          'is-danger',
          '❌'
        );

        // Si falla, redirigir al login
        setTimeout(() => {
          // Limpiar localStorage
          localStorage.removeItem('token');
          localStorage.removeItem('user_id');
          localStorage.removeItem('user_role');
          localStorage.removeItem('user_name');

          // Limpiar refs también
          token.value = '';
          userId.value = '';
          userRole.value = '';
          userName.value = '';

          // Redirigir al login
          router.push('/');
        }, 2000);
      }
    };

    // Cargar estudiantes
    const loadStudents = async () => {
      isLoading.value = true;
      errorState.value.hasError = false;

      // Verificar autenticación antes de continuar
      if (!checkAuthentication()) {
        isLoading.value = false;
        return { success: false, error: 'Error de autenticación' };
      }

      try {
        console.log("Cargando todos los estudiantes activos");

        const response = await axiosInstance.get('/users/by-status/activo/');

        if (response.data && Array.isArray(response.data)) {
          console.log(`Usuarios totales obtenidos: ${response.data.length}`);

          const estudiantes = response.data.filter(user => user.rol === 'estudiante');
          console.log(`Estudiantes filtrados: ${estudiantes.length}`);

          students.value = estudiantes;

          // No mostrar notificación automática

          return {
            success: true,
            data: students.value,
            count: students.value.length
          };
        } else {
          throw new Error('Formato de respuesta inesperado');
        }
      } catch (error) {
        console.error('Error al cargar estudiantes:', error);

        const isAuthError = error.response &&
          (error.response.status === 401 || error.response.status === 403);

        const errorMessage = isAuthError
          ? 'Su sesión ha caducado o no tiene permisos para acceder a esta información.'
          : (error.response?.data?.error || error.message || 'No se pudieron obtener los datos de estudiantes');

        errorState.value = {
          hasError: true,
          message: isAuthError ? 'Error de autenticación' : 'Error al cargar estudiantes',
          details: errorMessage,
          isAuthError: isAuthError
        };

        showNotificationMessage(
          errorState.value.message,
          errorState.value.details,
          'is-danger',
          '❌'
        );

        students.value = [];

        return {
          success: false,
          error: errorMessage,
          status: error.response?.status,
          data: error.response?.data
        };
      } finally {
        isLoading.value = false;
      }
    };

    // Funciones para modales
    const viewStudentPerformance = (student) => {
      // Guardar información que estamos en modo docente
      localStorage.setItem('view_mode', 'teacher');
      localStorage.setItem('view_student_id', student.id);
      localStorage.setItem('view_student_name', `${student.nombres} ${student.apellidos}`);

      // Navegar a la vista de historial
      router.push({
        path: '/estudiante/historial-evaluaciones',
        query: {
          student_id: student.id,
          student_name: `${student.nombres} ${student.apellidos}`,
          mode: 'teacher'
        }
      });
    };

    // Función para abrir detalles de evaluación en nueva pestaña (preparada para implementación futura)
    const openEvaluationDetails = (evaluation) => {
      showNotificationMessage(
        'Información',
        'La funcionalidad de detalles de evaluación será implementada próximamente.',
        'is-info',
        'ℹ️'
      );

      // Código que se implementará en el futuro:
      // const evaluationId = evaluation.id;
      // window.open(`/evaluacion/${evaluationId}/detalle`, '_blank');
    };

    // Funciones para cálculos de rendimiento
    const getStudentAverageGrade = (studentId) => {
      const studentEvals = mockStudentData.evaluations.filter(e => e.studentId === studentId);
      if (studentEvals.length === 0) return '0.0';

      const avgGrade = studentEvals.reduce((sum, e) => sum + e.score, 0) / studentEvals.length;
      return avgGrade.toFixed(1);
    };

    const calculateCompletionRate = (studentId) => {
      // Simular tasa de finalización de tareas/evaluaciones
      return Math.floor(Math.random() * 30) + 70; // Entre 70% y 100%
    };

    const calculateBestScore = (studentId) => {
      const studentEvals = mockStudentData.evaluations.filter(e => e.studentId === studentId);
      if (studentEvals.length === 0) return '0.0';

      const bestScore = Math.max(...studentEvals.map(e => e.score));
      return bestScore.toFixed(1);
    };

    const getStudentEvaluations = (studentId) => {
      return mockStudentData.evaluations
        .filter(e => e.studentId === studentId)
        .sort((a, b) => new Date(b.date) - new Date(a.date));
    };

    // Funciones de utilidad
    const clearSearch = () => {
      searchQuery.value = '';
    };

    const filterStudents = () => {
      // Esta función se llama al escribir en el campo de búsqueda
      // La lógica de filtrado está en el computed filteredStudents
    };

    const suggestAction = () => {
      showNotificationMessage(
        'Sugerencia',
        'Puede revisar que los estudiantes estén correctamente asignados a este curso y paralelo.',
        'is-info',
        'ℹ️'
      );
    };

    // Función mejorada para obtener nombre del curso basada en LoginBox.vue
    const getCursoNombre = (curso) => {
      if (!curso) return 'No asignado';

      const cursosMap = {
        '1': '1ro de Bachillerato',
        '2': '2do de Bachillerato',
        '3': '3ro de Bachillerato',
        '8': '8vo de Básica',
        '9': '9no de Básica',
        '10': '10mo de Básica'
      };

      return cursosMap[curso] || `Curso ${curso}`;
    };

    const formatDate = (dateString) => {
      if (!dateString) return '';

      try {
        const date = new Date(dateString);
        return date.toLocaleDateString('es-ES', {
          day: '2-digit',
          month: '2-digit',
          year: 'numeric'
        });
      } catch (error) {
        console.error('Error al formatear fecha:', error);
        return dateString;
      }
    };

    const getScoreClass = (score) => {
      if (score >= 9) return 'excellent';
      if (score >= 7) return 'good';
      if (score >= 5) return 'average';
      return 'poor';
    };

    // Gestión de notificaciones
    const showNotificationMessage = (title, message, type = 'is-success', icon = '✅') => {
      // Limpiar timeout anterior si existe
      if (notification.timeout) {
        clearTimeout(notification.timeout);
      }

      // Actualizar datos de notificación
      notification.show = true;
      notification.title = title;
      notification.message = message;
      notification.type = type;
      notification.icon = icon;

      // Ocultar después de 4 segundos
      notification.timeout = setTimeout(() => {
        notification.show = false;
      }, 4000);
    };

    const closeNotification = () => {
      notification.show = false;
    };

    // Cargar datos iniciales
    onMounted(() => {
      // Cargar valores de localStorage
      token.value = localStorage.getItem('token') || '';
      userId.value = localStorage.getItem('user_id') || '';
      userRole.value = localStorage.getItem('user_role') || '';
      userName.value = localStorage.getItem('user_name') || '';

      // Comprobar autenticación y cargar todos los estudiantes independientemente del curso/paralelo
      if (checkAuthentication()) {
        // Pequeño delay para asegurar que todo está inicializado correctamente
        setTimeout(() => {
          loadStudents();
        }, 100);
      }
    });

    // Observadores para cambios en los filtros
    watch([selectedCourse, selectedParallel], () => {
      clearSearch();
      // Al cambiar el curso o paralelo, se filtra automáticamente por el computed
      // No es necesario volver a cargar todos los estudiantes
    });

    return {
      // Estados
      isLoading,
      students,
      filteredStudents,
      searchQuery,
      paralelos,
      selectedCourse,
      selectedParallel,
      showStudentModal,
      selectedStudent,
      notification,
      errorState,
      // Variables de localStorage
      token,
      userId,
      userRole,
      userName,
      // Funciones
      loadStudents,
      refreshToken,
      viewStudentPerformance,
      clearSearch,
      filterStudents,
      suggestAction,
      formatDate,
      getCursoNombre,
      getScoreClass,
      closeNotification,
      openEvaluationDetails,
      getApiBaseUrl,
      // Funciones de rendimiento
      getStudentAverageGrade,
      calculateCompletionRate,
      calculateBestScore,
      getStudentEvaluations
    };
  }
};
</script>

<style>
/* =================== ESTILOS GLOBALES (SIN SCOPED) =================== */
.student-management-wrapper .button {
  border-radius: var(--border-radius-sm);
  transition: all var(--transition-fast);
  font-weight: 600;
  padding: 0.75rem 1.25rem;
  height: auto;
  display: inline-flex;
  align-items: center;
  justify-content: center;
}

.student-management-wrapper .button.is-primary {
  background-color: var(--color-primary) !important;
  color: var(--color-text-primary) !important;
  border: none !important;
}

.student-management-wrapper .button.is-primary:hover {
  background-color: var(--color-primary-dark) !important;
  transform: translateY(-2px);
  box-shadow: var(--shadow-sm);
}

.student-management-wrapper .progress.is-primary::-webkit-progress-value {
  background-color: var(--color-primary) !important;
}

.student-management-wrapper .tag.is-primary {
  background-color: var(--color-primary) !important;
  color: var(--color-text-primary) !important;
}

.student-management-wrapper .modal-card-foot {
  justify-content: center !important;
  background-color: var(--color-bg-element-alt);
  border-top: 1px solid var(--color-border);
  padding: 1.5rem;
}

.student-management-wrapper .modal-card-head {
  background-color: var(--color-primary);
  color: var(--color-text-primary);
  border-bottom: none;
}

.student-management-wrapper .modal-card-title {
  color: var(--color-text-primary);
  font-weight: 600;
  display: flex;
  align-items: center;
}

.student-management-wrapper .modal-card-body {
  background-color: var(--color-bg-element);
  color: var(--color-text-primary);
  padding: 1.5rem;
}

.student-management-wrapper .input,
.student-management-wrapper .textarea,
.student-management-wrapper .select select {
  background-color: var(--color-bg-element-alt);
  border: 1px solid var(--color-border);
  color: var(--color-text-primary);
  border-radius: var(--border-radius-sm);
}

.student-management-wrapper .input:focus,
.student-management-wrapper .textarea:focus,
.student-management-wrapper .select select:focus {
  border-color: var(--color-primary);
  box-shadow: 0 0 0 2px rgba(235, 179, 0, 0.25);
}

.student-management-wrapper .tabs ul {
  border-bottom-color: var(--color-border);
}

.student-management-wrapper .tabs a {
  color: var(--color-text-secondary);
  border-bottom-color: transparent;
  padding: 0.5rem 1rem;
}

.student-management-wrapper .tabs li.is-active a {
  color: var(--color-primary);
  border-bottom-color: var(--color-primary);
}

.student-management-wrapper .table {
  background-color: var(--color-bg-element);
  color: var(--color-text-primary);
  border-radius: var(--border-radius);
  border: 1px solid var(--color-border);
}

.student-management-wrapper .table thead th {
  color: var(--color-text-secondary);
  border-bottom-color: var(--color-border);
}

.student-management-wrapper .table td {
  border-color: var(--color-border);
}

.student-management-wrapper .modal {
  z-index: 100;
}

.student-management-wrapper .modal-background {
  background-color: rgba(10, 10, 10, 0.7);
}

/* =================== TRANSICIONES =================== */
.fade-enter-active,
.fade-leave-active {
  transition: opacity var(--transition-smooth), transform var(--transition-smooth);
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
  transform: translateY(-10px);
}
</style>

<style scoped>
/* =================== CONTENEDOR PRINCIPAL =================== */
.student-management-wrapper {
  padding: 1.5rem;
  margin-left: 10px;
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

/* =================== HEADER =================== */
.header-section {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 2rem;
  flex-wrap: wrap;
  gap: 1rem;
  background-color: var(--color-bg-element);
  padding: 1.5rem;
  border-radius: var(--border-radius);
  box-shadow: var(--shadow-sm);
  border-left: 4px solid var(--color-primary);
}

.header-content .title {
  color: var(--color-text-primary);
  margin-bottom: 0.5rem;
  font-weight: 600;
  display: flex;
  align-items: center;
  gap: 0.75rem;
}

.header-content .subtitle {
  color: var(--color-text-secondary);
  margin-top: 0;
}

.title-icon {
  font-size: 2rem;
  color: var(--color-primary);
  display: inline-block;
  transform: rotate(-5deg);
}

/* =================== FILTROS =================== */
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
  gap: 1rem;
}

.search-container {
  flex-grow: 2;
  min-width: 200px;
  width: 40%;
}

.search-container .input {
  background-color: var(--color-bg-main);
  border: 1px solid var(--color-border);
  padding-left: 2.5rem;
  height: 2.5rem;
  width: 100%;
  color: var(--color-text-primary);
}

.search-container .icon.is-small.is-left {
  font-size: 1.25rem;
  color: var(--color-primary);
}

.filter-select-container {
  flex-grow: 1;
  min-width: 140px;
  width: 30%;
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

/* =================== ESTADOS DE CARGA Y ERROR =================== */
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

.error-container {
  background-color: var(--color-error-bg);
  border: 2px solid var(--color-error);
  border-radius: var(--border-radius);
  padding: 2rem;
  text-align: center;
  margin: 2rem 0;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
}

.error-icon {
  font-size: 3rem;
  margin-bottom: 1rem;
}

.error-title {
  font-size: 1.5rem;
  font-weight: 600;
  margin-bottom: 0.5rem;
  color: var(--color-error);
}

.error-message {
  margin-bottom: 1.5rem;
  color: var(--color-text-secondary);
}

.error-actions {
  display: flex;
  justify-content: center;
  gap: 1rem;
  flex-wrap: wrap;
}

.retry-btn {
  background-color: var(--color-bg-main);
  color: var(--color-text-primary);
  border: 1px solid var(--color-primary);
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.retry-btn:hover {
  background-color: var(--color-primary);
  color: var(--color-bg-main);
}

.auth-btn {
  background-color: var(--color-bg-main);
  color: var(--color-info);
  border: 1px solid var(--color-info);
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.auth-btn:hover {
  background-color: var(--color-info);
  color: var(--color-bg-main);
}

/* =================== ESTADO VACÍO =================== */
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

/* =================== TABLA DE ESTUDIANTES =================== */
.students-table-container {
  overflow-x: auto;
}

.students-table {
  width: 100%;
  border-collapse: separate;
  border-spacing: 0;
  border-radius: var(--border-radius);
  overflow: hidden;
  background-color: var(--color-bg-element);
  box-shadow: var(--shadow);
  border: 1px solid var(--color-border);
}

.students-table thead {
  background-color: var(--color-bg-element-alt);
}

.students-table th {
  padding: 1rem 1.5rem;
  text-align: left;
  font-weight: 600;
  color: var(--color-text-primary);
  border-bottom: 2px solid var(--color-border);
  font-size: 1rem;
  white-space: nowrap;
}

.students-table td {
  padding: 0.875rem 1.5rem;
  border-bottom: 1px solid var(--color-border);
  color: var(--color-text-secondary);
  font-size: 0.95rem;
  transition: all var(--transition-fast) ease;
}

.students-table tbody tr:hover {
  background-color: var(--color-bg-element-hover);
}

.students-table tbody tr:hover td {
  color: var(--color-text-primary);
}

.students-table tbody tr:last-child td {
  border-bottom: none;
}

.icon-text {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.icon-text .icon {
  color: var(--color-primary-light);
  font-size: 1.2rem;
  flex-shrink: 0;
}

.id-text {
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.icon-text .student-icon {
  font-size: 1.3rem;
}

.student-col {
  width: 200px;
  text-align: left;
}

.actions-col {
  width: 120px;
  text-align: center;
}

.student-info {
  display: flex;
  align-items: center;
  gap: 15px;
  padding-left: 5px;
}

.student-icon {
  font-size: 1.3rem;
  display: inline-block;
}

.action-button {
  background-color: var(--color-success-light);
  color: var(--color-bg-main);
  border: none;
  border-radius: var(--border-radius);
  padding: 0.15rem 0.4rem;
  font-size: 0.9rem;
  font-weight: 500;
  cursor: pointer;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 0.2rem;
  box-shadow: var(--shadow-sm);
  width: 128px;
  height: 35px;
  text-align: center;
  margin: 0 auto;
}

.action-button:hover {
  background-color: var(--color-success);
}

/* =================== MODAL DE ESTUDIANTE =================== */
.modal-title-icon {
  margin-right: 0.75rem;
  font-size: 1.25rem;
}

.section-title {
  font-size: 1.1rem;
  font-weight: 600;
  margin: 1.5rem 0 1rem;
  color: var(--color-text-primary);
  padding-bottom: 0.5rem;
  border-bottom: 1px solid var(--color-border);
}

.student-contact-info {
  background-color: var(--color-bg-element-alt);
  border-radius: var(--border-radius-sm);
  padding: 0.75rem 1rem;
  margin-bottom: 1.5rem;
  border-left: 3px solid var(--color-info);
  display: flex;
  justify-content: center;
  align-items: center;
}

.contact-item {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  font-size: 1rem;
}

.contact-icon {
  color: var(--color-info);
  font-size: 1.25rem;
}

.contact-value {
  color: var(--color-text-primary);
  font-weight: 500;
}

/* =================== ESTADÍSTICAS DE RENDIMIENTO =================== */
.performance-stats {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
  gap: 1rem;
  margin-bottom: 1.5rem;
}

.stat-box {
  background-color: var(--color-bg-element-alt);
  border-radius: var(--border-radius-sm);
  padding: 1.25rem 1rem;
  text-align: center;
  border-bottom: 3px solid var(--color-primary);
}

.stat-icon {
  font-size: 1.75rem;
  margin-bottom: 0.75rem;
  color: var(--color-primary);
}

.stat-value {
  font-size: 1.5rem;
  font-weight: 700;
  margin-bottom: 0.25rem;
  color: var(--color-text-primary);
}

.stat-label {
  font-size: 0.85rem;
  color: var(--color-text-muted);
}

/* =================== EVALUACIONES =================== */
.evaluations-list {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
  margin-top: 0.5rem;
}

.evaluation-item {
  background-color: var(--color-bg-element-alt);
  border-radius: var(--border-radius-sm);
  padding: 1rem;
  border-left: 3px solid var(--color-primary);
}

.evaluation-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 0.5rem;
}

.evaluation-name {
  font-weight: 600;
  color: var(--color-text-primary);
}

.evaluation-score {
  font-weight: 600;
  padding: 0.25rem 0.5rem;
  border-radius: var(--border-radius-sm);
  font-size: 0.85rem;
}

.evaluation-score.excellent {
  background-color: var(--color-success-bg);
  color: var(--color-success);
}

.evaluation-score.good {
  background-color: rgba(235, 179, 0, 0.15);
  color: var(--color-primary);
}

.evaluation-score.average {
  background-color: var(--color-warning-bg);
  color: var(--color-warning);
}

.evaluation-score.poor {
  background-color: var(--color-error-bg);
  color: var(--color-error);
}

.evaluation-date {
  font-size: 0.85rem;
  color: var(--color-text-muted);
  margin-bottom: 0.5rem;
}

.progress.excellent::-webkit-progress-value {
  background-color: var(--color-success);
}

.progress.good::-webkit-progress-value {
  background-color: var(--color-primary);
}

.progress.average::-webkit-progress-value {
  background-color: var(--color-warning);
}

.progress.poor::-webkit-progress-value {
  background-color: var(--color-error);
}

.evaluation-actions {
  display: flex;
  justify-content: flex-end;
  margin-top: 0.75rem;
}

.details-button {
  font-size: 0.85rem;
  padding: 0.4rem 0.75rem;
  background-color: var(--color-bg-main);
  color: var(--color-text-secondary);
  border: 1px solid var(--color-border);
  border-radius: 4px;
  display: flex;
  align-items: center;
  gap: 0.5rem;
  transition: all var(--transition-fast);
}

.details-button:hover {
  background-color: var(--color-primary);
  color: var(--color-text-primary);
  border-color: var(--color-primary);
  transform: translateY(-2px);
}

.no-data {
  padding: 1.5rem;
  text-align: center;
  color: var(--color-text-muted);
  background-color: var(--color-bg-element-alt);
  border-radius: var(--border-radius-sm);
  border: 1px dashed var(--color-border);
}

/* =================== NOTIFICACIONES =================== */
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
  animation: slideIn var(--transition-smooth) ease-out;
}

.custom-notification.is-success {
  border-left-color: var(--color-success);
}

.custom-notification.is-danger {
  border-left-color: var(--color-error);
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

/* =================== ANIMACIONES =================== */
@keyframes spin {
  0% {
    transform: rotate(0deg);
  }
  100% {
    transform: rotate(360deg);
  }
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

/* =================== RESPONSIVE =================== */
@media screen and (max-width: 768px) {
  .student-management-wrapper {
    margin-left: 0;
    padding: 1rem;
  }

  .header-section {
    flex-direction: column;
    align-items: flex-start;
  }

  .filters-section {
    flex-direction: column;
  }

  .select-filters {
    width: 100%;
    justify-content: space-between;
    flex-wrap: wrap;
  }

  .performance-stats {
    grid-template-columns: 1fr;
  }
}

.icon {
  opacity: 100%;
}
</style>