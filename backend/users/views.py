# backend/users/views.py
from rest_framework import status, viewsets
from django.core.files.storage import default_storage
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.permissions import AllowAny, IsAuthenticated, IsAdminUser
from .permissions import IsAdmin, IsDocente, IsEstudiante
from django.contrib.auth import authenticate
from rest_framework_simplejwt.tokens import RefreshToken
from django.shortcuts import get_object_or_404
from django.middleware.csrf import get_token
from django.http import JsonResponse
from django.utils import timezone
import traceback
import json


from .models import User, UserProfile
from .serializers import UserSerializer, UserLoginSerializer


# Añadir esta vista para obtener un token CSRF
@api_view(['GET'])
@permission_classes([AllowAny])
def csrf_token_view(request):
    """
    Esta vista no hace nada más que devolver un token CSRF en una cookie,
    que el navegador puede usar para solicitudes POST subsiguientes.
    """
    # get_token fuerza la creación de un token CSRF en una cookie
    token = get_token(request)
    return JsonResponse({'detail': 'CSRF cookie set'})


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [AllowAny]  # Para registro público
    
    def get_permissions(self):
        if self.action == 'create':
            return [AllowAny()]
        return [IsAuthenticated()]



@api_view(['POST'])
@permission_classes([AllowAny])
def login_view(request):
    serializer = UserLoginSerializer(data=request.data)
    if not serializer.is_valid():
        return Response(
            {'error': 'Por favor, proporcione un ID de usuario y contraseña válidos'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    user_id = serializer.validated_data['userId']
    password = serializer.validated_data['password']
    
    try:
        # Buscar usuario por su número de identificación (username)
        user = User.objects.get(username=user_id)
        
        # Verificar la contraseña
        if not user.check_password(password):
            return Response(
                {'error': 'Credenciales inválidas. Por favor, intente nuevamente.'},
                status=status.HTTP_401_UNAUTHORIZED
            )
        
        if not user.is_active:
            return Response(
                {'error': 'Su cuenta no está activa. Por favor, contacte al administrador.'},
                status=status.HTTP_401_UNAUTHORIZED
            )
        
        # Valor por defecto para requiere_cambio_clave
        requiere_cambio_clave = False
        
        # Verificar estado del usuario
        try:
            profile = UserProfile.objects.get(user=user)
            
            # Verificar si se requiere cambio de contraseña
            requiere_cambio_clave = getattr(profile, 'requiere_cambio_clave', False)
            
            # Si el usuario es superusuario o admin, no verificar estado
            if not user.is_superuser and profile.rol != 'admin':
                if profile.estado == 'pendiente':
                    return Response(
                        {'error': 'Su solicitud de registro está pendiente de aprobación por un administrador.', 'estado': 'pendiente'},
                        status=status.HTTP_403_FORBIDDEN
                    )
                elif profile.estado == 'rechazado':
                    return Response(
                        {'error': 'Su solicitud de registro ha sido rechazada. Contacte al administrador para más información.', 'estado': 'rechazado'},
                        status=status.HTTP_403_FORBIDDEN
                    )
            
            rol = profile.rol
            nombres = profile.nombres
        except UserProfile.DoesNotExist:
            # Si no tiene perfil pero es superusuario, le damos rol de admin
            if user.is_superuser:
                rol = "admin"
                nombres = user.username
            else:
                rol = "sin_perfil"
                nombres = user.username
        
        # Generar token JWT
        refresh = RefreshToken.for_user(user)
        access_token = str(refresh.access_token)
        
        response_data = {
            'token': access_token,
            'user_id': user.id,
            'rol': rol,
            'nombres': nombres,
            'requiere_cambio_clave': requiere_cambio_clave  # Añadimos la bandera a la respuesta
        }
        
        print(f"Inicio de sesión exitoso: {response_data}")  # Para depuración
        
        return Response(response_data)
    
    except User.DoesNotExist:
        return Response(
            {'error': 'No existe un usuario con este ID. Por favor, verifique sus credenciales.'},
            status=status.HTTP_404_NOT_FOUND
        )
    except Exception as e:
        print(f"Error en login: {str(e)}")  # Para depuración
        return Response(
            {'error': 'Ha ocurrido un error. Por favor, intente más tarde.'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )



@api_view(['GET'])
@permission_classes([IsAuthenticated])
def user_profile_view(request):
    try:
        user = request.user
        profile = UserProfile.objects.get(user=user)
        
        return Response({
            'user_id': user.id,
            'username': user.username,
            'email': user.email,
            'rol': profile.rol,
            'nombres': profile.nombres,
            'apellidos': profile.apellidos,
            'identificacion': profile.identificacion,
            # Añadir otros campos según necesidad
        })
    except UserProfile.DoesNotExist:
        return Response(
            {'error': 'Perfil no encontrado'},
            status=status.HTTP_404_NOT_FOUND
        )
        

@api_view(['POST'])
@permission_classes([AllowAny])
def register_docente_view(request):
    """
    Endpoint específico para registrar docentes sin autenticación previa
    """
    try:
        # Asegurarse de que los datos incluyan el rol de docente
        data = request.data.copy()
        if 'profile' in data and isinstance(data['profile'], dict):
            data['profile']['rol'] = 'docente'
        
        serializer = UserSerializer(data=data)
        if serializer.is_valid():
            user = serializer.save()
            
            # Generar token JWT
            refresh = RefreshToken.for_user(user)
            access_token = str(refresh.access_token)
            
            # Obtener información del perfil
            profile = UserProfile.objects.get(user=user)
            
            response_data = {
                'token': access_token,
                'user_id': user.id,
                'rol': profile.rol,
                'nombres': profile.nombres
            }
            
            return Response(response_data, status=status.HTTP_201_CREATED)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    except Exception as e:
        print(f"Error en registro de docente: {str(e)}")  # Para depuración
        return Response(
            {'error': 'Ha ocurrido un error durante el registro. Por favor, intente nuevamente.'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['GET'])
@permission_classes([IsAuthenticated])  
def list_users_by_status(request, estado):
    """Endpoint para listar usuarios por estado (pendiente, activo, rechazado)"""
    # Verificar que el usuario es admin o docente
    try:
        user = request.user
        print(f"Usuario autenticado: {user.username} (ID: {user.id})")
        
        # Verificación más robusta para permitir acceso tanto a admins como a docentes
        if user.is_superuser:
            print("Usuario es superusuario, permitiendo acceso")
            is_authorized = True
        else:
            try:
                perfil = UserProfile.objects.get(user=user)
                print(f"Perfil obtenido: Rol={perfil.rol}")
                # IMPORTANTE: Aquí está el cambio para permitir a docentes
                is_authorized = perfil.rol == 'admin' or perfil.rol == 'docente'
            except UserProfile.DoesNotExist:
                print(f"Perfil no encontrado para usuario {user.username}")
                return Response(
                    {"error": "No se encontró un perfil para este usuario"},
                    status=status.HTTP_400_BAD_REQUEST
                )
        
        if not is_authorized:
            return Response(
                {"error": "No tiene permisos para acceder a esta información"},
                status=status.HTTP_403_FORBIDDEN
            )
        
        # Validar estado con mejor manejo de errores
        if estado not in ['pendiente', 'activo', 'rechazado', 'todos']:
            print(f"Estado inválido recibido: '{estado}'")
            return Response(
                {"error": f"Estado no válido: '{estado}'"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Consultar perfiles según el estado
        if estado == 'todos':
            perfiles = UserProfile.objects.all()
        else:
            perfiles = UserProfile.objects.filter(estado=estado)
        
        print(f"Perfiles encontrados con estado '{estado}': {perfiles.count()}")
        
        # Serializar y devolver datos
        usuarios = []
        for perfil in perfiles:
            print(f"Procesando perfil: {perfil.nombres} {perfil.apellidos} (estado: {perfil.estado})")
            usuarios.append({
                'id': perfil.user.id,
                'username': perfil.user.username,
                'email': perfil.user.email,
                'nombres': perfil.nombres,
                'apellidos': perfil.apellidos,
                'identificacion': perfil.identificacion,
                'rol': perfil.rol,
                'curso': perfil.curso,
                'paralelo': perfil.paralelo,
                'genero': perfil.genero,
                'edad': perfil.edad,
                'turno': perfil.turno,
                'especializacion': perfil.especializacion,
                'estado': perfil.estado,
                'fecha_registro': perfil.user.date_joined,
                'motivo_rechazo': perfil.motivo_rechazo
            })
        
        return Response(usuarios)
        
    except Exception as e:
        print(f"Error en list_users_by_status: {str(e)}")
        print(traceback.format_exc())
        return Response(
            {"error": f"Error al procesar la solicitud: {str(e)}"},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def update_user_status(request):
    """Endpoint para actualizar el estado de un usuario (aprobar/rechazar)"""
    # Verificar que el usuario es admin - implementación más robusta
    try:
        user = request.user
        print(f"Usuario autenticado: {user.username} (ID: {user.id})")
        
        # Verificar si es superusuario primero
        if user.is_superuser:
            print("El usuario es superusuario, permitiendo acceso")
            is_admin = True
        else:
            # Buscar el perfil explícitamente con una consulta
            try:
                perfil = UserProfile.objects.get(user=user)
                print(f"Perfil encontrado para usuario {user.username}: rol={perfil.rol}")
                is_admin = perfil.rol == 'admin'
            except UserProfile.DoesNotExist:
                print(f"No se encontró perfil para usuario {user.username}")
                # Si no tiene perfil pero es staff, también permitir
                is_admin = user.is_staff
                print(f"Usuario es staff: {is_admin}")
            except Exception as e:
                print(f"Error al buscar perfil: {str(e)}")
                is_admin = False
        
        if not is_admin:
            print(f"Usuario {user.username} no tiene permisos de administrador")
            return Response(
                {"error": "No tiene permisos para modificar usuarios"},
                status=status.HTTP_403_FORBIDDEN
            )
        
        # Validar datos
        user_id = request.data.get('user_id')
        nuevo_estado = request.data.get('estado')
        motivo_rechazo = request.data.get('motivo_rechazo', '')
        
        print(f"Datos recibidos: user_id={user_id}, nuevo_estado={nuevo_estado}, motivo_rechazo={motivo_rechazo}")
        
        if not user_id or not nuevo_estado:
            return Response(
                {"error": "Datos incompletos"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        if nuevo_estado not in ['pendiente', 'activo', 'rechazado']:
            return Response(
                {"error": "Estado no válido"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Actualizar estado del usuario
        try:
            target_user = User.objects.get(id=user_id)
            print(f"Usuario objetivo encontrado: {target_user.username}")
            
            perfil = UserProfile.objects.get(user=target_user)
            print(f"Perfil objetivo encontrado: {perfil.nombres} {perfil.apellidos}, estado actual: {perfil.estado}")
            
            # Guardar estado anterior para retornarlo
            estado_anterior = perfil.estado
            
            # Actualizar estado
            perfil.estado = nuevo_estado
            
            # Si se está aprobando, registrar fecha
            if nuevo_estado == 'activo':
                perfil.fecha_aprobacion = timezone.now()
                perfil.motivo_rechazo = None
                print(f"Aprobando usuario, fecha: {perfil.fecha_aprobacion}")
            
            # Si se está rechazando, registrar motivo
            if nuevo_estado == 'rechazado':
                perfil.motivo_rechazo = motivo_rechazo
                print(f"Rechazando usuario, motivo: {motivo_rechazo}")
            
            perfil.save()
            print(f"Perfil actualizado: {perfil.nombres} {perfil.apellidos}, nuevo estado: {perfil.estado}")
            
            return Response({
                'success': True,
                'message': f'Usuario {perfil.nombres} {perfil.apellidos} ahora está {nuevo_estado}',
                'usuario': {
                    'id': target_user.id,
                    'nombres': perfil.nombres,
                    'apellidos': perfil.apellidos,
                    'estado_anterior': estado_anterior,
                    'estado_nuevo': nuevo_estado
                }
            })
        
        except User.DoesNotExist:
            print(f"Error: Usuario con ID {user_id} no encontrado")
            return Response(
                {"error": "Usuario no encontrado"},
                status=status.HTTP_404_NOT_FOUND
            )
        except UserProfile.DoesNotExist:
            print(f"Error: Perfil para usuario con ID {user_id} no encontrado")
            return Response(
                {"error": "Perfil de usuario no encontrado"},
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            print(f"Error inesperado: {str(e)}")
            print(traceback.format_exc())
            return Response(
                {"error": f"Error: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    except Exception as e:
        print(f"Error general en update_user_status: {str(e)}")
        print(traceback.format_exc())
        return Response(
            {"error": f"Error del servidor: {str(e)}"},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )
        
        

# Vista de creación de usuario (admin)
@api_view(['POST'])
@permission_classes([IsAuthenticated, IsAdmin])
def create_user_view(request):
    try:
        # Obtener datos de la solicitud
        data = request.data
        
        # Log para depuración
        print(f"Datos recibidos en create_user_view: {data}")
        
        # Intentar obtener username desde diferentes campos posibles
        username = data.get('username') or data.get('identificacion')
        
        # Validar datos mínimos requeridos
        if not username or not data.get('nombres') or not data.get('apellidos'):
            return Response(
                {'error': 'Los campos username/identificacion, nombres y apellidos son obligatorios'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Crear usuario
        user_data = {
            'username': username,
            'email': data.get('email', f"{username}@example.com"),
            'password': data.get('password', username)  # Usar username como contraseña si no se proporciona
        }
        
        # Comprobar si ya existe un usuario con ese username
        if User.objects.filter(username=username).exists():
            return Response(
                {'error': f'Ya existe un usuario con el identificador {username}'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        user = User.objects.create_user(**user_data)
        
        # Obtener identificación desde diferentes fuentes posibles
        identificacion = data.get('identificacion') or username
        
        # Crear perfil
        profile_data = {
            'user': user,
            'rol': data.get('rol', 'estudiante'),
            'nombres': data.get('nombres'),
            'apellidos': data.get('apellidos'),
            'identificacion': identificacion,
            'estado': 'activo'  # Usuario creado por admin es activo por defecto
        }
        
        # Campos opcionales
        if 'genero' in data:
            profile_data['genero'] = data.get('genero')
        if 'edad' in data and data.get('edad'):
            try:
                profile_data['edad'] = int(data.get('edad'))
            except (ValueError, TypeError):
                pass  # Ignorar si no es un número válido
        if 'turno' in data:
            profile_data['turno'] = data.get('turno')
        
        # Campos específicos según rol
        if data.get('rol') == 'estudiante':
            if 'curso' in data:
                profile_data['curso'] = data.get('curso')
            if 'paralelo' in data:
                profile_data['paralelo'] = data.get('paralelo')
        elif data.get('rol') == 'docente':
            if 'especializacion' in data:
                profile_data['especializacion'] = data.get('especializacion')
        
        # Crear perfil
        profile = UserProfile.objects.create(**profile_data)
        
        # Preparar respuesta
        response_data = {
            'id': user.id,
            'username': user.username,
            'email': user.email,
            'rol': profile.rol,
            'nombres': profile.nombres,
            'apellidos': profile.apellidos,
            'mensaje': 'Usuario creado exitosamente'
        }
        
        return Response(response_data, status=status.HTTP_201_CREATED)
        
    except Exception as e:
        print(f"Error en create_user_view: {str(e)}")
        import traceback
        traceback.print_exc()
        return Response(
            {'error': f'Error al crear usuario: {str(e)}'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )
        
        

# Vista de actualización de usuario existente
@api_view(['PUT'])
@permission_classes([IsAuthenticated, IsAdmin])
def update_user_view(request, user_id):
    try:
        # Obtener el usuario que se va a actualizar
        user = get_object_or_404(User, id=user_id)
        
        # Obtener los datos de la solicitud
        data = request.data
        
        # Actualizar datos básicos del usuario
        if 'email' in data:
            user.email = data['email']
        
        # Actualizar contraseña si se proporciona
        if 'password' in data and data['password']:
            user.set_password(data['password'])
        
        # Guardar cambios en el usuario
        user.save()
        
        # Actualizar perfil del usuario
        try:
            profile = UserProfile.objects.get(user=user)
            
            # Actualizar campos del perfil
            if 'nombres' in data:
                profile.nombres = data['nombres']
            if 'apellidos' in data:
                profile.apellidos = data['apellidos']
            if 'genero' in data:
                profile.genero = data['genero']
            if 'edad' in data:
                profile.edad = data['edad']
            if 'curso' in data:
                profile.curso = data['curso']
            if 'paralelo' in data:
                profile.paralelo = data['paralelo']
            if 'turno' in data:
                profile.turno = data['turno']
            if 'especializacion' in data:
                profile.especializacion = data['especializacion']
            if 'rol' in data: 
                profile.rol = data['rol']
            
            # Guardar cambios en el perfil
            profile.save()
            
            # Construir respuesta
            response_data = {
                'id': user.id,
                'username': user.username,
                'email': user.email,
                'nombres': profile.nombres,
                'apellidos': profile.apellidos,
                'identificacion': profile.identificacion,
                'rol': profile.rol,
                'genero': profile.genero,
                'edad': profile.edad,
                'curso': profile.curso,
                'paralelo': profile.paralelo,
                'turno': profile.turno,
                'especializacion': profile.especializacion
            }
            
            return Response(response_data, status=status.HTTP_200_OK)
            
        except UserProfile.DoesNotExist:
            return Response(
                {'error': 'Perfil de usuario no encontrado'},
                status=status.HTTP_404_NOT_FOUND
            )
            
    except User.DoesNotExist:
        return Response(
            {'error': 'Usuario no encontrado'},
            status=status.HTTP_404_NOT_FOUND
        )
    except Exception as e:
        return Response(
            {'error': f'Error al actualizar usuario: {str(e)}'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )
        
        

# Vista de eliminación definitiva de usuario
@api_view(['DELETE'])
@permission_classes([IsAuthenticated, IsAdmin])
def delete_user_view(request, user_id):
    try:
        user = get_object_or_404(User, id=user_id)
        
        # Verificar que no se está eliminando a sí mismo
        if user == request.user:
            return Response(
                {"error": "No puedes eliminar tu propio usuario."},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # En lugar de eliminar, desactivar el usuario
        user.is_active = False
        user.save()
        
        # También actualizar el perfil
        try:
            profile = UserProfile.objects.get(user=user)
            profile.estado = 'inactivo'  # Si existe este campo
            profile.save()
        except UserProfile.DoesNotExist:
            pass
        
        return Response(
            {"message": f"Usuario {user_id} desactivado correctamente"},
            status=status.HTTP_200_OK
        )
    except Exception as e:
        return Response(
            {"error": f"Error al desactivar usuario: {str(e)}"},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

# Vista para resetear contraseña (por admin)
@api_view(['POST'])
@permission_classes([IsAuthenticated, IsAdmin])
def admin_reset_password_view(request):
    """
    Permite a un administrador resetear la contraseña de un usuario.
    Requiere la contraseña del administrador para verificación.
    """
    try:
        # Obtener datos de la solicitud
        data = request.data
        user_id = data.get('user_id')
        admin_password = data.get('admin_password')
        
        if not user_id or not admin_password:
            return Response(
                {'error': 'Se requiere ID de usuario y contraseña de administrador'},
                status=status.HTTP_400_BAD_REQUEST
            )
            
        # Verificar la contraseña del administrador
        admin_user = request.user
        if not admin_user.check_password(admin_password):
            return Response(
                {'error': 'Contraseña de administrador incorrecta'},
                status=status.HTTP_401_UNAUTHORIZED
            )
        
        # Obtener el usuario objetivo
        try:
            target_user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            return Response(
                {'error': 'Usuario no encontrado'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Obtener el perfil del usuario
        try:
            profile = UserProfile.objects.get(user=target_user)
        except UserProfile.DoesNotExist:
            return Response(
                {'error': 'Perfil de usuario no encontrado'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Generar una contraseña temporal usando la identificación del perfil (no del usuario)
        temp_password = profile.identificacion
        
        # Establecer la nueva contraseña
        target_user.set_password(temp_password)
        target_user.save()
        
        # Marcar que el usuario debe cambiar su contraseña en el próximo inicio de sesión
        profile.requiere_cambio_clave = True
        profile.save()
        
        return Response(
            {
                'success': True,
                'message': f'Contraseña restablecida para {target_user.username}. El usuario deberá cambiar su contraseña en el próximo inicio de sesión.'
            },
            status=status.HTTP_200_OK
        )
    
    except Exception as e:
        print(f"Error al resetear contraseña: {str(e)}")
        return Response(
            {'error': f'Error al procesar la solicitud: {str(e)}'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )



# Vista para importar usuarios desde CSV/Excel
@api_view(['POST'])
@permission_classes([IsAuthenticated, IsAdmin])
def import_users_view(request):
    # Procesar importación de usuarios y devolver respuesta...
    pass

# Vista para solicitar recuperación de contraseña (usuario)
@api_view(['POST'])
@permission_classes([AllowAny])
def request_password_reset_view(request):
    # Procesar solicitud de recuperación y devolver respuesta...
    pass

# Vista para resetear contraseña (usuario)
@api_view(['POST'])
@permission_classes([AllowAny])
def reset_password_view(request):
    try:
        # Obtener datos de la solicitud
        data = request.data
        user_id = data.get('userId')
        new_password = data.get('newPassword')
        temp_password = data.get('tempPassword')
        
        if not user_id or not new_password or not temp_password:
            return Response(
                {'error': 'Se requiere ID de usuario, contraseña temporal y nueva contraseña'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        print(f"ID: {user_id}, Nueva Clave: **************," + 
              f" Temp Clave: **********")
        
        # CAMBIO AQUÍ: Buscar por username en lugar de id
        try:
            # Primero intentamos buscar por username, que debería ser el número de identificación
            user = User.objects.get(username=user_id)
        except User.DoesNotExist:
            # Como alternativa, podríamos intentar buscar por identificación en el perfil
            try:
                profile = UserProfile.objects.get(identificacion=user_id)
                user = profile.user
            except UserProfile.DoesNotExist:
                return Response(
                    {'error': 'Usuario no encontrado'},
                    status=status.HTTP_404_NOT_FOUND
                )
        
        # Verificar la contraseña temporal
        if not user.check_password(temp_password):
            return Response(
                {'error': 'Contraseña temporal incorrecta'},
                status=status.HTTP_401_UNAUTHORIZED
            )
        
        # El resto del código sigue igual...
        # Establecer la nueva contraseña
        user.set_password(new_password)
        user.save()
        
        # Actualizar el perfil
        try:
            profile = UserProfile.objects.get(user=user)
            profile.requiere_cambio_clave = False
            profile.save()
        except UserProfile.DoesNotExist:
            pass
        
        # Generar token JWT
        refresh = RefreshToken.for_user(user)
        access_token = str(refresh.access_token)
        
        # Preparar respuesta
        try:
            profile = UserProfile.objects.get(user=user)
            rol = profile.rol
            nombres = profile.nombres
        except UserProfile.DoesNotExist:
            rol = 'sin_perfil'
            nombres = user.username
        
        return Response({
            'token': access_token,
            'user_id': user.id,
            'rol': rol,
            'nombres': nombres,
            'requiere_cambio_clave': False
        })
        
    except Exception as e:
        print(f"Error al cambiar contraseña: {str(e)}")
        return Response(
            {'error': f'Error al procesar la solicitud: {str(e)}'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )
        
        

# Vista para confirmar recuperación con código (si se implementa)
@api_view(['POST'])
@permission_classes([AllowAny])
def confirm_password_reset_view(request):
    # Procesar confirmación de recuperación y devolver respuesta...
    pass
