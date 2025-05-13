import os
import django
import sys
from django.utils import timezone

# Configurar entorno Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

# Importar modelos después de configurar Django
from django.contrib.auth import get_user_model
from users.models import UserProfile

User = get_user_model()

def create_admin_user(username, email, password, nombres=None, apellidos=None):
    """
    Crear un superusuario con perfil de administrador.
    
    Args:
        username (str): Nombre de usuario / identificación
        email (str): Correo electrónico
        password (str): Contraseña
        nombres (str, optional): Nombres del administrador
        apellidos (str, optional): Apellidos del administrador
    
    Returns:
        User: Objeto de usuario creado o None si ya existe
    """
    try:
        # Comprobar si el usuario ya existe
        if User.objects.filter(username=username).exists():
            print(f"El usuario {username} ya existe.")
            user = User.objects.get(username=username)
            
            # Verificar si ya tiene perfil de admin
            try:
                profile = UserProfile.objects.get(user=user)
                if profile.rol != 'admin':
                    print(f"El usuario existe pero no es administrador. Rol actual: {profile.rol}")
                    # Actualizar a admin si se desea
                    if input("¿Desea convertirlo en administrador? (s/n): ").lower() == 's':
                        profile.rol = 'admin'
                        profile.estado = 'activo'
                        profile.fecha_aprobacion = timezone.now()
                        profile.save()
                        print(f"Usuario {username} actualizado a administrador.")
                else:
                    print(f"El usuario ya es administrador.")
                return user
            except UserProfile.DoesNotExist:
                # Crear perfil admin si no existe
                UserProfile.objects.create(
                    user=user,
                    rol='admin',
                    nombres=nombres or username,
                    apellidos=apellidos or 'Admin',
                    identificacion=username,
                    estado='activo',
                    fecha_aprobacion=timezone.now(),
                    categoria='tecnologia_educativa'
                )
                print(f"Perfil de administrador creado para usuario existente {username}.")
                return user
        
        # Valores por defecto
        nombres = nombres or username
        apellidos = apellidos or 'Admin'
        
        print(f"Creando nuevo superusuario: {username}")
        
        # Crear superusuario
        user = User.objects.create_superuser(
            username=username,
            email=email,
            password=password
        )
        
        # El perfil podría ser creado automáticamente por la señal post_save,
        # pero lo creamos manualmente para asegurar todos los campos
        try:
            # Crear perfil de administrador más completo
            UserProfile.objects.create(
                user=user,
                rol='admin',
                nombres=nombres,
                apellidos=apellidos,
                identificacion=username,
                estado='activo',  # Admins siempre activos
                fecha_aprobacion=timezone.now(),
                categoria='tecnologia_educativa',
                requiere_cambio_clave=False
            )
            print(f"Perfil de administrador creado exitosamente para {nombres} {apellidos}.")
        except Exception as profile_error:
            print(f"Error al crear perfil: {profile_error}")
            # Si falla la creación del perfil, verificar si fue creado por la señal
            if not hasattr(user, 'profile'):
                print("Error crítico: No se pudo crear el perfil de administrador.")
                user.delete()
                return None
        
        print(f"Superusuario {username} creado con éxito con rol de administrador.")
        return user
    except Exception as e:
        print(f"Error al crear superusuario: {e}")
        return None

if __name__ == '__main__':
    print("=== Creación de Superusuario Administrador CURIOSMAZE ===")
    
    # Solicitar datos con validación
    while True:
        admin_username = input("Nombre de usuario / Identificación: ")
        if admin_username:
            break
        print("El nombre de usuario no puede estar vacío.")
    
    while True:
        admin_email = input("Correo electrónico: ")
        if '@' in admin_email:
            break
        print("Por favor ingrese un correo electrónico válido.")
    
    while True:
        admin_password = input("Contraseña: ")
        if len(admin_password) >= 8:
            break
        print("La contraseña debe tener al menos 8 caracteres.")
    
    # Datos adicionales opcionales
    print("\nInformación adicional (opcional):")
    admin_nombres = input("Nombres (Enter para usar el nombre de usuario): ") or None
    admin_apellidos = input("Apellidos (Enter para usar 'Admin'): ") or None
    
    # Crear el usuario
    user = create_admin_user(
        admin_username, 
        admin_email, 
        admin_password,
        admin_nombres,
        admin_apellidos
    )
    
    if user:
        print("\n=== Superusuario creado exitosamente ===")
        print(f"Nombre de usuario: {user.username}")
        print(f"Correo electrónico: {user.email}")
        if hasattr(user, 'profile'):
            print(f"Rol: {user.profile.rol}")
            print(f"Nombre completo: {user.profile.nombres} {user.profile.apellidos}")
        print("\nPuede iniciar sesión en el sistema con estas credenciales.")
    else:
        print("\n❌ No se pudo crear el superusuario. Verifique los errores e intente nuevamente.")
        sys.exit(1)