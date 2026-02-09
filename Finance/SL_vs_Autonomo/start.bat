@echo off
REM Startup script for SL vs Autónomo Fiscal Simulator (Windows)
REM This script starts both the backend API and frontend dev server

echo ================================================
echo 🚀 Starting Simulador Fiscal - SL vs Autónomo
echo ================================================
echo.

cd /d %~dp0

REM Check if Python is installed
where python >nul 2>nul
if %ERRORLEVEL% NEQ 0 (
    echo ❌ Error: Python is not installed
    pause
    exit /b 1
)

REM Check if Node.js is installed
where node >nul 2>nul
if %ERRORLEVEL% NEQ 0 (
    echo ❌ Error: Node.js is not installed
    pause
    exit /b 1
)

echo 📦 Checking backend dependencies...
cd backend
if not exist venv (
    echo Creating virtual environment...
    python -m venv venv
)

call venv\Scripts\activate.bat

pip show fastapi >nul 2>nul
if %ERRORLEVEL% NEQ 0 (
    echo Installing backend dependencies...
    pip install -r requirements.txt
)
cd ..

echo 📦 Checking frontend dependencies...
cd frontend
if not exist node_modules (
    echo Installing frontend dependencies...
    call npm install
)
cd ..

echo.
echo ================================================
echo ✅ All dependencies ready!
echo ================================================
echo.

REM Start backend in new window
echo 🔧 Starting Backend API on http://localhost:8000
cd backend
start "Backend API" cmd /k "venv\Scripts\activate.bat && python -m uvicorn main:app --reload --host 127.0.0.1 --port 8000"
cd ..

REM Wait for backend to start
timeout /t 3 /nobreak >nul

REM Start frontend in new window
echo 🎨 Starting Frontend on http://localhost:5173
cd frontend
start "Frontend App" cmd /k "npm run dev"
cd ..

echo.
echo ================================================
echo ✨ Servers are running in separate windows!
echo ================================================
echo.
echo 📊 Backend API:     http://localhost:8000
echo 📚 API Docs:        http://localhost:8000/docs
echo 🌐 Frontend App:    http://localhost:5173
echo.
echo Close the command windows to stop the servers
echo ================================================
echo.

REM Open browser
timeout /t 2 /nobreak >nul
start http://localhost:5173

pause
