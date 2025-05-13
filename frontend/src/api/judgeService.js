// src/api/judgeService.js - Versión corregida para Judge0
import axios from "axios";

// Configuración base para Judge0
const JUDGE0_API = import.meta.env.VITE_JUDGE0_API_URL;
const MAX_WAIT_TIME = 30000; // 30 segundos máximo de espera

// Cliente axios específico para Judge0
const judgeClient = axios.create({
  baseURL: JUDGE0_API,
  timeout: MAX_WAIT_TIME,
  headers: {
    "Content-Type": "application/json",
  },
});

// Mapeo de lenguajes a IDs de Judge0
const LANGUAGE_IDS = {
  python3: 71,
  python: 71,
  javascript: 63,
  java: 62,
  c: 50,
  cpp: 54,
};

// Límites seguros para ejercicios
const DEFAULT_LIMITS = {
  cpu_time_limit: 5, // 5 segundos
  cpu_extra_time: 1, // 1 segundo extra
  wall_time_limit: 15, // 15 segundos total
  memory_limit: 256000, // 256MB
  stack_limit: 64000, // 64MB
  max_processes_and_or_threads: 60,
};

// Servicio mejorado para interactuar con Judge0
const judgeService = {
  // Comprobar conectividad con Judge0
  async checkConnection() {
    try {
      const response = await judgeClient.get("/languages");
      return {
        success: true,
        message: "Conexión exitosa con Judge0",
        languages: response.data.length,
      };
    } catch (error) {
      console.error("Error al conectar con Judge0:", error);
      return {
        success: false,
        message: `Error de conexión: ${error.message}`,
      };
    }
  },

  // Ejecuta código en Judge0
  async executeCode(code, language = "python3", input = "", expectedOutput = "") {
    console.log("======= EJECUTANDO CÓDIGO =======");
    console.log(`Lenguaje: ${language}`);
    console.log(`Input: ${input}`);
    console.log(`Código (primeros 100 caracteres): ${code.substring(0, 100)}...`);

    try {
      // Crear la submisión
      const submissionData = {
        source_code: code,
        language_id: LANGUAGE_IDS[language] || 71, // Default a Python 3
        stdin: input,
        expected_output: expectedOutput,
        ...DEFAULT_LIMITS,
      };

      // Enviar a Judge0
      const createResponse = await judgeClient.post("/submissions", submissionData);

      if (!createResponse.data || !createResponse.data.token) {
        throw new Error("No se recibió token de Judge0");
      }

      const token = createResponse.data.token;
      console.log("Token recibido:", token);

      // Esperar resultado con polling y tiempo máximo
      const result = await this.waitForResult(token);
      console.log("Resultado completo:", result);

      // Formatear respuesta
      return {
        success: result.status && result.status.id === 3, // 3 = Accepted
        stdout: result.stdout || "",
        stderr: result.stderr || "",
        compile_output: result.compile_output || "",
        message: result.message || "",
        time: result.time || "0",
        memory: result.memory || 0,
        status: result.status || { id: 0, description: "Unknown" },
      };
    } catch (error) {
      console.error("Error en executeCode:", error);
      return {
        success: false,
        error: error.message,
        stdout: "",
        stderr: error.toString(),
        time: "0",
        status: { id: -1, description: "Error" },
      };
    }
  },

  async waitForResult(token) {
    const startTime = Date.now();
    const pollInterval = 1000; // 1 segundo entre intentos

    while (Date.now() - startTime < MAX_WAIT_TIME) {
      try {
        // Simplificación de URL para mejor compatibilidad
        const response = await judgeClient.get(`/submissions/${token}`);

        if (!response.data) {
          throw new Error("Respuesta vacía de Judge0");
        }

        const result = response.data;

        // Si todavía está en proceso (status 1 o 2), seguir esperando
        if (result.status && (result.status.id === 1 || result.status.id === 2)) {
          console.log(`Código en ejecución... (${Math.round((Date.now() - startTime) / 1000)}s)`);
          await new Promise((resolve) => setTimeout(resolve, pollInterval));
          continue;
        }

        return result;
      } catch (error) {
        console.error("Error al obtener resultado:", error);

        // Si estamos cerca del tiempo límite, mejor fallar rápido
        if (Date.now() - startTime > MAX_WAIT_TIME - 5000) {
          throw error;
        }

        // Esperar e intentar de nuevo con un intervalo mayor
        await new Promise((resolve) => setTimeout(resolve, pollInterval * 2));
      }
    }

    throw new Error(`Tiempo máximo excedido (${MAX_WAIT_TIME / 1000}s)`);
  },

  // Enviar un lote de ejercicios a Judge0
  async submitBatch(submissions) {
    console.log("======= ENVIANDO BATCH A JUDGE0 =======");
    console.log(`Total de ejercicios: ${submissions.length}`);

    try {
      if (!Array.isArray(submissions) || submissions.length === 0) {
        throw new Error("Se debe proporcionar un array no vacío de ejercicios");
      }

      // Asegurar que cada submission tenga los campos correctos
      const formattedSubmissions = submissions.map((sub) => ({
        language_id: sub.language_id || LANGUAGE_IDS.python3,
        source_code: sub.source_code || "",
        ...DEFAULT_LIMITS,
      }));

      // Crear el objeto batch según la documentación
      const batchData = {
        submissions: formattedSubmissions,
      };

      // Enviar a Judge0
      console.log("Enviando datos a /submissions/batch...");
      const response = await judgeClient.post("/submissions/batch", batchData);

      // Verificar la respuesta
      if (!response.data || !Array.isArray(response.data)) {
        throw new Error("Formato de respuesta inesperado de Judge0");
      }

      // Extraer tokens y errores
      const tokens = [];
      const errors = [];

      response.data.forEach((item) => {
        if (item && item.token) {
          tokens.push(item.token);
        } else {
          errors.push(item);
        }
      });

      console.log(`Tokens recibidos: ${tokens.length}, Errores: ${errors.length}`);

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
        message: error.message,
        tokens: [],
        errors: [{ general: error.toString() }],
      };
    }
  },

  // Obtener resultados de un lote de ejercicios
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

      // Obtener resultados
      console.log(`Consultando: ${url}`);
      const response = await judgeClient.get(url);

      if (!response.data || !response.data.submissions) {
        throw new Error("Formato de respuesta inesperado");
      }

      const { submissions } = response.data;
      console.log(`Resultados recibidos: ${submissions.length}`);

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
      console.error("Error en getBatchResults:", error);
      return {
        success: false,
        message: error.message,
        results: [],
      };
    }
  },

  // Verificar ejemplos de un ejercicio
  async verificarEjemplos(code, ejemplos) {
    console.log("======= VERIFICANDO EJEMPLOS =======");
    console.log(`Total ejemplos: ${ejemplos.length}`);

    if (!ejemplos || !Array.isArray(ejemplos) || ejemplos.length === 0) {
      return {
        success: false,
        message: "No hay ejemplos para verificar",
      };
    }

    try {
      const resultados = [];
      let casosCorrectos = 0;
      let totalEjemplos = ejemplos.length;

      // Procesar cada ejemplo
      for (let i = 0; i < ejemplos.length; i++) {
        const ejemplo = ejemplos[i];
        const entrada = ejemplo.entrada || "";
        const salidaEsperada = (ejemplo.salida || "").trim();

        console.log(`Procesando ejemplo ${i + 1}:`);
        console.log(`Entrada: "${entrada}"`);
        console.log(`Salida esperada: "${salidaEsperada}"`);

        try {
          // Ejecutar con Judge0
          const result = await this.executeCode(code, "python3", entrada, salidaEsperada);

          // Obtener la salida real
          const salidaReal = (result.stdout || "").trim();
          console.log(`Salida real: "${salidaReal}"`);

          // Verificar si es correcto
          const esCorrecto = salidaReal === salidaEsperada;
          if (esCorrecto) {
            casosCorrectos++;
            console.log("✅ Correcto");
          } else {
            console.log("❌ Incorrecto");
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
          console.error(`Error en ejemplo ${i + 1}:`, ejemploError);

          // Añadir resultado de error
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

      // Resultado consolidado
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

  // Ejecuta tests avanzados
  async executeAdvancedTests(code, testCode) {
    console.log("======= EJECUTANDO TESTS AVANZADOS =======");

    try {
      // Asegurar que testCode tenga las funciones auxiliares necesarias
      const finalTestCode = this.ensureTestHelpers(testCode);

      // Combinar código y tests
      const combinedCode = `
# Código del estudiante
${code}

# Código de tests
${finalTestCode}
`.trim();

      // Ejecutar el código combinado
      const result = await this.executeCode(combinedCode, "python3");

      // Analizar resultado
      const output = result.stdout || "";

      // Extraer información de tests pasados
      let totalTests = 0;
      let passingTests = 0;

      // Intentar extraer resultado de tests a partir de la salida
      const testSummaryMatch = output.match(/Resultado:\s*(\d+)\/(\d+)\s*pruebas\s*pasadas/i);
      if (testSummaryMatch) {
        passingTests = parseInt(testSummaryMatch[1], 10);
        totalTests = parseInt(testSummaryMatch[2], 10);
      } else {
        // Si no hay formato estándar, contar manualmente
        totalTests = (output.match(/Prueba|Test|CORRECTO|INCORRECTO/gi) || []).length || 1;
        passingTests = (output.match(/CORRECTO|Passed|OK/gi) || []).length;
      }

      return {
        success: result.success,
        allPassed: passingTests > 0 && passingTests === totalTests,
        rawOutput: output,
        totalTests: totalTests || 1,
        passingTests: passingTests,
        failingTests: totalTests - passingTests,
        stderr: result.stderr || "",
      };
    } catch (error) {
      console.error("Error en executeAdvancedTests:", error);
      return {
        success: false,
        message: `Error en tests avanzados: ${error.message}`,
        rawOutput: error.toString(),
        totalTests: 0,
        passingTests: 0,
      };
    }
  },

  // Asegura que el código de tests tenga todas las funciones auxiliares necesarias
  ensureTestHelpers(testCode) {
    // Si ya incluye las funciones auxiliares, no hacer nada
    if (
      testCode.includes("def ejecutar_tests_avanzados") ||
      testCode.includes("def test(") ||
      testCode.includes("function ejecutar_tests_avanzados")
    ) {
      return testCode;
    }

    // Funciones auxiliares estándar para tests
    const helpers = `
# Funciones auxiliares para tests
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

    // Unir las funciones auxiliares con el código de tests
    return helpers + "\n\n" + testCode;
  },
};

export default judgeService;
