@echo off
cd /d "d:\Codigo\Synth-GPR"

call C:\Users\barba\miniconda3\Scripts\activate.bat gprMax >nul 2>&1

echo Running gprMax: Clean Ballast WITH ROCKS (135 polygonal rocks)
python -m gprMax start_fresh_with_rocks_correct.in

if %errorlevel% equ 0 (
    for %%F in ("start_fresh_with_rocks_correct.out") do (
        echo [OK] Output: start_fresh_with_rocks_correct.out (%%~zF bytes)
    )
)
