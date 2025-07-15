<!-- src/components/BackgroundLogin/BackgroundLogin.vue -->
<template>
  <div class="background-login">
    <div id="container">
      <!-- Se generan 1599 tiles y se asigna el componente de icono correspondiente -->
      <div v-for="(TileIcon, index) in tiles" :key="index" class="tile">
        <component :is="TileIcon" class="icon" />
      </div>
    </div>
  </div>
</template>

<script setup>
import IconBug from '../icons/background/Icon_Bug.vue'
import IconGithub from '../icons/background/Icon_Github.vue'
import IconPython from '../icons/background/Icon_Python.vue'
import IconJavascript from '../icons/background/Icon_Javascript.vue'
import IconBash from '../icons/background/Icon_Bash.vue'
import IconLinux from '../icons/background/Icon_Linux.vue'
import IconCLanguage from '../icons/background/Icon_C.vue'

// Array con los componentes de los iconos 
const iconComponents = [
  IconBug,
  IconGithub,
  IconPython,
  IconJavascript,
  IconBash,
  IconLinux,
  IconCLanguage,
]

// Creamos un array de 1599 elementos que alterna los iconos
const tiles = Array.from({ length: 1599 }, (_, i) => iconComponents[i % iconComponents.length])
</script>

<style>
/* Estilos principales del fondo */
.background-login {
  height: 100vh;
  width: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  /* background aquí para cambiar el color de fondo principal */
  background: var(--color-backgroundlogin-main);
  overflow: hidden;
  perspective: 2000px;
  position: relative;
}

#container {
  width: 140rem;
  aspect-ratio: 1;
  display: grid;
  grid-template-rows: repeat(40, 1fr);
  grid-template-columns: repeat(40, 1fr);
  position: absolute;
  transform: rotateX(50deg) rotateY(-5deg) rotateZ(20deg) scale(1.25);
}

.tile {
  /* border-color aquí para cambiar el color de los bordes de los tiles */
  border: 1px solid var(--color-backgroundlogin-border);;
  transition: background-color 1500ms;
  position: relative;
  display: flex;
  align-items: center;
  justify-content: center;
}

.tile:hover {
  transition-duration: 0ms;
}

/* background-color en estas reglas para cambiar el color de fondo al hacer hover */
.tile:nth-child(4n):hover,
.tile:nth-child(4n + 1):hover,
.tile:nth-child(4n + 2):hover,
.tile:nth-child(4n + 3):hover,
.tile:nth-child(7n):hover,
.tile:nth-child(7n + 3):hover,
.tile:nth-child(7n + 5):hover,
.tile:nth-child(7n + 6):hover,
.tile:nth-child(11n + 1):hover,
.tile:nth-child(11n + 4):hover,
.tile:nth-child(11n + 7):hover,
.tile:nth-child(11n + 10):hover {
  background-color: var(--color-backgroundlogin-hover);;
}

.icon {
  opacity: 0;
  transition: opacity 0.3s ease;
  width: 35px;
  height: 35px;
  /* CAMBIAR COLOR: Agregar un filtro aquí para cambiar el color de los iconos */
  /* filter: invert(1); */ /* Descomentar para invertir los colores */
}

.tile:hover .icon {
  opacity: 1;
}
</style>