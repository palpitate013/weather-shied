#!/bin/bash
# Weather Shield - Start Script
# Starts the unified weather monitoring and dashboard application

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PID_FILE="$PROJECT_DIR/.weather_shield.pid"
LOG_FILE="$PROJECT_DIR/weather_shield.log"
DASHBOARD_PORT="${1:-5000}"

echo -e "${BLUE}================================${NC}"
echo -e "${BLUE}🌦️  Weather Shield - Start${NC}"
echo -e "${BLUE}================================${NC}"
echo ""

# Check if already running
if [ -f "$PID_FILE" ]; then
    OLD_PID=$(cat "$PID_FILE")
    if kill -0 "$OLD_PID" 2>/dev/null; then
        echo -e "${YELLOW}⚠️  Weather Shield is already running (PID: $OLD_PID)${NC}"
        echo "Use './stop.sh' to stop it first"
        exit 1
    else
        echo -e "${YELLOW}ℹ️  Cleaning up old PID file${NC}"
        rm "$PID_FILE"
    fi
fi

# Check if config.json exists
if [ ! -f "$PROJECT_DIR/config.json" ]; then
    echo -e "${RED}❌ Error: config.json not found${NC}"
    echo "Please copy config.example.json to config.json and configure it"
    exit 1
fi

# Check if running in nix-shell or has Python available
if ! command -v python &> /dev/null; then
    echo -e "${RED}❌ Error: Python not found${NC}"
    echo "Please run: nix-shell"
    exit 1
fi

# Check if Flask is installed
if ! python -c "import flask" 2>/dev/null; then
    echo -e "${RED}❌ Error: Flask not installed${NC}"
    echo "Please run: nix-shell"
    exit 1
fi

# Create log directory if needed
mkdir -p "$(dirname "$LOG_FILE")"

echo -e "${BLUE}Starting Weather Shield...${NC}"
echo "Dashboard port: $DASHBOARD_PORT"
echo "Log file: $LOG_FILE"
echo ""

# Start the application in the background
cd "$PROJECT_DIR"
python weather_shield.py >> "$LOG_FILE" 2>&1 &
APP_PID=$!

# Save PID to file
echo "$APP_PID" > "$PID_FILE"

# Wait a moment to see if it starts successfully
sleep 2

if ! kill -0 "$APP_PID" 2>/dev/null; then
    echo -e "${RED}❌ Failed to start Weather Shield${NC}"
    echo "Check the log file: $LOG_FILE"
    rm "$PID_FILE"
    exit 1
fi

echo -e "${GREEN}✅ Weather Shield started successfully!${NC}"
echo ""
echo -e "${BLUE}Status:${NC}"
echo "  PID: $APP_PID"
echo "  Dashboard: ${BLUE}http://localhost:$DASHBOARD_PORT${NC}"
echo "  Monitor: Running"
echo ""
echo -e "${YELLOW}Tips:${NC}"
echo "  • View logs: ${BLUE}tail -f $LOG_FILE${NC}"
echo "  • Stop: ${BLUE}./stop.sh${NC}"
echo "  • Status: ${BLUE}./status.sh${NC}"
echo ""
