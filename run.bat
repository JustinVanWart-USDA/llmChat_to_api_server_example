@echo off
REM Start the GovChat API Server

echo.
echo ============================================================
echo  GovChat API Server Launcher
echo ============================================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    pause
    exit /b 1
)

REM Check if requirements are installed
echo [*] Checking dependencies...
pip list | findstr "fastapi uvicorn requests" >nul
if errorlevel 1 (
    echo [!] Installing dependencies from requirements.txt...
    pip install -r requirements.txt
    if errorlevel 1 (
        echo ERROR: Failed to install dependencies
        pause
        exit /b 1
    )
)

REM Run the server
echo.
echo [*] Starting server...
echo [*] Server will be available at: http://127.0.0.1:8000
echo [*] API docs at: http://127.0.0.1:8000/docs
echo.
python run.py

pause
