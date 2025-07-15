REM =================================================================
REM ARCHIVO: /scripts/dev-reset.bat (Windows)
REM Script para reiniciar completamente el entorno
REM =================================================================

@echo off
echo ========================================
echo    CURIOSMAZE - Reset Completo
echo ========================================
echo.

echo ADVERTENCIA: Esto eliminará todos los datos!
echo.
set /p confirm="¿Está seguro? (s/N): "
if /i "%confirm%" neq "s" (
    echo Operación cancelada.
    pause
    exit /b
)

echo.
echo Deteniendo y eliminando contenedores...
docker-compose down -v --remove-orphans

echo.
echo Eliminando imágenes de CURIOSMAZE...
docker images curiosmaze* -q | xargs docker rmi -f 2>nul

echo.
echo Limpiando volúmenes huérfanos...
docker volume prune -f

echo.
echo Reconstruyendo y iniciando...
docker-compose up -d --build

echo.
echo Reset completo finalizado!
echo.
pause