// src/composables/useTheme.js
import { ref, onMounted, watch } from 'vue'

// Estado global del tema
const currentTheme = ref('auto')
const systemTheme = ref('dark')

// Detectar el tema del sistema
const detectSystemTheme = () => {
  if (typeof window !== 'undefined' && window.matchMedia) {
    return window.matchMedia('(prefers-color-scheme: light)').matches ? 'light' : 'dark'
  }
  return 'dark'
}

// Aplicar el tema al documento
const applyTheme = (theme) => {
  const html = document.documentElement
  
  if (theme === 'auto') {
    // Quitar atributo data-theme para usar la detección automática
    html.removeAttribute('data-theme')
  } else {
    // Aplicar tema específico
    html.setAttribute('data-theme', theme)
  }
  
  // Agregar clase para transiciones suaves
  html.classList.add('theme-transition')
}

// Función principal del composable
export function useTheme() {
  // Cambiar tema
  const setTheme = (theme) => {
    if (!['auto', 'light', 'dark'].includes(theme)) {
      console.warn(`Tema inválido: ${theme}. Usando 'auto' por defecto.`)
      theme = 'auto'
    }
    
    currentTheme.value = theme
    applyTheme(theme)
    
    // Guardar en localStorage
    try {
      if (theme === 'auto') {
        localStorage.removeItem('theme')
      } else {
        localStorage.setItem('theme', theme)
      }
    } catch (error) {
      console.warn('No se pudo guardar el tema en localStorage:', error)
    }
  }
  
  // Alternar entre claro y oscuro
  const toggleTheme = () => {
    const newTheme = currentTheme.value === 'dark' ? 'light' : 'dark'
    setTheme(newTheme)
  }
  
  // Obtener el tema efectivo actual
  const getEffectiveTheme = () => {
    if (currentTheme.value === 'auto') {
      return systemTheme.value
    }
    return currentTheme.value
  }
  
  // Inicializar tema
  const initTheme = () => {
    // Detectar tema del sistema
    systemTheme.value = detectSystemTheme()
    
    // Cargar tema guardado
    let savedTheme = 'auto'
    try {
      savedTheme = localStorage.getItem('theme') || 'auto'
    } catch (error) {
      console.warn('No se pudo leer el tema desde localStorage:', error)
    }
    
    setTheme(savedTheme)
    
    // Escuchar cambios en el tema del sistema
    if (typeof window !== 'undefined' && window.matchMedia) {
      const mediaQuery = window.matchMedia('(prefers-color-scheme: light)')
      const handleSystemThemeChange = (e) => {
        systemTheme.value = e.matches ? 'light' : 'dark'
        // Si está en modo auto, re-aplicar el tema
        if (currentTheme.value === 'auto') {
          applyTheme('auto')
        }
      }
      
      // Agregar listener
      mediaQuery.addEventListener('change', handleSystemThemeChange)
      
      // Cleanup function (se puede usar en onUnmounted si es necesario)
      return () => {
        mediaQuery.removeEventListener('change', handleSystemThemeChange)
      }
    }
  }
  
  // Auto-inicializar cuando se monta el composable
  onMounted(initTheme)
  
  return {
    currentTheme,
    systemTheme,
    setTheme,
    toggleTheme,
    getEffectiveTheme,
    initTheme
  }
}