@echo off
echo ============================================================
echo   AGENDADOR DIARIO - SCRAPER LIGAPOKEMON
echo ============================================================
echo.

set TASK_NAME=LigaPokemonScraper
set SCRIPT_DIR=%~dp0
set PYTHON_EXEC=python

echo Configurando tarefa agendada para rodar diariamente as 20:00...
echo (Com opcao de executar na primeira inicializacao caso o PC estivesse desligado)
echo Diretorio: %SCRIPT_DIR%
echo.

schtasks /Create /TN "%TASK_NAME%" /TR "cmd.exe /c cd /d %SCRIPT_DIR% && %PYTHON_EXEC% scraper.py >> data\scheduler.log 2>&1" /SC DAILY /ST 20:00 /F

if %ERRORLEVEL% EQU 0 (
    echo.
    echo [SUCESSO] Tarefa agendada com sucesso!
    echo Nome da tarefa: %TASK_NAME%
    echo Frequencia: Diariamente as 20:00
    echo Log de execucao sera salvo em: data\scheduler.log
) else (
    echo.
    echo [ALERTA] Falha ao criar a tarefa agendada no Windows.
)

echo.
pause
