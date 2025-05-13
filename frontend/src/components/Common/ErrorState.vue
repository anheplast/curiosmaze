<!-- components/common/ErrorState.vue -->
<template>
    <div class="error-container">
      <div class="error-icon">⚠️</div>
      <h2 class="error-title">{{ title }}</h2>
      <p class="error-message">{{ details }}</p>
      <div class="error-actions">
        <button class="button retry-btn" @click="$emit('retry')">
          <span class="button-icon">🔄</span>
          <span>Reintentar</span>
        </button>
      </div>
    </div>
  </template>
  
  <script>
  export default {
    name: 'ErrorState',
    props: {
      title: {
        type: String,
        default: 'Ocurrió un error'
      },
      details: {
        type: String,
        default: 'No se pudo cargar la información solicitada. Por favor, intente nuevamente.'
      }
    }
  };
  </script>
  
  <style scoped>
  .error-container {
    background-color: rgba(255, 107, 107, 0.1);
    border: 2px solid var(--color-danger);
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
    color: var(--color-danger);
  }
  
  .error-message {
    margin-bottom: 1.5rem;
    color: var(--color-text-secondary);
    max-width: 600px;
  }
  
  .error-actions {
    display: flex;
    justify-content: center;
  }
  
  .retry-btn {
    background-color: var(--color-bg-main);
    color: var(--color-text-primary);
    border: 1px solid var(--color-primary);
    display: flex;
    align-items: center;
    gap: 0.5rem;
    padding: 0.5rem 1.25rem;
    border-radius: var(--border-radius-sm);
    transition: all var(--transition-fast);
  }
  
  .retry-btn:hover {
    background-color: var(--color-primary);
    color: var(--color-bg-main);
  }
  
  .button-icon {
    font-size: 1.2rem;
  }
  </style>