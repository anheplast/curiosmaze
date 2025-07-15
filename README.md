# CURIOSMAZE
<p align="center">
  <img src="./img/Logo-CuriosMaze.png" alt="CURIOSMAZE Logo" width="300">
</p>

<p align="center">
  <img src="https://img.shields.io/badge/version-0.5.1-blue" alt="Version">
  <img src="https://img.shields.io/badge/License-MIT-green.svg" alt="License: MIT">
  <img src="https://img.shields.io/badge/Vue.js-3.x-42b883" alt="Vue 3">
  <img src="https://img.shields.io/badge/Django-REST-ff1709" alt="Django">
  <img src="https://img.shields.io/badge/Judge0-API-5b5ff9" alt="Judge0">
</p>

**CURIOSMAZE** es una plataforma web educativa para el desarrollo del pensamiento lógico y la evaluación automática de ejercicios de programación.

La plataforma permite crear evaluaciones interactivas con ejercicios de programación, los cuales son evaluados automáticamente mediante un sistema de ejecución de código (Judge0) que proporciona retroalimentación inmediata.

## Stack Tecnológico

| Componente | Tecnología |
|------------|------------|
| **Frontend** | Vue.js 3 + Vite |
| **Backend** | Django REST Framework |
| **Base de Datos** | PostgreSQL |
| **Ejecución de Código** | Judge0 API |
| **Estilos** | BulmaCSS + CSS Custom |
| **Contenedores** | Docker + Docker Compose |

## Inicio Rápido

### Prerequisitos
- Docker & Docker Compose
- node
- python

### Instalación
```bash
# Clonar repositorio
git clone <repository-url>
cd curiosmaze

# Copiar variables de entorno ajustarlas
cp .env.example .env

# Iniciar con Docker
# Construir todas las imágenes
docker-compose build

# Iniciar servicios paso a paso
docker-compose up -d db          # Primero la base de datos
docker-compose up -d backend     # Luego el backend
docker-compose up -d frontend    # Finalmente el frontend

# Iniciar con Nginx (usando profile)
docker-compose --profile proxy up -d

# O iniciar todo junto
docker-compose up -d

# Verificar estado
docker-compose ps

# Ver logs
docker-compose logs -f

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
docker-compose exec db pg_isready -U usuario -d curiosmaze

# Probar conexión manual
docker-compose exec backend python -c "
import psycopg2
conn = psycopg2.connect(host='db', user='usuario', password='password', dbname='curiosmaze')
print('Conexión exitosa!')
"
```

### URLs de Acceso
- **Frontend**: http://localhost:5173
- **Backend API**: http://localhost:8000/api
- **Admin Django**: http://localhost:8000/admin

## 📁 Estructura del Proyecto

```
curiosmaze/
├── frontend/                    # Aplicación Vue.js 3
│   ├── src/
│   │   ├── components/         # Componentes reutilizables
│   │   │   ├── admin/         # Componentes de administración
│   │   │   ├── docentes/      # Componentes para profesores
│   │   │   ├── estudiantes/   # Componentes para estudiantes
│   │   │   └── Common/        # Componentes compartidos
│   │   ├── views/             # Vistas principales
│   │   ├── api/               # Servicios API
│   │   ├── router/            # Configuración de rutas
│   │   └── store/             # Gestión de estado
├── backend/                     # API Django REST
│   ├── config/                # Configuración Django
│   ├── users/                 # Gestión de usuarios
│   ├── evaluations/           # Sistema de evaluaciones
│   └── manage_students/       # Gestión de estudiantes
├── scripts/                     # Scripts de automatización
└── nginx/                      # Configuración Nginx
```

## 👥 Roles del Sistema

| Rol | Descripción | Funcionalidades |
|-----|-------------|-----------------|
| **Admin** | Administrador del sistema | Gestión de usuarios, configuración global |
| **Docente** | Profesor/Instructor | Crear evaluaciones, ejercicios, ver progreso |
| **Estudiante** | Alumno | Resolver evaluaciones, ver historial |

## Funcionalidades Principales

- ✅ **Evaluaciones automáticas** con Judge0
- ✅ **Editor de código** [CodeMirror](https://codemirror.net/)
- ✅ **Sistema de roles** y permisos
- ✅ **Gestión de estudiantes** 
- ✅ **Histórial de evaluaciones** y estadística
- ✅ **Interfaz responsive** con BulmaCSS
- ✅ **Notificaciones** en tiempo real

## 🔧 Scripts de Desarrollo

```bash
# Desarrollo
npm run scripts/dev-start.bat    # Iniciar servicios
npm run scripts/dev-stop.bat     # Detener servicios
npm run scripts/dev-reset.bat    # Reset completo

# Utilidades
npm run scripts/backup.bat       # Backup BD
npm run scripts/monitor.bat      # Monitoreo
```

## 🐳 Docker Compose

```bash
docker-compose up -d               # Levanta todo 
docker-compose --profile proxy up -d  # Con Nginx
```


## 🏫 Implementación Educativa

<img src="./img/fe_y_alegria_logo.png" alt="Logo Unidad Educativa Juan Pablo II" width="60"/>

Implementado en la Unidad Educativa Juan Pablo II – Ibarra, Ecuador.