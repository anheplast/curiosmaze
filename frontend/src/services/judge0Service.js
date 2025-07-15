// src/services/judge0Service.js - Servicio unificado para Judge0
import axios from "axios";

// Configuración desde variables de entorno con fallbacks seguros
const JUDGE0_API_URL = import.meta.env.VITE_JUDGE0_API_URL;
const JUDGE0_TIMEOUT = parseInt(import.meta.env.VITE_JUDGE0_TIMEOUT || "30000");

// ID de lenguajes en Judge0 - Mapeo completo
const LANGUAGE_IDS = {
  python: 71,
  python3: 71,
  javascript: 63,
  java: 62,
  cpp: 54,
  c: 50,
};

// Cliente Axios configurado para Judge0
const judgeClient = axios.create({
  baseURL: JUDGE0_API_URL,
  timeout: JUDGE0_TIMEOUT,
  headers: { "Content-Type": "application/json" },
});

// Configuración para ejecuciones - Combina lo mejor de ambos servicios
const DEFAULT_EXECUTION_OPTIONS = {
  cpu_time_limit: import.meta.env.VITE_CPU_TIME_LIMIT || 5, // 5 segundos por defecto
  cpu_extra_time: import.meta.env.VITE_CPU_EXTRA_TIME || 1, // 1 segundo extra
  wall_time_limit: import.meta.env.VITE_WALL_TIME_LIMIT || 15, // 15 segundos total
  memory_limit: import.meta.env.VITE_MEMORY_LIMIT || 256000, // 256MB
  stack_limit: 64000, // 64MB
  max_processes_and_or_threads: 60,
  enable_network: false,
};

/**
 * Servicio unificado para interactuar con Judge0
 * Combina las mejores características de ambos servicios anteriores
 */
const judge0Service = {
  
  /**
   * Verifica si Judge0 está disponible y funcionando
   * @returns {Promise<{isAvailable: boolean, message: string, languages?: number}>}
   */
  async checkAvailability() {
    try {
      console.log("Verificando disponibilidad de Judge0...");
      
      // Primero intentar con /statuses (más rápido)
      const statusResponse = await judgeClient.get("/statuses", { timeout: 3000 });
      console.log("Respuesta de statuses:", statusResponse.status);
      
      if (statusResponse.status === 200) {
        // Opcionalmente verificar languages para obtener más información
        try {
          const langResponse = await judgeClient.get("/languages", { timeout: 2000 });
          return {
            isAvailable: true,
            message: "Judge0 está listo para trabajar 👷‍♂️",
            languages: langResponse.data?.length || 0,
          };
        } catch (langError) {
          // Si falla languages pero statuses funciona, aún consideramos disponible
          return {
            isAvailable: true,
            message: "Judge0 está disponible (verificación básica)",
          };
        }
      }
      
      return {
        isAvailable: false,
        message: "Judge0 no responde correctamente",
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
   * Ejecuta código en Judge0 con configuración flexible
   * @param {string} sourceCode - Código fuente a ejecutar
   * @param {string|number} language - Lenguaje de programación o ID de lenguaje
   * @param {string} input - Entrada estándar (opcional)
   * @param {string} expectedOutput - Salida esperada (opcional)
   * @returns {Promise<Object>} - Resultado de la ejecución
   */
  async executeCode(sourceCode, language = "python3", input = "", expectedOutput = "") {
    console.log("======= EJECUTANDO CÓDIGO =======");
    
    // Determinar ID de lenguaje (acepta tanto string como número)
    const languageId = typeof language === 'number' ? language : LANGUAGE_IDS[language] || 71;
    console.log(`Lenguaje: ${language} (ID: ${languageId})`);
    console.log(`Input: ${input}`);
    console.log(`Código (primeros 100 caracteres): ${sourceCode.substring(0, 100)}...`);

    try {
      // Verificar disponibilidad primero
      const availability = await this.checkAvailability();
      if (!availability.isAvailable) {
        return {
          success: false,
          error: "Judge0 no está disponible en este momento",
          message: availability.message,
          stdout: "",
          stderr: "",
        };
      }

      console.log(`Ejecutando código (${sourceCode.length} caracteres) con lenguaje ID: ${languageId}`);

      // Crear objeto de envío con configuración completa
      const submission = {
        source_code: sourceCode,
        language_id: languageId,
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

      // Esperar resultado con polling inteligente
      const result = await this.waitForResult(token);
      console.log(`Resultado recibido para token ${token}:`, result.status?.description);

      // Formatear respuesta unificada
      return {
        success: result.status?.id === 3, // 3 = Accepted
        stdout: result.stdout || "",
        stderr: result.stderr || "",
        compile_output: result.compile_output || "",
        message: result.message || "",
        time: result.time || "0",
        memory: result.memory || 0,
        status: result.status || { id: 0, description: "Unknown" },
        token: token,
      };
      
    } catch (error) {
      console.error("Error en executeCode:", error);
      return {
        success: false,
        error: error.message || "Error desconocido al ejecutar código",
        stdout: "",
        stderr: error.toString(),
        time: "0",
        status: { id: -1, description: "Error" },
      };
    }
  },

  /**
   * Espera y obtiene el resultado de una ejecución con polling inteligente
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
        const elapsedTime = Math.round((Date.now() - startTime) / 1000);
        console.log(`[${elapsedTime}s] Consultando ${url}`);

        const response = await judgeClient.get(url);

        if (!response.data) {
          throw new Error("Respuesta vacía de Judge0");
        }

        const result = response.data;
        const statusId = result.status?.id;

        // Si no está en cola (1) ni procesando (2), retornamos resultado
        if (statusId !== 1 && statusId !== 2) {
          console.log(
            `✅ Resultado obtenido para token ${token}, status: ${result.status?.description}`
          );
          return result;
        }

        // Mostrar progreso
        console.log(
          `⏳ Token ${token} en ${
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
   * Envía múltiples códigos para ejecución en batch
   * @param {Array} submissions - Array de objetos con código a ejecutar
   * @returns {Promise<Object>}
   */
  async submitBatch(submissions) {
    console.log("======= ENVIANDO BATCH A JUDGE0 =======");
    console.log(`Total de ejercicios: ${submissions.length}`);

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

      // Formatear cada submission con flexibilidad en los campos de entrada
      const formattedSubmissions = submissions.map((sub, index) => {
        console.log(`Preparando ejercicio #${index + 1}: ${(sub.code || sub.source_code || "").length} caracteres`);

        // Determinar ID de lenguaje con flexibilidad
        const languageId = sub.language_id || 
                          LANGUAGE_IDS[sub.language] || 
                          LANGUAGE_IDS.python3;

        return {
          language_id: languageId,
          source_code: sub.code || sub.source_code || "",
          stdin: sub.input || sub.stdin || "",
          expected_output: sub.expected_output || "",
          ...DEFAULT_EXECUTION_OPTIONS,
        };
      });

      // Crear el objeto batch
      const batchData = { submissions: formattedSubmissions };

      // Enviar a Judge0 con parámetros optimizados
      console.log("🚀 POST /submissions/batch - enviando...");
      const response = await judgeClient.post("/submissions/batch", batchData, {
        params: { base64_encoded: "false" },
      });

      console.log("✅ POST /submissions/batch - respuesta recibida");

      if (!response.data || !Array.isArray(response.data)) {
        throw new Error("Formato de respuesta inesperado de Judge0");
      }

      // Extraer tokens y errores con mejor logging
      const tokens = [];
      const errors = [];

      response.data.forEach((item, index) => {
        if (item && item.token) {
          tokens.push(item.token);
          console.log(`✅ Token #${index + 1}: ${item.token}`);
        } else {
          errors.push(item);
          console.warn(`❌ Error en ejercicio #${index + 1}:`, item);
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
   * Obtiene resultados de un lote de ejecuciones con polling inteligente
   * @param {Array} tokens - Array de tokens para verificar resultados
   * @returns {Promise<Object>}
   */
  async getBatchResults(tokens) {
    console.log("======= OBTENIENDO RESULTADOS DE BATCH =======");
    console.log(`Tokens a consultar: ${tokens.length}`);

    try {
      if (!Array.isArray(tokens) || tokens.length === 0) {
        throw new Error("Se debe proporcionar un array no vacío de tokens");
      }

      // Construir URL con tokens
      const tokensStr = tokens.join(",");
      const url = `/submissions/batch?tokens=${tokensStr}&base64_encoded=false`;

      // Polling inteligente con timeout adaptativo
      const MAX_ATTEMPTS = 60; // Aumentado para batches grandes
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

          // Formatear resultados con información completa
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
   * Verifica ejemplos/tests para un ejercicio
   * @param {string} code - Código a evaluar
   * @param {Array} ejemplos - Array de ejemplos con formato {entrada, salida}
   * @param {string|number} language - Lenguaje de programación (por defecto Python)
   * @returns {Promise<Object>}
   */
  async verificarEjemplos(code, ejemplos, language = "python3") {
    console.log("======= VERIFICANDO EJEMPLOS =======");
    
    const languageId = typeof language === 'number' ? language : LANGUAGE_IDS[language] || 71;
    console.log(`Verificando ${ejemplos?.length || 0} ejemplos con lenguaje ${language} (ID: ${languageId})`);

    if (!ejemplos || !Array.isArray(ejemplos) || ejemplos.length === 0) {
      return {
        success: false,
        message: "No hay ejemplos para verificar",
        resultados: [],
        casosCorrectos: 0,
        totalEjemplos: 0,
        porcentajeExito: 0,
      };
    }

    try {
      const resultados = [];
      let casosCorrectos = 0;
      const totalEjemplos = ejemplos.length;

      // Procesar cada ejemplo secuencialmente para mejor control
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
          const result = await this.executeCode(code, languageId, entrada, salidaEsperada);

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
        `Resultado final: ${casosCorrectos}/${totalEjemplos} correctos (${porcentajeExito.toFixed(2)}%)`
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

  /**
   * Ejecuta tests avanzados combinando código del estudiante con tests personalizados
   * @param {string} code - Código del estudiante
   * @param {string} testCode - Código de tests avanzados
   * @param {string|number} language - Lenguaje de programación
   * @returns {Promise<Object>}
   */
  async executeAdvancedTests(code, testCode, language = "python3") {
    console.log("======= EJECUTANDO TESTS AVANZADOS =======");

    try {
      // Asegurar que testCode tenga las funciones auxiliares necesarias
      const finalTestCode = this.ensureTestHelpers(testCode, language);

      // Combinar código y tests de manera inteligente
      const combinedCode = `
# ===== CÓDIGO DEL ESTUDIANTE =====
${code}

# ===== CÓDIGO DE TESTS =====
${finalTestCode}
`.trim();

      // Ejecutar el código combinado
      const result = await this.executeCode(combinedCode, language);

      // Analizar resultado
      const output = result.stdout || "";

      // Extraer información de tests pasados usando múltiples patrones
      let totalTests = 0;
      let passingTests = 0;

      // Patrón 1: "Resultado: X/Y pruebas pasadas"
      const testSummaryMatch = output.match(/Resultado:\s*(\d+)\/(\d+)\s*pruebas\s*pasadas/i);
      if (testSummaryMatch) {
        passingTests = parseInt(testSummaryMatch[1], 10);
        totalTests = parseInt(testSummaryMatch[2], 10);
      } else {
        // Patrón 2: Contar líneas de CORRECTO/INCORRECTO
        const correctLines = (output.match(/✓.*CORRECTO/gi) || []).length;
        const incorrectLines = (output.match(/✗.*INCORRECTO/gi) || []).length;
        
        if (correctLines + incorrectLines > 0) {
          passingTests = correctLines;
          totalTests = correctLines + incorrectLines;
        } else {
          // Patrón 3: Fallback genérico
          totalTests = Math.max(1, (output.match(/Prueba|Test|Case/gi) || []).length);
          passingTests = (output.match(/Passed|OK|Success|✓/gi) || []).length;
        }
      }

      return {
        success: result.success,
        allPassed: passingTests > 0 && passingTests === totalTests,
        rawOutput: output,
        totalTests: totalTests || 1,
        passingTests: passingTests,
        failingTests: Math.max(0, totalTests - passingTests),
        stderr: result.stderr || "",
        time: result.time,
        porcentajeExito: totalTests > 0 ? (passingTests / totalTests) * 100 : 0,
      };
      
    } catch (error) {
      console.error("Error en executeAdvancedTests:", error);
      return {
        success: false,
        message: `Error en tests avanzados: ${error.message}`,
        rawOutput: error.toString(),
        totalTests: 0,
        passingTests: 0,
        failingTests: 0,
        porcentajeExito: 0,
      };
    }
  },

  /**
   * Asegura que el código de tests tenga todas las funciones auxiliares necesarias
   * @param {string} testCode - Código de tests original
   * @param {string|number} language - Lenguaje de programación
   * @returns {string} - Código de tests con funciones auxiliares
   */
  ensureTestHelpers(testCode, language = "python3") {
    const lang = typeof language === 'string' ? language : 'python3';
    
    // Si ya incluye las funciones auxiliares, no hacer nada
    if (
      testCode.includes("def ejecutar_tests_avanzados") ||
      testCode.includes("def test(") ||
      testCode.includes("function ejecutar_tests_avanzados")
    ) {
      return testCode;
    }

    // Generar funciones auxiliares según el lenguaje
    let helpers = "";
    
    if (lang.includes('python')) {
      helpers = `
# ===== FUNCIONES AUXILIARES PARA TESTS =====
def ejecutar_tests_avanzados(func, casos_prueba, mostrar_detalle=True):
    """
    Ejecuta una serie de pruebas para una función.
    
    Args:
        func: La función a probar
        casos_prueba: Lista de tuplas (entrada, salida_esperada)
        mostrar_detalle: Si es True, muestra el detalle de cada caso
    
    Returns:
        int: Número de pruebas pasadas
    """
    pruebas_pasadas = 0
    total_pruebas = len(casos_prueba)
    
    print(f"Ejecutando {total_pruebas} pruebas:")
    
    for i, (entrada, esperado) in enumerate(casos_prueba, 1):
        try:
            # Si la entrada es una tupla, desempaquetar
            if isinstance(entrada, tuple):
                resultado = func(*entrada)
            else:
                resultado = func(entrada)
                
            if resultado == esperado:
                pruebas_pasadas += 1
                if mostrar_detalle:
                    print(f"✓ CORRECTO - Prueba {i}: con entrada {entrada} se obtuvo {resultado}")
            else:
                if mostrar_detalle:
                    print(f"✗ INCORRECTO - Prueba {i}: con entrada {entrada}")
                    print(f"  Se esperaba: {esperado}")
                    print(f"  Se obtuvo: {resultado}")
        except Exception as e:
            if mostrar_detalle:
                print(f"✗ ERROR - Prueba {i}: con entrada {entrada}")
                print(f"  Error: {str(e)}")
    
    print(f"Resultado: {pruebas_pasadas}/{total_pruebas} pruebas pasadas")
    return pruebas_pasadas

def test(actual, expected, message=""):
    """
    Compara un valor actual con uno esperado.
    
    Args:
        actual: El valor obtenido
        expected: El valor esperado
        message: Mensaje descriptivo opcional
        
    Returns:
        bool: True si los valores coinciden
    """
    if actual == expected:
        print(f"✓ CORRECTO: {message}")
        return True
    else:
        print(f"✗ INCORRECTO: {message}")
        print(f"  Esperado: {expected}")
        print(f"  Obtenido: {actual}")
        return False
`.trim();
    
    } else if (lang.includes('java')) {
      helpers = `
// ===== FUNCIONES AUXILIARES PARA TESTS =====
public static int resultadoTests = 0;
public static int totalTests = 0;

public static boolean test(Object actual, Object expected, String message) {
    totalTests++;
    if (actual.equals(expected)) {
        System.out.println("✓ CORRECTO: " + message);
        resultadoTests++;
        return true;
    } else {
        System.out.println("✗ INCORRECTO: " + message);
        System.out.println("  Esperado: " + expected);
        System.out.println("  Obtenido: " + actual);
        return false;
    }
}
`.trim();
    
    } else {
      // Para otros lenguajes, usar una versión genérica en comentarios
      helpers = `
// ===== FUNCIONES AUXILIARES PARA TESTS =====
// Funciones de testing genéricas añadidas automáticamente
`.trim();
    }

    // Unir las funciones auxiliares con el código de tests
    return helpers + "\n\n" + testCode;
  },

  // Métodos de compatibilidad para mantener compatibilidad con código existente
  
  /**
   * Alias para checkAvailability (compatibilidad)
   */
  async checkConnection() {
    return await this.checkAvailability();
  },

  /**
   * Obtiene información sobre los lenguajes disponibles en Judge0
   * @returns {Promise<Object>}
   */
  async getLanguages() {
    try {
      const response = await judgeClient.get("/languages");
      return {
        success: true,
        languages: response.data,
        count: response.data?.length || 0,
      };
    } catch (error) {
      console.error("Error obteniendo lenguajes:", error);
      return {
        success: false,
        message: error.message,
        languages: [],
        count: 0,
      };
    }
  },

};

export default judge0Service;