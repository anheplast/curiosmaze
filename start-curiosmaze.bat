@echo off
cls
echo =====================================================
echo           CURIOSMAZE - INICIADOR DE SERVICIOS
echo =====================================================
echo.
echo Este script inicia ambos servicios de CURIOSMAZE:
echo [+] Backend (Django API)  
echo [+] Frontend (Vue.js)
echo.
echo IMPORTANTE: Ambos servicios se ejecutan por separado
echo Necesitaras mantener ambas ventanas abiertas
echo.
echo =====================================================

REM Verificar que existe la configuracion
if not exist "curiosmaze_backend\.env" (
    echo [ERROR] No se encontro la configuracion del backend
    echo Ejecuta primero: setup-curiosmaze-fixed.bat
    pause
    exit /b 1
)

if not exist "frontend\.env" (
    echo [ERROR] No se encontro la configuracion del frontend  
    echo Ejecuta primero: setup-curiosmaze-fixed.bat
    pause
    exit /b 1
)

REM Leer configuracion del frontend para mostrar URLs
set FRONTEND_URL=
set BACKEND_URL=
for /f "tokens=2 delims==" %%a in ('findstr "VITE_BACKEND_URL" frontend\.env') do set BACKEND_URL=%%a
for /f "tokens=2 delims==" %%a in ('findstr "VITE_BACKEND_URL" frontend\.env') do set FRONTEND_URL=%%a

REM Cambiar puerto para frontend (5173)
set FRONTEND_URL=%FRONTEND_URL:8000=5173%

echo [INFO] URLs configuradas:
echo Backend API: %BACKEND_URL%/api/
echo Frontend App: %FRONTEND_URL%
echo.

echo Selecciona como quieres iniciar los servicios:
echo.
echo 1) AUTOMATICO - Abre ambos servicios en ventanas separadas
echo 2) MANUAL - Solo Backend (tu inicias Frontend aparte)  
echo 3) SOLO FRONTEND - Solo Frontend (Backend ya ejecutandose)
echo.

set /p OPTION="Selecciona opcion (1-3): "

if "%OPTION%"=="1" goto AUTO_START
if "%OPTION%"=="2" goto BACKEND_ONLY
if "%OPTION%"=="3" goto FRONTEND_ONLY

echo [ERROR] Opcion no valida
pause
exit /b 1

:AUTO_START
echo.
echo [INFO] Iniciando ambos servicios automaticamente...
echo.

REM Iniciar Backend en ventana separada
echo [INFO] Iniciando Backend en ventana separada...
start "CURIOSMAZE - Backend API" cmd /k "cd curiosmaze_backend && venv\Scripts\activate.bat && echo [BACKEND] Iniciando servidor Django... && python manage.py runserver 0.0.0.0:8000"

REM Esperar un poco para que el backend inicie
echo [INFO] Esperando que el backend inicie...
timeout /t 5 /nobreak >nul

REM Iniciar Frontend en ventana separada  
echo [INFO] Iniciando Frontend en ventana separada...
start "CURIOSMAZE - Frontend" cmd /k "cd frontend && echo [FRONTEND] Iniciando servidor de desarrollo... && npm run preview -- --host 0.0.0.0 --port 5173"

echo.
echo =====================================================
echo             SERVICIOS INICIADOS
echo =====================================================
echo.
echo [OK] Backend iniciado en ventana separada
echo [OK] Frontend iniciado en ventana separada
echo.
echo PARA ACCEDER A LA APLICACION:
echo =============================
echo.
echo 1. Espera unos segundos a que ambos servicios terminen de cargar
echo.
echo 2. Abre tu navegador y ve a:
echo    Frontend: %FRONTEND_URL%
echo.
echo 3. Para probar la API:
echo    Backend: %BACKEND_URL%/api/
echo.
echo NOTAS IMPORTANTES:
echo ==================
echo - Mantén ambas ventanas de comando abiertas
echo - Si cierras una ventana, ese servicio se detiene
echo - Para detener: Ctrl+C en cada ventana
echo.
goto END

:BACKEND_ONLY
echo.
echo [INFO] Iniciando solo el Backend...
echo.
echo Para iniciar el Frontend despues, ejecuta en otra terminal:
echo cd frontend
echo npm run preview -- --host 0.0.0.0 --port 5173
echo.
pause

cd curiosmaze_backend
if exist "venv\Scripts\activate.bat" (
    call venv\Scripts\activate.bat
    echo [BACKEND] Iniciando servidor Django en: %BACKEND_URL%
    echo [BACKEND] API disponible en: %BACKEND_URL%/api/
    echo.
    python manage.py runserver 0.0.0.0:8000
) else (
    echo [ERROR] No se encontro el entorno virtual
    echo Ejecuta primero: setup-curiosmaze-fixed.bat
    pause
)
goto END

:FRONTEND_ONLY
echo.
echo [INFO] Iniciando solo el Frontend...
echo.
echo IMPORTANTE: Asegurate de que el Backend ya este ejecutandose en:
echo %BACKEND_URL%
echo.
set /p CONTINUE="¿El Backend ya esta ejecutandose? (S/N): "
if /i not "%CONTINUE%"=="S" (
    echo [INFO] Inicia primero el Backend antes de continuar
    pause
    exit /b 1
)

cd frontend
if exist "node_modules" (
    echo [FRONTEND] Iniciando servidor de desarrollo en: %FRONTEND_URL%
    echo [FRONTEND] Aplicacion disponible en: %FRONTEND_URL%
    echo.
    npm run preview -- --host 0.0.0.0 --port 5173
) else (
    echo [ERROR] No se encontraron las dependencias de Node.js
    echo Ejecuta primero: setup-curiosmaze-fixed.bat
    pause
)
goto END

:END
echo.
echo [INFO] Script finalizado
pause