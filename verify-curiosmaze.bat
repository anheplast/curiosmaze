@echo off
cls
echo =====================================================
echo        CURIOSMAZE - VERIFICADOR DE INSTALACION
echo =====================================================
echo.
echo Este script verifica que CURIOSMAZE este configurado correctamente
echo.

set ERRORS=0

echo [INFO] Verificando estructura de archivos...
echo.

REM Verificar carpetas principales
if not exist "frontend" (
    echo [ERROR] No se encontro la carpeta 'frontend'
    set /a ERRORS+=1
) else (
    echo [OK] Carpeta frontend encontrada
)

if not exist "curiosmaze_backend" (
    echo [ERROR] No se encontro la carpeta 'curiosmaze_backend'  
    set /a ERRORS+=1
) else (
    echo [OK] Carpeta curiosmaze_backend encontrada
)

echo.
echo [INFO] Verificando archivos de configuracion...
echo.

REM Verificar archivos .env
if not exist "frontend\.env" (
    echo [ERROR] No se encontro frontend\.env
    set /a ERRORS+=1
) else (
    echo [OK] Archivo frontend\.env encontrado
    
    REM Mostrar configuracion del frontend
    echo      Configuracion Frontend:
    for /f "tokens=1,2 delims==" %%a in ('type frontend\.env ^| findstr "VITE_"') do (
        echo      %%a = %%b
    )
)

if not exist "curiosmaze_backend\.env" (
    echo [ERROR] No se encontro curiosmaze_backend\.env
    set /a ERRORS+=1
) else (
    echo [OK] Archivo curiosmaze_backend\.env encontrado
    
    REM Mostrar configuracion del backend
    echo      Configuracion Backend:
    for /f "tokens=1,2 delims==" %%a in ('type curiosmaze_backend\.env ^| findstr /v "SECRET_KEY"') do (
        echo      %%a = %%b
    )
)

echo.
echo [INFO] Verificando dependencias...
echo.

REM Verificar Node.js
node --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Node.js no esta instalado
    set /a ERRORS+=1
) else (
    for /f %%i in ('node --version') do set NODE_VERSION=%%i
    echo [OK] Node.js !NODE_VERSION! encontrado
)

REM Verificar Python
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Python no esta instalado
    set /a ERRORS+=1
) else (
    for /f "tokens=2" %%i in ('python --version') do set PYTHON_VERSION=%%i
    echo [OK] Python !PYTHON_VERSION! encontrado
)

REM Verificar dependencias de Node.js
if exist "frontend\node_modules" (
    echo [OK] Dependencias de Node.js instaladas
) else (
    echo [ERROR] Dependencias de Node.js no instaladas
    set /a ERRORS+=1
)

REM Verificar entorno virtual de Python
if exist "curiosmaze_backend\venv\Scripts\activate.bat" (
    echo [OK] Entorno virtual de Python encontrado
) else (
    echo [ERROR] Entorno virtual de Python no encontrado
    set /a ERRORS+=1
)

REM Verificar build del frontend
if exist "frontend\dist\index.html" (
    echo [OK] Build del frontend encontrado
) else (
    echo [WARNING] Build del frontend no encontrado (puede ser normal)
)

echo.
echo [INFO] Verificando configuracion de red...
echo.

if exist "frontend\.env" (
    for /f "tokens=2 delims==" %%a in ('findstr "VITE_BACKEND_URL" frontend\.env') do (
        set BACKEND_URL=%%a
        echo [INFO] Probando conexion con backend: !BACKEND_URL!
        
        REM Intentar hacer ping a la IP del backend
        for /f "tokens=3 delims=:/" %%b in ("!BACKEND_URL!") do (
            ping -n 1 %%b >nul 2>&1
            if !errorlevel! equ 0 (
                echo [OK] IP del backend accesible: %%b
            ) else (
                echo [WARNING] No se pudo hacer ping a: %%b
                echo          Esto puede ser normal si el servidor no responde ping
            )
        )
    )
    
    for /f "tokens=2 delims==" %%a in ('findstr "VITE_JUDGE0_API_URL" frontend\.env') do (
        set JUDGE0_URL=%%a
        echo [INFO] Configuracion Judge0: !JUDGE0_URL!
        
        REM Intentar hacer ping a Judge0
        for /f "tokens=3 delims=:/" %%b in ("!JUDGE0_URL!") do (
            ping -n 1 %%b >nul 2>&1
            if !errorlevel! equ 0 (
                echo [OK] IP de Judge0 accesible: %%b
            ) else (
                echo [WARNING] No se pudo hacer ping a Judge0: %%b
                echo          Asegurate de que Judge0 este ejecutandose
            )
        )
    )
)

echo.
echo =====================================================
echo               RESULTADO DE VERIFICACION
echo =====================================================
echo.

if %ERRORS% equ 0 (
    echo [SUCCESS] CURIOSMAZE esta configurado correctamente!
    echo.
    echo PASOS SIGUIENTES:
    echo ================
    echo.
    echo 1. Para iniciar ambos servicios:
    echo    start-curiosmaze.bat
    echo.
    echo 2. O manualmente:
    echo    Terminal 1: cd curiosmaze_backend ^&^& venv\Scripts\activate ^&^& python manage.py runserver 0.0.0.0:8000
    echo    Terminal 2: cd frontend ^&^& npm run preview -- --host 0.0.0.0 --port 5173
    echo.
    echo 3. Abrir navegador en:
    if exist "frontend\.env" (
        for /f "tokens=2 delims==" %%a in ('findstr "VITE_BACKEND_URL" frontend\.env') do (
            set FRONTEND_URL=%%a
            set FRONTEND_URL=!FRONTEND_URL:8000=5173!
            echo    Frontend: !FRONTEND_URL!
            echo    Backend API: %%a/api/
        )
    )
) else (
    echo [ERROR] Se encontraron %ERRORS% problemas
    echo.
    echo Ejecuta primero: setup-curiosmaze-fixed.bat
    echo.
    echo PROBLEMAS ENCONTRADOS:
    echo ======================
    
    if not exist "frontend" echo - Falta carpeta frontend
    if not exist "curiosmaze_backend" echo - Falta carpeta curiosmaze_backend
    if not exist "frontend\.env" echo - Falta frontend\.env
    if not exist "curiosmaze_backend\.env" echo - Falta curiosmaze_backend\.env
    
    node --version >nul 2>&1
    if %errorlevel% neq 0 echo - Node.js no instalado
    
    python --version >nul 2>&1
    if %errorlevel% neq 0 echo - Python no instalado
    
    if not exist "frontend\node_modules" echo - Dependencias Node.js no instaladas
    if not exist "curiosmaze_backend\venv\Scripts\activate.bat" echo - Entorno virtual Python no creado
)

echo.
pause