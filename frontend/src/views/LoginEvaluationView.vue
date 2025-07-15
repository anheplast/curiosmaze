<!-- src/views/LoginEvaluationView.vue -->
<template>
  <div class="evaluation-view">
    <!-- Botón para volver atrás -->
    <button class="back-button" @click="goBack" title="Volver al dashboard">
      <i class="fas fa-arrow-left"></i>
    </button>

    <!-- Botón de cerrar sesión -->
    <button class="logout-button" @click="logout" title="Cerrar sesión">
      <i class="fas fa-sign-out-alt"></i>
    </button>

    <!-- Selector de tema -->
    <div class="theme-selector-container">
      <theme-selector />
    </div>

    <EvaluationAccess @access-granted="startEvaluation" />
  </div>
</template>

<script>
import EvaluationAccess from '@/components/estudiantes/EvaluationAccess.vue';
import { useRouter } from 'vue-router';
import { useStore } from 'vuex';
import ThemeSelector from '@/components/Common/ThemeSelector.vue';

export default {
  name: 'LoginEvaluationView',
  components: {
    EvaluationAccess,
    ThemeSelector
  },
  setup() {
    const router = useRouter();
    const store = useStore();

    const startEvaluation = (accessKey) => {
      console.log('Acceso concedido con clave:', accessKey);
    }

    // Función para volver al dashboard de estudiante
    const goBack = () => {
      router.push('/estudiante/dashboard');
    }

    // Función para cerrar sesión
    const logout = () => {
      store.dispatch('auth/logout').then(() => {
        router.push('/');
      });
    }

    return {
      startEvaluation,
      goBack,
      logout
    }
  }
}
</script>

<style>
/* =================== ESTILOS GLOBALES =================== */
body {
  margin: 0;
  padding: 0;
  font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
  background-color: var(--color-bg-lighter);
}
</style>

<style scoped>
/* =================== CONTENEDOR PRINCIPAL =================== */
.evaluation-view {
  min-height: 100vh;
  width: 100%;
  position: relative;
}

/* =================== BOTÓN VOLVER ATRÁS =================== */
.back-button {
  position: absolute;
  top: 1.5rem;
  left: 1.5rem;
  background-color: var(--color-bg-element);
  color: var(--color-text-muted);
  border: 1px solid var(--color-border);
  cursor: pointer;
  width: 40px;
  height: 40px;
  border-radius: var(--border-radius);
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all var(--transition-smooth) ease;
  font-size: 1.25rem;
  z-index: 100;
  box-shadow: var(--shadow-sm);
}

.back-button:hover {
  color: var(--color-info);
  background-color: var(--color-info-bg);
  border-color: var(--color-info);
  transform: translateY(-2px);
  box-shadow: var(--shadow);
}

/* =================== BOTÓN CERRAR SESIÓN =================== */
.logout-button {
  position: absolute;
  top: 1.5rem;
  right: 1.5rem;
  background-color: var(--color-bg-element);
  color: var(--color-text-muted);
  border: 1px solid var(--color-border);
  cursor: pointer;
  width: 40px;
  height: 40px;
  border-radius: var(--border-radius);
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all var(--transition-smooth) ease;
  font-size: 1.25rem;
  z-index: 100;
  box-shadow: var(--shadow-sm);
}

.logout-button:hover {
  color: var(--color-error);
  background-color: var(--color-error-bg);
  border-color: var(--color-error);
  transform: translateY(-2px);
  box-shadow: var(--shadow);
}

/* =================== SELECTOR DE TEMA =================== */
.theme-selector-container {
  position: absolute;
  top: 1.5rem;
  right: 5rem; /* A la izquierda del logout button (40px + 16px gap) */
  z-index: 100;
}
</style>