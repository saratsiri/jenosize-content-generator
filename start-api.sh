#!/bin/bash
set -e

# Production startup script for FastAPI on Railway
export PYTHONPATH="/app/src:$PYTHONPATH"

# Debug API key first
echo "=== DEBUG API KEY ==="
python debug_api.py

# Start the FastAPI application (minimal version with fixes)
uvicorn src.api.main_minimal:app --host 0.0.0.0 --port ${PORT:-8000}