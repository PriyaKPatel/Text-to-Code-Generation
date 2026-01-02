#!/bin/bash
# Phase 2: AWS Setup - Commands to Run
# Run these commands in your terminal (where AWS CLI is configured)

set -e

echo "=========================================="
echo "Phase 2: AWS Setup - Automated Commands"
echo "=========================================="
echo ""

# Your AWS Account ID (from aws sts get-caller-identity)
AWS_ACCOUNT_ID="518627289438"
AWS_REGION="us-east-1"

echo "Step 2.2: Creating ECR Repository..."
aws ecr create-repository \
    --repository-name text-to-code \
    --region $AWS_REGION \
    2>/dev/null || echo "Repository already exists"

ECR_URI=$(aws ecr describe-repositories \
    --region $AWS_REGION \
    --repository-names text-to-code \
    --query 'repositories[0].repositoryUri' \
    --output text)

echo "✅ ECR Repository URI: $ECR_URI"
echo ""

echo "Step 2.3: Creating S3 Bucket..."
aws s3 mb s3://text-to-code-models-priya --region $AWS_REGION 2>/dev/null || \
    echo "Bucket might already exist or name taken. Try a different name if needed."

echo "✅ S3 Bucket created (or already exists)"
echo ""

echo "Step 2.4: Checking for existing EC2 instances..."
aws ec2 describe-instances \
    --filters "Name=tag:Name,Values=text-to-code-api" \
    --query "Reservations[*].Instances[*].[InstanceId,PublicIpAddress,State.Name]" \
    --output table

echo ""
echo "=========================================="
echo "Next Steps:"
echo "=========================================="
echo ""
echo "1. If EC2 instance doesn't exist, launch it via AWS Console:"
echo "   - Go to: https://console.aws.amazon.com/ec2/"
echo "   - Click 'Launch Instance'"
echo "   - Follow AWS_SETUP_DETAILED.md Step 2.4"
echo ""
echo "2. Save these values:"
echo "   AWS_ACCOUNT_ID=$AWS_ACCOUNT_ID"
echo "   ECR_URI=$ECR_URI"
echo "   S3_BUCKET=text-to-code-models-priya"
echo ""
echo "3. Once EC2 is running, get the Public IP and proceed to Phase 3"
echo ""


