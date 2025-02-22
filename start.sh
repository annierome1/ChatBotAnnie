#!/bin/bash

#PORT=${PORT:-8004}
export PYTHONPATH=$(pwd)/backend
uvicorn backend.api:app --host 0.0.0.0 --port $PORT
