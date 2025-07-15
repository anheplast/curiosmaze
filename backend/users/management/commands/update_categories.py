# curiosmaze_backend/users/management/commands/update_categories.py

from django.core.management.base import BaseCommand
from users.models import UserProfile
from django.db import transaction

class Command(BaseCommand):
    help = "Asigna la categoría 'Tecnología Educativa' a todos los usuarios"

    def handle(self, *args, **kwargs):
        self.stdout.write("Iniciando actualización de categorías de usuarios...")
        
        # Contar usuarios
        total_users = UserProfile.objects.count()
        self.stdout.write(f"Total de usuarios encontrados: {total_users}")
        
        # Actualizar categorías
        with transaction.atomic():
            updated = UserProfile.objects.update(categoria='tecnologia_educativa')
            
        self.stdout.write(self.style.SUCCESS(f"Actualización completada: {updated} perfiles actualizados."))
        
        # Verificar actualización
        tech_edu_count = UserProfile.objects.filter(categoria='tecnologia_educativa').count()
        self.stdout.write(f"Usuarios con categoría 'Tecnología Educativa': {tech_edu_count}")
        
        if tech_edu_count != total_users:
            self.stdout.write(self.style.WARNING(
                f"ADVERTENCIA: Hay {total_users - tech_edu_count} usuarios que no fueron actualizados."
            ))
        else:
            self.stdout.write(self.style.SUCCESS(
                "Todos los usuarios tienen ahora la categoría 'Tecnología Educativa'."
            ))