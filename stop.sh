#!/bin/bash
# Weather Shield - Stop Script
# Stops the weather monitoring and dashboard application

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PID_FILE="$PROJECT_DIR/.weather_shield.pid"

echo -e "${BLUE}================================${NC}"
echo -e "${BLUE}🌦️  Weather Shield - Stop${NC}"
echo -e "${BLUE}================================${NC}"
echo ""

# Check if running
if [ ! -f "$PID_FILE" ]; then
    echo -e "${YELLOW}ℹ️  Weather Shield is not running${NC}"
    exit 0
fi

APP_PID=$(cat "$PID_FILE")

# Verify the process exists
if ! kill -0 "$APP_PID" 2>/dev/null; then
    echo -e "${YELLOW}⚠️  Process not found (PID: $APP_PID)${NC}"
    echo "Cleaning up PID file..."
    rm "$PID_FILE"
    exit 0
fi

echo -e "${BLUE}Stopping Weather Shield (PID: $APP_PID)...${NC}"

# Send TERM signal
kill -TERM "$APP_PID" 2>/dev/null

# Wait for graceful shutdown (up to 10 seconds)
for i in {1..10}; do
    if ! kill -0 "$APP_PID" 2>/dev/null; then
        break
    fi
    echo -n "."
    sleep 1
done

# If still running, force kill
if kill -0 "$APP_PID" 2>/dev/null; then
    echo ""
    echo -e "${YELLOW}⚠️  Process didn't stop gracefully, forcing...${NC}"
    kill -9 "$APP_PID" 2>/dev/null || true
    sleep 1
fi

# Remove PID file
rm -f "$PID_FILE"

# Verify it's stopped
if ! kill -0 "$APP_PID" 2>/dev/null; then
    echo ""
    echo -e "${GREEN}✅ Weather Shield stopped successfully${NC}"
    exit 0
else
    echo ""
    echo -e "${RED}❌ Failed to stop Weather Shield${NC}"
    exit 1
fi
