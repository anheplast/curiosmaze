<!-- src/views/StudentDashboard.vue -->
<template>
  <div class="student-dashboard">
    <!-- 2 opciones -> historial o ingresar a una evaluacion -->
    <StudentOptions 
      @select-option="handleOptionSelect"
    />
    
    <!-- Redireccionar a loginEvaluation cuando se selecciona -->
    <div v-if="isRedirecting" class="redirect-container">
      <div class="redirect-animation">
        <span class="redirect-icon">🚀</span>
        <p>Redirigiendo...</p>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, onMounted } from 'vue';
import { useRouter } from 'vue-router';
import { useStore } from 'vuex';
import StudentOptions from '@/components/estudiantes/StudentOptions.vue';

export default {
  name: 'StudentDashboard',
  components: {
    StudentOptions
  },
  setup() {
    const router = useRouter();
    const store = useStore();
    const isRedirecting = ref(false);

    // Verifica que el usuario es un estudiante
    onMounted(() => {
      const userRole = store.getters['auth/userRole'];
      if (userRole !== 'estudiante') {
        router.push('/');
      }
    });

    // Maneja la selección de opciones
    const handleOptionSelect = (option) => {
      console.log('Opción seleccionada:', option);
      
      if (option === 'new') {
        // Redirecciona a una nueva evaluacion
        isRedirecting.value = true;
        setTimeout(() => {
          router.push('/evaluation-access');
        }, 1000);
      } 
      else if (option === 'history') {
        // Redirecciona al historial de evaluaciones
        isRedirecting.value = true;
        setTimeout(() => {
          router.push('/estudiante/historial-evaluaciones');
        }, 1000);
      }
    };

    return {
      isRedirecting,
      handleOptionSelect
    };
  }
}
</script>

<style scoped>
.student-dashboard {
  min-height: 100vh;
  width: 100%;
  background-color: #1C1C21;
  display: flex;
  justify-content: center;
  align-items: center;
  position: relative;
}

.redirect-container {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  display: flex;
  justify-content: center;
  align-items: center;
  background-color: rgba(28, 28, 33, 0.9);
  z-index: 1000;
}

.redirect-animation {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  background-color: #2A2A30;
  padding: 2rem;
  border-radius: 12px;
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.3);
  animation: fadeIn 0.5s ease-out;
}

.redirect-icon {
  font-size: 4rem;
  margin-bottom: 1rem;
  animation: launch 1.5s infinite;
}

.redirect-animation p {
  font-size: 1.2rem;
  color: #e0e0e0;
}

@keyframes launch {
  0% {
    transform: translateY(0) rotate(0deg);
  }
  50% {
    transform: translateY(-20px) rotate(5deg);
  }
  100% {
    transform: translateY(0) rotate(0deg);
  }
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
</style>