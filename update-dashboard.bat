@echo off
REM Trading Journal - Auto Update Dashboard
REM This script scans the CSV folder and updates the database

echo ====================================
echo Trading Journal - Dashboard Update
echo ====================================
echo.

REM Get the directory where this script is located
cd /d "%~dp0"

echo [1/3] Checking backend service...
echo.

REM Check if backend is running (optional - will start if needed)
curl -s http://localhost:8000/ >nul 2>&1
if %errorlevel% neq 0 (
    echo Backend is not running. Please start it first with: start-backend.bat
    echo.
    pause
    exit /b 1
)

echo Backend is running!
echo.

echo [2/3] Scanning CSV folder for new files...
echo.

REM Trigger folder scan via API
curl -X POST "http://localhost:8000/api/scan-folder" -H "Content-Type: application/json"

echo.
echo.
echo [3/3] Dashboard updated successfully!
echo.
echo You can now refresh your web browser to see the latest data.
echo Dashboard URL: http://localhost:3000
echo.
echo ====================================

pause
