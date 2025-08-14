#!/bin/bash
set -e

# Production startup script for FastAPI on Fly.io
export PYTHONPATH="/app/src:$PYTHONPATH"

# Start the FastAPI application
uvicorn src.api.main:app --host 0.0.0.0 --port ${PORT:-8000}