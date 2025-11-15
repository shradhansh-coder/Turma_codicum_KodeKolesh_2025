@echo off
REM run.bat - Quick start script for Windows

echo.
echo 🚀 Legal Document Intelligence MVP - Quick Start
echo ==================================================
echo.

REM Check Python
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python not found. Please install Python 3.9+
    exit /b 1
)

REM Check Node
node --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Node.js not found. Please install Node.js 16+
    exit /b 1
)

echo ✅ Python and Node found
echo.

REM Start Backend
echo 📦 Starting Backend (Flask)...
cd backend

if not exist "venv" (
    echo Creating virtual environment...
    python -m venv venv
)

call venv\Scripts\activate.bat
pip install -r requirements.txt >nul 2>&1

start "Backend Server" python app.py
echo ✅ Backend running on http://localhost:5000

REM Wait for backend
timeout /t 2 /nobreak >nul

cd ..\frontend

REM Start Frontend
echo 🎨 Starting Frontend (React)...

if not exist "node_modules" (
    echo Installing dependencies...
    npm install >nul 2>&1
)

start "Frontend Server" npm start
echo ✅ Frontend running on http://localhost:3000

echo.
echo ==================================================
echo 🎉 MVP is ready!
echo.
echo Browser: http://localhost:3000
echo API: http://localhost:5000/api
echo.
echo Close this window to stop servers
echo ==================================================
echo.

pause
