@echo off
chcp 65001 > nul
echo Executando Scraper da LigaPokemon...
cd /d %~dp0
python scraper.py
echo.
pause
