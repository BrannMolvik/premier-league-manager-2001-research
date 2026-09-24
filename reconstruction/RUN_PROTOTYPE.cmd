@echo off
setlocal
cd /d "%~dp0"
where py >nul 2>nul && (py -3 app.py %* & exit /b %errorlevel%)
where python >nul 2>nul && (python app.py %* & exit /b %errorlevel%)
echo Python 3 was not found.
pause
