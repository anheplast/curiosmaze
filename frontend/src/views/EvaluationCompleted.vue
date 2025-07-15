<!-- src/views/EvaluationCompleted.vue -->
<template>
  <div class="evaluation-completed">
    <!-- Overlay de carga -->
    <div v-if="loadingState.isLoading" class="loading-overlay">
      <div class="loading-container">
        <div class="loading-spinner"></div>
        <h3>{{ loadingState.message }}</h3>
        <p v-if="loadingState.attempt > 5">
          Esto está tomando más tiempo de lo esperado...
        </p>
        <p v-if="loadingState.attempt > 10">
          La calificación puede estar tardando debido a la complejidad de los ejercicios.
          Por favor, espere un momento más.
        </p>
      </div>
    </div>

    <!-- Mensaje de error -->
    <div v-else-if="error" class="error-overlay">
      <div class="error-container">
        <div class="error-icon">❌</div>
        <h3>Error al cargar resultados</h3>
        <p>{{ error }}</p>
        <button class="retry-button" @click="retryLoading">
          Intentar nuevamente
        </button>
        <button class="return-button" @click="returnToEvaluationAccess">
          Volver al inicio
        </button>
      </div>
    </div>

    <div v-else class="certificate-paper">
      <!-- Encabezado con título y datos del estudiante -->
      <div class="header-container">
        <!-- Nota y trofeo (parte izquierda) -->
        <div class="score-container">
          <div class="score-card" :class="getScoreColorClass()">
            <div class="score-label">CALIFICACIÓN</div>
            <div class="score-divider"></div>
            <div class="trophy-container">
              <div class="score-value">{{ scaledScore }}/10</div>
              <div class="trophy-icon" :class="getScoreColorClass()">🏆</div>
            </div>
          </div>
        </div>

        <!-- Información del estudiante (parte derecha) -->
        <div class="student-info">
          <div class="student-name">{{ getUserName() || 'Estudiante' }}</div>
          <div class="teacher-name">Prof. {{ getTeacherName() || 'Docente' }}</div>
          <div class="evaluation-date">{{ getEvaluationDate() }}</div>
        </div>
      </div>

      <div class="title-banner">
        <h1>{{ getEvaluationName() || 'Evaluación Completada' }}</h1>
        <div class="completion-badge">¡COMPLETADO!</div>
      </div>

      <!-- Estadísticas principales -->
      <div class="stats-grid">
        <div class="stat-box">
          <div class="stat-icon">⏱️</div>
          <div class="stat-value">{{ formatCompletionTime() }}</div>
          <div class="stat-label">Tiempo</div>
        </div>

        <div class="stat-box">
          <div class="stat-icon">✅</div>
          <div class="stat-value">{{ getCompletedExercisesCount() }}/{{ exercises.length }}</div>
          <div class="stat-label">Completados</div>
        </div>

        <div class="stat-box">
          <div class="stat-icon">🎯</div>
          <div class="stat-value">{{ calculateAccuracy() }}%</div>
          <div class="stat-label">Precisión</div>
        </div>

        <div class="stat-box">
          <div class="stat-icon">📝</div>
          <div class="stat-value">{{ totalScore }}/{{ maxScore }}</div>
          <div class="stat-label">Puntos</div>
        </div>
      </div>

      <!-- Sección de ejercicios -->
      <div class="exercises-section">
        <div class="section-title">
          <span class="section-icon">📋</span>
          Ejercicios
        </div>

        <div v-if="loadingExercises" class="loading-container">
          <div class="loader"></div>
          <p>Cargando ejercicios...</p>
        </div>

        <div v-else-if="exercises.length === 0" class="empty-container">
          <div class="empty-icon">📝</div>
          <p>No hay ejercicios disponibles</p>
        </div>

        <div v-else class="exercises-list">
          <div v-for="(exercise, index) in exercises" :key="exercise.id || exercise.ejercicio_id" 
               class="exercise-item" :class="exercise.es_correcta ? 'completed' : 'incorrect'">
            <!-- Encabezado del ejercicio -->
            <div class="exercise-header">
              <div class="exercise-status">
                <span class="status-icon">{{ exercise.es_correcta ? '✓' : '❌' }}</span>
              </div>
              <div class="exercise-title">{{ exercise.titulo || exercise.ejercicio_titulo || `Ejercicio ${index + 1}` }}</div>
            </div>
            
            <!-- Barra de progreso (100% si está correcto, 0% si no) -->
            <div class="exercise-progress">
              <div class="progress-bar" :class="exercise.es_correcta ? 'success' : 'failure'"></div>
            </div>
            
            <!-- Código de solución -->
            <div class="exercise-code">
              <div class="code-header">
                <span class="code-label">Solución:</span>
                <span class="code-language">{{ getLanguageNameForExercise(exercise) }}</span>
              </div>
              <pre class="code-block"><code>{{ exercise.codigo || 'Sin código' }}</code></pre>
              <div class="code-output" v-if="exercise.resultados">
                <div class="output-header">Resultado:</div>
                <pre class="output-content">{{ exercise.resultados }}</pre>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Botón de acción -->
      <div class="action-button-container">
        <button class="action-button" @click="returnToEvaluationAccess">
          <span class="button-icon">🏠</span>
          <span>Volver al inicio</span>
        </button>
      </div>

      <!-- Firma del certificado -->
      <div class="certificate-footer">
        <div class="certificate-stamp" style="width: 314px;">
          <span>CURIOSMAZE</span>
          <div class="logo-container">
            <img src="../../public/logo/Logo-CuriosMaze-40x40.png" alt="Logo" class="certificate-logo">
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, computed, onMounted, inject } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import { useStore } from 'vuex';
import evaluationsService from '@/api/evaluationsService';


export default {
  name: 'EvaluationCompleted',
  props: {
    evaluation_id: {
      type: [String, Number],
      default: null
    }
  },
  setup(props) {
    const route = useRoute();
    const router = useRouter();
    const store = useStore();
    const evaluation = ref(null); 
    
    // Estados reactivos
    const exercises = ref([]);
    const loadingExercises = ref(true);
    const totalScore = ref(0);
    const maxScore = ref(0);
    const scaledScore = ref(0);
    const completionTime = ref(0);
    const error = ref('');

    const availableLanguages = ref([]);
    const languagesLoaded = ref(false);
    
    // Computeds
    const evaluationId = computed(() => {
      // PRIORIDAD 1: Props
      if (props.evaluation_id) {
        console.log(`🔍 ID desde props: ${props.evaluation_id}`);
        return props.evaluation_id;
      }

      // PRIORIDAD 2: Query params de la URL
      if (route.query.evaluation_id) {
        console.log(`🔍 ID desde query: ${route.query.evaluation_id}`);
        return route.query.evaluation_id;
      }

      // PRIORIDAD 3: LocalStorage (solo como último recurso)
      const storedId = localStorage.getItem('completedEvaluationId');
      if (storedId) {
        console.log(`🔍 ID desde localStorage: ${storedId}`);
        return storedId;
      }

      console.warn("⚠️ No se pudo determinar ID de evaluación");
      return null;
    });

    // Estado de carga y error mejorados
    const loadingState = ref({
      isLoading: true,
      message: "Cargando resultados...",
      attempt: 0
    });


    // Verificar que los datos estén listos para cargar
    const esperarDatosCompletos = async () => {
      const userId = getCurrentUserId();
      const evaluationId = route.query.evaluation_id || localStorage.getItem('completedEvaluationId');

      // Verificar si los datos críticos están disponibles
      const verificarDisponibilidad = () => {
        const puntajeDisponible = localStorage.getItem(`evaluation_scaled_score_${userId}`);
        const resultadosDisponibles = localStorage.getItem(`evaluation_raw_results_${userId}`);
        return puntajeDisponible && resultadosDisponibles;
      };

      // Intentar hasta 5 veces con espera progresiva
      for (let intento = 1; intento <= 5; intento++) {
        if (verificarDisponibilidad()) {
          console.log(`✅ Datos completos disponibles (intento ${intento})`);
          return true;
        }

        console.log(`⏳ Esperando datos completos (intento ${intento}/5)...`);
        await new Promise(resolve => setTimeout(resolve, intento * 200));
      }

      console.warn("⚠️ No se pudieron verificar todos los datos después de 5 intentos");
      return false;
    };


    // Método para reintentar carga
    const retryLoading = async () => {
      loadingState.value = {
        isLoading: true,
        message: "Reintentando cargar resultados...",
        attempt: 0
      };
      error.value = '';
      
      await loadEvaluationData();
      await loadExerciseDetails();
    };
    
    const currentUserId = computed(() => {
      return store.getters['auth/userId'] || 
             localStorage.getItem('user_id') || 
             'anonymous';
    });

    // Obtener ID del usuario actual (método de utilidad)
    const getCurrentUserId = () => {
      return currentUserId.value;
    };


    // Función para obtener el nombre del lenguaje por ejercicio
    const getLanguageName = (exerciseId) => {
      try {
        // Buscar el ejercicio en los datos
        const exercise = exercises.value.find(ex => 
          ex.ejercicio_id === exerciseId || ex.id === exerciseId
        );

        if (exercise && exercise.codigo) {
          const code = exercise.codigo.trim();
          console.log(`🔍 Detectando lenguaje para ejercicio ${exerciseId} desde código`);
          
          // Detectar lenguaje basado en patrones únicos del código
          
          // Python
          if (code.includes('print(') && !code.includes('System.out.print') && !code.includes('console.log')) {
            console.log(`✅ Detectado Python para ejercicio ${exerciseId}`);
            return 'Python (3.8.1)';
          }
          
          // JavaScript
          if (code.includes('console.log') || code.includes('function ') || 
              (code.includes('let ') || code.includes('const ') || code.includes('var ')) && 
              !code.includes('#include')) {
            console.log(`✅ Detectado JavaScript para ejercicio ${exerciseId}`);
            return 'JavaScript (Node.js 12.14.0)';
          }
          
          // C#
          if (code.includes('using System') || code.includes('Console.WriteLine') || 
              code.includes('class Program') && code.includes('static void Main')) {
            console.log(`✅ Detectado C# para ejercicio ${exerciseId}`);
            return 'C# (Mono 6.6.0.161)';
          }
          
          // Java
          if (code.includes('public class') && code.includes('public static void main') && 
              code.includes('System.out.print')) {
            console.log(`✅ Detectado Java para ejercicio ${exerciseId}`);
            return 'Java (OpenJDK 13.0.1)';
          }
          
          // C++
          if (code.includes('#include <iostream>') || 
              (code.includes('#include') && (code.includes('cout') || code.includes('std::cout')))) {
            console.log(`✅ Detectado C++ para ejercicio ${exerciseId}`);
            return 'C++ (GCC 9.2.0)';
          }
          
          // C
          if (code.includes('#include <stdio.h>') || 
              (code.includes('#include') && code.includes('printf'))) {
            console.log(`✅ Detectado C para ejercicio ${exerciseId}`);
            return 'C (GCC 9.2.0)';
          }
          
          // Go
          if (code.includes('package main') && code.includes('fmt.Print')) {
            console.log(`✅ Detectado Go para ejercicio ${exerciseId}`);
            return 'Go (1.13.5)';
          }
          
          // Rust
          if (code.includes('fn main()') && code.includes('println!')) {
            console.log(`✅ Detectado Rust para ejercicio ${exerciseId}`);
            return 'Rust (1.40.0)';
          }
          
          // PHP
          if (code.includes('<?php') || code.includes('echo ')) {
            console.log(`✅ Detectado PHP para ejercicio ${exerciseId}`);
            return 'PHP (7.4.1)';
          }
          
          // Ruby
          if (code.includes('puts ') && !code.includes('#include')) {
            console.log(`✅ Detectado Ruby para ejercicio ${exerciseId}`);
            return 'Ruby (2.7.0)';
          }
        }
        
        // Si no se puede detectar, usar Python por defecto
        console.log(`⚠️ No se pudo detectar lenguaje para ejercicio ${exerciseId}, usando Python por defecto`);
        return 'Python (3.8.1)';
      } catch (error) {
        console.warn('❌ Error al detectar lenguaje:', error);
        return 'Python (3.8.1)';
      }
    };

    // Obtener nombre del usuario
    const getUserName = () => {
      return localStorage.getItem('user_name') || '';
    };

    // Obtener nombre del docente
    const getTeacherName = () => {
      try {
        const evalData = localStorage.getItem('currentEvaluation');
        if (evalData) {
          const evaluation = JSON.parse(evalData);

          // Buscar en la información del creador
          if (evaluation.creador) {
            if (evaluation.creador.nombres && evaluation.creador.apellidos) {
              return `${evaluation.creador.nombres} ${evaluation.creador.apellidos}`;
            } else if (evaluation.creador.username) {
              return evaluation.creador.username;
            }
          }

          // Fallbacks
          if (evaluation.creador_nombre) return evaluation.creador_nombre;
          if (evaluation.docente_nombre) return evaluation.docente_nombre;
        }
        return 'Docente';
      } catch (error) {
        console.error('Error al leer nombre del docente:', error);
        return 'Docente';
      }
    };

    // Obtener fecha de la evaluación
    const getEvaluationDate = () => {
      try {
        const evalData = localStorage.getItem('currentEvaluation');
        if (evalData) {
          const evaluation = JSON.parse(evalData);
          if (evaluation.fecha_inicio) {
            const fecha = new Date(evaluation.fecha_inicio);
            return fecha.toLocaleDateString('es-ES', {
              weekday: 'long',
              year: 'numeric',
              month: 'long',
              day: 'numeric'
            });
          }
        }
        return new Date().toLocaleDateString('es-ES', {
          weekday: 'long',
          year: 'numeric',
          month: 'long',
          day: 'numeric'
        });
      } catch (error) {
        console.error('Error al leer fecha de evaluación:', error);
        return new Date().toLocaleDateString('es-ES');
      }
    };

    // Obtener nombre de la evaluación
    const getEvaluationName = () => {
      try {
        const evalData = localStorage.getItem('currentEvaluation');
        if (evalData) {
          const evaluation = JSON.parse(evalData);
          return evaluation.titulo || evaluation.title || 'Evaluación';
        }
        return 'Evaluación';
      } catch (error) {
        console.error('Error al leer nombre de evaluación:', error);
        return 'Evaluación';
      }
    };

    // Función para obtener códigos para todos los ejercicios
    function getCodesForExercises() {
      try {
        // Obtener el ID de usuario
        const userId = localStorage.getItem('user_id') || 'anonymous';
        const evaluationId = localStorage.getItem('completedEvaluationId');

        // Si no hay ID de evaluación, no podemos continuar
        if (!evaluationId) {
          console.warn("⚠️ No se encontró ID de evaluación para buscar códigos");
          return {};
        }

        console.log(`🔍 Buscando códigos de ejercicios para evaluación ${evaluationId}`);

        // Buscar todas las claves de localStorage que contienen códigos de ejercicios
        const codeKeys = Object.keys(localStorage).filter(key =>
          key.startsWith(`exercise_code_${userId}_${evaluationId}_`) ||
          key.startsWith(`exercise_code_${userId}_`)
        );

        console.log(`🔑 Encontradas ${codeKeys.length} claves de código`);

        // Extraer los códigos y asociarlos a IDs de ejercicios
        const exerciseCodes = {};

        codeKeys.forEach(key => {
          // Extraer ID de ejercicio de la clave
          let exerciseId;
          if (key.startsWith(`exercise_code_${userId}_${evaluationId}_`)) {
            exerciseId = key.split('_').pop();
          } else {
            exerciseId = key.split('_').pop();
          }

          // Si es un ID válido, guardar el código
          if (exerciseId && !isNaN(parseInt(exerciseId))) {
            exerciseCodes[exerciseId] = localStorage.getItem(key) || '';
            console.log(`📝 ID ${exerciseId}: ${exerciseCodes[exerciseId].length} caracteres`);
          }
        });

        return exerciseCodes;
      } catch (e) {
        console.error("Error al recopilar códigos de ejercicios:", e);
        return {};
      }
    }

    // Función para obtener puntuaciones de múltiples fuentes
    function getRobustScoreData() {
      const userId = localStorage.getItem('user_id') || 'anonymous';
      
      // Intentar obtener datos de múltiples fuentes posibles en orden de prioridad
      let totalScore = null;
      let maxScore = null;
      let scaledScore = null;
      
      // Primero intenta con el formato nuevo específico por usuario
      totalScore = localStorage.getItem(`evaluation_total_score_${userId}`);
      maxScore = localStorage.getItem(`evaluation_max_score_${userId}`);
      scaledScore = localStorage.getItem(`evaluation_scaled_score_${userId}`);
      
      // Segundo si no hay datos específicos, intentar con formato genérico
      if (!totalScore) totalScore = localStorage.getItem('evaluation_total_score');
      if (!maxScore) maxScore = localStorage.getItem('evaluation_max_score');
      if (!scaledScore) scaledScore = localStorage.getItem('evaluation_scaled_score');
      
      // Tercero intenta obtener desde resultados raw si están disponibles
      if (!totalScore || !maxScore || !scaledScore) {
        try {
          const rawData = localStorage.getItem(`evaluation_raw_results_${userId}`);
          if (rawData) {
            const parsedData = JSON.parse(rawData);
            if (parsedData.total_puntaje) totalScore = parsedData.total_puntaje;
            if (parsedData.puntaje_maximo) maxScore = parsedData.puntaje_maximo;
            if (parsedData.puntaje_sobre_10) scaledScore = parsedData.puntaje_sobre_10;
          }
        } catch (e) {
          console.warn('Error al extraer datos de evaluation_raw_results:', e);
        }
      }
      
      // Cuarto calcula scaledScore si tenemos totalScore y maxScore pero no scaledScore
      if (totalScore && maxScore && !scaledScore) {
        scaledScore = ((parseFloat(totalScore) / parseFloat(maxScore)) * 10).toFixed(2);
      }
      
      // Quinto valores por defecto si todo falla
      if (!totalScore) totalScore = "0";
      if (!maxScore) maxScore = "10";
      if (!scaledScore) scaledScore = "0";
      
      // Retornar objeto con valores numéricos
      return {
        totalScore: parseFloat(totalScore),
        maxScore: parseFloat(maxScore),
        scaledScore: parseFloat(scaledScore)
      };
    }

    // Función para cargar ejercicios desde localStorage
    const loadExercisesFromLocalStorage = () => {
      try {
        const userId = getCurrentUserId();
        console.log("🔄 Cargando ejercicios desde localStorage");

        // Primero intenta con respuestas de datos brutos
        const rawResultsKey = `evaluation_raw_results_${userId}`;
        const rawResultsData = localStorage.getItem(rawResultsKey);

        if (rawResultsData) {
          try {
            const parsedResults = JSON.parse(rawResultsData);

            if (parsedResults.resultados && Array.isArray(parsedResults.resultados)) {
              console.log(`📋 Encontrados ${parsedResults.resultados.length} resultados en evaluation_raw_results`);

              // Transformar resultados al formato esperado de ejercicios
              const ejerciciosFormateados = parsedResults.resultados.map(resultado => {
                // Buscar código del ejercicio
                const ejercicioId = resultado.ejercicio_id;
                let codigo = '';

                // Intentar obtener código del ejercicio usando la clave correcta
                try {
                  const evaluationId = evaluation.value?.id ||
                    localStorage.getItem('completedEvaluationId') || 'unknown';

                  const codeKey = `exercise_code_${userId}_${evaluationId}_${ejercicioId}`;
                  codigo = localStorage.getItem(codeKey) || '';

                  if (!codigo) {
                    // Intentar clave alternativa (antigua)
                    codigo = localStorage.getItem(`exercise_code_${userId}_${ejercicioId}`) || '';
                  }

                  console.log(`📝 Código para ejercicio ${ejercicioId}: ${codigo ? codigo.length : 0} caracteres`);
                } catch (e) {
                  console.warn(`Error al obtener código para ejercicio ${ejercicioId}:`, e);
                }

                // Buscar título del ejercicio en el listado de evaluación actual
                let titulo = `Ejercicio ${ejercicioId}`;
                let descripcion = '';

                // Determinar si el ejercicio es correcto
                const es_correcta = resultado.es_correcto || false;

                // Construir objeto completo
                return {
                  ejercicio_id: ejercicioId,
                  id: ejercicioId,
                  titulo: titulo,
                  ejercicio_titulo: titulo, // Redundancia para compatibilidad
                  descripcion: descripcion,
                  ejercicio_descripcion: descripcion, // Redundancia para compatibilidad
                  es_correcta: es_correcta,
                  puntaje_obtenido: resultado.puntaje_obtenido || 0,
                  puntaje_maximo: resultado.puntaje_maximo || 10,
                  codigo: codigo, // Código del ejercicio
                  resultados: resultado.output || '',
                  stderr: resultado.stderr || ''
                };
              });

              // Si hay ejercicios formateados, usarlos
              if (ejerciciosFormateados.length > 0) {
                console.log(`✅ Formateados ${ejerciciosFormateados.length} ejercicios desde resultados raw`);
                exercises.value = ejerciciosFormateados;
                loadingExercises.value = false;
                return true;
              }
            }
          } catch (e) {
            console.warn("Error al parsear resultados raw:", e);
          }
        }

        // Segundo intenta con datos en el objeto evaluation.value 
        if (evaluation.value && evaluation.value.respuestas && Array.isArray(evaluation.value.respuestas)) {
          const respuestas = evaluation.value.respuestas;
          console.log(`📋 Usando ${respuestas.length} respuestas desde evaluation.value`);

          // Transformar respuestas al formato de ejercicios
          const ejerciciosDesdeEval = respuestas.map(respuesta => {
            // Buscar código del ejercicio usando las claves correctas
            let codigo = '';
            const ejercicioId = respuesta.ejercicio_id;

            try {
              const evaluationId = evaluation.value?.id ||
                localStorage.getItem('completedEvaluationId') || 'unknown';

              const codeKey = `exercise_code_${userId}_${evaluationId}_${ejercicioId}`;
              codigo = localStorage.getItem(codeKey) || '';

              if (!codigo) {
                // Intentar clave alternativa
                codigo = localStorage.getItem(`exercise_code_${userId}_${ejercicioId}`) || '';
              }

              // Si el código está en la respuesta, usarlo
              if (respuesta.codigo) {
                codigo = respuesta.codigo;
              }

              console.log(`📝 Código para ejercicio ${ejercicioId}: ${codigo ? codigo.length : 0} caracteres`);
            } catch (e) {
              console.warn(`Error al obtener código para ejercicio ${ejercicioId}:`, e);
            }

            // Determinar si el ejercicio es correcto
            const es_correcta = respuesta.es_correcta !== undefined ?
              respuesta.es_correcta : (respuesta.puntaje_obtenido >= respuesta.puntaje_maximo);

            return {
              ejercicio_id: ejercicioId,
              id: ejercicioId,
              titulo: respuesta.ejercicio_titulo || `Ejercicio ${ejercicioId}`,
              ejercicio_titulo: respuesta.ejercicio_titulo || `Ejercicio ${ejercicioId}`,
              descripcion: respuesta.ejercicio_descripcion || '',
              ejercicio_descripcion: respuesta.ejercicio_descripcion || '',
              es_correcta: es_correcta,
              puntaje_obtenido: respuesta.puntaje_obtenido || 0,
              puntaje_maximo: respuesta.puntaje_maximo || 10,
              codigo: codigo,
              resultados: respuesta.output || respuesta.resultados || '',
              stderr: respuesta.stderr || ''
            };
          });

          // Si hay ejercicios, los usa
          if (ejerciciosDesdeEval.length > 0) {
            console.log(`✅ Preparados ${ejerciciosDesdeEval.length} ejercicios desde evaluation.value`);
            exercises.value = ejerciciosDesdeEval;
            loadingExercises.value = false;
            return true;
          }
        }

        // Tercero -> Fallback: buscar ejercicios mediante historial
        console.log("🔄 Intentando reconstruir ejercicios desde historial");
        loadingExercises.value = false;
        return false;
      } catch (e) {
        console.error("Error general en loadExercisesFromLocalStorage:", e);
        loadingExercises.value = false;
        return false;
      }
    };

    // Verificaciones y correcciones finales
    async function performFinalChecks() {
      try {
        console.log("🧐 Realizando verificaciones finales...");
        
        // Primero verifica que los ejercicios tengan código - si no, intenta añadirlo
        if (exercises.value && exercises.value.length > 0) {
          const ejerciciosSinCodigo = exercises.value.filter(ej => !ej.codigo || ej.codigo.trim() === '');

          if (ejerciciosSinCodigo.length > 0) {
            console.log(`⚠️ Se encontraron ${ejerciciosSinCodigo.length} ejercicios sin código. Intentando recuperar...`);

            // Obtener todos los códigos disponibles
            const exerciseCodes = getCodesForExercises();

            // Actualizar ejercicios sin código
            exercises.value = exercises.value.map(ejercicio => {
              if (!ejercicio.codigo || ejercicio.codigo.trim() === '') {
                const id = ejercicio.ejercicio_id || ejercicio.id;
                if (exerciseCodes[id]) {
                  console.log(`✅ Recuperado código para ejercicio ${id}`);
                  return { ...ejercicio, codigo: exerciseCodes[id] };
                }
              }
              return ejercicio;
            });

            // Intenta otra búsqueda para ejercicios que aún no tienen código
            exercises.value.forEach((ejercicio, index) => {
              if (!ejercicio.codigo || ejercicio.codigo.trim() === '') {
                const id = ejercicio.ejercicio_id || ejercicio.id;

                // Buscar con otros formatos posibles
                const userId = getCurrentUserId();
                const claves = [
                  `exercise_code_${userId}_${id}`,
                  `exercise_code_${evaluation.value?.id}_${id}`,
                  `exercise_code_${userId}_${evaluation.value?.id}_${id}`
                ];

                for (const clave of claves) {
                  const codigoEncontrado = localStorage.getItem(clave);
                  if (codigoEncontrado) {
                    console.log(`✅ Recuperado código para ejercicio ${id} con clave ${clave}`);
                    exercises.value[index].codigo = codigoEncontrado;
                    break;
                  }
                }
              }
            });
          }
        }
        
        // Segundo verifica si statistics son correctos (completados_count y ejercicios_count)
        if (evaluation.value) {
          // Si es necesario, actualizar contadores
          if (exercises.value && exercises.value.length > 0) {
            const completados = exercises.value.filter(e => e.es_correcta === true).length;
            
            if (!evaluation.value.completados_count || evaluation.value.completados_count === 0) {
              console.log(`📊 Actualizando contador de completados: ${completados}`);
              evaluation.value.completados_count = completados;
            }
            
            if (!evaluation.value.ejercicios_count || evaluation.value.ejercicios_count === 0) {
              console.log(`📊 Actualizando contador de ejercicios: ${exercises.value.length}`);
              evaluation.value.ejercicios_count = exercises.value.length;
            }
          }
        }
        
        console.log("✅ Verificaciones finales completadas");
      } catch (e) {
        console.error("Error en verificaciones finales:", e);
      }
    }

    // Función de recuperación completa de emergencia
    const loadFromLocalStorage = () => {
      try {
        console.log("🔄 Intentando recuperación de emergencia desde localStorage");

        // Usar método robusto para obtener puntuaciones
        const scoreData = getRobustScoreData();
        totalScore.value = scoreData.totalScore;
        maxScore.value = scoreData.maxScore;
        scaledScore.value = scoreData.scaledScore;
        
        console.log("📊 Puntuaciones recuperadas de forma robusta:", scoreData);
        
        // Segundo calcula duración si es posible
        const userId = getCurrentUserId();
        const startTime = parseInt(localStorage.getItem(`evaluationStartTime_${userId}`) ||
          localStorage.getItem('evaluationStartTime') || '0');

        const endTime = parseInt(localStorage.getItem(`evaluationEndTime_${userId}`) || '0');

        if (startTime > 0 && endTime > 0) {
          completionTime.value = endTime - startTime;
          console.log("🔄 Tiempo calculado:", completionTime.value);
        }

        // Tercero calcula color clase basado en puntuación
        let colorClase = 'poor';
        if (scaledScore.value >= 9) colorClase = 'excellent';
        else if (scaledScore.value >= 7) colorClase = 'good';
        else if (scaledScore.value >= 5) colorClase = 'average';

        // Cuarto crea un objeto de evaluación básico
        evaluation.value = {
          id: evaluationId.value,
          titulo: getEvaluationName(),
          puntaje_total: totalScore.value,
          puntaje_maximo: maxScore.value,
          puntaje_sobre_10: scaledScore.value,
          color_clase: colorClase,
          formattedScore: `${scaledScore.value.toFixed(1)}/10`,
          formattedScoreDisplay: scaledScore.value >= 9 ? "¡Excelente!" :
            scaledScore.value >= 7 ? "¡Muy bien!" :
              scaledScore.value >= 5 ? "Regular" :
                "Necesita mejorar",
          showAchievement: scaledScore.value >= 9,
          ejercicios_count: 0,
          completados_count: 0
        };

        // Buscar códigos para los ejercicios
        const exerciseCodes = getCodesForExercises();
        
        // Si tenemos códigos de ejercicios, podemos reconstruir los ejercicios
        if (Object.keys(exerciseCodes).length > 0) {
          console.log(`🔍 Encontrados ${Object.keys(exerciseCodes).length} códigos de ejercicios`);
          
          // Crear ejercicios basados en estos códigos
          const reconstructedExercises = Object.entries(exerciseCodes).map(([id, code]) => {
            return {
              id: parseInt(id),
              ejercicio_id: parseInt(id),
              titulo: `Ejercicio ${id}`,
              ejercicio_titulo: `Ejercicio ${id}`,
              descripcion: '',
              ejercicio_descripcion: '',
              es_correcta: false, // Por defecto, no se conoce si es correcto
              puntaje_obtenido: 0,
              puntaje_maximo: 10,
              codigo: code,
              resultados: '',
              stderr: ''
            };
          });
          
          // Si tenemos ejercicios, usarlos
          if (reconstructedExercises.length > 0) {
            console.log(`⚒️ Reconstruidos ${reconstructedExercises.length} ejercicios desde códigos`);
            exercises.value = reconstructedExercises;
          }
        }

        // Quinto cargar ejercicios
        loadExercisesFromLocalStorage();

        // Sexto actualizar contadores
        if (exercises.value.length > 0) {
          evaluation.value.ejercicios_count = exercises.value.length;
          evaluation.value.completados_count = exercises.value.filter(e => e.es_correcta).length;
        }

        console.log("✅ Recuperación de emergencia completada");
      } catch (e) {
        console.error("Error en recuperación de emergencia:", e);
      }
    };

    // Función auxiliar para parsear duración de tiempo
    const parseTimeDuration = (timeString) => {
      if (!timeString) return 0;
      
      // Si es formato HH:MM:SS
      const parts = timeString.split(':');
      if (parts.length === 3) {
        const hours = parseInt(parts[0]) || 0;
        const minutes = parseInt(parts[1]) || 0;
        const seconds = parseInt(parts[2]) || 0;
        return (hours * 3600 + minutes * 60 + seconds) * 1000;
      }
      
      return 0;
    };

    // Cargar datos de la evaluación
    const loadEvaluationData = async () => {
      loadingState.value.isLoading = true;
      loadingState.value.message = "Cargando resultados de evaluación...";
      loadingState.value.attempt = 0;
      error.value = '';

      try {
        // Espera a que los datos estén disponibles
        await esperarDatosCompletos();
        // Buscar el ID de evaluación en múltiples fuentes
        let evalId = evaluationId.value;

        // Si no tenemos ID en props o route, intentar obtenerlo de localStorage
        if (!evalId) {
          const userId = getCurrentUserId();
          console.log("🔍 Buscando ID de evaluación en localStorage para usuario:", userId);

          // Intentar recuperar de completedEvaluationId (forma tradicional)
          evalId = localStorage.getItem('completedEvaluationId');
          console.log("🔍 ID desde completedEvaluationId:", evalId);

          // Si no hay ID por la forma tradicional, buscar en el resultado de Judge0
          if (!evalId) {
            const rawResultsKey = `evaluation_raw_results_${userId}`;
            const rawResultsData = localStorage.getItem(rawResultsKey);

            if (rawResultsData) {
              try {
                const jsonData = JSON.parse(rawResultsData);
                const evalData = localStorage.getItem('currentEvaluation');

                if (evalData) {
                  const evaluationObj = JSON.parse(evalData);
                  evalId = evaluationObj.id;
                  console.log("🔍 ID recuperado desde currentEvaluation:", evalId);
                }
              } catch (e) {
                console.warn("Error al parsear datos raw:", e);
              }
            }
          }

          // Busca en localStorage específico por usuario
          if (!evalId) {
            // Buscar keys que puedan contener evaluationStartTime_userId_evalId
            const startTimeKeys = Object.keys(localStorage).filter(
              key => key.startsWith(`evaluationStartTime_${userId}_`)
            );

            if (startTimeKeys.length > 0) {
              // Obtener el ID de la última evaluación iniciada
              const lastKey = startTimeKeys[startTimeKeys.length - 1];
              evalId = lastKey.split('_')[2];
              console.log("🔍 ID recuperado desde patrón evaluationStartTime:", evalId);
            }
          }

          // Actualizar el valor reactivo
          if (evalId) {
            evaluationId.value = evalId;
            console.log("✅ ID de evaluación recuperado:", evalId);

            // Guardar en localStorage para futuros intentos
            localStorage.setItem('completedEvaluationId', evalId);
          } else {
            console.warn("⚠️ No se pudo recuperar ID de evaluación de ninguna fuente");
          }
        }

        // Si tenemos ID, intentar cargar los datos de la API
        if (evalId) {
          const userId = getCurrentUserId();
          console.log("🔍 Intentando cargar evaluación ID:", evalId);

          // Recuperar datos locales si están disponibles
          // Intentar obtener datos de localStorage
          const localData = localStorage.getItem(`evaluation_raw_results_${userId}`);
          const localScaledScore = localStorage.getItem(`evaluation_scaled_score_${userId}`);

          // Si tenemos datos locales, verificar si podemos usarlos
          if (localData && localScaledScore) {
            try {
              const localResults = JSON.parse(localData);
              if (localResults.total_puntaje !== undefined &&
                localResults.puntaje_maximo !== undefined) {

                console.log("📊 Encontrados datos locales válidos, pre-cargando...");
                // Usar datos locales mientras esperamos la API
                totalScore.value = localResults.total_puntaje;
                maxScore.value = localResults.puntaje_maximo;
                scaledScore.value = parseFloat(localScaledScore);
              }
            } catch (e) {
              console.warn("Error al pre-cargar datos locales:", e);
            }
          }

          // Mostrar overlay de carga
          loadingState.value = {
            isLoading: true,
            message: "Cargando resultados de evaluación...",
            attempt: 0
          };

          // Obtener todos los datos directamente del backend
          const response = await evaluationsService.getEvaluationCompleteResults(evalId);
          console.log("Respuesta de resultados completos:", response.data);

          if (!response.data || !response.data.success) {
            throw new Error('Datos de evaluación no disponibles o incompletos');
          }

          const evalData = response.data.evaluation;
          console.log("Datos de evaluación:", evalData);

          // CORREGIR PUNTUACIÓN RECIBIDA
          // Convertir a número si es string
          if (typeof evalData.puntaje_sobre_10 !== 'number') {
            evalData.puntaje_sobre_10 = parseFloat(evalData.puntaje_sobre_10) || 0;
          }

          // Verificar si el valor es correcto - corregir si es necesario
          if (evalData.puntaje_sobre_10 &&
            (evalData.puntaje_sobre_10 < 0 || evalData.puntaje_sobre_10 > 10 ||
              evalData.puntaje_sobre_10.toString().length > 10)) {
            console.log("⚠️ Corrigiendo valor de puntaje_sobre_10 incorrecto:", evalData.puntaje_sobre_10);

            // Recalcular si parece inválido
            if (evalData.puntaje_total && evalData.puntaje_maximo && evalData.puntaje_maximo > 0) {
              evalData.puntaje_sobre_10 = parseFloat(((evalData.puntaje_total / evalData.puntaje_maximo) * 10).toFixed(2));
              console.log("📊 Puntuación recalculada:", evalData.puntaje_sobre_10);
            }
          }

          // SEGUNDA VERIFICACIÓN - Si tenemos valores locales que parecen más precisos, usarlos
          if (localScaledScore) {
            const localScore = parseFloat(localScaledScore);
            // Solo sobreescribir si el valor local parece razonable y diferente
            if (!isNaN(localScore) && localScore >= 0 && localScore <= 10 &&
              Math.abs(localScore - evalData.puntaje_sobre_10) > 0.1) {
              console.log(`⚠️ Detectada discrepancia: API=${evalData.puntaje_sobre_10}, localStorage=${localScore}`);
              console.log("📊 Usando puntuación almacenada localmente por mayor precisión");
              evalData.puntaje_sobre_10 = localScore;
            }
          }

          // Formatear valores
          evalData.formattedScore = `${parseFloat(evalData.puntaje_sobre_10).toFixed(2)}/10`;

          // GUARDAR COLOR CORRECTO BASADO EN LA PUNTUACIÓN
          if (!evalData.color_clase || evalData.color_clase === "poor") {
            const score = evalData.puntaje_sobre_10;
            if (score >= 9) evalData.color_clase = 'excellent';
            else if (score >= 7) evalData.color_clase = 'good';
            else if (score >= 5) evalData.color_clase = 'average';
            else evalData.color_clase = 'poor';

            console.log(`📊 Estableciendo color_clase basado en puntuación ${score}: ${evalData.color_clase}`);
          }

          // Aplicar todos los valores corregidos
          evaluation.value = evalData;
          totalScore.value = evalData.puntaje_total || 0;
          maxScore.value = evalData.puntaje_maximo || 0;
          scaledScore.value = parseFloat(evalData.puntaje_sobre_10) || 0;

          // Obtener tiempo total desde la API (ya incluido en evalData)
          if (evalData.tiempo_total_ms) {
            completionTime.value = evalData.tiempo_total_ms;
            console.log("⏱️ Tiempo obtenido desde BD:", completionTime.value);
          } else if (evalData.tiempo_total) {
            completionTime.value = parseTimeDuration(evalData.tiempo_total);
            console.log("⏱️ Tiempo parseado desde tiempo_total:", completionTime.value);
          } else {
            // Fallback: calcular desde fechas o localStorage
            if (evalData.fecha_fin && evalData.fecha_inicio) {
              const start = new Date(evalData.fecha_inicio);
              const end = new Date(evalData.fecha_fin);
              completionTime.value = end - start;
              console.log("⏱️ Tiempo calculado desde fechas:", completionTime.value);
            } else {
              // Último recurso: localStorage
              const userId = getCurrentUserId();
              const startTime = parseInt(localStorage.getItem(`evaluationStartTime_${userId}`) || '0');
              const endTime = parseInt(localStorage.getItem(`evaluationEndTime_${userId}`) || '0');

              if (startTime > 0 && endTime > 0) {
                completionTime.value = endTime - startTime;
                console.log("⏱️ Tiempo calculado desde localStorage:", completionTime.value);
              }
            }
          }

          // Comprobar si hay datos de ejercicios/respuestas
          if (evalData.respuestas && Array.isArray(evalData.respuestas)) {
            console.log(`Cargadas ${evalData.respuestas.length} respuestas desde API`);
            exercises.value = evalData.respuestas;
            loadingExercises.value = false; // Marcar como cargados
          } else {
            console.warn("No se encontraron respuestas en los datos de evaluación");
            exercises.value = [];

            // Intentar cargar desde localStorage como plan B
            loadExercisesFromLocalStorage();
          }

          loadingState.value.isLoading = false;
          console.log("✅ Datos cargados correctamente");
          return evalData.id;
        } else {
          // No tenemos ID, usar recuperación de emergencia
          console.log("🚨 Usando recuperación de emergencia sin ID de evaluación");
          loadFromLocalStorage();
          loadingState.value.isLoading = false;
        }
      } catch (error) {
        console.error('Error al cargar datos de evaluación:', error);

        // Intentar recuperación de emergencia desde localStorage
        loadFromLocalStorage();

        loadingState.value.isLoading = false;
        error.value = `Error al cargar resultados: ${error.message}`;
        return null;
      }
    };


    // Cargar detalles de ejercicios
    const loadExerciseDetails = async () => {
      try {
        if (!evaluationId.value) {
          console.warn('No hay ID de evaluación disponible para cargar ejercicios');
          return;
        }

        console.log(`🔍 Cargando detalles de ejercicios para evaluación ID: ${evaluationId.value}`);

        // Intentar obtener ejercicios mediante API de detalles
        try {
          const response = await evaluationsService.getDetallesEvaluacion(evaluationId.value);
          console.log('📊 Datos de detalles recibidos:', response.data);

          if (response.data && response.data.ejercicios && response.data.ejercicios.length > 0) {
            console.log(`✅ Obtenidos ${response.data.ejercicios.length} ejercicios mediante API de detalles`);
            exercises.value = response.data.ejercicios;
            return true;
          } else {
            console.warn('⚠️ No se encontraron ejercicios en la respuesta de detalles');
          }
        } catch (detailsError) {
          console.error('❌ Error al obtener ejercicios mediante detalles:', detailsError);
        }

        // Intentar obtener del historial si estamos en modo historial
        const historialId = localStorage.getItem('view_historial_id');
        if (historialId) {
          try {
            console.log(`🔍 Intentando cargar desde historial ID: ${historialId}`);
            const historialResponse = await evaluationsService.getEvaluacionHistorial(historialId);

            if (historialResponse.data && historialResponse.data.success &&
              historialResponse.data.evaluacion &&
              historialResponse.data.evaluacion.ejercicios &&
              historialResponse.data.evaluacion.ejercicios.length > 0) {

              console.log(`✅ Obtenidos ${historialResponse.data.evaluacion.ejercicios.length} ejercicios desde historial`);
              exercises.value = historialResponse.data.evaluacion.ejercicios;
              return true;
            } else {
              console.warn('⚠️ No se encontraron ejercicios en la respuesta del historial');
            }
          } catch (historialError) {
            console.error('❌ Error al obtener ejercicios desde historial:', historialError);
          }
        }

        // Intentar reconstruir ejercicios desde respuestas almacenadas localmente
        console.log('🔄 Intentando reconstruir ejercicios desde respuestas almacenadas...');
        const userId = localStorage.getItem('user_id') || 'anonymous';
        const rawResultsKey = `evaluation_raw_results_${userId}`;
        const rawResultsData = localStorage.getItem(rawResultsKey);

        if (rawResultsData) {
          try {
            const rawResults = JSON.parse(rawResultsData);

            if (rawResults.resultados && Array.isArray(rawResults.resultados)) {
              const ejerciciosReconstruidos = rawResults.resultados.map(resultado => ({
                id: resultado.ejercicio_id,
                titulo: `Ejercicio ${resultado.ejercicio_id}`,
                descripcion: 'No hay descripción disponible',
                puntaje: resultado.puntaje_maximo || 10,
                puntaje_obtenido: resultado.puntaje_obtenido || 0,
                es_correcta: resultado.es_correcto || false,
                contenido: {}
              }));

              if (ejerciciosReconstruidos.length > 0) {
                console.log(`✅ Reconstruidos ${ejerciciosReconstruidos.length} ejercicios desde resultados`);
                exercises.value = ejerciciosReconstruidos;
                return true;
              }
            }
          } catch (e) {
            console.error('❌ Error al reconstruir ejercicios desde resultados:', e);
          }
        }

        // Si llegamos aquí, no pudimos obtener los ejercicios de ninguna fuente
        console.error('⛔ No se pudieron obtener ejercicios de ninguna fuente');
        return false;
      } catch (e) {
        console.error('❌ Error general en loadExerciseDetails:', e);
        return false;
      }
    };

    // Contar ejercicios completados
    const getCompletedExercisesCount = () => {
      // Si la evaluación tiene un valor predefinido, usarlo
      if (evaluation.value?.completados_count !== undefined) {
        return evaluation.value.completados_count;
      }
      
      // Si tenemos ejercicios, contar los que están correctos
      if (exercises.value && exercises.value.length > 0) {
        return exercises.value.filter(e => e.es_correcta === true).length;
      }
      
      return 0;
    };

    // Calcular precisión en los ejercicios intentados
    const calculateAccuracy = () => {
      // Si no hay ejercicios, la precisión es 0
      if (!exercises.value || exercises.value.length === 0) return 0;

      // Contar ejercicios correctos
      const totalCorrect = exercises.value.filter(e => e.es_correcta === true).length;
      const totalAttempted = exercises.value.length;
      
      // Calcular y formatear porcentaje
      const percentage = (totalCorrect / totalAttempted) * 100;
      return Math.round(percentage);
    };

    // Calcular el porcentaje de puntuación
    const calculatePercentage = () => {
      if (maxScore.value <= 0) return 0;
      return Math.round((totalScore.value / maxScore.value) * 100);
    };

    // Obtener clase de color para el trofeo de puntuación
    const getScoreColorClass = () => {
      // Si evaluation.value no existe o no tiene color_clase, calcular basado en scaledScore
      if (!evaluation.value || !evaluation.value.color_clase) {
        const score = scaledScore.value;
        if (score >= 9) return 'excellent';
        if (score >= 7) return 'good';
        if (score >= 5) return 'average';
        return 'poor';
      }
      return evaluation.value.color_clase;
    };

    // Formatear el tiempo de finalización
    const formatCompletionTime = () => {
      const minutes = Math.floor(completionTime.value / 60000);
      const seconds = Math.floor((completionTime.value % 60000) / 1000);

      if (minutes === 0) {
        return `${seconds} seg`;
      }

      return `${minutes}m ${seconds}s`;
    };

    // Volver a la página de acceso a evaluación
    const returnToEvaluationAccess = () => {
      const userId = getCurrentUserId();
      
      // Limpiar datos de la evaluación actual antes de volver
      localStorage.removeItem(`evaluationStartTime_${userId}`);
      localStorage.removeItem(`evaluationEndTime_${userId}`);
      localStorage.removeItem('currentEvaluation');

      // No eliminamos las puntuaciones para mantener historial
      router.push('/evaluation-access');
    };


    // Función para cargar lenguajes de Judge0
    const loadJudge0Languages = async () => {
      if (languagesLoaded.value) return;

      try {
        console.log("🔧 Cargando lenguajes de Judge0...");
        const judge0Url = import.meta.env.VITE_JUDGE0_API_URL;
        if (!judge0Url) {
          console.error("URL de Judge0 no configurada");
          return;
        }

        const apiUrl = judge0Url.endsWith('/') ? `${judge0Url}languages` : `${judge0Url}/languages`;
        const response = await fetch(apiUrl);

        if (!response.ok) {
          console.error("Error al cargar lenguajes:", response.status, response.statusText);
          return;
        }

        const languages = await response.json();
        if (!Array.isArray(languages)) {
          console.error("Respuesta inesperada:", languages);
          return;
        }

        availableLanguages.value = languages;
        languagesLoaded.value = true;
        console.log(`✅ Cargados ${languages.length} lenguajes de Judge0`);
      } catch (error) {
        console.error('Error al cargar lenguajes de Judge0:', error);
      }
    };

    // Función para obtener el language_id del ejercicio
    const getLanguageIdForExercise = (exercise) => {
      // Obtener el ejercicio_id
      const exerciseId = exercise.ejercicio_id || exercise.id;

      // Intentar obtener desde localStorage con múltiples claves
      const userId = getCurrentUserId();
      const evaluationId = evaluation.value?.id || localStorage.getItem('completedEvaluationId') || 'unknown';

      const languageKeys = [
        `exercise_language_${userId}_${evaluationId}_${exerciseId}`,
        `exercise_language_${userId}_unknown_${exerciseId}`,
        `exercise_language_${userId}_${exerciseId}`
      ];

      for (const key of languageKeys) {
        const savedLanguage = localStorage.getItem(key);
        if (savedLanguage) {
          return parseInt(savedLanguage);
        }
      }

      // Si no se encuentra en localStorage, intentar detectar desde el código
      if (exercise.codigo) {
        return detectLanguageFromCode(exercise.codigo);
      }

      return 71; // Python por defecto
    };

    // Función para detectar lenguaje desde el código
    const detectLanguageFromCode = (codigo) => {
      if (!codigo) return 71;

      // JavaScript
      if (codigo.includes('console.log') || codigo.includes('function') ||
        codigo.includes('let ') || codigo.includes('const ') ||
        codigo.includes('var ') || codigo.includes('=>')) {
        return 63;
      }
      // Java
      else if (codigo.includes('public class') || codigo.includes('System.out.print') ||
        codigo.includes('public static void main')) {
        return 62;
      }
      // C++
      else if (codigo.includes('#include') && (codigo.includes('std::') ||
        codigo.includes('cout') || codigo.includes('cin'))) {
        return 54;
      }
      // C
      else if (codigo.includes('#include') && (codigo.includes('printf') ||
        codigo.includes('scanf') || codigo.includes('main()'))) {
        return 50;
      }
      // Python
      else if (codigo.includes('print(') || codigo.includes('def ') ||
        codigo.includes('import ') || codigo.includes('range(')) {
        return 71;
      }

      return 71; // Por defecto Python
    };

    // Función principal para obtener el nombre del lenguaje para un ejercicio
    const getLanguageNameForExercise = (exercise) => {
      const languageId = getLanguageIdForExercise(exercise);

      // Buscar en lenguajes cargados
      if (availableLanguages.value.length > 0) {
        const language = availableLanguages.value.find(lang => lang.id === languageId);
        if (language) {
          return language.name;
        }
      }

      // Fallback con nombres conocidos
      const languageNames = {
        71: 'Python (3.8.1)',
        70: 'Python (2.7.17)',
        63: 'JavaScript (Node.js 12.14.0)',
        62: 'Java (OpenJDK 13.0.1)',
        54: 'C++ (GCC 9.2.0)',
        53: 'C++ (GCC 8.3.0)',
        52: 'C++ (GCC 7.4.0)',
        50: 'C (GCC 9.2.0)',
        49: 'C (GCC 8.3.0)',
        48: 'C (GCC 7.4.0)',
        74: 'TypeScript (3.7.4)',
        73: 'Rust (1.40.0)',
        60: 'Go (1.13.5)',
        68: 'PHP (7.4.1)'
      };

      return languageNames[languageId] || `Lenguaje ID ${languageId}`;
    };



    onMounted(async () => {
      console.log('🔍 EvaluationCompleted montado');
      console.log('Evaluation ID:', evaluationId.value);
      console.log('Usuario:', currentUserId.value);

      // Esperar un momento para asegurar que localStorage esté actualizado
      await new Promise(resolve => setTimeout(resolve, 10000));

      // Verificar si llegamos con error
      const queryError = route.query.error;
      if (queryError === 'true') {
        console.warn('⚠️ Se detectó un parámetro de error en la URL');
        error.value = "Hubo un problema al procesar la evaluación. Los resultados pueden estar incompletos.";
      }

      // Inicializar carga con tiempo extendido
      loadingState.value = {
        isLoading: true,
        message: "Cargando resultados de evaluación...",
        attempt: 0
      };

      // Espera a que los datos estén completos
      await esperarDatosCompletos();

      // Aumenta el tiempo de espera inicial para la carga
      setTimeout(async () => {
        try {
          // Intentar cargar varias veces con retardo
          for (let attempt = 1; attempt <= 5; attempt++) {
            try {
              loadingState.value.attempt = attempt;
              loadingState.value.message = `Cargando resultados de evaluación... (Intento ${attempt}/5)`;
              
              await loadEvaluationData();
              
              // Si tiene éxito, salir del bucle
              break;
            } catch (attemptError) {
              console.warn(`Intento ${attempt} fallido:`, attemptError);
              // Esperar antes de reintentar
              await new Promise(resolve => setTimeout(resolve, 2000));
            }
          }

          // PASO ADICIONAL -> Verificar que los ejercicios tengan su código
          // Esto es crítico para mostrar correctamente los ejercicios
          if (exercises.value.length === 0) {
            console.log('Intentando cargar ejercicios desde localStorage...');
            loadExercisesFromLocalStorage();
          }
          
          // Intentar complementar con detalles de ejercicios si es necesario
          if (exercises.value.length === 0 || !exercises.value[0].codigo) {
            console.log('Intentando cargar detalles de ejercicios...');
            await loadExerciseDetails();
          }

          // Verificar si tenemos respuestas pero sin código
          const ejerciciosSinCodigo = exercises.value.filter(ej => !ej.codigo || ej.codigo.trim() === '');
          if (ejerciciosSinCodigo.length > 0) {
            console.log(`Encontrados ${ejerciciosSinCodigo.length} ejercicios sin código. Recuperando...`);
            
            // Ejecutar función para recuperar códigos
            await performFinalChecks();
          }

          // Imprimir diagnóstico final
          if (exercises.value.length === 0) {
            console.warn('No se pudo obtener información de ejercicios');
          } else {
            console.log(`Cargados ${exercises.value.length} ejercicios`);
            console.log(`Ejercicios completados: ${getCompletedExercisesCount()}/${exercises.value.length}`);
            console.log(`Precisión: ${calculateAccuracy()}%`);
            
            // Diagnóstico detallado de cada ejercicio
            exercises.value.forEach((ejercicio, index) => {
              console.log(`Ejercicio #${index+1}:`);
              console.log(`- ID: ${ejercicio.ejercicio_id || ejercicio.id}`);
              console.log(`- Título: ${ejercicio.titulo || ejercicio.ejercicio_titulo}`);
              console.log(`- Código: ${ejercicio.codigo ? ejercicio.codigo.length + ' caracteres' : 'No disponible'}`);
              console.log(`- Es correcto: ${ejercicio.es_correcta}`);
              console.log(`- Puntaje: ${ejercicio.puntaje_obtenido}/${ejercicio.puntaje_maximo}`);
            });
          }

          // Verificación final y mostrar la interfaz
          await performFinalChecks();
          // Carga los lenguajes de jude0
          await loadJudge0Languages();
          
          // Mantener la pantalla de carga un poco más
          setTimeout(() => {
            loadingState.value.isLoading = false;
          }, 3000);
        } catch (err) {
          console.error('Error iniciando carga:', err);
          error.value = 'Error al iniciar carga de datos: ' + err.message;
          loadingState.value.isLoading = false;
        }
      }, 5000); // Esperar antes de iniciar carga
    });

    return {
      // Variables reactivas
      exercises,
      loadingExercises,
      totalScore,
      maxScore,
      scaledScore,
      completionTime,
      evaluationId,
      currentUserId,
      error,
      evaluation,

      // Estados
      loadingState,

      // Métodos
      returnToEvaluationAccess,
      retryLoading,

      // Otras funciones útiles
      getUserName,
      getEvaluationName,
      getTeacherName,
      getEvaluationDate,
      getCompletedExercisesCount,
      calculateAccuracy,
      getScoreColorClass,
      formatCompletionTime,
      getLanguageName,
      getLanguageNameForExercise,
      loadJudge0Languages,
      availableLanguages
    };
  }
}
</script>

<style scoped>
/* =================== CONTENEDOR PRINCIPAL =================== */
.evaluation-completed {
  min-height: 100vh;
  background-color: var(--color-bg-main);
  display: flex;
  justify-content: center;
  align-items: center;
  padding: 2rem 1rem;
  font-family: Arial, Helvetica, sans-serif;
  background-image: linear-gradient(to bottom, var(--color-bg-main), var(--color-bg-main));
}

/* =================== PAPEL DEL CERTIFICADO =================== */
.certificate-paper {
  background-color: var(--color-bg-element-active);
  border-radius: var(--border-radius-xl);
  max-width: 850px;
  width: 100%;
  padding: 2rem;
  position: relative;
  margin: 0 auto;
  box-shadow: var(--shadow-xl), 0 0 0 1px rgba(255, 255, 255, 0.05), inset 0 0 20px rgba(0, 0, 0, 0.2);
  background-image: repeating-linear-gradient(-45deg, rgba(255, 255, 255, 0.02), rgba(255, 255, 255, 0.02) 1px, transparent 1px, transparent 6px);
  overflow: hidden;
  animation: fadeIn 0.8s ease;
}

.certificate-paper::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  border: 1px solid rgba(255, 255, 255, 0.08);
  border-radius: var(--border-radius-xl);
  pointer-events: none;
}

/* =================== HEADER CONTAINER =================== */
.header-container {
  display: flex;
  justify-content: space-between;
  margin-bottom: 2rem;
  align-items: flex-start;
}

/* =================== CONTENEDOR DE PUNTAJE =================== */
.score-container {
  flex-shrink: 0;
}

.score-card {
  width: 185px;
  height: 214px;
  background-color: white;
  border-radius: var(--border-radius-xl);
  overflow: hidden;
  display: flex;
  flex-direction: column;
  border: 4px solid;
  box-shadow: var(--shadow-xl);
  transition: transform var(--transition-smooth);
}

.score-card:hover {
  transform: translateY(-5px);
}

.score-card.excellent {
  border-color: var(--color-score-excellent);
}

.score-card.good {
  border-color: var(--color-score-good);
}

.score-card.average {
  border-color: var(--color-score-average);
}

.score-card.poor {
  border-color: var(--color-score-poor);
}

.score-label {
  padding: 10px;
  text-align: center;
  font-weight: bold;
  font-size: 1.1rem;
  color: #333;
  background-color: #f8f8f8;
}

.score-divider {
  height: 2px;
  background-color: #DDD;
}

.trophy-container {
  flex-grow: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  text-align: center;
  padding: 15px;
  position: relative;
  background-color: white;
}

.score-value {
  font-size: 2.5rem;
  font-weight: bold;
  color: #222;
  margin-bottom: 12px;
  text-shadow: var(--shadow-sm);
}

.trophy-icon {
  font-size: 3rem;
}

.trophy-icon.excellent {
  color: var(--color-score-excellent);
}

.trophy-icon.good {
  color: var(--color-score-good);
}

.trophy-icon.average {
  color: var(--color-score-average);
}

.trophy-icon.poor {
  color: var(--color-score-poor);
}

/* =================== INFORMACIÓN DEL ESTUDIANTE =================== */
.student-info {
  text-align: right;
  background-color: rgba(255, 255, 255, 0.03);
  padding: 1.2rem;
  border-radius: var(--border-radius-lg);
  border-left: 4px solid var(--color-accent-blue);
  box-shadow: var(--shadow);
}

.student-name {
  font-size: 1.6rem;
  font-weight: bold;
  color: var(--color-text-primary);
  margin-bottom: 0.5rem;
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
  padding-bottom: 0.5rem;
}

.teacher-name {
  font-size: 1.1rem;
  color: var(--color-text-primary);
  margin-bottom: 0.5rem;
}

.evaluation-date {
  font-size: 0.9rem;
  color: var(--color-text-secondary);
  font-style: italic;
}

/* =================== BANNER DEL TÍTULO =================== */
.title-banner {
  text-align: center;
  margin-bottom: 2.5rem;
  position: relative;
  background-color: #13100a36;
  padding: 1.5rem 1rem;
  border-radius: var(--border-radius-lg);
  border-left: 4px solid var(--color-accent-purple);
  border-right: 4px solid var(--color-accent-purple);
  border: 2px solid #ffffff2c;
}

.title-banner h1 {
  font-size: 1.8rem;
  font-weight: bold;
  color: var(--color-text-primary);
  margin: 0;
  padding: 0;
  text-shadow: var(--shadow-sm);
}

.completion-badge {
  background-color: var(--color-primary);
  color: white;
  position: absolute;
  top: -10px;
  right: 20px;
  padding: 5px 15px;
  font-weight: bold;
  border-radius: 20px;
  font-size: 0.8rem;
  transform: rotate(3deg);
  box-shadow: var(--shadow-lg);
}

/* =================== GRID DE ESTADÍSTICAS =================== */
.stats-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 1rem;
  margin-bottom: 2.5rem;
}

.stat-box {
  background-color: var(--color-bg-element-alt);
  border-radius: var(--border-radius-lg);
  border: 1px solid var(--color-border);
  padding: 1.2rem 1rem;
  text-align: center;
  transition: transform var(--transition-smooth), box-shadow var(--transition-smooth);
  box-shadow: var(--shadow);
  animation: fadeIn 1s ease forwards;
  opacity: 0;
}

.stat-box:nth-child(1) {
  border-top: 3px solid var(--color-accent-cyan);
  animation-delay: 0.1s;
}

.stat-box:nth-child(2) {
  border-top: 3px solid var(--color-teal);
  animation-delay: 0.2s;
}

.stat-box:nth-child(3) {
  border-top: 3px solid var(--color-accent-purple);
  animation-delay: 0.3s;
}

.stat-box:nth-child(4) {
  border-top: 3px solid var(--color-accent-blue);
  animation-delay: 0.4s;
}

.stat-box:hover {
  transform: translateY(-8px);
  box-shadow: var(--shadow-xl);
}

.stat-icon {
  font-size: 2rem;
  margin-bottom: 0.8rem;
}

.stat-box:nth-child(1) .stat-icon {
  color: var(--color-accent-cyan);
}

.stat-box:nth-child(2) .stat-icon {
  color: var(--color-teal);
}

.stat-box:nth-child(3) .stat-icon {
  color: var(--color-accent-purple);
}

.stat-box:nth-child(4) .stat-icon {
  color: var(--color-accent-blue);
}

.stat-value {
  font-size: 1.4rem;
  font-weight: bold;
  color: var(--color-text-primary);
  margin-bottom: 0.4rem;
}

.stat-label {
  font-size: 0.9rem;
  color: var(--color-text-secondary);
  text-transform: uppercase;
  letter-spacing: 1px;
}

/* =================== SECCIÓN DE EJERCICIOS =================== */
.exercises-section {
  margin-bottom: 2.5rem;
  background-color: rgba(0, 0, 0, 0.1);
  padding: 1.8rem;
  border-radius: var(--border-radius-xl);
  box-shadow: inset 0 0 15px rgba(0, 0, 0, 0.1);
}

.section-title {
  font-size: 1.5rem;
  font-weight: bold;
  color: var(--color-text-primary);
  margin-bottom: 1.5rem;
  display: flex;
  align-items: center;
  border-bottom: 1px solid var(--color-border);
  padding-bottom: 0.7rem;
}

.section-icon {
  margin-right: 0.75rem;
  color: var(--color-teal);
}

.exercises-list {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

/* =================== ITEMS DE EJERCICIO =================== */
.exercise-item {
  background-color: var(--color-bg-element-alt);
  border-radius: var(--border-radius-lg);
  overflow: hidden;
  border: 1px solid var(--color-border);
  transition: transform var(--transition-smooth);
  box-shadow: var(--shadow);
}

.exercise-item:hover {
  transform: translateY(-5px);
  box-shadow: var(--shadow-xl);
}

.exercise-item.completed {
  border-left: 5px solid var(--color-status-completed);
}

.exercise-item.incorrect {
  border-left: 5px solid var(--color-score-poor);
}

.exercise-header {
  display: flex;
  align-items: center;
  background-color: rgba(0, 0, 0, 0.2);
  padding: 1rem;
  border-bottom: 1px solid var(--color-border);
}

.exercise-status {
  margin-right: 1rem;
  display: flex;
  align-items: center;
  justify-content: center;
  width: 30px;
  height: 30px;
  border-radius: 50%;
  background-color: rgba(0, 0, 0, 0.3);
  flex-shrink: 0;
}

.completed .exercise-status {
  background-color: rgba(76, 175, 80, 0.2);
}

.incorrect .exercise-status {
  background-color: rgba(244, 67, 54, 0.2);
}

.status-icon {
  font-size: 1.1rem;
}

.completed .status-icon {
  color: var(--color-status-completed);
}

.incorrect .status-icon {
  color: var(--color-score-poor);
}

.exercise-title {
  font-weight: bold;
  font-size: 1.1rem;
  color: var(--color-text-primary);
}

/* =================== BARRA DE PROGRESO =================== */
.exercise-progress {
  height: 5px;
  background-color: rgba(244, 67, 54, 0.2);
  margin-top: -1px;
}

.progress-bar {
  height: 100%;
  transition: width 0.5s ease;
  width: 0;
}

.progress-bar.success {
  width: 100%;
  background: linear-gradient(90deg, #2E7D32, var(--color-score-excellent));
}

.progress-bar.failure {
  width: 100%;
  background: linear-gradient(90deg, #B71C1C, var(--color-score-poor));
}

/* =================== CÓDIGO Y OUTPUT =================== */
.exercise-code {
  padding: 1rem;
  background-color: var(--color-editor-bg);
  border-radius: 0 0 var(--border-radius-lg) var(--border-radius-lg);
}

.code-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 0.5rem;
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
  padding-bottom: 0.5rem;
}

.code-label {
  font-weight: bold;
  color: var(--color-text-secondary);
  font-size: 0.9rem;
}

.code-language {
  background-color: var(--color-bg-element-hover);
  padding: 2px 6px;
  border-radius: var(--border-radius-sm);
  font-size: 0.8rem;
  color: var(--color-secondary);
}

.code-block {
  background-color: var(--color-editor-bg);
  color: var(--color-text-secondary);
  padding: 1rem;
  border-radius: var(--border-radius-sm);
  overflow-x: auto;
  font-family: 'Fira Code', monospace;
  font-size: 0.9rem;
  line-height: 1.5;
  margin: 0 0 0.5rem 0;
  max-height: 200px;
  overflow-y: auto;
}

.code-output {
  margin-top: 1rem;
  border-top: 1px dashed rgba(255, 255, 255, 0.1);
  padding-top: 0.5rem;
}

.output-header {
  font-weight: bold;
  font-size: 0.9rem;
  color: var(--color-text-secondary);
  margin-bottom: 0.5rem;
}

.output-content {
  background-color: var(--color-bg-darker);
  padding: 0.8rem;
  border-radius: var(--border-radius-sm);
  color: var(--color-success);
  font-family: 'Fira Code', monospace;
  font-size: 0.85rem;
  white-space: pre-wrap;
  max-height: 150px;
  overflow-y: auto;
  margin: 0;
}

/* =================== ESTADOS DE CARGA =================== */
.loading-container,
.empty-container {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  min-height: 200px;
  color: var(--color-text-secondary);
}

.loader {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  border: 3px solid rgba(255, 255, 255, 0.1);
  border-top-color: var(--color-accent-purple);
  animation: spin 1s infinite linear;
  margin-bottom: 1rem;
}

.empty-icon {
  font-size: 3rem;
  margin-bottom: 1rem;
  opacity: 0.6;
}

/* =================== OVERLAYS =================== */
.loading-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-color: rgba(28, 28, 33, 0.9);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 9999;
  backdrop-filter: blur(5px);
}

.loading-container {
  background-color: var(--color-bg-element);
  border-radius: var(--border-radius-lg);
  padding: 2rem;
  text-align: center;
  max-width: 400px;
  width: 90%;
  box-shadow: var(--shadow-xl);
  border: 1px solid var(--color-border);
  animation: fadeIn var(--transition-smooth) ease-out;
}

.loading-container h3 {
  margin: 1rem 0;
  color: var(--color-text-primary);
  font-size: 1.2rem;
}

.loading-container p {
  color: var(--color-text-secondary);
  margin-top: 1rem;
  font-size: 0.9rem;
  opacity: 0.8;
}

.loading-spinner {
  width: 50px;
  height: 50px;
  margin: 0 auto;
  border: 4px solid rgba(255, 255, 255, 0.1);
  border-radius: 50%;
  border-top-color: var(--color-primary);
  animation: spin 1s linear infinite;
}

.error-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-color: rgba(28, 28, 33, 0.9);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 9999;
}

.error-container {
  background-color: var(--color-bg-element);
  border-radius: var(--border-radius-lg);
  padding: 2rem;
  text-align: center;
  max-width: 500px;
  width: 90%;
  box-shadow: var(--shadow-xl);
  border: 1px solid var(--color-error);
  animation: fadeIn var(--transition-smooth) ease-out;
}

.error-icon {
  font-size: 3rem;
  margin-bottom: 1rem;
  color: var(--color-error);
}

.error-container h3 {
  margin: 0.5rem 0;
  color: var(--color-text-primary);
  font-size: 1.4rem;
}

.error-container p {
  color: var(--color-text-secondary);
  margin: 1rem 0;
  line-height: 1.5;
}

/* =================== BOTONES =================== */
.action-button-container {
  display: flex;
  justify-content: center;
  margin-top: 2.5rem;
}

.action-button {
  background: linear-gradient(135deg, var(--color-accent-blue), var(--color-secondary));
  color: white;
  border: none;
  border-radius: var(--border-radius-lg);
  padding: 0.85rem 2.2rem;
  font-size: 1.1rem;
  font-weight: bold;
  cursor: pointer;
  transition: all var(--transition-smooth);
  display: flex;
  align-items: center;
  justify-content: center;
  box-shadow: var(--shadow-lg);
}

.action-button:hover {
  background: linear-gradient(135deg, #303F9F, var(--color-accent-blue));
  transform: translateY(-5px);
  box-shadow: var(--shadow-xl);
}

.button-icon {
  margin-right: 0.9rem;
  font-size: 1.3rem;
}

.retry-button, .return-button {
  padding: 0.8rem 1.5rem;
  border-radius: var(--border-radius);
  border: none;
  font-weight: bold;
  margin: 0.5rem;
  cursor: pointer;
  transition: all var(--transition-smooth);
}

.retry-button {
  background-color: var(--color-primary);
  color: var(--color-bg-main);
}

.retry-button:hover {
  background-color: var(--color-primary-light);
  transform: translateY(-2px);
}

.return-button {
  background-color: rgba(255, 255, 255, 0.1);
  color: var(--color-text-primary);
  border: 1px solid var(--color-border);
}

.return-button:hover {
  background-color: rgba(255, 255, 255, 0.15);
  transform: translateY(-2px);
}

/* =================== FOOTER DEL CERTIFICADO =================== */
.certificate-footer {
  margin-top: 3rem;
  text-align: center;
  position: relative;
}

.certificate-stamp {
  display: inline-block;
  font-family: 'Brush Script MT', cursive;
  font-size: 2rem;
  color: var(--color-text-primary);
  transform: rotate(-5deg);
  position: relative;
  padding: 0.5rem 2rem;
  width: 100%;
}

.certificate-stamp span {
  display: inline-block;
}

.certificate-stamp::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  border: 2px dashed var(--color-text-primary);
  border-radius: 50%;
}

.logo-container {
  position: absolute;
  top: -12px;
  right: -2px;
  width: 50px;
  height: 50px;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 5px;
}

.certificate-logo {
  width: 100%;
  height: 100%;
  object-fit: contain;
  border-radius: 50%;
}

/* =================== ANIMACIONES =================== */
@keyframes fadeIn {
  from { opacity: 0; }
  to { opacity: 1; }
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

/* =================== MEDIA QUERIES =================== */
@media (max-width: 768px) {
  .certificate-paper {
    padding: 1.5rem 1rem;
  }

  .header-container {
    flex-direction: column;
    align-items: center;
    text-align: center;
    gap: 1.5rem;
  }

  .student-info {
    text-align: center;
    width: 100%;
  }

  .stats-grid {
    grid-template-columns: 1fr 1fr;
    gap: 0.75rem;
  }

  .title-banner h1 {
    font-size: 1.5rem;
  }

  .completion-badge {
    position: static;
    display: inline-block;
    margin-top: 0.75rem;
    transform: none;
  }
}

@media (max-width: 480px) {
  .stats-grid {
    grid-template-columns: 1fr;
  }

  .score-card {
    width: 140px;
    height: 140px;
  }

  .score-value {
    font-size: 2rem;
  }

  .trophy-icon {
    font-size: 2.5rem;
  }
}
</style>