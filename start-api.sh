#!/bin/bash
set -e

# Production startup script for FastAPI on Railway
export PYTHONPATH="/app/src:$PYTHONPATH"

# Start the minimal FastAPI application with Claude integration
uvicorn src.api.main_minimal:app --host 0.0.0.0 --port ${PORT:-8000}