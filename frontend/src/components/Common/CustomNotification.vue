<!-- components/common/CustomNotification.vue -->
<template>
    <div class="notification" :class="type" role="alert">
      <div class="notification-content">
        <span class="notification-icon">{{ icon }}</span>
        <div class="notification-text">
          <div class="notification-title">{{ title }}</div>
          <div class="notification-message">{{ message }}</div>
        </div>
      </div>
      <button class="notification-close" @click="$emit('close')">×</button>
    </div>
  </template>
  
  <script>
  export default {
    name: 'CustomNotification',
    props: {
      title: {
        type: String,
        required: true
      },
      message: {
        type: String,
        required: true
      },
      icon: {
        type: String,
        default: 'ℹ️'
      },
      type: {
        type: String,
        default: 'info',
        validator: (value) => ['info', 'success', 'warning', 'danger'].includes(value)
      }
    }
  };
  </script>
  
  <style scoped>
  .notification {
    position: fixed;
    bottom: 30px;
    right: 30px;
    background-color: var(--color-bg-element);
    color: var(--color-text-primary);
    padding: 1rem;
    border-radius: var(--border-radius);
    box-shadow: var(--shadow-lg);
    z-index: 1000;
    min-width: 300px;
    max-width: 400px;
    animation: slide-in 0.3s ease-out forwards;
    display: flex;
    justify-content: space-between;
    align-items: flex-start;
    border-left: 4px solid var(--color-secondary);
  }
  
  .notification.info {
    border-left-color: var(--color-info);
  }
  
  .notification.success {
    border-left-color: var(--color-success);
  }
  
  .notification.warning {
    border-left-color: var(--color-warning);
  }
  
  .notification.danger {
    border-left-color: var(--color-danger);
  }
  
  .notification-content {
    display: flex;
    gap: 0.75rem;
  }
  
  .notification-icon {
    font-size: 1.5rem;
  }
  
  .notification-text {
    flex: 1;
  }
  
  .notification-title {
    font-weight: bold;
    margin-bottom: 0.25rem;
    font-size: 1rem;
  }
  
  .notification-message {
    font-size: 0.9rem;
    color: var(--color-text-secondary);
  }
  
  .notification-close {
    background: transparent;
    border: none;
    color: var(--color-text-secondary);
    font-size: 1.2rem;
    cursor: pointer;
    padding: 0;
    height: 24px;
    width: 24px;
    display: flex;
    align-items: center;
    justify-content: center;
    transition: color 0.2s;
  }
  
  .notification-close:hover {
    color: var(--color-text-primary);
  }
  
  @keyframes slide-in {
    from {
      transform: translateX(100%);
      opacity: 0;
    }
    to {
      transform: translateX(0);
      opacity: 1;
    }
  }
  
  @media (max-width: 768px) {
    .notification {
      bottom: 20px;
      right: 20px;
      left: 20px;
      max-width: none;
    }
  }
  </style>