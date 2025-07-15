REM =================================================================
REM ARCHIVO: /scripts/backup.bat (Windows)
REM Script para crear backup de la base de datos
REM =================================================================

@echo off
echo ========================================
echo      CURIOSMAZE - Backup Database
echo ========================================
echo.

set backup_date=%date:~-4,4%%date:~-10,2%%date:~-7,2%_%time:~0,2%%time:~3,2%
set backup_date=%backup_date: =0%

echo Creando backup de la base de datos...
echo Fecha: %backup_date%
echo.

if not exist backups mkdir backups

docker-compose -f docker-compose.prod.yml run --rm backup

echo.
echo Backup creado exitosamente!
echo Ubicación: ./backups/backup_%backup_date%.sql
echo.
pause