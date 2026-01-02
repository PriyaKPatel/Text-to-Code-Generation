#!/bin/bash

# Script to build Docker image directly on EC2 (avoids large upload)

set -e

EC2_HOST="ubuntu@3.239.116.3"
KEY_PATH="~/Downloads/text-to-code-key.pem"
ECR_REPO="518627289438.dkr.ecr.us-east-1.amazonaws.com/text-to-code"

echo "📦 Copying project files to EC2..."
rsync -avz --progress \
  --exclude 'venv' \
  --exclude '.git' \
  --exclude 'models' \
  --exclude 'models_local' \
  --exclude 'models_pytorch' \
  --exclude '__pycache__' \
  --exclude '*.pyc' \
  --exclude '.env*' \
  --exclude '*.pem' \
  -e "ssh -i $KEY_PATH" \
  ./ $EC2_HOST:~/text-to-code/

echo "🔨 Building Docker image on EC2..."
ssh -i $KEY_PATH $EC2_HOST << 'ENDSSH'
cd ~/text-to-code

# Stop old container
docker stop text-to-code 2>/dev/null || true
docker rm text-to-code 2>/dev/null || true

# Build image on EC2 (much faster than uploading)
docker build -t text-to-code:latest .

# Tag for ECR (optional - can also just use local image)
docker tag text-to-code:latest 518627289438.dkr.ecr.us-east-1.amazonaws.com/text-to-code:latest

# Run container
docker run -d \
  --name text-to-code \
  -p 80:8000 \
  --restart unless-stopped \
  -e AWS_DEFAULT_REGION=us-east-1 \
  -e S3_BUCKET=text-to-code-models-priya \
  -e S3_PREFIX=models/v1 \
  text-to-code:latest

echo "✅ Container started!"
echo "📋 Viewing logs (Ctrl+C to exit)..."
docker logs -f text-to-code
ENDSSH

echo "✅ Deployment complete!"
echo "🌐 Test at: http://3.239.116.3/health"

