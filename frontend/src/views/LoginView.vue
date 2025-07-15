<!-- src/views/LoginView.vue -->
<template>
  <div class="login-view">
    <!-- Fondo -->
    <BackgroundLogin class="background-layer" />

    <div class="login-box-container">
      <LoginBox />
    </div>

    <!-- Efecto de ruido (estará por encima de todo) -->
    <EffectNoise /> 
  </div>
</template>

<script setup>
import BackgroundLogin from '@/components/BackgroundLogin/BackgroundLogin.vue';
import EffectNoise from '@/components/EffectNoise.vue';
import LoginBox from '@/components/auth/LoginBox.vue';
</script>

<style scoped>
/* =================== CONTENEDOR PRINCIPAL =================== */
.login-view {
  position: relative;
  width: 100vw;
  height: 100vh;
  overflow: hidden;
}

/* =================== CAPA DE FONDO =================== */
.background-layer {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  z-index: 1;
}

/* =================== CONTENEDOR DEL LOGIN BOX =================== */
.login-box-container {
  position: absolute;
  z-index: 100;
  width: 100%;
  height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  pointer-events: none;
}

.login-box-container > * {
  pointer-events: auto;
}
</style>