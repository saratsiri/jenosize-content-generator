#!/bin/bash
set -e

# Production startup script for Streamlit on Fly.io
export PYTHONPATH="/app/src:$PYTHONPATH"

# Start the Streamlit application
streamlit run demo/app.py \
    --server.port ${PORT:-8501} \
    --server.address 0.0.0.0 \
    --server.headless true \
    --browser.gatherUsageStats false