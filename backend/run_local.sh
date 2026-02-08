#!/bin/bash
# For local development - runs the main app publicly and metrics app privately.

echo "Starting main app on 0.0.0.0:8000..."
uvicorn main:app --host 0.0.0.0 --port 8000 &
APP_PID=$!

echo "Starting metrics app on 127.0.0.1:9091..."
uvicorn main:metrics_app --host 127.0.0.1 --port 9091 &
METRICS_PID=$!

# Wait for either process to exit
wait -n $APP_PID $METRICS_PID

# Clean up other process
kill $APP_PID $METRICS_PID 2>/dev/null
