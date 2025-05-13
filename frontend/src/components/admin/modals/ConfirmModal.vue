<!-- components/admin/modals/ConfirmModal.vue -->
<template>
    <div class="modal is-active">
      <div class="modal-background" @click="$emit('cancel')"></div>
      <div class="modal-card">
        <header class="modal-card-head">
          <p class="modal-card-title">
            <span class="modal-title-icon">{{ icon }}</span>
            {{ title }}
          </p>
          <button class="delete" aria-label="close" @click="$emit('cancel')"></button>
        </header>
        
        <section class="modal-card-body">
          <div class="confirm-content">
            <div class="confirm-icon">{{ icon }}</div>
            <p class="confirm-message">{{ message }}</p>
  
            <div class="field" v-if="showRejectReason">
              <label class="label">Motivo del rechazo:</label>
              <div class="control">
                <textarea 
                  class="textarea" 
                  v-model="localRejectReason"
                  placeholder="Describa el motivo del rechazo"
                  @input="$emit('update:reject-reason', localRejectReason)"
                ></textarea>
              </div>
            </div>
          </div>
        </section>
        
        <footer class="modal-card-foot">
          <button class="button cancel-btn" @click="$emit('cancel')">Cancelar</button>
          <button class="button" :class="buttonClass" @click="$emit('confirm')">
            {{ buttonText }}
          </button>
        </footer>
      </div>
    </div>
  </template>
  
  <script>
  import { ref, watch } from 'vue';
  
  export default {
    name: 'ConfirmModal',
    props: {
      title: {
        type: String,
        required: true
      },
      message: {
        type: String,
        required: true
      },
      icon: {
        type: String,
        default: '❓'
      },
      buttonText: {
        type: String,
        default: 'Confirmar'
      },
      buttonClass: {
        type: String,
        default: 'is-primary'
      },
      showRejectReason: {
        type: Boolean,
        default: false
      },
      rejectReason: {
        type: String,
        default: ''
      }
    },
    setup(props, { emit }) {
      const localRejectReason = ref(props.rejectReason);
      
      // Mantener sincronizado el valor local con el prop
      watch(() => props.rejectReason, (newVal) => {
        localRejectReason.value = newVal;
      });
      
      return {
        localRejectReason
      };
    }
  };
  </script>
  
  <style scoped>
  .modal-card {
    background-color: var(--color-bg-element);
    border-radius: var(--border-radius);
    overflow: hidden;
    max-width: 500px;
    width: 90%;
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
  
  .modal-title-icon,
  .confirm-icon {
    font-size: 1.5rem;
  }
  
  .modal-card-body {
    background-color: var(--color-bg-element);
    padding: 2rem;
    color: var(--color-text-primary);
  }
  
  .confirm-content {
    text-align: center;
  }
  
  .confirm-icon {
    font-size: 3rem;
    margin-bottom: 1rem;
  }
  
  .confirm-message {
    font-size: 1.1rem;
    margin-bottom: 1.5rem;
    line-height: 1.5;
  }
  
  .modal-card-foot {
    background-color: var(--color-bg-element-alt);
    padding: 1.25rem;
    justify-content: center;
    border-top: 1px solid var(--color-border);
  }
  
  .cancel-btn {
    background-color: var(--color-bg-main);
    color: var(--color-text-primary);
    border: 1px solid var(--color-border);
    margin-right: 0.75rem;
  }
  
  .cancel-btn:hover {
    background-color: var(--color-bg-element-hover);
    color: var(--color-text-primary);
  }
  
  /* Estilos para los botones de confirmación */
  .confirm-approve-btn {
    background-color: var(--color-success);
    color: white;
    border: none;
  }
  
  .confirm-approve-btn:hover {
    background-color: var(--color-success);
    opacity: 0.9;
  }
  
  .confirm-reject-btn {
    background-color: var(--color-danger);
    color: white;
    border: none;
  }
  
  .confirm-reject-btn:hover {
    background-color: var(--color-danger);
    opacity: 0.9;
  }
  
  .confirm-deactivate-btn {
    background-color: var(--color-warning);
    color: var(--color-bg-main);
    border: none;
  }
  
  .confirm-deactivate-btn:hover {
    background-color: var(--color-warning);
    opacity: 0.9;
  }
  
  .confirm-delete-btn {
    background-color: var(--color-danger);
    color: white;
    border: none;
  }
  
  .confirm-delete-btn:hover {
    background-color: var(--color-danger);
    opacity: 0.9;
  }
  
  /* Campos de texto */
  .field {
    margin-top: 1.5rem;
    text-align: left;
  }
  
  .label {
    color: var(--color-text-primary);
    font-weight: 600;
    margin-bottom: 0.5rem;
  }
  
  .textarea {
    background-color: var(--color-bg-main);
    border: 1px solid var(--color-border);
    color: var(--color-text-primary);
    border-radius: var(--border-radius-sm);
    padding: 0.75rem;
    resize: vertical;
    min-height: 100px;
  }
  
  .textarea:focus {
    border-color: var(--color-primary);
    outline: none;
    box-shadow: 0 0 0 2px rgba(235, 179, 0, 0.2);
  }
  </style>