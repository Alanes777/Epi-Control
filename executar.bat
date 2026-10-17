@echo off
chcp 65001 > nul
title EPI Control — Sistema de Gerenciamento de EPIs

echo ========================================================
echo       EPI Control — Sistema de Gerenciamento de EPIs
echo ========================================================
echo.
echo Iniciando servidor Django e abrindo o navegador...
echo.

start "" "http://127.0.0.1:8000"
python manage.py runserver 127.0.0.1:8000

pause
