<!-- src/components/DevelopmentOverlay.vue -->
<template>
    <div class="development-container">
      <!-- El contenido original se renderiza aquí -->
      <div class="content-wrapper" :class="{ 'blur-content': blurContent }">
        <slot></slot>
      </div>
      
      <!-- Superposición de desarrollo -->
      <div class="development-overlay" :style="{ opacity: opacity }">
        <div class="overlay-content">
          <div class="development-icon">{{ icon }}</div>
          <h2 class="development-title">{{ title }}</h2>
          <p class="development-message">{{ message }}</p>
          <div v-if="showDate" class="development-info">Disponible: {{ releaseDate }}</div>
          <button v-if="dismissable" class="dismiss-button" @click="dismiss">{{ dismissText }}</button>
        </div>
      </div>
    </div>
  </template>
  
  <script>
  export default {
    name: 'DevelopmentOverlay',
    props: {
      // Título principal de la superposición
      title: {
        type: String,
        default: 'En Desarrollo'
      },
      // Mensaje descriptivo
      message: {
        type: String,
        default: 'Esta funcionalidad se encuentra actualmente en desarrollo.'
      },
      // Icono que se mostrará (emoji)
      icon: {
        type: String,
        default: '🚧'
      },
      // Fecha estimada de lanzamiento (opcional)
      releaseDate: {
        type: String,
        default: '🤹‍♂️'
      },
      // Si se debe mostrar la fecha
      showDate: {
        type: Boolean,
        default: true
      },
      // Opacidad de la superposición (0-1)
      opacity: {
        type: Number,
        default: 0.9,
        validator: (value) => value >= 0 && value <= 1
      },
      // Si el contenido debajo debe desenfocarse
      blurContent: {
        type: Boolean,
        default: true
      },
      // Si se puede descartar la superposición
      dismissable: {
        type: Boolean,
        default: false
      },
      // Texto del botón para descartar
      dismissText: {
        type: String,
        default: 'Entendido'
      }
    },
    methods: {
      dismiss() {
        this.$emit('dismissed');
      }
    }
  }
  </script>
  
  <style scoped>
  /* Variables de color basadas en ManageEvaluations */
  :root {
    --color-bg-main: #1C1C21;
    --color-bg-element: #2A2A30;
    --color-border: #36363c;
    --color-text-primary: #ffffff;
    --color-text-secondary: #e0e0e0;
    --color-primary: #EBB300;
    --color-primary-light: #FFD03F;
    --color-primary-dark: #C89500;
    --color-warning: #FFBD2E;
    --border-radius-lg: 12px;
    --border-radius: 8px;
    --shadow-lg: 0 8px 16px rgba(0, 0, 0, 0.2);
    --transition-smooth: 0.3s;
  }
  
  .development-container {
    position: relative;
    width: 100%;
    height: 100%;
    overflow: hidden;
  }
  
  .content-wrapper {
    width: 100%;
    height: 100%;
    transition: filter var(--transition-smooth);
  }
  
  .content-wrapper.blur-content {
    filter: blur(4px);
  }
  
  .development-overlay {
    position: absolute;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    background-color: rgba(28, 28, 33, 0.9);
    display: flex;
    align-items: center;
    justify-content: center;
    z-index: 1000;
    backdrop-filter: blur(8px);
    transition: all var(--transition-smooth);
  }
  
  .overlay-content {
    max-width: 500px;
    text-align: center;
    background-color: var(--color-bg-element);
    padding: 2.5rem;
    border-radius: var(--border-radius-lg);
    box-shadow: var(--shadow-lg);
    border-top: 4px solid var(--color-primary);
    animation: fadeIn 0.5s ease-out;
  }
  
  .development-icon {
    font-size: 4rem;
    margin-bottom: 1.5rem;
    animation: bounce 1.5s infinite alternate;
  }
  
  .development-title {
    font-size: 1.75rem;
    font-weight: 600;
    color: var(--color-text-primary);
    margin-bottom: 1rem;
  }
  
  .development-message {
    font-size: 1.1rem;
    color: var(--color-text-secondary);
    margin-bottom: 1.5rem;
    line-height: 1.6;
  }
  
  .development-info {
    display: inline-block;
    background-color: rgba(235, 179, 0, 0.15);
    color: var(--color-primary);
    font-weight: 600;
    padding: 0.5rem 1rem;
    border-radius: 20px;
    margin-bottom: 1.5rem;
    border: 1px solid var(--color-primary-dark);
  }
  
  .dismiss-button {
    background-color: var(--color-primary);
    color: var(--color-bg-main);
    border: none;
    padding: 0.75rem 1.75rem;
    border-radius: var(--border-radius);
    font-weight: 600;
    cursor: pointer;
    transition: all 0.2s;
  }
  
  .dismiss-button:hover {
    background-color: var(--color-primary-light);
    transform: translateY(-2px);
    box-shadow: 0 4px 8px rgba(235, 179, 0, 0.3);
  }
  
  @keyframes fadeIn {
    from {
      opacity: 0;
      transform: translateY(-20px);
    }
    to {
      opacity: 1;
      transform: translateY(0);
    }
  }
  
  @keyframes bounce {
    from {
      transform: translateY(0);
    }
    to {
      transform: translateY(-10px);
    }
  }
  
  /* Responsive */
  @media screen and (max-width: 768px) {
    .overlay-content {
      max-width: 90%;
      padding: 2rem 1.5rem;
    }
    
    .development-icon {
      font-size: 3rem;
    }
    
    .development-title {
      font-size: 1.5rem;
    }
    
    .development-message {
      font-size: 1rem;
    }
  }
  </style>