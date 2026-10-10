@echo off
chcp 65001 > nul
echo ============================================================
echo   INICIANDO DASHBOARD DA COLEÇÃO LIGAPOKEMON
echo ============================================================
echo.
echo Servidor rodando em: http://127.0.0.1:5050
echo Visão Geral:         http://127.0.0.1:5050/dashboard.html
echo Busca de Cartas:     http://127.0.0.1:5050/collections.html
echo.

cd /d %~dp0

start "" "http://127.0.0.1:5050"
python server.py

pause
