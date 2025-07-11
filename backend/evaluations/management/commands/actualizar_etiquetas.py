import json
from django.core.management.base import BaseCommand
from evaluations.models import Ejercicio

class Command(BaseCommand):
    help = (
        "Asegura que todos los ejercicios tengan el campo 'etiquetas' "
        "en su JSON de contenido, añadiéndolo vacío si falta."
    )

    def handle(self, *args, **options):
        ejercicios = Ejercicio.objects.all()
        total = ejercicios.count()
        actualizados = 0

        self.stdout.write(f"Actualizando {total} ejercicios...")

        for ejercicio in ejercicios:
            contenido = ejercicio.contenido or {}

            # Si el contenido está serializado como string JSON, parsearlo
            if isinstance(contenido, str):
                try:
                    contenido = json.loads(contenido)
                except json.JSONDecodeError:
                    self.stderr.write(
                        f"⚠️  Ejercicio {ejercicio.id}: JSON inválido, se reinicializa a {{}}"
                    )
                    contenido = {}

            # Asegurarnos de que sea un dict
            if not isinstance(contenido, dict):
                contenido = {}

            # Añadir 'etiquetas' si no existe
            if 'etiquetas' not in contenido:
                contenido['etiquetas'] = []
                ejercicio.contenido = contenido
                ejercicio.save(update_fields=['contenido'])
                actualizados += 1
                self.stdout.write(f"✔️  Ejercicio {ejercicio.id} actualizado.")

        self.stdout.write(self.style.SUCCESS(
            f"Proceso completo: {actualizados} de {total} ejercicios actualizados."
        ))
