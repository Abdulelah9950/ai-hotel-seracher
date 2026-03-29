@echo off
REM AI Hotel Booking Chatbot - Server Startup Script

echo.
echo ============================================================
echo Starting AI Hotel Booking Chatbot Server...
echo ============================================================
echo.

REM Navigate to backend directory
cd /d "%~dp0backend"

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python and try again
    pause
    exit /b 1
)

REM Start Flask server
echo Starting Flask server...
echo Server will be available at: http://127.0.0.1:5000
echo.
python app.py

REM Keep window open if there's an error
pause
