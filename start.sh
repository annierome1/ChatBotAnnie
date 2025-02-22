#!/bin/bash

pip install -r backend/requirements.txt --no-cache-dir

export PYTHONPATH=$PYTHONPATH:/app
uvicorn backend.api:app --host 0.0.0.0 --port ${PORT:-8006}
