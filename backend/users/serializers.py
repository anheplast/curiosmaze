# backend/users/serializers.py
from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import UserProfile


User = get_user_model()


class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserProfile
        exclude = ['user']
        extra_kwargs = {
            'nombres': {'required': True, 'error_messages': {'required': 'El campo nombres es obligatorio'}},
            'apellidos': {'required': True, 'error_messages': {'required': 'El campo apellidos es obligatorio'}},
            'identificacion': {'required': True, 'error_messages': {'required': 'El número de identificación es obligatorio'}},
            # Hacemos que los demás campos no sean obligatorios
            'edad': {'required': False},
            'genero': {'required': False},
            'fecha_nacimiento': {'required': False},
            'turno': {'required': False},
            'curso': {'required': False},
            'paralelo': {'required': False},
            'especializacion': {'required': False},
            'categoria': {'required': False},  # Añadimos el nuevo campo
        }


class UserSerializer(serializers.ModelSerializer):
    profile = UserProfileSerializer(required=True)
    
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'password', 'profile']
        extra_kwargs = {
            'password': {'write_only': True, 'required': True, 'error_messages': {'required': 'La contraseña es obligatoria'}},
            'username': {'required': True, 'error_messages': {'required': 'El nombre de usuario es obligatorio'}},
            'email': {'required': True, 'error_messages': {'required': 'El correo electrónico es obligatorio'}}
        }

    def create(self, validated_data):
        profile_data = validated_data.pop('profile')
        password = validated_data.pop('password')
        
        # Asegurar que todos los usuarios tengan categoría "Tecnología Educativa" por defecto
        if 'categoria' not in profile_data:
            profile_data['categoria'] = 'tecnologia_educativa'
        
        # Crear el usuario
        user = User.objects.create(**validated_data)
        user.set_password(password)
        user.save()
        
        # Crear el perfil
        UserProfile.objects.create(user=user, **profile_data)
        
        return user


class UserLoginSerializer(serializers.Serializer):
    userId = serializers.CharField(max_length=50, required=True, error_messages={'required': 'El ID de usuario es obligatorio'})
    password = serializers.CharField(max_length=128, write_only=True, required=True, error_messages={'required': 'La contraseña es obligatoria'})
    
    token = serializers.CharField(max_length=255, read_only=True)
    user_id = serializers.IntegerField(read_only=True)
    rol = serializers.CharField(read_only=True)
    nombres = serializers.CharField(read_only=True)
