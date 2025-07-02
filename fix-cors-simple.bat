@echo off
cls
echo =====================================================
echo        CURIOSMAZE - CORRECTOR SIMPLE DE CORS
echo =====================================================
echo.

if not exist "curiosmaze_backend\.env" (
    echo [ERROR] No se encontro curiosmaze_backend\.env
    pause
    exit /b 1
)

echo [INFO] Creando respaldo...
copy "curiosmaze_backend\.env" "curiosmaze_backend\.env.backup" >nul

echo [INFO] Corrigiendo CORS...

REM Leer el archivo actual y crear uno nuevo
(
echo DEBUG=True
echo DJANGO_SECRET_KEY=django-insecure-dev-key-12345
echo ALLOWED_HOSTS=192.168.1.2,192.168.1.21,localhost,127.0.0.1
echo BACKEND_CORS_ORIGINS=http://localhost:5173,http://192.168.1.2:5173,http://192.168.1.21:5173
echo CSRF_TRUSTED_ORIGINS=http://localhost:5173,http://192.168.1.2:5173,http://192.168.1.21:5173
echo.
echo # Configuracion Judge0
echo JUDGE0_API_URL=http://192.168.1.80:2358
echo JUDGE0_AUTH_TOKEN=
echo JUDGE0_TIMEOUT=120000
echo JUDGE0_MAX_WORKERS=5
echo.
echo # Limites de ejecucion
echo CPU_TIME_LIMIT=2
echo CPU_EXTRA_TIME=0.5
echo WALL_TIME_LIMIT=5
echo MEMORY_LIMIT=128000
echo MAX_QUEUE_SIZE=200
echo NUMBER_OF_WORKERS=8
echo MAX_FILE_SIZE=1024
echo.
echo # Parametros de seguridad
echo ENABLE_NETWORK=false
echo ENABLE_PER_PROCESS_AND_THREAD_MEMORY_LIMIT=true
) > curiosmaze_backend\.env

echo [OK] CORS corregido exitosamente
echo.
echo =====================================================
echo                 SIGUIENTE PASO
echo =====================================================
echo.
echo REINICIA EL BACKEND:
echo.
echo 1. Si el backend esta ejecutandose, presiona Ctrl+C
echo 2. cd curiosmaze_backend
echo 3. venv\Scripts\activate.bat
echo 4. python manage.py runserver 0.0.0.0:8000
echo.
echo Luego prueba el login en: http://localhost:5173
echo.
pause