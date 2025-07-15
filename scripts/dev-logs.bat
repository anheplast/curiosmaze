REM =================================================================
REM ARCHIVO: /scripts/dev-logs.bat (Windows)
REM Script para ver logs en tiempo real
REM =================================================================

@echo off
echo ========================================
echo     CURIOSMAZE - Logs en Tiempo Real
echo ========================================
echo.
echo Presiona Ctrl+C para salir
echo.
docker-compose logs -f