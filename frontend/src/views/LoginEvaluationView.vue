<!-- views/LoginEvaluationView.vue -->
<template>
  <div class="evaluation-view">
    <!-- Botón para volver atrás -->
    <button class="back-button" @click="goBack" title="Volver al dashboard">
      <i class="fas fa-arrow-left"></i>
    </button>

    <!-- Botón de cerrar sesión -->
    <button class="logout-button" @click="logout" title="Cerrar sesión">
      <i class="fas fa-sign-out-alt"></i>
    </button>
    
    <EvaluationAccess @access-granted="startEvaluation" />
  </div>
</template>

<script>
import EvaluationAccess from '@/components/EvaluationAccess.vue';
import { useRouter } from 'vue-router';
import { useStore } from 'vuex';

export default {
  name: 'LoginEvaluationView',
  components: {
    EvaluationAccess
  },
  setup() {
    const router = useRouter();
    const store = useStore();

    const startEvaluation = (accessKey) => {
      console.log('Acceso concedido con clave:', accessKey);
    }

    // Función para volver al dashboard de estudiante
    const goBack = () => {
      router.push('/estudiante/dashboard');
    }

    // Función para cerrar sesión
    const logout = () => {
      store.dispatch('auth/logout').then(() => {
        router.push('/');
      });
    }

    return {
      startEvaluation,
      goBack,
      logout
    }
  }
}
</script>

<style>
body {
  margin: 0;
  padding: 0;
  font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
  background-color: #f5f5f5;
}

.evaluation-view {
  min-height: 100vh;
  width: 100%;
  position: relative;
}

/* Botón para volver atrás */
.back-button {
  position: absolute;
  top: 1.5rem;
  left: 1.5rem;
  background-color: #2A2A30;
  color: #9090A0;
  border: 1px solid #36363c;
  cursor: pointer;
  width: 40px;
  height: 40px;
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.3s ease;
  font-size: 1.25rem;
  z-index: 100;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.back-button:hover {
  color: #65B1C1;
  background-color: rgba(101, 177, 193, 0.1);
  border-color: #65B1C1;
  transform: translateY(-2px);
  box-shadow: 0 4px 8px rgba(101, 177, 193, 0.2);
}

/* Botón de cerrar sesión */
.logout-button {
  position: absolute;
  top: 1.5rem;
  right: 1.5rem;
  background-color: #2A2A30;
  color: #9090A0;
  border: 1px solid #36363c;
  cursor: pointer;
  width: 40px;
  height: 40px;
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.3s ease;
  font-size: 1.25rem;
  z-index: 100;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.logout-button:hover {
  color: #FF6B6B;
  background-color: rgba(255, 107, 107, 0.1);
  border-color: #FF6B6B;
  transform: translateY(-2px);
  box-shadow: 0 4px 8px rgba(255, 107, 107, 0.2);
}
</style>