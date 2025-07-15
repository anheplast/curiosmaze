<!-- src/views/Dashboard.vue -->
<template>
  <div class="role-dashboard">
    <!-- Componente Sidebar, al que le pasamos el estado (colapsado/expandido) -->
    <RoleSidebar :collapsed="isCollapsed" @toggleSidebar="toggleSidebar" />

    <!-- Área de contenido donde se renderiza la ruta hija -->
    <div class="dashboard-content">
      <router-view />
    </div>
  </div>
</template>

<script>
import { ref, computed, onMounted } from 'vue';
import { useStore } from 'vuex';
import { useRouter } from 'vue-router';
import RoleSidebar from '@/components/Common/RoleSidebar.vue';

export default {
  name: 'RoleDashboard',
  components: {
    RoleSidebar
  },
  setup() {
    const store = useStore();
    const router = useRouter();
    
    // Estado para el sidebar
    const isCollapsed = ref(true);
    
    // Manejador para cambiar el estado del sidebar
    const toggleSidebar = (collapsed) => {
      isCollapsed.value = collapsed;
    };
    
    // Inicializar el estado de autenticación
    onMounted(() => {
      // Inicializar estado de autenticación desde localStorage
      store.dispatch('auth/initAuth');
      
      // Verificar si el usuario está autenticado
      const isAuthenticated = store.getters['auth/isAuthenticated'];
      const userRole = store.getters['auth/userRole'];
      
      if (!isAuthenticated) {
        // Redirigir al login si no está autenticado
        router.push('/');
        return;
      }
      
      // Verificar que esté en la ruta correcta según su rol
      const currentPath = router.currentRoute.value.path;
      const correctBasePath = userRole === 'admin' 
        ? '/admin/dashboard' 
        : userRole === 'docente' 
          ? '/docente/dashboard' 
          : '/evaluation-access';
      
      if (!currentPath.startsWith(correctBasePath)) {
        router.push(correctBasePath);
      }
    });
    
    return {
      isCollapsed,
      toggleSidebar
    };
  }
};
</script>

<style scoped>
/* =================== CONTENEDOR PRINCIPAL =================== */
.role-dashboard {
  display: flex;
  min-height: 100vh;
  background-color: var(--color-bg-lighter);
  position: relative;
}

/* =================== CONTENIDO DEL DASHBOARD =================== */
.dashboard-content {
  flex: 1;
  position: relative;
  padding: 20px;
  padding-left: 75px;
  width: 100%;
  box-sizing: border-box;
  overflow-x: hidden;
  background-color: var(--color-bg-main);
}

/* =================== MEDIA QUERIES =================== */
@media (max-width: 768px) {
  .dashboard-content {
    padding-left: 65px;
    padding-right: 10px;
  }
}
</style>