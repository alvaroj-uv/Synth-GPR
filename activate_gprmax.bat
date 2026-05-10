@echo off
:: ============================================================
::  activate_gprmax.bat
::  Opens an interactive shell with the gprMax conda environment
::  activated and the project root on the PYTHONPATH.
:: ============================================================

set "CONDA_ROOT=C:\ProgramData\miniconda3"
set "ENV_NAME=gprMax"
set "PROJECT_ROOT=%~dp0"

:: -- Initialise conda for cmd --
call "%CONDA_ROOT%\Scripts\activate.bat" "%CONDA_ROOT%"

:: -- Activate the target environment --
call conda activate %ENV_NAME%

if errorlevel 1 (
    echo.
    echo [ERROR] Could not activate conda environment "%ENV_NAME%".
    echo         Make sure Miniconda is installed at %CONDA_ROOT%
    echo         and the environment exists: conda env list
    pause
    exit /b 1
)

:: -- Add project root to PYTHONPATH so src/ imports work --
set "PYTHONPATH=%PROJECT_ROOT%;%PYTHONPATH%"

echo.
echo [OK] Environment "%ENV_NAME%" is active.
echo      Project root : %PROJECT_ROOT%
echo      Python       : 
python --version
echo.
echo      Type 'deactivate' to leave the environment.
echo      Type 'exit'  to close this window.
echo.

:: -- Keep the shell open --
cmd /k
