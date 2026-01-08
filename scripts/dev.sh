#!/bin/bash
# Development script - starts all services
# Team: DevOps

echo "Starting development servers..."

# Start backend
echo "Starting backend on :8000..."
cd packages/api
python -m uvicorn src.app:app --reload --port 8000 &
BACKEND_PID=$!

# Start frontend
echo "Starting frontend on :5173..."
cd ../ui
npm run dev &
FRONTEND_PID=$!

echo ""
echo "Services started:"
echo "  Backend:  http://localhost:8000"
echo "  Frontend: http://localhost:5173"
echo "  API Docs: http://localhost:8000/docs"
echo ""
echo "Press Ctrl+C to stop all services"

# Wait for interrupt
trap "kill $BACKEND_PID $FRONTEND_PID 2>/dev/null" EXIT
wait
