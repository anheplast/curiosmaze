@echo off
cls
echo =====================================================
echo           CURIOSMAZE - PROBADOR DE JUDGE0
echo =====================================================
echo.
echo Este script verifica que Judge0 este funcionando correctamente
echo.

REM Leer configuracion de Judge0 del .env
set JUDGE0_URL=
if exist "curiosmaze_backend\.env" (
    for /f "tokens=2 delims==" %%a in ('findstr "JUDGE0_API_URL" curiosmaze_backend\.env') do (
        set JUDGE0_URL=%%a
    )
) else if exist "frontend\.env" (
    for /f "tokens=2 delims==" %%a in ('findstr "VITE_JUDGE0_API_URL" frontend\.env') do (
        set JUDGE0_URL=%%a
    )
) else (
    echo [ERROR] No se encontraron archivos de configuracion
    echo Ejecuta primero: setup-curiosmaze-fixed.bat
    pause
    exit /b 1
)

if "%JUDGE0_URL%"=="" (
    echo [ERROR] No se pudo obtener la URL de Judge0
    pause
    exit /b 1
)

echo [INFO] Probando Judge0 en: %JUDGE0_URL%
echo.

REM Extraer IP y puerto
for /f "tokens=3 delims=:/" %%a in ("%JUDGE0_URL%") do set JUDGE0_IP=%%a
for /f "tokens=4 delims=:" %%a in ("%JUDGE0_URL%") do set JUDGE0_PORT=%%a

echo [TEST] 1. Probando conectividad de red...
ping -n 1 %JUDGE0_IP% >nul 2>&1
if %errorlevel% equ 0 (
    echo [OK] IP %JUDGE0_IP% es accesible
) else (
    echo [WARNING] No se pudo hacer ping a %JUDGE0_IP%
    echo          Esto puede ser normal si el servidor no responde ping
)

echo.
echo [TEST] 2. Probando puerto %JUDGE0_PORT%...
REM Usar netstat para verificar si el puerto está abierto localmente
netstat -an | findstr ":%JUDGE0_PORT%" >nul 2>&1
if %errorlevel% equ 0 (
    echo [OK] Puerto %JUDGE0_PORT% parece estar en uso (buena señal)
) else (
    echo [INFO] Puerto %JUDGE0_PORT% no detectado localmente
    echo        Esto es normal si Judge0 está en otro servidor
)

echo.
echo [TEST] 3. Probando API de Judge0...

REM Verificar si curl está disponible
curl --version >nul 2>&1
if %errorlevel% equ 0 (
    echo [INFO] Usando curl para probar API...
    
    REM Probar endpoint de información de Judge0
    curl -s -m 10 "%JUDGE0_URL%/about" >temp_judge0_test.txt 2>&1
    
    if exist temp_judge0_test.txt (
        findstr "Judge0" temp_judge0_test.txt >nul 2>&1
        if %errorlevel% equ 0 (
            echo [OK] Judge0 API responde correctamente
            echo [INFO] Información de Judge0:
            type temp_judge0_test.txt | findstr "version"
        ) else (
            echo [ERROR] Judge0 API no responde correctamente
            echo [INFO] Respuesta recibida:
            type temp_judge0_test.txt
        )
        del temp_judge0_test.txt
    ) else (
        echo [ERROR] No se pudo conectar con Judge0
    )
) else (
    echo [INFO] curl no disponible, probando con PowerShell...
    
    REM Usar PowerShell como alternativa
    powershell -command "try { $response = Invoke-WebRequest -Uri '%JUDGE0_URL%/about' -TimeoutSec 10; if ($response.Content -like '*Judge0*') { Write-Host '[OK] Judge0 API responde correctamente' } else { Write-Host '[ERROR] Judge0 API no responde correctamente' } } catch { Write-Host '[ERROR] No se pudo conectar con Judge0:', $_.Exception.Message }"
)

echo.
echo [TEST] 4. Probando lenguajes disponibles...

if exist "curiosmaze_backend" (
    cd curiosmaze_backend
    
    if exist "venv\Scripts\activate.bat" (
        echo [INFO] Probando desde Python...
        call venv\Scripts\activate.bat
        
        REM Crear script Python temporal para probar Judge0
        echo import requests > temp_test_judge0.py
        echo import os >> temp_test_judge0.py
        echo from dotenv import load_dotenv >> temp_test_judge0.py
        echo. >> temp_test_judge0.py
        echo load_dotenv('.env') >> temp_test_judge0.py
        echo judge0_url = os.environ.get('JUDGE0_API_URL', '%JUDGE0_URL%') >> temp_test_judge0.py
        echo. >> temp_test_judge0.py
        echo try: >> temp_test_judge0.py
        echo     response = requests.get(f"{judge0_url}/languages", timeout=10) >> temp_test_judge0.py
        echo     if response.status_code == 200: >> temp_test_judge0.py
        echo         languages = response.json() >> temp_test_judge0.py
        echo         python_langs = [lang for lang in languages if 'python' in lang.get('name', '').lower()] >> temp_test_judge0.py
        echo         print(f"[OK] Judge0 tiene {len(languages)} lenguajes disponibles") >> temp_test_judge0.py
        echo         print(f"[INFO] Lenguajes Python: {len(python_langs)}") >> temp_test_judge0.py
        echo         for lang in python_langs[:3]:  # Solo mostrar primeros 3 >> temp_test_judge0.py
        echo             print(f"      - {lang.get('name')} (ID: {lang.get('id')})") >> temp_test_judge0.py
        echo     else: >> temp_test_judge0.py
        echo         print(f"[ERROR] Judge0 respondió con código: {response.status_code}") >> temp_test_judge0.py
        echo except Exception as e: >> temp_test_judge0.py
        echo     print(f"[ERROR] Error conectando con Judge0: {e}") >> temp_test_judge0.py
        
        python temp_test_judge0.py
        del temp_test_judge0.py
    ) else (
        echo [WARNING] Entorno virtual no encontrado
    )
    
    cd ..
)

echo.
echo =====================================================
echo                 RESUMEN DE PRUEBAS
echo =====================================================
echo.
echo Judge0 URL: %JUDGE0_URL%
echo IP: %JUDGE0_IP%
echo Puerto: %JUDGE0_PORT%
echo.
echo RECOMENDACIONES:
echo ================
echo.
echo 1. Si Judge0 no responde:
echo    - Verifica que Judge0 esté ejecutándose
echo    - Revisa la IP y puerto en la configuración
echo    - Verifica que no haya firewall bloqueando
echo.
echo 2. Para instalar Judge0 localmente:
echo    - Sigue la documentación oficial: https://github.com/judge0/judge0
echo    - O usa Docker: docker run -p 2358:2358 judge0/judge0
echo.
echo 3. Si todo funciona:
echo    - Judge0 está listo para CURIOSMAZE
echo    - Puedes proceder a usar la aplicación
echo.
pause