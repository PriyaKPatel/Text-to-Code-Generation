# 🤖 Text-to-Code Generation with AI

[![CI/CD Pipeline](https://github.com/PriyaKPatel/Text-to-Code-Generation/actions/workflows/deploy.yml/badge.svg)](https://github.com/PriyaKPatel/Text-to-Code-Generation/actions)
[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.109.0-green.svg)](https://fastapi.tiangolo.com/)
[![TensorFlow](https://img.shields.io/badge/TensorFlow-2.16-orange.svg)](https://www.tensorflow.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

> **Transform natural language into Python code using a fine-tuned CodeT5 model**  
> A complete end-to-end MLOps project with production-grade deployment, CI/CD, and monitoring.

---

## 🌟 **Live Demo**

**Try it now:** [http://44.210.237.157/](http://44.210.237.157/)

🎯 **Interactive Web UI** - Chat-like interface with real-time code generation  
📖 **API Documentation** - [http://44.210.237.157/docs](http://44.210.237.157/docs)  
💚 **Health Check** - [http://44.210.237.157/health](http://44.210.237.157/health)

---

## 📋 **Table of Contents**

- [Overview](#-overview)
- [Features](#-key-features)
- [Demo](#-demo)
- [Architecture](#-architecture)
- [Tech Stack](#-tech-stack)
- [Quick Start](#-quick-start)
- [API Usage](#-api-usage)
- [Deployment](#-deployment)
- [Testing](#-testing)
- [Monitoring](#-monitoring)
- [Project Structure](#-project-structure)
- [Performance](#-performance)
- [Future Enhancements](#-future-enhancements)

---

## 🎯 **Overview**

This project demonstrates a **complete MLOps pipeline** for deploying an AI-powered code generation model. It showcases best practices in machine learning operations, including:

- ✅ **Model Training**: Fine-tuned CodeT5 on 2,000+ code generation tasks (MBPP dataset)
- ✅ **Production API**: FastAPI with async support, validation, and error handling
- ✅ **Modern Frontend**: React-based chat interface with typing animations
- ✅ **Containerization**: Optimized Docker images with multi-stage builds
- ✅ **Cloud Deployment**: AWS EC2 with S3 model storage and ECR registry
- ✅ **CI/CD**: Automated testing, building, and deployment via GitHub Actions
- ✅ **Monitoring**: Prometheus metrics, health checks, and structured logging

### **Key Statistics**

| Metric | Value |
|--------|-------|
| **Model** | CodeT5 (Salesforce, T5-based) |
| **Parameters** | 220M |
| **Training Data** | MBPP (Mostly Basic Python Problems) |
| **Fine-tuning** | 3 epochs on 2,000+ samples |
| **API Latency** | ~20-30 seconds per request |
| **Deployment** | AWS EC2 (t2.large, 2 vCPUs, 8GB RAM) |
| **Model Storage** | AWS S3 (~1GB) |
| **Container** | Docker (optimized for CPU) |

---

## ✨ **Key Features**

### **🤖 AI-Powered Code Generation**
- Convert natural language descriptions to Python code
- Supports functions, algorithms, and data structures
- Fine-tuned on real-world coding problems

### **🎨 Beautiful Web Interface**
- Modern React UI with gradient animations
- Chat-like interaction with typing effects
- Copy-to-clipboard functionality
- Responsive design for mobile and desktop

### **⚡ Production-Ready API**
- FastAPI with automatic OpenAPI documentation
- Request validation with Pydantic V2
- Async/await for concurrent requests
- CORS enabled for cross-origin access
- Comprehensive error handling

### **🐳 Containerized & Cloud-Native**
- Optimized Docker images (~2GB)
- S3 integration for model weights
- ECR for container registry
- Health checks and graceful shutdown

### **🔄 Automated CI/CD**
- GitHub Actions workflow
- Automated testing with pytest (18 tests)
- Docker build and push to ECR
- Zero-downtime deployment to EC2
- Health verification post-deployment

### **📊 Monitoring & Observability**
- Prometheus metrics (requests, latency, errors)
- Structured logging with timestamps
- Health check endpoint
- API statistics endpoint

---

## 🎬 **Demo**

### **Web Interface**
Visit [http://44.210.237.157/](http://44.210.237.157/) to try the interactive UI.

**Example Prompts:**
```
✨ "Create a function to sort a list"
✨ "Build a binary search algorithm"
✨ "Make a function to reverse a string"
✨ "Generate a fibonacci sequence"
```

### **API Example**

```bash
curl -X POST "http://44.210.237.157/generate" \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "write a function to calculate factorial",
    "max_length": 150,
    "temperature": 0.7
  }'
```

**Response:**
```json
{
  "code": "def factorial(n):\n    if n <= 1:\n        return 1\n    return n * factorial(n - 1)",
  "latency": 25.42,
  "timestamp": "2026-01-02T08:00:00.123456",
  "prompt": "write a function to calculate factorial"
}
```

---

## 🏗️ **Architecture**

```
┌─────────────────────────────────────────────────────────────────┐
│                         USER / CLIENT                            │
└───────────────────┬─────────────────────────────────────────────┘
                    │
                    ▼
        ┌───────────────────────────┐
        │   React Frontend (UI)     │
        │   - Chat Interface        │
        │   - Code Display          │
        │   - Copy to Clipboard     │
        └───────────┬───────────────┘
                    │
                    ▼
        ┌───────────────────────────┐
        │   FastAPI Backend         │
        │   - /generate endpoint    │
        │   - /health endpoint      │
        │   - /metrics (Prometheus) │
        └───────────┬───────────────┘
                    │
                    ▼
        ┌───────────────────────────┐
        │   T5CodeGenerator         │
        │   - TensorFlow Model      │
        │   - Tokenizer             │
        │   - Inference Engine      │
        └───────────┬───────────────┘
                    │
                    ▼
        ┌───────────────────────────┐
        │   AWS S3 (Model Storage)  │
        │   - tf_model.h5 (~1GB)    │
        │   - tokenizer files       │
        │   - config.json           │
        └───────────────────────────┘
```

### **CI/CD Pipeline**

```
┌─────────────┐      ┌──────────────┐      ┌─────────────┐
│   Push to   │─────▶│   GitHub     │─────▶│   Run       │
│   GitHub    │      │   Actions    │      │   Tests     │
└─────────────┘      └──────────────┘      └──────┬──────┘
                                                    │
                                                    ▼
                                            ┌───────────────┐
                                            │  Build Docker │
                                            │  Image        │
                                            └───────┬───────┘
                                                    │
                                                    ▼
                                            ┌───────────────┐
                                            │  Push to ECR  │
                                            │  Registry     │
                                            └───────┬───────┘
                                                    │
                                                    ▼
                                            ┌───────────────┐
                                            │  Deploy to    │
                                            │  EC2 Instance │
                                            └───────┬───────┘
                                                    │
                                                    ▼
                                            ┌───────────────┐
                                            │  Health Check │
                                            │  ✅ Success    │
                                            └───────────────┘
```

---

## 🛠️ **Tech Stack**

### **Machine Learning**
- **Model**: CodeT5 (Salesforce/codet5-base)
- **Framework**: TensorFlow 2.16 with Keras
- **Library**: Hugging Face Transformers 4.48+
- **Tokenizer**: RobertaTokenizer
- **Training**: Google Colab (GPU)

### **Backend**
- **API Framework**: FastAPI 0.109.0
- **Server**: Uvicorn (ASGI)
- **Validation**: Pydantic V2
- **Logging**: Python logging + structured logs

### **Frontend**
- **Framework**: React 18 (CDN)
- **Styling**: Tailwind CSS
- **Icons**: Lucide React (SVG)
- **Build**: Single HTML file (no build step)

### **Infrastructure**
- **Cloud Provider**: AWS
- **Compute**: EC2 (t2.large)
- **Storage**: S3 (model weights)
- **Registry**: ECR (Docker images)
- **IAM**: Role-based access (EC2-SSM-Role)

### **DevOps**
- **Containerization**: Docker (single-stage optimized)
- **CI/CD**: GitHub Actions
- **Version Control**: Git + GitHub
- **Monitoring**: Prometheus metrics

### **Testing**
- **Framework**: pytest 7.4.3
- **Async**: pytest-asyncio
- **Mocking**: unittest.mock
- **Coverage**: 18 passing tests

---

## 🚀 **Quick Start**

### **Prerequisites**

- Python 3.9+
- Docker (optional, for containerized deployment)
- AWS Account (for cloud deployment)

### **Local Development**

```bash
# 1. Clone the repository
git clone https://github.com/PriyaKPatel/Text-to-Code-Generation.git
cd Text-to-Code-Generation

# 2. Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Set environment variables
export MODEL_PATH=./models_local
export S3_BUCKET=your-bucket-name  # Optional, for S3 model loading
export S3_PREFIX=models/v1

# 5. Run the API
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

**Access the application:**
- **Web UI**: http://localhost:8000/
- **API Docs**: http://localhost:8000/docs
- **Health**: http://localhost:8000/health

---

## 📡 **API Usage**

### **Endpoints**

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/` | GET | React frontend UI |
| `/generate` | POST | Generate Python code from prompt |
| `/health` | GET | Health check with model status |
| `/api/info` | GET | API version and endpoints |
| `/metrics` | GET | Prometheus metrics |
| `/stats` | GET | API statistics |
| `/docs` | GET | Swagger UI documentation |

### **Generate Code (cURL)**

```bash
curl -X POST "http://44.210.237.157/generate" \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "create a function to check if a number is prime",
    "max_length": 150,
    "temperature": 0.7,
    "num_return_sequences": 1
  }'
```

### **Generate Code (Python)**

```python
import requests

url = "http://44.210.237.157/generate"
payload = {
    "prompt": "write a function to merge two sorted lists",
    "max_length": 200,
    "temperature": 0.8
}

response = requests.post(url, json=payload)
result = response.json()

print(f"Generated Code:\n{result['code']}")
print(f"Latency: {result['latency']} seconds")
```

### **Health Check**

```bash
curl http://44.210.237.157/health
```

**Response:**
```json
{
  "status": "healthy",
  "model_loaded": true,
  "timestamp": "2026-01-02T08:00:00.123456",
  "version": "1.0.0",
  "error": null
}
```

---

## 🐳 **Deployment**

### **Local Docker**

```bash
# Build image
docker build -t text-to-code:latest .

# Run container
docker run -d \
  --name text-to-code \
  -p 8000:8000 \
  -e MODEL_PATH=/app/models \
  -e S3_BUCKET=your-bucket \
  -e S3_PREFIX=models/v1 \
  -e AWS_DEFAULT_REGION=us-east-1 \
  text-to-code:latest

# View logs
docker logs -f text-to-code
```

### **AWS EC2 Deployment**

The project includes automated deployment scripts:

```bash
# 1. Upload model to S3
./scripts/upload-model-to-s3.sh

# 2. Deploy updated model
./scripts/deploy-updated-model.sh

# 3. (Optional) Build on EC2 directly
./scripts/build-on-ec2.sh
```

### **CI/CD with GitHub Actions**

**Setup GitHub Secrets:**

1. Go to your repo → Settings → Secrets and variables → Actions
2. Add the following secrets:
   - `AWS_ACCOUNT_ID`
   - `AWS_ACCESS_KEY_ID`
   - `AWS_SECRET_ACCESS_KEY`
   - `EC2_HOST` (e.g., `44.210.237.157`)
   - `EC2_USERNAME` (e.g., `ubuntu`)
   - `EC2_SSH_KEY` (contents of `.pem` file)
   - `S3_BUCKET`
   - `S3_PREFIX`

**Workflow triggers automatically on:**
- Push to `main` branch
- Pull requests to `main`

**Pipeline stages:**
1. ✅ **Test** (~2-3 min) - Run pytest
2. ✅ **Build & Push** (~7-10 min) - Docker build + ECR push
3. ✅ **Deploy** (~2-3 min) - Deploy to EC2 + health check

---

## 🧪 **Testing**

```bash
# Run all tests
pytest tests/ -v

# Run with coverage
pytest tests/ --cov=app --cov-report=html --cov-report=term

# Run specific test file
pytest tests/test_api.py -v

# Run flake8 linting
flake8 app/ tests/ --max-line-length=120
```

**Test Coverage:**
- ✅ Root endpoint (HTML UI)
- ✅ API info endpoint
- ✅ Health checks
- ✅ Code generation endpoint
- ✅ Error handling (validation errors, model not loaded)
- ✅ CORS headers
- ✅ Full workflow integration

**Current Status:** 18/18 tests passing ✅

---

## 📊 **Monitoring**

### **Prometheus Metrics**

Access at: `http://44.210.237.157/metrics`

**Available Metrics:**
```
# Request count by status
text_to_code_requests_total{status="success"} 42
text_to_code_requests_total{status="error"} 2

# Request latency histogram
text_to_code_latency_seconds_bucket{le="5.0"} 38
text_to_code_latency_seconds_bucket{le="10.0"} 42

# Active requests gauge
text_to_code_active_requests 1

# Model load status
text_to_code_model_loaded 1
```

### **Structured Logging**

All logs include:
- Timestamp
- Log level (INFO, WARNING, ERROR)
- Module name
- Request/response details
- Latency measurements

**Example:**
```
2026-01-02 08:00:00,123 - app.main - INFO - Request: POST /generate
2026-01-02 08:00:25,456 - app.main - INFO - Response: POST /generate Status: 200 Time: 25.3s
```

---

## 🗂️ **Project Structure**

```
Text-to-Code-Generation/
│
├── app/                          # FastAPI application
│   ├── __init__.py
│   ├── main.py                   # FastAPI app + routes
│   ├── model.py                  # T5CodeGenerator class
│   ├── schemas.py                # Pydantic models
│   └── index.html                # React frontend UI
│
├── tests/                        # Test suite
│   ├── __init__.py
│   ├── conftest.py               # Pytest fixtures + mocking
│   └── test_api.py               # API endpoint tests
│
├── scripts/                      # Deployment scripts
│   ├── upload-model-to-s3.sh    # Upload model to S3
│   ├── deploy-updated-model.sh  # Deploy to EC2
│   ├── build-on-ec2.sh          # Build on EC2 directly
│   └── fix-ec2-disk-space.sh    # Cleanup EC2 disk
│
├── .github/
│   └── workflows/
│       └── deploy.yml            # CI/CD pipeline
│
├── docs/                         # Documentation
│   ├── GITHUB_SECRETS_SETUP.md  # Secrets configuration guide
│   ├── MLOps_2Day_Crash_Course.md
│   ├── MLOps_Interview_Questions_Part1.md
│   └── MLOps_Interview_Questions_Part2.md
│
├── models/                       # Model weights (gitignored)
│   ├── config.json
│   ├── tf_model.h5               # TensorFlow weights (~1GB)
│   ├── tokenizer_config.json
│   └── vocab.json
│
├── Dockerfile                    # Docker image definition
├── requirements.txt              # Python dependencies
├── .gitignore                    # Git ignore rules
├── .env.local                    # Local environment config
└── README.md                     # This file
```

---

## 📈 **Performance**

### **Benchmarks** (AWS EC2 t2.large)

| Metric | Value | Details |
|--------|-------|---------|
| **Cold Start** | ~90s | Model download from S3 + TF init |
| **Warm Start** | ~10s | Model already in memory |
| **Average Latency** | ~25s | Per code generation request |
| **Throughput** | ~2-3 req/min | Single worker (CPU-bound) |
| **Memory Usage** | ~2.5GB | TensorFlow model + runtime |
| **Model Size** | ~1GB | Compressed tf_model.h5 |
| **Container Size** | ~2GB | Optimized Docker image |

### **Optimization Tips**

To improve performance:
1. **Use GPU Instance** (e.g., AWS g4dn.xlarge) → 10x faster
2. **Convert to PyTorch** → Better CPU performance
3. **Model Quantization** → Reduce size by 4x
4. **Batch Processing** → Process multiple requests together
5. **Redis Caching** → Cache common prompts

---

## 🚧 **Future Enhancements**

### **Phase 1: Model Improvements** 🎯
- [ ] Train for more epochs (10+ instead of 3)
- [ ] Fine-tune on larger dataset (CodeParrot, GitHub Code)
- [ ] Convert TensorFlow model to PyTorch
- [ ] Model quantization (INT8) for faster inference
- [ ] Support multiple programming languages (JS, Java, etc.)

### **Phase 2: Performance Optimization** ⚡
- [ ] Implement Redis caching for repeated prompts
- [ ] Add GPU support (CUDA)
- [ ] Batch inference for multiple requests
- [ ] Model distillation (reduce size)
- [ ] WebSocket support for streaming responses

### **Phase 3: Enhanced Monitoring** 📊
- [ ] CloudWatch Alarms (CPU, Memory, Errors)
- [ ] Grafana dashboards
- [ ] Distributed tracing (OpenTelemetry)
- [ ] User analytics and usage patterns
- [ ] A/B testing infrastructure

### **Phase 4: Advanced Features** 🎨
- [ ] Code explanation (reverse: code → description)
- [ ] Code completion (GitHub Copilot style)
- [ ] Multi-language support
- [ ] Syntax validation before returning
- [ ] Code execution sandbox (optional)
- [ ] User authentication and API keys
- [ ] Rate limiting per user

### **Phase 5: Scale & Reliability** 🌐
- [ ] Kubernetes deployment (EKS)
- [ ] Auto-scaling based on load
- [ ] Multi-region deployment
- [ ] Load balancer (ALB)
- [ ] Database for user history
- [ ] HTTPS with SSL certificate
- [ ] Custom domain name

---

## 🤝 **Contributing**

Contributions are welcome! Here's how you can help:

1. **Fork** the repository
2. **Create** a feature branch (`git checkout -b feature/AmazingFeature`)
3. **Commit** your changes (`git commit -m 'Add AmazingFeature'`)
4. **Push** to the branch (`git push origin feature/AmazingFeature`)
5. **Open** a Pull Request

**Areas for contribution:**
- Model improvements (training, datasets)
- Frontend enhancements (UI/UX)
- Performance optimizations
- Documentation improvements
- Bug fixes and testing

---

## 📄 **License**

This project is licensed under the **MIT License** - see the [LICENSE](LICENSE) file for details.

---

## 👤 **Author**

**Priya K Patel**

- 🌐 Portfolio: [Your Portfolio](https://yourportfolio.com)
- 💼 LinkedIn: [linkedin.com/in/your-profile](https://linkedin.com/in/your-profile)
- 📧 Email: your.email@example.com
- 🐙 GitHub: [@PriyaKPatel](https://github.com/PriyaKPatel)

---

## 🙏 **Acknowledgments**

- **Salesforce Research** - CodeT5 model
- **Hugging Face** - Transformers library
- **Google Research** - T5 architecture
- **MBPP Dataset** - Training data
- **FastAPI** - Modern Python API framework
- **AWS** - Cloud infrastructure
- **GitHub Actions** - CI/CD platform

---

## 📞 **Support**

If you found this project helpful, please ⭐ **star the repository**!

For questions or issues:
- 🐛 Open an [Issue](https://github.com/PriyaKPatel/Text-to-Code-Generation/issues)
- 💬 Start a [Discussion](https://github.com/PriyaKPatel/Text-to-Code-Generation/discussions)

---

<div align="center">

**Built with ❤️ by Priya K Patel**

[![GitHub stars](https://img.shields.io/github/stars/PriyaKPatel/Text-to-Code-Generation?style=social)](https://github.com/PriyaKPatel/Text-to-Code-Generation/stargazers)
[![GitHub forks](https://img.shields.io/github/forks/PriyaKPatel/Text-to-Code-Generation?style=social)](https://github.com/PriyaKPatel/Text-to-Code-Generation/network/members)

</div>
