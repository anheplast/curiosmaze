#!/bin/bash
# =================================================================
# Script de entrada para el contenedor Django
# Ubicación: /backend/entrypoint.sh
# =================================================================

set -e  # Salir si cualquier comando falla

echo "Iniciando backend CURIOSMAZE..."
echo "==================================="

# Función para esperar a que PostgreSQL esté listo
wait_for_postgres() {
    echo "Esperando a que PostgreSQL esté listo..."
    
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
    print('PostgreSQL está listo')
except Exception as e:
    print(f'PostgreSQL no está listo: {e}')
    exit(1)
"; do
        echo "PostgreSQL aún no está listo, esperando 2 segundos..."
        sleep 2
    done
}

# Ejecutar verificaciones
echo "Verificando configuración de Django..."
python manage.py check --database default

# Esperar a PostgreSQL
wait_for_postgres

# Ejecutar migraciones
echo "Ejecutando migraciones..."
python manage.py makemigrations --noinput
python manage.py migrate --noinput

# Crear superusuario si no existe
echo "Verificando superusuario..."
python manage.py shell -c "
from django.contrib.auth import get_user_model
User = get_user_model()
if not User.objects.filter(username='admin').exists():
    User.objects.create_superuser('admin', 'admin@curiosmaze.com', 'admin123')
    print('Superusuario creado: admin/admin123')
else:
    print('Superusuario ya existe')
"

# Recolectar archivos estáticos
echo "Recolectando archivos estáticos..."
python manage.py collectstatic --noinput --clear

echo "Backend listo! Iniciando servidor Django..."
echo "Servidor disponible en puerto 8000"
echo "==================================="

# Ejecutar el comando pasado como argumento (por defecto runserver)
exec "$@"