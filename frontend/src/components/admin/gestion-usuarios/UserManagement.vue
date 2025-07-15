<!-- src/components/admin/gestion-usuarios/UserManagement.vue -->
<template>
  <div class="user-management-wrapper">
    <div class="box form-container">
      <div class="header-section">
        <div class="header-content">
          <h1 class="title is-3">
            <span class="header-icon">👥</span> Gestión de Usuarios
          </h1>
          <p class="subtitle is-6">Administre usuarios, solicitudes y permisos del sistema</p>
        </div>

        <!-- Botones de acciones principales -->
        <div class="header-actions">
          <button class="button action-btn create-btn" @click="openCreateUserModal()">
            <span class="icon">👤</span>
            <span>Crear Usuario</span>
          </button>
          <!-- FUNCION DESACTIVADA 
            <button class="button action-btn import-btn" @click="openImportUsersModal()">
              <span class="icon">📥</span>
              <span>Importar Lista</span>
            </button>
            -->
        </div>
      </div>

      <!-- Estado de error general -->
      <ErrorState v-if="errorState.hasError" :title="errorState.message" :details="errorState.details"
        @retry="retryLoadWithBackoff(currentTab)" />

      <!-- Pestañas para diferentes secciones -->
      <div class="tabs-container">
        <div v-for="tab in tabs" :key="tab.value" class="tab" :class="{ 'active-tab': currentTab === tab.value }"
          @click="changeTab(tab.value)">
          <span class="tab-icon">{{ tab.icon }}</span>
          <span class="tab-text">{{ tab.label }}</span>
          <div v-if="tab.value === 'pending' && pendingCount > 0" class="badge">{{ pendingCount }}</div>
        </div>
      </div>

      <!-- Estado de carga -->
      <div class="loading-container" v-if="isLoading">
        <div class="loader"></div>
        <p>Cargando usuarios...</p>
      </div>

      <!-- Contenido según pestaña activa -->
      <template v-else>
        <!-- Solicitudes pendientes -->
        <PendingUsers v-if="currentTab === 'pending'" :users="pendingUsers" @approve-user="approveUser"
          @reject-user="rejectUser" />

        <!-- Usuarios activos -->
        <ActiveUsers v-if="currentTab === 'active'" :users="activeUsers" @view-user="viewUserDetails"
          @edit-user="openEditModal" @deactivate-user="deactivateUser" @reset-password="resetUserPassword" />

        <!-- Solicitudes rechazadas -->
        <RejectedUsers v-if="currentTab === 'rejected'" :users="rejectedUsers" @reconsider-user="approveUser"
          @delete-user="deleteUser" />
      </template>
    </div>

    <!-- Componentes de modales -->
    <ConfirmModal v-if="showConfirmModal" :title="confirmTitle" :message="confirmMessage" :icon="confirmIcon"
      :button-text="confirmButtonText" :button-class="confirmButtonClass" :show-reject-reason="showRejectReason"
      :reject-reason="rejectReason" @confirm="confirmAction" @cancel="cancelConfirmAction"
      @update:reject-reason="rejectReason = $event" />

    <UserDetailsModal v-if="showUserDetailsModal" :user="selectedUser" @close="closeUserDetailsModal" />

    <UserFormModal v-if="showUserFormModal" :user="editingUser" :mode="userFormMode" :is-loading="isProcessingUserForm"
      @save="saveUser" @cancel="closeUserFormModal" />

    <ResetPasswordModal v-if="showResetPasswordModal" :user="selectedUser" :is-loading="isResetting"
      @reset="confirmResetPassword" @cancel="closeResetPasswordModal" />

    <ImportUsersModal v-if="showImportModal" :is-loading="isImporting" @import="importUsers"
      @cancel="closeImportModal" />

    <!-- Notificación personalizada -->
    <CustomNotification v-if="showNotification" :title="notificationTitle" :message="notificationMessage"
      :icon="notificationIcon" :type="notificationType" @close="closeNotification" />
  </div>
</template>

<script>
import { ref, computed, onMounted, watch } from 'vue';
import authService from '@/api/authService';

// Importar componentes
import PendingUsers from '@/components/admin/gestion-usuarios/PendingUsers.vue';
import ActiveUsers from '@/components/admin/gestion-usuarios/ActiveUsers.vue';
import RejectedUsers from '@/components/admin/gestion-usuarios/RejectedUsers.vue';
import ConfirmModal from '@/components/admin/gestion-usuarios/modals/ConfirmModal.vue';
import UserDetailsModal from '@/components/admin/gestion-usuarios/modals/UserDetailsModal.vue';
import UserFormModal from '@/components/admin/gestion-usuarios/modals/UserFormModal.vue';
import ResetPasswordModal from '@/components/admin/gestion-usuarios/modals/ResetPasswordModal.vue';
import ImportUsersModal from '@/components/admin/gestion-usuarios/modals/ImportUsersModal.vue';
import CustomNotification from '@/components/Common/CustomNotification.vue';
import ErrorState from '@/components/Common/ErrorState.vue';

export default {
  name: 'UserManagement',
  components: {
    PendingUsers,
    ActiveUsers,
    RejectedUsers,
    ConfirmModal,
    UserDetailsModal,
    UserFormModal,
    ResetPasswordModal,
    ImportUsersModal,
    CustomNotification,
    ErrorState
  },
  setup() {
    // Pestañas disponibles
    const tabs = [
      { value: 'pending', label: 'Solicitudes Pendientes', icon: '🕒' },
      { value: 'active', label: 'Usuarios Activos', icon: '✅' },
      { value: 'rejected', label: 'Solicitudes Rechazadas', icon: '❌' }
    ];

    // Estados
    const currentTab = ref('pending');
    const pendingUsers = ref([]);
    const activeUsers = ref([]);
    const rejectedUsers = ref([]);
    const isLoading = ref(true);

    // Conteo de solicitudes pendientes para la insignia
    const pendingCount = computed(() => pendingUsers.value.length);

    // Estados para confirmación
    const showConfirmModal = ref(false);
    const confirmTitle = ref('');
    const confirmMessage = ref('');
    const confirmIcon = ref('');
    const confirmButtonText = ref('');
    const confirmButtonClass = ref('');
    const confirmAction = ref(null);
    const selectedUser = ref(null);
    const showRejectReason = ref(false);
    const rejectReason = ref('');

    // Estados para notificación
    const showNotification = ref(false);
    const notificationTitle = ref('');
    const notificationMessage = ref('');
    const notificationIcon = ref('');
    const notificationType = ref('');

    // Estado de error para mostrar en la interfaz
    const errorState = ref({
      hasError: false,
      message: '',
      details: ''
    });

    // Estados para modal de detalles
    const showUserDetailsModal = ref(false);

    // Estados para modal de formulario de usuario
    const showUserFormModal = ref(false);
    const editingUser = ref(null);
    const isProcessingUserForm = ref(false);
    const userFormMode = ref('create'); // 'create', 'edit'

    // Estados para modal de reset de contraseña
    const showResetPasswordModal = ref(false);
    const isResetting = ref(false);

    // Estados para modal de importación
    const showImportModal = ref(false);
    const isImporting = ref(false);

    // Cambiar de pestaña
    const changeTab = (tab) => {
      currentTab.value = tab;
    };

    // Obtener datos de usuarios del backend
    const loadUsers = async (estado) => {
      try {
        isLoading.value = true;
        errorState.value.hasError = false;

        console.log(`Cargando usuarios con estado: ${estado}`);
        console.log('Información de autenticación:');
        console.log('- Token:', localStorage.getItem('token') ? 'Presente' : 'No presente');
        console.log('- User ID:', localStorage.getItem('user_id'));
        console.log('- User Role:', localStorage.getItem('user_role'));

        const response = await authService.getUsersByStatus(estado);
        console.log(`Usuarios ${estado} obtenidos:`, response.data);

        if (estado === 'pendiente') {
          pendingUsers.value = response.data || [];
        } else if (estado === 'activo') {
          activeUsers.value = response.data || [];
        } else if (estado === 'rechazado') {
          rejectedUsers.value = response.data || [];
        } else if (estado === 'todos') {
          // Cargar todos los estados en una sola llamada (opcional)
          const data = response.data || [];
          pendingUsers.value = data.filter(user => user.estado === 'pendiente');
          activeUsers.value = data.filter(user => user.estado === 'activo');
          rejectedUsers.value = data.filter(user => user.estado === 'rechazado');
        }

      } catch (error) {
        console.error(`Error al cargar usuarios ${estado}:`, error);

        // Mostrar estado de error en la interfaz
        errorState.value = {
          hasError: true,
          message: `Error al cargar usuarios ${estado}`,
          details: error.response?.data?.error || error.message || 'Error desconocido'
        };

        // Mostrar notificación de error
        showNotificationMessage(
          'Error',
          `No se pudieron cargar los usuarios ${estado}. ${errorState.value.details}`,
          '❌',
          'danger'
        );

        // Garantizar que al menos tengamos un array vacío
        if (estado === 'pendiente') {
          pendingUsers.value = [];
        } else if (estado === 'activo') {
          activeUsers.value = [];
        } else if (estado === 'rechazado') {
          rejectedUsers.value = [];
        }
      } finally {
        isLoading.value = false;
      }
    };

    // Intentar recargar de forma recursiva con retroceso exponencial
    const retryLoadWithBackoff = async (estado, attempt = 1, maxAttempts = 3) => {
      try {
        await loadUsers(estado);
      } catch (error) {
        if (attempt < maxAttempts) {
          const delay = Math.pow(2, attempt) * 1000; // 2s, 4s, 8s...
          console.log(`Reintentando en ${delay}ms (intento ${attempt} de ${maxAttempts})...`);

          setTimeout(() => {
            retryLoadWithBackoff(estado, attempt + 1, maxAttempts);
          }, delay);
        }
      }
    };

    // Método para mostrar confirmación de acción
    const showConfirmation = (user, type) => {
      selectedUser.value = user;
      showRejectReason.value = false;

      if (type === 'approve') {
        confirmTitle.value = 'Aprobar Usuario';
        confirmMessage.value = `¿Está seguro que desea aprobar al usuario ${user.nombres} ${user.apellidos}?`;
        confirmIcon.value = '✅';
        confirmButtonText.value = 'Aprobar';
        confirmButtonClass.value = 'confirm-approve-btn';
        confirmAction.value = async () => {
          try {
            console.log('Aprobando usuario:', user);
            const response = await authService.updateUserStatus({
              user_id: user.id,
              estado: 'activo'
            });

            console.log('Respuesta de aprobación:', response.data);

            // Actualizar listas localmente
            if (user.estado === 'pendiente') {
              pendingUsers.value = pendingUsers.value.filter(u => u.id !== user.id);
            } else if (user.estado === 'rechazado') {
              rejectedUsers.value = rejectedUsers.value.filter(u => u.id !== user.id);
            }

            // Recargar usuarios activos
            await loadUsers('activo');

            showConfirmModal.value = false;
            showNotificationMessage('Usuario aprobado', `${user.nombres} ${user.apellidos} ha sido aprobado exitosamente.`, '✅', 'success');
          } catch (error) {
            console.error('Error al aprobar usuario:', error);
            showNotificationMessage('Error', 'No se pudo aprobar el usuario. Intente nuevamente.', '❌', 'danger');
          }
        };
      } else if (type === 'reject') {
        confirmTitle.value = 'Rechazar Usuario';
        confirmMessage.value = `¿Está seguro que desea rechazar al usuario ${user.nombres} ${user.apellidos}?`;
        confirmIcon.value = '❌';
        confirmButtonText.value = 'Rechazar';
        confirmButtonClass.value = 'confirm-reject-btn';
        showRejectReason.value = false; // No necesitamos motivo de rechazo según los requisitos
        confirmAction.value = async () => {
          try {
            console.log('Rechazando usuario:', user);
            const response = await authService.updateUserStatus({
              user_id: user.id,
              estado: 'rechazado'
            });

            console.log('Respuesta de rechazo:', response.data);

            // Actualizar listas localmente
            if (user.estado === 'pendiente') {
              pendingUsers.value = pendingUsers.value.filter(u => u.id !== user.id);
            } else if (user.estado === 'activo') {
              activeUsers.value = activeUsers.value.filter(u => u.id !== user.id);
            }

            // Recargar usuarios rechazados
            await loadUsers('rechazado');

            showConfirmModal.value = false;
            showNotificationMessage('Usuario rechazado', `${user.nombres} ${user.apellidos} ha sido rechazado.`, '❌', 'success');
          } catch (error) {
            console.error('Error al rechazar usuario:', error);
            showNotificationMessage('Error', 'No se pudo rechazar el usuario. Intente nuevamente.', '❌', 'danger');
          }
        };
      } else if (type === 'deactivate') {
        confirmTitle.value = 'Desactivar Usuario';
        confirmMessage.value = `¿Está seguro que desea desactivar al usuario ${user.nombres} ${user.apellidos}?`;
        confirmIcon.value = '🚫';
        confirmButtonText.value = 'Desactivar';
        confirmButtonClass.value = 'confirm-deactivate-btn';
        confirmAction.value = async () => {
          try {
            console.log('Desactivando usuario:', user);
            const response = await authService.updateUserStatus({
              user_id: user.id,
              estado: 'rechazado'
            });

            console.log('Respuesta de desactivación:', response.data);

            // Actualizar listas localmente
            activeUsers.value = activeUsers.value.filter(u => u.id !== user.id);

            // Recargar usuarios rechazados
            await loadUsers('rechazado');

            showConfirmModal.value = false;
            showNotificationMessage('Usuario desactivado', `${user.nombres} ${user.apellidos} ha sido desactivado.`, '🚫', 'warning');
          } catch (error) {
            console.error('Error al desactivar usuario:', error);
            showNotificationMessage('Error', 'No se pudo desactivar el usuario. Intente nuevamente.', '❌', 'danger');
          }
        };
      } else if (type === 'delete') {
        confirmTitle.value = 'Eliminar Usuario';
        confirmMessage.value = `¿Está seguro que desea eliminar definitivamente al usuario ${user.nombres} ${user.apellidos}?`;
        confirmIcon.value = '🗑️';
        confirmButtonText.value = 'Eliminar';
        confirmButtonClass.value = 'confirm-delete-btn';
        confirmAction.value = async () => {
          try {
            console.log('Eliminando usuario:', user);
            const response = await authService.deleteUser(user.id);

            console.log('Respuesta de eliminación:', response.data);

            // Actualizar listas localmente
            pendingUsers.value = pendingUsers.value.filter(u => u.id !== user.id);
            activeUsers.value = activeUsers.value.filter(u => u.id !== user.id);
            rejectedUsers.value = rejectedUsers.value.filter(u => u.id !== user.id);

            showConfirmModal.value = false;
            showNotificationMessage('Usuario eliminado', `${user.nombres} ${user.apellidos} ha sido eliminado definitivamente.`, '🗑️', 'danger');
          } catch (error) {
            console.error('Error al eliminar usuario:', error);
            showNotificationMessage('Error', 'No se pudo eliminar el usuario. Intente nuevamente.', '❌', 'danger');
          }
        };
      }

      showConfirmModal.value = true;
    };

    // Cancelar confirmación
    const cancelConfirmAction = () => {
      showConfirmModal.value = false;
      selectedUser.value = null;
      showRejectReason.value = false;
      rejectReason.value = '';
    };

    // Métodos para acciones de usuario
    const approveUser = (user) => {
      showConfirmation(user, 'approve');
    };

    const rejectUser = (user) => {
      showConfirmation(user, 'reject');
    };

    const deactivateUser = (user) => {
      showConfirmation(user, 'deactivate');
    };

    const deleteUser = (user) => {
      showConfirmation(user, 'delete');
    };

    // Mostrar detalles del usuario
    const viewUserDetails = (user) => {
      selectedUser.value = { ...user };
      showUserDetailsModal.value = true;
    };

    // Cerrar modal de detalles
    const closeUserDetailsModal = () => {
      showUserDetailsModal.value = false;
      selectedUser.value = null;
    };

    // Abrir modal de creación de usuario
    const openCreateUserModal = () => {
      userFormMode.value = 'create';
      editingUser.value = {
        nombres: '',
        apellidos: '',
        identificacion: '',
        email: '',
        password: '',
        password_confirm: '',
        rol: 'estudiante',
        genero: '',
        edad: null,
        curso: '',
        paralelo: '',
        turno: '',
        especializacion: ''
      };
      showUserFormModal.value = true;
    };

    // Abrir modal de edición
    const openEditModal = (user) => {
      userFormMode.value = 'edit';
      editingUser.value = {
        ...user,
        password: '',
        password_confirm: ''
      };
      showUserFormModal.value = true;
    };

    // Cerrar modal de formulario
    const closeUserFormModal = () => {
      showUserFormModal.value = false;
      editingUser.value = null;
    };

    // Guardar usuario (crear o editar)
    const saveUser = async (userData) => {
      try {
        isProcessingUserForm.value = true;

        // Crear una copia de los datos para procesarlos
        const processedData = { ...userData };

        // Asegurarse de que el campo 'username' existe y tiene el valor correcto
        // En este caso, usamos la identificación como username (o ID único)
        if (processedData.identificacion && !processedData.username) {
          processedData.username = processedData.identificacion;
        }

        // Si aún no hay username, mostrar error
        if (!processedData.username) {
          showNotificationMessage(
            'Error',
            'El número de identificación es obligatorio',
            '❌',
            'danger'
          );
          isProcessingUserForm.value = false;
          return;
        }

        // Verificar otros campos obligatorios
        if (!processedData.nombres || !processedData.apellidos) {
          showNotificationMessage(
            'Error',
            'Los nombres y apellidos son obligatorios',
            '❌',
            'danger'
          );
          isProcessingUserForm.value = false;
          return;
        }

        let response;
        if (userFormMode.value === 'create') {
          // Crear nuevo usuario
          response = await authService.createUser(processedData);
          showNotificationMessage('Usuario creado', `${processedData.nombres} ${processedData.apellidos} ha sido creado exitosamente.`, '✅', 'success');
        } else {
          // Editar usuario existente
          response = await authService.updateUser(processedData.id, processedData);
          showNotificationMessage('Usuario actualizado', `${processedData.nombres} ${processedData.apellidos} ha sido actualizado exitosamente.`, '✅', 'success');
        }

        // Recargar usuarios según el estado
        await loadUsers('activo');

        // Cerrar modal
        closeUserFormModal();

      } catch (error) {
        console.error('Error al procesar usuario:', error);
        let errorMsg = 'Ha ocurrido un error. Por favor, intente nuevamente.';

        if (error.response && error.response.data) {
          if (error.response.data.error) {
            errorMsg = error.response.data.error;
          } else if (typeof error.response.data === 'string') {
            errorMsg = error.response.data;
          } else {
            errorMsg = JSON.stringify(error.response.data);
          }
        }

        showNotificationMessage('Error', errorMsg, '❌', 'danger');
      } finally {
        isProcessingUserForm.value = false;
      }
    };

    // Abrir modal de reset de contraseña
    const resetUserPassword = (user) => {
      selectedUser.value = { ...user };
      showResetPasswordModal.value = true;
    };

    // Cerrar modal de reset de contraseña
    const closeResetPasswordModal = () => {
      showResetPasswordModal.value = false;
      selectedUser.value = null;
    };

    // Confirmar reset de contraseña
    const confirmResetPassword = async (data) => {
      try {
        isResetting.value = true;

        // Llamar a la API para resetear contraseña
        const response = await authService.adminResetPassword({
          user_id: selectedUser.value.id,
          admin_password: data.adminPassword
        });

        // Cerrar modal
        closeResetPasswordModal();

        // Guardar referencia al nombre de usuario antes de cerrar el modal
        const userFullName = selectedUser.value ?
          `${selectedUser.value.nombres} ${selectedUser.value.apellidos}` :
          'Usuario';

        // Mostrar notificación
        showNotificationMessage(
          'Contraseña restablecida',
          `La contraseña de ${userFullName} ha sido restablecida exitosamente.`,
          '🔑',
          'success'
        );

      } catch (error) {
        console.error('Error al resetear contraseña:', error);
        let errorMsg = 'No se pudo restablecer la contraseña. Verifique su contraseña de administrador e intente nuevamente.';

        if (error.response && error.response.data && error.response.data.error) {
          errorMsg = error.response.data.error;
        }

        showNotificationMessage('Error', errorMsg, '❌', 'danger');
      } finally {
        isResetting.value = false;
      }
    };

    // Abrir modal de importación
    const openImportUsersModal = () => {
      showImportModal.value = true;
    };

    // Cerrar modal de importación
    const closeImportModal = () => {
      showImportModal.value = false;
    };

    // Importar usuarios
    const importUsers = async (data) => {
      try {
        isImporting.value = true;

        // Llamar a la API para importar usuarios
        const response = await authService.importUsers(data);

        // Cerrar modal
        closeImportModal();

        // Recargar usuarios
        await loadUsers('activo');

        // Mostrar notificación
        showNotificationMessage(
          'Usuarios importados',
          `Se han importado ${response.data.count || 'los'} usuarios exitosamente.`,
          '📥',
          'success'
        );

      } catch (error) {
        console.error('Error al importar usuarios:', error);
        showNotificationMessage('Error', 'No se pudieron importar los usuarios. Verifique el formato e intente nuevamente.', '❌', 'danger');
      } finally {
        isImporting.value = false;
      }
    };

    // Mostrar notificación
    const showNotificationMessage = (title, message, icon, type) => {
      notificationTitle.value = title;
      notificationMessage.value = message;
      notificationIcon.value = icon;
      notificationType.value = type;
      showNotification.value = true;

      // Auto-ocultar después de 4 segundos
      setTimeout(() => {
        showNotification.value = false;
      }, 4000);
    };

    // Cerrar notificación
    const closeNotification = () => {
      showNotification.value = false;
    };

    // Cargar datos cuando cambia la pestaña activa
    watch(currentTab, (newValue) => {
      if (newValue === 'pending') {
        retryLoadWithBackoff('pendiente');
      } else if (newValue === 'active') {
        retryLoadWithBackoff('activo');
      } else if (newValue === 'rejected') {
        retryLoadWithBackoff('rechazado');
      }
    });

    // Cargar datos al montar el componente
    onMounted(() => {
      // Verificar si hay información de autenticación
      const token = localStorage.getItem('token');
      const userRole = localStorage.getItem('user_role');

      if (!token) {
        errorState.value = {
          hasError: true,
          message: 'No se ha iniciado sesión',
          details: 'Por favor, inicie sesión para acceder a esta página'
        };
        return;
      }

      if (userRole !== 'admin') {
        errorState.value = {
          hasError: true,
          message: 'Permisos insuficientes',
          details: 'Solo los administradores pueden acceder a esta página'
        };
        return;
      }

      console.log('Iniciando carga de usuarios pendientes...');
      retryLoadWithBackoff('pendiente');
    });

    return {
      // Estados
      tabs,
      currentTab,
      pendingUsers,
      activeUsers,
      rejectedUsers,
      isLoading,
      pendingCount,
      errorState,

      // Estados de modales
      showConfirmModal,
      confirmTitle,
      confirmMessage,
      confirmIcon,
      confirmButtonText,
      confirmButtonClass,
      confirmAction,
      selectedUser,
      showRejectReason,
      rejectReason,
      showUserDetailsModal,
      showUserFormModal,
      editingUser,
      isProcessingUserForm,
      userFormMode,
      showResetPasswordModal,
      isResetting,
      showImportModal,
      isImporting,

      // Estados de notificación
      showNotification,
      notificationTitle,
      notificationMessage,
      notificationIcon,
      notificationType,

      // Métodos
      changeTab,
      loadUsers,
      retryLoadWithBackoff,
      approveUser,
      rejectUser,
      deactivateUser,
      deleteUser,
      viewUserDetails,
      openCreateUserModal,
      openEditModal,
      saveUser,
      cancelConfirmAction,
      closeUserDetailsModal,
      closeUserFormModal,
      resetUserPassword,
      closeResetPasswordModal,
      confirmResetPassword,
      openImportUsersModal,
      closeImportModal,
      importUsers,
      closeNotification
    };
  }
};
</script>


<style scoped>
/* =================== CONTENEDOR PRINCIPAL =================== */
.user-management-wrapper {
  padding: 1.5rem;
  margin-left: 10px;
  min-height: 100vh;
  background-color: var(--color-bg-main);
  color: var(--color-text-primary);
}

.box.form-container {
  background-color: var(--color-bg-main);
  border-radius: var(--border-radius-lg);
  border-top: 4px solid var(--color-primary);
  box-shadow: var(--shadow-lg);
  width: 100%;
  margin: 0 auto;
  padding: 2rem;
}

/* =================== SECCIÓN DE CABECERA =================== */
.header-section {
  margin-bottom: 2rem;
  display: flex;
  justify-content: space-between;
  align-items: center;
  flex-wrap: wrap;
  gap: 1rem;
}

.header-content .title {
  color: var(--color-text-primary);
  margin-bottom: 0.5rem;
  font-weight: 600;
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.header-icon {
  font-size: 1.5rem;
}

.header-content .subtitle {
  color: var(--color-text-secondary);
  margin-top: 0;
}

/* =================== ACCIONES DEL HEADER =================== */
.header-actions {
  display: flex;
  gap: 0.75rem;
}

.action-btn {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.5rem 1rem;
  border-radius: var(--border-radius-sm);
  font-weight: 500;
  transition: all var(--transition-fast);
  cursor: pointer;
}

.create-btn {
  background-color: var(--color-primary);
  color: var(--color-bg-main);
  border: none;
}

.create-btn:hover {
  background-color: var(--color-primary-dark);
  transform: translateY(-1px);
  box-shadow: var(--shadow-sm);
}

.import-btn {
  background-color: var(--color-bg-element);
  color: var(--color-text-primary);
  border: 1px solid var(--color-border);
}

.import-btn:hover {
  background-color: var(--color-bg-element-hover);
  color: var(--color-primary-light);
  border-color: var(--color-primary);
}

/* =================== SISTEMA DE TABS =================== */
.tabs-container {
  display: flex;
  background-color: var(--color-bg-element);
  border-radius: var(--border-radius);
  margin-bottom: 2rem;
  overflow: hidden;
  border: 1px solid var(--color-border);
}

.tab {
  flex: 1;
  padding: 1.25rem;
  text-align: center;
  cursor: pointer;
  transition: all var(--transition-fast);
  color: var(--color-text-secondary);
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  position: relative;
  border-bottom: 3px solid transparent;
}

.tab:hover {
  background-color: var(--color-bg-element-hover);
  color: var(--color-text-primary);
}

.tab.active-tab {
  background-color: var(--color-bg-element-hover);
  color: var(--color-primary);
  border-bottom-color: var(--color-primary);
}

.tab-icon {
  font-size: 1.5rem;
  margin-bottom: 0.5rem;
}

.tab-text {
  font-weight: 500;
}

/* =================== BADGE DE NOTIFICACIÓN =================== */
.badge {
  position: absolute;
  top: 10px;
  right: 10px;
  background-color: var(--color-error);
  color: white;
  border-radius: 50%;
  width: 24px;
  height: 24px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 0.8rem;
  font-weight: bold;
}

/* =================== LOADER =================== */
.loading-container {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 4rem 0;
  color: var(--color-text-secondary);
}

.loader {
  border: 4px solid var(--color-bg-element);
  border-top: 4px solid var(--color-primary);
  border-radius: 50%;
  width: 40px;
  height: 40px;
  animation: spin 1s linear infinite;
  margin-bottom: 1rem;
}

/* =================== ICONOS =================== */
.icon {
  opacity: 1;
}

/* =================== ANIMACIONES =================== */
@keyframes spin {
  0% {
    transform: rotate(0deg);
  }
  100% {
    transform: rotate(360deg);
  }
}

/* =================== MEDIA QUERIES =================== */
@media (max-width: 768px) {
  .user-management-wrapper {
    padding: 1rem;
    margin-left: 0;
  }

  .header-section {
    flex-direction: column;
    align-items: flex-start;
  }

  .header-actions {
    width: 100%;
    flex-direction: column;
  }

  .action-btn {
    width: 100%;
    justify-content: center;
  }

  .tabs-container {
    flex-direction: column;
  }

  .tab {
    padding: 1rem;
    flex-direction: row;
    justify-content: flex-start;
    gap: 1rem;
  }

  .tab-icon {
    margin-bottom: 0;
  }

  .badge {
    position: static;
    margin-left: auto;
  }
}
</style>