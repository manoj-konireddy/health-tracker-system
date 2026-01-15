#!/bin/bash

# Health Tracker Startup Script

echo "================================"
echo "Health Tracker System"
echo "================================"
echo ""

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "Error: Python 3 is not installed. Please install Python 3.7 or higher."
    exit 1
fi

echo "✓ Python found"
echo ""

# Check if pip is installed
if ! command -v pip3 &> /dev/null; then
    echo "Error: pip is not installed. Please install pip."
    exit 1
fi

echo "✓ pip found"
echo ""

# Install/update dependencies
echo "Installing dependencies..."
pip3 install -r requirements.txt

if [ $? -eq 0 ]; then
    echo "✓ Dependencies installed successfully"
else
    echo "✗ Failed to install dependencies"
    exit 1
fi

echo ""
echo "================================"
echo "Starting Health Tracker..."
echo "================================"
echo ""
echo "The application will be available at: http://localhost:5000"
echo ""
echo "Default login:"
echo "  - Create a new account on the registration page"
echo "  - Or use test credentials if available"
echo ""
echo "Press Ctrl+C to stop the server"
echo ""

# Run the Flask app
python3 app.py
