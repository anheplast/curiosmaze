# Guía Completa de Dockerización para CURIOSMAZE

## Tabla de Contenidos

1. [Preparación del Entorno](#preparación-del-entorno)
2. [Construcción de Contenedores](#construcción-de-contenedores)
3. [Configuraciones de Despliegue](#configuraciones-de-despliegue)
4. [Variaciones del Sistema](#variaciones-del-sistema)
5. [Operaciones Diarias](#operaciones-diarias)

---

## **Preparación del Entorno**

### **Requisitos Previos**

Antes de comenzar, necesitas tener instalado Docker Desktop en tu máquina Windows. Docker Desktop actúa como el "administrador del edificio de apartamentos" que gestiona todos los contenedores.

### **Estructura de Archivos Requerida**

Tu proyecto debe tener esta estructura específica. Cada archivo tiene un propósito pedagógico que explicaremos:

```
curiosmaze/                          # Directorio raíz del proyecto
├── .env                            # Configuración principal (el "panel de control")
├── docker-compose.yml              # Orquestador básico
├── docker-compose.prod.yml         # Orquestador de producción
├── .dockerignore                   # Exclusiones globales
├── backend/
│   ├── Dockerfile                  # Receta para el contenedor backend
│   ├── .dockerignore              # Exclusiones específicas del backend
│   ├── entrypoint.sh              # Script de inicialización
│   ├── requirements.txt           # Dependencias Python actualizadas
│   └── config/
│       ├── settings.py            # Configuración Django adaptada
│       └── urls.py                # URLs con soporte para debug toolbar
├── frontend/
│   ├── Dockerfile                  # Receta para el contenedor frontend
│   ├── .dockerignore              # Exclusiones específicas del frontend
│   └── ... (código Vue.js existente)
├── nginx/
│   ├── nginx.dev.conf             # Configuración para desarrollo
│   └── nginx.prod.conf            # Configuración para producción
└── scripts/
    ├── dev-start.bat              # Scripts de automatización
    ├── dev-stop.bat
    ├── update-ips.bat
    └── verify-setup.bat
```

---

## **Construcción de Contenedores**

### **Fase 1: Configuración de Variables de Entorno**

El archivo `.env` actúa como el panel de control centralizado de toda tu aplicación. Piensa en él como el tablero de instrumentos de un avión: desde aquí controlas todos los aspectos importantes del sistema.

**Archivo: `/.env`**
```bash
# =================================================================
# CONFIGURACIÓN PRINCIPAL DE CURIOSMAZE
# =================================================================

# 🌐 Servicios Principales
HOST_MACHINE_IP=192.168.1.2          # IP de tu máquina Windows
JUDGE0_HOST=192.168.1.80              # IP donde está Judge0
JUDGE0_PORT=2358
JUDGE0_API_URL=http://192.168.1.80:2358

# 🔌 Puertos de Servicios
BACKEND_PORT=8000
FRONTEND_PORT=5173
DATABASE_PORT=5432
REDIS_PORT=6379

# 📊 Base de Datos PostgreSQL
DATABASE_NAME=curiosmaze
DATABASE_USER=mappl3
DATABASE_PASSWORD=gordo1neon          # Sin espacios ni comillas especiales

# 🔒 Seguridad
SECRET_KEY=django-curiosmaze-super-secret-key-2024
DEBUG=true
ALLOWED_HOSTS=localhost,127.0.0.1,backend,curiosmaze-backend

# 🌍 CORS Configuration
BACKEND_CORS_ORIGINS=http://localhost:5173,http://127.0.0.1:5173
CSRF_TRUSTED_ORIGINS=http://localhost:5173,http://127.0.0.1:5173

# ⚙️ Judge0 Límites
CPU_TIME_LIMIT=2.0
CPU_EXTRA_TIME=0.5
WALL_TIME_LIMIT=5.0
MEMORY_LIMIT=128000
JUDGE0_MAX_WORKERS=5
JUDGE0_TIMEOUT=30

# 🚀 Redis
REDIS_PASSWORD=redis_curiosmaze_2024

# 🐳 Docker
DOCKER_ENVIRONMENT=true
COMPOSE_PROJECT_NAME=curiosmaze
```

### **Fase 2: Dockerfile del Backend Django**

El Dockerfile del backend es como la receta detallada para preparar el entorno donde vivirá Django. Cada instrucción tiene un propósito específico que contribuye a la estabilidad y funcionalidad del contenedor.

**Archivo: `/backend/Dockerfile`**
```dockerfile
# Usamos Python 3.11 slim como base - es liviano pero completo
FROM python:3.11-slim

# Configuramos variables de entorno que optimizan Python para contenedores
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    DEBIAN_FRONTEND=noninteractive \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Instalamos dependencias del sistema necesarias para PostgreSQL y herramientas básicas
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# Establecemos el directorio de trabajo
WORKDIR /app

# Copiamos y configuramos el script de entrada primero (para mejor caching)
COPY entrypoint.sh /app/entrypoint.sh
RUN chmod +x /app/entrypoint.sh

# Copiamos requirements.txt primero para aprovechar el cache de Docker
COPY requirements.txt .

# Instalamos dependencias Python
RUN pip install --upgrade pip && \
    pip install -r requirements.txt

# Copiamos todo el código del proyecto
COPY . .

# Creamos directorios necesarios para logs y archivos estáticos
RUN mkdir -p logs staticfiles media

# Verificamos que el script de entrada existe
RUN ls -la /app/entrypoint.sh

# Exponemos el puerto donde Django escuchará
EXPOSE 8000

# Definimos el punto de entrada y comando por defecto
ENTRYPOINT ["/app/entrypoint.sh"]
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
```

### **Fase 3: Script de Entrada del Backend**

El script `entrypoint.sh` es el ceremoniaster del contenedor backend. Se encarga de preparar todo antes de que Django entre en escena: verifica conexiones, ejecuta migraciones y configura el superusuario.

**Archivo: `/backend/entrypoint.sh`**
```bash
#!/bin/bash
# Script de inicialización del contenedor Django

set -e  # Detener ejecución si algún comando falla

echo "🚀 Iniciando backend CURIOSMAZE..."
echo "==================================="

# Función que espera pacientemente a que PostgreSQL esté listo
wait_for_postgres() {
    echo "⏳ Esperando a que PostgreSQL esté listo..."
    
    while ! python -c "
import os
import psycopg2
try:
    conn = psycopg2.connect(
        host=os.environ.get('DATABASE_HOST', 'db'),
        port=os.environ.get('DATABASE_PORT', '5432'),
        user=os.environ.get('DATABASE_USER', 'mappl3'),
        password=os.environ.get('DATABASE_PASSWORD', 'gordo1neon'),
        dbname=os.environ.get('DATABASE_NAME', 'curiosmaze')
    )
    conn.close()
    print('✅ PostgreSQL está listo')
except Exception as e:
    print(f'⏳ PostgreSQL no está listo: {e}')
    exit(1)
"; do
        echo "⏳ PostgreSQL aún no está listo, esperando 2 segundos..."
        sleep 2
    done
}

# Verificamos la configuración de Django
echo "🔍 Verificando configuración de Django..."
python manage.py check --database default

# Esperamos a que PostgreSQL esté completamente operativo
wait_for_postgres

# Ejecutamos las migraciones para crear/actualizar la estructura de la base de datos
echo "📊 Ejecutando migraciones..."
python manage.py makemigrations --noinput
python manage.py migrate --noinput

# Creamos un superusuario si no existe (útil para acceso administrativo inmediato)
echo "👤 Verificando superusuario..."
python manage.py shell -c "
from django.contrib.auth import get_user_model
User = get_user_model()
if not User.objects.filter(username='admin').exists():
    User.objects.create_superuser('admin', 'admin@curiosmaze.com', 'admin123')
    print('✅ Superusuario creado: admin/admin123')
else:
    print('ℹ️  Superusuario ya existe')
"

# Recolectamos archivos estáticos para servir CSS, JS, etc.
echo "📁 Recolectando archivos estáticos..."
python manage.py collectstatic --noinput --clear

echo "✅ Backend listo! Iniciando servidor Django..."
echo "🌐 Servidor disponible en puerto 8000"
echo "==================================="

# Ejecutamos el comando que se pasó al contenedor (por defecto runserver)
exec "$@"
```

### **Fase 4: Dockerfile del Frontend Vue.js**

El Dockerfile del frontend utiliza una técnica llamada "multi-stage build", que es como tener diferentes cocinas especializadas: una para preparar los ingredientes (desarrollo) y otra para servir el plato final (producción).

**Archivo: `/frontend/Dockerfile`**
```dockerfile
# =============================================================================
# ETAPA 1: Construcción (Build Stage)
# Aquí preparamos la aplicación para producción
# =============================================================================
FROM node:18-alpine AS builder

ENV NODE_ENV=production \
    PNPM_HOME="/pnpm" \
    PATH="$PNPM_HOME:$PATH"

# Habilitamos pnpm para gestión de paquetes más eficiente
RUN corepack enable

WORKDIR /app

# Copiamos archivos de configuración de dependencias primero
COPY package*.json ./

# Instalamos solo dependencias de producción
RUN npm ci --only=production --silent

# Copiamos el código fuente completo
COPY . .

# Construimos la aplicación optimizada para producción
RUN npm run build

# =============================================================================
# ETAPA 2: Desarrollo (Development Stage)
# Esta etapa mantiene todas las herramientas de desarrollo activas
# =============================================================================
FROM node:18-alpine AS development

ENV NODE_ENV=development

RUN corepack enable

WORKDIR /app

# Creamos usuario no-root por seguridad
RUN addgroup -g 1001 -S nodejs && \
    adduser -S nextjs -u 1001

# Copiamos configuración de paquetes
COPY package*.json ./

# Instalamos TODAS las dependencias (incluidas las de desarrollo)
RUN npm install

# Copiamos todo el código fuente
COPY . .

# Cambiamos propietario de archivos al usuario no-root
RUN chown -R nextjs:nodejs /app
USER nextjs

# Exponemos puerto de desarrollo de Vite
EXPOSE 5173

# Comando para desarrollo con hot-reload
CMD ["npm", "run", "dev", "--", "--host", "0.0.0.0", "--port", "5173"]

# =============================================================================
# ETAPA 3: Producción con Nginx (Production Stage)
# Aquí servimos la aplicación optimizada usando Nginx
# =============================================================================
FROM nginx:alpine AS production

# Instalamos herramientas adicionales útiles
RUN apk --no-cache add curl

# Creamos directorio para logs personalizados
RUN mkdir -p /var/log/nginx

# Copiamos los archivos construidos desde la etapa builder
COPY --from=builder /app/dist /usr/share/nginx/html

# Configuramos Nginx específicamente para aplicaciones Vue.js SPA
RUN echo 'server {\n\
    listen 80;\n\
    listen [::]:80;\n\
    \n\
    root /usr/share/nginx/html;\n\
    index index.html;\n\
    \n\
    # Configuración especial para Vue Router (Single Page App)\n\
    location / {\n\
        try_files $uri $uri/ /index.html;\n\
    }\n\
    \n\
    # Optimización de cache para archivos estáticos\n\
    location ~* \.(js|css|png|jpg|jpeg|gif|ico|svg|woff|woff2|ttf|eot)$ {\n\
        expires 1y;\n\
        add_header Cache-Control "public, immutable";\n\
        add_header Access-Control-Allow-Origin "*";\n\
    }\n\
    \n\
    # Headers de seguridad básicos\n\
    add_header X-Frame-Options "SAMEORIGIN" always;\n\
    add_header X-Content-Type-Options "nosniff" always;\n\
    add_header X-XSS-Protection "1; mode=block" always;\n\
    \n\
    # Compresión para mejor rendimiento\n\
    gzip on;\n\
    gzip_vary on;\n\
    gzip_min_length 1024;\n\
    gzip_types text/plain text/css text/xml text/javascript application/javascript application/xml+rss application/json;\n\
    \n\
    # Endpoint de salud para monitoreo\n\
    location /health {\n\
        access_log off;\n\
        return 200 "healthy\n";\n\
        add_header Content-Type text/plain;\n\
    }\n\
}' > /etc/nginx/conf.d/default.conf

# Creamos script de verificación de salud
RUN echo '#!/bin/sh\n\
curl -f http://localhost/health || exit 1' > /health-check.sh && \
    chmod +x /health-check.sh

EXPOSE 80

# Configuramos verificación de salud automática
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
    CMD ["/health-check.sh"]

# Iniciamos Nginx en modo foreground
CMD ["nginx", "-g", "daemon off;"]
```

---

## **Configuraciones de Despliegue**

### **Configuración Básica (Sin Redis, Sin Nginx)**

Esta es la configuración más simple, ideal para empezar a entender Docker. Es como aprender a caminar antes de correr.

**Archivo: `/docker-compose.yml`**
```yaml
version: '3.8'

# Red privada para que los contenedores se comuniquen
networks:
  curiosmaze-net:
    driver: bridge

# Volúmenes para persistir datos importantes
volumes:
  backend_data:
    driver: local
  postgres_data:
    driver: local

services:
  # Base de datos PostgreSQL - El almacén de datos
  db:
    image: postgres:15-alpine
    container_name: curiosmaze-db
    restart: unless-stopped
    environment:
      POSTGRES_DB: ${DATABASE_NAME}
      POSTGRES_USER: ${DATABASE_USER}
      POSTGRES_PASSWORD: ${DATABASE_PASSWORD}
      POSTGRES_HOST_AUTH_METHOD: trust
    volumes:
      - postgres_data:/var/lib/postgresql/data
      - ./backups:/backups
    ports:
      - "${DATABASE_PORT}:5432"
    networks:
      - curiosmaze-net
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U ${DATABASE_USER} -d ${DATABASE_NAME}"]
      interval: 10s
      timeout: 5s
      retries: 5

  # Backend Django - El cerebro de la aplicación
  backend:
    build:
      context: ./backend
      dockerfile: Dockerfile
    container_name: curiosmaze-backend
    restart: unless-stopped
    environment:
      - DEBUG=${DEBUG}
      - SECRET_KEY=${SECRET_KEY}
      - ALLOWED_HOSTS=${ALLOWED_HOSTS}
      - DOCKER_ENVIRONMENT=true
      
      # Configuración de base de datos
      - DATABASE_ENGINE=django.db.backends.postgresql
      - DATABASE_NAME=${DATABASE_NAME}
      - DATABASE_USER=${DATABASE_USER}
      - DATABASE_PASSWORD=${DATABASE_PASSWORD}
      - DATABASE_HOST=db  # Nombre del servicio Docker
      - DATABASE_PORT=5432
      
      # Configuración de Judge0
      - JUDGE0_API_URL=${JUDGE0_API_URL}
      - JUDGE0_MAX_WORKERS=${JUDGE0_MAX_WORKERS}
      - JUDGE0_TIMEOUT=${JUDGE0_TIMEOUT}
      
      # Configuración CORS
      - BACKEND_CORS_ORIGINS=${BACKEND_CORS_ORIGINS}
      - CSRF_TRUSTED_ORIGINS=${CSRF_TRUSTED_ORIGINS}
      
      # Límites de ejecución
      - CPU_TIME_LIMIT=${CPU_TIME_LIMIT}
      - CPU_EXTRA_TIME=${CPU_EXTRA_TIME}
      - WALL_TIME_LIMIT=${WALL_TIME_LIMIT}
      - MEMORY_LIMIT=${MEMORY_LIMIT}
      
    volumes:
      # Montamos código para desarrollo (permite hot-reload)
      - ./backend:/app
      - backend_data:/app/media
      - ./backend/logs:/app/logs
    ports:
      - "${BACKEND_PORT}:8000"
    networks:
      - curiosmaze-net
    depends_on:
      db:
        condition: service_healthy
    healthcheck:
      test: ["CMD-SHELL", "curl -f http://localhost:8000/api/ || exit 1"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 60s

  # Frontend Vue.js - La cara visible de la aplicación
  frontend:
    build:
      context: ./frontend
      dockerfile: Dockerfile
      target: development  # Usamos la etapa de desarrollo
    container_name: curiosmaze-frontend
    restart: unless-stopped
    environment:
      # Variables específicas para Vue.js
      - VITE_API_URL=http://localhost:${BACKEND_PORT}/api
      - VITE_JUDGE0_API_URL=${JUDGE0_API_URL}
      - VITE_APP_TITLE=CURIOSMAZE
      - VITE_APP_VERSION=0.5.1
      - VITE_APP_ENV=development
      - VITE_DEBUG_MODE=true
      - VITE_SHOW_DEV_OVERLAY=true
      
      # Límites para mostrar en la interfaz
      - VITE_CPU_TIME_LIMIT=${CPU_TIME_LIMIT}
      - VITE_CPU_EXTRA_TIME=${CPU_EXTRA_TIME}
      - VITE_WALL_TIME_LIMIT=${WALL_TIME_LIMIT}
      - VITE_MEMORY_LIMIT=${MEMORY_LIMIT}
      
      # Configuración de interfaz
      - VITE_DEFAULT_THEME=dark
      - VITE_ENABLE_ANIMATIONS=true
      - VITE_NOTIFICATION_DURATION=4000
      
    volumes:
      # Montamos código para desarrollo
      - ./frontend:/app
      - /app/node_modules  # Volumen anónimo para optimización
    ports:
      - "${FRONTEND_PORT}:5173"
    networks:
      - curiosmaze-net
    depends_on:
      - backend
    stdin_open: true
    tty: true
```

### **Comandos para Configuración Básica**

```bash
# Construir todas las imágenes
docker-compose build

# Iniciar servicios paso a paso
docker-compose up -d db          # Primero la base de datos
docker-compose up -d backend     # Luego el backend
docker-compose up -d frontend    # Finalmente el frontend

# O iniciar todo junto
docker-compose up -d

# Verificar estado
docker-compose ps

# Ver logs
docker-compose logs -f

# URLs disponibles:
# Frontend: http://localhost:5173
# Backend: http://localhost:8000/api/
# Admin: http://localhost:8000/admin/
```

---

## **Variaciones del Sistema**

### **Variación 1: Agregando Redis (Cache + Performance)**

Redis actúa como la memoria de trabajo rápida de tu aplicación, almacenando información frecuentemente accedida para mejorar significativamente el rendimiento.

Para agregar Redis, añade este servicio a tu `docker-compose.yml`:

```yaml
  # Servicio Redis para cache y mejora de rendimiento
  redis:
    image: redis:7-alpine
    container_name: curiosmaze-redis
    restart: unless-stopped
    command: redis-server --appendonly yes --requirepass ${REDIS_PASSWORD}
    ports:
      - "${REDIS_PORT}:6379"
    networks:
      - curiosmaze-net
    volumes:
      - ./redis-data:/data
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 30s
      timeout: 5s
      retries: 3
```

Y actualiza el backend para usar Redis:

```yaml
# En el servicio backend, agregar:
environment:
  - REDIS_URL=redis://:${REDIS_PASSWORD}@redis:${REDIS_PORT}/1
  - CACHE_BACKEND=django_redis.cache.RedisCache
```

**Comandos para usar con Redis:**
```bash
# Iniciar incluyendo Redis
docker-compose up -d db redis backend frontend

# Conectarse a Redis para debugging
docker-compose exec redis redis-cli
# Dentro de Redis: AUTH redis_curiosmaze_2024
```

### **Variación 2: Agregando Nginx (Reverse Proxy Professional)**

Nginx actúa como el recepcionista profesional de tu aplicación, dirigiendo el tráfico de manera inteligente y añadiendo funcionalidades avanzadas como compresión y cache.

Primero, crea la configuración de Nginx para desarrollo:

**Archivo: `/nginx/nginx.dev.conf`**
```nginx
events {
    worker_connections 1024;
}

http {
    include /etc/nginx/mime.types;
    default_type application/octet-stream;
    
    # Logging para desarrollo
    access_log /var/log/nginx/access.log;
    error_log /var/log/nginx/error.log;
    
    # Configuraciones básicas
    sendfile on;
    keepalive_timeout 65;
    
    # Definimos los servidores backend
    upstream backend {
        server curiosmaze-backend:8000;
    }
    
    upstream frontend {
        server curiosmaze-frontend:5173;
    }
    
    server {
        listen 80;
        server_name localhost;
        
        # API Backend - Todas las rutas /api/
        location /api/ {
            proxy_pass http://backend;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
            
            # Headers CORS para desarrollo
            add_header Access-Control-Allow-Origin * always;
            add_header Access-Control-Allow-Methods "GET, POST, PUT, DELETE, OPTIONS" always;
            add_header Access-Control-Allow-Headers "Authorization, Content-Type, X-Requested-With" always;
        }
        
        # Admin Django
        location /admin/ {
            proxy_pass http://backend;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
        }
        
        # Archivos estáticos del backend
        location /static/ {
            proxy_pass http://backend;
            proxy_set_header Host $host;
        }
        
        location /media/ {
            proxy_pass http://backend;
            proxy_set_header Host $host;
        }
        
        # Health check
        location /health {
            access_log off;
            return 200 "nginx-proxy-healthy\n";
            add_header Content-Type text/plain;
        }
        
        # Configuraciones especiales para Vite (Hot Module Replacement)
        location /@vite/ {
            proxy_pass http://frontend;
            proxy_http_version 1.1;
            proxy_set_header Upgrade $http_upgrade;
            proxy_set_header Connection 'upgrade';
            proxy_set_header Host $host;
            proxy_cache_bypass $http_upgrade;
        }
        
        location /src/ {
            proxy_pass http://frontend;
            proxy_http_version 1.1;
            proxy_set_header Upgrade $http_upgrade;
            proxy_set_header Connection 'upgrade';
            proxy_set_header Host $host;
            proxy_cache_bypass $http_upgrade;
        }
        
        location /node_modules/ {
            proxy_pass http://frontend;
            proxy_http_version 1.1;
            proxy_set_header Upgrade $http_upgrade;
            proxy_set_header Connection 'upgrade';
            proxy_set_header Host $host;
            proxy_cache_bypass $http_upgrade;
        }
        
        # Frontend Vue.js - Catch-all (debe ser el último)
        location / {
            proxy_pass http://frontend;
            proxy_http_version 1.1;
            proxy_set_header Upgrade $http_upgrade;
            proxy_set_header Connection 'upgrade';
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
            proxy_cache_bypass $http_upgrade;
        }
    }
}
```

Luego añade el servicio Nginx a tu `docker-compose.yml`:

```yaml
  # Nginx Reverse Proxy - El director de tráfico profesional
  nginx:
    image: nginx:alpine
    container_name: curiosmaze-nginx
    restart: unless-stopped
    ports:
      - "80:80"
    volumes:
      - ./nginx/nginx.dev.conf:/etc/nginx/nginx.conf:ro
      - backend_data:/media:ro
    networks:
      - curiosmaze-net
    depends_on:
      - backend
      - frontend
    profiles:
      - proxy  # Solo se ejecuta con el profile 'proxy'
    healthcheck:
      test: ["CMD-SHELL", "curl -f http://localhost/health || exit 1"]
      interval: 30s
      timeout: 10s
      retries: 3
```

**Comandos para usar con Nginx:**
```bash
# Iniciar con Nginx (usando profile)
docker-compose --profile proxy up -d

# Sin Nginx (modo normal)
docker-compose up -d

# Solo agregar Nginx a un sistema corriendo
docker-compose --profile proxy up -d nginx

# URLs con Nginx:
# Todo a través de: http://localhost/
# Frontend: http://localhost/
# Backend: http://localhost/api/
# Admin: http://localhost/admin/
```

### **Variación 3: Sistema Completo (Redis + Nginx)**

Para usar todas las funcionalidades juntas, combina los servicios anteriores:

```bash
# Iniciar sistema completo
docker-compose --profile proxy up -d

# Verificar que todos los servicios estén corriendo
docker-compose --profile proxy ps

# Deberías ver:
# - curiosmaze-db
# - curiosmaze-backend  
# - curiosmaze-frontend
# - curiosmaze-redis
# - curiosmaze-nginx
```

---

## **Operaciones Diarias**

### **Scripts de Automatización**

Para facilitar el uso diario, puedes crear scripts que automaticen las operaciones más comunes.

**Archivo: `/scripts/dev-start.bat`**
```batch
@echo off
echo ========================================
echo    CURIOSMAZE - Inicio Desarrollo
echo ========================================

echo 🚀 Iniciando servicios de desarrollo...
docker-compose up -d

echo ⏳ Esperando a que los servicios estén listos...
timeout /t 10 /nobreak

echo 📊 Estado de los contenedores:
docker-compose ps

echo 🌐 URLs disponibles:
echo   Frontend: http://localhost:5173
echo   Backend API: http://localhost:8000/api
echo   Admin Django: http://localhost:8000/admin

echo ✅ Entorno de desarrollo listo!
pause
```

**Archivo: `/scripts/dev-stop.bat`**
```batch
@echo off
echo ========================================
echo   CURIOSMAZE - Detener Desarrollo  
echo ========================================

echo 🛑 Deteniendo contenedores...
docker-compose down

echo ✅ Contenedores detenidos correctamente!
pause
```

### **Comandos de Monitoreo y Debugging**

```bash
# Ver logs en tiempo real de todos los servicios
docker-compose logs -f

# Ver logs de un servicio específico
docker-compose logs -f backend
docker-compose logs -f frontend

# Acceder al shell de un contenedor para debugging
docker-compose exec backend bash
docker-compose exec frontend sh

# Ejecutar comandos Django directamente
docker-compose exec backend python manage.py shell
docker-compose exec backend python manage.py createsuperuser

# Verificar conectividad entre contenedores
docker-compose exec backend ping curiosmaze-db
docker-compose exec nginx wget -O- http://curiosmaze-backend:8000/api/

# Ver uso de recursos
docker stats

# Limpiar sistema (cuidado: elimina datos)
docker-compose down -v  # Elimina volúmenes
docker system prune     # Limpia imágenes no usadas
```

### **Solución de Problemas Comunes**

**Problema: Los contenedores no se comunican**
```bash
# Verificar que están en la misma red
docker network ls
docker network inspect curiosmaze_curiosmaze-net

# Probar conectividad DNS
docker-compose exec backend nslookup curiosmaze-db
```

**Problema: Frontend no carga**
```bash
# Verificar logs del frontend
docker-compose logs frontend

# Verificar que Vite está corriendo en el puerto correcto
docker-compose exec frontend netstat -tlnp
```

**Problema: Backend no conecta a la base de datos**
```bash
# Verificar que PostgreSQL está listo
docker-compose exec db pg_isready -U mappl3 -d curiosmaze

# Probar conexión manual
docker-compose exec backend python -c "
import psycopg2
conn = psycopg2.connect(host='db', user='mappl3', password='gordo1neon', dbname='curiosmaze')
print('Conexión exitosa!')
"
```

### **Actualización de IPs (Judge0)**

Cuando cambies la IP de Judge0, usa el script automatizado:

**Archivo: `/scripts/update-ips.bat`**
```batch
@echo off
echo ========================================
echo     CURIOSMAZE - Actualizar IPs
echo ========================================

echo IP actual de Judge0:
type ..\.env | findstr "JUDGE0_HOST"

set /p new_ip="Nueva IP de Judge0: "

echo Actualizando configuración...
powershell -Command "(Get-Content '..\.env') | ForEach-Object { $_ -replace '^JUDGE0_HOST=.*', 'JUDGE0_HOST=%new_ip%' } | Set-Content '..\.env'"

echo ✅ IP actualizada. Reinicia los contenedores:
echo    docker-compose restart backend frontend

pause
```

---

## **Configuración para Producción**

### **Diferencias Clave en Producción**

La configuración de producción enfatiza seguridad, rendimiento y estabilidad sobre facilidad de desarrollo.

**Archivo: `/docker-compose.prod.yml`**
```yaml
version: '3.8'

networks:
  curiosmaze-prod:
    driver: bridge
  internal:
    driver: bridge
    internal: true  # Red interna segura

volumes:
  postgres_data_prod:
    driver: local
  backend_media:
    driver: local
  backend_static:
    driver: local

services:
  db:
    image: postgres:15-alpine
    container_name: curiosmaze-db-prod
    restart: always  # Reinicio automático en producción
    environment:
      POSTGRES_DB: ${DATABASE_NAME}
      POSTGRES_USER: ${DATABASE_USER}
      POSTGRES_PASSWORD: ${DATABASE_PASSWORD}
    volumes:
      - postgres_data_prod:/var/lib/postgresql/data
      - ./backups:/backups
    networks:
      - internal  # Solo accesible internamente
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U ${DATABASE_USER} -d ${DATABASE_NAME}"]
      interval: 30s
      timeout: 10s
      retries: 3

  backend:
    build:
      context: ./backend
      dockerfile: Dockerfile
    container_name: curiosmaze-backend-prod
    restart: always
    environment:
      # Configuración de producción estricta
      - DEBUG=False
      - SECRET_KEY=${SECRET_KEY}
      - ALLOWED_HOSTS=${ALLOWED_HOSTS}
      
      # Base de datos
      - DATABASE_ENGINE=django.db.backends.postgresql
      - DATABASE_NAME=${DATABASE_NAME}
      - DATABASE_USER=${DATABASE_USER}
      - DATABASE_PASSWORD=${DATABASE_PASSWORD}
      - DATABASE_HOST=db
      - DATABASE_PORT=5432
      
      # Seguridad mejorada
      - SESSION_COOKIE_SECURE=True
      - CSRF_COOKIE_SECURE=True
      - SESSION_COOKIE_SAMESITE=None
      - CSRF_COOKIE_SAMESITE=None
      
    volumes:
      - backend_media:/app/media
      - backend_static:/app/staticfiles
    networks:
      - curiosmaze-prod
      - internal
    depends_on:
      db:
        condition: service_healthy

  frontend:
    build:
      context: ./frontend
      dockerfile: Dockerfile
      target: production  # Usamos la etapa de producción optimizada
    container_name: curiosmaze-frontend-prod
    restart: always
    networks:
      - curiosmaze-prod

  nginx:
    image: nginx:alpine
    container_name: curiosmaze-nginx-prod
    restart: always
    ports:
      - "80:80"
      - "443:443"  # HTTPS para producción
    volumes:
      - ./nginx/nginx.prod.conf:/etc/nginx/nginx.conf:ro
      - ./nginx/ssl:/etc/nginx/ssl:ro  # Certificados SSL
      - backend_static:/static:ro
      - backend_media:/media:ro
    networks:
      - curiosmaze-prod
    depends_on:
      - backend
      - frontend
```

**Comandos para Producción:**
```bash
# Construcción y despliegue de producción
docker-compose -f docker-compose.prod.yml build
docker-compose -f docker-compose.prod.yml up -d

# Verificar estado en producción
docker-compose -f docker-compose.prod.yml ps

# Backup de base de datos en producción
docker-compose -f docker-compose.prod.yml exec db pg_dump -U ${DATABASE_USER} ${DATABASE_NAME} > backup_$(date +%Y%m%d).sql
```

---

## **Conclusión y Mejores Prácticas**

### **Principios Fundamentales Aprendidos**

A través de esta guía, hemos aplicado varios principios fundamentales de containerización que te servirán en cualquier proyecto futuro:

**Separación de Responsabilidades**: Cada contenedor tiene una función específica y bien definida, similar a como cada músico en una orquesta tiene su papel específico.

**Configuración Centralizada**: Todas las variables importantes se manejan desde archivos de configuración centralizados, facilitando el mantenimiento y la portabilidad.

**Escalabilidad Gradual**: Comenzamos con una configuración básica y añadimos complejidad gradualmente, permitiendo entender cada componente antes de agregar el siguiente.

### **Patrones de Uso Recomendados**

Para desarrollo diario, utiliza la configuración básica (sin Redis ni Nginx) ya que es más simple de debuggear y permite acceso directo a los logs de cada servicio.

Para testing de integración o cuando necesites simular un entorno más cercano a producción, activa Nginx usando profiles.

Para desarrollo de funcionalidades que requieren cache intensivo, activa Redis para probar el comportamiento real del sistema.

### **Comandos de Referencia Rápida**

```bash
# Desarrollo básico
docker-compose up -d
docker-compose logs -f
docker-compose down

# Con Nginx (más cercano a producción)
docker-compose --profile proxy up -d
docker-compose --profile proxy logs -f
docker-compose --profile proxy down

# Producción
docker-compose -f docker-compose.prod.yml up -d

# Debugging y mantenimiento
docker-compose exec backend python manage.py shell
docker-compose exec db psql -U mappl3 -d curiosmaze
docker system prune  # Limpiar sistema
```


