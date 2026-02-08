#!/bin/bash

# Complete ML Pipeline + API Startup Script
# This script orchestrates: Data → Preprocessing → Training → Evaluation → MLflow → API

set -e  # Exit on error

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$SCRIPT_DIR"
VENV_PATH="$PROJECT_ROOT/scoringenv"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}"
echo "╔════════════════════════════════════════════════════════════════╗"
echo "║      Credit Scoring ML Pipeline + API Orchestrator            ║"
echo "╚════════════════════════════════════════════════════════════════╝"
echo -e "${NC}"

# Check if venv exists
if [ ! -d "$VENV_PATH" ]; then
    echo -e "${RED}Error: Virtual environment not found at $VENV_PATH${NC}"
    exit 1
fi

# Activate venv
echo -e "${YELLOW}Activating virtual environment...${NC}"
source "$VENV_PATH/bin/activate"

# Step 1: Run complete ML pipeline
echo -e "${BLUE}"
echo "╔════════════════════════════════════════════════════════════════╗"
echo "║                 Running ML Pipeline                            ║"
echo "╚════════════════════════════════════════════════════════════════╝"
echo -e "${NC}"

cd "$PROJECT_ROOT"
python src/pipelines/run_pipeline.py

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✓ ML Pipeline completed successfully!${NC}"
else
    echo -e "${RED}✗ ML Pipeline failed!${NC}"
    exit 1
fi

# Step 2: Ask user if they want to start API
echo -e "${YELLOW}Pipeline completed. Start FastAPI server now? (y/n)${NC}"
read -r response

if [[ "$response" == "y" || "$response" == "Y" ]]; then
    echo -e "${BLUE}"
    echo "╔════════════════════════════════════════════════════════════════╗"
    echo "║              Starting FastAPI Server                           ║"
    echo "╚════════════════════════════════════════════════════════════════╝"
    echo -e "${NC}"
    
    echo -e "${GREEN}Starting API on http://0.0.0.0:8000${NC}"
    echo -e "${YELLOW}Documentation available at: http://localhost:8000/docs${NC}"
    echo -e "${YELLOW}Press Ctrl+C to stop the server${NC}\n"
    
    python Api/main.py
else
    echo -e "${YELLOW}API not started. To start manually:${NC}"
    echo "  cd $PROJECT_ROOT"
    echo "  source $VENV_PATH/bin/activate"
    echo "  python Api/main.py"
fi
