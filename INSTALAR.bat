@echo off
chcp 65001 >nul
title Motion Design Kit - Instalacion
echo.
echo  Instalando el Motion Design Kit...
echo.
powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0instalar.ps1" %*
echo.
pause
