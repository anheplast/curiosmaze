<!-- src/App.vue -->
<template>
  <!-- Enlaces a Google Fonts -->
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Charm:wght@400;700&family=Cookie&family=Monoton&display=swap" rel="stylesheet">

  <!-- Contenedor principal de la aplicación -->
  <div id="app">
    <!-- Router view donde se renderizarán las vistas -->
    <router-view></router-view>
    
    <!-- Efecto de ruido global que estará por encima de todo -->
    <EffectNoise />
  </div>
</template>

<script>
import EffectNoise from '@/components/EffectNoise.vue';

export default {
  name: 'App',
  components: {
    EffectNoise
  }
};
</script>

<style>
/* Estilos globales */
body, html {
  margin: 0;
  padding: 0;
  height: 100%;
  width: 100%;
}

#app {
  position: relative;
  min-height: 100vh;
  width: 100%;
}
</style>