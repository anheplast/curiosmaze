<!-- src/components/admin/gestion-usuarios/modals/UserFormModal.vue -->
<template>
  <div class="modal is-active">
    <div class="modal-background" @click="$emit('cancel')"></div>
    <div class="modal-card">
      <header class="modal-card-head">
        <p class="modal-card-title">
          <span class="modal-title-icon">{{ titleIcon }}</span>
          {{ title }}
        </p>
        <button class="delete" aria-label="close" @click="$emit('cancel')"></button>
      </header>

      <section class="modal-card-body">
        <div v-if="formErrors.length > 0" class="form-errors">
          <div class="error-header">Por favor, corrija los siguientes errores:</div>
          <ul>
            <li v-for="(error, index) in formErrors" :key="index">{{ error }}</li>
          </ul>
        </div>

        <form @submit.prevent="submitForm" class="edit-form">
          <!-- Selector de rol -->
          <div class="role-selector">
            <div class="role-option" v-for="role in availableRoles" :key="role.value"
              :class="{ active: formData.rol === role.value }" @click="formData.rol = role.value">
              <span class="role-icon">{{ role.icon }}</span>
              <span class="role-name">{{ role.label }}</span>
            </div>
          </div>

          <!-- Información Personal -->
          <div class="form-section">
            <h3 class="section-title">Información Personal</h3>

            <div class="field-group">
              <div class="field">
                <label class="label">Nombres</label>
                <div class="control">
                  <input class="input" type="text" v-model="formData.nombres" required>
                </div>
              </div>

              <div class="field">
                <label class="label">Apellidos</label>
                <div class="control">
                  <input class="input" type="text" v-model="formData.apellidos" required>
                </div>
              </div>
            </div>

            <div class="field">
              <label class="label">Número de Identificación</label>
              <div class="control">
                <input class="input" type="text" v-model="formData.identificacion" required>
              </div>
            </div>

            <div class="field">
              <label class="label">Correo electrónico</label>
              <div class="control">
                <input class="input" type="email" v-model="formData.email" placeholder="correo@ejemplo.com">
              </div>
            </div>

            <div class="field-group">
              <div class="field">
                <label class="label">Género</label>
                <div class="control">
                  <div class="select is-fullwidth">
                    <select v-model="formData.genero">
                      <option value="">Seleccionar</option>
                      <option value="masculino">Masculino</option>
                      <option value="femenino">Femenino</option>
                    </select>
                  </div>
                </div>
              </div>

              <div class="field">
                <label class="label">Edad</label>
                <div class="control">
                  <input class="input" type="number" v-model="formData.edad" min="1" max="100">
                </div>
              </div>
            </div>
          </div>

          <!-- Información Académica (para estudiantes) -->
          <div class="form-section" v-if="formData.rol === 'estudiante'">
            <h3 class="section-title">Información Académica</h3>

            <div class="field-group">
              <div class="field">
                <label class="label">Curso</label>
                <div class="control">
                  <div class="select is-fullwidth">
                    <select v-model="formData.curso">
                      <option value="">Seleccionar</option>
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

              <div class="field">
                <label class="label">Paralelo</label>
                <div class="control">
                  <div class="select is-fullwidth">
                    <select v-model="formData.paralelo">
                      <option value="">Seleccionar</option>
                      <option v-for="letra in paralelos" :key="letra" :value="letra">{{ letra }}</option>
                    </select>
                  </div>
                </div>
              </div>
            </div>

            <div class="field">
              <label class="label">Turno</label>
              <div class="control">
                <div class="select is-fullwidth">
                  <select v-model="formData.turno">
                    <option value="">Seleccionar</option>
                    <option value="mañana">Mañana</option>
                    <option value="tarde">Tarde</option>
                  </select>
                </div>
              </div>
            </div>
          </div>

          <!-- Información Profesional (para docentes) -->
          <div class="form-section" v-if="formData.rol === 'docente'">
            <h3 class="section-title">Información Profesional</h3>

            <div class="field">
              <label class="label">Especialización</label>
              <div class="control">
                <input class="input" type="text" v-model="formData.especializacion"
                  placeholder="Ej: Matemática, Informática, Física...">
              </div>
            </div>

            <div class="field">
              <label class="label">Turno</label>
              <div class="control">
                <div class="select is-fullwidth">
                  <select v-model="formData.turno">
                    <option value="">Seleccionar</option>
                    <option value="mañana">Mañana</option>
                    <option value="tarde">Tarde</option>
                  </select>
                </div>
              </div>
            </div>
          </div>

          <!-- Contraseña (solo para creación o si se está cambiando) -->
          <div class="form-section">
            <h3 class="section-title">Seguridad</h3>

            <div class="field">
              <label class="label">
                {{ mode === 'create' ? 'Contraseña' : 'Nueva Contraseña' }}
                <span v-if="mode === 'edit'" class="optional-text">(opcional)</span>
              </label>
              <div class="control">
                <input class="input" type="password" v-model="formData.password" :required="mode === 'create'"
                  placeholder="Ingresar contraseña" @input="checkPasswordStrength">
              </div>
              <!-- Indicador de fuerza de contraseña -->
              <div v-if="formData.password" class="password-strength-wrapper">
                <div class="password-strength-meter">
                  <div class="password-strength-value"
                    :style="{ width: passwordStrength.percentage + '%', backgroundColor: passwordStrength.color }">
                  </div>
                </div>
                <small :style="{ color: passwordStrength.color }">{{ passwordStrength.message }}</small>
              </div>
            </div>

            <div class="field" v-if="formData.password">
              <label class="label">Confirmar Contraseña</label>
              <div class="control">
                <input class="input" type="password" v-model="formData.password_confirm"
                  placeholder="Confirmar contraseña" @input="checkPasswordMatch">
              </div>
              <p v-if="passwordMismatch" class="help is-danger">Las contraseñas no coinciden</p>
            </div>
          </div>
        </form>
      </section>

      <footer class="modal-card-foot">
        <button class="button cancel-btn" @click="$emit('cancel')">Cancelar</button>
        <button class="button save-btn" @click="submitForm" :disabled="isLoading || hasErrors">
          {{ isLoading ? 'Guardando...' : 'Guardar' }}
        </button>
      </footer>
    </div>
  </div>
</template>

<script>
import { ref, computed, reactive, watch } from 'vue';

export default {
  name: 'UserFormModal',
  props: {
    user: {
      type: Object,
      default: null
    },
    mode: {
      type: String,
      default: 'create', // 'create' o 'edit'
      validator: value => ['create', 'edit'].includes(value)
    },
    isLoading: {
      type: Boolean,
      default: false
    }
  },
  setup(props, { emit }) {
    // Roles disponibles
    const availableRoles = [
      { value: 'estudiante', label: 'Estudiante', icon: '👨‍🎓' },
      { value: 'docente', label: 'Docente', icon: '👨‍🏫' },
      { value: 'admin', label: 'Administrador', icon: '👑' }
    ];

    // Lista de paralelos
    const paralelos = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M'];

    // Estado de errores
    const formErrors = ref([]);
    const passwordMismatch = ref(false);

    // Estado de fortaleza de contraseña
    const passwordStrength = reactive({
      score: 0,
      percentage: 0,
      message: '',
      color: '#cccccc'
    });

    // Función para inicializar datos del formulario
    const initializeFormData = () => ({
      id: props.user?.id || null,
      username: props.user?.username || '',
      nombres: props.user?.nombres || '',
      apellidos: props.user?.apellidos || '',
      identificacion: props.user?.identificacion || '',
      email: props.user?.email || '',
      password: '',
      password_confirm: '',
      rol: props.user?.rol || 'estudiante',
      genero: props.user?.genero || '',
      edad: props.user?.edad || null,
      curso: props.user?.curso || '',
      paralelo: props.user?.paralelo || '',
      turno: props.user?.turno || '',
      especializacion: props.user?.especializacion || ''
    });

    // Datos del formulario
    const formData = reactive(initializeFormData());

    // Watch para actualizar formData cuando cambien los props
    watch(() => props.user, (newUser) => {
      if (newUser) {
        Object.assign(formData, initializeFormData());
      }
    }, { immediate: true, deep: true });

    // Título del modal
    const title = computed(() => {
      return props.mode === 'create' ? 'Crear Nuevo Usuario' : 'Editar Usuario';
    });

    // Ícono del título
    const titleIcon = computed(() => {
      return props.mode === 'create' ? '👤' : '✏️';
    });

    // Verificar si hay errores
    const hasErrors = computed(() => {
      return formErrors.value.length > 0 || passwordMismatch.value;
    });

    // Verificar coincidencia de contraseñas
    const checkPasswordMatch = () => {
      passwordMismatch.value = formData.password !== formData.password_confirm;
    };

    // Verificar fortaleza de contraseña
    const checkPasswordStrength = () => {
      const password = formData.password;
      let score = 0;

      // Criterios de fortaleza
      if (password.length >= 8) score += 1;
      if (/[A-Z]/.test(password)) score += 1;
      if (/[a-z]/.test(password)) score += 1;
      if (/[0-9]/.test(password)) score += 1;
      if (/[^A-Za-z0-9]/.test(password)) score += 1;

      // Actualizar estado de fortaleza
      passwordStrength.score = score;
      passwordStrength.percentage = (score / 5) * 100;

      // Definir mensaje y color
      if (password === '') {
        passwordStrength.message = '';
        passwordStrength.color = '#cccccc';
      } else if (score <= 1) {
        passwordStrength.message = 'Muy débil';
        passwordStrength.color = '#ff4d4f';
      } else if (score <= 2) {
        passwordStrength.message = 'Débil';
        passwordStrength.color = '#ff7a45';
      } else if (score <= 3) {
        passwordStrength.message = 'Regular';
        passwordStrength.color = '#ffc53d';
      } else if (score <= 4) {
        passwordStrength.message = 'Buena';
        passwordStrength.color = '#73d13d';
      } else {
        passwordStrength.message = 'Excelente';
        passwordStrength.color = '#389e0d';
      }

      // Verificar coincidencia si ya hay contraseña de confirmación
      if (formData.password_confirm) {
        checkPasswordMatch();
      }
    };

    // Validar formulario
    const validateForm = () => {
      formErrors.value = [];

      // Validar campos obligatorios básicos
      if (!formData.nombres) formErrors.value.push('El nombre es obligatorio');
      if (!formData.apellidos) formErrors.value.push('Los apellidos son obligatorios');
      if (!formData.identificacion) formErrors.value.push('El número de identificación es obligatorio');

      // Validar contraseña en creación
      if (props.mode === 'create') {
        if (!formData.password) {
          formErrors.value.push('La contraseña es obligatoria');
        } else if (passwordStrength.score < 3) {
          formErrors.value.push('La contraseña es demasiado débil');
        }
      } else if (formData.password && passwordStrength.score < 3) {
        formErrors.value.push('La contraseña es demasiado débil');
      }

      // Validar coincidencia de contraseñas
      if (formData.password && formData.password !== formData.password_confirm) {
        formErrors.value.push('Las contraseñas no coinciden');
      }

      // Validaciones según rol
      if (formData.rol === 'estudiante') {
        if (!formData.curso) formErrors.value.push('El curso es obligatorio');
        if (!formData.paralelo) formErrors.value.push('El paralelo es obligatorio');
      }

      return formErrors.value.length === 0;
    };

    // Enviar formulario
    const submitForm = () => {
      // Sincronizar username con identificación
      formData.username = formData.identificacion;

      if (!validateForm()) return;

      // Preparar datos para envío
      const userData = { ...formData };

      // Eliminar confirmación de contraseña
      delete userData.password_confirm;

      // Si no se cambia la contraseña en edición, eliminarla
      if (props.mode === 'edit' && !userData.password) {
        delete userData.password;
      }

      // Llamar al evento para guardar
      emit('save', userData);
    };

    return {
      availableRoles,
      paralelos,
      formData,
      formErrors,
      passwordMismatch,
      passwordStrength,
      title,
      titleIcon,
      hasErrors,
      checkPasswordMatch,
      checkPasswordStrength,
      submitForm
    };
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
  background-color: var(--color-primary);
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
  justify-content: flex-end;
  border-top: 1px solid var(--color-border);
}

/* =================== BOTONES DEL MODAL =================== */
.cancel-btn {
  background-color: var(--color-bg-main);
  color: var(--color-text-primary);
  border: 1px solid var(--color-border);
  margin-right: 0.75rem;
  transition: all var(--transition-fast);
}

.cancel-btn:hover {
  background-color: var(--color-bg-element-hover);
  border-color: var(--color-border-hover);
}

.save-btn {
  background-color: var(--color-primary);
  color: var(--color-bg-main);
  border: none;
  transition: all var(--transition-fast);
}

.save-btn:hover:not(:disabled) {
  background-color: var(--color-primary-dark);
}

.save-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

/* =================== FORMULARIO =================== */
.edit-form {
  max-width: 600px;
  margin: 0 auto;
}

.form-section {
  margin-bottom: 2rem;
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

/* =================== CAMPOS DEL FORMULARIO =================== */
.field {
  margin-bottom: 1rem;
}

.field:last-child {
  margin-bottom: 0;
}

.field-group {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 1rem;
}

.label {
  color: var(--color-text-primary);
  font-weight: 600;
  margin-bottom: 0.5rem;
  display: block;
}

.optional-text {
  color: var(--color-text-secondary);
  font-size: 0.8rem;
  font-weight: normal;
  margin-left: 0.5rem;
}

.input,
.select select {
  background-color: var(--color-bg-main);
  border: 1px solid var(--color-border);
  color: var(--color-text-primary);
  border-radius: var(--border-radius-sm);
  padding: 0.5rem 0.75rem;
  height: 2.5rem;
  width: 100%;
  transition: border-color var(--transition-fast);
}

.input:focus,
.select select:focus {
  border-color: var(--color-border-focus);
  outline: none;
  box-shadow: 0 0 0 2px rgba(138, 79, 255, 0.25);
}

/* =================== SELECTOR DE ROL =================== */
.role-selector {
  display: flex;
  justify-content: center;
  gap: 1rem;
  margin-bottom: 2rem;
}

.role-option {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 0.5rem;
  padding: 1rem;
  border-radius: var(--border-radius);
  background-color: var(--color-bg-element-alt);
  border: 2px solid var(--color-border);
  cursor: pointer;
  transition: all var(--transition-fast);
  width: 120px;
}

.role-option:hover {
  border-color: var(--color-primary-light);
  transform: translateY(-3px);
  box-shadow: var(--shadow-sm);
}

.role-option.active {
  border-color: var(--color-primary);
  background-color: rgba(235, 179, 0, 0.1);
}

.role-icon {
  font-size: 2rem;
}

.role-name {
  font-weight: 600;
  color: var(--color-text-primary);
}

/* =================== ERRORES DEL FORMULARIO =================== */
.form-errors {
  background-color: var(--color-error-bg);
  border: 1px solid var(--color-error);
  border-radius: var(--border-radius);
  padding: 1rem;
  margin-bottom: 1.5rem;
  color: var(--color-error);
}

.error-header {
  font-weight: 600;
  margin-bottom: 0.5rem;
}

.form-errors ul {
  padding-left: 1.5rem;
}

.help.is-danger {
  color: var(--color-error);
  font-size: 0.8rem;
  margin-top: 0.25rem;
}

/* =================== INDICADOR DE FUERZA DE CONTRASEÑA =================== */
.password-strength-wrapper {
  margin-top: 0.5rem;
}

.password-strength-meter {
  height: 6px;
  background-color: var(--color-bg-main);
  border-radius: 3px;
  margin-bottom: 0.3rem;
}

.password-strength-value {
  height: 100%;
  border-radius: 3px;
  transition: width var(--transition-smooth), background-color var(--transition-smooth);
}

/* =================== MEDIA QUERIES =================== */
@media (max-width: 768px) {
  .field-group {
    grid-template-columns: 1fr;
  }

  .role-selector {
    flex-direction: column;
    align-items: center;
  }

  .role-option {
    width: 100%;
    max-width: 250px;
    flex-direction: row;
    justify-content: flex-start;
    text-align: left;
  }

  .role-icon {
    margin-right: 1rem;
  }
}
</style>