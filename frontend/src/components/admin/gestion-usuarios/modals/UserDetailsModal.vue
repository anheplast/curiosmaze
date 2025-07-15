<!-- src/components/admin/gestion-usuarios/modals/UserDetailsModal.vue -->
<template>
  <div class="modal is-active">
    <div class="modal-background" @click="$emit('close')"></div>
    <div class="modal-card">
      <header class="modal-card-head">
        <p class="modal-card-title">
          <span class="modal-title-icon">👁️</span>
          Detalles del Usuario
        </p>
        <button class="delete" aria-label="close" @click="$emit('close')"></button>
      </header>

      <section class="modal-card-body" v-if="user">
        <div class="user-details-container">
          <div class="user-details-header">
            <div class="user-avatar-large">
              {{ getInitials(user.nombres, user.apellidos) }}
            </div>
            <div class="user-info-main">
              <h2 class="user-name-large">{{ user.nombres }} {{ user.apellidos }}</h2>
              <p class="user-role-badge" :class="user.rol">{{ capitalizeFirst(user.rol) }}</p>
            </div>
          </div>

          <div class="user-details-grid">
            <div class="detail-section">
              <h3 class="section-title">Información Personal</h3>
              <div class="detail-item">
                <span class="detail-label">Identificación:</span>
                <span class="detail-value">{{ user.identificacion }}</span>
              </div>
              <div class="detail-item">
                <span class="detail-label">Correo electrónico:</span>
                <span class="detail-value">{{ user.email || 'No disponible' }}</span>
              </div>
              <div class="detail-item" v-if="user.genero">
                <span class="detail-label">Género:</span>
                <span class="detail-value">{{ capitalizeFirst(user.genero) }}</span>
              </div>
              <div class="detail-item" v-if="user.edad">
                <span class="detail-label">Edad:</span>
                <span class="detail-value">{{ user.edad }} años</span>
              </div>
              <div class="detail-item" v-if="user.fecha_nacimiento">
                <span class="detail-label">Fecha de nacimiento:</span>
                <span class="detail-value">{{ formatDate(user.fecha_nacimiento) }}</span>
              </div>
            </div>

            <div class="detail-section" v-if="user.rol === 'estudiante'">
              <h3 class="section-title">Información Académica</h3>
              <div class="detail-item">
                <span class="detail-label">Curso:</span>
                <span class="detail-value">{{ getCursoNombre(user.curso) }}</span>
              </div>
              <div class="detail-item">
                <span class="detail-label">Paralelo:</span>
                <span class="detail-value">{{ user.paralelo || 'No asignado' }}</span>
              </div>
              <div class="detail-item" v-if="user.turno">
                <span class="detail-label">Turno:</span>
                <span class="detail-value">{{ capitalizeFirst(user.turno) }}</span>
              </div>
            </div>

            <div class="detail-section" v-if="user.rol === 'docente'">
              <h3 class="section-title">Información Profesional</h3>
              <div class="detail-item" v-if="user.especializacion">
                <span class="detail-label">Especialización:</span>
                <span class="detail-value">{{ user.especializacion }}</span>
              </div>
            </div>

            <div class="detail-section">
              <h3 class="section-title">Información del Sistema</h3>
              <div class="detail-item">
                <span class="detail-label">Fecha de registro:</span>
                <span class="detail-value">{{ formatDate(user.fecha_registro) }}</span>
              </div>
              <div class="detail-item">
                <span class="detail-label">Estado:</span>
                <span class="detail-value status-badge" :class="user.estado">
                  {{ capitalizeFirst(user.estado) }}
                </span>
              </div>
              <div class="detail-item" v-if="user.fecha_aprobacion">
                <span class="detail-label">Fecha de aprobación:</span>
                <span class="detail-value">{{ formatDate(user.fecha_aprobacion) }}</span>
              </div>
              <div class="detail-item" v-if="user.ultimo_login">
                <span class="detail-label">Último inicio de sesión:</span>
                <span class="detail-value">{{ formatDate(user.ultimo_login) }}</span>
              </div>
            </div>
          </div>
        </div>
      </section>

      <footer class="modal-card-foot">
        <button class="button is-primary" @click="$emit('close')">Cerrar</button>
      </footer>
    </div>
  </div>
</template>

<script>
export default {
  name: 'UserDetailsModal',
  props: {
    user: {
      type: Object,
      required: true
    }
  },
  methods: {
    // Obtener iniciales para avatar
    getInitials(nombres, apellidos) {
      let initials = '';
      if (nombres) {
        initials += nombres.charAt(0).toUpperCase();
      }
      if (apellidos) {
        initials += apellidos.charAt(0).toUpperCase();
      }
      return initials || '?';
    },

    // Formatear fecha
    formatDate(date) {
      if (!date) return 'No disponible';

      const d = new Date(date);
      return d.toLocaleDateString('es-ES', {
        day: '2-digit',
        month: '2-digit',
        year: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
      });
    },

    // Capitalizar primera letra
    capitalizeFirst(text) {
      if (!text) return 'No disponible';
      return text.charAt(0).toUpperCase() + text.slice(1);
    },

    // Obtener nombre del curso
    getCursoNombre(curso) {
      if (!curso) return 'No asignado';

      const cursos = {
        '1': '1ro de Bachillerato',
        '2': '2do de Bachillerato',
        '3': '3ro de Bachillerato',
        '8': '8vo de Básica',
        '9': '9no de Básica',
        '10': '10mo de Básica'
      };
      return cursos[curso] || `Curso ${curso}`;
    }
  }
};
</script>

<style scoped>
/* =================== MODAL CARD =================== */
.modal-card {
  background-color: var(--color-bg-element);
  border-radius: var(--border-radius);
  overflow: hidden;
  width: 90%;
  max-width: 700px;
  margin: 0 auto;
}

.modal-card-head {
  background-color: var(--color-info);
  padding: 1.25rem;
  border-bottom: none;
}

.modal-card-title {
  color: white;
  font-weight: 600;
  display: flex;
  align-items: center;
  gap: 0.75rem;
}

.modal-title-icon {
  font-size: 1.5rem;
}

.modal-card-body {
  background-color: var(--color-bg-element);
  padding: 2rem;
  color: var(--color-text-primary);
  max-height: 70vh;
  overflow-y: auto;
}

.modal-card-foot {
  background-color: var(--color-bg-element-alt);
  padding: 1.25rem;
  justify-content: center;
  border-top: 1px solid var(--color-border);
}

/* =================== BOTÓN =================== */
.button {
  background-color: var(--color-primary);
  color: white;
  border: none;
  border-radius: var(--border-radius-sm);
  padding: 0.625rem 2rem;
  font-weight: 600;
  transition: all var(--transition-fast);
  cursor: pointer;
}

.button:hover {
  background-color: var(--color-primary-dark);
  transform: translateY(-1px);
  box-shadow: var(--shadow-sm);
}

/* =================== CONTENEDOR DE DETALLES =================== */
.user-details-container {
  max-width: 600px;
  margin: 0 auto;
}

/* =================== HEADER DEL USUARIO =================== */
.user-details-header {
  display: flex;
  gap: 1.5rem;
  align-items: center;
  margin-bottom: 2rem;
  padding-bottom: 1rem;
  border-bottom: 1px solid var(--color-border);
}

.user-avatar-large {
  width: 80px;
  height: 80px;
  border-radius: 50%;
  background-color: var(--color-primary);
  color: var(--color-bg-element);
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: bold;
  font-size: 2rem;
  flex-shrink: 0;
}

.user-info-main {
  flex: 1;
}

.user-name-large {
  font-size: 1.5rem;
  font-weight: 600;
  margin-bottom: 0.5rem;
  color: var(--color-text-primary);
}

/* =================== BADGES DE ROL =================== */
.user-role-badge {
  padding: 0.5rem 1rem;
  border-radius: 20px;
  font-size: 1rem;
  font-weight: 500;
  display: inline-block;
}

.user-role-badge.estudiante {
  background-color: var(--color-success-bg);
  color: var(--color-success);
}

.user-role-badge.docente {
  background-color: var(--color-info-bg);
  color: var(--color-info);
}

.user-role-badge.admin {
  background-color: var(--color-warning-bg);
  color: var(--color-warning);
}

/* =================== GRID DE DETALLES =================== */
.user-details-grid {
  display: grid;
  gap: 1.5rem;
}

.detail-section {
  background-color: var(--color-bg-element-alt);
  border-radius: var(--border-radius);
  padding: 1.5rem;
  border: 1px solid var(--color-border);
}

.section-title {
  font-size: 1.1rem;
  font-weight: 600;
  margin-bottom: 1rem;
  color: var(--color-primary);
  border-bottom: 1px solid var(--color-border);
  padding-bottom: 0.5rem;
}

/* =================== ITEMS DE DETALLE =================== */
.detail-item {
  margin-bottom: 0.75rem;
  display: flex;
  align-items: center;
}

.detail-item:last-child {
  margin-bottom: 0;
}

.detail-label {
  font-weight: 500;
  color: var(--color-text-secondary);
  min-width: 140px;
  margin-right: 0.5rem;
}

.detail-value {
  color: var(--color-text-primary);
  flex: 1;
}

/* =================== BADGES DE ESTADO =================== */
.status-badge {
  display: inline-block;
  padding: 0.25rem 0.75rem;
  border-radius: 20px;
  font-size: 0.85rem;
  font-weight: 500;
}

.status-badge.activo {
  background-color: var(--color-success-bg);
  color: var(--color-success);
}

.status-badge.pendiente {
  background-color: var(--color-warning-bg);
  color: var(--color-warning);
}

.status-badge.rechazado {
  background-color: var(--color-error-bg);
  color: var(--color-error);
}

/* =================== MEDIA QUERIES =================== */
@media (max-width: 768px) {
  .user-details-header {
    flex-direction: column;
    text-align: center;
  }

  .detail-item {
    flex-direction: column;
    align-items: flex-start;
  }

  .detail-label {
    min-width: auto;
    margin-bottom: 0.25rem;
  }
}
</style>