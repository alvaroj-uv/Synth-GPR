@echo off
setlocal

:: ============================================================
:: Run EFE picks model v2 (fouling matrix) — experiment 2026-06-29
:: Conda env: gprMax  |  Miniconda: C:\Users\barba\miniconda3
:: ============================================================

set CONDA_ROOT=C:\Users\barba\miniconda3
set CONDA_ENV=gprMax
set IN_FILE=%~dp0from_picks_pk20000m_v2.in
set LOG_FILE=%~dp0run_log_v2.txt

echo ============================================================ > "%LOG_FILE%"
echo EFE picks model v2 - fouling matrix gprMax run >> "%LOG_FILE%"
echo Started: %date% %time% >> "%LOG_FILE%"
echo File: %IN_FILE% >> "%LOG_FILE%"
echo ============================================================ >> "%LOG_FILE%"

call "%CONDA_ROOT%\Scripts\activate.bat" "%CONDA_ENV%"
if errorlevel 1 (
    echo ERROR: Could not activate conda env "%CONDA_ENV%"
    exit /b 1
)

echo Running simulation...
python -m gprMax "%IN_FILE%" >> "%LOG_FILE%" 2>&1

echo ============================================================ >> "%LOG_FILE%"
echo Finished: %date% %time% >> "%LOG_FILE%"
echo ============================================================ >> "%LOG_FILE%"

echo Done. Log: %LOG_FILE%
pause
