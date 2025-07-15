<!-- src/components/Common/ErrorState.vue -->
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
/* =================== CONTENEDOR PRINCIPAL =================== */
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

/* =================== ELEMENTOS DE ERROR =================== */
.error-icon {
  font-size: 3rem;
  margin-bottom: 1rem;
  color: var(--color-error);
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
  max-width: 600px;
  line-height: 1.5;
}

/* =================== ACCIONES =================== */
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
  cursor: pointer;
  font-weight: 500;
}

.retry-btn:hover {
  background-color: var(--color-primary);
  color: var(--color-bg-main);
  transform: translateY(-2px);
  box-shadow: var(--shadow-sm);
}

.button-icon {
  font-size: 1.2rem;
}
</style>