import './assets/main.css'
import './assets/bulma.min.css'

import { createApp } from 'vue'
import App from './App.vue'
import router from './router'
import store from './store'


import judgeService from './api/judgeService'
import '@fortawesome/fontawesome-free/css/all.min.css'

// Componente DevelopmentOverlay
import DevelopmentOverlay from './components/DevelopmentOverlay.vue'
// Componente de efecto de ruido
import EffectNoise from './components/EffectNoise.vue'

// judgeService globalmente para uso en evaluationsService
window.judgeService = judgeService;

const app = createApp(App)

// Registrar componentes globales
app.component('DevelopmentOverlay', DevelopmentOverlay)
app.component('EffectNoise', EffectNoise)

app.use(router)
app.use(store)

app.mount('#app')
