@echo off
echo ===============================
echo   Запуск TelegramBot + API
echo ===============================

REM Активируем виртуальное окружение
call .venv\Scripts\activate

echo.
echo ---- Запуск API и BOT ----
start "API Server" cmd /k "uvicorn api:app --reload --host 0.0.0.0 --port 8000"
timeout /t 3
start "Telegram Bot" cmd /k "python bot.py"

echo.
echo Все процессы запущены!
echo API: http://localhost:8000
pause