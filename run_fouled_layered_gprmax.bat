@echo off
cd /d "d:\Codigo\Synth-GPR"

call C:\Users\barba\miniconda3\Scripts\activate.bat gprMax >nul 2>&1

python -m gprMax start_fresh_fouled_layered.in

if %errorlevel% equ 0 (
    for %%F in ("start_fresh_fouled_layered.out") do (
        echo [OK] Output: start_fresh_fouled_layered.out (%%~zF bytes)
    )
)
