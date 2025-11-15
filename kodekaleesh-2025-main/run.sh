#!/bin/bash
# run.sh - Quick start script for development

echo "🚀 Legal Document Intelligence MVP - Quick Start"
echo "=================================================="

# Check Python
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 not found. Please install Python 3.9+"
    exit 1
fi

# Check Node
if ! command -v node &> /dev/null; then
    echo "❌ Node.js not found. Please install Node.js 16+"
    exit 1
fi

echo "✅ Python and Node found"
echo ""

# Start Backend
echo "📦 Starting Backend (Flask)..."
cd backend

if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

source venv/bin/activate
pip install -r requirements.txt > /dev/null 2>&1

python app.py &
BACKEND_PID=$!
echo "✅ Backend running on http://localhost:5000 (PID: $BACKEND_PID)"

# Wait for backend to start
sleep 2

cd ../frontend

# Start Frontend
echo "🎨 Starting Frontend (React)..."

if [ ! -d "node_modules" ]; then
    echo "Installing dependencies..."
    npm install > /dev/null 2>&1
fi

npm start &
FRONTEND_PID=$!
echo "✅ Frontend running on http://localhost:3000 (PID: $FRONTEND_PID)"

echo ""
echo "=================================================="
echo "🎉 MVP is ready!"
echo ""
echo "Browser: http://localhost:3000"
echo "API: http://localhost:5000/api"
echo ""
echo "To stop: Press Ctrl+C"
echo "=================================================="

# Wait for both processes
wait $BACKEND_PID $FRONTEND_PID
