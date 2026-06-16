@echo off
REM Test multiple antenna heights with gprMax
REM Creates .in files for each height, runs them, and compares correlations

cd /d d:\Codigo\Synth-GPR

mkdir output_test\antenna_height_sweep

echo.
echo ========================================================================
echo ANTENNA HEIGHT SWEEP TEST - Manual Batch Execution
echo ========================================================================
echo.

REM Height 1: 1.0 cm (antenna_clearance = 0.02)
echo [1/8] Testing 1.0cm antenna height...
python scripts/pipeline/generate_in_files.py examples/DEFAULT.toml -o output_test\antenna_height_sweep\height_1cm.in
python -m gprMax output_test\antenna_height_sweep\height_1cm.in 2>&1 | find "Simulation completed" || echo [FAIL] gprMax height 1cm

REM Height 2: 2.5 cm (antenna_clearance = 0.05)
echo [2/8] Testing 2.5cm antenna height...
python scripts/pipeline/generate_in_files.py examples/DEFAULT_with_ballast.toml -o output_test\antenna_height_sweep\height_2.5cm.in
python -m gprMax output_test\antenna_height_sweep\height_2.5cm.in 2>&1 | find "Simulation completed" || echo [FAIL] gprMax height 2.5cm

REM Height 3: 5.0 cm (antenna_clearance = 0.1, DEFAULT)
echo [3/8] Testing 5.0cm antenna height (DEFAULT)...
python scripts/pipeline/generate_in_files.py examples/DEFAULT.toml -o output_test\antenna_height_sweep\height_5cm.in
python -m gprMax output_test\antenna_height_sweep\height_5cm.in 2>&1 | find "Simulation completed" || echo [FAIL] gprMax height 5cm

REM Height 4: 10 cm (antenna_clearance = 0.2)
echo [4/8] Testing 10cm antenna height...
for /f "tokens=*" %%i in ('python -c "
content = open('examples/DEFAULT.toml').read()
content = content.replace('antenna_clearance = 0.1', 'antenna_clearance = 0.2')
with open('output_test/height_10cm.toml', 'w') as f:
    f.write(content)
print('OK')
"') do set result=%%i
python scripts/pipeline/generate_in_files.py output_test/height_10cm.toml -o output_test\antenna_height_sweep\height_10cm.in
python -m gprMax output_test\antenna_height_sweep\height_10cm.in 2>&1 | find "Simulation completed" || echo [FAIL] gprMax height 10cm

REM Height 5: 15 cm (antenna_clearance = 0.3)
echo [5/8] Testing 15cm antenna height...
for /f "tokens=*" %%i in ('python -c "
content = open('examples/DEFAULT.toml').read()
content = content.replace('antenna_clearance = 0.1', 'antenna_clearance = 0.3')
with open('output_test/height_15cm.toml', 'w') as f:
    f.write(content)
print('OK')
"') do set result=%%i
python scripts/pipeline/generate_in_files.py output_test/height_15cm.toml -o output_test\antenna_height_sweep\height_15cm.in
python -m gprMax output_test\antenna_height_sweep\height_15cm.in 2>&1 | find "Simulation completed" || echo [FAIL] gprMax height 15cm

REM Height 6: 20 cm (antenna_clearance = 0.4)
echo [6/8] Testing 20cm antenna height...
for /f "tokens=*" %%i in ('python -c "
content = open('examples/DEFAULT.toml').read()
content = content.replace('antenna_clearance = 0.1', 'antenna_clearance = 0.4')
with open('output_test/height_20cm.toml', 'w') as f:
    f.write(content)
print('OK')
"') do set result=%%i
python scripts/pipeline/generate_in_files.py output_test/height_20cm.toml -o output_test\antenna_height_sweep\height_20cm.in
python -m gprMax output_test\antenna_height_sweep\height_20cm.in 2>&1 | find "Simulation completed" || echo [FAIL] gprMax height 20cm

echo.
echo ========================================================================
echo Generated .out files (compare manually with visualization scripts)
echo ========================================================================
echo.
dir output_test\antenna_height_sweep\*.out
echo.
echo Next: Run visualization script to compare correlations
echo python scripts/16_ballast_coda_comparison.py [output1] [output2] data.DZT
echo.
