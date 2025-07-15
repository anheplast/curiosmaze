# backend/config/settings.py - Configuración corregida para Debug Toolbar

import os
from datetime import timedelta
from pathlib import Path
from dotenv import load_dotenv

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# Cargar variables de entorno desde .env
load_dotenv(BASE_DIR / '.env')

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.environ.get('SECRET_KEY', 'django-insecure-change-this-in-production')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = os.environ.get('DEBUG', 'False').lower() == 'true'

# Hosts permitidos - importante para Docker
ALLOWED_HOSTS = os.environ.get('ALLOWED_HOSTS', '*').split(',')

# =================================================================
# CONFIGURACIÓN DE BASE DE DATOS - POSTGRESQL
# =================================================================

DATABASE_ENGINE = os.environ.get('DATABASE_ENGINE', 'django.db.backends.postgresql')

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.environ.get('DATABASE_NAME', 'db_curiosmaze'),
        'USER': os.environ.get('DATABASE_USER', 'curiosmaze_user'),
        'PASSWORD': os.environ.get('DATABASE_PASSWORD', 'curiosmaze_password'),
        'HOST': os.environ.get('DATABASE_HOST', 'localhost'),
        'PORT': os.environ.get('DATABASE_PORT', '5432'),
        'OPTIONS': {
            'connect_timeout': 20,
        },
        'CONN_MAX_AGE': 600,
    }
}

print("🐘 Usando PostgreSQL como base de datos")

# =================================================================
# CONFIGURACIÓN DE JUDGE0
# =================================================================

JUDGE0_API_URL = os.environ.get('JUDGE0_API_URL', 'http://localhost:2358')
JUDGE0_AUTH_TOKEN = os.environ.get('JUDGE0_AUTH_TOKEN', '')
JUDGE0_MAX_WORKERS = int(os.environ.get('JUDGE0_MAX_WORKERS', '5'))
JUDGE0_TIMEOUT = int(os.environ.get('JUDGE0_TIMEOUT', '30'))

# Límites de ejecución para Judge0
CPU_TIME_LIMIT = float(os.environ.get('CPU_TIME_LIMIT', '2.0'))
CPU_EXTRA_TIME = float(os.environ.get('CPU_EXTRA_TIME', '0.5'))
WALL_TIME_LIMIT = float(os.environ.get('WALL_TIME_LIMIT', '5.0'))
MEMORY_LIMIT = int(os.environ.get('MEMORY_LIMIT', '128000'))

if DEBUG:
    print(f"🔧 Judge0 API URL: {JUDGE0_API_URL}")
    print(f"⏱️  Límites: CPU={CPU_TIME_LIMIT}s, Memoria={MEMORY_LIMIT}KB")

# =================================================================
# APLICACIONES INSTALADAS
# =================================================================

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    
    # Aplicaciones de terceros
    'rest_framework',
    'corsheaders',
    
    # Aplicaciones propias
    'users',
    'evaluations',
    'manage_students',
]

# =================================================================
# CONFIGURACIÓN DE HERRAMIENTAS DE DESARROLLO
# =================================================================

# Solo agregar herramientas de desarrollo si DEBUG=True y están instaladas
if DEBUG:
    # Verificar si django-extensions está disponible
    try:
        import django_extensions
        INSTALLED_APPS.append('django_extensions')
        print("✅ Django Extensions disponible")
    except ImportError:
        print("⚠️  Django Extensions no instalado")
    
    # Verificar si debug-toolbar está disponible
    try:
        import debug_toolbar
        INSTALLED_APPS.append('debug_toolbar')
        print("✅ Debug Toolbar disponible")
    except ImportError:
        print("⚠️  Debug Toolbar no instalado")

# =================================================================
# MIDDLEWARE
# =================================================================

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'corsheaders.middleware.CorsMiddleware',
]

# Agregar debug toolbar middleware solo si está disponible
if DEBUG:
    try:
        import debug_toolbar
        MIDDLEWARE.append('debug_toolbar.middleware.DebugToolbarMiddleware')
        print("🐛 Debug Toolbar middleware agregado")
    except ImportError:
        pass

MIDDLEWARE.extend([
    'middleware.PermissionLoggingMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'middleware.JudgeRateLimitMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
])

ROOT_URLCONF = 'config.urls'

# =================================================================
# CONFIGURACIÓN ESPECÍFICA PARA DEBUG TOOLBAR
# =================================================================

if DEBUG:
    try:
        import debug_toolbar
        
        # IPs internas que pueden ver el debug toolbar
        INTERNAL_IPS = [
            '127.0.0.1',
            'localhost',
            # Para Docker
            '172.17.0.1',  # IP típica del host de Docker
            '192.168.0.1', # Otra IP común
            '10.0.2.2',    # VirtualBox
        ]
        
        # Agregar la IP actual si está disponible
        try:
            import socket
            hostname, _, ips = socket.gethostbyname_ex(socket.gethostname())
            INTERNAL_IPS.extend([ip[:-1] + '1' for ip in ips])
        except:
            pass
        
        # Configuración adicional para debug toolbar
        DEBUG_TOOLBAR_CONFIG = {
            'SHOW_TOOLBAR_CALLBACK': lambda request: DEBUG,
            'SHOW_TEMPLATE_CONTEXT': True,
            'ENABLE_STACKTRACES': True,
        }
        
        print(f"🔍 Debug Toolbar configurado para IPs: {INTERNAL_IPS}")
        
    except ImportError:
        pass

# =================================================================
# CONFIGURACIÓN DE CORS
# =================================================================

CORS_ALLOW_ALL_ORIGINS = True  # Para desarrollo
CORS_ALLOW_CREDENTIALS = True

CORS_ALLOW_METHODS = [
    'DELETE',
    'GET',
    'OPTIONS',
    'PATCH',
    'POST',
    'PUT',
]

CORS_ALLOW_HEADERS = [
    'accept',
    'accept-encoding',
    'authorization',
    'content-type',
    'dnt',
    'origin',
    'user-agent',
    'x-csrftoken',
    'x-requested-with',
]

# =================================================================
# CONFIGURACIÓN DE TEMPLATES
# =================================================================

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'config.wsgi.application'

# =================================================================
# CONFIGURACIÓN DE CACHE SIMPLE
# =================================================================

CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
        'LOCATION': 'curiosmaze-cache',
        'TIMEOUT': 3600,
        'OPTIONS': {
            'MAX_ENTRIES': 1000,
            'CULL_FREQUENCY': 3,
        }
    }
}

print("💾 Usando cache en memoria local")

# =================================================================
# PASSWORD VALIDATION
# =================================================================

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

# =================================================================
# INTERNATIONALIZATION
# =================================================================

LANGUAGE_CODE = 'es-es'
TIME_ZONE = 'America/Guayaquil'
USE_I18N = True
USE_TZ = True

# =================================================================
# STATIC FILES
# =================================================================

STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'

MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

# =================================================================
# REST FRAMEWORK
# =================================================================

REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ),
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.AllowAny',
    ],
    'DEFAULT_PARSER_CLASSES': [
        'rest_framework.parsers.JSONParser',
        'rest_framework.parsers.FormParser',
        'rest_framework.parsers.MultiPartParser',
    ],
}

# =================================================================
# JWT CONFIGURATION
# =================================================================

SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(hours=8),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=7),
    'ROTATE_REFRESH_TOKENS': True,
    'BLACKLIST_AFTER_ROTATION': True,
    'AUTH_HEADER_TYPES': ('Bearer',),
}

# =================================================================
# LOGGING BÁSICO
# =================================================================

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
        },
    },
    'root': {
        'handlers': ['console'],
        'level': 'INFO',
    },
}

# Configuración específica del modelo de usuario
AUTH_USER_MODEL = 'users.User'

# Default primary key field type
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

print(f"⚙️  Configuración cargada - DEBUG: {DEBUG}, DB: postgresql")
print(f"🌐 Hosts permitidos: {ALLOWED_HOSTS}")