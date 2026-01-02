#!/bin/bash
# Project Setup Script
# This script sets up your Text-to-Code project structure

set -e

echo "=========================================="
echo "Text-to-Code Project Setup"
echo "=========================================="
echo ""

# Get project directory
read -p "Enter project directory name (default: text-to-code-generation): " PROJECT_DIR
PROJECT_DIR=${PROJECT_DIR:-text-to-code-generation}

# Create project directory
echo "Creating project directory: $PROJECT_DIR"
mkdir -p "$PROJECT_DIR"
cd "$PROJECT_DIR"

# Create directory structure
echo "Creating directory structure..."
mkdir -p app
mkdir -p tests
mkdir -p deployment/kubernetes
mkdir -p scripts
mkdir -p models
mkdir -p .github/workflows

echo "✅ Directory structure created"

# Get user information
echo ""
echo "Please provide your information:"
read -p "Your Name: " USER_NAME
read -p "Your GitHub Username: " GITHUB_USER
read -p "Your AWS Account ID: " AWS_ACCOUNT
read -p "Your AWS Region (default: us-east-1): " AWS_REGION
AWS_REGION=${AWS_REGION:-us-east-1}

echo ""
echo "Configuration:"
echo "  Name: $USER_NAME"
echo "  GitHub: $GITHUB_USER"
echo "  AWS Account: $AWS_ACCOUNT"
echo "  AWS Region: $AWS_REGION"
echo ""

# Initialize git
echo "Initializing git repository..."
git init
git branch -M main

echo "✅ Git initialized"

# Create placeholder .gitkeep files
touch models/.gitkeep

echo ""
echo "=========================================="
echo "✅ Project setup complete!"
echo "=========================================="
echo ""
echo "Next steps:"
echo "1. Copy all project files into this directory"
echo "2. Update placeholders in files:"
echo "   - YOUR_USERNAME → $GITHUB_USER"
echo "   - YOUR_ACCOUNT_ID → $AWS_ACCOUNT"
echo "   - Your Name → $USER_NAME"
echo "3. Create .env file from .env.example"
echo "4. Install dependencies: pip install -r requirements.txt"
echo "5. Test locally: uvicorn app.main:app --reload"
echo "6. Commit to GitHub:"
echo "   git add ."
echo "   git commit -m 'Initial commit'"
echo "   git remote add origin https://github.com/$GITHUB_USER/text-to-code-generation.git"
echo "   git push -u origin main"
echo ""
echo "See IMPLEMENTATION_GUIDE.md for detailed steps!"
