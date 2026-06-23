@echo off
cd /d "d:\Codigo\Synth-GPR"

call C:\Users\barba\miniconda3\Scripts\activate.bat gprMax >nul 2>&1

echo Running gprMax: Fouled Ballast Model (eps=9.5)
python -m gprMax start_fresh_fouled.in

if %errorlevel% equ 0 (
    for %%F in ("start_fresh_fouled.out") do (
        echo.
        echo [OK] Output: start_fresh_fouled.out (%%~zF bytes)
    )
)
