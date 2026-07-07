@echo off
echo.
echo   Big Mamba Installer
echo   ===================
echo.

where python >nul 2>nul
if %errorlevel% neq 0 (
    echo   Error: Python is not installed.
    echo.
    echo   Install Python first:
    echo     winget install Python.Python.3
    echo.
    echo   Or download from https://python.org/downloads
    echo.
    pause
    exit /b 1
)

for /f "tokens=2" %%i in ('python --version 2^>^&1') do set PYVER=%%i
echo   Found Python %PYVER%

echo   Installing Big Mamba...
echo.
pip install big-mamba-lang

if %errorlevel% neq 0 (
    echo.
    echo   Error: Installation failed.
    echo   Try running as Administrator or use: python -m pip install big-mamba-lang
    pause
    exit /b 1
)

echo.
echo   Big Mamba installed successfully.
echo.
echo   Quick start:
echo     mamba repl              Start interactive mode
echo     mamba run file.mamba    Run a program
echo     mamba help              Show all commands
echo.
pause
