<!-- views/TheoricExercises.vue -->
<template>
  <!-- Simplemente queda como una idea futura -->
  <DevelopmentOverlay>
    <div class="exercises-container">
      <!-- Navbar -->
      <ExercisesNavbar />
      
      <!-- Contenido principal -->
      <div class="main-content">
        <!-- Panel izquierdo (área oscura) -->
        <div class="left-panel">
          <!-- Este es el área donde iría el contenido del ejercicio -->
        </div>
        
        <!-- Panel derecho con navegación y botones -->
        <div class="right-panel">
          <!-- Sección Teórico -->
          <div class="section-header">
            <div class="header-spacer"></div>
            <div class="header-title">Teorico</div>
            <div class="header-spacer"></div>
          </div>
          
          <!-- Botones numéricos para sección teórica - Fila 1 -->
          <div class="buttons-row">
            <button v-for="n in 6" :key="`teorico-row1-${n}`" class="number-button">{{ n }}</button>
          </div>
          
          <!-- Botones numéricos para sección teórica - Fila 2 -->
          <div class="buttons-row">
            <button v-for="n in 6" :key="`teorico-row2-${n}`" class="number-button">1</button>
          </div>
          
          <!-- Botones numéricos para sección teórica - Fila 3 -->
          <div class="buttons-row">
            <button v-for="n in 6" :key="`teorico-row3-${n}`" class="number-button">1</button>
          </div>
          
          <!-- Separador -->
          <div class="section-divider"></div>
          
          <!-- Sección Práctico -->
          <div class="section-header">
            <div class="header-spacer"></div>
            <div class="header-title">Practico</div>
            <div class="header-spacer"></div>
          </div>
          
          <!-- Botones numéricos para sección práctica - Fila 1 -->
          <div class="buttons-row">
            <button v-for="n in 6" :key="`practico-row1-${n}`" class="number-button">{{ n }}</button>
          </div>
          
          <!-- Botones numéricos para sección práctica - Fila 2 -->
          <div class="buttons-row">
            <button v-for="n in 6" :key="`practico-row2-${n}`" class="number-button">1</button>
          </div>
          
          <!-- Botones numéricos para sección práctica - Fila 3 -->
          <div class="buttons-row">
            <button v-for="n in 6" :key="`practico-row3-${n}`" class="number-button">1</button>
          </div>
          
          <!-- Sección inferior con botón de idea y enviar -->
          <div class="bottom-section">
            <div class="idea-button">
              <button class="icon-button">
                <span class="lightbulb-icon">💡</span>
              </button>
            </div>
            <div class="submit-button-container">
              <button class="submit-button">Enviar</button>
            </div>
          </div>
        </div>
      </div>
    </div>
  </DevelopmentOverlay>
  </template>
  
  <script>
  import { defineComponent } from 'vue'
  import ExercisesNavbar from '@/components/Common/ExercisesNavbar.vue'
  
  export default defineComponent({
    name: 'TheoricExercises',
    components: {
      ExercisesNavbar
    },
    setup() {
      return {}
    }
  })
  </script>
  
  <style scoped>
  .exercises-container {
    display: flex;
    flex-direction: column;
    height: 100vh;
    width: 100%;
    background-color: #000;
    color: white;
  }
  
  .main-content {
    display: flex;
    flex: 1;
  }
  
  .left-panel {
    flex: 1;
    background-color: #11a159;
    border-right: 1px solid #333;
  }
  
  .right-panel {
    width: 280px;
    background-color: #000;
    display: flex;
    flex-direction: column;
    border-left: 1px solid #444;
  }
  
  .section-header {
    display: flex;
    align-items: center;
    padding: 5px 0;
    border-top: 1px solid #444;
    border-bottom: 1px solid #444;
  }
  
  .header-spacer {
    flex: 1;
  }
  
  .header-title {
    padding: 5px 10px;
    text-align: center;
    font-size: 16px;
  }
  
  .buttons-row {
    display: flex;
    justify-content: space-around;
    padding: 8px 5px;
  }
  
  .number-button {
    width: 36px;
    height: 36px;
    border-radius: 50%;
    background-color: #111;
    color: #FFD700;
    border: 2px solid #8B4513;
    font-weight: bold;
    display: flex;
    align-items: center;
    justify-content: center;
    margin: 0 2px;
    cursor: pointer;
  }
  
  .number-button:hover {
    background-color: #222;
  }
  
  .section-divider {
    height: 10px;
    background-color: #000;
  }
  
  .bottom-section {
    margin-top: auto;
    display: flex;
    border-top: 1px solid #444;
  }
  
  .idea-button {
    width: 60px;
    height: 60px;
    display: flex;
    align-items: center;
    justify-content: center;
    border-right: 1px solid #444;
  }
  
  .icon-button {
    width: 40px;
    height: 40px;
    border-radius: 50%;
    background-color: #111;
    border: none;
    cursor: pointer;
    display: flex;
    align-items: center;
    justify-content: center;
  }
  
  .lightbulb-icon {
    font-size: 20px;
  }
  
  .submit-button-container {
    flex: 1;
    display: flex;
    align-items: center;
    justify-content: center;
  }
  
  .submit-button {
    padding: 8px 16px;
    background-color: darkgreen;
    color: white;
    border: none;
    border-radius: 4px;
    cursor: pointer;
    font-weight: bold;
  }
  
  .submit-button:hover {
    background-color: #006400;
  }
  </style>