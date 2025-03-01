#!/bin/bash

pip install -r requirements.txt --no-cache-dir

export PYTHONPATH=$PYTHONPATH:/app
uvicorn api:app --host 0.0.0.0 --port ${PORT:-8006}
