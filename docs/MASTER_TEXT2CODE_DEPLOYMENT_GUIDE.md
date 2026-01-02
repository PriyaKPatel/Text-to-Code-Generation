# Text-to-Code (CodeT5) — End-to-End Deployment Guide (Master)

This document consolidates all project guides into **one clean, non-duplicated, step-by-step playbook** for:
- Local setup → Docker → AWS (IAM/ECR/S3/EC2) → Production deployment
- Colab training → model upload to S3 → model update / rollback
- Optional CI/CD + monitoring

> **Project you currently have**: FastAPI app containerized with Docker, deployed to AWS EC2, pulling images from ECR and (optionally) pulling the model from S3.
> - **ECR**: `518627289438.dkr.ecr.us-east-1.amazonaws.com/text-to-code`
> - **S3**: `text-to-code-models-priya`
> - **EC2 Public IP**: `3.239.116.3`
> - **Region**: `us-east-1`

---

## 0) Big Picture Architecture

```
(Local Mac)                           (AWS)
┌──────────────┐     Docker build     ┌──────────────┐
│ FastAPI Code │ ───────────────────▶ │     ECR      │
│ + Dockerfile │     docker push      │ (Image Repo) │
└──────┬───────┘                      └──────┬───────┘
       │                                     │ docker pull
       │                                     ▼
       │                              ┌──────────────┐
       │                              │     EC2      │
       │  (Optional) Model files      │ Docker Run   │
       │  uploaded to S3              │ FastAPI API  │
       ▼                              └──────┬───────┘
┌──────────────┐                             │
│      S3      │ ◀──────── model download ───┘
│  (models/v*) │
└──────────────┘
```

---

## 1) Repository Contents (What each folder/file is for)

### Core application
- `app/main.py`: FastAPI endpoints (`/health`, `/generate`, `/metrics`, docs).
- `app/model.py`: Model loading (local/S3/HF fallback) + generation logic.
- `app/schemas.py`: Request/response schemas.

### Infra & automation
- `Dockerfile`, `docker-compose.yml`: containerization & local orchestration.
- `scripts/`: setup/deploy helpers (EC2 setup, deploy local/AWS, S3 upload).
- `.github/workflows/deploy.yml`: CI/CD pipeline (optional).

### Ops
- `tests/`: API tests.
- `deployment/`: Kubernetes manifests + Prometheus config (optional).

---

## 2) Prerequisites Checklist

### On your Mac
- Python 3.9+ with `venv`
- Docker Desktop
- AWS CLI (`aws --version`)
- Git

### On AWS
- IAM user with programmatic access
- ECR repository
- S3 bucket for model artifacts
- EC2 Ubuntu 22.04 instance with ports open (22/80/8000)

---

## 3) Phase 1 — Local Setup (Run once)

### 3.1 Create venv + install dependencies
```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 3.2 Configure environment
```bash
cp .env.example .env
# Edit .env with your values if needed
```

### 3.3 Run FastAPI locally
```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Test:
```bash
curl http://localhost:8000/health
curl -X POST http://localhost:8000/generate   -H "Content-Type: application/json"   -d '{"prompt":"Write a function to reverse a string","max_length":120}'
```

### 3.4 Docker local test
```bash
docker build -t text-to-code:latest .
docker run --rm -p 8000:8000 text-to-code:latest
```

---

## 4) Phase 2 — AWS Setup (IAM → ECR → S3 → EC2)

### 4.1 IAM user (programmatic access)
Create an IAM user (example: `text-to-code-deploy`) with policies:
- `AmazonEC2FullAccess`
- `AmazonS3FullAccess`
- `AmazonECRFullAccess`

Then configure locally:
```bash
aws configure
aws sts get-caller-identity
```

### 4.2 Create ECR repository
```bash
aws ecr create-repository --repository-name text-to-code --region us-east-1
aws ecr describe-repositories --region us-east-1
```

### 4.3 Create S3 bucket (globally unique name)
```bash
aws s3 mb s3://text-to-code-models-priya --region us-east-1
aws s3 ls | grep text-to-code
```

### 4.4 Launch EC2 instance (Ubuntu 22.04)
Minimum recommended: **t3.small+** for smoother inference; your current EC2 shows `t3.micro` in docs (likely tight on RAM for big models).

Security group inbound rules:
- SSH 22: **My IP**
- HTTP 80: Anywhere
- Custom 8000: Anywhere (or only 80 if you map 80→8000)

SSH test:
```bash
chmod 400 ~/Downloads/text-to-code-key.pem
ssh -i ~/Downloads/text-to-code-key.pem ubuntu@3.239.116.3
```

---

## 5) Phase 3 — Deploy to EC2 (ECR pull + docker run)

### 5.1 Push image to ECR (from Mac)
Login + push:
```bash
aws ecr get-login-password --region us-east-1 |   docker login --username AWS --password-stdin   518627289438.dkr.ecr.us-east-1.amazonaws.com

docker tag text-to-code:latest   518627289438.dkr.ecr.us-east-1.amazonaws.com/text-to-code:latest

docker push 518627289438.dkr.ecr.us-east-1.amazonaws.com/text-to-code:latest
```

### 5.2 Pull + run on EC2
SSH into EC2:
```bash
ssh -i ~/Downloads/text-to-code-key.pem ubuntu@3.239.116.3
```

Then:
```bash
docker stop text-to-code || true
docker rm text-to-code || true

aws ecr get-login-password --region us-east-1 |   docker login --username AWS --password-stdin   518627289438.dkr.ecr.us-east-1.amazonaws.com

docker pull 518627289438.dkr.ecr.us-east-1.amazonaws.com/text-to-code:latest

docker run -d   --name text-to-code   -p 80:8000   --restart unless-stopped   -e AWS_DEFAULT_REGION=us-east-1   -e S3_BUCKET=text-to-code-models-priya   -e S3_PREFIX=models/v1   518627289438.dkr.ecr.us-east-1.amazonaws.com/text-to-code:latest

docker logs -f text-to-code
```

From your Mac:
```bash
curl http://3.239.116.3/health
curl http://3.239.116.3/docs
```

---

## 6) Phase 3.5 — Make FastAPI match Notebook (Critical fixes)

If outputs are poor/nonsense, the top causes are:
1) Wrong model (T5-base instead of CodeT5)  
2) Wrong tokenizer (T5Tokenizer instead of RobertaTokenizer)  
3) Wrong prompt prefix (must match training: `Generate Python:`)  
4) Generation parameters mismatch  

**Target configuration:**
- Model: `Salesforce/codet5-base` (or your fine-tuned CodeT5)
- Tokenizer: `RobertaTokenizer`
- Prefix: `Generate Python: `
- Generation: `top_p=0.95, top_k=50, repetition_penalty=2.0, do_sample=True`

(Your docs indicate these were already fixed.)

---

## 7) Phase 6 — Train in Colab → Move to Production (Best quality)

### 7.1 Train in Colab
Run all notebook cells. Model saves to:
`runs/saved_model/`

Expected files:
- `config.json`
- `pytorch_model.bin`
- `tokenizer_config.json`
- `vocab.json`
- `merges.txt`
- `special_tokens_map.json`

### 7.2 Download from Colab (recommended ZIP)
Add last cell:
```python
import shutil
from google.colab import files
shutil.make_archive('codet5-trained', 'zip', 'runs/saved_model')
files.download('codet5-trained.zip')
```

### 7.3 Extract on Mac
```bash
cd /Users/priya/Data/Projects/TEXT2CODE
unzip ~/Downloads/codet5-trained.zip -d ./models/
ls -lh ./models/
```

### 7.4 Upload model to S3 (production-friendly)
```bash
./scripts/upload-model-to-s3.sh ./models/
aws s3 ls s3://text-to-code-models-priya/models/v1/
```

### 7.5 Restart EC2 container to pull new model
```bash
ssh -i ~/Downloads/text-to-code-key.pem ubuntu@3.239.116.3
docker restart text-to-code
docker logs -f text-to-code
exit
```

### 7.6 Test in production
```bash
curl -X POST http://3.239.116.3/generate   -H "Content-Type: application/json"   -d '{"prompt":"Write a function to compute factorial","max_length":160,"temperature":0.3}'
```

---

## 8) Model Versioning + Rollback (Highly recommended)

### 8.1 Recommended S3 structure
```
s3://text-to-code-models-priya/models/
  v1/   # production
  v2/   # staging/test
  archive/...
```

### 8.2 Deploy a new version (v2) without overwriting v1
Upload:
```bash
aws s3 sync ./models/v2/ s3://text-to-code-models-priya/models/v2/ --region us-east-1
```

Run EC2 container pointing to v2:
```bash
ssh -i ~/Downloads/text-to-code-key.pem ubuntu@3.239.116.3

docker stop text-to-code && docker rm text-to-code

docker run -d   --name text-to-code   -p 80:8000   --restart unless-stopped   -e AWS_DEFAULT_REGION=us-east-1   -e S3_BUCKET=text-to-code-models-priya   -e S3_PREFIX=models/v2   518627289438.dkr.ecr.us-east-1.amazonaws.com/text-to-code:latest

docker logs -f text-to-code
exit
```

Rollback = rerun with `S3_PREFIX=models/v1`.

---

## 9) Phase 4 — CI/CD (Optional but recommended)

### 9.1 Add GitHub Secrets
Repo → Settings → Secrets and variables → Actions:

- `AWS_ACCESS_KEY_ID`
- `AWS_SECRET_ACCESS_KEY`
- `AWS_ACCOUNT_ID`
- `AWS_REGION` (`us-east-1`)
- `EC2_HOST` (`3.239.116.3`)
- `EC2_USERNAME` (`ubuntu`)
- `EC2_SSH_KEY` (paste content of `.pem`)
- `S3_BUCKET` (`text-to-code-models-priya`)
- `S3_PREFIX` (`models/v1`)

### 9.2 Test pipeline
Make a small commit to `README.md` → push → GitHub Actions should:
1) run tests
2) build + push image to ECR
3) SSH to EC2 and redeploy container

---

## 10) Monitoring (Optional)

### 10.1 Metrics endpoint
Your API exposes Prometheus metrics:
```bash
curl http://3.239.116.3/metrics
```

### 10.2 CloudWatch alarms (suggested)
- CPU > 80%
- Memory > 85% (requires agent)
- Disk > 85%

---

## 11) Troubleshooting (Most common)

### A) “Model files not found”
Check:
```bash
ls -lh ./models/
# Must include config.json
```

### B) EC2 cannot download from S3
- Ensure EC2 role has `AmazonS3ReadOnlyAccess`
- Verify from EC2:
```bash
aws s3 ls s3://text-to-code-models-priya/models/v1/
```

### C) Out of memory on EC2
- Upgrade to `t3.small` (2GB) or higher
- Use smaller model variant if needed

### D) Docker image arch mismatch
Build for EC2:
```bash
docker build --platform linux/amd64 -t text-to-code:latest .
```

### E) Generation quality still poor
- Confirm tokenizer + prefix + model are correct (CodeT5 + RobertaTokenizer + `Generate Python:`)
- Fine-tune in Colab and deploy trained weights

---

## 12) Quick Commands (Copy/Paste)

### Local
```bash
source venv/bin/activate
uvicorn app.main:app --reload
pytest -q
docker build -t text-to-code:latest .
docker run --rm -p 8000:8000 text-to-code:latest
```

### AWS / ECR
```bash
aws sts get-caller-identity
aws ecr describe-repositories --region us-east-1
aws s3 ls s3://text-to-code-models-priya/models/v1/
```

### Production test
```bash
curl http://3.239.116.3/health
curl -X POST http://3.239.116.3/generate   -H "Content-Type: application/json"   -d '{"prompt":"Write a function to check prime","max_length":140,"temperature":0.3}'
```

---

## Appendix — “What should I do next?” (Practical priority order)

1) **Train model in Colab** (biggest quality jump)
2) **Upload to S3 and restart container**
3) **Add CI/CD secrets** to auto-deploy
4) **Add monitoring** (CloudWatch alarms)

