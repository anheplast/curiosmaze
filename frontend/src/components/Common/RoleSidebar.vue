<!-- Componente Sidebar Common/RoleSidebar.vue -->
<template>
    <nav id="sidebar" :class="{ expanded: !collapsed }" @mouseenter="expandSidebar" @mouseleave="collapseSidebar">
        <div class="sidebar-logo">
            <img src="../../../public/logo/Logo-CuriosMaze-40x40.png" alt="Logo">
            <div class="logo-text">
                CURIOS<br>
                MAZE
            </div>
        </div>

        <!-- Categoría: Navegación 
        <div class="sidebar-category">
            <div class="category-indicator">
                <div class="sidebar-dot"></div> 
                <div class="sidebar-label">NAVEGACIÓN</div> 
            </div>
        </div>
        -->

        <!-- Home icon 
        <a href="#" class="sidebar-item"
            @click.prevent="$router.push(userRole === 'admin' ? '/admin/dashboard' : '/docente/dashboard')">
            <div class="sidebar-item-icon">
                <i class="fas fa-home"></i>
            </div>
            <div class="sidebar-item-content">
                <strong>Inicio</strong>
                <span>Panel principal</span>
            </div>
        </a>
        -->

        <!-- Categoría: Contenido -->
        <div class="sidebar-category">
            <div class="category-indicator">
                <div class="sidebar-dot"></div>
                <div class="sidebar-label">CONTENIDO</div>
            </div>
        </div>

        <!-- Crear Evaluación (solo para docentes) -->
        <a v-if="userRole === 'docente'" href="#" class="sidebar-item"
            @click.prevent="$router.push('/docente/dashboard/crear-evaluacion')">
            <div class="sidebar-item-icon">
                <i class="fas fa-file-alt"></i>
            </div>
            <div class="sidebar-item-content">
                <strong>Crear Evaluación</strong>
                <span>Nueva evaluación</span>
            </div>
        </a>

        <!-- Crear Ejercicio (para ambos roles) -->
        <a href="#" class="sidebar-item"
            @click.prevent="$router.push(userRole === 'admin' ? '/admin/dashboard/crear-ejercicio' : '/docente/dashboard/crear-ejercicio')">
            <div class="sidebar-item-icon">
                <i class="fas fa-code"></i>
            </div>
            <div class="sidebar-item-content">
                <strong>Crear Ejercicio</strong>
                <span>Nuevo ejercicio</span>
            </div>
        </a>

        <!-- Repositorio de Ejercicios (para ambos roles) -->
        <a href="#" class="sidebar-item"
            @click.prevent="$router.push(userRole === 'admin' ? '/admin/dashboard/repositorio-ejercicios' : '/docente/dashboard/repositorio-ejercicios')">
            <div class="sidebar-item-icon">
                <i class="fas fa-folder-open"></i>
            </div>
            <div class="sidebar-item-content">
                <strong>Repositorio</strong>
                <span>Banco de ejercicios</span>
            </div>
        </a>

        <!-- Categoría: Administración -->
        <div class="sidebar-category">
            <div class="category-indicator">
                <div class="sidebar-dot"></div>
                <div class="sidebar-label">ADMINISTRACIÓN</div>
            </div>
        </div>

        <!-- Estudiantes (para docentes) / Usuarios (para admin) -->
        <a href="#" class="sidebar-item"
            @click.prevent="$router.push(userRole === 'admin' ? '/admin/dashboard/gestion-usuarios' : '/docente/dashboard/estudiantes')">
            <div class="sidebar-item-icon">
                <i class="fas fa-users"></i>
            </div>
            <div class="sidebar-item-content">
                <strong>{{ userRole === 'admin' ? 'Gestión de Usuarios' : 'Estudiantes' }}</strong>
                <span>{{ userRole === 'admin' ? 'Administrar usuarios' : 'Gestión de estudiantes' }}</span>
            </div>
        </a>

        <!-- Evaluaciones (solo para docentes) -->
        <a v-if="userRole === 'docente'" href="#" class="sidebar-item"
            @click.prevent="$router.push('/docente/dashboard/evaluaciones')">
            <div class="sidebar-item-icon">
                <i class="fas fa-clipboard-list"></i>
            </div>
            <div class="sidebar-item-content">
                <strong>Evaluaciones</strong>
                <span>Lista de evaluaciones</span>
            </div>
        </a>

        <!-- Categoría: Cuenta -->
        <div class="sidebar-category mt-auto">
            <div class="category-indicator">
                <div class="sidebar-dot"></div>
                <div class="sidebar-label">CUENTA</div>
            </div>
        </div>


        <!-- Cerrar Sesión -->
        <a href="#" class="sidebar-item logout-item" @click.prevent="logout">
            <div class="sidebar-item-icon">
                <i class="fas fa-sign-out-alt"></i>
            </div>
            <div class="sidebar-item-content">
                <strong>Cerrar Sesión</strong>
                <span>Salir de la plataforma</span>
            </div>
        </a>
    </nav>
</template>

<script>
// Importaciones necesarias
import { computed, ref, watch } from 'vue';
import { useStore } from 'vuex';
import { useRouter } from 'vue-router';

// Importamos anime.js
import anime from 'animejs';

export default {
    name: 'RoleSidebar',
    props: {
        collapsed: {
            type: Boolean,
            default: false
        }
    },
    emits: ['toggleSidebar'],
    setup(props, { emit }) {
        const store = useStore();
        const router = useRouter();
        
        // Estado interno
        const isSidebarExpanded = ref(!props.collapsed);
        
        // Observar cambios en la prop collapsed
        watch(() => props.collapsed, (newVal) => {
            isSidebarExpanded.value = !newVal;
            if (newVal) {
                handleCollapse();
            } else {
                handleExpand();
            }
        });
        
        // Obtener el rol del usuario desde store o localStorage
        const userRole = computed(() => {
            return store.state.auth?.userRole || localStorage.getItem('user_role') || 'docente';
        });

        // Expandir sidebar
        const expandSidebar = () => {
            if (isSidebarExpanded.value) return;
            isSidebarExpanded.value = true;
            emit('toggleSidebar', false);
            handleExpand();
        };
        
        // Colapsar sidebar
        const collapseSidebar = () => {
            if (!isSidebarExpanded.value) return;
            isSidebarExpanded.value = false;
            emit('toggleSidebar', true);
            handleCollapse();
        };
        
        // Manejar la expansión (separando animaciones)
        const handleExpand = () => {
            // 1. Animar primero los puntos a texto (más rápido)
            animateDotsToText();
            
            // 2. Luego animar el contenido del sidebar (normal)
            animateSidebarExpand();
        };
        
        // Manejar el colapso (separando animaciones)
        const handleCollapse = () => {
            // 1. Animar primero el contenido del sidebar (normal)
            animateSidebarCollapse();
            
            // 2. Luego animar el texto a puntos (más rápido)
            animateTextToDots();
        };
        
        // Animación rápida: puntos a texto - MODIFICADO
        const animateDotsToText = () => {
            anime.timeline({
                easing: 'easeOutQuad',
                duration: 120 // Más rápido
            })
            .add({
                targets: '#sidebar .sidebar-dot', // Selector específico
                scale: 0,
                opacity: 0
            })
            .add({
                targets: '#sidebar .sidebar-label', // Selector específico
                opacity: 1,
                translateX: 0,
                scale: 1,
                duration: 150, // Más rápido
                delay: 10
            }, '-=80'); // Superposición para mejor timing
        };
        
        // Animación rápida: texto a puntos 
        const animateTextToDots = () => {
            anime.timeline({
                easing: 'easeOutQuad',
                duration: 120 // Más rápido
            })
            .add({
                targets: '#sidebar .sidebar-label', // Selector específico
                opacity: 0,
                translateX: -10,
                scale: 0.8
            })
            .add({
                targets: '#sidebar .sidebar-dot', // Selector específico
                scale: 1,
                opacity: 1,
                duration: 150, // Más rápido
                delay: 10
            }, '-=80'); // Superposición para mejor timing
        };
        
        // Animación normal: expandir sidebar
        const animateSidebarExpand = () => {
            // Mostrar contenido de items
            anime({
                targets: '#sidebar .sidebar-item-content', // Selector específico
                opacity: 1,
                translateX: 0,
                easing: 'easeOutQuint',
                duration: 300,
                delay: anime.stagger(50, {start: 50})
            });
            
            // Mostrar texto del logo
            anime({
                targets: '#sidebar .logo-text', // Selector específico
                opacity: 1,
                translateX: 0,
                easing: 'easeOutQuint',
                duration: 300,
                delay: 50
            });
        };
        
        // Animación normal: colapsar sidebar
        const animateSidebarCollapse = () => {
            // Ocultar contenido de items
            anime({
                targets: '#sidebar .sidebar-item-content', // Selector específico
                opacity: 0,
                translateX: -10,
                easing: 'easeOutQuint',
                duration: 200
            });
            
            // Ocultar texto del logo
            anime({
                targets: '#sidebar .logo-text', // Selector específico
                opacity: 0,
                translateX: -10,
                easing: 'easeOutQuint',
                duration: 200
            });
        };
        
        // Función para cerrar sesión
        const logout = async () => {
            try {
                await store.dispatch('auth/logout');
                router.push('/');
            } catch (error) {
                console.error('Error al cerrar sesión:', error);
            }
        };

        return {
            userRole,
            expandSidebar,
            collapseSidebar,
            logout
        };
    }
}
</script>

<style scoped>
@import url('https://fonts.googleapis.com/css2?family=Candara:wght@700&display=swap');
@import url('https://fonts.googleapis.com/css2?family=Nunito:wght@400;500;600;700&display=swap');

/* =================== CONTENEDOR PRINCIPAL =================== */
#sidebar {
  position: fixed !important;
  left: 0 !important;
  top: 0 !important;
  height: 100vh !important;
  width: 55px !important;
  min-width: 55px !important;
  max-width: 55px !important;
  background-color: var(--color-bg-main) !important;
  display: flex !important;
  flex-direction: column !important;
  z-index: 1100 !important;
  transition: all 0.06s ease-in-out !important;
  overflow: hidden !important;
  box-shadow: var(--shadow-lg) !important;
  font-family: 'Nunito', sans-serif !important;
  color: var(--color-text-primary) !important;
}

#sidebar.expanded, 
#sidebar:hover {
  width: 233px !important;
  min-width: 233px !important;
  max-width: 233px !important;
}

/* =================== LOGO DEL SIDEBAR =================== */
#sidebar .sidebar-logo {
  display: flex !important;
  align-items: center !important;
  justify-content: flex-start !important;
  height: 55px !important;
  padding: 0 15px !important;
  margin-bottom: 5px !important;
}

#sidebar .sidebar-logo img {
  max-width: 40px !important;
  max-height: 40px !important;
  margin-right: 5px !important;
  margin-left: -8px !important;
}

#sidebar .logo-text {
  font-family: 'Candara', sans-serif !important;
  font-weight: bold !important;
  font-size: 1.2em !important;
  line-height: 1.1 !important;
  opacity: 0 !important;
  transform: translateX(-10px) !important;
  margin-left: 10px !important;
  transition: opacity var(--transition-fast) ease-in-out, 
              transform var(--transition-fast) ease-in-out !important;
}

#sidebar.expanded .logo-text, 
#sidebar:hover .logo-text {
  opacity: 1 !important;
  transform: translateX(0) !important;
}

/* =================== CATEGORÍAS DEL SIDEBAR =================== */
#sidebar .sidebar-category {
  display: flex !important;
  align-items: center !important;
  justify-content: center !important;
  height: 25px !important;
  padding: 0 !important;
  margin: 10px 0 !important;
  position: relative !important;
  width: 100% !important;
  box-sizing: border-box !important;
}

#sidebar .category-indicator {
  position: relative !important;
  display: flex !important;
  align-items: center !important;
  justify-content: flex-start !important;
  width: 100% !important;
  padding: 0 20px !important;
}

/* =================== INDICADOR DE PUNTO =================== */
#sidebar .sidebar-dot {
  width: 10px !important;
  height: 10px !important;
  background-color: var(--color-pointer-sidebar) !important;
  border-radius: 50% !important;
  position: absolute !important;
  left: 50% !important;
  transform: translateX(-50%) !important;
  transform-origin: center !important;
  z-index: 2 !important;
  transition: transform 0.15s ease-out, opacity 0.15s ease-out !important;
}

#sidebar.expanded .sidebar-dot, 
#sidebar:hover .sidebar-dot {
  opacity: 0 !important;
  transform: translateX(-50%) scale(0) !important;
}

/* =================== ETIQUETAS DE CATEGORÍA =================== */
#sidebar .sidebar-label {
  font-size: 11px !important;
  font-weight: 600 !important;
  color: var(--color-text-primary) !important;
  text-transform: uppercase !important;
  letter-spacing: 0.5px !important;
  white-space: nowrap !important;
  opacity: 0 !important;
  transform: translateX(-20px) scale(0.8) !important;
  position: absolute !important;
  left: 20px !important;
  transition: transform 0.15s ease-out, opacity 0.15s ease-out !important;
}

#sidebar.expanded .sidebar-label, 
#sidebar:hover .sidebar-label {
  opacity: 1 !important;
  transform: translateX(0) scale(1) !important;
}

#sidebar .mt-auto {
  margin-top: auto !important;
}

/* =================== ÍTEMS DEL SIDEBAR =================== */
#sidebar .sidebar-item {
  display: flex !important;
  align-items: center !important;
  padding: 0 1rem !important;
  color: var(--color-text-primary) !important;
  text-decoration: none !important;
  position: relative !important;
  overflow: hidden !important;
  white-space: nowrap !important;
  height: 60px !important;
  box-sizing: border-box !important;
  margin: 2px 0 !important;
  transition: background-color var(--transition-fast) ease-in-out, 
              color var(--transition-fast) ease-in-out !important;
  border: none !important;
  background: transparent !important;
}

#sidebar .sidebar-item:hover {
  color: var(--color-primary) !important;
  background-color: var(--color-bg-element-hover) !important;
}

/* =================== ICONOS DE ÍTEMS =================== */
#sidebar .sidebar-item-icon {
  width: 28px !important;
  height: 28px !important;
  display: flex !important;
  align-items: center !important;
  justify-content: center !important;
  position: absolute !important;
  left: 15px !important;
  top: 50% !important;
  transform: translateY(-50%) !important;
}

#sidebar .sidebar-item-icon i {
  font-size: 20px !important;
  color: var(--color-text-primary) !important;
  transition: color var(--transition-fast) ease-in-out !important;
}

#sidebar .sidebar-item:hover .sidebar-item-icon i {
  color: var(--color-primary) !important;
}

/* =================== CONTENIDO DE ÍTEMS =================== */
#sidebar .sidebar-item-content {
  font-size: 15px !important;
  display: flex !important;
  flex-direction: column !important;
  margin-left: 45px !important;
  opacity: 0 !important;
  transform: translateX(-10px) !important;
  transition: opacity var(--transition-fast) ease-in-out, 
              transform var(--transition-fast) ease-in-out !important;
}

#sidebar .sidebar-item-content strong {
  font-size: 16px !important;
  line-height: 1.2 !important;
  font-weight: 600 !important;
  margin: 0 !important;
  padding: 0 !important;
}

#sidebar .sidebar-item-content span {
  font-size: 14px !important;
  opacity: 0.8 !important;
  line-height: 1.3 !important;
  margin: 0 !important;
  padding: 0 !important;
}

#sidebar.expanded .sidebar-item-content, 
#sidebar:hover .sidebar-item-content {
  opacity: 1 !important;
  transform: translateX(0) !important;
}

/* =================== ÍTEM DE LOGOUT =================== */
#sidebar .logout-item {
  margin-bottom: 10px !important;
  color: var(--color-text-primary) !important;
}

#sidebar .logout-item:hover {
  background-color: var(--color-logout-bg) !important;
  color: var(--color-logout-hover) !important;
}

#sidebar .logout-item .sidebar-item-icon i {
  color: var(--color-logout) !important;
}

#sidebar .logout-item:hover .sidebar-item-icon i {
  color: var(--color-logout-hover) !important;
}

#sidebar .logout-item .sidebar-item-content strong,
#sidebar .logout-item .sidebar-item-content span {
  transition: color var(--transition-fast) ease-in-out !important;
}

#sidebar .logout-item:hover .sidebar-item-content strong,
#sidebar .logout-item:hover .sidebar-item-content span {
  color: var(--color-logout-hover) !important;
}
</style>