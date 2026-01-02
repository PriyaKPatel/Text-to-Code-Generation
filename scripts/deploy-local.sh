#!/bin/bash
# Local deployment script for Text-to-Code API

set -e

echo "=========================================="
echo "Text-to-Code API Deployment Script"
echo "=========================================="

# Check if .env file exists
if [ ! -f .env ]; then
    echo "Error: .env file not found!"
    echo "Please create .env file from .env.example"
    exit 1
fi

# Load environment variables
source .env

# Build Docker image
echo "Building Docker image..."
docker build -t text-to-code:latest .

# Stop and remove existing container if running
echo "Stopping existing container..."
docker stop text-to-code 2>/dev/null || true
docker rm text-to-code 2>/dev/null || true

# Run new container
echo "Starting new container..."
docker run -d \
    --name text-to-code \
    -p 8000:8000 \
    -e AWS_ACCESS_KEY_ID=${AWS_ACCESS_KEY_ID} \
    -e AWS_SECRET_ACCESS_KEY=${AWS_SECRET_ACCESS_KEY} \
    -e AWS_DEFAULT_REGION=${AWS_DEFAULT_REGION} \
    -e S3_BUCKET=${S3_BUCKET} \
    -e S3_PREFIX=${S3_PREFIX} \
    -v $(pwd)/models:/app/models \
    --restart unless-stopped \
    text-to-code:latest

# Wait for container to be healthy
echo "Waiting for container to be healthy..."
sleep 5

# Check health
echo "Checking health..."
if curl -f http://localhost:8000/health; then
    echo ""
    echo "=========================================="
    echo "✅ Deployment successful!"
    echo "=========================================="
    echo "API is running at: http://localhost:8000"
    echo "API docs: http://localhost:8000/docs"
    echo "Health check: http://localhost:8000/health"
    echo "Metrics: http://localhost:8000/metrics"
else
    echo ""
    echo "❌ Deployment failed - health check failed"
    echo "Check logs with: docker logs text-to-code"
    exit 1
fi
