# manage_students/management/commands/assign_students.py

from django.core.management.base import BaseCommand
from django.db import transaction
from users.models import UserProfile
from manage_students.models import Estudiante, DocenteEstudiante

class Command(BaseCommand):
    help = 'Asigna todos los estudiantes a todos los docentes.'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            dest='dry_run',
            help='Ejecutar en modo simulación sin realizar cambios',
        )
    
    def handle(self, *args, **options):
        dry_run = options['dry_run']
        
        self.stdout.write(self.style.SUCCESS("Iniciando asignación de estudiantes a docentes..."))
        
        # Obtener todos los docentes
        docentes = UserProfile.objects.filter(rol='docente')
        docentes_count = docentes.count()
        self.stdout.write(f"Encontrados {docentes_count} docentes")
        
        # Obtener todos los estudiantes
        estudiantes_profiles = UserProfile.objects.filter(rol='estudiante')
        estudiantes_count = estudiantes_profiles.count()
        self.stdout.write(f"Encontrados {estudiantes_count} estudiantes")
        
        # Contar asignaciones existentes
        asignaciones_previas = DocenteEstudiante.objects.count()
        self.stdout.write(f"Asignaciones existentes antes del proceso: {asignaciones_previas}")
        
        # Mostrar aviso si estamos en modo simulación
        if dry_run:
            self.stdout.write(self.style.WARNING("MODO SIMULACIÓN: No se realizarán cambios en la base de datos"))
        
        # Nuevas asignaciones
        nuevas_asignaciones = 0
        
        # Transacción para evitar problemas si algo falla
        try:
            with transaction.atomic():
                for perfil_docente in docentes:
                    docente = perfil_docente.user
                    self.stdout.write(f"Procesando docente: {perfil_docente.nombres} {perfil_docente.apellidos}")
                    
                    for perfil_estudiante in estudiantes_profiles:
                        # Obtener o crear el registro de estudiante
                        estudiante, created = Estudiante.objects.get_or_create(user=perfil_estudiante.user)
                        
                        # Verificar si ya existe la asignación
                        asignacion_existente = DocenteEstudiante.objects.filter(
                            docente=docente,
                            estudiante=estudiante
                        ).exists()
                        
                        # Si no existe, crearla
                        if not asignacion_existente:
                            if not dry_run:
                                DocenteEstudiante.objects.create(
                                    docente=docente,
                                    estudiante=estudiante
                                )
                            nuevas_asignaciones += 1
                
                # Si estamos en modo simulación, hacer rollback
                if dry_run:
                    transaction.set_rollback(True)
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"Error durante el proceso: {str(e)}"))
            return
        
        # Contar asignaciones totales después del proceso
        if not dry_run:
            asignaciones_totales = DocenteEstudiante.objects.count()
            self.stdout.write(self.style.SUCCESS(f"Asignaciones nuevas creadas: {nuevas_asignaciones}"))
            self.stdout.write(self.style.SUCCESS(f"Total de asignaciones después del proceso: {asignaciones_totales}"))
            self.stdout.write(self.style.SUCCESS("Proceso completado con éxito."))
        else:
            self.stdout.write(self.style.SUCCESS(f"Simulación completada. Se crearían {nuevas_asignaciones} nuevas asignaciones."))
            self.stdout.write(self.style.SUCCESS(f"Total de asignaciones después del proceso (simulado): {asignaciones_previas + nuevas_asignaciones}"))