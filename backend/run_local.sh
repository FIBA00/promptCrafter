#!/bin/bash
# For local development - runs the main app publicly and metrics app privately.
echo "Killing processes on ports 8000 and 9091..."
fuser -k 8000/tcp 9091/tcp 2>/dev/null

echo "Reloading main app..."
uvicorn main:app --host 0.0.0.0 --port 8000 --reload &
APP_PID=$!

echo "Reloading metrics app..."
uvicorn main:metrics_app --host 127.0.0.1 --port 9091 --reload &
METRICS_PID=$!

# # Wait for either process to exit
# wait -n $APP_PID $METRICS_PID

# # Clean up other process
