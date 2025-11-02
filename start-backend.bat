@echo off
REM Start Trading Journal Backend Server

echo ====================================
echo Trading Journal - Starting Backend
echo ====================================
echo.

REM Get the directory where this script is located
cd /d "%~dp0"

echo Starting FastAPI server on http://localhost:8000
echo.
echo Press Ctrl+C to stop the server
echo.
echo ====================================
echo.

REM Navigate to backend directory and start uvicorn
cd backend
python -m uvicorn main:app --host 0.0.0.0 --port 8000 --reload

pause
