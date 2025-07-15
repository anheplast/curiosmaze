// src/main.js
import './assets/main.css'
import './assets/style_variables.css'
import './assets/bulma.min.css'

import { createApp } from 'vue'
import App from './App.vue'
import router from './router'
import store from './store'


import judge0Service from './services/judge0Service'
import '@fortawesome/fontawesome-free/css/all.css'

// Componente DevelopmentOverlay
import DevelopmentOverlay from './components/DevelopmentOverlay.vue'
// Componente de efecto de ruido
import EffectNoise from './components/EffectNoise.vue'

// judge0Service disponible globalmente para compatibilidad
window.judgeService = judge0Service;      // Para código que usa el nombre anterior
window.judge0Service = judge0Service;     // Para código que usa el nombre nuevo

const app = createApp(App)

// Registrar componentes globales
app.component('DevelopmentOverlay', DevelopmentOverlay)
app.component('EffectNoise', EffectNoise)

app.use(router)
app.use(store)

app.mount('#app')
