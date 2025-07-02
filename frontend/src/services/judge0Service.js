// src/services/judge0Service.js
import axios from "axios";

// Configuración desde variables de entorno
const JUDGE0_API_URL = import.meta.env.VITE_JUDGE0_API_URL;
const JUDGE0_TIMEOUT = parseInt(import.meta.env.VITE_JUDGE0_TIMEOUT || "30000");

// ID de lenguajes en Judge0
const LANGUAGE_IDS = {
  python: 71,
  javascript: 63,
  java: 62,
  cpp: 54,
  c: 50,
};

// Cliente Axios configurado para Judge0 - TIMEOUT AUMENTADO
const judgeClient = axios.create({
  baseURL: JUDGE0_API_URL,
  timeout: JUDGE0_TIMEOUT,
  headers: { "Content-Type": "application/json" },
});

// Configuración para ejecuciones
const DEFAULT_EXECUTION_OPTIONS = {
  cpu_time_limit: import.meta.env.VITE_CPU_TIME_LIMIT || 2,
  cpu_extra_time: import.meta.env.VITE_CPU_EXTRA_TIME || 0.5,
  wall_time_limit: import.meta.env.VITE_WALL_TIME_LIMIT || 5,
  memory_limit: import.meta.env.VITE_MEMORY_LIMIT || 128000,
  stack_limit: 64000,
  max_processes_and_or_threads: 60,
  enable_network: false,
};

const judge0Service = {
  /**
   * Verifica si Judge0 está disponible
   * @returns {Promise<{isAvailable: boolean, message: string}>}
   */
  async checkAvailability() {
    try {
      console.log("Verificando disponibilidad de Judge0...");
      const response = await judgeClient.get("/statuses", { timeout: 3000 });
      console.log("Respuesta de statuses:", response.status);
      return {
        isAvailable: response.status === 200,
        message:
          response.status === 200
            ? "Judge0 está listo para trabajar 👷‍♂️"
            : "Judge0 no responde correctamente",
      };
    } catch (error) {
      console.error("Error verificando Judge0:", error);
      return {
        isAvailable: false,
        message: "Judge0 está de vacaciones 🏖",
      };
    }
  },

  /**
   * Ejecuta código en Judge0
   * @param {string} sourceCode - Código fuente a ejecutar
   * @param {string} input - Entrada estándar (opcional)
   * @param {string} expectedOutput - Salida esperada (opcional)
   * @param {string} language - Lenguaje de programación (por defecto 'python')
   * @returns {Promise<Object>} - Resultado de la ejecución
   */
  async executeCode(sourceCode, input = "", expectedOutput = "", languageId = 71) {
    console.log(`Ejecutando código con lenguaje ID: ${languageId}`);

    try {
      // Verificar disponibilidad primero
      const availability = await this.checkAvailability();
      if (!availability.isAvailable) {
        return {
          success: false,
          error: "Judge0 no está disponible en este momento",
          message: availability.message,
        };
      }

      console.log(`Ejecutando código (${sourceCode.length} caracteres) con lenguaje ID: ${languageId}`);

      // Crear objeto de envío
      const submission = {
        source_code: sourceCode,
        language_id: languageId, // Usar el ID proporcionado
        stdin: input,
        expected_output: expectedOutput,
        ...DEFAULT_EXECUTION_OPTIONS,
      };

      // Enviar a Judge0
      console.log("Enviando código a Judge0...");
      const createResponse = await judgeClient.post("/submissions", submission);

      if (!createResponse.data || !createResponse.data.token) {
        throw new Error("No se recibió token de Judge0");
      }

      // Obtener token para seguimiento
      const token = createResponse.data.token;
      console.log(`Token recibido: ${token}`);

      // Esperar resultado
      const result = await this.waitForResult(token);
      console.log(`Resultado recibido para token ${token}:`, result.status?.description);

      // Formatear respuesta
      return {
        success: result.status?.id === 3, // 3 = Accepted
        stdout: result.stdout || "",
        stderr: result.stderr || "",
        compile_output: result.compile_output || "",
        message: result.message,
        time: result.time,
        memory: result.memory,
        status: result.status,
        token: token,
      };
    } catch (error) {
      console.error("Error en executeCode:", error);
      return {
        success: false,
        error: error.message || "Error desconocido al ejecutar código",
        stderr: error.toString(),
      };
    }
  },

  /**
   * Espera y obtiene el resultado de una ejecución 
   * @param {string} token - Token de seguimiento
   * @returns {Promise<Object>} - Resultado completo
   */
  async waitForResult(token) {
    console.log(`Esperando resultado para token: ${token}`);
    const startTime = Date.now();
    const MAX_WAIT_TIME = JUDGE0_TIMEOUT;
    const POLL_INTERVAL = 500; // 0.5 segundos entre intentos

    while (Date.now() - startTime < MAX_WAIT_TIME) {
      try {
        const url = `/submissions/${token}?fields=*&base64_encoded=false`;
        console.log(`[${Math.round((Date.now() - startTime) / 1000)}s] GET ${url}`);

        const response = await judgeClient.get(url);

        if (!response.data) {
          throw new Error("Respuesta vacía de Judge0");
        }

        const result = response.data;
        const statusId = result.status?.id;

        // Si no está en cola (1) ni procesando (2), retornamos resultado
        if (statusId !== 1 && statusId !== 2) {
          console.log(
            `Resultado obtenido para token ${token}, status: ${result.status?.description}`
          );
          return result;
        }

        // Mostrar progreso
        console.log(
          `Token ${token} en ${
            statusId === 1 ? "cola" : "procesamiento"
          }... espero ${POLL_INTERVAL}ms`
        );

        // Si aún corre, esperar antes de nuevo polling
        await new Promise((resolve) => setTimeout(resolve, POLL_INTERVAL));
      } catch (error) {
        console.error("Error al obtener resultado:", error);

        // Si estamos cerca del tiempo límite, mejor fallar rápido
        if (Date.now() - startTime > MAX_WAIT_TIME - 5000) {
          throw error;
        }

        // Esperar e intentar de nuevo con un intervalo mayor
        await new Promise((resolve) => setTimeout(resolve, POLL_INTERVAL * 2));
      }
    }

    throw new Error(`Tiempo máximo excedido (${MAX_WAIT_TIME / 1000}s)`);
  },

  /**
   * Enviar múltiples códigos para ejecución en batch
   * @param {Array} submissions - Array de objetos con código a ejecutar
   * @returns {Promise<Object>}
   */
  async submitBatch(submissions) {
    console.log("⏳ Enviando batch con", submissions.length, "ejercicios");

    try {
      // Verificar disponibilidad primero
      const availability = await this.checkAvailability();
      if (!availability.isAvailable) {
        return {
          success: false,
          error: "Judge0 no está disponible en este momento",
          message: availability.message,
          tokens: [],
        };
      }

      if (!Array.isArray(submissions) || submissions.length === 0) {
        throw new Error("Se debe proporcionar un array no vacío de ejercicios");
      }

      // Formatear cada submission
      const formattedSubmissions = submissions.map((sub, index) => {
        console.log(`Preparando ejercicio #${index + 1}: ${sub.code?.length || 0} caracteres`);

        return {
          language_id: LANGUAGE_IDS[sub.language] || 71, // Python por defecto
          source_code: sub.code || sub.source_code || "",
          stdin: sub.input || "",
          expected_output: sub.expected_output || "",
          ...DEFAULT_EXECUTION_OPTIONS,
        };
      });

      // Crear el objeto batch
      const batchData = { submissions: formattedSubmissions };

      // Enviar a Judge0
      console.log("🚀 POST /submissions/batch - enviando...");
      const response = await judgeClient.post("/submissions/batch", batchData, {
        params: { base64_encoded: "false" }, // Parámetro importante 
      });

      console.log("✅ POST /submissions/batch - respuesta recibida");

      if (!response.data) {
        throw new Error("Formato de respuesta inesperado de Judge0");
      }

      // Extraer tokens y errores
      const tokens = [];
      const errors = [];

      response.data.forEach((item, index) => {
        if (item && item.token) {
          tokens.push(item.token);
          console.log(`Token #${index + 1}: ${item.token}`);
        } else {
          errors.push(item);
          console.warn(`Error en ejercicio #${index + 1}:`, item);
        }
      });

      if (tokens.length === 0) {
        throw new Error("No se recibió ningún token válido");
      }

      return {
        success: true,
        tokens,
        errors,
        totalSubmissions: submissions.length,
      };
    } catch (error) {
      console.error("Error en submitBatch:", error);
      return {
        success: false,
        message: error.message || "Error desconocido",
        tokens: [],
        errors: [{ general: error.toString() }],
      };
    }
  },

  /**
   * Obtener resultados de un lote de ejecuciones
   * @param {Array} tokens - Array de tokens para verificar resultados
   * @returns {Promise<Object>}
   */
  async getBatchResults(tokens) {
    console.log("⏳ Esperando resultados para", tokens.length, "tokens");

    try {
      if (!Array.isArray(tokens) || tokens.length === 0) {
        throw new Error("Se debe proporcionar un array no vacío de tokens");
      }

      // Construir URL con tokens
      const tokensStr = tokens.join(",");
      const url = `/submissions/batch?tokens=${tokensStr}&base64_encoded=false`;

      // Intentos y polling
      const MAX_ATTEMPTS = 30;
      const POLL_INTERVAL = 1000; // 1 segundo

      for (let attempt = 1; attempt <= MAX_ATTEMPTS; attempt++) {
        console.log(`🔄 Intento ${attempt}/${MAX_ATTEMPTS} - GET ${url}`);

        try {
          const response = await judgeClient.get(url);

          if (!response.data || !response.data.submissions) {
            console.warn("⚠️ Formato de respuesta inesperado:", response.data);
            await new Promise((resolve) => setTimeout(resolve, POLL_INTERVAL));
            continue;
          }

          const { submissions } = response.data;
          console.log(`📊 Recibidas ${submissions.length} submissions`);

          // Verificar si hay submissions pendientes
          const pending = submissions.filter(
            (s) => s.status?.id === 1 || s.status?.id === 2 // 1=In Queue, 2=Processing
          );

          if (pending.length > 0) {
            console.log(`⏱️ Aún hay ${pending.length} submissions pendientes, esperando...`);
            await new Promise((resolve) => setTimeout(resolve, POLL_INTERVAL));
            continue;
          }

          // Si todas están completas, procesar y devolver
          console.log("✅ Todas las submissions completadas");

          // Formatear resultados
          const results = submissions.map((sub) => ({
            token: sub.token,
            status: sub.status,
            stdout: sub.stdout || "",
            stderr: sub.stderr || "",
            compile_output: sub.compile_output || "",
            time: sub.time || "0",
            memory: sub.memory || 0,
            language_id: sub.language_id,
            success: sub.status && sub.status.id === 3, // 3 = Accepted
          }));

          return {
            success: true,
            results,
          };
        } catch (error) {
          console.error(`❌ Error en intento ${attempt}:`, error);
          // Esperar más tiempo entre intentos si hay errores
          await new Promise((resolve) => setTimeout(resolve, POLL_INTERVAL * 2));
        }
      }

      throw new Error(`Tiempo máximo excedido después de ${MAX_ATTEMPTS} intentos`);
    } catch (error) {
      console.error("Error en getBatchResults:", error);
      return {
        success: false,
        message: error.message || "Error desconocido",
        results: [],
      };
    }
  },

  /**
   * Verificar ejemplos/tests para un ejercicio
   * @param {string} code - Código a evaluar
   * @param {Array} ejemplos - Array de ejemplos con formato {entrada, salida}
   * @returns {Promise<Object>}
   */
  async verificarEjemplos(code, ejemplos, languageId = 71) {
    console.log("Verificando", ejemplos?.length || 0, "ejemplos con lenguaje ID:", languageId);

    if (!ejemplos || !Array.isArray(ejemplos) || ejemplos.length === 0) {
      return {
        success: false,
        message: "No hay ejemplos para verificar",
      };
    }

    try {
      const resultados = [];
      let casosCorrectos = 0;
      const totalEjemplos = ejemplos.length;

      // Procesar cada ejemplo secuencialmente
      for (let i = 0; i < ejemplos.length; i++) {
        const ejemplo = ejemplos[i];
        console.log(
          `Procesando ejemplo #${i + 1}:`,
          ejemplo.entrada?.substring(0, 30) || "<vacío>"
        );

        const entrada = ejemplo.entrada || "";
        const salidaEsperada = (ejemplo.salida || "").trim();

        try {
          // Ejecutar con Judge0
          const result = await this.executeCode(code, entrada, salidaEsperada, languageId);

          // Obtener la salida real
          const salidaReal = (result.stdout || "").trim();

          // Verificar si es correcto
          const esCorrecto = salidaReal === salidaEsperada;
          if (esCorrecto) {
            casosCorrectos++;
            console.log(`✅ Ejemplo #${i + 1} correcto`);
          } else {
            console.log(`❌ Ejemplo #${i + 1} incorrecto`);
            console.log(`  Esperado: "${salidaEsperada}"`);
            console.log(`  Obtenido: "${salidaReal}"`);
          }

          // Guardar resultado detallado
          resultados.push({
            ejemplo: i + 1,
            entrada: entrada,
            salidaEsperada: salidaEsperada,
            salidaReal: salidaReal,
            esCorrecto: esCorrecto,
            tiempo: result.time,
            error: result.stderr || result.compile_output || "",
            stderr: result.stderr || "",
          });
        } catch (ejemploError) {
          console.error(`Error en ejemplo #${i + 1}:`, ejemploError);
          resultados.push({
            ejemplo: i + 1,
            entrada: entrada,
            salidaEsperada: salidaEsperada,
            salidaReal: "",
            esCorrecto: false,
            tiempo: "0",
            error: ejemploError.message || "Error en la ejecución",
            stderr: "",
          });
        }
      }

      // Calcular porcentaje de éxito
      const porcentajeExito = (casosCorrectos / totalEjemplos) * 100;
      console.log(
        `Resultado final: ${casosCorrectos}/${totalEjemplos} correctos (${porcentajeExito.toFixed(
          2
        )}%)`
      );

      return {
        success: true,
        resultados: resultados,
        casosCorrectos: casosCorrectos,
        totalEjemplos: totalEjemplos,
        porcentajeExito: porcentajeExito,
      };
    } catch (error) {
      console.error("Error en verificarEjemplos:", error);
      return {
        success: false,
        message: `Error al verificar ejemplos: ${error.message}`,
        resultados: [],
        casosCorrectos: 0,
        totalEjemplos: ejemplos.length,
        porcentajeExito: 0,
      };
    }
  },
};

export default judge0Service;
