REM =================================================================
REM ARCHIVO: /scripts/monitor.bat (Windows)  
REM Script para monitorear el sistema
REM =================================================================

@echo off
:monitor
cls
echo ========================================
echo     CURIOSMAZE - Monitor Sistema
echo ========================================
echo.
echo Actualizado: %date% %time%
echo.

echo Estado de Contenedores:
docker-compose ps
echo.

echo Uso de Memoria:
docker stats --no-stream --format "table {{.Container}}\t{{.CPUPerc}}\t{{.MemUsage}}" curiosmaze*
echo.

echo Espacio en Disco:
docker system df
echo.

echo Actualizando en 30 segundos... (Ctrl+C para salir)
timeout /t 30 /nobreak
goto monitor