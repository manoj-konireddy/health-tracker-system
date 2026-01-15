@echo off
REM Health Tracker Startup Script for Windows

echo ================================
echo Health Tracker System
echo ================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo Error: Python is not installed or not in PATH
    echo Please install Python 3.7 or higher
    pause
    exit /b 1
)

echo ^✓ Python found
echo.

REM Install/update dependencies
echo Installing dependencies...
pip install -r requirements.txt

if %errorlevel% neq 0 (
    echo ^✗ Failed to install dependencies
    pause
    exit /b 1
)

echo ^✓ Dependencies installed successfully
echo.

echo ================================
echo Starting Health Tracker...
echo ================================
echo.
echo The application will be available at: http://localhost:5000
echo.
echo Press Ctrl+C to stop the server
echo.

REM Run the Flask app
python app.py

pause
