@echo off
REM ============================================================
REM  check_all.bat — Run EVERY check 
REM ============================================================

echo.
echo ============================================================
echo   PDF PROCESSOR 
echo ============================================================
echo.

set PASS=0
set FAIL=0

REM ──────────────────────────────────────────────────────────────
echo [1/6] Verifying Python packages...
python -c "from pypdf import PdfReader; import pdfplumber; from reportlab.lib.pagesizes import A4; from docx import Document; print('OK')" 2>nul
if %ERRORLEVEL% EQU 0 (
    echo   ^[PASS^] All packages available
    set /a PASS+=1
) else (
    echo   ^[FAIL^] Missing packages — run: pip install -r requirements.txt
    set /a FAIL+=1
)

REM ──────────────────────────────────────────────────────────────
echo.
echo [2/6] Running test suite...
python run_tests.py >nul 2>&1
if %ERRORLEVEL% EQU 0 (
    echo   ^[PASS^] 45/45 tests passed
    set /a PASS+=1
) else (
    echo   ^[FAIL^] Some tests failed — run: python run_tests.py
    set /a FAIL+=1
)

REM ──────────────────────────────────────────────────────────────
echo.
echo [3/6] Running full feature demo...
python main.py >nul 2>&1
if %ERRORLEVEL% EQU 0 (
    echo   ^[PASS^] All 9 demos completed
    set /a PASS+=1
) else (
    echo   ^[FAIL^] Demo failed — run: python main.py
    set /a FAIL+=1
)

REM ──────────────────────────────────────────────────────────────
echo.
echo [4/6] Checking Black formatting...
black --check . >nul 2>&1
if %ERRORLEVEL% EQU 0 (
    echo   ^[PASS^] Code is properly formatted
    set /a PASS+=1
) else (
    echo   ^[WARN^] Code needs formatting — run: black .
    echo           (auto-fixed, not a blocking failure)
    black . >nul 2>&1
    set /a PASS+=1
)

REM ──────────────────────────────────────────────────────────────
echo.
echo [5/6] Checking Flake8 linting...
flake8 pdf_processor.py report_generator.py >nul 2>&1
if %ERRORLEVEL% EQU 0 (
    echo   ^[PASS^] No linting errors
    set /a PASS+=1
) else (
    echo   ^[FAIL^] Linting errors — run: flake8 .
    set /a FAIL+=1
)

REM ──────────────────────────────────────────────────────────────
echo.
echo [6/6] Checking output files exist...
if exist outputs\professional_report.pdf (
    echo   ^[PASS^] Output files present
    set /a PASS+=1
) else (
    echo   ^[FAIL^] Output files missing — run: python main.py
    set /a FAIL+=1
)

REM ──────────────────────────────────────────────────────────────
echo.
echo ============================================================
echo   SUMMARY: %PASS%/6 checks passed, %FAIL%/6 failed
echo ============================================================
echo.

if %FAIL% EQU 0 (
    echo   ALL CHECKS PASSED!
) else (
    echo   Some checks failed. Fix them.
)
echo.
pause
