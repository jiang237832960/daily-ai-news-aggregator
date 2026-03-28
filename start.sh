#!/bin/bash

# Horizon - AI News Aggregator Startup Script

set -e

echo "=================================="
echo "Horizon - AI News Aggregator"
echo "=================================="

# Function to cleanup background processes
cleanup() {
    echo "Stopping services..."
    if [ ! -z "$BACKEND_PID" ]; then
        kill $BACKEND_PID 2>/dev/null || true
    fi
    if [ ! -z "$FRONTEND_PID" ]; then
        kill $FRONTEND_PID 2>/dev/null || true
    fi
}

trap cleanup EXIT

# Install dependencies if needed
if [ ! -d "horizon" ] || [ ! -f "horizon/pyproject.toml" ]; then
    echo "Error: horizon directory not found"
    exit 1
fi

if [ ! -d "web" ] || [ ! -f "web/package.json" ]; then
    echo "Error: web directory not found"
    exit 1
fi

# Install Python dependencies
echo "Installing Python dependencies..."
cd horizon
pip install -e . --quiet 2>/dev/null || pip install -e .
cd ..

# Start backend (FastAPI)
echo "Starting FastAPI backend on port 8000..."
cd horizon
python -m uvicorn horizon.api:app --host 0.0.0.0 --port 8000 &
BACKEND_PID=$!
cd ..

# Wait for backend to start
sleep 3

# Start frontend (Next.js)
echo "Starting Next.js frontend on port 3000..."
cd web
npm run dev &
FRONTEND_PID=$!
cd ..

echo ""
echo "=================================="
echo "Services started:"
echo "  - Backend API: http://localhost:8000"
echo "  - Frontend:   http://localhost:3000"
echo "  - API Docs:   http://localhost:8000/docs"
echo "=================================="
echo ""
echo "Press Ctrl+C to stop all services"

# Wait for user interrupt
wait
