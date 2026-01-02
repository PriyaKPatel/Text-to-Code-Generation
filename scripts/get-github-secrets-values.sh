#!/bin/bash

# Script to gather values for GitHub Secrets

echo "=========================================="
echo "GitHub Secrets Configuration Values"
echo "=========================================="
echo ""

# AWS Account ID
echo "1. AWS_ACCOUNT_ID:"
aws sts get-caller-identity --query Account --output text 2>/dev/null || echo "   Run: aws sts get-caller-identity --query Account --output text"
echo ""

# AWS Credentials (from your AWS CLI config)
echo "2. AWS_ACCESS_KEY_ID:"
echo "   Get from: ~/.aws/credentials or AWS Console (IAM > Users > Security Credentials)"
echo "   Value: (Keep this secret!)"
echo ""

echo "3. AWS_SECRET_ACCESS_KEY:"
echo "   Get from: ~/.aws/credentials or AWS Console (IAM > Users > Security Credentials)"
echo "   Value: (Keep this secret!)"
echo ""

# EC2 Details
echo "4. EC2_HOST:"
echo "   Value: 3.85.224.148"
echo ""

echo "5. EC2_USERNAME:"
echo "   Value: ubuntu"
echo ""

# SSH Key
echo "6. EC2_SSH_KEY:"
echo "   Get from: ~/Downloads/text-to-code-key.pem"
if [ -f ~/Downloads/text-to-code-key.pem ]; then
    echo "   File found! Copy the entire content including:"
    echo "   -----BEGIN RSA PRIVATE KEY-----"
    echo "   ...your key..."
    echo "   -----END RSA PRIVATE KEY-----"
else
    echo "   ⚠️  File not found at ~/Downloads/text-to-code-key.pem"
fi
echo ""

# S3 Bucket
echo "7. S3_BUCKET:"
echo "   Value: text-to-code-models-priya"
echo ""

echo "8. S3_PREFIX:"
echo "   Value: models/v1"
echo ""

echo "=========================================="
echo "How to Add These to GitHub:"
echo "=========================================="
echo ""
echo "1. Go to: https://github.com/PriyaKPatel/Text-to-Code-Generation/settings/secrets/actions"
echo ""
echo "2. Click 'New repository secret' for each:"
echo "   - Name: AWS_ACCOUNT_ID           Value: (from step 1 above)"
echo "   - Name: AWS_ACCESS_KEY_ID        Value: (from your AWS credentials)"
echo "   - Name: AWS_SECRET_ACCESS_KEY    Value: (from your AWS credentials)"
echo "   - Name: EC2_HOST                 Value: 3.85.224.148"
echo "   - Name: EC2_USERNAME             Value: ubuntu"
echo "   - Name: EC2_SSH_KEY              Value: (entire content of .pem file)"
echo "   - Name: S3_BUCKET                Value: text-to-code-models-priya"
echo "   - Name: S3_PREFIX                Value: models/v1"
echo ""
echo "3. Save each secret"
echo ""
echo "=========================================="
echo ""

