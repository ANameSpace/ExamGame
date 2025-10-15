@echo off
title StudentGame

REM Проверка наличия Python
where python >nul 2>nul
if errorlevel 1 (
    echo Python not found.
    pause
    exit /b
)

REM Проверка наличия виртуального окружения
if not exist ".venv" (
    python -m venv .venv
    call .venv\Scripts\activate.bat
    pip install --upgrade pip
    pip install -r requirements.txt
)

.\.venv\Scripts\python.exe .\main.py


pause