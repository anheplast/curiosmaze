<!-- components/LoginBox.vue -->
<template>
  <div class="login-wrapper">
    <div class="login-container">
      <div class="left-section"></div>
      <div class="right-section">
        <div class="logos-container">
          <div class="logo-wrap"></div>
          <div class="logo-institucion"></div>
        </div>

        <!-- Contenedor de mensajes -->
        <div class="message-container">
          <div v-if="displayError" class="notification is-danger fixed-height">
            {{ errorMessage }}
          </div>
        </div>

        <!-- Formulario de Inicio de Sesión -->
        <form @submit.prevent="handleLogin" @keydown.enter="handleLogin">
          <div class="login-note">
            <span v-if="!passwordResetMode">Ingrese sus credenciales institucionales</span>
            <span v-else class="password-reset-note">Por favor, establezca una nueva contraseña</span>
          </div>

          <!-- Campo ID de Usuario -->
          <div class="field login-field">
            <div class="control has-icons-left">
              <input 
                class="input" 
                type="text" 
                placeholder="Número de identidad (ID No.)" 
                v-model="userId"
                :disabled="passwordResetMode"
                ref="userIdInput"
                @keyup.enter="!passwordResetMode ? focusPasswordField() : null"
              >
              <span class="icon-login-box is-small is-left">
                <i>
                  <IconUser />
                </i>
              </span>
            </div>
          </div>

          <template v-if="!passwordResetMode">
            <!-- Contraseña Normal -->
            <div class="field login-field">
              <div class="control has-icons-left">
                <input 
                  class="input" 
                  type="password" 
                  placeholder="Contraseña (Password)" 
                  v-model="password"
                  ref="passwordInput"
                  @keyup.enter="handleLogin"
                >
                <span class="icon-login-box is-left">
                  <i>
                    <IconLock />
                  </i>
                </span>
              </div>
            </div>
          </template>
          <template v-else>
            <!-- Nueva Contraseña -->
            <div class="field login-field">
              <div class="control has-icons-left">
                <input 
                  class="input" 
                  type="password" 
                  placeholder="Nueva contraseña" 
                  v-model="newPassword"
                  ref="newPasswordInput"
                  @input="checkPasswordStrength"
                >
                <span class="icon-login-box is-left">
                  <i>
                    <IconLock />
                  </i>
                </span>
              </div>
              <!-- Indicador de fuerza de contraseña -->
              <div class="password-strength-meter">
                <div 
                  class="password-strength-value" 
                  :style="{ width: passwordStrength.percentage + '%', backgroundColor: passwordStrength.color }"
                ></div>
              </div>
              <small class="password-strength-text" :style="{ color: passwordStrength.color }">
                {{ passwordStrength.message }}
              </small>
            </div>

            <!-- Confirmar Nueva Contraseña -->
            <div class="field login-field">
              <div class="control has-icons-left">
                <input 
                  class="input" 
                  type="password" 
                  placeholder="Confirmar nueva contraseña" 
                  v-model="confirmPassword"
                  ref="confirmPasswordInput"
                  @input="checkPasswordMatch"
                  @keyup.enter="handleLogin"
                >
                <span class="icon-login-box is-left">
                  <i>
                    <IconLock />
                  </i>
                </span>
              </div>
              <small v-if="passwordMismatch" class="help is-danger">
                Las contraseñas no coinciden
              </small>
            </div>
          </template>

          <div class="field">
            <div class="control">
              <button 
                class="button is-primary is-fullwidth" 
                type="submit" 
                :class="{ 'is-loading': isLoading }"
                :disabled="isLoading || (passwordResetMode && passwordMismatch)"
              >
                {{ passwordResetMode ? 'Establecer nueva contraseña' : 'Inicio de sesión (Login)' }}
              </button>
            </div>
          </div>
        </form>

        <!-- Enlace de solicitud de cuenta -->
        <div class="no-account-section">
          <span class="icon-login-box">
            <i>
              <IconInfo />
            </i>
          </span>
          <p>Si aún no tiene cuenta,</p>
          <a href="#" class="has-text-link" @click.prevent="openRegisterModal" style="color: #0f61e4;">Solicítela</a>
        </div>

        <!-- Enlace para recuperación de contraseña -->
        <div class="forgot-password-section">
          <a href="#" @click.prevent="openForgotPasswordModal" style="color: #0f61e4;">
            ¿Olvidó su contraseña?
          </a>
        </div>
      </div>
    </div>

    <!-- Modal de registro -->
    <div class="modal" :class="{'is-active': isModalActive}">
      <div class="modal-background" @click="closeRegisterModal"></div>
      <div class="modal-card cartoon-style">
        <header class="modal-card-head">
          <p class="modal-card-title">
            <span class="emoji">✏️</span> Solicitud de Cuenta <span class="emoji">📝</span>
          </p>
          <button class="delete" aria-label="close" @click="closeRegisterModal"></button>
        </header>
        <section class="modal-card-body">
          <div v-if="registerError" class="notification is-danger">
            {{ registerError }}
          </div>

          <!-- Selector de rol con emojis -->
          <div class="tabs is-centered cartoon-tabs">
            <ul>
              <li :class="{ 'is-active': activeRole === 'estudiante' }">
                <a @click="activeRole = 'estudiante'">
                  <span class="emoji">👨‍🎓</span> Estudiante
                </a>
              </li>
              <li :class="{ 'is-active': activeRole === 'docente' }">
                <a @click="activeRole = 'docente'">
                  <span class="emoji">👨‍🏫</span> Docente
                </a>
              </li>
            </ul>
          </div>

          <!-- Formulario de registro -->
          <div class="registration-form">
            <!-- Datos Personales -->
            <h3 class="subtitle is-5 section-title">
              <span class="emoji">👤</span> Datos Personales
            </h3>
            
            <div class="columns is-multiline">
              <div class="column is-half">
                <div class="field">
                  <label class="label">Nombres</label>
                  <div class="control has-icons-left">
                    <input class="input" type="text" v-model="formData.nombres" placeholder="Ingrese sus nombres">
                    <span class="icon is-small is-left">
                      <i class="emoji-small">📛</i>
                    </span>
                  </div>
                </div>
              </div>
              
              <div class="column is-half">
                <div class="field">
                  <label class="label">Apellidos</label>
                  <div class="control has-icons-left">
                    <input class="input" type="text" v-model="formData.apellidos" placeholder="Ingrese sus apellidos">
                    <span class="icon is-small is-left">
                      <i class="emoji-small">📛</i>
                    </span>
                  </div>
                </div>
              </div>
              
              <div class="column is-one-third">
                <div class="field">
                  <label class="label">Fecha de Nacimiento</label>
                  <div class="control has-icons-left">
                    <input class="input" type="date" v-model="formData.fechaNacimiento" @change="calculateAge">
                    <span class="icon is-small is-left">
                      <i class="emoji-small">🗓️</i>
                    </span>
                  </div>
                </div>
              </div>
              
              <div class="column is-one-third">
                <div class="field">
                  <label class="label">Edad</label>
                  <div class="control has-icons-left">
                    <input class="input" type="number" v-model="formData.edad" :readonly="!!formData.fechaNacimiento" placeholder="Calculado automáticamente">
                    <span class="icon is-small is-left">
                      <i class="emoji-small">🔢</i>
                    </span>
                  </div>
                </div>
              </div>
              
              <div class="column is-one-third">
                <div class="field">
                  <label class="label">Género</label>
                  <div class="control has-icons-left">
                    <div class="select is-fullwidth">
                      <select v-model="formData.genero">
                        <option value="" disabled selected>Seleccione género</option>
                        <option value="masculino">Masculino</option>
                        <option value="femenino">Femenino</option>
                      </select>
                    </div>
                    <span class="icon is-small is-left">
                      <i class="emoji-small">👫</i>
                    </span>
                  </div>
                </div>
              </div>
              
              <div class="column is-full">
                <div class="field">
                  <label class="label">Número de Identificación</label>
                  <div class="control has-icons-left">
                    <input class="input" type="text" v-model="formData.identificacion" placeholder="Cédula, DNI o Pasaporte">
                    <span class="icon is-small is-left">
                      <i class="emoji-small">🪪</i>
                    </span>
                  </div>
                </div>
              </div>

              <!-- Campos para crear la cuenta -->
              <div class="column is-half">
                <div class="field">
                  <label class="label">Correo Electrónico (Opcional)</label>
                  <div class="control has-icons-left">
                    <input class="input" type="email" v-model="formData.email" placeholder="Ingrese su correo electrónico">
                    <span class="icon is-small is-left">
                      <i class="emoji-small">📧</i>
                    </span>
                  </div>
                </div>
              </div>
              
              <div class="column is-half">
                <div class="field">
                  <label class="label">Contraseña</label>
                  <div class="control has-icons-left">
                    <input class="input" type="password" v-model="formData.password" placeholder="Ingrese una contraseña" @input="checkRegisterPasswordStrength">
                    <span class="icon is-small is-left">
                      <i class="emoji-small">🔒</i>
                    </span>
                  </div>
                  <!-- Indicador de fuerza de contraseña -->
                  <div class="password-strength-wrapper">
                    <div class="password-strength-meter">
                      <div 
                        class="password-strength-value" 
                        :style="{ width: registerPasswordStrength.percentage + '%', backgroundColor: registerPasswordStrength.color }"
                      ></div>
                    </div>
                    <small :style="{ color: registerPasswordStrength.color }">{{ registerPasswordStrength.message }}</small>
                  </div>
                </div>
              </div>
              
              <div class="column is-half">
                <div class="field">
                  <label class="label">Confirmar Contraseña</label>
                  <div class="control has-icons-left">
                    <input class="input" type="password" v-model="formData.confirmPassword" placeholder="Confirme su contraseña" @input="checkRegisterPasswordMatch">
                    <span class="icon is-small is-left">
                      <i class="emoji-small">🔒</i>
                    </span>
                  </div>
                  <p v-if="registerPasswordMismatch" class="help is-danger">Las contraseñas no coinciden</p>
                </div>
              </div>
            </div>

            <!-- Datos Académicos -->
            <h3 class="subtitle is-5 section-title">
              <span class="emoji">🏫</span> Datos Académicos
            </h3>
            
            <!-- Para estudiantes -->
            <div v-if="activeRole === 'estudiante'" class="columns is-multiline">
              <div class="column is-half">
                <div class="field">
                  <label class="label">Curso</label>
                  <div class="control has-icons-left">
                    <div class="select is-fullwidth">
                      <select v-model="formData.curso">
                        <option value="" disabled selected>Seleccione curso</option>
                        <option value="8">8vo de Básica</option>
                        <option value="9">9no de Básica</option>
                        <option value="10">10mo de Básica</option>
                        <option value="1">1ro de Bachillerato</option>
                        <option value="2">2do de Bachillerato</option>
                        <option value="3">3ro de Bachillerato</option>
                      </select>
                    </div>
                    <span class="icon is-small is-left">
                      <i class="emoji-small">📚</i>
                    </span>
                  </div>
                </div>
              </div>
              
              <div class="column is-half">
                <div class="field">
                  <label class="label">Paralelo</label>
                  <div class="control has-icons-left">
                    <div class="select is-fullwidth">
                      <select v-model="formData.paralelo">
                        <option value="" disabled selected>Seleccione paralelo</option>
                        <option v-for="letra in paralelos" :key="letra" :value="letra">{{ letra }}</option>
                      </select>
                    </div>
                    <span class="icon is-small is-left">
                      <i class="emoji-small">🔤</i>
                    </span>
                  </div>
                </div>
              </div>
            </div>
            
            <!-- Para docentes -->
            <div v-if="activeRole === 'docente'" class="columns is-multiline">
              <div class="column is-full">
                <div class="field">
                  <label class="label">Especialización o Áreas (Seleccione una o varias)</label>
                  <div class="materias-container">
                    <div v-for="(materia, index) in materias" :key="index" class="materia-checkbox">
                      <label class="checkbox">
                        <input type="checkbox" :value="materia.value" v-model="formData.especializaciones">
                        {{ materia.label }}
                      </label>
                    </div>
                    <div v-if="showOtroInput" class="otro-input">
                      <input 
                        class="input" 
                        type="text" 
                        v-model="formData.otroEspecializacion" 
                        placeholder="Especifique otra área"
                      >
                    </div>
                  </div>
                </div>
              </div>
            </div>
            
            <!-- Turno -->
            <div class="columns">
              <div class="column is-half">
                <div class="field">
                  <label class="label">Turno</label>
                  <div class="control has-icons-left">
                    <div class="select is-fullwidth">
                      <select v-model="formData.turno">
                        <option value="" disabled selected>Seleccione turno</option>
                        <option value="mañana">Mañana</option>
                        <option value="tarde">Tarde</option>
                      </select>
                    </div>
                    <span class="icon is-small is-left">
                      <i class="emoji-small">🕒</i>
                    </span>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </section>
        <footer class="modal-card-foot">
          <button class="button is-primary" @click="submitRegistration" :class="{ 'is-loading': isRegistering }">
            <span class="emoji">📨</span> Enviar Solicitud
          </button>
          <button class="button" @click="closeRegisterModal">
            <span class="emoji">❌</span> Cancelar
          </button>
        </footer>
      </div>
    </div>

    <!-- Modal de recuperación de contraseña -->
    <div class="modal" :class="{'is-active': showForgotPasswordModal}">
      <div class="modal-background" @click="closeForgotPasswordModal"></div>
      <div class="modal-card cartoon-style">
        <header class="modal-card-head">
          <p class="modal-card-title">
            <span class="emoji">🔑</span> Recuperación de Contraseña
          </p>
          <button class="delete" aria-label="close" @click="closeForgotPasswordModal"></button>
        </header>
        <section class="modal-card-body">
          <div class="recovery-info">
            <h3 class="subtitle mb-2"><span class="emoji">📝</span> Instrucciones</h3>
            <p>Para solicitar el restablecimiento de su contraseña, siga estos pasos:</p>
            <ol class="mt-3">
              <li>Haga clic en el botón "Ir al formulario" que aparece a continuación</li>
              <li>Complete el formulario con sus datos personales y de identificación</li>
              <li>Un administrador revisará su solicitud y procesará el cambio</li>
              <li>Recibirá una notificación cuando su contraseña sea restablecida</li>
            </ol>
          </div>
        </section>
        <footer class="modal-card-foot">
          <button class="button is-primary" @click="openPasswordResetForm">
            <span class="emoji">📝</span> Ir al formulario
          </button>
          <button class="button" @click="closeForgotPasswordModal">
            <span class="emoji">❌</span> Cancelar
          </button>
        </footer>
      </div>
    </div>

    <!-- Notificación personalizada -->
    <div class="custom-notification" :class="notificationType" v-if="showNotification">
      <div class="notification-content">
        <span class="notification-icon">{{ notificationIcon }}</span>
        <div class="notification-text">
          <div class="notification-title">{{ notificationTitle }}</div>
          <div class="notification-message">{{ notificationMessage }}</div>
        </div>
      </div>
      <button class="notification-close" @click="closeNotification">×</button>
    </div>
  </div>
</template>

<script setup>
import authService from '@/api/authService' 
import { useStore } from 'vuex'
import { ref, reactive, computed, onMounted, nextTick } from 'vue'
import { useRouter } from 'vue-router'

// Importaciones de iconos
import IconUser from './icons/forms/Icon_User.vue'
import IconLock from './icons/forms/Icon_Lock.vue'
import IconInfo from './icons/forms/Icon_Info.vue'

// Router para navegación
const router = useRouter()
const store = useStore()

// Estado de la aplicación
const userId = ref('')
const password = ref('')
const newPassword = ref('')
const confirmPassword = ref('')
const isModalActive = ref(false)
const activeRole = ref('estudiante')
const isLoading = ref(false)
const isRegistering = ref(false)
const errorMessage = ref('')
const displayError = ref(false)
const registerError = ref('')
const passwordMismatch = ref(false)
const registerPasswordMismatch = ref(false)
const passwordResetMode = ref(false)
const showForgotPasswordModal = ref(false)
const forgotPasswordId = ref('')
const forgotPasswordError = ref('')
const isRequestingReset = ref(false)

// Referencias a los inputs para focus
const userIdInput = ref(null)
const passwordInput = ref(null)
const newPasswordInput = ref(null)
const confirmPasswordInput = ref(null)

// Estado para notificaciones
const showNotification = ref(false)
const notificationTitle = ref('')
const notificationMessage = ref('')
const notificationIcon = ref('')
const notificationType = ref('info')

// Estado para medición de fuerza de contraseña (login)
const passwordStrength = reactive({
  score: 0,
  percentage: 0,
  message: '',
  color: '#cccccc'
})

// Estado para medición de fuerza de contraseña (registro)
const registerPasswordStrength = reactive({
  score: 0,
  percentage: 0,
  message: '',
  color: '#cccccc'
})

// Lista de paralelos (A-M)
const paralelos = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M']

// Lista de materias
const materias = [
  { value: 'cs_computacion', label: 'Ciencias de la Computación' },
  { value: 'matematica', label: 'Matemática' },
  { value: 'fisica', label: 'Física' },
  { value: 'informatica', label: 'Informática' },
  { value: 'estructuras_datos', label: 'Estructuras de Datos' },
  { value: 'algoritmos', label: 'Algoritmos' },
  { value: 'otros', label: 'Otro' }
]

// Datos del formulario de registro
const formData = reactive({
  nombres: '',
  apellidos: '',
  edad: '',
  genero: '',
  fechaNacimiento: '',
  identificacion: '',
  email: '',
  password: '',
  confirmPassword: '',
  curso: '',
  paralelo: '',
  especializaciones: [],
  otroEspecializacion: '',
  turno: ''
})

// Mostrar input de "otro" en especializaciones
const showOtroInput = computed(() => {
  return formData.especializaciones.includes('otros')
})

// Mostrar notificación
const showNotificationMessage = (title, message, icon, type = 'info') => {
  notificationTitle.value = title
  notificationMessage.value = message
  notificationIcon.value = icon
  notificationType.value = type
  showNotification.value = true
  
  // Auto-cerrar después de 5 segundos
  setTimeout(() => {
    closeNotification()
  }, 5000)
}

// Cerrar notificación
const closeNotification = () => {
  showNotification.value = false
}

// Mostrar error en el login
const showError = (message) => {
  errorMessage.value = message
  displayError.value = true
  
  // Auto-ocultar después de 5 segundos
  setTimeout(() => {
    displayError.value = false
  }, 5000)
}

// Cambiar foco al campo de contraseña
const focusPasswordField = () => {
  if (passwordResetMode.value) {
    newPasswordInput.value?.focus()
  } else {
    passwordInput.value?.focus()
  }
}

// Verificar coincidencia de contraseñas (login)
const checkPasswordMatch = () => {
  passwordMismatch.value = newPassword.value !== confirmPassword.value
}

// Verificar coincidencia de contraseñas (registro)
const checkRegisterPasswordMatch = () => {
  registerPasswordMismatch.value = formData.password !== formData.confirmPassword
}

// Verificar fortaleza de contraseña (login)
const checkPasswordStrength = () => {
  const password = newPassword.value
  let score = 0
  
  // Criterios de fortaleza
  if (password.length >= 8) score += 1
  if (/[A-Z]/.test(password)) score += 1
  if (/[a-z]/.test(password)) score += 1
  if (/[0-9]/.test(password)) score += 1
  if (/[^A-Za-z0-9]/.test(password)) score += 1
  
  // Actualizar estado de fortaleza
  passwordStrength.score = score
  passwordStrength.percentage = (score / 5) * 100
  
  // Definir mensaje y color
  if (password === '') {
    passwordStrength.message = ''
    passwordStrength.color = '#cccccc'
  } else if (score <= 1) {
    passwordStrength.message = 'Muy débil'
    passwordStrength.color = '#ff4d4f'
  } else if (score <= 2) {
    passwordStrength.message = 'Débil'
    passwordStrength.color = '#ff7a45'
  } else if (score <= 3) {
    passwordStrength.message = 'Regular'
    passwordStrength.color = '#ffc53d'
  } else if (score <= 4) {
    passwordStrength.message = 'Buena'
    passwordStrength.color = '#73d13d'
  } else {
    passwordStrength.message = 'Excelente'
    passwordStrength.color = '#389e0d'
  }
  
  // Verificar coincidencia si ya hay contraseña de confirmación
  if (confirmPassword.value) {
    checkPasswordMatch()
  }
}

// Verificar fortaleza de contraseña (registro)
const checkRegisterPasswordStrength = () => {
  const password = formData.password
  let score = 0
  
  // Criterios de fortaleza
  if (password.length >= 8) score += 1
  if (/[A-Z]/.test(password)) score += 1
  if (/[a-z]/.test(password)) score += 1
  if (/[0-9]/.test(password)) score += 1
  if (/[^A-Za-z0-9]/.test(password)) score += 1
  
  // Actualizar estado de fortaleza
  registerPasswordStrength.score = score
  registerPasswordStrength.percentage = (score / 5) * 100
  
  // Definir mensaje y color
  if (password === '') {
    registerPasswordStrength.message = ''
    registerPasswordStrength.color = '#cccccc'
  } else if (score <= 1) {
    registerPasswordStrength.message = 'Muy débil'
    registerPasswordStrength.color = '#ff4d4f'
  } else if (score <= 2) {
    registerPasswordStrength.message = 'Débil'
    registerPasswordStrength.color = '#ff7a45'
  } else if (score <= 3) {
    registerPasswordStrength.message = 'Regular'
    registerPasswordStrength.color = '#ffc53d'
  } else if (score <= 4) {
    registerPasswordStrength.message = 'Buena'
    registerPasswordStrength.color = '#73d13d'
  } else {
    registerPasswordStrength.message = 'Excelente'
    registerPasswordStrength.color = '#389e0d'
  }
  
  // Verificar coincidencia si ya hay contraseña de confirmación
  if (formData.confirmPassword) {
    checkRegisterPasswordMatch()
  }
}

// Calcular edad desde fecha de nacimiento
const calculateAge = () => {
  if (formData.fechaNacimiento) {
    const birthDate = new Date(formData.fechaNacimiento)
    const today = new Date()
    let age = today.getFullYear() - birthDate.getFullYear()
    const monthDiff = today.getMonth() - birthDate.getMonth()
    
    if (monthDiff < 0 || (monthDiff === 0 && today.getDate() < birthDate.getDate())) {
      age--
    }
    
    formData.edad = age
  }
}

// Método de inicio de sesión
const handleLogin = async () => {
  try {
    if (passwordResetMode.value) {
      if (!userId.value || !newPassword.value || !confirmPassword.value) {
        showError('Por favor, complete todos los campos')
        return
      }
      
      if (passwordMismatch.value) {
        showError('Las contraseñas no coinciden')
        return
      }
      
      if (passwordStrength.score < 3) {
        showError('La contraseña es demasiado débil')
        return
      }
      
      await resetPassword()
      return
    }
    
    if (!userId.value || !password.value) {
      showError('Por favor, ingrese su número de identidad y contraseña')
      return
    }

    isLoading.value = true
    displayError.value = false

    console.log('Intentando iniciar sesión con:', { userId: userId.value })
    
    try {
      const response = await authService.login({
        userId: userId.value,
        password: password.value
      })

      console.log('Respuesta del servidor:', response.data)

      // Verificar si la contraseña debe ser cambiada
      if (response.data.requiere_cambio_clave) {
        passwordResetMode.value = true
        isLoading.value = false
        showNotificationMessage(
          'Cambio de contraseña requerido', 
          'Por favor, establezca una nueva contraseña para continuar.',
          '🔑',
          'warning'
        )
        
        // Focus en el campo de nueva contraseña
        nextTick(() => {
          newPasswordInput.value?.focus()
        })
        
        return
      }
      
      // Verificar estado de la cuenta
      if (response.data.estado === 'pendiente') {
        showError('Su solicitud de registro está pendiente de aprobación por un administrador.')
        isLoading.value = false
        return
      }
      
      if (response.data.estado === 'rechazado') {
        showError('Su solicitud de registro ha sido rechazada. Contacte al administrador para más información.')
        isLoading.value = false
        return
      }
      
      // Limpiar cualquier dato antiguo
      localStorage.removeItem('token')
      localStorage.removeItem('user_id')
      localStorage.removeItem('user_role')
      localStorage.removeItem('user_name')
      
      // Almacenar datos en localStorage
      localStorage.setItem('token', response.data.token)
      localStorage.setItem('user_id', response.data.user_id)
      localStorage.setItem('user_role', response.data.rol)
      localStorage.setItem('user_name', response.data.nombres)
      
      // También almacenar en Vuex
      store.dispatch('auth/login', response.data)
      
      console.log('Rol del usuario:', response.data.rol)
      
      // Mostrar notificación de éxito
      showNotificationMessage(
        '¡Bienvenido!', 
        `Inicio de sesión exitoso como ${response.data.nombres}`,
        '✅',
        'success'
      )
      
      // Redireccionar según el rol
      if (response.data.rol === 'estudiante') {
        console.log('Redirigiendo a estudiante')
        router.push('/estudiante/dashboard')
      } else if (response.data.rol === 'docente') {
        console.log('Redirigiendo a docente')
        router.push('/docente/dashboard')
      } else if (response.data.rol === 'admin') {
        console.log('Redirigiendo a admin')
        router.push('/admin/dashboard')
      } else {
        console.error('Rol no reconocido:', response.data.rol)
        showError('Error: Rol de usuario no válido.')

        // Limpiar localStorage
        localStorage.removeItem('token')
        localStorage.removeItem('user_id')
        localStorage.removeItem('user_role')
        localStorage.removeItem('user_name')
      }
    } catch (error) {
      console.error('Error detallado de inicio de sesión:', error)
      
      if (error.response) {
        if (error.response.status === 403 && error.response.data && error.response.data.estado) {
          if (error.response.data.estado === 'pendiente') {
            showError('Su solicitud de registro está pendiente de aprobación por un administrador.')
          } else if (error.response.data.estado === 'rechazado') {
            showError('Su solicitud de registro ha sido rechazada. Contacte al administrador para más información.')
          } else {
            showError(error.response.data.error || 'No tiene permisos para acceder.')
          }
        } else if (error.response.data && error.response.data.error) {
          showError(error.response.data.error)
        } else {
          showError('Credenciales inválidas o problema de conexión. Por favor, intente nuevamente.')
        }
      } else {
        showError('Error de conexión. Por favor, verifique su conexión a internet e intente nuevamente.')
      }
    } finally {
      isLoading.value = false
    }
  } catch (error) {
    console.error('Error general:', error)
    showError('Ha ocurrido un error inesperado. Por favor, intente nuevamente.')
    isLoading.value = false
  }
}

// Resetear contraseña (después de login con contraseña temporal)
const resetPassword = async () => {
  try {
    isLoading.value = true;

    const resetData = {
      userId: userId.value,
      tempPassword: password.value,
      newPassword: newPassword.value
    };

    console.log("Datos para resetear contraseña:", resetData);
    
    //const response = await authService.resetPassword(resetData);

    // Implementar llamada a API para cambiar contraseña
    const response = await authService.resetPassword({
      userId: userId.value,
      tempPassword: password.value,  // La contraseña temporal usada para iniciar sesión
      newPassword: newPassword.value
    });

    console.log("Respuesta de reseteo de contraseña:", response.data);

    // Almacenar nuevos datos de sesión en localStorage
    localStorage.setItem('token', response.data.token);
    localStorage.setItem('user_id', response.data.user_id);
    localStorage.setItem('user_role', response.data.rol);
    localStorage.setItem('user_name', response.data.nombres);

    // También almacenar en Vuex
    store.dispatch('auth/login', response.data);

    // Mostrar notificación de éxito
    showNotificationMessage(
      'Contraseña actualizada',
      'Su contraseña ha sido actualizada exitosamente.',
      '✅',
      'success'
    );

    // Volver al modo normal de login y redireccionar
    passwordResetMode.value = false;
    newPassword.value = '';
    confirmPassword.value = '';

    // Redireccionar según el rol
    const rol = response.data.rol;
    if (rol === 'estudiante') {
      router.push('/estudiante/dashboard');
    } else if (rol === 'docente') {
      router.push('/docente/dashboard');
    } else if (rol === 'admin') {
      router.push('/admin/dashboard');
    }

  } catch (error) {
    console.error('Error al resetear contraseña:', error);
    showError('No se pudo cambiar la contraseña. Por favor, intente nuevamente.');
  } finally {
    isLoading.value = false;
  }
}

// Abrir modal de recuperación de contraseña
const openForgotPasswordModal = () => {
  showForgotPasswordModal.value = true;
}

// Abrir formulario de recuperación de contraseña en nueva pestaña
const openPasswordResetForm = () => {
  // Obtener URL del formulario desde variables de entorno
  const formUrl = import.meta.env.VITE_PASSWORD_RESET_FORM_URL || '#';
  window.open(formUrl, '_blank');
  closeForgotPasswordModal();
}

// Cerrar modal de recuperación de contraseña
const closeForgotPasswordModal = () => {
  showForgotPasswordModal.value = false;
}

// Abrir modal de registro
const openRegisterModal = () => {
  isModalActive.value = true
  registerError.value = ''
}

// Cerrar modal de registro
const closeRegisterModal = () => {
  isModalActive.value = false
  resetForm()
}

// Método para enviar el formulario de registro
const submitRegistration = async () => {
  // Validaciones
  registerError.value = ''
  
  // Verificar campos obligatorios
  if (!formData.identificacion || !formData.password || !formData.nombres || !formData.apellidos) {
    registerError.value = 'Por favor, complete los campos obligatorios (nombres, apellidos, identificación y contraseña)'
    return
  }
  
  // Verificar coincidencia de contraseñas
  if (formData.password !== formData.confirmPassword) {
    registerError.value = 'Las contraseñas no coinciden'
    return
  }
  
  // Verificar fuerza de contraseña
  if (registerPasswordStrength.score < 3) {
    registerError.value = 'La contraseña es demasiado débil. Debe incluir mayúsculas, minúsculas, números y caracteres especiales'
    return
  }
  
  // Verificaciones específicas por rol
  if (activeRole.value === 'estudiante') {
    if (!formData.curso || !formData.paralelo) {
      registerError.value = 'Por favor, seleccione su curso y paralelo'
      return
    }
  } else if (activeRole.value === 'docente') {
    if (formData.especializaciones.length === 0) {
      registerError.value = 'Por favor, seleccione al menos una especialización'
      return
    }
  }

  try {
    isRegistering.value = true

    // Preparar datos según el rol seleccionado
    const registrationData = {
      username: formData.identificacion,
      email: formData.email || `${formData.identificacion}@example.com`, // Email por defecto si no se proporciona
      password: formData.password,
      profile: {
        rol: activeRole.value,
        nombres: formData.nombres,
        apellidos: formData.apellidos,
        edad: formData.edad ? parseInt(formData.edad) : null, 
        genero: formData.genero,
        fecha_nacimiento: formData.fechaNacimiento,
        identificacion: formData.identificacion,
        turno: formData.turno
      }
    }

    // Añadir datos específicos según el rol
    if (activeRole.value === 'estudiante') {
      registrationData.profile.curso = formData.curso;
      registrationData.profile.paralelo = formData.paralelo;
    } else if (activeRole.value === 'docente') {
      // Manejar campo "Otro" en especializaciones
      let especializaciones = [...formData.especializaciones];
      if (especializaciones.includes('otros') && formData.otroEspecializacion) {
        // Quitar "otros" y agregar el valor personalizado
        especializaciones = especializaciones.filter(e => e !== 'otros');
        especializaciones.push(formData.otroEspecializacion);
      }
      // Convertir array de especializaciones a string separado por comas
      registrationData.profile.especializacion = especializaciones.join(',');
    }
    
    // Asegurar que el estado es pendiente
    registrationData.profile.estado = 'pendiente';

    console.log('Datos de registro a enviar:', registrationData);

    // Usar el servicio apropiado según el rol
    let response;
    try {
      if (activeRole.value === 'docente') {
        response = await authService.registerDocente(registrationData);
      } else {
        response = await authService.registerUser(registrationData);
      }
      
      console.log('Respuesta de registro:', response.data);
      
      // Mostrar mensaje de éxito y cerrar el modal
      closeRegisterModal();
      showNotificationMessage(
        '¡Solicitud enviada!', 
        'Su solicitud ha sido enviada exitosamente. Un administrador revisará y aprobará su cuenta pronto.',
        '✅',
        'success'
      );
    } catch (error) {
      console.error('Error específico en la petición:', error);
      throw error; // Re-lanzar el error para el manejo en el catch exterior
    }
  } catch (error) {
    console.error('Error detallado:', error);
    if (error.response) {
      // El servidor respondió con un código de estado fuera del rango 2xx
      console.error('Respuesta del servidor:', error.response.data);
      console.error('Código de estado:', error.response.status);
      
      // Mostrar mensaje de error más específico
      if (error.response.data) {
        let errorMessage = 'Error en el registro: ';
        if (typeof error.response.data === 'object') {
          // Si es un objeto, formatea los errores
          for (const [key, value] of Object.entries(error.response.data)) {
            errorMessage += `${key}: ${Array.isArray(value) ? value.join(', ') : value} `;
          }
          registerError.value = errorMessage;
        } else {
          registerError.value = `Error: ${error.response.data}`;
        }
      } else {
        registerError.value = `Error ${error.response.status}: ${error.response.statusText}`;
      }
    } else {
      // Error de conexión o de otro tipo
      registerError.value = 'Error al procesar su solicitud. Por favor, intente más tarde.';
    }
  } finally {
    isRegistering.value = false;
  }
}

// Método para resetear el formulario
const resetForm = () => {
  Object.keys(formData).forEach(key => {
    if (key === 'especializaciones') {
      formData[key] = []
    } else {
      formData[key] = ''
    }
  })
  activeRole.value = 'estudiante'
  registerPasswordStrength.score = 0
  registerPasswordStrength.percentage = 0
  registerPasswordStrength.message = ''
  registerPasswordStrength.color = '#cccccc'
  registerPasswordMismatch.value = false
}

// Al montar el componente, enfocar el campo de usuario
onMounted(() => {
  nextTick(() => {
    userIdInput.value?.focus()
  })
})
</script>

<style scoped>
html,
body {
  height: 100%;
  background-color: #f4f4f4;
  font-family: 'Roboto', sans-serif, Arial;
}

.login-wrapper {
  display: flex;
  align-items: center;
  justify-content: center;
}

.login-container {
  display: flex;
  width: 900px;
  height: 460px; /* Altura reducida para un aspecto más compacto */
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
  border-radius: 8px;
  overflow: hidden;
}

.left-section {
  width: 55%;
  flex: 0 0 55%; /* Para mantener el ancho fijo */
  background-image: url('../../public/login/fondo_left.png');
  background-size: cover;
  background-position: center;
  position: relative;
}

.right-section {
  width: 45%;
  flex: 0 0 45%; /* Para mantener el ancho fijo */
  background-color: white;
  padding: 2rem;
  display: flex;
  flex-direction: column;
  justify-content: space-between;
  position: relative;
}

.logos-container {
  display: flex;
  justify-content: space-between;
  align-items: center;
  width: 100%;
  margin-bottom: 1rem;
}

.logo-wrap {
  width: 170px;
  height: 50px;
  background: url('../../public/logo/Logo-CuriosMaze-170x45.png') center no-repeat;
}

.logo-institucion {
  width: 50px;
  height: 50px;
  background-image: url('../../public/Institucion_img/fe_y_alegria_logo.png');
  background-size: contain;
  background-repeat: no-repeat; 
  background-position: center;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  font-weight: bold;
  border-radius: 5px;
  font-size: 0.8rem;
  margin-right: 4px;
}

.login-note {
  text-align: left;
  color: #888888;
  margin-bottom: 0.4rem;
  font-size: 12px;
  font-weight: 400;
  font-style: italic;
}

.password-reset-note {
  color: #E25E5E;
  font-weight: 600;
}

/* Contenedor para mensajes de error con altura fija */
.message-container {
  height: 40px;
  margin-bottom: 0.5rem;
}

.notification.is-danger.fixed-height {
  height: 100%;
  overflow: hidden;
  padding: 0.5rem 0.75rem;
  border-radius: 4px;
  font-size: 0.85rem;
  background-color: #feecf0;
  color: #cc0f35;
  display: flex;
  align-items: center;
}

/* Contenedor de los campos de login */
.login-field {
  margin-bottom: 0.6rem;
}

/* Posicionar el ícono dentro del input */
.control.has-icons-left {
  position: relative;
}

.input {
  background-color: #ffffff !important;
  color: #000000 !important;
  padding-left: 2.5rem;
  border: 1px solid #dbdbdb;
  border-radius: 4px;
  height: 2.5rem;
}

/* Placeholder en color #DBDBDB */
.input::placeholder {
  color: #75746eb7;
  text-align: left;
}

/* Forzar color de los íconos */
.icon-login-box svg {
  margin-top: 5px;
  color: #DBDBDB;
  font-size: 1rem;
}

.icon-login-box.is-left {
  position: absolute;
  left: 0.75rem;
  top: 50%;
  transform: translateY(-50%);
  pointer-events: none;
}

.no-account-section {
  display: flex;
  align-items: center;
  justify-content: center;
  background-color: #f0f0f0;
  padding: 0.75rem;
  border-radius: 4px;
  margin-top: 0.5rem;
}

.no-account-section .icon-login-box {
  margin-right: 0.5rem;
}

.no-account-section p {
  margin-right: 0.5rem;
  color: #4a4a4a;
}

/* Nueva sección para olvidé mi contraseña */
.forgot-password-section {
  text-align: center;
  margin-top: 0.5rem;
  font-size: 0.9rem;
}

.forgot-password-section a {
  color: #0f61e4;
  text-decoration: none;
}

.forgot-password-section a:hover {
  text-decoration: underline;
}

.button.is-primary {
  background-color: #d39402;
  border-color: transparent;
  color: #fff;
}

.button.is-primary:hover {
  background-color: #c58c08;
}

/* Indicador de fuerza de contraseña */
.password-strength-meter {
  height: 4px;
  background-color: #eee;
  border-radius: 2px;
  margin-top: 0.3rem;
  overflow: hidden;
}

.password-strength-value {
  height: 100%;
  transition: width 0.3s, background-color 0.3s;
}

.password-strength-text {
  font-size: 0.75rem;
  margin-top: 0.2rem;
  display: block;
}

/* Estilos mejorados para el modal cartoon */
.modal-card.cartoon-style {
  width: 90%;
  max-width: 700px;
  border-radius: 20px;
  overflow: hidden;
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.2);
}

.modal-card-head {
  background-color: #f7e4a5;
  border-bottom: 3px solid #e6c653;
  padding: 1.5rem;
}

.modal-card-title {
  color: #805b08;
  font-size: 1.5rem;
  font-weight: bold;
  display: flex;
  align-items: center;
  justify-content: center;
}

.modal-card-body {
  max-height: 70vh;
  overflow-y: auto;
  background-color: #fffdf5;
  padding: 1.5rem;
}

.section-title {
  border-bottom: 2px dashed #dbdbdb;
  padding-bottom: 0.5rem;
  margin-top: 1.5rem;
  margin-bottom: 1rem;
  color: #BC870B;
  display: flex;
  align-items: center;
}

.section-title:first-child {
  margin-top: 0;
}

/* Estilos para tabs cartoon */
.cartoon-tabs {
  margin-bottom: 1.5rem;
}

.cartoon-tabs ul {
  border-bottom: 2px solid #e6c653;
}

.cartoon-tabs li a {
  padding: 0.7em 1.2em;
  border-bottom-width: 3px;
  border-radius: 8px 8px 0 0;
  font-weight: bold;
  transition: all 0.2s;
}

.cartoon-tabs li.is-active a {
  color: #d39402;
  border-bottom-color: #d39402;
  background-color: #fff9e0;
}

.cartoon-tabs li a:hover {
  background-color: #fff9e0;
}

/* Estilos para emojis */
.emoji {
  font-size: 1.2rem;
  margin-right: 0.5rem;
  display: inline-block;
}

.emoji-small {
  font-size: 1rem;
}

/* Estilos para campos del formulario */
.label {
  color: #4a4a4a;
  font-size: 0.9rem;
  font-weight: 600;
}

.select, .select select {
  width: 100%;
}

.field {
  margin-bottom: 1.2rem;
}

/* Estilos para el pie del modal */
.modal-card-foot {
  justify-content: space-between; /* Espacio entre botones */
  background-color: #f7e4a5;
  border-top: 3px solid #e6c653;
  padding: 1.5rem;
}

.modal-card-foot .button {
  padding: 0.5em 1.5em;
  border-radius: 8px;
  font-weight: bold;
  margin: 0 0.5rem;
}

/* Estilos para el indicador de fuerza de contraseña */
.password-strength-wrapper {
  margin-top: 0.5rem;
}

.password-strength-meter {
  height: 6px;
  background-color: #eee;
  border-radius: 3px;
  margin-bottom: 0.3rem;
}

.password-strength-value {
  height: 100%;
  border-radius: 3px;
  transition: width 0.3s, background-color 0.3s;
}

/* Estilos para selección múltiple de materias */
.materias-container {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
  gap: 0.8rem;
  background-color: #fff;
  padding: 1rem;
  border-radius: 8px;
  border: 1px solid #eee;
  margin-top: 0.5rem;
}

.materia-checkbox {
  padding: 0.5rem;
  border-radius: 6px;
  transition: background-color 0.2s;
}

.materia-checkbox:hover {
  background-color: #f9f3e0;
}

.checkbox {
  display: flex;
  align-items: center;
  cursor: pointer;
}

.checkbox input {
  margin-right: 0.5rem;
}

/* Estilos para notificaciones personalizadas */
.custom-notification {
  position: fixed;
  bottom: 30px;
  right: 30px;
  background-color: #1C1C21;
  color: white;
  padding: 1rem;
  border-radius: 8px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.2);
  z-index: 1000;
  min-width: 300px;
  max-width: 400px;
  animation: slide-in 0.3s ease-out forwards;
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  border-left: 4px solid #6B7280;
}

.custom-notification.info {
  border-left-color: #65B1C1;
}

.custom-notification.success {
  border-left-color: #9DBEB6;
}

.custom-notification.warning {
  border-left-color: #FFBD2E;
}

.custom-notification.danger {
  border-left-color: #FF6B6B;
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
  color: #e0e0e0;
}

.notification-close {
  background: transparent;
  border: none;
  color: #9090A0;
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
  color: white;
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

/* Estilos para modal de recuperación de contraseña */
.recovery-info {
  background-color: #f7e4a5;
  padding: 1rem;
  border-radius: 8px;
  margin-bottom: 1.5rem;
  border-left: 4px solid #e6c653;
}

.recovery-info ol {
  margin-left: 1rem;
}

.recovery-info li {
  margin-bottom: 0.5rem;
}

/* Responsivo */
@media (max-width: 768px) {
  .login-container {
    flex-direction: column;
    width: 95%;
    height: auto;
  }
  
  .left-section {
    width: 100%;
    height: 150px;
  }
  
  .right-section {
    width: 100%;
    padding: 1.5rem;
  }
}

/* Estilos para tema oscuro */
@media (prefers-color-scheme: dark) {
  .recovery-info {
    background-color: #2a2a2a;
    color: #e0e0e0;
    border-left-color: #ffd700;
  }
  
  .recovery-info h3.subtitle {
    color: #f0f0f0;
  }
  
  .recovery-info p {
    color: #d0d0d0;
  }
  
  .recovery-info li {
    color: #d0d0d0;
  }
}
</style>