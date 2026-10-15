@echo off
cd /d "%~dp0"
echo Installing PulseTwin frontend dependencies...
npm install
if errorlevel 1 goto failed
npm run dev
goto end
:failed
echo Dependency installation failed. Check your internet connection and Node.js/npm installation.
:end
pause
