<!-- components/admin/PendingUsers.vue -->
<template>
    <div class="pending-users-container">
      <div v-if="users.length === 0" class="empty-state">
        <div class="empty-icon">📭</div>
        <h2 class="empty-title">No hay solicitudes pendientes</h2>
        <p class="empty-message">Cuando se registren nuevos usuarios, aparecerán aquí para su aprobación.</p>
      </div>
  
      <div v-else class="user-cards">
        <div v-for="user in users" :key="user.id" class="user-card">
          <div class="user-card-header">
            <div class="user-avatar">
              {{ getInitials(user.nombres, user.apellidos) }}
            </div>
            <div class="user-details">
              <h3 class="user-name">{{ user.nombres }} {{ user.apellidos }}</h3>
              <p class="user-id">
                <span class="id-icon">🆔</span> {{ user.identificacion }}
              </p>
              <p class="user-email">
                <span class="email-icon">📧</span> {{ user.email || 'No disponible' }}
              </p>
            </div>
            <div class="role-badge" :class="user.rol">
              <span class="role-icon">
                <span v-if="user.rol === 'estudiante'">👨‍🎓</span>
                <span v-else-if="user.rol === 'docente'">👨‍🏫</span>
                <span v-else>👑</span>
              </span>
              {{ user.rol }}
            </div>
          </div>
  
          <div class="user-card-body">
            <div class="user-info-grid">
              <div class="info-item" v-if="user.rol === 'estudiante'">
                <span class="info-icon">📚</span>
                <span class="info-label">Curso:</span>
                <span class="info-value">{{ getCursoNombre(user.curso) }} "{{ user.paralelo }}"</span>
              </div>
              <div class="info-item" v-if="user.rol === 'docente' && user.especializacion">
                <span class="info-icon">🎓</span>
                <span class="info-label">Especialización:</span>
                <span class="info-value">{{ user.especializacion }}</span>
              </div>
              <div class="info-item" v-if="user.genero">
                <span class="info-icon">👤</span>
                <span class="info-label">Género:</span>
                <span class="info-value">{{ capitalizeFirst(user.genero) }}</span>
              </div>
              <div class="info-item" v-if="user.edad">
                <span class="info-icon">🔢</span>
                <span class="info-label">Edad:</span>
                <span class="info-value">{{ user.edad }} años</span>
              </div>
              <div class="info-item" v-if="user.turno">
                <span class="info-icon">🕒</span>
                <span class="info-label">Turno:</span>
                <span class="info-value">{{ capitalizeFirst(user.turno) }}</span>
              </div>
              <div class="info-item">
                <span class="info-icon">📆</span>
                <span class="info-label">Solicitud:</span>
                <span class="info-value">{{ formatDate(user.fecha_registro || new Date()) }}</span>
              </div>
            </div>
          </div>
  
          <div class="user-card-footer">
            <button class="button approve-btn" @click="$emit('approve-user', user)">
              <span class="button-icon">✅</span>
              <span>Aprobar</span>
            </button>
            <button class="button reject-btn" @click="$emit('reject-user', user)">
              <span class="button-icon">❌</span>
              <span>Rechazar</span>
            </button>
          </div>
        </div>
      </div>
    </div>
  </template>
  
  <script>
  export default {
    name: 'PendingUsers',
    props: {
      users: {
        type: Array,
        required: true
      }
    },
    methods: {
      // Obtener iniciales para avatar
      getInitials(nombres, apellidos) {
        let initials = '';
        if (nombres) {
          initials += nombres.charAt(0).toUpperCase();
        }
        if (apellidos) {
          initials += apellidos.charAt(0).toUpperCase();
        }
        return initials || '?';
      },
  
      // Formatear fecha
      formatDate(date) {
        if (!date) return 'N/A';
        
        const d = new Date(date);
        return d.toLocaleDateString('es-ES', {
          day: '2-digit',
          month: '2-digit',
          year: 'numeric',
          hour: '2-digit',
          minute: '2-digit'
        });
      },
  
      // Capitalizar primera letra
      capitalizeFirst(text) {
        if (!text) return '';
        return text.charAt(0).toUpperCase() + text.slice(1);
      },
  
      // Obtener nombre del curso
      getCursoNombre(curso) {
        const cursos = {
          '1': '1ro de Bachillerato',
          '2': '2do de Bachillerato',
          '3': '3ro de Bachillerato',
          '8': '8vo de Básica',
          '9': '9no de Básica',
          '10': '10mo de Básica'
        };
        return cursos[curso] || `Curso ${curso}`;
      }
    }
  };
  </script>
  
  <style scoped>
  .pending-users-container {
    width: 100%;
  }
  
  /* Estado vacío */
  .empty-state {
    text-align: center;
    padding: 3rem 0;
    background-color: var(--color-bg-element);
    border-radius: var(--border-radius);
    border: 2px dashed var(--color-border);
    margin-top: 1rem;
  }
  
  .empty-icon {
    font-size: 3.5rem;
    margin-bottom: 1rem;
    color: var(--color-primary-light);
    opacity: 0.7;
  }
  
  .empty-title {
    color: var(--color-text-primary);
    font-size: 1.5rem;
    margin-bottom: 0.75rem;
  }
  
  .empty-message {
    color: var(--color-text-secondary);
    max-width: 400px;
    margin: 0 auto;
  }
  
  /* Tarjetas de usuario */
  .user-cards {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(350px, 1fr));
    gap: 1.5rem;
  }
  
  .user-card {
    background-color: var(--color-bg-element);
    border-radius: var(--border-radius);
    overflow: hidden;
    transition: transform var(--transition-fast), box-shadow var(--transition-fast);
    box-shadow: var(--shadow);
    border: 1px solid var(--color-border);
    display: flex;
    flex-direction: column;
  }
  
  .user-card:hover {
    transform: translateY(-5px);
    box-shadow: var(--shadow-lg);
    border-color: var(--color-primary-light);
  }
  
  .user-card-header {
    padding: 1.25rem;
    display: flex;
    align-items: center;
    gap: 1rem;
    background-color: var(--color-bg-element-alt);
    border-bottom: 1px solid var(--color-border);
    position: relative;
  }
  
  .user-avatar {
    width: 50px;
    height: 50px;
    border-radius: 50%;
    background-color: var(--color-primary);
    color: var(--color-bg-element);
    display: flex;
    align-items: center;
    justify-content: center;
    font-weight: bold;
    font-size: 1.2rem;
    flex-shrink: 0;
  }
  
  .user-details {
    flex-grow: 1;
    min-width: 0;
  }
  
  .user-name {
    font-size: 1.1rem;
    font-weight: 600;
    color: var(--color-text-primary);
    margin-bottom: 0.25rem;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
  }
  
  .user-id, .user-email {
    font-size: 0.9rem;
    color: var(--color-text-secondary);
    margin-bottom: 0.25rem;
    display: flex;
    align-items: center;
    gap: 0.5rem;
  }
  
  .id-icon, .email-icon {
    color: var(--color-primary-light);
  }
  
  .role-badge {
    position: absolute;
    top: 10px;
    right: 10px;
    padding: 0.25rem 0.75rem;
    border-radius: 20px;
    font-size: 0.85rem;
    font-weight: 500;
    display: flex;
    align-items: center;
    gap: 0.5rem;
  }
  
  .role-badge.estudiante {
    background-color: rgba(157, 190, 182, 0.2);
    color: var(--color-success);
  }
  
  .role-badge.docente {
    background-color: rgba(101, 177, 193, 0.2);
    color: var(--color-info);
  }
  
  .role-badge.admin {
    background-color: rgba(255, 189, 46, 0.2);
    color: var(--color-warning);
  }
  
  .user-card-body {
    padding: 1.25rem;
    flex-grow: 1;
  }
  
  .user-info-grid {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
    gap: 0.75rem;
  }
  
  .info-item {
    display: flex;
    align-items: center;
    gap: 0.5rem;
    font-size: 0.9rem;
  }
  
  .info-icon {
    color: var(--color-primary-light);
    font-size: 1.1rem;
  }
  
  .info-label {
    color: var(--color-text-secondary);
    font-weight: 500;
  }
  
  .info-value {
    color: var(--color-text-primary);
  }
  
  .user-card-footer {
    padding: 1.25rem;
    display: flex;
    justify-content: center;
    gap: 1rem;
    background-color: var(--color-bg-element-alt);
    border-top: 1px solid var(--color-border);
  }
  
  /* Botones */
  .button {
    border-radius: var(--border-radius-sm);
    transition: all var(--transition-fast);
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 0.5rem;
    padding: 0.625rem 1.25rem;
    font-weight: 600;
  }
  
  .button-icon {
    font-size: 1.1rem;
  }
  
  .approve-btn {
    background-color: rgba(157, 190, 182, 0.2);
    color: var(--color-success);
    border: 1px solid var(--color-success);
  }
  
  .approve-btn:hover {
    background-color: var(--color-success);
    color: white;
  }
  
  .reject-btn {
    background-color: rgba(255, 107, 107, 0.2);
    color: var(--color-danger);
    border: 1px solid var(--color-danger);
  }
  
  .reject-btn:hover {
    background-color: var(--color-danger);
    color: white;
  }
  
  /* Responsive */
  @media (max-width: 768px) {
    .user-cards {
      grid-template-columns: 1fr;
    }
    
    .user-info-grid {
      grid-template-columns: 1fr;
    }
    
    .user-card-header {
      flex-direction: column;
      align-items: flex-start;
      text-align: center;
      padding-top: 3rem;
    }
    
    .role-badge {
      position: static;
      margin: 0.5rem auto;
    }
    
    .user-avatar {
      margin: 0 auto;
    }
    
    .user-details {
      width: 100%;
      text-align: center;
    }
    
    .user-id, .user-email {
      justify-content: center;
    }
    
    .user-card-footer {
      flex-direction: column;
    }
    
    .button {
      width: 100%;
    }
  }
  </style>