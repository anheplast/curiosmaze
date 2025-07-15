<!-- src/components/Common/NotificationSystem.vue -->
<template>
  <div class="notification-system">
    <!-- Área de notificaciones flotantes -->
    <div class="notifications-container">
      <transition-group name="notification" tag="div">
        <div
          v-for="notification in notifications"
          :key="notification.id"
          :class="['notification', `notification-${notification.type}`]"
        >
          <div class="notification-content">
            <span class="notification-icon">{{ getIcon(notification.type) }}</span>
            <span class="notification-message">{{ notification.message }}</span>
          </div>
          <button class="notification-close" @click="removeNotification(notification.id)">
            ×
          </button>
        </div>
      </transition-group>
    </div>

    <!-- Modal de confirmación -->
    <div class="modal-overlay" v-if="currentConfirmation">
      <div class="modal-card confirmation-modal">
        <div class="modal-header">
          <h3>
            <span class="modal-icon">❓</span>
            {{ currentConfirmation.title || 'Confirmación' }}
          </h3>
        </div>
        <div class="modal-body">
          <p>{{ currentConfirmation.message }}</p>
        </div>
        <div class="modal-footer">
          <button 
            class="modal-button cancel-button" 
            @click="handleConfirmation(false)"
          >
            {{ currentConfirmation.cancelText || 'Cancelar' }}
          </button>
          <button 
            class="modal-button confirm-button" 
            @click="handleConfirmation(true)"
          >
            {{ currentConfirmation.confirmText || 'Confirmar' }}
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, defineExpose } from 'vue';

const notifications = ref([]);
const currentConfirmation = ref(null);
let notificationId = 0;

const getIcon = (type) => {
  const icons = {
    info: 'ℹ️',
    success: '✅',
    warning: '⚠️',
    error: '❌'
  };
  return icons[type] || icons.info;
};

const showNotification = (message, type = 'info', duration = 3000) => {
  const id = ++notificationId;
  const notification = {
    id,
    message,
    type,
    duration
  };

  notifications.value.push(notification);

  if (duration !== 0) {
    setTimeout(() => {
      removeNotification(id);
    }, duration);
  }
};

const removeNotification = (id) => {
  const index = notifications.value.findIndex(n => n.id === id);
  if (index > -1) {
    notifications.value.splice(index, 1);
  }
};

const showConfirmation = (message, onConfirm, onCancel = null, options = {}) => {
  currentConfirmation.value = {
    message,
    onConfirm,
    onCancel,
    title: options.title,
    confirmText: options.confirmText,
    cancelText: options.cancelText
  };
};

const handleConfirmation = (confirmed) => {
  if (currentConfirmation.value) {
    if (confirmed && currentConfirmation.value.onConfirm) {
      currentConfirmation.value.onConfirm();
    } else if (!confirmed && currentConfirmation.value.onCancel) {
      currentConfirmation.value.onCancel();
    }
    currentConfirmation.value = null;
  }
};

// Exponer métodos públicos
defineExpose({
  showNotification,
  showConfirmation
});
</script>

<style scoped>
/* =================== CONTENEDOR PRINCIPAL =================== */
.notification-system {
  position: fixed;
  pointer-events: none;
  z-index: 9999;
}

.notifications-container {
  position: fixed;
  top: 20px;
  right: 20px;
  display: flex;
  flex-direction: column;
  gap: 12px;
  pointer-events: none;
}

/* =================== NOTIFICACIONES =================== */
.notification {
  background-color: var(--color-bg-element);
  border-radius: var(--border-radius);
  padding: 12px 16px;
  min-width: 300px;
  max-width: 500px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  box-shadow: var(--shadow);
  pointer-events: auto;
  transform-origin: top right;
  border-left: 4px solid transparent;
}

.notification-info {
  border-left-color: var(--color-info);
}

.notification-success {
  border-left-color: var(--color-success);
}

.notification-warning {
  border-left-color: var(--color-warning);
}

.notification-error {
  border-left-color: var(--color-error);
}

.notification-content {
  display: flex;
  align-items: center;
  gap: 12px;
}

.notification-icon {
  font-size: 20px;
}

.notification-message {
  color: var(--color-text-primary);
  font-weight: 500;
}

.notification-close {
  background: none;
  border: none;
  color: var(--color-text-secondary);
  font-size: 20px;
  cursor: pointer;
  padding: 0 8px;
  transition: all var(--transition-fast) ease;
}

.notification-close:hover {
  color: var(--color-text-primary);
}

/* =================== MODAL DE CONFIRMACIÓN =================== */
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-color: rgba(0, 0, 0, 0.7);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 10000;
  animation: fadeIn var(--transition-fast) ease-out;
  pointer-events: auto;
}

.modal-card {
  background-color: var(--color-bg-element);
  border-radius: var(--border-radius);
  width: 90%;
  max-width: 450px;
  box-shadow: var(--shadow-lg);
  animation: slideIn var(--transition-smooth) ease-out;
}

.modal-header {
  background-color: var(--color-primary);
  color: var(--color-bg-main);
  padding: 16px 20px;
  border-top-left-radius: var(--border-radius);
  border-top-right-radius: var(--border-radius);
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.modal-header h3 {
  font-size: 18px;
  font-weight: 600;
  display: flex;
  align-items: center;
  gap: 8px;
}

.modal-icon {
  font-size: 20px;
}

.modal-body {
  padding: 20px;
  color: var(--color-text-primary);
}

.modal-body p {
  line-height: 1.6;
  margin-bottom: 16px;
}

.modal-footer {
  padding: 16px 20px;
  display: flex;
  justify-content: center;
  gap: 16px;
  border-top: 1px solid var(--color-border);
}

/* =================== BOTONES DEL MODAL =================== */
.modal-button {
  padding: 10px 20px;
  border-radius: var(--border-radius);
  font-weight: 600;
  font-size: 14px;
  min-width: 120px;
  transition: all var(--transition-smooth) ease;
  cursor: pointer;
  border: none;
}

.modal-button:hover {
  transform: translateY(-2px);
}

.cancel-button {
  background-color: var(--color-bg-element-hover);
  color: var(--color-text-primary);
  border: 1px solid var(--color-border-light);
}

.cancel-button:hover {
  background-color: var(--color-border-light);
}

.confirm-button {
  background-color: var(--color-primary);
  color: var(--color-bg-main);
}

.confirm-button:hover {
  background-color: var(--color-primary-light);
  box-shadow: 0 4px 12px rgba(235, 179, 0, 0.3);
}

/* =================== ANIMACIONES =================== */
.notification-enter-active {
  animation: notificationEnter var(--transition-smooth) ease-out;
}

.notification-leave-active {
  animation: notificationLeave var(--transition-smooth) ease-in;
}

@keyframes notificationEnter {
  from {
    opacity: 0;
    transform: translateX(100%) scale(0.8);
  }
  to {
    opacity: 1;
    transform: translateX(0) scale(1);
  }
}

@keyframes notificationLeave {
  from {
    opacity: 1;
    transform: translateX(0) scale(1);
  }
  to {
    opacity: 0;
    transform: translateX(100%) scale(0.8);
  }
}

@keyframes fadeIn {
  from { opacity: 0; }
  to { opacity: 1; }
}

@keyframes slideIn {
  from {
    transform: translateY(-20px);
    opacity: 0;
  }
  to {
    transform: translateY(0);
    opacity: 1;
  }
}
</style>