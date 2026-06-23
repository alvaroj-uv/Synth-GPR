@echo off
cd /d "d:\Codigo\Synth-GPR"

call C:\Users\barba\miniconda3\Scripts\activate.bat gprMax >nul 2>&1

echo Running gprMax: start_fresh_reduced.in
python -m gprMax start_fresh_reduced.in

if %errorlevel% equ 0 (
    for %%F in ("start_fresh_reduced.out") do (
        echo.
        echo [OK] Output: start_fresh_reduced.out (%%~zF bytes)
    )
)
