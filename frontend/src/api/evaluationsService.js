// api/evaluationsService.js 
import apiClient from "../api/axios";
import { v4 as uuidv4 } from "uuid"; // Para generar IDs únicos de tracking

// Configuración de Judge0
const JUDGE0_API_URL = import.meta.env.VITE_JUDGE0_API_URL;
const JUDGE0_TIMEOUT = parseInt(import.meta.env.VITE_JUDGE0_TIMEOUT || "60000");

// Servicio para gestionar evaluaciones
const evaluationsService = {

  // ---------- MÉTODOS PARA GESTIÓN DE EVALUACIONES ----------
  async getEvaluaciones() {
    try {
      const userId = localStorage.getItem("user_id");
      console.log(`Obteniendo evaluaciones para usuario ID: ${userId}`);

      const response = await apiClient.get("/evaluaciones/", {
        params: { autor_id: userId },
      });
      return response;
    } catch (error) {
      console.error("Error al obtener evaluaciones:", error);
      throw error;
    }
  },

  getHistorialEvaluaciones(studentId = null) {
    const params = studentId ? { estudiante_id: studentId } : {};
    console.log("📊 Solicitando historial con parámetros:", params);

    return apiClient
      .get("/historial-evaluaciones/", { params })
      .then((response) => {
        // Debug logs
        console.log("📊 Historial evaluaciones respuesta cruda:", response);

        // Verificar y corregir la estructura de la respuesta
        if (response.data) {
          // Si no tiene la estructura esperada, adaptarla
          if (!response.data.hasOwnProperty("success")) {
            console.log("📊 Adaptando formato de respuesta");
            response.data = {
              success: true,
              historial: Array.isArray(response.data)
                ? response.data
                : response.data.historial || [],
            };
          }

          // Procesar el historial para asegurar que tenga valores válidos
          if (response.data.historial) {
            response.data.historial = response.data.historial.map((item) => {
              // Asegurar que puntaje_sobre_10 esté definido y sea un número
              if (item.puntaje_sobre_10 === undefined) {
                if (
                  item.puntaje_total !== undefined &&
                  item.evaluacion_puntaje_total &&
                  item.evaluacion_puntaje_total > 0
                ) {
                  item.puntaje_sobre_10 = (item.puntaje_total / item.evaluacion_puntaje_total) * 10;
                } else {
                  item.puntaje_sobre_10 = 0;
                }
              } else {
                // Asegurar que sea un número
                item.puntaje_sobre_10 = parseFloat(item.puntaje_sobre_10) || 0;
              }

              // Asegurar que respuestas sea un array
              if (!Array.isArray(item.respuestas)) {
                // Intentar extraer respuestas del objeto detalles
                if (item.detalles && Array.isArray(item.detalles.respuestas)) {
                  item.respuestas = item.detalles.respuestas;
                } else {
                  item.respuestas = [];
                }
              }

              return item;
            });
          }
        }

        console.log("📊 Historial evaluaciones respuesta procesada:", response.data);
        return response;
      })
      .catch((error) => {
        console.error("❌ Error al obtener historial de evaluaciones:", error);

        // Devolver un formato consistente incluso en caso de error
        return {
          data: {
            success: false,
            message: error.message || "Error al obtener historial de evaluaciones",
            historial: [],
          },
        };
      });
  },

  getEvaluacionHistorial(historialId, studentId = null) {
    const params = studentId ? { estudiante_id: studentId } : {};
    console.log(`📚 Solicitando evaluación historial ID:${historialId}`, params);

    return apiClient
      .get(`/historial/${historialId}/`, { params })
      .then((response) => {
        console.log("📚 Evaluación historial respuesta:", response.data);

        // Procesar respuesta para asegurar consistencia
        if (response.data && response.data.evaluacion) {
          // Procesar cada ejercicio de la evaluación
          if (Array.isArray(response.data.evaluacion.ejercicios)) {
            response.data.evaluacion.ejercicios = response.data.evaluacion.ejercicios.map(
              (ejercicio) => {
                // Asegurar que los campos críticos existan
                if (!ejercicio.puntaje_obtenido && ejercicio.puntaje_obtenido !== 0) {
                  ejercicio.puntaje_obtenido = 0;
                }

                if (!ejercicio.puntaje) {
                  ejercicio.puntaje = ejercicio.puntaje_maximo || 10;
                }

                return ejercicio;
              }
            );
          }
        }

        return response;
      })
      .catch((error) => {
        console.error("❌ Error al obtener evaluación del historial:", error);
        throw error;
      });
  },

  async crearEvaluacion(datos) {
    try {
      console.log("Creando evaluación con datos:", datos);

      // Crear una copia de los datos para no modificar el objeto original
      const datosFormateados = { ...datos };

      // Mapeo de valores del formulario a IDs de curso reales
      const cursoMapping = {
        8: 5, // 8vo de Básica -> ID 5
        9: 6, // 9no de Básica -> ID 6
        10: 7, // 10mo de Básica -> ID 7
        1: 8, // 1ro de Bachillerato -> ID 8
        2: 9, // 2do de Bachillerato -> ID 9
        3: 10, // 3ro de Bachillerato -> ID 10
      };

      // Transformar el valor del curso al ID correcto en la base de datos
      if (datosFormateados.curso !== undefined) {
        const cursoKey = datosFormateados.curso.toString();
        if (cursoMapping[cursoKey] !== undefined) {
          datosFormateados.curso = cursoMapping[cursoKey];
          console.log(`Curso convertido: ${cursoKey} -> ${datosFormateados.curso}`);
        } else {
          console.log(`Usando curso sin convertir: ${datosFormateados.curso}`);
        }
      }

      console.log("Datos formateados para enviar:", JSON.stringify(datosFormateados));

      const response = await apiClient.post("/evaluaciones/", datosFormateados);
      console.log("Evaluación creada exitosamente:", response.data);
      return response;
    } catch (error) {
      console.error("Error al crear evaluación:", error);

      // Mostrar detalle completo del error
      if (error.response && error.response.data) {
        console.error("Detalle del error:", JSON.stringify(error.response.data));
      }

      throw error;
    }
  },

  async getCursos() {
    try {
      const response = await apiClient.get("/cursos/");
      return response;
    } catch (error) {
      console.error("Error al obtener cursos:", error);
      throw error;
    }
  },

  async actualizarEvaluacion(id, datos) {
    try {
      console.log(`Actualizando evaluación ${id} con:`, datos);
      const response = await apiClient.put(`/evaluaciones/${id}/`, datos);
      return response;
    } catch (error) {
      console.error(`Error al actualizar evaluación ${id}:`, error);
      throw error;
    }
  },

  async eliminarEvaluacion(id) {
    try {
      const response = await apiClient.delete(`/evaluaciones/${id}/`);
      return response;
    } catch (error) {
      console.error(`Error al eliminar evaluación ${id}:`, error);
      throw error;
    }
  },

  // ---------- MÉTODOS PARA ACCESO A EVALUACIONES ----------
  async validarCodigoAcceso(codigo) {
    try {
      console.log(`Validando código de acceso: ${codigo}`);
      const response = await apiClient.post("/evaluaciones/validar_codigo/", {
        codigo: codigo,
      });
      return response;
    } catch (error) {
      console.error("Error al validar código de acceso:", error);
      throw error;
    }
  },

  async inscribirEstudiante(evaluacionId, datos) {
    try {
      console.log(`Inscribiendo estudiante en evaluación ${evaluacionId}:`, datos);
      const response = await apiClient.post(`/evaluaciones/${evaluacionId}/inscribir/`, datos);
      return response;
    } catch (error) {
      console.error(`Error al inscribir estudiante en evaluación ${evaluacionId}:`, error);
      throw error;
    }
  },

  async getDetallesEvaluacion(id) {
    try {
      console.log(`Solicitando detalles de evaluación ID: ${id}`);
      const cacheKey = `eval_details_${id}`;

      try {
        const cachedData = localStorage.getItem(cacheKey);
        if (cachedData) {
          const { data, timestamp } = JSON.parse(cachedData);
          const cacheAge = Date.now() - timestamp;
          if (cacheAge < 120000) {
            console.log("Usando detalles de evaluación desde caché local");
            return { data };
          }
        }
      } catch (cacheError) {
        console.warn("Error al leer caché:", cacheError);
      }

      const response = await apiClient.get(`/evaluaciones/${id}/detalles/`);
      console.log("Detalles de evaluación recibidos:", response.data);

      if (response.data) {
        localStorage.setItem(
          cacheKey,
          JSON.stringify({
            data: response.data,
            timestamp: Date.now(),
          })
        );
      }

      return response;
    } catch (error) {
      console.error("Error al obtener detalles de evaluación:", error);
      throw error;
    }
  },

  // ---------- MÉTODOS PARA EJECUCIÓN DE CÓDIGO CON JUDGE0 ----------

  /**
   * Verificar conexión con Judge0
   * @returns {Promise<{isAvailable: boolean, message: string}>}
   */
  async checkJudge0Status() {
    try {
      console.log("Verificando conexión con Judge0...");
      const response = await fetch(`${JUDGE0_API_URL}/statuses`, {
        method: "GET",
        headers: { "Content-Type": "application/json" },
        timeout: 3000,
      });

      if (response.ok) {
        console.log("✅ Judge0 disponible");
        return {
          isAvailable: true,
          message: "Judge0 está listo para trabajar 👷‍♂️",
        };
      } else {
        console.warn(`⚠️ Judge0 respondió con ${response.status}`);
        return {
          isAvailable: false,
          message: `Judge0 no responde correctamente: ${response.status}`,
        };
      }
    } catch (error) {
      console.error("❌ Error al verificar estado de Judge0:", error);
      return {
        isAvailable: false,
        message: "Judge0 está de vacaciones 🏖",
      };
    }
  },

  /**
   * Espera por un resultado de Judge0
   * @param {string} token - Token de seguimiento de Judge0
   * @returns {Promise<Object>} - Resultado de la ejecución
   */
  async waitForJudge0Result(token) {
    console.log(`⏳ Esperando resultado para token: ${token}`);
    const startTime = Date.now();
    const url = `${JUDGE0_API_URL}/submissions/${token}?fields=*&base64_encoded=false`;

    // Bucle de espera con timeout 
    while (Date.now() - startTime < JUDGE0_TIMEOUT) {
      try {
        const response = await fetch(url, {
          method: "GET",
          headers: { "Content-Type": "application/json" },
        });

        if (!response.ok) {
          console.warn(`⚠️ Error temporal: ${response.status}. Reintentando...`);
          await new Promise((resolve) => setTimeout(resolve, 1000));
          continue;
        }

        const result = await response.json();
        const status = result.status?.id;

        // Si ya está procesado (no en cola o procesando)
        if (status !== 1 && status !== 2) {
          // 1: In Queue, 2: Processing
          console.log(`✅ Resultado obtenido para token ${token}: status=${status}`);
          return result;
        }

        // Mostrar progreso
        console.log(
          `🔄 Token ${token} aún en proceso (status=${status}). Tiempo: ${Math.round(
            (Date.now() - startTime) / 1000
          )}s`
        );

        // Esperar antes del siguiente intento
        await new Promise((resolve) => setTimeout(resolve, 1000));
      } catch (error) {
        console.error(`❌ Error al obtener resultado para token ${token}:`, error);
        // Reintentar después de un error
        await new Promise((resolve) => setTimeout(resolve, 2000));
      }
    }

    throw new Error(
      `Timeout esperando resultado de Judge0 después de ${JUDGE0_TIMEOUT / 1000} segundos`
    );
  },

  /**
   * Envía un lote de ejercicios para evaluación usando Judge0
   * @param {Object} data - Datos del lote a enviar
   * @returns {Promise<Object>} - Resultado de la evaluación en lote
   */
  async submitBatch(data, allExercises = []) {
    const batchId =
      typeof uuidv4 !== "undefined"
        ? uuidv4().substring(0, 8)
        : Date.now().toString(36).substring(4);

    console.log(
      `[Batch:${batchId}] 🚀 Iniciando envío de batch con ${
        data.ejercicios?.length || 0
      } ejercicios`
    );

    try {
      // Validación de datos
      if (!data.evaluacion_id || !data.ejercicios || !Array.isArray(data.ejercicios)) {
        throw new Error("Datos incompletos para procesamiento en batch");
      }

      // PASO 1: Verificar disponibilidad de Judge0
      console.log(`[Batch:${batchId}] Verificando disponibilidad de Judge0...`);
      const judge0Status = await this.checkJudge0Status();
      if (!judge0Status.isAvailable) {
        return {
          data: {
            success: false,
            message: `Judge0 no disponible: ${judge0Status.message}`,
            resultados: [],
          },
        };
      }

      // PASO 2: Preparar todos los ejercicios para Judge0
      console.log(
        `[Batch:${batchId}] Preparando ${data.ejercicios.length} ejercicios para envío...`
      );

      // Filtrar ejercicios válidos y formatear para Judge0 
      const ejerciciosValidos = data.ejercicios.filter((ej) => ej && ej.ejercicio_id);
      console.log(`[Batch:${batchId}] Ejercicios válidos: ${ejerciciosValidos.length}`);

      // Preparar submissions con ejemplos para Judge0
      const submissionsForJudge0 = [];

      for (let i = 0; i < ejerciciosValidos.length; i++) {
        const ej = ejerciciosValidos[i];
        console.log(
          `[Batch:${batchId}] Ejercicio #${i + 1} - ID: ${ej.ejercicio_id}, Código: ${
            ej.codigo ? ej.codigo.substring(0, 50) + "..." : "(vacío)"
          }`
        );

        // Buscar el ejercicio completo para obtener los ejemplos
        const ejercicioCompleto = allExercises.find((e) => e.id === ej.ejercicio_id);

        // Preparar stdin y expected_output desde los ejemplos
        let stdin = "";
        let expected_output = "";

        if (ejercicioCompleto && ejercicioCompleto.ejemplos?.length > 0) {
          const primerEjemplo = ejercicioCompleto.ejemplos[0];
          stdin = primerEjemplo.entrada || "";
          expected_output = primerEjemplo.salida || "";
          console.log(
            `[Batch:${batchId}] Usando ejemplo de ejercicio: stdin="${stdin}", expected="${expected_output}"`
          );
        } else if (ejercicioCompleto && ejercicioCompleto.contenido) {
          const contenido =
            typeof ejercicioCompleto.contenido === "object"
              ? ejercicioCompleto.contenido
              : JSON.parse(ejercicioCompleto.contenido || "{}");

          if (contenido.ejemplos?.length > 0) {
            const primerEjemplo = contenido.ejemplos[0];
            stdin = primerEjemplo.entrada || "";
            expected_output = primerEjemplo.salida || "";
            console.log(
              `[Batch:${batchId}] Usando ejemplo de contenido: stdin="${stdin}", expected="${expected_output}"`
            );
          }
        }

        // Crear la submission para Judge0
        submissionsForJudge0.push({
          source_code: ej.codigo || "",
          language_id: 71, // Python 3
          stdin,
          expected_output,
          base64_encoded: false,
          cpu_time_limit: 5,
          cpu_extra_time: 1,
          wall_time_limit: 15,
          memory_limit: 256000,
          stack_limit: 64000,
          max_processes_and_or_threads: 60,
          enable_network: false,
        });
      }

      console.log(
        `[Batch:${batchId}] ${submissionsForJudge0.length} ejercicios preparados para Judge0`
      );

      // PASO 3: Enviar batch a Judge0 
      console.log(`[Batch:${batchId}] Enviando batch a Judge0...`);
      const judge0Response = await fetch(`${JUDGE0_API_URL}/submissions/batch`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ submissions: submissionsForJudge0 }),
      });

      if (!judge0Response.ok) {
        throw new Error(`Error al enviar batch a Judge0: ${judge0Response.status}`);
      }

      const responseJson = await judge0Response.json();
      console.log(
        `[Batch:${batchId}] Respuesta de Judge0 recibida con ${responseJson.length} elementos`
      );

      // PASO 4: Extraer tokens 
      const tokens = responseJson.filter((item) => item?.token).map((item) => item.token);

      if (!tokens.length) {
        throw new Error("No se obtuvieron tokens válidos de Judge0");
      }

      console.log(`[Batch:${batchId}] Tokens obtenidos (${tokens.length}): ${tokens.join(", ")}`);

      // PASO 5: Crear asociación de tokens con ejercicios
      const tokenToExercise = {};
      tokens.forEach((token, index) => {
        if (index < ejerciciosValidos.length) {
          tokenToExercise[token] = ejerciciosValidos[index].ejercicio_id;
          console.log(
            `[Batch:${batchId}] Asociación: Token ${token} -> Ejercicio ${ejerciciosValidos[index].ejercicio_id}`
          );
        }
      });

      // PASO 6: Esperar resultados 
      console.log(`[Batch:${batchId}] ⏳ Esperando resultados de Judge0...`);
      const startTime = Date.now();

      // Bucle de polling mientras hay submissions pendientes
      const getResults = async () => {
        const tokensParam = tokens.join(",");
        const batchUrl = `${JUDGE0_API_URL}/submissions/batch?tokens=${tokensParam}&base64_encoded=false`;

        while (Date.now() - startTime < JUDGE0_TIMEOUT) {
          try {
            console.log(
              `[Batch:${batchId}] GET ${batchUrl} - Tiempo transcurrido: ${Math.round(
                (Date.now() - startTime) / 1000
              )}s`
            );

            const batchResponse = await fetch(batchUrl, {
              method: "GET",
              headers: { "Content-Type": "application/json" },
            });

            if (!batchResponse.ok) {
              console.warn(
                `[Batch:${batchId}] Error temporal: ${batchResponse.status}. Reintentando...`
              );
              await new Promise((resolve) => setTimeout(resolve, 2000));
              continue;
            }

            const resultData = await batchResponse.json();

            if (!resultData.submissions || !Array.isArray(resultData.submissions)) {
              console.warn(`[Batch:${batchId}] Formato inesperado:`, resultData);
              await new Promise((resolve) => setTimeout(resolve, 2000));
              continue;
            }

            // Verificar si todas las submissions están procesadas
            const pending = resultData.submissions.filter(
              (s) => s.status?.id === 1 || s.status?.id === 2 // 1:In Queue, 2:Processing
            );

            console.log(
              `[Batch:${batchId}] Estado: ${resultData.submissions.length - pending.length}/${
                resultData.submissions.length
              } completados`
            );

            if (pending.length === 0) {
              // Todos los resultados están listos
              console.log(`[Batch:${batchId}] ✅ Todos los resultados recibidos!`);
              return resultData.submissions;
            }

            // Mostrar progreso detallado
            pending.forEach((p, i) => {
              console.log(
                `[Batch:${batchId}] Pendiente #${i + 1}: Token ${p.token}, Status: ${p.status?.id}`
              );
            });

            // Esperar antes del siguiente intento
            await new Promise((resolve) => setTimeout(resolve, 2000));
          } catch (error) {
            console.error(`[Batch:${batchId}] Error al obtener resultados:`, error);
            await new Promise((resolve) => setTimeout(resolve, 3000));
          }
        }

        throw new Error(`Timeout esperando resultados después de ${JUDGE0_TIMEOUT / 1000}s`);
      };

      // Esperar a que todos los tokens estén procesados
      const allResults = await getResults();
      console.log(`[Batch:${batchId}] Resultados completos recibidos: ${allResults.length}`);

      // PASO 7: Procesar resultados para nuestro formato
      const resultados = allResults
        .map((submission) => {
          const token = submission.token;
          const ejercicio_id = tokenToExercise[token];

          // Si no hay id de ejercicio asociado, saltar
          if (!ejercicio_id) {
            console.warn(`[Batch:${batchId}] Token ${token} sin ejercicio asociado`);
            return null;
          }

          const statusId = submission.status?.id;
          const isSuccess = statusId === 3; // 3 = Accepted

          // Buscar información del ejercicio en ejerciciosValidos
          const ejercicio = ejerciciosValidos.find((ej) => ej.ejercicio_id === ejercicio_id);

          // Buscar el puntaje correcto primero en allExercises (que contiene info completa)
          const ejercicioCompleto = allExercises.find((e) => e.id === ejercicio_id);
          const puntajeMaximo = ejercicioCompleto?.puntaje || ejercicio?.puntaje || 10;

          console.log(
            `[Batch:${batchId}] Resultado para ejercicio ${ejercicio_id}: status=${statusId}, success=${isSuccess}, puntaje=${puntajeMaximo}`
          );

          return {
            ejercicio_id: ejercicio_id,
            success: true, // La submission fue exitosa (aunque el resultado pueda ser incorrecto)
            es_correcto: isSuccess,
            casos_correctos: isSuccess ? 1 : 0,
            total_casos: 1,
            porcentaje: isSuccess ? 100 : 0,
            puntaje_obtenido: isSuccess ? puntajeMaximo : 0,
            puntaje_maximo: puntajeMaximo, // Ahora con el valor real del ejercicio
            output: submission.stdout || "",
            stderr: submission.stderr || submission.compile_output || "",
            judge0_token: token,
          };
        })
        .filter((r) => r !== null); // Eliminar nulls

      console.log(`[Batch:${batchId}] ✅ Resultados procesados: ${resultados.length}`);

      // Calcular puntuación total
      let total_puntaje = 0;
      let puntaje_maximo = 0;

      resultados.forEach((resultado) => {
        total_puntaje += resultado.puntaje_obtenido || 0;
        puntaje_maximo += resultado.puntaje_maximo || 0;
      });

      // Convertir a escala 10
      const puntaje_sobre_10 = puntaje_maximo > 0 ? (total_puntaje / puntaje_maximo) * 10 : 0;

      console.log(
        `[Batch:${batchId}] Puntuación: ${total_puntaje}/${puntaje_maximo} (${puntaje_sobre_10.toFixed(
          2
        )}/10)`
      );

      // PASO 8: Enviar resultados a nuestro backend
      console.log(`[Batch:${batchId}] Enviando resultados al backend...`);
      const response = await apiClient.post("/submit-batch/", {
        evaluacion_id: data.evaluacion_id,
        ejercicios: ejerciciosValidos,
        resultados_judge0: resultados,
        batch_id: batchId,
        total_puntaje,
        puntaje_maximo,
        puntaje_sobre_10: parseFloat(puntaje_sobre_10.toFixed(2)),
      });

      // ASEGURARSE DE QUE EL BACKEND PROCESÓ CORRECTAMENTE
      if (!response.data || !response.data.success) {
        throw new Error("Backend no procesó correctamente los resultados");
      }

      console.log(`[Batch:${batchId}] ✅ Respuesta exitosa del backend:`, response.data);
      return response;
    } catch (error) {
      console.error(`[Batch:${batchId}] ❌ Error crítico:`, error);

      // Enviar a nuestro backend para registrar el error
      try {
        console.log(`[Batch:${batchId}] Comunicando error al backend...`);
        const fallbackResponse = await apiClient.post("/submit-batch/", {
          evaluacion_id: data.evaluacion_id,
          ejercicios: data.ejercicios,
          error: error.message,
          batch_id: batchId,
          judge0_error: true,
        });

        return fallbackResponse;
      } catch (backendError) {
        console.error(`[Batch:${batchId}] Error al comunicar fallo a backend:`, backendError);

        // Respuesta de emergencia estructurada
        return {
          data: {
            success: false,
            message: `Error en procesamiento batch: ${error.message}`,
            judge0Error: error.message,
            resultados: [],
            total_puntaje: 0,
            puntaje_maximo: 0,
            puntaje_sobre_10: 0,
          },
        };
      }
    }
  },

  /**
   * Envía y evalúa el código de un ejercicio individual usando Judge0
   * @param {number} evaluationId - ID de la evaluación
   * @param {number} exerciseId - ID del ejercicio
   * @param {string} code - Código del estudiante
   * @returns {Promise<Object>} - Resultado de la evaluación
   */
  async submitCodeExercise(evaluationId, exerciseId, code) {
    // Generar ID único para este envío (para logs)
    const submissionId =
      typeof uuidv4 !== "undefined"
        ? uuidv4().substring(0, 8)
        : Date.now().toString(36).substring(4);

    console.log(`[${submissionId}] Enviando código para ejercicio ${exerciseId} a Judge0`);

    try {
      // 1. Verificar disponibilidad de Judge0
      const judge0Status = await this.checkJudge0Status();
      if (!judge0Status.isAvailable) {
        return {
          ejercicio_id: exerciseId,
          success: false,
          message: `Judge0 no disponible: ${judge0Status.message}`,
        };
      }

      // 2. Enviar directamente a Judge0 para verificar compilación básica
      const judge0Response = await fetch(`${JUDGE0_API_URL}/submissions`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          source_code: code,
          language_id: 71, // Python 3
          base64_encoded: false,
          cpu_time_limit: 5,
          cpu_extra_time: 1,
          wall_time_limit: 15,
          memory_limit: 256000,
          stack_limit: 64000,
          max_processes_and_or_threads: 60,
          enable_network: false,
        }),
      });

      if (!judge0Response.ok) {
        throw new Error(`Error de Judge0: ${judge0Response.status} ${judge0Response.statusText}`);
      }

      const submissionData = await judge0Response.json();
      const token = submissionData.token;

      if (!token) {
        throw new Error("No se recibió token de Judge0");
      }

      // 3. Esperar resultado de la ejecución en Judge0
      const result = await this.waitForJudge0Result(token);

      // 4. Enviar resultado también a nuestro backend
      const backendResponse = await apiClient.post("/submit-codigo/", {
        evaluacion_id: evaluationId,
        ejercicio_id: exerciseId,
        codigo: code,
        timestamp: new Date().toISOString(),
        submission_id: submissionId,
        judge0_result: result, // Pasar el resultado de Judge0
      });

      // 5. Combinar resultados
      return {
        ...backendResponse.data,
        ejercicio_id: exerciseId,
        judge0_token: token,
        codigo: code, // Incluir código evaluado
      };
    } catch (error) {
      console.error(`[${submissionId}] Error en submitCodeExercise:`, error);
      return {
        ejercicio_id: exerciseId,
        success: true,
        message: `Error: ${error.message || "Error desconocido"}`,
      };
    }
  },

  // ---------- MÉTODOS PARA FINALIZACIÓN DE EVALUACIONES ----------

  /**
   * Finaliza una evaluación
   */
  async finishEvaluation(evaluationId) {
    try {
      const userId = localStorage.getItem("user_id");
      console.log(`Finalizando evaluación ${evaluationId} para usuario ${userId}`);

      const response = await apiClient.post(`/evaluaciones/${evaluationId}/finalizar/`, {
        estudiante_id: userId,
        timestamp: new Date().toISOString(),
      });

      // Registrar fin en localStorage con ID de usuario
      localStorage.setItem(`evaluationEndTime_${userId}`, Date.now().toString());

      return response;
    } catch (error) {
      console.error("Error al finalizar evaluación:", error);

      // Registrar fin en localStorage incluso si falla la API
      const userId = localStorage.getItem("user_id");
      localStorage.setItem(`evaluationEndTime_${userId}`, Date.now().toString());

      throw error;
    }
  },

  /**
   * Obtiene resultados para un estudiante
   */
  async getEvaluationResults(evaluationId, studentId) {
    try {
      studentId = studentId || localStorage.getItem("user_id");
      console.log(
        `Obteniendo resultados de evaluación ${evaluationId} para estudiante ${studentId}`
      );

      const response = await apiClient.get(`/evaluaciones/${evaluationId}/resultados/`, {
        params: { estudiante_id: studentId },
      });
      return response;
    } catch (error) {
      console.error("Error al obtener resultados:", error);
      throw error;
    }
  },


  

  /**
   * Obtiene resultados completos de una evaluación
   */
  getEvaluationCompleteResults(evaluationId, studentId = null) {
    const params = studentId ? { estudiante_id: studentId } : {};
    console.log(`📊 Solicitando resultados completos para evaluación ${evaluationId}`);

    // Verificar datos en localStorage antes de hacer la petición
    const userId = localStorage.getItem("user_id") || "anonymous";
    const localData = localStorage.getItem(`evaluation_raw_results_${userId}`);

    if (localData) {
      try {
        const parsedData = JSON.parse(localData);
        const correctScore = localStorage.getItem(`evaluation_scaled_score_${userId}`);

        if (parsedData && correctScore) {
          console.log("📊 Utilizando datos de evaluación almacenados localmente");
          console.log("📊 Puntuación almacenada:", correctScore);

          const processRawResultsForExercises = (parsedData) => {
            // Asegurarnos de tener resultados
            if (!parsedData.resultados || !Array.isArray(parsedData.resultados)) {
              return [];
            }

            // Convertir resultados a formato de respuestas
            return parsedData.resultados.map((resultado) => {
              const ejercicioId = resultado.ejercicio_id;

              // Recuperar código del ejercicio
              let codigo = "";
              try {
                const userId = localStorage.getItem("user_id") || "anonymous";
                const evaluationId = localStorage.getItem("completedEvaluationId");

                // Intentar con formato moderno
                if (evaluationId) {
                  const codeKey = `exercise_code_${userId}_${evaluationId}_${ejercicioId}`;
                  codigo = localStorage.getItem(codeKey) || "";
                }

                // Si no hay código, intentar con formato antiguo
                if (!codigo) {
                  codigo = localStorage.getItem(`exercise_code_${userId}_${ejercicioId}`) || "";
                }
              } catch (e) {
                // Ignorar errores al obtener código
              }

              // Devolver formato compatible con respuestas
              return {
                ejercicio_id: ejercicioId,
                ejercicio_titulo: `Ejercicio ${ejercicioId}`,
                ejercicio_descripcion: "",
                es_correcta: resultado.es_correcto || false,
                puntaje_obtenido: resultado.puntaje_obtenido || 0,
                puntaje_maximo: resultado.puntaje_maximo || 10,
                codigo: codigo, // IMPORTANTE: Incluir código
                resultados: resultado.output || "",
                stderr: resultado.stderr || "",
              };
            });
          };

          // Crear estructura esperada para compatibilidad
          const fakeResponse = {
            data: {
              success: true,
              evaluation: {
                id: evaluationId,
                titulo: localStorage.getItem("currentEvaluation")
                  ? JSON.parse(localStorage.getItem("currentEvaluation")).titulo
                  : "Evaluación",
                puntaje_total: parsedData.total_puntaje || 0,
                puntaje_maximo: parsedData.puntaje_maximo || 0,
                puntaje_sobre_10: parseFloat(correctScore),
                respuestas: processRawResultsForExercises(parsedData), // Usar función para procesar respuestas
                completados_count: parsedData.resultados
                  ? parsedData.resultados.filter((r) => r.es_correcto).length
                  : 0,
                ejercicios_count: parsedData.resultados ? parsedData.resultados.length : 0,
                color_clase:
                  parseFloat(correctScore) >= 9
                    ? "excellent"
                    : parseFloat(correctScore) >= 7
                    ? "good"
                    : parseFloat(correctScore) >= 5
                    ? "average"
                    : "poor",
                fecha_fin: new Date().toISOString(),
              },
            },
          };

          // Esperar antes de devolver para simular petición
          return new Promise((resolve) => {
            setTimeout(() => resolve(fakeResponse), 1000);
          });
        }
      } catch (e) {
        console.warn("⚠️ Error al procesar datos locales:", e);
      }
    }

    // Continuar con la petición original al servidor
    return apiClient
      .get(`/evaluaciones/${evaluationId}/resultados-completos/`, { params })
      .then((response) => {
        console.log("📊 Resultados completos recibidos:", response.data);
        return response;
      })
      .catch((error) => {
        console.error("❌ Error al obtener resultados completos:", error);
        throw error;
      });
  },

  /**
   * Guarda puntuaciones de ejercicios en localStorage
   */
  saveExerciseScore(exerciseId, score, maxScore) {
    try {
      const scoresKey = "evaluation_exercise_scores";
      let scores = {};

      // Cargar puntuaciones existentes
      const savedScores = localStorage.getItem(scoresKey);
      if (savedScores) {
        scores = JSON.parse(savedScores);
      }

      // Actualizar puntuación
      scores[exerciseId] = {
        score: score,
        maxScore: maxScore,
        timestamp: new Date().toISOString(),
      };

      // Guardar scores actualizados
      localStorage.setItem(scoresKey, JSON.stringify(scores));
      console.log(`Guardada puntuación para ejercicio ${exerciseId}: ${score}/${maxScore}`);
      return true;
    } catch (e) {
      console.warn("Error al guardar puntuación:", e);
      return false;
    }
  },

  /**
   * Guarda puntuaciones totales de evaluación en localStorage
   */
  saveEvaluationScores(totalScore, maxScore, scaledScore) {
    try {
      const userId = localStorage.getItem("user_id") || "anonymous";
      localStorage.setItem(`evaluation_total_score_${userId}`, totalScore.toString());
      localStorage.setItem(`evaluation_max_score_${userId}`, maxScore.toString());
      localStorage.setItem(`evaluation_scaled_score_${userId}`, scaledScore.toString());
      return true;
    } catch (e) {
      console.warn("Error al guardar puntuación total:", e);
      return false;
    }
  },
};

export default evaluationsService;
