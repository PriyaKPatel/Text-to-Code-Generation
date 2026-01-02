#!/bin/bash
# Deploy to AWS EC2 script

set -e

echo "=========================================="
echo "AWS EC2 Deployment Script"
echo "=========================================="

# Check required environment variables
if [ -z "$AWS_ACCOUNT_ID" ]; then
    echo "Error: AWS_ACCOUNT_ID not set"
    exit 1
fi

if [ -z "$AWS_REGION" ]; then
    AWS_REGION="us-east-1"
fi

if [ -z "$ECR_REPOSITORY" ]; then
    ECR_REPOSITORY="text-to-code"
fi

# Create ECR repository if it doesn't exist
echo "Creating ECR repository..."
aws ecr create-repository \
    --repository-name $ECR_REPOSITORY \
    --region $AWS_REGION \
    2>/dev/null || echo "Repository already exists"

# Login to ECR
echo "Logging in to ECR..."
aws ecr get-login-password --region $AWS_REGION | \
    docker login --username AWS --password-stdin \
    $AWS_ACCOUNT_ID.dkr.ecr.$AWS_REGION.amazonaws.com

# Build Docker image
echo "Building Docker image..."
docker build -t $ECR_REPOSITORY:latest .

# Tag image
echo "Tagging image..."
docker tag $ECR_REPOSITORY:latest \
    $AWS_ACCOUNT_ID.dkr.ecr.$AWS_REGION.amazonaws.com/$ECR_REPOSITORY:latest

# Push to ECR
echo "Pushing to ECR..."
docker push $AWS_ACCOUNT_ID.dkr.ecr.$AWS_REGION.amazonaws.com/$ECR_REPOSITORY:latest

# Create S3 bucket for models if it doesn't exist
if [ ! -z "$S3_BUCKET" ]; then
    echo "Creating S3 bucket for models..."
    aws s3 mb s3://$S3_BUCKET --region $AWS_REGION 2>/dev/null || echo "Bucket already exists"
    
    # Upload models if they exist locally
    if [ -d "./models" ] && [ "$(ls -A ./models)" ]; then
        echo "Uploading models to S3..."
        aws s3 sync ./models s3://$S3_BUCKET/models/v1/ --region $AWS_REGION
    fi
fi

echo "=========================================="
echo "✅ Build and push complete!"
echo "=========================================="
echo ""
echo "ECR Image: $AWS_ACCOUNT_ID.dkr.ecr.$AWS_REGION.amazonaws.com/$ECR_REPOSITORY:latest"
echo ""
echo "Next steps:"
echo "1. Launch EC2 instance"
echo "2. SSH into instance and run setup script"
echo "3. Pull and run the Docker image"
echo ""
echo "Or use GitHub Actions for automated deployment!"
