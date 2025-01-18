@echo off
cd /D "%~dp0"
call .venv\Scripts\activate.bat
python run_clenaup_workshop.py
pause
