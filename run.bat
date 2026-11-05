@echo off
REM ==============================================================================
REM Virtual Chemistry Laboratory — Windows Launcher Script
REM ==============================================================================

cd /d "%~dp0"

if "%1"=="test" (
    echo Running Virtual Titration Laboratory Automated Test Suite...
    set PYTHONPATH=%CD%
    python -m pytest tests/ -v
    pause
    exit /b %ERRORLEVEL%
)

echo Launching Virtual Chemistry Laboratory (HCl-NaOH Titration)...
set PYTHONPATH=%CD%
python main.py %*
pause
