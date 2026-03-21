#!/bin/bash
# Weather Shield - Status Script
# Shows the current status of the weather monitoring application

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

echo -e "${BLUE}================================${NC}"
echo -e "${BLUE}🌦️  Weather Shield - Status${NC}"
echo -e "${BLUE}================================${NC}"
echo ""

# Check if running
if [ ! -f "$PID_FILE" ]; then
    echo -e "${RED}Status: NOT RUNNING${NC}"
    exit 1
fi

APP_PID=$(cat "$PID_FILE")

if ! kill -0 "$APP_PID" 2>/dev/null; then
    echo -e "${RED}Status: NOT RUNNING${NC}"
    echo -e "${YELLOW}PID file exists but process not found${NC}"
    rm -f "$PID_FILE"
    exit 1
fi

echo -e "${GREEN}Status: RUNNING${NC}"
echo ""
echo "PID: $APP_PID"
echo ""

# Show process info
if command -v ps &> /dev/null; then
    echo -e "${BLUE}Process Info:${NC}"
    ps -p "$APP_PID" -o pid,vsz,rss,comm= 2>/dev/null || true
    echo ""
fi

# Show recent log entries
if [ -f "$LOG_FILE" ]; then
    echo -e "${BLUE}Recent Logs (last 5 lines):${NC}"
    tail -5 "$LOG_FILE" 2>/dev/null || echo "No logs available"
    echo ""
fi

# Show dashboard URL
echo -e "${BLUE}Dashboard:${NC}"
echo -e "  ${YELLOW}http://localhost:5000${NC}"
echo ""

echo -e "${BLUE}Commands:${NC}"
echo "  Stop: ./stop.sh"
echo "  View logs: tail -f $LOG_FILE"
echo ""
