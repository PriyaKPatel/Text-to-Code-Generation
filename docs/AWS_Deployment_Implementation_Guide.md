Text-to-Code Project: Complete AWS Deployment & MLOps Implementation Guide
Step-by-Step Implementation for Your GitHub Project
## PREREQUISITES
Before starting, ensure you have:
✓ AWS account (free tier is sufficient for testing)
✓ AWS CLI installed and configured with access keys
✓ Docker installed on your local machine
✓ Git repository with your Text-to-Code project
✓ Python 3.8+ installed
## PART 1: REORGANIZE PROJECT STRUCTURE
Create this directory structure in your repository:
text-to-code-generation/
├── app/
│   ├── __init__.py
│   ├── main.py              # FastAPI application
│   ├── model.py             # Model loading and inference
│   └── schemas.py           # Pydantic models
├── models/                   # Store model weights (add to .gitignore)
│   └── .gitkeep
├── tests/
│   ├── __init__.py
│   └── test_api.py          # API tests
├── .github/
│   └── workflows/
│       └── deploy.yml       # CI/CD pipeline
├── deployment/
│   ├── docker-compose.yml
│   └── kubernetes/          # K8s manifests
│       ├── deployment.yaml
│       └── service.yaml
├── Dockerfile
├── requirements.txt
├── .dockerignore
├── .gitignore
└── README.md
## PART 2: DOCKERIZE YOUR APPLICATION
Step 1: Create Dockerfile
Create file: Dockerfile
# Multi-stage build for optimization
FROM python:3.9-slim as builder

WORKDIR /build
COPY requirements.txt .
RUN pip install --no-cache-dir --user -r requirements.txt

# Runtime stage
FROM python:3.9-slim

WORKDIR /app

# Copy dependencies from builder
COPY --from=builder /root/.local /root/.local
ENV PATH=/root/.local/bin:$PATH

# Copy application code
COPY app/ ./app/

# Health check
HEALTHCHECK --interval=30s --timeout=10s --retries=3 \
CMD curl -f http://localhost:8000/health || exit 1

## EXPOSE 8000

# Run with uvicorn
CMD ['uvicorn', 'app.main:app', '--host', '0.0.0.0', '--port', '8000']
Step 2: Create .dockerignore
__pycache__
*.pyc
*.pyo
.git
.gitignore
README.md
tests/
.venv/
venv/
Step 3: Update FastAPI Application
Create file: app/main.py
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from prometheus_client import Counter, Histogram, generate_latest
from fastapi.responses import Response
import time
import logging
from .model import T5CodeGenerator
from .schemas import CodeRequest, CodeResponse

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Prometheus metrics
REQUEST_COUNT = Counter('text_to_code_requests_total', 'Total requests')
REQUEST_LATENCY = Histogram('text_to_code_latency_seconds', 'Request latency')

app = FastAPI(title='Text-to-Code API', version='1.0.0')

# Initialize model
generator = T5CodeGenerator()

@app.get('/health')
async def health_check():
return {'status': 'healthy', 'model_loaded': generator.is_loaded()}

@app.post('/generate', response_model=CodeResponse)
async def generate_code(request: CodeRequest):
start_time = time.time()
REQUEST_COUNT.inc()

try:
code = generator.generate(request.prompt)
latency = time.time() - start_time
REQUEST_LATENCY.observe(latency)

logger.info(f'Generated code in {latency:.2f}s')
return CodeResponse(code=code, latency=latency)
except Exception as e:
logger.error(f'Error: {str(e)}')
raise HTTPException(status_code=500, detail=str(e))

@app.get('/metrics')
async def metrics():
return Response(content=generate_latest(), media_type='text/plain')
Step 4: Build and Test Docker Image
Run these commands:
# Build image
docker build -t text-to-code:latest .

# Run container locally
docker run -p 8000:8000 text-to-code:latest

# Test the API
curl -X POST http://localhost:8000/generate \
-H 'Content-Type: application/json' \
-d '{"prompt": "create a function to sort a list"}'
## PART 3: DEPLOY TO AWS EC2
Step 1: Push Docker Image to ECR
# Create ECR repository
aws ecr create-repository --repository-name text-to-code

# Login to ECR
aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin YOUR_ACCOUNT_ID.dkr.ecr.us-east-1.amazonaws.com

# Tag and push image
docker tag text-to-code:latest YOUR_ACCOUNT_ID.dkr.ecr.us-east-1.amazonaws.com/text-to-code:latest
docker push YOUR_ACCOUNT_ID.dkr.ecr.us-east-1.amazonaws.com/text-to-code:latest
Step 2: Upload Model to S3
# Create S3 bucket
aws s3 mb s3://text-to-code-models

# Upload model weights
aws s3 cp models/ s3://text-to-code-models/v1/ --recursive
Step 3: Launch EC2 Instance
In AWS Console:
1. Navigate to EC2 → Launch Instance
2. Choose Ubuntu Server 22.04 LTS
3. Select t3.large (2 vCPU, 8GB RAM) for testing
4. Configure Security Group:
- SSH (22) from your IP
- HTTP (80) from anywhere
- HTTPS (443) from anywhere
- Custom TCP (8000) from anywhere
5. Create new key pair or use existing
6. Attach IAM role with EC2 and S3 permissions
7. Launch instance
Step 4: Configure EC2 Instance
SSH into instance:
ssh -i your-key.pem ubuntu@YOUR_EC2_PUBLIC_IP

# Update system
sudo apt update && sudo apt upgrade -y

# Install Docker
sudo apt install docker.io -y
sudo systemctl start docker
sudo systemctl enable docker
sudo usermod -aG docker ubuntu

# Install AWS CLI
sudo apt install awscli -y

# Login to ECR
aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin YOUR_ACCOUNT_ID.dkr.ecr.us-east-1.amazonaws.com

# Pull Docker image
docker pull YOUR_ACCOUNT_ID.dkr.ecr.us-east-1.amazonaws.com/text-to-code:latest

# Run container
docker run -d -p 80:8000 --name text-to-code \
-e AWS_DEFAULT_REGION=us-east-1 \
YOUR_ACCOUNT_ID.dkr.ecr.us-east-1.amazonaws.com/text-to-code:latest
Step 5: Verify Deployment
# Test health endpoint
curl http://YOUR_EC2_PUBLIC_IP/health

# Test code generation
curl -X POST http://YOUR_EC2_PUBLIC_IP/generate \
-H 'Content-Type: application/json' \
-d '{"prompt": "create a function to reverse a string"}'
## PART 4: SETUP CI/CD WITH GITHUB ACTIONS
Step 1: Create GitHub Secrets
In GitHub repository → Settings → Secrets → Actions, add:
## • AWS_ACCESS_KEY_ID
## • AWS_SECRET_ACCESS_KEY
• AWS_REGION (e.g., us-east-1)
• ECR_REPOSITORY (YOUR_ACCOUNT_ID.dkr.ecr.us-east-1.amazonaws.com/text-to-code)
• EC2_HOST (EC2 public IP)
• EC2_SSH_KEY (private key content)
Step 2: Create GitHub Actions Workflow
Create file: .github/workflows/deploy.yml
name: Deploy to AWS EC2

on:
push:
branches: [ main ]

jobs:
test:
runs-on: ubuntu-latest
steps:
- uses: actions/checkout@v3
- name: Set up Python
uses: actions/setup-python@v4
with:
python-version: '3.9'
- name: Install dependencies
run: pip install -r requirements.txt
- name: Run tests
run: pytest tests/

build-and-push:
needs: test
runs-on: ubuntu-latest
steps:
- uses: actions/checkout@v3
- name: Configure AWS credentials
uses: aws-actions/configure-aws-credentials@v2
with:
aws-access-key-id: ${{ secrets.AWS_ACCESS_KEY_ID }}
aws-secret-access-key: ${{ secrets.AWS_SECRET_ACCESS_KEY }}
aws-region: ${{ secrets.AWS_REGION }}
- name: Login to ECR
run: aws ecr get-login-password | docker login --username AWS --password-stdin ${{ secrets.ECR_REPOSITORY }}
- name: Build and push Docker image
run: |
docker build -t ${{ secrets.ECR_REPOSITORY }}:${{ github.sha }} .
docker push ${{ secrets.ECR_REPOSITORY }}:${{ github.sha }}

deploy:
needs: build-and-push
runs-on: ubuntu-latest
steps:
- name: Deploy to EC2
uses: appleboy/ssh-action@master
with:
host: ${{ secrets.EC2_HOST }}
username: ubuntu
key: ${{ secrets.EC2_SSH_KEY }}
script: |
docker stop text-to-code || true
docker rm text-to-code || true
docker pull ${{ secrets.ECR_REPOSITORY }}:${{ github.sha }}
docker run -d -p 80:8000 --name text-to-code ${{ secrets.ECR_REPOSITORY }}:${{ github.sha }}
## PART 5: SETUP MONITORING
Step 1: Install CloudWatch Agent on EC2
SSH into EC2 and run:
wget https://s3.amazonaws.com/amazoncloudwatch-agent/ubuntu/amd64/latest/amazon-cloudwatch-agent.deb
sudo dpkg -i amazon-cloudwatch-agent.deb
Step 2: Setup CloudWatch Alarms
In AWS Console → CloudWatch → Alarms, create:
• CPU Utilization > 80% for 5 minutes
• Memory Utilization > 85%
• API Response Time > 2 seconds
## PART 6: UPDATE README & DOCUMENTATION
Update your README.md to include:
1. Project overview with updated architecture diagram
2. Installation and setup instructions
3. Docker build and run commands
4. API endpoints documentation
5. AWS deployment instructions
6. CI/CD pipeline description
7. Monitoring and logging details
8. Live demo link (http://YOUR_EC2_PUBLIC_IP/docs)
## IMPLEMENTATION CHECKLIST
Before Interview, Complete These:
☐ Dockerized application with multi-stage build
☐ Docker image pushed to AWS ECR
☐ Model weights stored in S3
☐ Application deployed on EC2 and accessible
☐ GitHub Actions CI/CD pipeline configured
☐ Health and metrics endpoints working
☐ CloudWatch monitoring setup
☐ README updated with all documentation
☐ Able to demo live endpoint
☐ Can explain each component and design decision
Implementation Time Estimate: 4-6 hours
Pro Tip: Take screenshots of each working component for your interview presentation! 📸