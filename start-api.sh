#!/bin/bash
set -e

# Production startup script for FastAPI on Railway
export PYTHONPATH="/app/src:$PYTHONPATH"

# Start the ultra-simple FastAPI application for testing
uvicorn src.api.simple:app --host 0.0.0.0 --port ${PORT:-8000}