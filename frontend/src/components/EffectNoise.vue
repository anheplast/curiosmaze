<!-- src/components/EffectNoise.vue -->
<template>
  <div class="noise-overlay"></div>
</template>

<style scoped>
.noise-overlay {
  position: fixed;
  top: 0;
  left: 0;
  width: 100vw;
  height: 100vh;
  background-image: url("../../public/effect_noise.avif");
  background-size: 200px;
  background-repeat: repeat;
  pointer-events: none; /* Asegura que no interfiera con interacciones */
  z-index: 99999; /* Valor extremadamente alto para estar por encima de todo */
  opacity: 0.3; /* Opacidad ajustable para controlar la intensidad del efecto */
}
</style>