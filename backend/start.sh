#!/bin/bash

# Check if Python 3 is available
if ! command -v python3 &> /dev/null; then
    echo "Error: Python 3 is not installed or not in PATH"
    exit 1
fi

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate

# Install dependencies
echo "Installing dependencies..."
pip install -r requirements.txt --no-cache-dir

# Set Python path
export PYTHONPATH=$PYTHONPATH:/app

# Start the server
echo "Starting ChatBot API server..."
uvicorn api:app --host 0.0.0.0 --port ${PORT:-8006}
