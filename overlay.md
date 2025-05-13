# Guía de uso de DevelopmentOverlay.vue

## Índice

* [Introducción](#introducción)
* [Instalación](#instalación)
* [Propiedades](#propiedades)
* [Eventos](#eventos)
* [Ejemplos de uso](#ejemplos-de-uso)

  * [Uso básico](#uso-básico)
  * [Uso avanzado](#uso-avanzado)
  * [Uso con localStorage](#uso-con-localstorage)
  * [Uso condicional](#uso-condicional)
* [Personalizaciones](#personalizaciones)
* [Buenas prácticas](#buenas-prácticas)
* [Solución de problemas](#solución-de-problemas)
* [Ejemplos prácticos para CuriosMaze](#ejemplos-prácticos-para-curiosmaze)
* [Conclusión](#conclusión)

---

## Introducción

`DevelopmentOverlay` es un componente Vue que te permite marcar fácilmente cualquier sección de tu aplicación como "en desarrollo". Muestra una superposición elegante que informa a los usuarios que una característica o sección específica está siendo trabajada.

**Características principales**:

* ⚡ Fácil de implementar
* 🎨 Altamente personalizable
* 📱 Totalmente responsive
* 🔔 Eventos para interacción del usuario
* 🎯 Diseñado para CuriosMaze

---

## Instalación

### Registro global

```javascript
// main.js
import { createApp } from 'vue'
import App from './App.vue'
import DevelopmentOverlay from './components/DevelopmentOverlay.vue'

const app = createApp(App)
app.component('DevelopmentOverlay', DevelopmentOverlay)
app.mount('#app')
```

### Registro local

```vue
<script>
import DevelopmentOverlay from '@/components/DevelopmentOverlay.vue'

export default {
  components: {
    DevelopmentOverlay
  }
}
</script>
```

---

## Propiedades

| Propiedad     | Tipo    | Valor por defecto                                              | Descripción                               |
| ------------- | ------- | -------------------------------------------------------------- | ----------------------------------------- |
| `title`       | String  | `"En Desarrollo"`                                              | Título principal de la superposición      |
| `message`     | String  | `"Esta funcionalidad se encuentra actualmente en desarrollo."` | Mensaje descriptivo                       |
| `icon`        | String  | `"🚧"`                                                         | Emoji o símbolo que se muestra            |
| `releaseDate` | String  | `"Próximamente"`                                               | Fecha estimada de lanzamiento             |
| `showDate`    | Boolean | `true`                                                         | Si debe mostrarse la información de fecha |
| `opacity`     | Number  | `0.9`                                                          | Opacidad de la superposición (0-1)        |
| `blurContent` | Boolean | `true`                                                         | Si el contenido debe estar desenfocado    |
| `dismissable` | Boolean | `false`                                                        | Si se puede descartar la notificación     |
| `dismissText` | String  | `"Entendido"`                                                  | Texto del botón de descarte               |

---

## Eventos

| Evento      | Payload | Descripción                                        |
| ----------- | ------- | -------------------------------------------------- |
| `dismissed` | —       | Emitido cuando el usuario descarta la notificación |

---

## Ejemplos de uso

### Uso básico

```vue
<template>
  <DevelopmentOverlay>
    <YourComponent />
  </DevelopmentOverlay>
</template>
```

### Uso avanzado

```vue
<template>
  <DevelopmentOverlay
    title="Estadísticas Avanzadas"
    message="Estamos desarrollando un dashboard con métricas en tiempo real."
    icon="📊"
    releaseDate="Junio 2025"
    :opacity="0.85"
    :dismissable="true"
    dismissText="Ver avance"
    @dismissed="handleDismiss">

    <StatsDashboard />
  </DevelopmentOverlay>
</template>

<script>
export default {
  methods: {
    handleDismiss() {
      console.log('Usuario descartó la notificación')
    }
  }
}
</script>
```

### Uso con localStorage

```vue
<template>
  <div v-if="!hasSeenDevNotice">
    <DevelopmentOverlay
      title="Nuevo Módulo de Reportes"
      message="Explora nuestras nuevas capacidades de generación de reportes."
      icon="📑"
      :dismissable="true"
      @dismissed="markAsSeen">

      <ReportsModule />
    </DevelopmentOverlay>
  </div>

  <ReportsModule v-else />
</template>

<script>
export default {
  data() {
    return { hasSeenDevNotice: false }
  },
  mounted() {
    this.hasSeenDevNotice = localStorage.getItem('reports_dev_notice') === 'true'
  },
  methods: {
    markAsSeen() {
      localStorage.setItem('reports_dev_notice', 'true')
      this.hasSeenDevNotice = true
    }
  }
}
</script>
```

### Uso condicional

```vue
<template>
  <div>
    <DevelopmentOverlay v-if="isDevEnv">
      <BetaFeature />
    </DevelopmentOverlay>

    <BetaFeature v-else />
  </div>
</template>

<script>
export default {
  computed: {
    isDevEnv() {
      return import.meta.env.MODE !== 'production'
    }
  }
}
</script>
```

---

## Personalizaciones

### Colores personalizados

```vue
<template>
  <DevelopmentOverlay class="custom-overlay">
    <YourComponent />
  </DevelopmentOverlay>
</template>

<style>
.custom-overlay .development-overlay {
  --color-primary: #FF6B6B;
  --color-primary-light: #FF8E8E;
  --color-primary-dark: #CC5555;
}
</style>
```

### Animaciones personalizadas

```css
@keyframes customFadeIn {
  from { opacity: 0; transform: scale(0.9); }
  to   { opacity: 1; transform: scale(1);   }
}

.custom-overlay .overlay-content {
  animation: customFadeIn 0.3s ease-out;
}
```

---

## Buenas prácticas

1. **Ubicación estratégica**

   ```vue
   <!-- ✅ Buena práctica -->
   <sections>
     <header-section />
     <DevelopmentOverlay title="Sección Beta">
       <beta-feature-section />
     </DevelopmentOverlay>
     <stable-section />
   </sections>
   ```

2. **Mensajes claros**

   ```vue
   <!-- ✅ Buena práctica -->
   <DevelopmentOverlay
     title="Sistema de Chat en Tiempo Real"
     message="Estamos implementando un chat en tiempo real para consultas entre docentes y estudiantes."
     releaseDate="Agosto 2025" />
   ```

3. **Usar opacidad adecuada**

   ```vue
   <!-- Contenido secundario -->
   <DevelopmentOverlay :opacity="0.9">
     <DataEntryForm />
   </DevelopmentOverlay>

   <!-- Contenido importante visible -->
   <DevelopmentOverlay :opacity="0.6" :blurContent="false">
     <DataVisualization />
   </DevelopmentOverlay>
   ```

4. **Fechas realistas**

   ```vue
   <!-- ✅ Buena práctica -->
   <DevelopmentOverlay releaseDate="Q2 2025" />
   ```

---

## Solución de problemas

* **El overlay no se muestra**

  * Causa: componente no registrado.
  * Solución:

    ```javascript
    app.component('DevelopmentOverlay', DevelopmentOverlay)
    ```

* **Contenido blureado ilegible**

  * Solución:

    ```vue
    <DevelopmentOverlay :blurContent="false" :opacity="0.7" />
    ```

* **Botón de descarte no funciona**

  * Asegúrate de manejar el evento:

    ```vue
    <DevelopmentOverlay :dismissable="true" @dismissed="handleDismiss" />
    <script>
    methods: {
      handleDismiss() {
        this.$emit('closed');
      }
    }
    </script>
    ```

* **Superposición muy invasiva**

  * Ajusta opacidad y blur:

    ```vue
    <DevelopmentOverlay :opacity="0.5" :blurContent="false" :dismissable="true" dismissText="OK" />
    ```

---

## Ejemplos prácticos para CuriosMaze

### Dashboard de docente

```vue
<template>
  <div class="teacher-dashboard">
    <ProfileSection />
    <DevelopmentOverlay
      title="Estadísticas AI-Powered"
      message="Próximamente: análisis predictivo del rendimiento estudiantil."
      icon="🤖"
      releaseDate="Septiembre 2025">
      <StatsSection />
    </DevelopmentOverlay>
    <DevelopmentOverlay
      title="Generador de Ejercicios IA"
      message="Crea ejercicios de programación automáticamente."
      icon="✨"
      :dismissable="true"
      @dismissed="trackBetaUnderstanding">
      <ExerciseGenerator />
    </DevelopmentOverlay>
  </div>
</template>
```

### Página de evaluaciones

```vue
<template>
  <div class="evaluations-page">
    <ExistingFeatures />
    <DevelopmentOverlay
      title="Evaluaciones en Tiempo Real"
      message="Monitorea a tus estudiantes mientras realizan evaluaciones."
      icon="⚡"
      :opacity="0.85">
      <RealtimeMonitoring />
    </DevelopmentOverlay>
  </div>
</template>
```

### Repositorio de ejercicios

```vue
<template>
  <div class="exercise-repository">
    <BasicRepository />
    <DevelopmentOverlay
      title="Búsqueda Inteligente"
      message="Encuentra ejercicios usando lenguaje natural."
      icon="🔍"
      dismissText="Probar versión beta"
      :dismissable="true">
      <IntelligentSearch />
    </DevelopmentOverlay>
  </div>
</template>
```

