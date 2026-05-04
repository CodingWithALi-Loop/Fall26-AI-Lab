#!/bin/bash

# Quick Start Script for Flask Weather Dashboard
echo "🌍 Flask Weather Dashboard - Quick Start"
echo "========================================"
echo ""

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed. Please install Python 3.8 or higher."
    exit 1
fi

echo "✅ Python found: $(python3 --version)"
echo ""

# Install dependencies
echo "📦 Installing dependencies..."
pip3 install -r requirements.txt

if [ $? -ne 0 ]; then
    echo "❌ Failed to install dependencies"
    exit 1
fi

echo "✅ Dependencies installed successfully"
echo ""

# Run the application
echo "🚀 Starting Flask Weather Dashboard..."
echo "📱 The app will open at: http://127.0.0.1:5000"
echo ""
echo "💡 Remember to:"
echo "   1. Get an API key from https://openweathermap.org/api"
echo "   2. Paste it in the app"
echo "   3. Search for any city to get started!"
echo ""

python3 app.py
