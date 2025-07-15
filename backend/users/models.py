# backend/users/models.py

from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin



class UserManager(BaseUserManager):
    def create_user(self, username, email, password=None, **extra_fields):
        if not username:
            raise ValueError('El número de identificación es obligatorio')
        if not email:
            raise ValueError('El correo electrónico es obligatorio')
        
        email = self.normalize_email(email)
        user = self.model(username=username, email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, username, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        
        if extra_fields.get('is_staff') is not True:
            raise ValueError('El superusuario debe tener is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('El superusuario debe tener is_superuser=True.')
        
        return self.create_user(username, email, password, **extra_fields)


class User(AbstractBaseUser, PermissionsMixin):
    username = models.CharField(max_length=50, unique=True, verbose_name="Número de identificación")
    email = models.EmailField(unique=True, verbose_name="Correo electrónico")
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    date_joined = models.DateTimeField(auto_now_add=True)
    
    objects = UserManager()
    
    USERNAME_FIELD = 'username'  # Usamos el número de identificación como campo de inicio de sesión
    REQUIRED_FIELDS = ['email']
    
    def __str__(self):
        return self.username
    
    class Meta:
        verbose_name = "Usuario"
        verbose_name_plural = "Usuarios"






class UserProfile(models.Model):
    ROLE_CHOICES = (
        ('estudiante', 'Estudiante'),
        ('docente', 'Docente'),
        ('admin', 'Administrador'),
    )
    
    GENDER_CHOICES = (
        ('masculino', 'Masculino'),
        ('femenino', 'Femenino'),
        ('otro', 'Otro'),
    )
    
    TURNO_CHOICES = (
        ('mañana', 'Mañana'),
        ('tarde', 'Tarde'),
    )
    
    ESTADO_CHOICES = (
        ('pendiente', 'Pendiente'),
        ('activo', 'Activo'),
        ('rechazado', 'Rechazado'),
    )
    
    # Añadir opciones de categoría, con Tecnología Educativa como valor por defecto
    CATEGORIA_CHOICES = (
        ('tecnologia_educativa', 'Tecnología Educativa'),
        ('ciencias', 'Ciencias'),
        ('humanidades', 'Humanidades'),
        ('arte', 'Arte y Cultura'),
        ('otros', 'Otros'),
    )
    
    

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    rol = models.CharField(max_length=20, choices=ROLE_CHOICES, default='estudiante')
    nombres = models.CharField(max_length=100)
    apellidos = models.CharField(max_length=100)
    edad = models.PositiveIntegerField(blank=True, null=True)
    genero = models.CharField(max_length=10, choices=GENDER_CHOICES, blank=True, null=True)
    fecha_nacimiento = models.DateField(blank=True, null=True)
    identificacion = models.CharField(max_length=20, unique=True)
    turno = models.CharField(max_length=10, choices=TURNO_CHOICES, blank=True, null=True)
    
    # Campos específicos de estudiante
    curso = models.CharField(max_length=10, blank=True, null=True)
    paralelo = models.CharField(max_length=5, blank=True, null=True)
    
    # Campos específicos de docente
    especializacion = models.CharField(max_length=50, blank=True, null=True)
    
    # Nuevo campo de categoría
    categoria = models.CharField(
        max_length=30, 
        choices=CATEGORIA_CHOICES, 
        default='tecnologia_educativa',
        help_text='Categoría general de educación'
    )

    
    # Campos para el estado del usuario
    estado = models.CharField(max_length=20, choices=ESTADO_CHOICES, default='pendiente')
    motivo_rechazo = models.TextField(blank=True, null=True)
    fecha_aprobacion = models.DateTimeField(blank=True, null=True)
    
    
    # Campos para la gestión de contraseñas
    requiere_cambio_clave = models.BooleanField(default=False)
    codigo_recuperacion = models.CharField(max_length=32, blank=True, null=True)
    codigo_expiracion = models.DateTimeField(blank=True, null=True)
    
    
    def __str__(self):
        return f"{self.nombres} {self.apellidos}"
    
    
    class Meta:
        verbose_name = "Perfil de Usuario"
        verbose_name_plural = "Perfiles de Usuario"
        
@receiver(post_save, sender=User)
def create_or_update_user_profile(sender, instance, created, **kwargs):
    """
    Crear o actualizar el perfil del usuario automáticamente.
    """
    if created and instance.is_superuser:
        # Si es un superusuario nuevo, crear un perfil de administrador
        UserProfile.objects.create(
            user=instance,
            rol='admin',
            nombres=instance.username,
            apellidos='Admin',
            identificacion=instance.username
        )


