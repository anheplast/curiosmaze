<!-- src/App.vue -->
<!-- Contenedor principal de la aplicación -->
<template>
  <div id="app" class="theme-transition">
    <!-- Selector de tema flotante - ocultar en ejercicios -->
    <div class="theme-selector-wrapper" v-if="showThemeSelector && !isExerciseView">
      <ThemeSelector />
    </div>

    <router-view />
    <EffectNoise />
  </div>
</template>

<script>
import { ref, onMounted, computed } from 'vue'
import { useRoute } from 'vue-router'
import EffectNoise from '@/components/EffectNoise.vue';
import ThemeSelector from './components/Common/ThemeSelector.vue'
import { useTheme } from './composables/useTheme'

export default {
  name: 'App',
  components: {
    EffectNoise,
    ThemeSelector
  },
  setup() {
    const route = useRoute()
    const { initTheme } = useTheme()
    const showThemeSelector = ref(true)

    // Computed para detectar si estamos en vista de ejercicios
    const isExerciseView = computed(() => {
      return route.path.includes('/ejercicios') ||
        route.path.includes('/resolucion-ejercicios-practico') ||
        route.path.includes('/evaluation-access')
    })

    onMounted(() => {
      initTheme()
    })

    return {
      showThemeSelector,
      isExerciseView
    }
  }
}
</script>

<style>
/* Estilos globales */
* {
  box-sizing: border-box;
}

#app {
  font-family: Avenir, Helvetica, Arial, sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  background-color: var(--color-bg-main);
  color: var(--color-text-primary);
  min-height: 100vh;
}

/* Wrapper para el selector de tema flotante */
.theme-selector-wrapper {
  position: fixed;
  top: 20px;
  right: 20px;
  z-index: 9999;
  /* Temporal para pruebas - quitar después */
}

/* Sobrescribir algunos estilos de Bulma */
.box {
  background-color: var(--color-bg-element) !important;
  color: var(--color-text-primary) !important;
}

.button.is-primary {
  background-color: var(--color-primary) !important;
  border-color: var(--color-primary) !important;
  color: var(--color-bg-main) !important;
}

.button.is-primary:hover {
  background-color: var(--color-primary-dark) !important;
  border-color: var(--color-primary-dark) !important;
}

.input, .textarea, .select select {
  background-color: var(--color-bg-element) !important;
  border-color: var(--color-border) !important;
  color: var(--color-text-primary) !important;
}

.input:focus, .textarea:focus, .select select:focus {
  border-color: var(--color-border-focus) !important;
  box-shadow: 0 0 0 2px rgba(138, 79, 255, 0.25) !important;
}

.title {
  color: var(--color-text-primary) !important;
}

.subtitle {
  color: var(--color-text-secondary) !important;
}
</style>



