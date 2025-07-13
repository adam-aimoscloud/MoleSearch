#!/bin/bash

# MoleSearch API + Worker startup script
# This script starts both the API server and the async worker

echo "🚀 Starting MoleSearch API and Worker..."

# Function to cleanup background processes
cleanup() {
    echo "🛑 Stopping all processes..."
    kill $API_PID $WORKER_PID 2>/dev/null
    exit 0
}

# Set up signal handlers
trap cleanup SIGINT SIGTERM

# Start API server in background
echo "📡 Starting API server..."
gunicorn -c gunicorn.conf.py main:app &
API_PID=$!

# Wait a moment for API to start
sleep 3

# Check if API is running
if ! kill -0 $API_PID 2>/dev/null; then
    echo "❌ Failed to start API server"
    exit 1
fi

echo "✅ API server started (PID: $API_PID)"

# Start worker in background
echo "⚙️  Starting async worker..."
python workers/start_worker.py &
WORKER_PID=$!

# Wait a moment for worker to start
sleep 2

# Check if worker is running
if ! kill -0 $WORKER_PID 2>/dev/null; then
    echo "❌ Failed to start worker"
    kill $API_PID 2>/dev/null
    exit 1
fi

echo "✅ Worker started (PID: $WORKER_PID)"
echo ""
echo "🎉 MoleSearch is running!"
echo "📡 API Server: http://localhost:8000"
echo "📚 API Docs: http://localhost:8000/docs"
echo "⚙️  Worker: Monitoring async tasks"
echo ""
echo "Press Ctrl+C to stop all services"

# Wait for either process to exit
wait 