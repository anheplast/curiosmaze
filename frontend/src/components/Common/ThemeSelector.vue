<!-- src/components/Common/ThemeSelector.vue -->
<template>
  <div class="theme-selector">
    <button 
      @click="toggleTheme"
      class="theme-toggle"
      :title="`Cambiar a tema ${nextThemeLabel}`"
      :aria-label="`Tema actual: ${currentThemeLabel}. Clic para cambiar a ${nextThemeLabel}`"
    >
      <span class="theme-icon">{{ currentIcon }}</span>
      <span v-if="showLabel" class="theme-label">{{ currentThemeLabel }}</span>
    </button>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { useTheme } from '@/composables/useTheme'

// Props
defineProps({
  showLabel: {
    type: Boolean,
    default: false
  }
})

// Composable de tema
const { currentTheme, getEffectiveTheme, toggleTheme } = useTheme()

// Computed properties para los iconos y etiquetas
const currentIcon = computed(() => {
  const effectiveTheme = getEffectiveTheme()
  const icons = {
    auto: '🌓',
    light: '☀️',
    dark: '🌙'
  }
  
  // Si está en auto, mostrar el icono del tema efectivo pero con indicador
  if (currentTheme.value === 'auto') {
    return '🌓' // Icono específico para auto
  }
  
  return icons[effectiveTheme] || '🌓'
})

const currentThemeLabel = computed(() => {
  const labels = {
    auto: 'Auto',
    light: 'Claro',
    dark: 'Oscuro'
  }
  return labels[currentTheme.value] || 'Auto'
})

const nextThemeLabel = computed(() => {
  const effectiveTheme = getEffectiveTheme()
  return effectiveTheme === 'dark' ? 'claro' : 'oscuro'
})
</script>

<style scoped>
.theme-selector {
  display: inline-block;
}

.theme-toggle {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.5rem 0.75rem;
  background-color: var(--color-bg-element);
  border: 1px solid var(--color-border);
  border-radius: var(--border-radius);
  color: var(--color-text-primary);
  cursor: pointer;
  transition: all var(--transition-fast);
  font-size: 0.9rem;
  min-width: 2.5rem;
  min-height: 2.5rem;
  justify-content: center;
}

.theme-toggle:hover {
  background-color: var(--color-bg-element-hover);
  border-color: var(--color-border-focus);
  transform: translateY(-1px);
  box-shadow: var(--shadow);
}

.theme-toggle:active {
  transform: translateY(0);
  box-shadow: var(--shadow-sm);
}

.theme-icon {
  font-size: 1.1rem;
  line-height: 1;
  display: flex;
  align-items: center;
  justify-content: center;
}

.theme-label {
  font-weight: 500;
  white-space: nowrap;
  font-size: 0.85rem;
}

/* Variante compacta para espacios pequeños */
.theme-selector.compact .theme-toggle {
  padding: 0.4rem;
  min-width: 2.2rem;
  min-height: 2.2rem;
}

.theme-selector.compact .theme-icon {
  font-size: 1rem;
}

/* Responsivo */
@media (max-width: 768px) {
  .theme-toggle {
    min-width: 2.2rem;
    min-height: 2.2rem;
    padding: 0.4rem;
  }
  
  .theme-label {
    display: none; /* Ocultar label en móviles */
  }
  
  .theme-icon {
    font-size: 1rem;
  }
}

/* Estados de focus para accesibilidad */
.theme-toggle:focus {
  outline: none;
  box-shadow: 0 0 0 2px var(--color-primary);
}

.theme-toggle:focus:not(:focus-visible) {
  box-shadow: var(--shadow);
}
</style>