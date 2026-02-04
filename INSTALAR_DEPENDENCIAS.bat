@echo off
title Instalador de Dependencias AbletonOSC
echo ==========================================
echo    Instalando Dependencias Python...
echo ==========================================
echo.

:: Verifica Python
python --version >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo [ERRO] Python nao encontrado no PATH.
    echo Por favor, instale o Python e marque a opcao "Add Python to PATH".
    echo O instalador pode ser baixado em python.org
    pause
    exit /b
)

:: Instala Requerimentos
echo Instalando bibliotecas (pode demorar um pouco)...
pip install -r python\requirements.txt

if %ERRORLEVEL% EQU 0 (
    echo.
    echo [SUCESSO] Todas as dependencias foram instaladas!
    echo Agora voce pode rodar o arquivo 'INICIAR_PROJETO.bat'
) else (
    echo.
    echo [ERRO] Houve um problema na instalacao. Verifique a conexao ou erros acima.
)

pause
