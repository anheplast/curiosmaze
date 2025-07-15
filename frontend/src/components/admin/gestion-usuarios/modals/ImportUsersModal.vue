<!-- src/components/admin/gestion-usuarios/modals/ImportUsersModal.vue -->
<template>
    <div class="modal is-active">
      <div class="modal-background" @click="$emit('cancel')"></div>
      <div class="modal-card">
        <header class="modal-card-head">
          <p class="modal-card-title">
            <span class="modal-title-icon">📥</span>
            Importar Usuarios
          </p>
          <button class="delete" aria-label="close" @click="$emit('cancel')"></button>
        </header>
        
        <section class="modal-card-body">
          <div v-if="importErrors.length > 0" class="import-errors">
            <div class="error-header">Se encontraron errores en el archivo:</div>
            <ul>
              <li v-for="(error, index) in importErrors" :key="index">{{ error }}</li>
            </ul>
          </div>
  
          <div class="import-content">
            <div class="import-icon">📄</div>
            <h3 class="import-title">Importar lista de usuarios</h3>
            
            <div class="import-info">
              <p>
                Puede importar múltiples usuarios a la vez utilizando un archivo CSV o Excel (.xlsx).
                El archivo debe contener las siguientes columnas:
              </p>
              
              <div class="columns-info">
                <div class="column-group">
                  <div class="column-title">Columnas obligatorias:</div>
                  <ul class="column-list">
                    <li><span class="column-name">identificacion</span> - Número de identidad único</li>
                    <li><span class="column-name">nombres</span> - Nombres del usuario</li>
                    <li><span class="column-name">apellidos</span> - Apellidos del usuario</li>
                    <li><span class="column-name">rol</span> - Rol del usuario (estudiante, docente, admin)</li>
                  </ul>
                </div>
                
                <div class="column-group">
                  <div class="column-title">Columnas opcionales:</div>
                  <ul class="column-list">
                    <li><span class="column-name">email</span> - Correo electrónico</li>
                    <li><span class="column-name">curso</span> - Curso (para estudiantes)</li>
                    <li><span class="column-name">paralelo</span> - Paralelo (para estudiantes)</li>
                    <li><span class="column-name">especializacion</span> - Especialización (para docentes)</li>
                    <li><span class="column-name">genero</span> - Género (masculino, femenino)</li>
                    <li><span class="column-name">edad</span> - Edad</li>
                    <li><span class="column-name">turno</span> - Turno (mañana, tarde)</li>
                  </ul>
                </div>
              </div>
              
              <div class="template-download">
                <button class="button template-btn" @click="downloadTemplate">
                  <span class="button-icon">📝</span>
                  <span>Descargar Plantilla</span>
                </button>
              </div>
            </div>
            
            <div class="file-upload-section">
              <div class="file-drop-area" 
                :class="{ 'is-dragover': isDragOver, 'has-file': !!selectedFile }"
                @dragover.prevent="isDragOver = true"
                @dragleave.prevent="isDragOver = false"
                @drop.prevent="handleFileDrop"
                @click="triggerFileInput"
              >
                <input 
                  type="file" 
                  ref="fileInput" 
                  class="file-input" 
                  accept=".csv,.xlsx,.xls"
                  @change="handleFileSelect"
                >
                <div class="drop-icon">{{ selectedFile ? '📄' : '📥' }}</div>
                <div class="drop-message" v-if="!selectedFile">
                  Arrastre y suelte su archivo aquí<br>
                  <span class="drop-submessage">o haga clic para seleccionar</span>
                </div>
                <div class="file-info" v-else>
                  <div class="file-name">{{ selectedFile.name }}</div>
                  <div class="file-size">{{ formatFileSize(selectedFile.size) }}</div>
                </div>
              </div>
              
              <div class="import-options">
                <div class="field">
                  <label class="checkbox">
                    <input type="checkbox" v-model="options.updateExisting">
                    Actualizar usuarios existentes
                  </label>
                </div>
  
                <div class="field">
                  <label class="checkbox">
                    <input type="checkbox" v-model="options.generatePasswords">
                    Generar contraseñas automáticamente
                  </label>
                  <p class="help">Si no se marca, se usará la identificación como contraseña inicial</p>
                </div>
              </div>
            </div>
          </div>
        </section>
        
        <footer class="modal-card-foot">
          <button class="button cancel-btn" @click="$emit('cancel')">Cancelar</button>
          <button 
            class="button import-btn" 
            @click="importUsers" 
            :disabled="isLoading || !selectedFile"
          >
            <span class="button-icon">{{ isLoading ? '⏳' : '📥' }}</span>
            <span>{{ isLoading ? 'Importando...' : 'Importar Usuarios' }}</span>
          </button>
        </footer>
      </div>
    </div>
  </template>
  
  <script>
  import { ref, reactive } from 'vue';
  
  export default {
    name: 'ImportUsersModal',
    props: {
      isLoading: {
        type: Boolean,
        default: false
      }
    },
    setup(props, { emit }) {
      const fileInput = ref(null);
      const selectedFile = ref(null);
      const isDragOver = ref(false);
      const importErrors = ref([]);
      
      // Opciones de importación
      const options = reactive({
        updateExisting: true,
        generatePasswords: false
      });
      
      // Disparar clic en input file
      const triggerFileInput = () => {
        fileInput.value.click();
      };
      
      // Manejar selección de archivo
      const handleFileSelect = (event) => {
        const file = event.target.files[0];
        if (file) {
          validateFile(file);
        }
      };
      
      // Manejar drop de archivo
      const handleFileDrop = (event) => {
        isDragOver.value = false;
        const file = event.dataTransfer.files[0];
        if (file) {
          validateFile(file);
        }
      };
      
      // Validar archivo
      const validateFile = (file) => {
        importErrors.value = [];
        
        // Validar extensión
        const validExtensions = ['.csv', '.xlsx', '.xls'];
        const fileExtension = file.name.substring(file.name.lastIndexOf('.')).toLowerCase();
        
        if (!validExtensions.includes(fileExtension)) {
          importErrors.value.push(`Formato de archivo no válido. Por favor, utilice ${validExtensions.join(', ')}`);
          return;
        }
        
        // Validar tamaño (máximo 5MB)
        const maxSize = 5 * 1024 * 1024; // 5MB
        if (file.size > maxSize) {
          importErrors.value.push(`El archivo es demasiado grande. El tamaño máximo es ${formatFileSize(maxSize)}`);
          return;
        }
        
        // Si pasa todas las validaciones, guardar archivo
        selectedFile.value = file;
      };
      
      // Formatear tamaño de archivo
      const formatFileSize = (sizeInBytes) => {
        if (sizeInBytes < 1024) {
          return `${sizeInBytes} bytes`;
        } else if (sizeInBytes < 1024 * 1024) {
          return `${(sizeInBytes / 1024).toFixed(2)} KB`;
        } else {
          return `${(sizeInBytes / (1024 * 1024)).toFixed(2)} MB`;
        }
      };
      
      // Descargar plantilla
      const downloadTemplate = () => {
        // Crear contenido CSV
        const headers = 'identificacion,nombres,apellidos,rol,email,curso,paralelo,especializacion,genero,edad,turno\n';
        const examples = [
          '1234567890,Juan,Pérez,estudiante,juan@example.com,1,A,,masculino,15,mañana',
          '0987654321,María,García,docente,maria@example.com,,,Matemáticas,femenino,35,tarde',
          '5555555555,Admin,Sistema,admin,admin@example.com,,,,masculino,30,'
        ].join('\n');
        
        const csvContent = headers + examples;
        
        // Crear blob y descargar
        const blob = new Blob([csvContent], { type: 'text/csv' });
        const url = URL.createObjectURL(blob);
        
        const a = document.createElement('a');
        a.href = url;
        a.download = 'plantilla_usuarios.csv';
        document.body.appendChild(a);
        a.click();
        
        // Limpiar
        setTimeout(() => {
          document.body.removeChild(a);
          URL.revokeObjectURL(url);
        }, 0);
      };
      
      // Importar usuarios
      const importUsers = () => {
        if (!selectedFile.value) return;
        
        // Crear FormData para envío de archivo
        const formData = new FormData();
        formData.append('file', selectedFile.value);
        formData.append('updateExisting', options.updateExisting);
        formData.append('generatePasswords', options.generatePasswords);
        
        // Emitir evento para importar
        emit('import', formData);
      };
      
      return {
        fileInput,
        selectedFile,
        isDragOver,
        importErrors,
        options,
        triggerFileInput,
        handleFileSelect,
        handleFileDrop,
        formatFileSize,
        downloadTemplate,
        importUsers
      };
    }
  };
  </script>
  
  <style scoped>
  .modal-card {
    background-color: var(--color-bg-element);
    border-radius: var(--border-radius);
    overflow: hidden;
    width: 90%;
    max-width: 700px;
    margin: 0 auto;
  }
  
  .modal-card-head {
    background-color: var(--color-primary);
    padding: 1.25rem;
    border-bottom: none;
  }
  
  .modal-card-title {
    color: white;
    font-weight: 600;
    display: flex;
    align-items: center;
    gap: 0.75rem;
  }
  
  .modal-title-icon {
    font-size: 1.5rem;
  }
  
  .modal-card-body {
    background-color: var(--color-bg-element);
    padding: 2rem;
    color: var(--color-text-primary);
    max-height: 70vh;
    overflow-y: auto;
  }
  
  .modal-card-foot {
    background-color: var(--color-bg-element-alt);
    padding: 1.25rem;
    justify-content: flex-end;
    border-top: 1px solid var(--color-border);
  }
  
  .cancel-btn {
    background-color: var(--color-bg-main);
    color: var(--color-text-primary);
    border: 1px solid var(--color-border);
    margin-right: 0.75rem;
  }
  
  .import-btn {
    background-color: var(--color-primary);
    color: var(--color-bg-main);
    border: none;
    display: flex;
    align-items: center;
    gap: 0.5rem;
  }
  
  .import-btn:disabled {
    opacity: 0.5;
    cursor: not-allowed;
  }
  
  .button-icon {
    font-size: 1.2rem;
  }
  
  /* Contenido */
  .import-content {
    display: flex;
    flex-direction: column;
    align-items: center;
  }
  
  .import-icon {
    font-size: 3rem;
    margin-bottom: 1rem;
  }
  
  .import-title {
    font-size: 1.25rem;
    font-weight: 600;
    margin-bottom: 1.5rem;
    color: var(--color-primary);
  }
  
  .import-info {
    margin-bottom: 2rem;
    background-color: var(--color-bg-element-alt);
    border-radius: var(--border-radius);
    padding: 1.5rem;
    border: 1px solid var(--color-border);
    width: 100%;
  }
  
  .import-info p {
    margin-bottom: 1rem;
    color: var(--color-text-secondary);
    line-height: 1.5;
  }
  
  .columns-info {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 1.5rem;
    margin-bottom: 1.5rem;
  }
  
  .column-title {
    font-weight: 600;
    margin-bottom: 0.75rem;
    color: var(--color-primary);
  }
  
  .column-list {
    padding-left: 1.25rem;
  }
  
  .column-list li {
    margin-bottom: 0.5rem;
    color: var(--color-text-secondary);
  }
  
  .column-name {
    color: var(--color-info);
    font-family: monospace;
    background-color: var(--color-bg-main);
    padding: 0.15rem 0.35rem;
    border-radius: 3px;
    font-size: 0.9rem;
  }
  
  .template-download {
    display: flex;
    justify-content: center;
    margin-top: 1rem;
  }
  
  .template-btn {
    background-color: var(--color-info);
    color: white;
    border: none;
    display: flex;
    align-items: center;
    gap: 0.5rem;
    padding: 0.5rem 1rem;
    border-radius: var(--border-radius-sm);
    transition: all var(--transition-fast);
  }
  
  .template-btn:hover {
    background-color: var(--color-info);
    opacity: 0.9;
  }
  
  /* Área de carga de archivos */
  .file-upload-section {
    width: 100%;
  }
  
  .file-drop-area {
    border: 2px dashed var(--color-border);
    border-radius: var(--border-radius);
    padding: 2rem;
    text-align: center;
    cursor: pointer;
    transition: all var(--transition-fast);
    position: relative;
    margin-bottom: 1.5rem;
  }
  
  .file-drop-area:hover {
    border-color: var(--color-primary);
  }
  
  .file-drop-area.is-dragover {
    border-color: var(--color-primary);
    background-color: rgba(235, 179, 0, 0.05);
  }
  
  .file-drop-area.has-file {
    border-color: var(--color-primary);
    background-color: rgba(235, 179, 0, 0.05);
  }
  
  .file-input {
    position: absolute;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    opacity: 0;
    cursor: pointer;
    z-index: -1;
  }
  
  .drop-icon {
    font-size: 3rem;
    margin-bottom: 1rem;
  }
  
  .drop-message {
    color: var(--color-text-secondary);
    font-size: 1.1rem;
  }
  
  .drop-submessage {
    font-size: 0.9rem;
    opacity: 0.7;
  }
  
  .file-info {
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 0.5rem;
  }
  
  .file-name {
    font-weight: 600;
    color: var(--color-primary);
  }
  
  .file-size {
    font-size: 0.9rem;
    color: var(--color-text-secondary);
  }
  
  /* Opciones de importación */
  .import-options {
    background-color: var(--color-bg-element-alt);
    border-radius: var(--border-radius);
    padding: 1.25rem;
    border: 1px solid var(--color-border);
  }
  
  .checkbox {
    display: flex;
    align-items: flex-start;
    gap: 0.5rem;
    color: var(--color-text-primary);
    cursor: pointer;
  }
  
  .checkbox input {
    margin-top: 0.25rem;
  }
  
  .help {
    margin-top: 0.25rem;
    margin-left: 1.5rem;
    font-size: 0.8rem;
    color: var(--color-text-secondary);
  }
  
  /* Errores de importación */
  .import-errors {
    background-color: rgba(255, 107, 107, 0.1);
    border: 1px solid var(--color-danger);
    border-radius: var(--border-radius);
    padding: 1rem;
    margin-bottom: 1.5rem;
    color: var(--color-danger);
  }
  
  .error-header {
    font-weight: 600;
    margin-bottom: 0.5rem;
  }
  
  .import-errors ul {
    padding-left: 1.5rem;
  }
  
  /* Responsive */
  @media (max-width: 768px) {
    .columns-info {
      grid-template-columns: 1fr;
      gap: 1rem;
    }
    
    .import-info,
    .file-drop-area {
      padding: 1rem;
    }
  }
  </style>