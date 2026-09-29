@echo off
setlocal
cd /d "%~dp0"
where py >nul 2>nul && (py -3 playable_snapshot.py %* & exit /b %errorlevel%)
where python >nul 2>nul && (python playable_snapshot.py %* & exit /b %errorlevel%)
echo Python 3 was not found.
pause
