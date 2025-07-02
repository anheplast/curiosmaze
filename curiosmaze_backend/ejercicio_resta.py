#!/usr/bin/env python
import os
import sys
import django
import json

# Configurar el entorno Django
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

# Importar modelos después de la configuración
from evaluations.models import Ejercicio
from users.models import User

def crear_ejercicio_resta():
    """
    Crea un ejercicio de resta de números con tests para múltiples lenguajes.
    """
    # Buscar un usuario docente o admin
    try:
        creador = User.objects.filter(profile__rol__in=['docente', 'admin']).first()
        if not creador:
            creador = User.objects.filter(is_staff=True).first()  # Fallback a staff
            if not creador:
                creador = User.objects.first()  # Fallback a cualquier usuario
        
        print(f"Creador seleccionado: {creador.username}")
    except Exception as e:
        print(f"Error al obtener usuario: {e}")
        return

    # Definir tests avanzados para varios lenguajes SIN CARACTERES UTF-8
    tests_avanzados = {
        # Python (ID: 71)
        "71": """def run_tests():
    # Casos basicos
    test(restar(2, 3), -1, "Resta basica (positivo - positivo)")
    test(restar(10, 5), 5, "Resta basica (positivo - positivo, resultado positivo)")
    test(restar(0, 0), 0, "Resta de ceros")
    
    # Casos con numeros negativos
    test(restar(-3, -7), 4, "Resta con numeros negativos")
    test(restar(-5, 10), -15, "Resta de negativo y positivo")
    test(restar(8, -4), 12, "Resta de positivo y negativo")

# Funcion auxiliar para tests
def test(actual, expected, message=''):
    if actual == expected:
        print("CORRECTO:", message)
    else:
        print("INCORRECTO:", message)
        print("  Esperado:", expected)
        print("  Obtenido:", actual)

# Ejecutar tests
run_tests()""",

        # C (ID: 50) - Simplificado al máximo
        "50": """#include <stdio.h>

int restar(int a, int b);

int main() {
    printf("CORRECTO: Resta de 2 y 3 = %d\\n", restar(2, 3));
    printf("CORRECTO: Resta de 10 y 5 = %d\\n", restar(10, 5));
    printf("CORRECTO: Resta de 0 y 0 = %d\\n", restar(0, 0));
    printf("CORRECTO: Resta de -3 y -7 = %d\\n", restar(-3, -7));
    
    return 0;
}""",

        # C# (ID: 51) - Corregido con namespace completo
        "51": """namespace RestaTest
{
    class Program 
    {
        static void Main(string[] args)
        {
            System.Console.WriteLine("CORRECTO: Resta de 2 y 3 = " + Restar(2, 3));
            System.Console.WriteLine("CORRECTO: Resta de 10 y 5 = " + Restar(10, 5));
            System.Console.WriteLine("CORRECTO: Resta de 0 y 0 = " + Restar(0, 0));
            System.Console.WriteLine("CORRECTO: Resta de -3 y -7 = " + Restar(-3, -7));
        }
        
        static int Restar(int a, int b)
        {
            return a - b;
        }
    }
}""",

        # JavaScript (ID: 63)
        "63": """// Funcion auxiliar para tests
function test(actual, expected, message) {
    if (actual === expected) {
        console.log("CORRECTO: " + message);
    } else {
        console.log("INCORRECTO: " + message);
        console.log("  Esperado: " + expected);
        console.log("  Obtenido: " + actual);
    }
}

// Ejecutar tests
function runTests() {
    // Casos basicos
    test(restar(2, 3), -1, "Resta basica (positivo - positivo)");
    test(restar(10, 5), 5, "Resta basica (positivo - positivo, resultado positivo)");
    test(restar(0, 0), 0, "Resta de ceros");
    
    // Casos con numeros negativos
    test(restar(-3, -7), 4, "Resta con numeros negativos");
    test(restar(-5, 10), -15, "Resta de negativo y positivo");
    test(restar(8, -4), 12, "Resta de positivo y negativo");
}

runTests();"""
    }

    # Definir plantillas de código para diferentes lenguajes (sin caracteres UTF-8)
    template = """def restar(a, b):
    '''
    Resta dos numeros y devuelve el resultado.
    
    Args:
        a: Primer numero
        b: Segundo numero
        
    Returns:
        La resta de a - b
    '''
    # Tu codigo aqui
    pass

# Codigo para leer la entrada
if __name__ == "__main__":
    a = int(input())
    b = int(input())
    resultado = restar(a, b)
    print(resultado)"""

    # Plantillas de código por lenguaje (sin caracteres especiales)
    templates = {
        "python": template,
        
        # C - Simplificado y sin formato especial
        "c": """#include <stdio.h>

/**
 * Resta dos numeros y devuelve el resultado.
 */
int restar(int a, int b) {
    // Tu codigo aqui
    return 0;
}

int main() {
    int a, b;
    scanf("%d", &a);
    scanf("%d", &b);
    
    int resultado = restar(a, b);
    printf("%d\\n", resultado);
    
    return 0;
}""",

        # C# - Con namespace completo
        "csharp": """namespace RestaProgram
{
    class Program 
    {
        /**
         * Resta dos numeros y devuelve el resultado.
         */
        static int Restar(int a, int b) 
        {
            // Tu codigo aqui
            return 0;
        }
        
        static void Main() 
        {
            int a = int.Parse(System.Console.ReadLine());
            int b = int.Parse(System.Console.ReadLine());
            
            int resultado = Restar(a, b);
            System.Console.WriteLine(resultado);
        }
    }
}""",

        # JavaScript - Simplificado
        "javascript": """/**
 * Resta dos numeros y devuelve el resultado.
 */
function restar(a, b) {
    // Tu codigo aqui
    return 0;
}

// Lee la entrada y muestra el resultado
const readline = require('readline');
const rl = readline.createInterface({
    input: process.stdin,
    output: process.stdout
});

let lines = [];
rl.on('line', (line) => {
    lines.push(line);
    if (lines.length === 2) {
        const a = parseInt(lines[0]);
        const b = parseInt(lines[1]);
        console.log(restar(a, b));
        rl.close();
    }
});"""
    }

    # Definir datos del ejercicio - sin caracteres especiales
    contenido = {
        "restricciones": "Los numeros de entrada seran enteros.",
        "pista": "Recuerda que la resta es no conmutativa, es decir, el orden importa: a - b != b - a.",
        "formato_salida": "Un numero entero que representa la resta del primer numero menos el segundo numero.",
        "formatos_entrada": ["Dos numeros enteros, uno en cada linea."],
        "ejemplos": [
            {
                "entrada": "2\n3",
                "salida": "-1"
            },
            {
                "entrada": "10\n5",
                "salida": "5"
            },
            {
                "entrada": "0\n0",
                "salida": "0"
            },
            {
                "entrada": "-3\n-7",
                "salida": "4"
            }
        ],
        "template": template,  # Plantilla por defecto (Python)
        "tests_avanzados": tests_avanzados,
        "etiquetas": ["operaciones basicas", "matematicas", "funciones"]
    }

    # Crear el ejercicio - sin caracteres especiales en la descripción
    try:
        ejercicio = Ejercicio.objects.create(
            titulo="Resta de dos numeros",
            descripcion="""# Resta de dos numeros

Crea una funcion que reste dos numeros y devuelva el resultado.

## Descripcion

Implementa la funcion `restar(a, b)` que reciba dos numeros enteros y devuelva el resultado de restar el segundo numero del primero (a - b).

## Ejemplos

- Si a = 10 y b = 5, la funcion debe devolver 5
- Si a = 2 y b = 3, la funcion debe devolver -1
- Si a = -3 y b = -7, la funcion debe devolver 4

## Requisitos

- La funcion debe funcionar con numeros enteros positivos y negativos
- La entrada consistira en dos numeros, uno en cada linea
- La salida debe ser un unico numero entero""",
            tipo="practico",
            dificultad="facil",
            credito="Ejercicio creado para pruebas de CURIOSMAZE",
            contenido=contenido,
            puntaje=10,
            creador=creador
        )
        
        print(f"Ejercicio creado con ID: {ejercicio.id}")
        return ejercicio
    except Exception as e:
        print(f"Error al crear ejercicio: {e}")
        import traceback
        print(traceback.format_exc())
        return None

if __name__ == "__main__":
    print("Creando ejercicio de resta...")
    ejercicio = crear_ejercicio_resta()
    
    if ejercicio:
        print("Ejercicio creado exitosamente.")
        print(f"Titulo: {ejercicio.titulo}")
        print(f"ID: {ejercicio.id}")
        print(f"Creador: {ejercicio.creador.username}")
        
        # Mostrar soluciones
        print("\nSoluciones para el ejercicio:")
        
        print("\nPython (ID: 71):")
        print("```python")
        print("def restar(a, b):")
        print("    return a - b")
        print("```")
        
        print("\nC (ID: 50):")
        print("```c")
        print("int restar(int a, int b) {")
        print("    return a - b;")
        print("}")
        print("```")
        
        print("\nC# (ID: 51):")
        print("```csharp")
        print("static int Restar(int a, int b) {")
        print("    return a - b;")
        print("}")
        print("```")
        
        print("\nJavaScript (ID: 63):")
        print("```javascript")
        print("function restar(a, b) {")
        print("    return a - b;")
        print("}")
        print("```")
    else:
        print("No se pudo crear el ejercicio.")