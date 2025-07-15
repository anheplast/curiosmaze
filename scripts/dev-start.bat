REM =================================================================
REM ARCHIVO: /scripts/dev-start.bat (Windows)
REM Script para iniciar el entorno de desarrollo
REM =================================================================

@echo off
echo ========================================
echo    CURIOSMAZE - Inicio Desarrollo
echo ========================================
echo.

echo Iniciando contenedores de desarrollo...
docker-compose up -d

echo.
echo Esperando a que los servicios estén listos...
timeout /t 10 /nobreak

echo.
echo Estado de los contenedores:
docker-compose ps

echo.
echo URLs disponibles:
echo   Frontend: http://localhost:5173
echo   Backend API: http://localhost:8000/api
echo   Admin Django: http://localhost:8000/admin
echo   PostgreSQL: localhost:5432
echo.
echo Entorno de desarrollo listo!
echo.
pause