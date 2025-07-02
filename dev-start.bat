@echo off
setlocal enabledelayedexpansion
cls
echo =====================================================
echo        CURIOSMAZE - MODO DESARROLLO
echo =====================================================
echo.
echo Este script configura e inicia CURIOSMAZE en modo desarrollo
echo.
echo IMPORTANTE: Este modo NO requiere build del frontend
echo El frontend se ejecuta con servidor de desarrollo (hot reload)
echo.

REM Verificar estructura del proyecto
if not exist "frontend" (
    echo [ERROR] No se encontro la carpeta 'frontend'
    echo Ejecuta este script desde la carpeta principal del proyecto
    pause
    exit /b 1
)

if not exist "curiosmaze_backend" (
    echo [ERROR] No se encontro la carpeta 'curiosmaze_backend'
    echo Ejecuta este script desde la carpeta principal del proyecto
    pause
    exit /b 1
)

echo =====================================================
echo           CONFIGURACION DE DESARROLLO
echo =====================================================
echo.

REM Obtener IP local automaticamente
for /f "tokens=2 delims=:" %%a in ('ipconfig ^| findstr /c:"IPv4"') do (
    set LOCAL_IP=%%a
    set LOCAL_IP=!LOCAL_IP: =!
    goto :got_ip
)
:got_ip

if "%LOCAL_IP%"=="" set LOCAL_IP=localhost

echo Tu IP local detectada: %LOCAL_IP%
echo.
echo Configuracion sugerida para desarrollo:
echo Backend: http://%LOCAL_IP%:8000
echo Frontend: http://%LOCAL_IP%:5173
echo.

set /p USE_DETECTED="Usar IP detectada (%LOCAL_IP%)? (S/N): "
if /i "%USE_DETECTED%"=="S" (
    set SERVER_IP=%LOCAL_IP%
) else (
    set /p SERVER_IP="Ingresa la IP del servidor backend: "
    if "!SERVER_IP!"=="" set SERVER_IP=localhost
)

echo.
echo [CRITICO] Configuracion de Judge0:
echo Judge0 es necesario para ejecutar el codigo de programacion
echo.
set /p JUDGE0_IP="IP del servidor Judge0 (ej: 192.168.1.80): "
if "%JUDGE0_IP%"=="" (
    echo [ERROR] La IP de Judge0 es obligatoria
    pause
    exit /b 1
)

set /p JUDGE0_PORT="Puerto de Judge0 (default: 2358): "
if "%JUDGE0_PORT%"=="" set JUDGE0_PORT=2358

echo.
echo =====================================================
echo        CONFIGURANDO FRONTEND (DESARROLLO)
echo =====================================================

cd frontend

echo [INFO] Configurando .env del frontend para desarrollo...
echo VITE_APP_NAME=CURIOSMAZE > .env
echo VITE_APP_VERSION=0.1.1-dev >> .env
echo VITE_BACKEND_URL=http://%SERVER_IP%:8000 >> .env
echo VITE_API_URL=http://%SERVER_IP%:8000/api >> .env
echo VITE_JUDGE0_API_URL=http://%JUDGE0_IP%:%JUDGE0_PORT% >> .env
echo VITE_PASSWORD_RESET_FORM_URL=https://docs.google.com/forms/d/e/1FAIpQLSdQiO3vIMH27yoZITCIqI6e_wWPgIQ-oRndgSsMS1fxg1vYsg/viewform?usp=dialog >> .env
echo VITE_HELP_FORM_URL=https://docs.google.com/forms/d/e/1FAIpQLSfKaPM3rzCLAvvC7k2TUmTJ-msj_7odiAoaErRQnn4aBwrnuw/viewform?usp=header >> .env

echo [OK] Frontend .env configurado para desarrollo

REM Verificar Node.js
echo [INFO] Verificando Node.js...
node --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Node.js no esta instalado
    echo Instala Node.js desde: https://nodejs.org/
    pause
    exit /b 1
)

REM Verificar/instalar dependencias
if not exist "node_modules" (
    echo [INFO] Instalando dependencias de Node.js...
    call npm install
    if %errorlevel% neq 0 (
        echo [ERROR] Error instalando dependencias
        pause
        exit /b 1
    )
) else (
    echo [OK] Dependencias de Node.js ya instaladas
)

cd ..

echo.
echo =====================================================
echo        CONFIGURANDO BACKEND (DESARROLLO)
echo =====================================================

cd curiosmaze_backend

echo [INFO] Configurando .env del backend para desarrollo...
echo DEBUG=True > .env
echo DJANGO_SECRET_KEY=django-insecure-dev-key-%RANDOM% >> .env
echo ALLOWED_HOSTS=%SERVER_IP%,localhost,127.0.0.1 >> .env
echo BACKEND_CORS_ORIGINS=http://%SERVER_IP%:5173,http://localhost:5173,http://127.0.0.1:5173 >> .env
echo CSRF_TRUSTED_ORIGINS=http://%SERVER_IP%:5173,http://localhost:5173,http://127.0.0.1:5173 >> .env
echo. >> .env
echo # Configuracion Judge0 >> .env
echo JUDGE0_API_URL=http://%JUDGE0_IP%:%JUDGE0_PORT% >> .env
echo JUDGE0_AUTH_TOKEN= >> .env
echo JUDGE0_TIMEOUT=30000 >> .env
echo JUDGE0_MAX_WORKERS=3 >> .env
echo. >> .env
echo # Limites de ejecucion para desarrollo >> .env
echo CPU_TIME_LIMIT=5 >> .env
echo CPU_EXTRA_TIME=1 >> .env
echo WALL_TIME_LIMIT=10 >> .env
echo MEMORY_LIMIT=256000 >> .env
echo MAX_QUEUE_SIZE=100 >> .env
echo NUMBER_OF_WORKERS=4 >> .env
echo MAX_FILE_SIZE=2048 >> .env
echo. >> .env
echo # Parametros de desarrollo >> .env
echo ENABLE_NETWORK=false >> .env
echo ENABLE_PER_PROCESS_AND_THREAD_MEMORY_LIMIT=true >> .env

echo [OK] Backend .env configurado para desarrollo

REM Verificar Python
echo [INFO] Verificando Python...
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Python no esta instalado
    pause
    exit /b 1
)

REM Verificar/crear entorno virtual
if not exist "venv\Scripts\activate.bat" (
    echo [INFO] Creando entorno virtual...
    python -m venv venv
    if %errorlevel% neq 0 (
        echo [ERROR] Error creando entorno virtual
        pause
        exit /b 1
    )
)

call venv\Scripts\activate.bat

REM Verificar/instalar dependencias
echo [INFO] Verificando dependencias de Python...
pip install -r requirements.txt >nul 2>&1
if %errorlevel% neq 0 (
    echo [INFO] Instalando dependencias de Python...
    pip install -r requirements.txt
    if %errorlevel% neq 0 (
        echo [ERROR] Error instalando dependencias de Python
        pause
        exit /b 1
    )
)

REM Ejecutar migraciones
echo [INFO] Verificando migraciones...
python manage.py makemigrations >nul 2>&1
python manage.py migrate >nul 2>&1

REM Crear carpetas necesarias
if not exist "logs" mkdir logs >nul 2>&1
if not exist "media" mkdir media >nul 2>&1

cd ..

cls
echo =====================================================
echo           CONFIGURACION COMPLETADA
echo =====================================================
echo.
echo RESUMEN DE CONFIGURACION DE DESARROLLO:
echo.
echo Backend API:  http://%SERVER_IP%:8000/api/
echo Frontend Dev: http://%SERVER_IP%:5173
echo Judge0:       http://%JUDGE0_IP%:%JUDGE0_PORT%
echo.
echo MODO: Desarrollo (hot reload habilitado)
echo.
echo =====================================================
echo              INICIANDO SERVICIOS
echo =====================================================
echo.

echo Como quieres iniciar los servicios?
echo.
echo 1) AUTOMATICO - Ambos servicios en ventanas separadas
echo 2) SOLO BACKEND - Tu inicias el frontend despues
echo 3) SOLO FRONTEND - Backend ya ejecutandose
echo.
set /p START_OPTION="Selecciona opcion (1-3): "

if "%START_OPTION%"=="1" goto START_BOTH
if "%START_OPTION%"=="2" goto START_BACKEND_ONLY
if "%START_OPTION%"=="3" goto START_FRONTEND_ONLY

echo [ERROR] Opcion no valida
pause
exit /b 1

:START_BOTH
echo.
echo [INFO] Iniciando ambos servicios automaticamente...

REM Iniciar Backend
echo [INFO] Iniciando Backend en ventana separada...
start "CURIOSMAZE Backend [DEV]" cmd /k "cd curiosmaze_backend && venv\Scripts\activate.bat && echo [BACKEND-DEV] Iniciando servidor Django... && python manage.py runserver %SERVER_IP%:8000"

REM Esperar que backend inicie
echo [INFO] Esperando que backend inicie completamente...
timeout /t 8 /nobreak >nul

REM Iniciar Frontend
echo [INFO] Iniciando Frontend en ventana separada...
start "CURIOSMAZE Frontend [DEV]" cmd /k "cd frontend && echo [FRONTEND-DEV] Iniciando servidor de desarrollo con hot reload... && npm run dev -- --host %SERVER_IP% --port 5173"

echo.
echo =====================================================
echo          SERVICIOS DE DESARROLLO INICIADOS
echo =====================================================
echo.
echo [OK] Backend iniciado en: http://%SERVER_IP%:8000
echo [OK] Frontend iniciado en: http://%SERVER_IP%:5173
echo [OK] Hot reload habilitado en frontend
echo.
echo PARA ACCEDER:
echo.
echo 1. Espera unos segundos a que ambos servicios carguen
echo 2. Abre tu navegador en: http://%SERVER_IP%:5173
echo 3. Los cambios en el codigo se reflejaran automaticamente
echo.
echo DESARROLLO:
echo - Frontend: Hot reload activo (cambios instantaneos)
echo - Backend: Reinicia manualmente si cambias models/urls
echo - Judge0: Debe estar ejecutandose en %JUDGE0_IP%:%JUDGE0_PORT%
echo.
goto END_SUCCESS

:START_BACKEND_ONLY
echo.
echo [INFO] Iniciando solo Backend para desarrollo...
echo.
echo Para iniciar Frontend despues, ejecuta:
echo cd frontend
echo npm run dev -- --host %SERVER_IP% --port 5173
echo.
pause

cd curiosmaze_backend
call venv\Scripts\activate.bat
echo.
echo [BACKEND-DEV] Servidor Django iniciando en modo desarrollo...
echo [BACKEND-DEV] API disponible en: http://%SERVER_IP%:8000/api/
echo [BACKEND-DEV] Admin disponible en: http://%SERVER_IP%:8000/admin/
echo.
python manage.py runserver %SERVER_IP%:8000
goto END

:START_FRONTEND_ONLY
echo.
echo [INFO] Iniciando solo Frontend para desarrollo...
echo.
echo IMPORTANTE: Asegurate que el Backend este ejecutandose en:
echo http://%SERVER_IP%:8000
echo.
set /p BACKEND_RUNNING="El Backend ya esta ejecutandose? (S/N): "
if /i not "%BACKEND_RUNNING%"=="S" (
    echo [INFO] Inicia el Backend primero
    pause
    exit /b 1
)

cd frontend
echo.
echo [FRONTEND-DEV] Servidor de desarrollo iniciando con hot reload...
echo [FRONTEND-DEV] Aplicacion disponible en: http://%SERVER_IP%:5173
echo [FRONTEND-DEV] Hot reload activo - cambios se reflejan automaticamente
echo.
npm run dev -- --host %SERVER_IP% --port 5173
goto END

:END_SUCCESS
echo DESARROLLO LISTO!
echo Manten ambas ventanas abiertas para que los servicios funcionen
echo.
:END
echo.
echo [INFO] Script de desarrollo finalizado
pause