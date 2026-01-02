#!/bin/bash

# Deploy updated Docker image to EC2

set -e

EC2_HOST="ubuntu@3.239.116.3"
KEY_PATH="~/Downloads/text-to-code-key.pem"
ECR_REPO="518627289438.dkr.ecr.us-east-1.amazonaws.com/text-to-code"

echo "🚀 Deploying updated model to EC2..."

ssh -i $KEY_PATH $EC2_HOST << 'ENDSSH'
set -e

echo "📥 Logging into ECR..."
aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin 518627289438.dkr.ecr.us-east-1.amazonaws.com

echo "📦 Pulling latest image..."
docker pull 518627289438.dkr.ecr.us-east-1.amazonaws.com/text-to-code:latest

echo "🛑 Stopping old container (if running)..."
docker stop text-to-code 2>/dev/null || true
docker rm text-to-code 2>/dev/null || true

echo "🚀 Starting new container with updated TensorFlow model support..."
docker run -d \
  --name text-to-code \
  -p 80:8000 \
  --restart unless-stopped \
  -e AWS_DEFAULT_REGION=us-east-1 \
  -e S3_BUCKET=text-to-code-models-priya \
  -e S3_PREFIX=models/v1 \
  -e TF_USE_LEGACY_KERAS=1 \
  518627289438.dkr.ecr.us-east-1.amazonaws.com/text-to-code:latest

echo "⏳ Waiting for model to load (30 seconds)..."
sleep 30

echo "📋 Container logs:"
docker logs text-to-code

echo ""
echo "✅ Deployment complete!"
echo "🌐 API URL: http://3.239.116.3"
echo ""
echo "🧪 Testing health endpoint..."
curl -s http://localhost/health | head -20

ENDSSH

echo ""
echo "🎉 All done! Your updated API is running on EC2"
echo "Test it: curl http://3.239.116.3/health"

