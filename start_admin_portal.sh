#!/bin/bash

# Start script for the integrated cleaning service admin portal
# This script runs the Streamlit admin portal that connects to the React backend database

echo "🧹 Starting GRK Dienstleistungen Admin Portal..."
echo "========================================"

# Check if we're in the right directory
if [ ! -f "admin_portal_multilingual.py" ]; then
    echo "❌ Error: admin_portal_multilingual.py not found in current directory"
    echo "Please run this script from the CleaningServiceManagementSystem directory"
    exit 1
fi

# Check if the React backend database exists
if [ ! -f "cleaning-service-app/backend/data/cleaning_service.db" ]; then
    echo "⚠️  Warning: React backend database not found"
    echo "Please make sure to:"
    echo "1. Start the React backend: cd cleaning-service-app/backend && npm start"
    echo "2. Register at least one user through the React frontend"
    echo ""
fi

echo "📊 Starting Admin Portal on http://localhost:8502"
echo "📋 This portal will show bookings made through:"
echo "   - Frontend: http://localhost:3000"
echo "   - Backend API: http://localhost:5000"
echo ""
echo "🔐 Login credentials:"
echo "   Username: admin"
echo "   Password: admin123"
echo ""

# Start the Streamlit admin portal
streamlit run admin_portal_multilingual.py --server.port 8502 --server.headless false
