@echo off
setlocal

:: ============================================================
:: Run v2 (fouling matrix) + background reference — 2026-06-29
:: Conda env: gprMax  |  Miniconda: C:\Users\barba\miniconda3
:: ============================================================

set CONDA_ROOT=C:\Users\barba\miniconda3
set CONDA_ENV=gprMax
set EXP=%~dp0
set LOG=%EXP%run_log_v2_and_bg.txt

echo ============================================================ > "%LOG%"
echo v2 + background run >> "%LOG%"
echo Started: %date% %time% >> "%LOG%"
echo ============================================================ >> "%LOG%"

call "%CONDA_ROOT%\Scripts\activate.bat" "%CONDA_ENV%"
if errorlevel 1 ( echo ERROR activating conda & exit /b 1 )

echo Running v2 (fouling matrix, with rocks)...
echo --- v2 --- >> "%LOG%"
python -m gprMax "%EXP%from_picks_pk20000m_v2.in" >> "%LOG%" 2>&1

echo Running background (no layers, no rocks)...
echo --- background --- >> "%LOG%"
python -m gprMax "%EXP%from_picks_pk20000m_bg.in" >> "%LOG%" 2>&1

echo ============================================================ >> "%LOG%"
echo Finished: %date% %time% >> "%LOG%"
echo ============================================================ >> "%LOG%"

echo Done. Log: %LOG%
pause
