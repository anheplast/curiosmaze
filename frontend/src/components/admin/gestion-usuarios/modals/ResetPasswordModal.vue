<!-- components/admin/modals/ResetPasswordModal.vue -->
<template>
    <div class="modal is-active">
      <div class="modal-background" @click="$emit('cancel')"></div>
      <div class="modal-card">
        <header class="modal-card-head">
          <p class="modal-card-title">
            <span class="modal-title-icon">🔑</span>
            Restablecer Contraseña
          </p>
          <button class="delete" aria-label="close" @click="$emit('cancel')"></button>
        </header>
        
        <section class="modal-card-body">
          <div class="reset-content">
            <div class="reset-icon">🔐</div>
            <h3 class="reset-title">Restablecer contraseña para {{ user.nombres }} {{ user.apellidos }}</h3>
            
            <div class="reset-info">
              <p>
                Está a punto de restablecer la contraseña del usuario. El usuario deberá crear una nueva contraseña la próxima vez que inicie sesión.
              </p>
              <div class="user-card">
                <div class="user-avatar-small">{{ getInitials(user.nombres, user.apellidos) }}</div>
                <div class="user-details-small">
                  <div class="user-name-small">{{ user.nombres }} {{ user.apellidos }}</div>
                  <div class="user-id-small">{{ user.identificacion }}</div>
                  <div class="user-role-small" :class="user.rol">{{ user.rol }}</div>
                </div>
              </div>
            </div>
            
            <div class="confirmation-section">
              <p class="confirmation-text">
                Para continuar, por favor ingrese su contraseña de administrador para confirmar:
              </p>
              
              <div class="field">
                <div class="control">
                  <input 
                    class="input" 
                    type="password" 
                    v-model="adminPassword" 
                    placeholder="Ingrese su contraseña de administrador"
                    :class="{ 'is-danger': passwordError }"
                    @input="passwordError = false"
                    ref="passwordInput"
                  >
                </div>
                <p v-if="passwordError" class="help is-danger">
                  Por favor, ingrese su contraseña para continuar
                </p>
              </div>
            </div>
          </div>
        </section>
        
        <footer class="modal-card-foot">
          <button class="button cancel-btn" @click="$emit('cancel')">Cancelar</button>
          <button 
            class="button reset-btn" 
            @click="resetPassword" 
            :disabled="isLoading || !adminPassword"
          >
            {{ isLoading ? 'Procesando...' : 'Restablecer Contraseña' }}
          </button>
        </footer>
      </div>
    </div>
  </template>
  
  <script>
  import { ref, onMounted, nextTick } from 'vue';
  
  export default {
    name: 'ResetPasswordModal',
    props: {
      user: {
        type: Object,
        required: true
      },
      isLoading: {
        type: Boolean,
        default: false
      }
    },
    setup(props, { emit }) {
      const adminPassword = ref('');
      const passwordError = ref(false);
      const passwordInput = ref(null);
      
      // Método para restablecer contraseña
      const resetPassword = () => {
        if (!adminPassword.value) {
          passwordError.value = true;
          return;
        }
        
        emit('reset', { adminPassword: adminPassword.value });
      };
      
      // Obtener iniciales para avatar
      const getInitials = (nombres, apellidos) => {
        let initials = '';
        if (nombres) {
          initials += nombres.charAt(0).toUpperCase();
        }
        if (apellidos) {
          initials += apellidos.charAt(0).toUpperCase();
        }
        return initials || '?';
      };
      
      // Al montar el componente, enfocar el campo de contraseña
      onMounted(() => {
        nextTick(() => {
          passwordInput.value?.focus();
        });
      });
      
      return {
        adminPassword,
        passwordError,
        passwordInput,
        resetPassword,
        getInitials
      };
    }
  };
  </script>
  
  <style scoped>
  .modal-card {
    background-color: var(--color-bg-element);
    border-radius: var(--border-radius);
    overflow: hidden;
    width: 90%;
    max-width: 500px;
    margin: 0 auto;
  }
  
  .modal-card-head {
    background-color: var(--color-warning);
    padding: 1.25rem;
    border-bottom: none;
  }
  
  .modal-card-title {
    color: var(--color-bg-main);
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
  }
  
  .modal-card-foot {
    background-color: var(--color-bg-element-alt);
    padding: 1.25rem;
    justify-content: flex-end;
    border-top: 1px solid var(--color-border);
  }
  
  .cancel-btn {
    background-color: var(--color-bg-main);
    color: var(--color-text-primary);
    border: 1px solid var(--color-border);
    margin-right: 0.75rem;
  }
  
  .reset-btn {
    background-color: var(--color-warning);
    color: var(--color-bg-main);
    border: none;
  }
  
  .reset-btn:disabled {
    opacity: 0.5;
    cursor: not-allowed;
  }
  
  /* Contenido */
  .reset-content {
    display: flex;
    flex-direction: column;
    align-items: center;
    text-align: center;
  }
  
  .reset-icon {
    font-size: 3rem;
    margin-bottom: 1rem;
  }
  
  .reset-title {
    font-size: 1.25rem;
    font-weight: 600;
    margin-bottom: 1.5rem;
    color: var(--color-warning);
  }
  
  .reset-info {
    margin-bottom: 2rem;
    background-color: var(--color-bg-element-alt);
    border-radius: var(--border-radius);
    padding: 1.25rem;
    border: 1px solid var(--color-border);
    width: 100%;
    text-align: left;
  }
  
  .reset-info p {
    margin-bottom: 1rem;
    color: var(--color-text-secondary);
    line-height: 1.5;
  }
  
  .user-card {
    display: flex;
    align-items: center;
    gap: 1rem;
    padding: 1rem;
    background-color: var(--color-bg-main);
    border-radius: var(--border-radius);
    border: 1px solid var(--color-border);
  }
  
  .user-avatar-small {
    width: 40px;
    height: 40px;
    border-radius: 50%;
    background-color: var(--color-primary);
    color: var(--color-bg-main);
    display: flex;
    align-items: center;
    justify-content: center;
    font-weight: bold;
    font-size: 1.1rem;
    flex-shrink: 0;
  }
  
  .user-details-small {
    flex: 1;
  }
  
  .user-name-small {
    font-weight: 600;
    margin-bottom: 0.25rem;
  }
  
  .user-id-small {
    font-size: 0.9rem;
    color: var(--color-text-secondary);
    margin-bottom: 0.25rem;
  }
  
  .user-role-small {
    display: inline-block;
    font-size: 0.8rem;
    padding: 0.15rem 0.5rem;
    border-radius: 12px;
  }
  
  .user-role-small.estudiante {
    background-color: rgba(157, 190, 182, 0.2);
    color: var(--color-success);
  }
  
  .user-role-small.docente {
    background-color: rgba(101, 177, 193, 0.2);
    color: var(--color-info);
  }
  
  .user-role-small.admin {
    background-color: rgba(255, 189, 46, 0.2);
    color: var(--color-warning);
  }
  
  .confirmation-section {
    width: 100%;
    margin-top: 1rem;
  }
  
  .confirmation-text {
    margin-bottom: 1rem;
    text-align: left;
    color: var(--color-text-primary);
  }
  
  .field {
    margin-bottom: 1rem;
  }
  
  .input {
    background-color: var(--color-bg-main);
    border: 1px solid var(--color-border);
    color: var(--color-text-primary);
    border-radius: var(--border-radius-sm);
    padding: 0.5rem 0.75rem;
    height: 2.5rem;
    width: 100%;
    transition: border-color var(--transition-fast);
  }
  
  .input:focus {
    border-color: var(--color-border-focus);
    outline: none;
  }
  
  .input.is-danger {
    border-color: var(--color-danger);
  }
  
  .help.is-danger {
    color: var(--color-danger);
    font-size: 0.8rem;
    margin-top: 0.25rem;
    text-align: left;
  }
  </style>