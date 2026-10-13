@echo off
chcp 65001 >nul
title OpenCode Terminal [Akademik Yayın - EVREN H200]
echo ======================================================================
echo   🚀 OpenCode Terminal (Akademik Yayın Projesi - EVREN H200)
echo   Model: DeepSeek V4.1 Flash (1M Bağlam - 15M Günlük Ücretsiz Kota)
echo   Dizin: %~dp0
echo   Yetki: God-Mode Sınırsız Kodlama, Analiz ve Terminal İzni
echo ======================================================================
echo.

:: .env dosyasından EVREN_API_KEY oku
if exist "%~dp0.env" (
    for /f "usebackq tokens=1,* delims==" %%A in ("%~dp0.env") do (
        if "%%A"=="EVREN_API_KEY" set "EVREN_API_KEY=%%B"
    )
)
if "%EVREN_API_KEY%"=="" (
    if exist "C:\Users\Mustafa\OneDrive\Masaüstü\opencode\.env" (
        for /f "usebackq tokens=1,* delims==" %%A in ("C:\Users\Mustafa\OneDrive\Masaüstü\opencode\.env") do (
            if "%%A"=="EVREN_API_KEY" set "EVREN_API_KEY=%%B"
        )
    )
)

cd /d "%~dp0"
call opencode -m evren/deepseek-v4.1-flash %*

if %ERRORLEVEL% NEQ 0 (
    echo.
    echo ======================================================================
    echo [!] OpenCode kapandı (Exit Code: %ERRORLEVEL%).
    echo ======================================================================
    pause
)
