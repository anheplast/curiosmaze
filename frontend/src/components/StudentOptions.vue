<!-- src/components/StudentOptions.vue -->
<template>
  <div class="student-options-container">
    <div class="logo-container">
      <img src="../../public/logo/Logo-CuriosMaze-40x40.png" alt="Logo" class="logo" />
    </div>

    <!-- Botón de cerrar sesión -->
    <button class="logout-button" @click="logout" title="Cerrar sesión">
      <i class="fas fa-sign-out-alt"></i>
    </button>

    <div class="options-header">
      <h1 class="title">
        <span class="title-icon">👋</span>
        ¡Hola, {{ studentName }}!
      </h1>
    </div>

    <div class="options-grid">
      <!-- Opción: Evaluaciones Anteriores -->
      <div class="option-card" @click="selectOption('history')" :class="{ 'pulse-animation': isHighlighted('history') }"
        @mouseover="highlightOption = 'history'" @mouseleave="highlightOption = null">
        <div class="option-icon">📝</div>
        <h2 class="option-title">Revisar evaluaciones anteriores</h2>
        <p class="option-description">
          Revisa los resultados, ejercicios y respuestas de tus evaluaciones pasadas
        </p>
        <div class="option-arrow">
          <span>👉</span>
        </div>
      </div>

      <!-- Opción: Ingresar a Evaluación -->
      <div class="option-card" @click="selectOption('new')" :class="{ 'pulse-animation': isHighlighted('new') }"
        @mouseover="highlightOption = 'new'" @mouseleave="highlightOption = null">
        <div class="option-icon">🚀</div>
        <h2 class="option-title">Ingresar a una evaluación</h2>
        <p class="option-description">
          Ingresa a una nueva evaluación usando el código proporcionado por tu profesor
        </p>
        <div class="option-arrow">
          <span>👉</span>
        </div>
      </div>
    </div>

    <!-- Ayuda y soporte -->
    <div class="help-section">
      <div class="help-icon">❓</div>
      <p>
        ¿Necesitas ayuda? Puedes contactar a tu profesor o
        <a :href="formUrl" target="_blank" rel="noopener noreferrer" class="help-link">acceder al formulario de
          ayuda</a>.
      </p>
    </div>
  </div>
</template>

<script>
import { ref, onMounted } from 'vue';
import { useStore } from 'vuex';
import { useRouter } from 'vue-router';

export default {
  name: 'StudentOptions',
  emits: ['select-option'],
  setup(props, { emit }) {
    const store = useStore();
    const router = useRouter();
    const studentName = ref('Estudiante');
    const highlightOption = ref(null);

    // Obtener URL del formulario desde las variables de entorno
    const formUrl = ref(import.meta.env.VITE_HELP_FORM_URL || '#');

    onMounted(() => {
      // Obtener nombre del estudiante del store
      studentName.value = store.getters['auth/userName'] || 'Estudiante';
    });

    const selectOption = (option) => {
      if (option === 'history') {
        router.push('/estudiante/historial-evaluaciones');
      } else if (option === 'new') {
        emit('select-option', option);
      }
    };

    const isHighlighted = (option) => {
      return highlightOption.value === option;
    };

    // Función para cerrar sesión
    const logout = () => {
      store.dispatch('auth/logout').then(() => {
        router.push('/');
      });
    };

    return {
      studentName,
      highlightOption,
      selectOption,
      isHighlighted,
      logout,
      formUrl
    };
  }
}
</script>

<style scoped>
:root {
  --color-bg-main: #1C1C21;
  --color-bg-element: #2A2A30;
  --color-bg-element-alt: #25252A;
  --color-bg-element-hover: #32323A;
  --color-border: #36363c;
  --color-border-focus: #7E91FF;
  --color-text-primary: #ffffff;
  --color-text-secondary: #e0e0e0;
  --color-text-muted: #9090A0;

  /* Paleta de colores */
  --color-primary: #EBB300;
  --color-primary-light: #FFD03F;
  --color-primary-dark: #C89500;
  --color-secondary: #6B7280;
  --color-success: #9DBEB6;
  --color-info: #65B1C1;
  --color-warning: #FFBD2E;
  --color-danger: #FF6B6B;
}

.student-options-container {
  width: 100%;
  max-width: 1000px;
  background-color: var(--color-bg-element, #2A2A30);
  border-radius: 16px;
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.3);
  padding: 2rem;
  display: flex;
  flex-direction: column;
  gap: 2rem;
  border-top: 5px solid var(--color-primary, #EBB300);
  animation: fadeIn 0.5s ease-out;
  position: relative;
  padding-top: 3.5rem;
  /* Asegura espacio suficiente para el logo */
}

/* Botón de cerrar sesión */
.logout-button {
  position: absolute;
  top: 1.5rem;
  right: 1.5rem;
  background-color: var(--color-bg-element-alt, #25252A);
  color: var(--color-text-muted, #9090A0);
  border: 1px solid var(--color-border, #36363c);
  cursor: pointer;
  width: 40px;
  height: 40px;
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.3s ease;
  font-size: 1.25rem;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.logout-button:hover {
  color: #FF6B6B;
  background-color: rgba(255, 107, 107, 0.1);
  border-color: #FF6B6B;
  transform: translateY(-2px);
  box-shadow: 0 4px 8px rgba(255, 107, 107, 0.2);
}

.options-header {
  text-align: center;
  margin-bottom: 1rem;
}

.logo-container {
  position: absolute;
  top: 1.5rem;
  left: 1.5rem;
  width: 60px;
  height: 60px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.logo {
  width: 40px;
  height: auto;
}

.title {
  font-size: 2rem;
  color: var(--color-text-primary, #ffffff);
  margin-bottom: 0.5rem;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.75rem;
}

.title-icon {
  font-size: 2rem;
  transform: rotate(-15deg);
}

.subtitle {
  font-size: 1.1rem;
  color: var(--color-text-secondary, #e0e0e0);
  margin-bottom: 2rem;
}

.options-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 2rem;
}

.option-card {
  background-color: var(--color-bg-element-alt, #25252A);
  border-radius: 12px;
  padding: 2rem;
  cursor: pointer;
  transition: all 0.3s ease;
  position: relative;
  border: 2px solid transparent;
  min-height: 280px;
  display: flex;
  flex-direction: column;
  align-items: center;
  text-align: center;
}

.option-card:hover {
  transform: translateY(-5px);
  box-shadow: 0 10px 20px rgba(0, 0, 0, 0.2);
  border-color: var(--color-primary, #EBB300);
  background-color: var(--color-bg-element-hover, #32323A);
}

.option-icon {
  font-size: 3rem;
  margin-bottom: 1.5rem;
}

.option-title {
  font-size: 1.5rem;
  color: var(--color-primary, #EBB300);
  margin-bottom: 1rem;
}

.option-description {
  color: var(--color-text-secondary, #e0e0e0);
  font-size: 1rem;
  margin-bottom: 1.5rem;
  line-height: 1.5;
}

.option-arrow {
  position: absolute;
  bottom: 1.5rem;
  right: 1.5rem;
  font-size: 1.5rem;
  opacity: 0;
  transition: all 0.3s ease;
  transform: translateX(-10px);
}

.option-card:hover .option-arrow {
  opacity: 1;
  transform: translateX(0);
}

.help-section {
  display: flex;
  align-items: center;
  gap: 1rem;
  background-color: rgba(101, 177, 193, 0.1);
  padding: 1rem;
  border-radius: 8px;
  border-left: 4px solid var(--color-info, #65B1C1);
}

.help-icon {
  font-size: 1.5rem;
  color: var(--color-info, #65B1C1);
}

.help-section p {
  color: var(--color-text-secondary, #e0e0e0);
  font-size: 0.9rem;
  margin: 0;
}

/* Animación de pulso para las opciones destacadas */
.pulse-animation .option-icon {
  animation: pulse 1.5s infinite;
}

@keyframes pulse {
  0% {
    transform: scale(1);
  }

  50% {
    transform: scale(1.1);
  }

  100% {
    transform: scale(1);
  }
}

@keyframes fadeIn {
  from {
    opacity: 0;
    transform: translateY(20px);
  }

  to {
    opacity: 1;
    transform: translateY(0);
  }
}

/* Responsive */
@media (max-width: 768px) {
  .student-options-container {
    padding: 1.5rem;
  }

  .options-grid {
    grid-template-columns: 1fr;
  }

  .option-card {
    min-height: 220px;
  }

  .title {
    font-size: 1.5rem;
  }

  .subtitle {
    font-size: 1rem;
  }
}

/* Estilos para el link al formulario */
.help-link {
  color: var(--color-primary, #EBB300);
  text-decoration: underline;
  transition: all 0.2s ease;
}

.help-link:hover {
  color: var(--color-primary-light, #FFD03F);
  text-decoration: none;
}
</style>