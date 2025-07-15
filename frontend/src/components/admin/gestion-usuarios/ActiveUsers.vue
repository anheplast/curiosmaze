<!-- src/components/admin/gestion-usuarios/ActiveUsers.vue -->
<template>
  <div class="active-users-container">
    <div class="filters-section">
      <div class="field has-addons search-container">
        <div class="control has-icons-left is-expanded">
          <input class="input" type="text" v-model="searchQuery" placeholder="Buscar por nombre, ID o correo..." />
          <span class="icon is-small is-left">
            <span>🔍</span>
          </span>
        </div>
      </div>

      <div class="select-filters">
        <div class="field">
          <div class="control">
            <div class="select">
              <select v-model="roleFilter">
                <option value="todos">Todos los roles</option>
                <option value="estudiante">Estudiantes</option>
                <option value="docente">Docentes</option>
                <option value="admin">Administradores</option>
              </select>
            </div>
          </div>
        </div>
      </div>
    </div>

    <div v-if="filteredUsers.length === 0" class="empty-state">
      <div class="empty-icon">👥</div>
      <h2 class="empty-title">No hay usuarios activos</h2>
      <p class="empty-message" v-if="searchQuery || roleFilter !== 'todos'">
        No se encontraron usuarios con los filtros actuales.
        <a href="#" @click.prevent="clearFilters">Limpiar filtros</a>
      </p>
      <p class="empty-message" v-else>
        No hay usuarios activos en el sistema.
      </p>
    </div>

    <div v-else class="user-table-container">
      <table class="table is-fullwidth">
        <thead>
          <tr>
            <th>Usuario</th>
            <th>Rol</th>
            <th>Identificación</th>
            <th>Correo</th>
            <th>Estado</th>
            <th>Acciones</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="user in filteredUsers" :key="user.id">
            <td>
              <div class="user-cell">
                <div class="user-avatar-small">{{ getInitials(user.nombres, user.apellidos) }}</div>
                <div class="user-info">
                  <div class="user-name-small">{{ user.nombres }} {{ user.apellidos }}</div>
                </div>
              </div>
            </td>
            <td>
              <div class="role-tag" :class="user.rol">{{ user.rol }}</div>
            </td>
            <td>{{ user.identificacion }}</td>
            <td>{{ user.email || 'No disponible' }}</td>
            <td>
              <span class="status-tag active">
                <span class="status-icon">🟢</span>
                Activo
              </span>
            </td>
            <td class="actions-cell">
              <div class="action-buttons">
                <button class="button is-small view-btn" title="Ver detalles" @click="$emit('view-user', user)">
                  <span>👁️</span>
                </button>
                <button class="button is-small edit-btn" title="Editar" @click="$emit('edit-user', user)">
                  <span>✏️</span>
                </button>
                <button class="button is-small password-btn" title="Resetear contraseña"
                  @click="$emit('reset-password', user)">
                  <span>🔑</span>
                </button>
                <button class="button is-small deactivate-btn" title="Desactivar"
                  @click="$emit('deactivate-user', user)">
                  <span>🚫</span>
                </button>
              </div>
            </td>
          </tr>
        </tbody>
      </table>

      <!-- Paginación -->
      <div class="pagination-container" v-if="totalPages > 1">
        <div class="pagination">
          <button class="pagination-previous" :disabled="currentPage === 1" @click="currentPage--">
            ⬅️
          </button>

          <ul class="pagination-list">
            <li v-for="page in displayedPages" :key="page">
              <a class="pagination-link" :class="{ 'is-current': page === currentPage }" @click="currentPage = page">
                {{ page }}
              </a>
            </li>
          </ul>

          <button class="pagination-next" :disabled="currentPage === totalPages" @click="currentPage++">
            ➡️
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, computed, watch } from 'vue';

export default {
  name: 'ActiveUsers',
  props: {
    users: {
      type: Array,
      required: true
    }
  },
  setup(props) {
    // Estados para filtrado
    const searchQuery = ref('');
    const roleFilter = ref('todos');

    // Estados para paginación
    const currentPage = ref(1);
    const perPage = ref(10);

    // Usuarios filtrados
    const filteredUsers = computed(() => {
      let filtered = [...props.users];

      // Filtrar por texto de búsqueda
      if (searchQuery.value) {
        const query = searchQuery.value.toLowerCase();
        filtered = filtered.filter(user =>
          (user.nombres && user.nombres.toLowerCase().includes(query)) ||
          (user.apellidos && user.apellidos.toLowerCase().includes(query)) ||
          (user.email && user.email.toLowerCase().includes(query)) ||
          (user.identificacion && user.identificacion.toLowerCase().includes(query))
        );
      }

      // Filtrar por rol
      if (roleFilter.value !== 'todos') {
        filtered = filtered.filter(user => user.rol === roleFilter.value);
      }

      // Calcular total de páginas
      const total = Math.ceil(filtered.length / perPage.value);
      totalPages.value = total;

      // Si la página actual es mayor que el total de páginas, resetear a 1
      if (currentPage.value > total && total > 0) {
        currentPage.value = 1;
      }

      // Paginar resultados
      const start = (currentPage.value - 1) * perPage.value;
      const end = start + perPage.value;

      return filtered.slice(start, end);
    });

    // Total de páginas para paginación
    const totalPages = ref(1);

    // Calcular qué páginas mostrar en la paginación
    const displayedPages = computed(() => {
      const pages = [];
      const maxButtons = 5; // Máximo número de botones a mostrar

      if (totalPages.value <= maxButtons) {
        // Si hay menos páginas que botones, mostrar todas
        for (let i = 1; i <= totalPages.value; i++) {
          pages.push(i);
        }
      } else {
        // Si hay más páginas que botones, mostrar un subconjunto
        if (currentPage.value <= maxButtons - 2) {
          // Estamos cerca del inicio
          for (let i = 1; i <= maxButtons - 1; i++) {
            pages.push(i);
          }
          pages.push(totalPages.value);
        } else if (currentPage.value >= totalPages.value - (maxButtons - 3)) {
          // Estamos cerca del final
          pages.push(1);
          for (let i = totalPages.value - (maxButtons - 2); i <= totalPages.value; i++) {
            pages.push(i);
          }
        } else {
          // Estamos en el medio
          pages.push(1);
          for (let i = currentPage.value - 1; i <= currentPage.value + 1; i++) {
            pages.push(i);
          }
          pages.push(totalPages.value);
        }
      }

      return pages;
    });

    // Limpiar filtros
    const clearFilters = () => {
      searchQuery.value = '';
      roleFilter.value = 'todos';
      currentPage.value = 1;
    };

    // Reiniciar página cuando cambian los filtros
    watch([searchQuery, roleFilter], () => {
      currentPage.value = 1;
    });

    // Obtener iniciales para avatar
    const getInitials = (nombres, apellidos) => {
      let initials = '';
      if (nombres) {
        initials += nombres.charAt(0).toUpperCase();
      }
      if (apellidos) {
        initials += apellidos.charAt(0).toUpperCase();
      }
      return initials || '?';
    };

    return {
      searchQuery,
      roleFilter,
      currentPage,
      filteredUsers,
      totalPages,
      displayedPages,
      clearFilters,
      getInitials
    };
  }
};
</script>

<style scoped>
/* =================== CONTENEDOR PRINCIPAL =================== */
.active-users-container {
  width: 100%;
}

/* =================== SECCIÓN DE FILTROS =================== */
.filters-section {
  background-color: var(--color-bg-element);
  border-radius: var(--border-radius);
  padding: 1.25rem;
  margin-bottom: 1.5rem;
  display: flex;
  flex-wrap: wrap;
  gap: 1rem;
  align-items: center;
  border-left: 4px solid var(--color-primary);
}

.search-container {
  flex-grow: 1;
  min-width: 200px;
}

.search-container .input {
  background-color: var(--color-bg-main);
  border: 1px solid var(--color-border);
  color: var(--color-text-primary);
  padding-left: 2.5rem;
  height: 2.5rem;
  transition: border-color var(--transition-fast);
}

.search-container .input:focus {
  border-color: var(--color-border-focus);
  outline: none;
}

.search-container .icon.is-small.is-left {
  font-size: 1.25rem;
  color: var(--color-primary);
}

.select-filters {
  display: flex;
  gap: 0.75rem;
  flex-wrap: wrap;
}

.select-filters .select select {
  background-color: var(--color-bg-main);
  border: 1px solid var(--color-border);
  color: var(--color-text-primary);
  height: 2.5rem;
  padding: 0 1rem;
  transition: border-color var(--transition-fast);
}

.select-filters .select select:focus {
  border-color: var(--color-border-focus);
  outline: none;
}

/* =================== ESTADO VACÍO =================== */
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

.empty-message a {
  color: var(--color-primary);
  text-decoration: underline;
  margin-left: 0.5rem;
  transition: color var(--transition-fast);
}

.empty-message a:hover {
  color: var(--color-primary-light);
}

/* =================== TABLA DE USUARIOS =================== */
.user-table-container {
  overflow-x: auto;
  background-color: var(--color-bg-element);
  border-radius: var(--border-radius);
  margin-top: 1rem;
}

.table {
  width: 100%;
  border-collapse: separate;
  border-spacing: 0;
  color: var(--color-text-primary);
  background-color: var(--color-bg-element);
}

.table thead th {
  background-color: var(--color-bg-element-alt);
  color: var(--color-text-secondary);
  padding: 1rem;
  font-weight: 600;
  text-align: left;
  border-bottom: 1px solid var(--color-border);
}

.table tbody td {
  padding: 1rem;
  border-bottom: 1px solid var(--color-border);
  vertical-align: middle;
}

.table tbody tr:hover {
  background-color: var(--color-bg-element-hover);
}

/* =================== CÉLULAS DE USUARIO =================== */
.user-cell {
  display: flex;
  align-items: center;
  gap: 0.75rem;
}

.user-avatar-small {
  width: 36px;
  height: 36px;
  border-radius: 50%;
  background-color: var(--color-primary);
  color: var(--color-bg-element);
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: bold;
  font-size: 1rem;
}

.user-name-small {
  font-weight: 600;
  color: var(--color-text-primary);
}

/* =================== ETIQUETAS Y BADGES =================== */
.role-tag {
  display: inline-flex;
  align-items: center;
  padding: 0.25rem 0.75rem;
  border-radius: 20px;
  font-size: 0.85rem;
  font-weight: 500;
}

.role-tag.estudiante {
  background-color: var(--color-success-bg);
  color: var(--color-success);
}

.role-tag.docente {
  background-color: var(--color-info-bg);
  color: var(--color-info);
}

.role-tag.admin {
  background-color: var(--color-warning-bg);
  color: var(--color-warning);
}

.status-tag {
  display: inline-flex;
  align-items: center;
  padding: 0.25rem 0.75rem;
  border-radius: 20px;
  font-size: 0.85rem;
  font-weight: 500;
  gap: 0.5rem;
}

.status-tag.active {
  background-color: var(--color-success-bg);
  color: var(--color-success);
}

/* =================== ACCIONES =================== */
.actions-cell {
  width: 160px;
}

.action-buttons {
  display: flex;
  gap: 0.5rem;
}

.action-buttons .button {
  padding: 0.4rem;
  width: 32px;
  height: 32px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1rem;
  border: 1px solid var(--color-border);
  background-color: var(--color-bg-main);
  transition: all var(--transition-fast);
  cursor: pointer;
}

.button.view-btn:hover {
  background-color: var(--color-info);
  color: white;
  border-color: var(--color-info);
}

.button.edit-btn:hover {
  background-color: var(--color-primary);
  color: white;
  border-color: var(--color-primary);
}

.button.password-btn:hover {
  background-color: var(--color-warning);
  color: white;
  border-color: var(--color-warning);
}

.button.deactivate-btn:hover {
  background-color: var(--color-error);
  color: white;
  border-color: var(--color-error);
}

/* =================== PAGINACIÓN =================== */
.pagination-container {
  padding: 1.25rem;
  display: flex;
  justify-content: center;
  border-top: 1px solid var(--color-border);
}

.pagination {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.pagination-previous,
.pagination-next {
  background-color: var(--color-bg-main);
  border: 1px solid var(--color-border);
  color: var(--color-text-primary);
  padding: 0.5rem 0.75rem;
  border-radius: var(--border-radius-sm);
  cursor: pointer;
  font-size: 0.9rem;
  transition: all var(--transition-fast);
}

.pagination-previous:hover:not(:disabled),
.pagination-next:hover:not(:disabled) {
  background-color: var(--color-primary);
  color: white;
  border-color: var(--color-primary);
}

.pagination-previous:disabled,
.pagination-next:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.pagination-list {
  display: flex;
  align-items: center;
  gap: 0.25rem;
  list-style: none;
  margin: 0;
  padding: 0;
}

.pagination-link {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 2rem;
  height: 2rem;
  border-radius: var(--border-radius-sm);
  background-color: var(--color-bg-main);
  border: 1px solid var(--color-border);
  color: var(--color-text-primary);
  cursor: pointer;
  transition: all var(--transition-fast);
}

.pagination-link:hover:not(.is-current) {
  background-color: var(--color-bg-element-hover);
  color: var(--color-primary-light);
}

.pagination-link.is-current {
  background-color: var(--color-primary);
  border-color: var(--color-primary);
  color: white;
}

/* =================== MEDIA QUERIES =================== */
@media (max-width: 768px) {
  .filters-section {
    flex-direction: column;
  }

  .select-filters,
  .search-container {
    width: 100%;
  }

  .action-buttons {
    flex-wrap: wrap;
    justify-content: center;
  }

  .action-buttons .button {
    margin-bottom: 0.5rem;
  }

  .actions-cell {
    width: auto;
  }

  .table thead {
    display: none;
  }

  .table,
  .table tbody,
  .table tr,
  .table td {
    display: block;
    width: 100%;
  }

  .table tr {
    margin-bottom: 1rem;
    border: 1px solid var(--color-border);
    border-radius: var(--border-radius);
    padding: 0.5rem;
  }

  .table td {
    display: flex;
    align-items: center;
    justify-content: space-between;
    border-bottom: 1px dashed var(--color-border);
    padding: 0.75rem 0;
  }

  .table td:before {
    content: attr(data-label);
    font-weight: 600;
    margin-right: 1rem;
  }

  .table td:last-child {
    border-bottom: none;
  }

  .user-cell {
    width: 100%;
    justify-content: flex-start;
  }
}
</style>