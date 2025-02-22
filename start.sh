#!/bin/bash

#PORT=${PORT:-8004}

uvicorn backend.api:app --host 0.0.0.0 --port $PORT
