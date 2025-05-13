import os
import django

# Configurar entorno Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

# Importar modelos después de configurar Django
from django.contrib.auth import get_user_model
from users.models import UserProfile

User = get_user_model()

def create_admin_user(username, email, password):
    """
    Crear un superusuario con perfil de administrador.
    """
    # Comprobar si el usuario ya existe
    if User.objects.filter(username=username).exists():
        print(f"El usuario {username} ya existe.")
        return None
    
    # Crear superusuario
    user = User.objects.create_superuser(
        username=username,
        email=email,
        password=password
    )
    
    # Comprobar si ya tiene un perfil
    if not hasattr(user, 'profile'):
        # Crear perfil de administrador
        UserProfile.objects.create(
            user=user,
            rol='admin',
            nombres=username,
            apellidos='Admin',
            identificacion=username
        )
    
    print(f"Superusuario {username} creado con éxito con rol de administrador.")
    return user

if __name__ == '__main__':
    # Puedes configurar estos valores o pedirlos como input
    admin_username = input("Nombre de usuario (ID): ")
    admin_email = input("Correo electrónico: ")
    admin_password = input("Contraseña: ")
    
    create_admin_user(admin_username, admin_email, admin_password)