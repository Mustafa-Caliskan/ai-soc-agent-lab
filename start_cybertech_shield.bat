@echo off
cd /d "%~dp0"
title CyberTech Neural Shield Server (Gemini 3.6 Flash)
echo ========================================================
echo   CyberTech Neural Shield - 3-Katmanli Guvenlik Ag Gecidi
echo   Model: XLM-RoBERTa ONNX INT8 + Google Gemini 3.6 Flash
echo ========================================================
echo.
echo Sunucu baslatiliyor: http://127.0.0.1:8000
echo - SkyPort Portali:        http://localhost:8000/
echo - Red Team Attack Lab:     http://localhost:8000/red
echo - Live Pipeline:           http://localhost:8000/pipeline
echo - Blue Team SOC Dashboard: http://localhost:8000/blue
echo.
python -m uvicorn main:app --app-dir ./backend --host 127.0.0.1 --port 8000
pause
