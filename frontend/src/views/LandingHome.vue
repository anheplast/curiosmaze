<template>
  <div class="landing-page">
    <!-- Google Fonts -->
    <link href="https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;500;600;700;800&display=swap"
      rel="stylesheet">

    <!-- Encabezado -->
    <header class="header">
      <div class="container-limited header-container">
        <div class="nav">
          <div class="logo">
            <img src="../../public/logo/Logo-CuriosMaze-170x45.png" alt="CURIOSMAZE" class="logo-img">
          </div>
          <div class="nav-right">
            <button @click="goToLogin" class="btn-login">
              <span class="btn-text">Ingresar</span>
            </button>
          </div>
        </div>
      </div>
    </header>

    <!-- Sección Principal -->
    <section class="hero">
      <div class="hero-background">
        <!-- Background limpio sin estrellas -->
      </div>

      <div class="container hero-container">
        <div class="hero-content">
          <h1 class="hero-title">
            <span class="title-line title-primary">Refuerza tu aprendizaje de forma divertida</span>
          </h1>

          <p class="hero-subtitle">
            Crea evaluaciones, ejercicios prácticos de programación y haz un seguimiento del rendimiento académico de
            tus estudiantes.
          </p>

          <div class="hero-quote">
            <p class="quote-text">"Ten menos curiosidad por las personas y más curiosidad por las ideas."</p>
            <span class="quote-author">- Marie Curie</span>
          </div>
        </div>

        <div class="hero-visual">
          <div class="hero-image-container">
            <img src="../../public/undraw_adventure-map_3e4p.svg" alt="Adventure Map" class="hero-image">
          </div>
        </div>
      </div>
    </section>

    <!-- Barra de iconos y palabras clave -->
    <div class="keywords-bar">
      <div class="keywords-track">
        <div class="keyword-item">
          <i class="fas fa-brain"></i>
          <span>Pensamiento Lógico</span>
        </div>
        <div class="keyword-item">
          <i class="fas fa-code"></i>
          <span>Programación</span>
        </div>
        <div class="keyword-item">
          <i class="fas fa-calculator"></i>
          <span>Matemáticas</span>
        </div>
        <div class="keyword-item">
          <i class="fas fa-user-graduate"></i>
          <span>Aprendizaje</span>
        </div>
        <div class="keyword-item">
          <i class="fas fa-chalkboard-teacher"></i>
          <span>Educación</span>
        </div>
        <div class="keyword-item">
          <i class="fas fa-university"></i>
          <span>Academia</span>
        </div>
        <div class="keyword-item">
          <i class="fas fa-laptop-code"></i>
          <span>Desarrollo</span>
        </div>
        <div class="keyword-item">
          <i class="fas fa-puzzle-piece"></i>
          <span>Resolución de Problemas</span>
        </div>
        <!-- Duplicamos para el efecto infinito -->
        <div class="keyword-item">
          <i class="fas fa-brain"></i>
          <span>Pensamiento Lógico</span>
        </div>
        <div class="keyword-item">
          <i class="fas fa-code"></i>
          <span>Programación</span>
        </div>
        <div class="keyword-item">
          <i class="fas fa-calculator"></i>
          <span>Matemáticas</span>
        </div>
        <div class="keyword-item">
          <i class="fas fa-user-graduate"></i>
          <span>Aprendizaje</span>
        </div>
        <div class="keyword-item">
          <i class="fas fa-chalkboard-teacher"></i>
          <span>Educación</span>
        </div>
        <div class="keyword-item">
          <i class="fas fa-university"></i>
          <span>Academia</span>
        </div>
        <div class="keyword-item">
          <i class="fas fa-laptop-code"></i>
          <span>Desarrollo</span>
        </div>
        <div class="keyword-item">
          <i class="fas fa-puzzle-piece"></i>
          <span>Resolución de Problemas</span>
        </div>
      </div>
    </div>

    <!-- Sección de Características -->
    <section class="features">
      <div class="container features-container">
        <div class="features-header">
          <h2 class="section-title">¿Qué puedes hacer?</h2>
        </div>

        <div class="features-grid">
          <div class="feature-card">
            <div class="feature-icon-circle feature-icon-purple">
              <i class="fas fa-clipboard-check"></i>
            </div>
            <div class="feature-text">
              <h3>Evaluaciones programadas</h3>
              <p>Crea exámenes con límite de tiempo y calificación automática</p>
            </div>
          </div>

          <div class="feature-card">
            <div class="feature-icon-circle feature-icon-blue">
              <i class="fas fa-code"></i>
            </div>
            <div class="feature-text">
              <h3>Editor CodeMirror</h3>
              <p>Editor integrado con ejecución automática usando Judge0</p>
            </div>
          </div>

          <div class="feature-card">
            <div class="feature-icon-circle feature-icon-green">
              <i class="fas fa-chart-line"></i>
            </div>
            <div class="feature-text">
              <h3>Análisis de rendimiento</h3>
              <p>Historial completo y estadísticas de cada estudiante</p>
            </div>
          </div>

          <div class="feature-card">
            <div class="feature-icon-circle feature-icon-orange">
              <i class="fas fa-bolt"></i>
            </div>
            <div class="feature-text">
              <h3>Solo ejercicios prácticos</h3>
              <p>Enfoque 100% en programación práctica, sin teoría</p>
            </div>
          </div>
        </div>
      </div>
    </section>

    <!-- Barra de iconos y palabras clave -->

    <!-- Sección de Institución -->
    <section class="institution" id="institution">
      <div class="institution-wrapper">
        <div class="container-limited">
          <div class="institution-content">
            <div class="institution-info">
              <h2>Confianza institucional</h2>
              <p>Implementado en la <strong>Unidad Educativa Juan Pablo II</strong> para reforzar el aprendizaje y el
                pensamiento lógico</p>
              <div class="institution-logo-small">
                <img src="../../public/Institucion_img/fe_y_alegria_logo.png" alt="Unidad Educativa Juan Pablo II"
                  class="inst-logo-small">
              </div>
            </div>
          </div>
        </div>
      </div>
    </section>

    <!-- Pie de página -->
    <footer class="footer">
      <div class="container-limited footer-container">
        <div class="footer-top">
          <div class="footer-brand">
            <img src="../../public/logo/Logo-CuriosMaze-40x40.png" alt="CURIOSMAZE" class="footer-logo">
            <span class="footer-text">CURIOSMAZE</span>
          </div>
        </div>

        <div class="footer-credits">
          <h4>Créditos:</h4>
          <div class="credits-list">
            <a href="https://codepen.io/Hyperplexed/pen/RwzGKwy" target="_blank" class="credit-item">
              <strong>CodePen - Hyperplexed</strong>
            </a>
            <a href="https://judge0.com/" target="_blank" class="credit-item">
              <strong>Judge0.com</strong>
            </a>
          </div>
        </div>

        <div class="footer-bottom">
          <p>© CURIOSMAZE - 2025</p>
        </div>
      </div>
    </footer>
  </div>
</template>

<script>
import { useRouter } from 'vue-router'

export default {
  name: 'LandingHome',
  setup() {
    const router = useRouter()

    // Función para navegar al login
    const goToLogin = () => {
      console.log('Navegando al login...')
      router.push('/login')
    }

    return {
      goToLogin
    }
  }
}
</script>

<style scoped>
/* ===================== */
/*  Reset y Base         */
/* ===================== */
* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

.landing-page {
  background: #F8FAFC;
  color: #111827;
  font-family: 'Poppins', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
  line-height: 1.6;
  overflow-x: hidden;
}

/* ===================== */
/*  Contenedores         */
/* ===================== */
.container,
.container-limited {
  width: 100%;
  margin: 0 auto;
  padding: 0 40px;
}

.container-limited {
  max-width: 100%;
}

@media (max-width: 768px) {

  .container,
  .container-limited {
    padding: 0 20px;
  }
}

@media (max-width: 480px) {

  .container,
  .container-limited {
    padding: 0 16px;
  }
}

/* ===================== */
/*  Header               */
/* ===================== */
.header {
  background: #FFFFFF;
  box-shadow: 0 2px 10px rgba(108, 99, 255, 0.1);
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  z-index: 1000;
  width: 100%;
}

.header-container {
  display: flex;
  justify-content: space-between;
  align-items: center;
  height: 80px;
}

.nav {
  display: flex;
  align-items: center;
  width: 100%;
  justify-content: space-between;
}

.logo-img {
  height: 40px;
  width: auto;
}

.nav-right {
  display: flex;
  align-items: center;
  gap: 12px;
}

.btn-login {
  background: #ffffff;
  color: #111827;
  border: 2px solid rgb(49 48 53 / 30%);
  padding: 12px 24px;
  border-radius: 8px;
  font-weight: 600;
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: 8px;
  transition: all 0.3s ease;
}

.btn-login:hover {
  border-color: rgba(0, 0, 0, 0.8);
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
}

/* ===================== */
/*  Sección Principal    */
/* ===================== */
.hero {
  color: #111827;
  padding: 140px 0 80px;
  position: relative;
  overflow: hidden;
}

.hero-background {
  position: absolute;
  inset: 0;
  overflow: hidden;
}

.hero-container {
  display: grid;
  grid-template-columns: 1.2fr 0.8fr;
  gap: 60px;
  align-items: center;
  position: relative;
  z-index: 1;
}

@media (max-width: 768px) {
  .hero-container {
    grid-template-columns: 1fr;
    gap: 40px;
  }
}

.hero-title {
  font-size: clamp(2.5rem, 5vw, 3.8rem);
  font-weight: 700;
  margin-bottom: 24px;
  line-height: 1.2;
  text-align: left;
}

.title-primary {
  color: #111827;
  font-weight: 900;
  position: relative;
}

.title-highlight {
  color: #111827;
  font-weight: 600;
  margin-top: 8px;
}

.hero-subtitle {
  font-size: 1.2rem;
  margin-bottom: 40px;
  font-weight: 400;
  line-height: 1.6;
  color: #6B7280;
  text-align: left;
}

.hero-quote {
  margin-top: 30px;
  text-align: left;
}

.quote-text {
  font-size: 1.1rem;
  font-style: italic;
  font-weight: 600;
  line-height: 1.6;
  margin-bottom: 12px;
  color: #047857;
  opacity: 0.9;
}

.quote-author {
  font-size: 0.9rem;
  font-weight: 700;
  color: #059669;
}

.hero-visual {
  display: flex;
  justify-content: center;
  align-items: center;
}

.hero-image-container {
  position: relative;
}

.hero-image {
  max-width: 100%;
  height: auto;
  max-height: 350px;
  filter: drop-shadow(0 15px 30px rgba(0, 0, 0, 0.2));
  position: relative;
  z-index: 1;
}

/* ===================== */
/*  Barra de Keywords    */
/* ===================== */
.keywords-bar {
  background: #f1f5f9;
  height: 80px;
  overflow: hidden;
  border-top: 1px solid #E5E7EB;
  border-bottom: 1px solid #E5E7EB;
  position: relative;
}

.keywords-track {
  display: flex;
  align-items: center;
  height: 100%;
  animation: moveLeft 30s linear infinite;
  white-space: nowrap;
}

.keyword-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 0 40px;
  color: #6B7280;
  font-size: 18px;
  font-weight: 600;
  flex-shrink: 0;
}

.keyword-item i {
  color: #000000;
  font-size: 22px;
}

@keyframes moveLeft {
  0% {
    transform: translateX(0);
  }

  100% {
    transform: translateX(-50%);
  }
}

/* ===================== */
/*  Sección de           */
/*  Características      */
/* ===================== */
.features {
  padding: 80px 0;
  background: #F8FAFC;
  position: relative;
}

.features-header {
  text-align: center;
  margin-bottom: 60px;
}

.section-title {
  font-size: clamp(2rem, 4vw, 3rem);
  font-weight: 700;
  margin-bottom: 16px;
  color: #111827;
}

.features-container {
  max-width: 1200px;
}

.features-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
  gap: 40px;
  max-width: 1000px;
  margin: 0 auto;
}

@media (min-width: 769px) and (max-width: 1024px) {
  .features-grid {
    grid-template-columns: repeat(2, 1fr);
    gap: 35px;
  }
}

@media (min-width: 1025px) {
  .features-grid {
    grid-template-columns: repeat(4, 1fr);
    gap: 30px;
  }
}

.feature-card {
  display: flex;
  flex-direction: column;
  align-items: center;
  text-align: center;
  padding: 30px 20px;
  background: #FFFFFF;
  border-radius: 16px;
  box-shadow: 0 8px 25px rgba(0, 0, 0, 0.08);
  border: 2px solid #f1f5f9;
  transition: transform 0.3s ease, box-shadow 0.3s ease;
}

.feature-card:hover {
  transform: translateY(-5px);
  box-shadow: 0 12px 35px rgba(0, 0, 0, 0.15);
}

.feature-icon-circle {
  width: 80px;
  height: 80px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-bottom: 20px;
  font-size: 2rem;
  color: #FFFFFF;
}

.feature-icon-purple {
  background: linear-gradient(135deg, #8B5CF6, #7C3AED);
}

.feature-icon-blue {
  background: linear-gradient(135deg, #3B82F6, #2563EB);
}

.feature-icon-green {
  background: linear-gradient(135deg, #10B981, #059669);
}

.feature-icon-orange {
  background: linear-gradient(135deg, #F59E0B, #D97706);
}

.feature-text h3 {
  font-size: 1.4rem;
  font-weight: 700;
  margin-bottom: 8px;
  color: #111827;
}

.feature-text p {
  color: #6B7280;
  line-height: 1.6;
  font-size: 1rem;
}

/* ===================== */
/*  Sección de           */
/*  Institución          */
/* ===================== */
.institution {
  padding: 0;
  background: #F8FAFC;
}

.institution-wrapper {
  background-image: linear-gradient(rgba(0, 0, 0, 0.7), rgba(0, 0, 0, 0.7)), url('../../public/Institucion_img/banner_ue_jpablo2.jpg');
  background-size: cover;
  background-position: center;
  background-repeat: no-repeat;
  padding: 80px 0;
  position: relative;
  overflow: hidden;
  color: #FFFFFF;
  width: 100%;
}

@media (max-width: 768px) {
  .institution-wrapper {
    padding: 40px 0;
  }
}

.institution-content {
  position: relative;
  z-index: 2;
}

.institution-info h2 {
  font-size: 2.5rem;
  font-weight: 700;
  margin-bottom: 24px;
  color: #FFFFFF;
}

.institution-info p {
  font-size: 1.2rem;
  line-height: 1.7;
  margin-bottom: 40px;
  color: rgba(255, 255, 255, 0.9);
}

.institution-info strong {
  color: #FFD93D;
  font-weight: 700;
}

.institution-logo-small {
  display: inline-flex;
  padding: 20px;
  border-radius: 16px;
}

.inst-logo-small {
  max-height: 60px;
  width: auto;
  filter: drop-shadow(0 4px 8px rgba(0, 0, 0, 0.2));
}

/* ===================== */
/*  Pie de página        */
/* ===================== */
.footer {
  background: #1a1a1a;
  color: #E5E7EB;
  padding: 60px 0 30px;
  width: 100%;
  margin: 0;
}

.footer-container {
  display: flex;
  flex-direction: column;
  gap: 40px;
  width: 100%;
}

.footer-top {
  display: flex;
  justify-content: flex-start;
  align-items: center;
}

.footer-brand {
  display: flex;
  align-items: center;
  gap: 16px;
  font-weight: 700;
  font-size: 1.3rem;
}

.footer-logo {
  width: 40px;
  height: 40px;
}

.footer-text {
  color: #E5E7EB;
  font-weight: 700;
  letter-spacing: 1px;
}

.footer-credits {
  border-top: 1px solid #333333;
  border-bottom: 1px solid #333333;
  padding: 30px 0;
}

.footer-credits h4 {
  font-size: 18px;
  font-weight: 600;
  margin-bottom: 16px;
  color: #FFD93D;
}

.credits-list {
  display: flex;
  gap: 32px;
}

.credit-item {
  color: #B0B0B0;
  text-decoration: none;
  font-size: 15px;
}

.credit-item:hover {
  color: #FFD93D;
}

.credit-item strong {
  font-weight: 600;
}

.footer-bottom {
  text-align: center;
  color: #808080;
  font-size: 14px;
  font-weight: 500;
}

/* ===================== */
/*  Responsive           */
/* ===================== */
@media (max-width: 768px) {
  .hero {
    padding: 120px 0 60px;
  }

  .hero-title,
  .hero-subtitle,
  .hero-quote {
    text-align: center;
  }
  
  .features {
    padding: 60px 0;
  }
  
  .features-grid {
    grid-template-columns: 1fr;
    gap: 30px;
  }
  
  .feature-card {
    padding: 25px 15px;
  }
  
  .feature-icon-circle {
    width: 70px;
    height: 70px;
    font-size: 1.8rem;
  }
  
  .footer {
    padding: 50px 0 25px;
  }
  
  .credits-list {
    flex-direction: column;
    gap: 16px;
  }
  
  .keywords-bar {
    height: 60px;
  }
  
  .keyword-item {
    font-size: 14px;
    gap: 8px;
    padding: 0 25px;
  }
  
  .keyword-item i {
    font-size: 16px;
  }
  
  .institution-wrapper {
    padding: 40px 0;
  }
}

@media (max-width: 480px) {
  .feature-card {
    padding: 20px 10px;
  }
  
  .feature-icon-circle {
    width: 60px;
    height: 60px;
    font-size: 1.5rem;
  }
  
  .institution-wrapper {
    padding: 30px 0;
  }
  
  .footer {
    padding: 40px 0 20px;
  }
  
  .hero-title {
    gap: 5px;
  }
  
  .title-highlight {
    margin-top: 5px;
  }
}
</style>