#!/bin/bash

# Library Management System Run Script
# This script starts the Library Management System

echo "🚀 Starting Library Management System..."
echo "======================================="

# Check if we're in the right directory
if [ ! -f "backend/library_api/src/main.py" ]; then
    echo "❌ Error: Please run this script from the library_management_system directory"
    exit 1
fi

# Check if virtual environment exists
if [ ! -d "backend/library_api/venv" ]; then
    echo "❌ Error: Virtual environment not found. Please run setup.sh first."
    exit 1
fi

# Check if MySQL is running
if ! pgrep -x "mysqld" > /dev/null; then
    echo "📋 Starting MySQL service..."
    if [[ "$OSTYPE" == "linux-gnu"* ]]; then
        sudo systemctl start mysql
    elif [[ "$OSTYPE" == "darwin"* ]]; then
        brew services start mysql
    fi
fi

# Navigate to backend directory
cd backend/library_api

# Activate virtual environment
echo "📋 Activating Python virtual environment..."
source venv/bin/activate

# Check if dependencies are installed
if ! python -c "import flask" 2>/dev/null; then
    echo "📋 Installing dependencies..."
    pip install -r requirements.txt
fi

# Start the Flask application
echo "🌟 Starting Flask application..."
echo "📍 Application will be available at: http://localhost:5000"
echo "🔑 Default login - Username: admin, Password: password"
echo "⏹️  Press Ctrl+C to stop the server"
echo ""

# Run the application
python src/main.py

