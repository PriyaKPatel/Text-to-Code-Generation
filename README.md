# Text-to-Code Generation 🚀

[![CI/CD](https://github.com/PriyaKPatel/Text-to-Code-Generation/actions/workflows/deploy.yml/badge.svg)](https://github.com/PriyaKPatel/Text-to-Code-Generation/actions)
[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.109.0-green.svg)](https://fastapi.tiangolo.com/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

Generate Python code from natural language descriptions using a fine-tuned T5 model. This project demonstrates end-to-end MLOps practices including containerization, CI/CD, cloud deployment, and monitoring.

## 📊 Project Overview

- **Model**: Fine-tuned T5 (Text-to-Text Transfer Transformer)
- **Training Data**: 2,000+ coding tasks with natural language descriptions
- **Accuracy**: 86% on code generation tasks
- **Deployment**: Containerized with Docker, deployed on AWS EC2
- **API**: FastAPI with automatic documentation
- **Monitoring**: Prometheus metrics, CloudWatch integration

## ✨ Features

- 🤖 **AI-Powered Code Generation**: Convert natural language to Python code
- 🐳 **Fully Containerized**: Docker and Docker Compose support
- ☁️ **Cloud-Ready**: AWS EC2 deployment with S3 model storage
- 🔄 **CI/CD Pipeline**: Automated testing and deployment with GitHub Actions
- 📊 **Monitoring**: Built-in Prometheus metrics and health checks
- 📚 **Auto-Generated Docs**: Interactive API documentation with Swagger UI
- 🧪 **Comprehensive Testing**: Unit tests with pytest
- ⚡ **Production-Ready**: Proper logging, error handling, and validation

## 🏗️ Architecture

```
┌─────────────┐      ┌──────────────┐      ┌─────────────┐
│   GitHub    │─────▶│ GitHub       │─────▶│   AWS ECR   │
│ Repository  │      │   Actions    │      │   (Docker)  │
└─────────────┘      └──────────────┘      └─────────────┘
                            │                      │
                            ▼                      ▼
                     ┌──────────────┐      ┌─────────────┐
                     │   Run Tests  │      │   AWS EC2   │
                     │   + Build    │      │  (FastAPI)  │
                     └──────────────┘      └─────────────┘
                                                  │
                                                  ▼
                                           ┌─────────────┐
                                           │   AWS S3    │
                                           │  (Models)   │
                                           └─────────────┘
```

## 🚀 Quick Start

### Prerequisites

- Python 3.9+
- Docker and Docker Compose
- AWS Account (for cloud deployment)
- AWS CLI configured

### Local Development

1. **Clone the repository**
```bash
git clone https://github.com/PriyaKPatel/Text-to-Code-Generation.git
cd Text-to-Code-Generation
```

2. **Set up environment**
```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

3. **Configure environment variables**
```bash
cp .env.example .env
# Edit .env with your configuration
```

4. **Run locally**
```bash
# Using uvicorn directly
uvicorn app.main:app --reload

# Or using Docker
docker-compose up --build
```

5. **Access the API**
- API: http://localhost:8000
- Docs: http://localhost:8000/docs
- Health: http://localhost:8000/health

## 🐳 Docker Deployment

### Build and Run

```bash
# Build image
docker build -t text-to-code:latest .

# Run container
docker run -d \
  -p 8000:8000 \
  --name text-to-code \
  -e S3_BUCKET=your-bucket \
  text-to-code:latest
```

### Using Docker Compose

```bash
# Start all services
docker-compose up -d

# With monitoring (Prometheus + Grafana)
docker-compose --profile monitoring up -d

# View logs
docker-compose logs -f api

# Stop services
docker-compose down
```

## ☁️ AWS Deployment

### 1. Setup AWS Resources

```bash
# Set your AWS account ID
export AWS_ACCOUNT_ID=123456789012
export AWS_REGION=us-east-1

# Run deployment script
chmod +x scripts/deploy-aws.sh
./scripts/deploy-aws.sh
```

### 2. Launch EC2 Instance

```bash
# SSH into your EC2 instance
ssh -i your-key.pem ubuntu@YOUR_EC2_IP

# Run setup script
chmod +x setup-ec2.sh
./setup-ec2.sh

# Configure AWS CLI
aws configure
```

### 3. Deploy Application

```bash
# Login to ECR
aws ecr get-login-password --region us-east-1 | \
  docker login --username AWS --password-stdin \
  $AWS_ACCOUNT_ID.dkr.ecr.us-east-1.amazonaws.com

# Pull and run
docker pull $AWS_ACCOUNT_ID.dkr.ecr.us-east-1.amazonaws.com/text-to-code:latest
docker run -d -p 80:8000 --name text-to-code \
  -e AWS_DEFAULT_REGION=us-east-1 \
  $AWS_ACCOUNT_ID.dkr.ecr.us-east-1.amazonaws.com/text-to-code:latest
```

## 🔄 CI/CD Pipeline

The project uses GitHub Actions for automated CI/CD:

1. **Test**: Run pytest, linting, type checking
2. **Build**: Build Docker image and push to ECR
3. **Deploy**: Deploy to EC2 instance
4. **Verify**: Run health checks

### Setup GitHub Secrets

Add these secrets to your GitHub repository:

- `AWS_ACCESS_KEY_ID`
- `AWS_SECRET_ACCESS_KEY`
- `AWS_REGION`
- `EC2_HOST`
- `EC2_USERNAME`
- `EC2_SSH_KEY`
- `S3_BUCKET`

## 📡 API Usage

### Generate Code

```bash
# Using curl
curl -X POST "http://localhost:8000/generate" \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "create a function to calculate factorial",
    "max_length": 150,
    "temperature": 0.7
  }'

# Response
{
  "code": "def factorial(n):\n    if n <= 1:\n        return 1\n    return n * factorial(n - 1)",
  "latency": 0.342,
  "timestamp": "2025-01-15T10:30:00Z",
  "prompt": "create a function to calculate factorial"
}
```

### Python Client Example

```python
import requests

response = requests.post(
    "http://localhost:8000/generate",
    json={
        "prompt": "create a function to reverse a string",
        "max_length": 100
    }
)

code = response.json()["code"]
print(code)
```

## 🧪 Testing

```bash
# Run all tests
pytest tests/ -v

# Run with coverage
pytest tests/ --cov=app --cov-report=html

# Run specific test file
pytest tests/test_api.py -v

# Run linting
flake8 app/ tests/

# Type checking
mypy app/ --ignore-missing-imports
```

## 📊 Monitoring

### Prometheus Metrics

Access metrics at: `http://localhost:8000/metrics`

Available metrics:
- `text_to_code_requests_total`: Total requests
- `text_to_code_latency_seconds`: Request latency
- `text_to_code_active_requests`: Active requests
- `text_to_code_model_loaded`: Model status

### Health Check

```bash
curl http://localhost:8000/health

{
  "status": "healthy",
  "model_loaded": true,
  "timestamp": "2025-01-15T10:30:00Z",
  "version": "1.0.0"
}
```

### CloudWatch (AWS)

- Container logs automatically shipped to CloudWatch
- Custom metrics for API performance
- Alarms configured for:
  - High CPU usage (>80%)
  - High memory (>85%)
  - API errors

## 🗂️ Project Structure

```
text-to-code-generation/
├── app/
│   ├── __init__.py
│   ├── main.py              # FastAPI application
│   ├── model.py             # T5 model wrapper
│   └── schemas.py           # Pydantic models
├── tests/
│   ├── __init__.py
│   └── test_api.py          # API tests
├── deployment/
│   ├── kubernetes/
│   │   ├── deployment.yaml  # K8s deployment
│   │   └── service.yaml     # K8s service
│   └── prometheus.yml       # Prometheus config
├── scripts/
│   ├── setup-ec2.sh         # EC2 setup script
│   ├── deploy-local.sh      # Local deployment
│   └── deploy-aws.sh        # AWS deployment
├── .github/
│   └── workflows/
│       └── deploy.yml       # CI/CD pipeline
├── models/                  # Model weights (gitignored)
├── Dockerfile               # Docker image definition
├── docker-compose.yml       # Docker Compose config
├── requirements.txt         # Python dependencies
├── .env.example             # Environment template
└── README.md                # This file
```

## 🛠️ Technologies Used

- **ML Framework**: PyTorch, Transformers (Hugging Face)
- **API Framework**: FastAPI
- **Server**: Uvicorn
- **Containerization**: Docker, Docker Compose
- **Orchestration**: Kubernetes (optional)
- **Cloud**: AWS (EC2, S3, ECR, CloudWatch)
- **CI/CD**: GitHub Actions
- **Monitoring**: Prometheus, Grafana
- **Testing**: Pytest
- **Code Quality**: Black, Flake8, MyPy

## 📈 Performance

- **Latency**: ~300-500ms per request (CPU)
- **Throughput**: ~10-20 requests/second
- **Model Size**: 220M parameters (T5-base)
- **Accuracy**: 86% on test set

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request


## Author

**Priya Patel**
- GitHub: [@PriyaKPatel](https://github.com/PriyaKPatel)
- LinkedIn: [Your LinkedIn](https://linkedin.com/in/YOUR_PROFILE)

## Acknowledgments

- Google Research for the T5 model
- Hugging Face for the Transformers library
