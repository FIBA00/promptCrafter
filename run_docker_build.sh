#!/bin/bash
set -e

echo "Building and starting the complete application stack (Backend + Database + Cache + Monitoring)..."

# Ensure clean slate by removing potentially conflicting containers
docker rm -f prometheus grafana postgres-exporter promptcrafter_api promptcrafter_db promptcrafter_redis 2>/dev/null || true

docker compose down
docker compose up --build -d

echo ""
echo "-------------------------------------------------------------"
echo "Service Status:"
docker compose ps
echo "-------------------------------------------------------------"
echo "App running at:        http://localhost:8000"
echo "Grafana (Monitoring):  http://localhost:3000 (admin/admin)"
echo "Prometheus:            http://localhost:9090"
echo "-------------------------------------------------------------"
echo "To view logs: docker compose logs -f"

echo "Launching logs in 3 seconds..."
sleep 3
docker compose logs -f api
