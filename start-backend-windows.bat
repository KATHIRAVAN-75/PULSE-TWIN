@echo off
cd /d "%~dp0\backend"
if not exist .venv python -m venv .venv
call .venv\Scripts\activate.bat
python -m pip install -r requirements.txt
if errorlevel 1 goto failed
uvicorn app.main:app --reload --port 8000
goto end
:failed
echo Backend setup failed. Check your Python and pip installation.
:end
pause
