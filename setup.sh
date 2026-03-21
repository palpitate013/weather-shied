#!/bin/bash
# Weather Shield - Installation and Setup Script
# This script automates the setup process for Weather Shield

set -e  # Exit on error

echo "================================"
echo "🌦️  Weather Shield Setup Script"
echo "================================"
echo ""

# Check if Python is installed
echo "Checking Python installation..."
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed"
    echo "Please install Python 3.7 or higher from https://www.python.org/"
    exit 1
fi

PYTHON_VERSION=$(python3 --version | cut -d' ' -f2)
echo "✓ Python $PYTHON_VERSION found"
echo ""

# Install dependencies
echo "Installing Python dependencies..."
if [ -f "requirements.txt" ]; then
    python3 -m pip install -r requirements.txt --quiet
    echo "✓ Dependencies installed successfully"
else
    echo "❌ requirements.txt not found"
    exit 1
fi
echo ""

# Check if config.json exists
echo "Checking configuration..."
if [ ! -f "config.json" ]; then
    echo "❌ config.json not found"
    echo "Creating config.json from template..."
    
    if [ -f "config.example.json" ]; then
        cp config.example.json config.json
        echo "✓ config.json created"
        echo ""
        echo "⚠️  IMPORTANT: Edit config.json with your details:"
        echo "   1. Get your API key from https://openweathermap.org/api"
        echo "   2. Add your latitude and longitude"
        echo "   3. Save the file"
    else
        echo "❌ config.example.json not found"
        exit 1
    fi
else
    echo "✓ config.json found"
fi
echo ""

# Test configuration
echo "Testing configuration..."
if python3 test_config.py; then
    echo ""
    echo "✅ Setup completed successfully!"
    echo ""
    echo "You can now run:"
    echo "  python3 weather_monitor.py"
    echo ""
    echo "For Linux users, to run as a system service:"
    echo "  sudo cp weather-shield.service /etc/systemd/system/"
    echo "  sudo systemctl enable weather-shield"
    echo "  sudo systemctl start weather-shield"
else
    echo ""
    echo "⚠️  Configuration test failed"
    echo "Please check your config.json and try again"
    exit 1
fi
