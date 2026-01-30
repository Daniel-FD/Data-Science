#!/bin/bash

# Startup script for SL vs Autónomo Fiscal Simulator
# This script starts both the backend API and frontend dev server

set -e

echo "================================================"
echo "🚀 Starting Simulador Fiscal - SL vs Autónomo"
echo "================================================"
echo ""

# Get the directory where the script is located
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR"

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Error: Python 3 is not installed"
    exit 1
fi

# Check if Node.js is installed
if ! command -v node &> /dev/null; then
    echo "❌ Error: Node.js is not installed"
    exit 1
fi

echo "📦 Checking backend dependencies..."
cd backend
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

source venv/bin/activate || . venv/Scripts/activate 2>/dev/null

if ! pip show fastapi &> /dev/null; then
    echo "Installing backend dependencies..."
    pip install -r requirements.txt
fi
cd ..

echo "📦 Checking frontend dependencies..."
cd frontend
if [ ! -d "node_modules" ]; then
    echo "Installing frontend dependencies..."
    npm install
fi
cd ..

echo ""
echo "================================================"
echo "✅ All dependencies ready!"
echo "================================================"
echo ""

# Function to cleanup on exit
cleanup() {
    echo ""
    echo "🛑 Shutting down servers..."
    kill $BACKEND_PID 2>/dev/null || true
    kill $FRONTEND_PID 2>/dev/null || true
    exit 0
}

trap cleanup SIGINT SIGTERM

# Start backend
echo "🔧 Starting Backend API on http://localhost:8000"
cd backend
source venv/bin/activate || . venv/Scripts/activate 2>/dev/null
python -m uvicorn main:app --reload --host 127.0.0.1 --port 8000 &
BACKEND_PID=$!
cd ..

# Wait for backend to start
sleep 3

# Start frontend
echo "🎨 Starting Frontend on http://localhost:5173"
cd frontend
npm run dev &
FRONTEND_PID=$!
cd ..

echo ""
echo "================================================"
echo "✨ Servers are running!"
echo "================================================"
echo ""
echo "📊 Backend API:     http://localhost:8000"
echo "📚 API Docs:        http://localhost:8000/docs"
echo "🌐 Frontend App:    http://localhost:5173"
echo ""
echo "Press Ctrl+C to stop all servers"
echo "================================================"
echo ""

# Wait for processes
wait
