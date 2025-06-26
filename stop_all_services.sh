#!/bin/bash

# GRK Dienstleistungen - Stop All Services
# This script stops the React frontend, Node.js backend, and Streamlit admin portal

echo "🛑 Stopping GRK Dienstleistungen Services..."

# Kill processes by port
echo "Stopping Frontend (port 3000)..."
lsof -ti:3000 | xargs kill -9 2>/dev/null || echo "Frontend not running"

echo "Stopping Backend (port 5000)..."
lsof -ti:5000 | xargs kill -9 2>/dev/null || echo "Backend not running"

echo "Stopping Admin Portal (port 8502)..."
lsof -ti:8502 | xargs kill -9 2>/dev/null || echo "Admin Portal not running"

echo "✅ All services stopped!"
