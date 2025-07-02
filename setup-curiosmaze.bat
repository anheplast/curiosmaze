@echo off
setlocal enabledelayedexpansion
cls
echo =====================================================
echo        CURIOSMAZE - CONFIGURADOR COMPLETO
echo =====================================================
echo.
echo Este script configura AUTOMATICAMENTE:
echo [+] Archivos .env de Frontend y Backend separados
echo [+] Instala dependencias de Node.js
echo [+] Construye el Frontend (dist/)
echo [+] Configura el Backend de Django
echo [+] Ejecuta migraciones
echo [+] Todo listo para usar por separado
echo.
echo =====================================================
echo.
echo Selecciona tu escenario de despliegue:
echo.
echo 1) DESARROLLO LOCAL    - Solo en tu PC (localhost)
echo 2) RED ESCOLAR        - Varias PCs en red local
echo 3) TESTING ABIERTO    - Acepta TODAS las IPs 
echo 4) PRODUCCION         - IPs especificas seguras
echo.

set /p OPTION="Ingresa tu opcion (1-4): "

if "%OPTION%"=="1" goto DESARROLLO
if "%OPTION%"=="2" goto RED_LOCAL
if "%OPTION%"=="3" goto TESTING_ABIERTO
if "%OPTION%"=="4" goto PRODUCCION

echo [ERROR] Opcion no valida
pause
exit /b 1

:DESARROLLO
echo.
echo [CONFIG] CONFIGURANDO PARA DESARROLLO LOCAL...
set BACKEND_IP=localhost
set BACKEND_PORT=8000
set FRONTEND_PORT=5173
set ALLOWED_HOSTS=localhost,127.0.0.1
set CORS_ORIGINS=http://localhost:5173
set ENV_TYPE=development
goto JUDGE0_CONFIG

:RED_LOCAL
echo.
echo [CONFIG] CONFIGURANDO PARA RED ESCOLAR...
echo.
echo Necesito algunas IPs para configurar:
set /p BACKEND_IP="IP donde estara el servidor backend (ej: 192.168.1.2): "
echo.
echo IPs de las computadoras que usaran la aplicacion:
set /p FRONTEND_IPS="Separadas por comas (ej: 192.168.1.2,192.168.1.3,192.168.1.10): "

set BACKEND_PORT=8000
set FRONTEND_PORT=5173

REM Construir CORS_ORIGINS
set CORS_ORIGINS=
for %%i in (%FRONTEND_IPS%) do (
    if defined CORS_ORIGINS (
        set CORS_ORIGINS=!CORS_ORIGINS!,http://%%i:5173
    ) else (
        set CORS_ORIGINS=http://%%i:5173
    )
)
set ALLOWED_HOSTS=%FRONTEND_IPS%,localhost
set ENV_TYPE=staging
goto JUDGE0_CONFIG

:TESTING_ABIERTO
echo.
echo [WARNING] CONFIGURANDO PARA TESTING (ACEPTA TODAS LAS IPs)...
echo.
echo ADVERTENCIA: Esta configuracion es INSEGURA
echo Solo usar para testing rapido, NUNCA en produccion
echo.
set /p CONFIRM="¿Estas seguro? (S/N): "
if /i not "%CONFIRM%"=="S" goto INICIO

set /p BACKEND_IP="IP del servidor backend (ej: 192.168.1.2): "
set BACKEND_PORT=8000
set FRONTEND_PORT=5173
set ALLOWED_HOSTS=*
set CORS_ORIGINS=*
set ENV_TYPE=open
goto JUDGE0_CONFIG

:PRODUCCION
echo.
echo [CONFIG] CONFIGURANDO PARA PRODUCCION...
echo.
echo Para produccion necesito configuracion especifica:
set /p BACKEND_IP="IP del servidor de produccion: "
set /p FRONTEND_IPS="IPs autorizadas para frontend (separadas por comas): "
set /p SECRET_KEY="Clave secreta de Django (deja vacio para generar una): "

if "%SECRET_KEY%"=="" (
    set SECRET_KEY=django-prod-%RANDOM%%RANDOM%%RANDOM%
)

set BACKEND_PORT=8000
set FRONTEND_PORT=5173

REM Construir CORS_ORIGINS para produccion
set CORS_ORIGINS=
for %%i in (%FRONTEND_IPS%) do (
    if defined CORS_ORIGINS (
        set CORS_ORIGINS=!CORS_ORIGINS!,http://%%i:5173
    ) else (
        set CORS_ORIGINS=http://%%i:5173
    )
)
set ALLOWED_HOSTS=%FRONTEND_IPS%
set ENV_TYPE=production
goto JUDGE0_CONFIG

:JUDGE0_CONFIG
echo.
echo [CONFIG] CONFIGURACION DE JUDGE0...
echo.
echo Judge0 es el sistema que ejecuta el codigo de programacion
set /p JUDGE0_IP="IP del servidor Judge0 (ej: 192.168.1.80): "
if "%JUDGE0_IP%"=="" set JUDGE0_IP=192.168.1.80
set JUDGE0_PORT=2358
goto CONFIGURAR

:CONFIGURAR
cls
echo =====================================================
echo           INICIANDO CONFIGURACION...
echo =====================================================
echo.
echo RESUMEN DE CONFIGURACION:
echo ----------------------------------------
echo Backend:     http://%BACKEND_IP%:%BACKEND_PORT%
echo Frontend:    http://%BACKEND_IP%:%FRONTEND_PORT%
echo Judge0:      http://%JUDGE0_IP%:%JUDGE0_PORT%
echo CORS:        %CORS_ORIGINS%
echo Hosts:       %ALLOWED_HOSTS%
echo Tipo:        %ENV_TYPE%
echo.
pause

echo.
echo ========================================
echo PASO 1: CONFIGURANDO FRONTEND...
echo ========================================

REM Verificar si existe la carpeta frontend
if not exist "frontend" (
    echo [ERROR] No se encontro la carpeta 'frontend'
    echo Ejecuta este script desde la carpeta principal del proyecto
    pause
    exit /b 1
)

cd frontend

echo [INFO] Creando archivo .env del frontend...
echo VITE_APP_NAME=CURIOSMAZE > .env
echo VITE_APP_VERSION=0.2.5 >> .env  
echo VITE_BACKEND_URL=http://%BACKEND_IP%:%BACKEND_PORT% >> .env
echo VITE_API_URL=http://%BACKEND_IP%:%BACKEND_PORT%/api >> .env
echo VITE_JUDGE0_API_URL=http://%JUDGE0_IP%:%JUDGE0_PORT% >> .env
echo VITE_PASSWORD_RESET_FORM_URL=https://docs.google.com/forms/d/e/1FAIpQLSdQiO3vIMH27yoZITCIqI6e_wWPgIQ-oRndgSsMS1fxg1vYsg/viewform?usp=dialog >> .env
echo VITE_HELP_FORM_URL=https://docs.google.com/forms/d/e/1FAIpQLSfKaPM3rzCLAvvC7k2TUmTJ-msj_7odiAoaErRQnn4aBwrnuw/viewform?usp=header >> .env

echo [OK] Archivo frontend/.env creado

echo.
echo [INFO] Verificando Node.js...
node --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Node.js no esta instalado
    echo Instala Node.js desde: https://nodejs.org/
    pause
    exit /b 1
) else (
    echo [OK] Node.js encontrado
)

echo.
echo [INFO] Instalando dependencias de Node.js...
call npm install
if %errorlevel% neq 0 (
    echo [ERROR] Error instalando dependencias de Node.js
    pause
    exit /b 1
)
echo [OK] Dependencias de Node.js instaladas

echo.
echo [INFO] Construyendo aplicacion frontend...
call npm run build
if %errorlevel% neq 0 (
    echo [ERROR] Error en el build del frontend
    pause
    exit /b 1
)
echo [OK] Frontend construido exitosamente

cd ..

echo.
echo ========================================
echo PASO 2: CONFIGURANDO BACKEND...
echo ========================================

REM Verificar si existe la carpeta backend
if not exist "curiosmaze_backend" (
    echo [ERROR] No se encontro la carpeta 'curiosmaze_backend'
    pause
    exit /b 1
)

cd curiosmaze_backend

echo [INFO] Creando archivo .env del backend...

if "%ENV_TYPE%"=="production" (
    echo DEBUG=False > .env
    echo DJANGO_SECRET_KEY=%SECRET_KEY% >> .env
) else (
    echo DEBUG=True > .env
    echo DJANGO_SECRET_KEY=django-insecure-dev-key-%RANDOM% >> .env
)

echo ALLOWED_HOSTS=%ALLOWED_HOSTS% >> .env
echo BACKEND_CORS_ORIGINS=%CORS_ORIGINS% >> .env
echo CSRF_TRUSTED_ORIGINS=%CORS_ORIGINS% >> .env
echo. >> .env
echo # Configuracion Judge0 >> .env
echo JUDGE0_API_URL=http://%JUDGE0_IP%:%JUDGE0_PORT% >> .env
echo JUDGE0_AUTH_TOKEN= >> .env
echo JUDGE0_TIMEOUT=120000 >> .env
echo JUDGE0_MAX_WORKERS=5 >> .env
echo. >> .env
echo # Limites de ejecucion >> .env
echo CPU_TIME_LIMIT=2 >> .env
echo CPU_EXTRA_TIME=0.5 >> .env
echo WALL_TIME_LIMIT=5 >> .env
echo MEMORY_LIMIT=128000 >> .env
echo MAX_QUEUE_SIZE=200 >> .env
echo NUMBER_OF_WORKERS=8 >> .env
echo MAX_FILE_SIZE=1024 >> .env
echo. >> .env
echo # Parametros de seguridad >> .env
echo ENABLE_NETWORK=false >> .env
echo ENABLE_PER_PROCESS_AND_THREAD_MEMORY_LIMIT=true >> .env

echo [OK] Archivo backend/.env creado

echo.
echo [INFO] Verificando Python...
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Python no esta instalado o no esta en PATH
    pause
    exit /b 1
) else (
    echo [OK] Python encontrado
)

echo.
echo [INFO] Verificando entorno virtual...
if exist "venv\Scripts\activate.bat" (
    echo [OK] Entorno virtual encontrado
    call venv\Scripts\activate.bat
) else (
    echo [INFO] Creando entorno virtual...
    python -m venv venv
    call venv\Scripts\activate.bat
)

echo.
echo [INFO] Instalando dependencias de Python...
pip install -r requirements.txt
if %errorlevel% neq 0 (
    echo [ERROR] Error instalando dependencias de Python  
    pause
    exit /b 1
)
echo [OK] Dependencias de Python instaladas

echo.
echo [INFO] Ejecutando migraciones...
python manage.py makemigrations
python manage.py migrate
if %errorlevel% neq 0 (
    echo [ERROR] Error en migraciones
    pause
    exit /b 1
)
echo [OK] Migraciones completadas

echo.
echo [INFO] Configurando archivos estaticos...
REM Crear carpetas necesarias
if not exist "staticfiles" mkdir staticfiles
if not exist "media" mkdir media
if not exist "logs" mkdir logs

REM Intentar collectstatic (puede fallar la primera vez, es normal)
python manage.py collectstatic --noinput --clear 2>nul || (
    echo [INFO] collectstatic falló (normal en primera ejecución)
)
echo [OK] Configuracion de archivos estaticos lista

cd ..

cls
echo =====================================================
echo           CONFIGURACION COMPLETADA
echo =====================================================
echo.
echo CURIOSMAZE esta listo para usar!
echo.
echo RESUMEN FINAL:
echo ----------------------------------------
echo Backend API: http://%BACKEND_IP%:%BACKEND_PORT%/api/
echo Frontend:    Se debe servir por separado
echo Judge0:      http://%JUDGE0_IP%:%JUDGE0_PORT%
echo Tipo:        %ENV_TYPE%
echo Archivos:    Frontend en dist/, Backend configurado
echo.
echo INSTRUCCIONES PARA EJECUTAR:
echo ========================================
echo.
echo TERMINAL 1 - BACKEND (API):
echo ---------------------------
echo cd curiosmaze_backend
echo venv\Scripts\activate.bat
echo python manage.py runserver 0.0.0.0:%BACKEND_PORT%
echo.
echo TERMINAL 2 - FRONTEND:
echo ----------------------
echo cd frontend  
echo npm run preview -- --host 0.0.0.0 --port %FRONTEND_PORT%
echo.
echo PARA PROBAR QUE FUNCIONA:
echo ========================
echo.
echo 1. Backend API: http://%BACKEND_IP%:%BACKEND_PORT%/api/
echo    (Debes ver la interfaz de Django REST Framework)
echo.
echo 2. Frontend: http://%BACKEND_IP%:%FRONTEND_PORT%
echo    (Debes ver la aplicacion CURIOSMAZE)
echo.
echo 3. Judge0: http://%JUDGE0_IP%:%JUDGE0_PORT%
echo    (Debe estar ejecutandose por separado)
echo.

if "%ENV_TYPE%"=="production" (
    echo NOTAS DE SEGURIDAD PARA PRODUCCION:
    echo ----------------------------------------
    echo - Configura HTTPS si es posible
    echo - Verifica firewall y puertos abiertos
    echo - Respalda regularmente la base de datos
    echo - Tu clave secreta: %SECRET_KEY%
    echo.
)

if "%ENV_TYPE%"=="open" (
    echo ADVERTENCIA DE SEGURIDAD:
    echo ----------------------------------------
    echo - Esta configuracion acepta TODAS las IPs
    echo - Solo usar para testing, NUNCA en produccion
    echo - Cambia la configuracion antes de uso real
    echo.
)

echo [OK] Todo configurado correctamente!
echo.
echo ¿Quieres ejecutar el BACKEND automaticamente? (S/N): 
set /p RUN_BACKEND=""
if /i "%RUN_BACKEND%"=="S" (
    echo.
    echo [INFO] Iniciando BACKEND...
    echo Para iniciar el FRONTEND, abre otra terminal y ejecuta:
    echo cd frontend ^&^& npm run preview -- --host 0.0.0.0 --port %FRONTEND_PORT%
    echo.
    pause
    cd curiosmaze_backend
    call venv\Scripts\activate.bat
    python manage.py runserver 0.0.0.0:%BACKEND_PORT%
) else (
    echo.
    echo Recuerda ejecutar ambos servicios por separado:
    echo 1. Backend: cd curiosmaze_backend ^&^& venv\Scripts\activate.bat ^&^& python manage.py runserver 0.0.0.0:%BACKEND_PORT%
    echo 2. Frontend: cd frontend ^&^& npm run preview -- --host 0.0.0.0 --port %FRONTEND_PORT%
    pause
)