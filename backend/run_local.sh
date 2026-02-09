#!/bin/bash
# For local development - runs the main app publicly (Metrics are now on 8000 too)
echo "Killing processes on ports 8000..."
fuser -k 8000/tcp 2>/dev/null

echo "Reloading main app..."
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
