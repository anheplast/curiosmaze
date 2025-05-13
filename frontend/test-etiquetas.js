async function testEtiquetas() {
    console.log("PRUEBA COMPLETA DE ETIQUETAS");
    console.log("============================");
    
    // Obtener URL base del API desde el entorno
    // Esta es la forma correcta de acceder a la URL del API configurada en tu aplicación
    const API_URL = window.axiosInstance?.defaults?.baseURL || 
                    import.meta?.env?.VITE_API_URL;
    
    console.log("URL del API:", API_URL);
    
    // 1. Crear un ejercicio con etiquetas
    console.log("\n1. Creando ejercicio con etiquetas...");
    
    const ejercicioData = {
      titulo: "Ejercicio de prueba con etiquetas",
      descripcion: "Este es un ejercicio para probar las etiquetas",
      puntaje: 30,
      tipo: "practico",
      dificultad: "facil",
      credito: "Test de etiquetas",
      contenido: {
        restricciones: "Sin restricciones",
        formato_salida: "Texto",
        formatos_entrada: ["Texto de entrada"],
        ejemplos: [{
          entrada: "test",
          salida: "test",
          explicacion: "Test"
        }],
        template: "print('Hola mundo')",
        etiquetas: ["prueba1", "test1", "etiquetas1"]
      },
      etiquetas: ["prueba1", "test1", "etiquetas1"]
    };
    
    // Obtener token
    const token = localStorage.getItem('token');
    if (!token) {
      console.error("No hay token de autenticación");
      return;
    }
    
    try {
      // Crear ejercicio
      console.log(`Haciendo petición POST a ${API_URL}/ejercicios/`);
      const createResponse = await fetch(`${API_URL}/ejercicios/`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify(ejercicioData)
      });
      
      if (!createResponse.ok) {
        const errorText = await createResponse.text();
        throw new Error(`Error al crear ejercicio: ${createResponse.status} - ${errorText}`);
      }
      
      const createdExercise = await createResponse.json();
      console.log("✓ Ejercicio creado:", createdExercise);
      
      // 2. Obtener el ejercicio para verificar etiquetas
      console.log("\n2. Verificando ejercicio creado...");
      
      const getResponse = await fetch(`${API_URL}/ejercicios/${createdExercise.id}/`, {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });
      
      if (!getResponse.ok) {
        throw new Error(`Error al obtener ejercicio: ${getResponse.status}`);
      }
      
      const retrievedExercise = await getResponse.json();
      console.log("✓ Ejercicio obtenido:", retrievedExercise);
      
      // Verificar etiquetas
      console.log("\n3. Verificando etiquetas...");
      
      if (retrievedExercise.etiquetas && Array.isArray(retrievedExercise.etiquetas)) {
        console.log("✓ Etiquetas encontradas:", retrievedExercise.etiquetas);
      } else {
        console.error("✗ No se encontraron etiquetas en el campo 'etiquetas'");
      }
      
      if (retrievedExercise.contenido) {
        let contenido;
        if (typeof retrievedExercise.contenido === 'string') {
          try {
            contenido = JSON.parse(retrievedExercise.contenido);
          } catch (e) {
            console.error("Error al parsear contenido:", e);
            contenido = null;
          }
        } else {
          contenido = retrievedExercise.contenido;
        }
        
        if (contenido && contenido.etiquetas && Array.isArray(contenido.etiquetas)) {
          console.log("✓ Etiquetas encontradas en contenido:", contenido.etiquetas);
        } else {
          console.error("✗ No se encontraron etiquetas en el contenido");
        }
      }
      
      // 3. Añadir ejercicio a una evaluación
      console.log("\n4. Añadiendo ejercicio a una evaluación...");
      
      // Primero obtener evaluaciones existentes
      const evaluacionesResponse = await fetch(`${API_URL}/evaluaciones/`, {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });
      
      if (!evaluacionesResponse.ok) {
        throw new Error(`Error al obtener evaluaciones: ${evaluacionesResponse.status}`);
      }
      
      const evaluaciones = await evaluacionesResponse.json();
      
      if (evaluaciones && evaluaciones.length > 0) {
        const evaluacion = evaluaciones[0];
        console.log(`Usando evaluación: ${evaluacion.titulo} (ID: ${evaluacion.id})`);
        
        // Añadir ejercicio a evaluación
        const updateEvalResponse = await fetch(`${API_URL}/evaluaciones/${evaluacion.id}/`, {
          method: 'PUT',
          headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${token}`
          },
          body: JSON.stringify({
            ...evaluacion,
            ejercicios: [createdExercise.id]
          })
        });
        
        if (!updateEvalResponse.ok) {
          throw new Error(`Error al actualizar evaluación: ${updateEvalResponse.status}`);
        }
        
        console.log("✓ Ejercicio añadido a evaluación");
        
        // 4. Obtener detalles de evaluación para verificar etiquetas
        console.log("\n5. Verificando etiquetas en detalles de evaluación...");
        
        const detallesResponse = await fetch(`${API_URL}/evaluaciones/${evaluacion.id}/detalles/`, {
          headers: {
            'Authorization': `Bearer ${token}`
          }
        });
        
        if (!detallesResponse.ok) {
          throw new Error(`Error al obtener detalles: ${detallesResponse.status}`);
        }
        
        const detalles = await detallesResponse.json();
        console.log("Detalles de evaluación:", detalles);
        
        if (detalles.ejercicios && detalles.ejercicios.length > 0) {
          const ejercicioDetalle = detalles.ejercicios.find(e => e.id === createdExercise.id);
          
          if (ejercicioDetalle) {
            console.log("Ejercicio encontrado en detalles:", ejercicioDetalle);
            
            if (ejercicioDetalle.etiquetas && Array.isArray(ejercicioDetalle.etiquetas)) {
              console.log("✓ Etiquetas encontradas en detalles:", ejercicioDetalle.etiquetas);
            } else {
              console.error("✗ No se encontraron etiquetas en detalles");
            }
          } else {
            console.error("✗ No se encontró el ejercicio en los detalles");
          }
        } else {
          console.error("✗ No hay ejercicios en los detalles");
        }
      } else {
        console.error("✗ No hay evaluaciones disponibles para probar");
      }
      
      console.log("\nPRUEBA COMPLETA FINALIZADA");
      
    } catch (error) {
      console.error("Error en la prueba:", error);
    }
  }

testEtiquetas();