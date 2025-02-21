#!/bin/bash

# Load environment variables from .env file (only if running locally)
if [ -f .env ]; then
    export $(grep -v '^#' .env | xargs)
fi

# Run FastAPI using Uvicorn
exec uvicorn backend.api:app --host 0.0.0.0 --port $PORT --workers 4
