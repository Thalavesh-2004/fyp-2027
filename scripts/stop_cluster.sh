#!/bin/bash
echo "Stopping Docker Cluster..."
docker compose down 2>/dev/null || docker-compose down
echo "Cluster stopped."
