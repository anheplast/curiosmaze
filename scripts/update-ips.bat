REM =================================================================
REM ARCHIVO: /scripts/update-ips.bat (Script para cambiar IPs fácilmente)
REM =================================================================
REM Script de Windows para actualizar IPs sin editar archivos manualmente
REM Ubicación: /curiosmaze/scripts/update-ips.bat

@echo off
echo ========================================
echo     CURIOSMAZE - Actualizar IPs
echo ========================================
echo.
echo Este script te ayudará a cambiar las IPs de los servicios
echo.

echo Configuración actual:
echo.
type ..\.env | findstr "JUDGE0_HOST\|HOST_MACHINE_IP\|DATABASE_HOST"
echo.

echo ¿Qué IP quieres cambiar?
echo.
echo 1) Judge0 (actualmente: %JUDGE0_HOST%)
echo 2) Máquina host (actualmente: %HOST_MACHINE_IP%)
echo 3) Mostrar todas las IPs configuradas
echo 4) Salir
echo.
set /p choice="Elige una opción (1-4): "

if "%choice%"=="1" goto change_judge0
if "%choice%"=="2" goto change_host
if "%choice%"=="3" goto show_all
if "%choice%"=="4" exit /b
goto invalid_choice

:change_judge0
echo.
echo Cambiar IP de Judge0
echo.
set /p new_judge0_ip="Nueva IP de Judge0 (ejemplo: 192.168.1.85): "

if "%new_judge0_ip%"=="" (
    echo IP no puede estar vacía
    pause
    exit /b
)

echo.
echo Actualizando configuración...

REM Usar PowerShell para reemplazar la línea en .env
powershell -Command "(Get-Content ..\.env) | ForEach-Object { $_ -replace '^JUDGE0_HOST=.*', 'JUDGE0_HOST=%new_judge0_ip%' } | Set-Content ..\.env"

echo IP de Judge0 actualizada a: %new_judge0_ip%
echo.
echo Necesitas reiniciar los contenedores para aplicar cambios:
echo    docker-compose down
echo    docker-compose up -d
echo.
pause
exit /b

:change_host
echo.
echo Cambiar IP de la máquina host
echo.
set /p new_host_ip="Nueva IP de tu máquina Windows (ejemplo: 192.168.1.105): "

if "%new_host_ip%"=="" (
    echo IP no puede estar vacía
    pause
    exit /b
)

echo.
echo Actualizando configuración...

powershell -Command "(Get-Content ..\.env) | ForEach-Object { $_ -replace '^HOST_MACHINE_IP=.*', 'HOST_MACHINE_IP=%new_host_ip%' } | Set-Content ..\.env"

echo IP de máquina host actualizada a: %new_host_ip%
echo.
pause
exit /b

:show_all
echo.
echo Todas las IPs configuradas:
echo.
echo Judge0:
type ..\.env | findstr "JUDGE0_HOST\|JUDGE0_PORT\|JUDGE0_API_URL"
echo.
echo Host:
type ..\.env | findstr "HOST_MACHINE_IP\|BACKEND_HOST\|FRONTEND_HOST"
echo.
echo Base de datos:
type ..\.env | findstr "DATABASE_HOST\|DATABASE_PORT"
echo.
pause
exit /b

:invalid_choice
echo Opción inválida
pause
exit /b