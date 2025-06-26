#!/bin/bash

# GRK Dienstleistungen - Start All Services
# This script starts the React frontend, Node.js backend, and Streamlit admin portal

echo "🚀 Starting GRK Dienstleistungen Services..."
echo ""

# Activate virtual environment
source .venv/bin/activate

# Start Backend (Node.js on port 5000)
echo "📦 Starting Backend Server (port 5000)..."
cd cleaning-service-app/backend
npm start &
BACKEND_PID=$!
cd ../..

# Wait a moment for backend to start
sleep 3

# Start Frontend (React on port 3000)
echo "🌐 Starting Frontend Server (port 3000)..."
cd cleaning-service-app/frontend
npm start &
FRONTEND_PID=$!
cd ../..

# Wait a moment for frontend to start
sleep 3

# Start Admin Portal (Streamlit on port 8502)
echo "🔧 Starting Admin Portal (port 8502)..."
python -m streamlit run admin_portal_multilingual.py --server.port 8502 &
ADMIN_PID=$!

echo ""
echo "✅ All services started successfully!"
echo ""
echo "🌐 Frontend (Customer Portal): http://localhost:3000"
echo "📦 Backend API: http://localhost:5000"
echo "🔧 Admin Portal: http://localhost:8502"
echo ""
echo "To stop all services, press Ctrl+C or run: ./stop_all_services.sh"
echo ""

# Keep script running and handle Ctrl+C
trap 'echo ""; echo "🛑 Stopping all services..."; kill $BACKEND_PID $FRONTEND_PID $ADMIN_PID 2>/dev/null; exit 0' INT

# Wait for all background processes
wait
