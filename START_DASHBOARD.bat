@echo off
title AbletonOSC Dashboard
echo ==========================================
echo    Iniciando AbletonOSC Dashboard
echo    - Controle de Logs
echo    - Selecao MIDI
echo    - Servidor Integrado
echo ==========================================
echo.

:: Limpeza de Processos Antigos
echo Matando processos antigos (Python, OSC)...
taskkill /F /IM python.exe >nul 2>&1
taskkill /F /IM open-stage-control.exe >nul 2>&1
taskkill /F /IM node.exe >nul 2>&1
timeout /t 1 /nobreak >nul

:: Verifica se Python esta no PATH
python --version >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo [ERRO] Python nao encontrado no PATH.
    pause
    exit /b
)

:: Inicia o Dashboard
echo Iniciando Dashboard GUI...
start "AbletonOSC Dashboard" python "%~dp0python\dashboard.py"

exit
