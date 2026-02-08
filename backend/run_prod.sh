#!/bin/bash
# For production with systemd - runs both services.

# Get the directory of the script
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"
cd $DIR

# Main app on port 8000, accessible by Nginx
uvicorn main:app --host 127.0.0.1 --port 8000 &
APP_PID=$!

# Metrics app on port 9091, for Prometheus only
uvicorn main:metrics_app --host 127.0.0.1 --port 9091 &
METRICS_PID=$!

# Wait for either process to exit
wait -n $APP_PID $METRICS_PID

# Clean up other process
kill $APP_PID $METRICS_PID 2>/dev/null