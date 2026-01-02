#!/bin/bash
# Upload trained model to S3 for use by FastAPI

set -e

# Load configuration
source aws-config.txt 2>/dev/null || true

# Configuration
MODEL_DIR="${1:-./models/codet5-base}"  # First argument or default
S3_BUCKET="${S3_BUCKET:-text-to-code-models-priya}"
S3_PREFIX="${S3_PREFIX:-models/v1}"
AWS_REGION="${AWS_REGION:-us-east-1}"

echo "========================================"
echo "Upload Model to S3"
echo "========================================"
echo "Model Directory: $MODEL_DIR"
echo "S3 Bucket: $S3_BUCKET"
echo "S3 Prefix: $S3_PREFIX"
echo "========================================"

# Check if model directory exists
if [ ! -d "$MODEL_DIR" ]; then
    echo "❌ Error: Model directory not found: $MODEL_DIR"
    echo ""
    echo "Usage:"
    echo "  $0 /path/to/model/directory"
    echo ""
    echo "Examples:"
    echo "  $0 ./models/codet5-base              # Upload CodeT5-base"
    echo "  $0 ./runs/saved_model                # Upload fine-tuned model from notebook"
    echo "  $0 /path/to/notebook/runs/saved_model # Upload from notebook location"
    exit 1
fi

# Check if model files exist
if [ ! -f "$MODEL_DIR/config.json" ]; then
    echo "❌ Error: config.json not found in $MODEL_DIR"
    echo "This doesn't look like a valid model directory."
    exit 1
fi

echo "✅ Model directory validated"
echo ""

# List files to be uploaded
echo "Files to upload:"
ls -lh "$MODEL_DIR"
echo ""

# Confirm upload
read -p "Upload to s3://$S3_BUCKET/$S3_PREFIX/? (y/n) " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "Upload cancelled."
    exit 0
fi

# Upload to S3
echo "Uploading model to S3..."
aws s3 sync "$MODEL_DIR/" "s3://$S3_BUCKET/$S3_PREFIX/" \
    --region $AWS_REGION \
    --exclude "*.git/*" \
    --exclude "__pycache__/*"

echo ""
echo "✅ Model uploaded successfully!"
echo ""
echo "S3 Location: s3://$S3_BUCKET/$S3_PREFIX/"
echo ""
echo "To use this model, update your .env file:"
echo "  S3_BUCKET=$S3_BUCKET"
echo "  S3_PREFIX=$S3_PREFIX"
echo ""
echo "FastAPI will automatically download this model on startup!"

