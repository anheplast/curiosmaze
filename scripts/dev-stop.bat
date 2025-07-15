REM =================================================================
REM ARCHIVO: /scripts/dev-stop.bat (Windows)  
REM Script para detener el entorno de desarrollo
REM =================================================================

@echo off
echo ========================================
echo   CURIOSMAZE - Detener Desarrollo
echo ========================================
echo.

echo Deteniendo contenedores de desarrollo...
docker-compose down

echo.
echo Contenedores detenidos correctamente!
echo.
pause