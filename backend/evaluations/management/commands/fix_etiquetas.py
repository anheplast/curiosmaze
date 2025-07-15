from django.core.management.base import BaseCommand
from evaluations.models import Ejercicio
import json

class Command(BaseCommand):
    help = 'Diagnostica y repara etiquetas en ejercicios'

    def handle(self, *args, **options):
        # Obtener todos los ejercicios
        ejercicios = Ejercicio.objects.all()
        self.stdout.write(f"Analizando {ejercicios.count()} ejercicios...")
        
        ejercicios_con_etiquetas = 0
        ejercicios_sin_etiquetas = 0
        ejercicios_reparados = 0
        
        for ejercicio in ejercicios:
            # Verificar si el contenido tiene etiquetas
            etiquetas = []
            contenido = None
            
            # Intentar obtener contenido
            if ejercicio.contenido:
                if isinstance(ejercicio.contenido, str):
                    try:
                        contenido = json.loads(ejercicio.contenido)
                    except:
                        contenido = {}
                else:
                    contenido = ejercicio.contenido
            else:
                contenido = {}
            
            # Verificar etiquetas en contenido
            if isinstance(contenido, dict) and 'etiquetas' in contenido:
                etiquetas = contenido['etiquetas']
                if isinstance(etiquetas, list) and etiquetas:
                    ejercicios_con_etiquetas += 1
                    self.stdout.write(self.style.SUCCESS(
                        f"ID {ejercicio.id} - '{ejercicio.titulo}' tiene etiquetas: {etiquetas}"
                    ))
                else:
                    ejercicios_sin_etiquetas += 1
                    self.stdout.write(self.style.WARNING(
                        f"ID {ejercicio.id} - '{ejercicio.titulo}' tiene etiquetas mal formateadas"
                    ))
            else:
                ejercicios_sin_etiquetas += 1
                self.stdout.write(self.style.WARNING(
                    f"ID {ejercicio.id} - '{ejercicio.titulo}' no tiene etiquetas"
                ))
                
                # Intentar reparar este ejercicio
                if self.reparar_ejercicio(ejercicio):
                    ejercicios_reparados += 1
        
        self.stdout.write("\nRESUMEN:")
        self.stdout.write(f"Total de ejercicios: {ejercicios.count()}")
        self.stdout.write(f"Ejercicios con etiquetas: {ejercicios_con_etiquetas}")
        self.stdout.write(f"Ejercicios sin etiquetas: {ejercicios_sin_etiquetas}")
        self.stdout.write(f"Ejercicios reparados: {ejercicios_reparados}")
    
    def reparar_ejercicio(self, ejercicio):
        """Intenta reparar un ejercicio sin etiquetas"""
        # Este es un lugar para implementar lógica de reparación
        # Por ejemplo, podríamos extraer palabras clave del título/descripción
        # o usar una lista predeterminada basada en el tipo de ejercicio
        
        # Implementación básica: agregar etiquetas genéricas basadas en dificultad y tipo
        try:
            contenido = ejercicio.contenido
            if isinstance(contenido, str):
                try:
                    contenido = json.loads(contenido)
                except:
                    contenido = {}
            else:
                contenido = contenido or {}
            
            # Crear contenido si no existe
            if not isinstance(contenido, dict):
                contenido = {}
            
            # Generar etiquetas básicas
            etiquetas = []
            if ejercicio.tipo:
                etiquetas.append(ejercicio.tipo.lower())
            if ejercicio.dificultad:
                etiquetas.append(ejercicio.dificultad.lower())
            
            # Palabras clave básicas
            palabras_clave = ['algoritmo', 'programación', 'python', 'ejercicio']
            etiquetas.extend(palabras_clave)
            
            # Guardar las etiquetas en contenido
            contenido['etiquetas'] = etiquetas
            ejercicio.contenido = contenido
            ejercicio.save()
            
            self.stdout.write(self.style.SUCCESS(
                f"  ✓ Reparado ejercicio ID {ejercicio.id} con etiquetas: {etiquetas}"
            ))
            
            return True
        except Exception as e:
            self.stdout.write(self.style.ERROR(
                f"  ✗ Error al reparar ejercicio ID {ejercicio.id}: {str(e)}"
            ))
            return False