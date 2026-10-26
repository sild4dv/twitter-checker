@echo off
cd /d "%~dp0"
:loop
python bot.py
echo Bot caiu, reiniciando em 10 segundos...
timeout /t 10
goto loop
