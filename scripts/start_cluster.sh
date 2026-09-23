#!/bin/bash
echo "Starting Spark Standalone + Kafka Docker Cluster..."
docker compose up -d 2>/dev/null || docker-compose up -d
echo "Cluster started. Spark Master UI available at http://localhost:8080"
