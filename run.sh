#!/bin/bash
set -e

# =============================================================================
# Synology Photo Archiver - Production Run Script
# =============================================================================

# Paths
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"
APP_DIR="$SCRIPT_DIR/synology-photo-archiver"
CONFIG_FILE="$APP_DIR/config.ini"

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${GREEN}=== Synology Photo Archiver Runner ===${NC}"

# 1. Check Prerequisities
echo -e "${YELLOW}[1/4] Checking environment...${NC}"

if ! command -v python3 &> /dev/null; then
    echo -e "${RED}Error: python3 is not installed or not in PATH.${NC}"
    exit 1
fi

echo "Python3 found: $(which python3)"

# Check if app directory exists
if [ ! -d "$APP_DIR" ]; then
    echo -e "${RED}Error: Application directory not found at $APP_DIR${NC}"
    exit 1
fi

# 2. Check Configuration
echo -e "${YELLOW}[2/4] Checking configuration...${NC}"

if [ ! -f "$CONFIG_FILE" ]; then
    echo -e "${RED}Error: Config file not found at $CONFIG_FILE${NC}"
    echo "Please copy the example config and edit it:"
    echo "  cp $APP_DIR/config.ini.example $APP_DIR/config.ini"
    echo "  nano $APP_DIR/config.ini"
    exit 1
else
    echo "Config file found."
fi

# 3. Setup Python Environment (Optional but recommended)
# If you have a venv, activate it here. Otherwise, ensure dependencies are installed.
echo -e "${YELLOW}[3/4] Preparing runtime...${NC}"

# Add project root to PYTHONPATH so imports work correctly
export PYTHONPATH="$SCRIPT_DIR"

# 4. Run the Application
echo -e "${GREEN}[4/4] Starting archiving process...${NC}"
echo "----------------------------------------"

cd "$APP_DIR"
# Run as a module
python3 -m src.main

EXIT_CODE=$?

echo "----------------------------------------"
if [ $EXIT_CODE -eq 0 ]; then
    echo -e "${GREEN}Archiving process completed successfully.${NC}"
else
    echo -e "${RED}Archiving process failed with exit code $EXIT_CODE.${NC}"
    exit $EXIT_CODE
fi
