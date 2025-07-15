# backend/users/urls.py
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    UserViewSet, login_view, user_profile_view, register_docente_view, 
    list_users_by_status, update_user_status, csrf_token_view,
    create_user_view, update_user_view, delete_user_view, 
    admin_reset_password_view, import_users_view,
    request_password_reset_view, reset_password_view, confirm_password_reset_view
)

from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from .models import User, UserProfile

router = DefaultRouter()
router.register(r'users', UserViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('login/', login_view, name='login'),
    path('profile/', user_profile_view, name='user-profile'),
    # Endpoint para obtener token CSRF
    path('csrf-token/', csrf_token_view, name='csrf-token'),
    # Endpoint para registro de docentes sin autenticación
    path('register/docente/', register_docente_view, name='register-docente'),
    
    # Endpoints para gestión de usuarios
    path('by-status/<str:estado>/', list_users_by_status, name='users-by-status'),
    path('update-status/', update_user_status, name='update-user-status'),
    
    # Endpoints para el sistema de administración
    path('create/', create_user_view, name='create-user'),
    path('update/<int:user_id>/', update_user_view, name='update-user'),
    path('delete/<int:user_id>/', delete_user_view, name='delete-user'),
    path('admin-reset-password/', admin_reset_password_view, name='admin-reset-password'),
    path('import/', import_users_view, name='import-users'),
    
    # Endpoints para recuperación de contraseña
    path('request-password-reset/', request_password_reset_view, name='request-password-reset'),
    path('reset-password/', reset_password_view, name='reset-password'),
    path('confirm-password-reset/', confirm_password_reset_view, name='confirm-password-reset'),

]