# 🚀 SuperAgent - Deployment Guide

## **How to Deploy SuperAgent**

Complete guide for deploying SuperAgent locally, on servers, or to the cloud.

---

## 📋 **Table of Contents**

1. [Local Installation](#local-installation)
2. [Server Deployment](#server-deployment)
3. [Docker Deployment](#docker-deployment)
4. [Cloud Deployment](#cloud-deployment)
5. [API Server Deployment](#api-server-deployment)
6. [Production Configuration](#production-configuration)
7. [Troubleshooting](#troubleshooting)

---

## 1️⃣ **Local Installation** (Easiest)

### **Prerequisites:**
- Python 3.10 or higher
- pip package manager
- Anthropic API key

### **Step-by-Step:**

```bash
# 1. Navigate to project
cd "/Users/armotorz/cursor project"

# 2. Create virtual environment (recommended)
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Install SuperAgent
pip install -e .

# 5. Set API key
export ANTHROPIC_API_KEY="sk-ant-your-key-here"

# Or create .env file:
echo "ANTHROPIC_API_KEY=sk-ant-your-key-here" > .env

# 6. Verify installation
python3 verify_claude_4_5.py
superagent models current

# 7. Test it!
superagent create "Test project"
```

### **Optional: Voice Features**
```bash
# Install voice dependencies
pip install SpeechRecognition pyaudio pyttsx3

# macOS:
brew install portaudio

# Linux (Ubuntu/Debian):
sudo apt-get install portaudio19-dev python3-pyaudio

# Test voice
superagent voice test
```

---

## 2️⃣ **Server Deployment** (VPS/Dedicated Server)

### **For Ubuntu/Debian Server:**

```bash
# 1. Update system
sudo apt update && sudo apt upgrade -y

# 2. Install Python 3.10+
sudo apt install python3.10 python3-pip python3-venv -y

# 3. Install system dependencies
sudo apt install git build-essential -y

# 4. Clone/copy project
git clone <your-repo> superagent
# OR
scp -r "/Users/armotorz/cursor project" user@server:/opt/superagent

# 5. Setup project
cd /opt/superagent
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
pip install -e .

# 6. Configure environment
sudo nano /etc/environment
# Add: ANTHROPIC_API_KEY=your-key-here

# 7. Create systemd service (for API server)
sudo nano /etc/systemd/system/superagent.service
```

**Service file content:**
```ini
[Unit]
Description=SuperAgent API Server
After=network.target

[Service]
Type=simple
User=www-data
WorkingDirectory=/opt/superagent
Environment="PATH=/opt/superagent/venv/bin"
Environment="ANTHROPIC_API_KEY=your-key-here"
ExecStart=/opt/superagent/venv/bin/python -m uvicorn superagent.api:app --host 0.0.0.0 --port 8000
Restart=always

[Install]
WantedBy=multi-user.target
```

```bash
# 8. Start service
sudo systemctl daemon-reload
sudo systemctl enable superagent
sudo systemctl start superagent
sudo systemctl status superagent

# 9. Check logs
sudo journalctl -u superagent -f
```

---

## 3️⃣ **Docker Deployment** (Recommended)

### **Create Dockerfile:**

```bash
# Create Dockerfile
cat > Dockerfile << 'EOF'
FROM python:3.10-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    git \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application
COPY . .

# Install SuperAgent
RUN pip install -e .

# Expose port for API
EXPOSE 8000

# Set environment variables
ENV PYTHONUNBUFFERED=1

# Default command (can be overridden)
CMD ["uvicorn", "superagent.api:app", "--host", "0.0.0.0", "--port", "8000"]
EOF
```

### **Create docker-compose.yml:**

```bash
cat > docker-compose.yml << 'EOF'
version: '3.8'

services:
  superagent:
    build: .
    ports:
      - "8000:8000"
    environment:
      - ANTHROPIC_API_KEY=${ANTHROPIC_API_KEY}
    volumes:
      - ./data:/app/data
      - ./logs:/app/logs
    restart: unless-stopped
    
  # Optional: Redis for caching
  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
    volumes:
      - redis-data:/data
    restart: unless-stopped

volumes:
  redis-data:
EOF
```

### **Deploy with Docker:**

```bash
# 1. Build image
docker build -t superagent:latest .

# 2. Run container
docker run -d \
  --name superagent \
  -p 8000:8000 \
  -e ANTHROPIC_API_KEY="your-key" \
  superagent:latest

# OR use docker-compose
docker-compose up -d

# 3. Check logs
docker logs -f superagent

# 4. Test API
curl http://localhost:8000/health
```

---

## 4️⃣ **Cloud Deployment**

### **Option A: AWS EC2**

```bash
# 1. Launch EC2 instance (Ubuntu 22.04 LTS)
# 2. SSH into instance
ssh -i your-key.pem ubuntu@your-ec2-ip

# 3. Follow "Server Deployment" steps above

# 4. Configure security group
# - Allow port 8000 (API)
# - Allow port 22 (SSH)
# - Allow port 443 (HTTPS)

# 5. Optional: Setup Nginx reverse proxy
sudo apt install nginx -y
sudo nano /etc/nginx/sites-available/superagent
```

**Nginx config:**
```nginx
server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    }
}
```

```bash
sudo ln -s /etc/nginx/sites-available/superagent /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx

# 6. Setup SSL with Let's Encrypt
sudo apt install certbot python3-certbot-nginx -y
sudo certbot --nginx -d your-domain.com
```

### **Option B: AWS Lambda (Serverless)**

```python
# Create lambda_handler.py
import json
from superagent import SuperAgent
import asyncio

def lambda_handler(event, context):
    """AWS Lambda handler for SuperAgent."""
    
    # Parse request
    body = json.loads(event.get('body', '{}'))
    instruction = body.get('instruction', '')
    
    # Execute with SuperAgent
    async def run():
        async with SuperAgent() as agent:
            result = await agent.execute_instruction(instruction)
            return result
    
    result = asyncio.run(run())
    
    return {
        'statusCode': 200,
        'body': json.dumps(result),
        'headers': {
            'Content-Type': 'application/json'
        }
    }
```

**Deploy to Lambda:**
```bash
# 1. Create deployment package
pip install -r requirements.txt -t package/
cp -r superagent package/
cp lambda_handler.py package/

# 2. Create zip
cd package
zip -r ../superagent-lambda.zip .

# 3. Upload to Lambda
aws lambda create-function \
  --function-name superagent \
  --runtime python3.10 \
  --role arn:aws:iam::YOUR_ACCOUNT:role/lambda-role \
  --handler lambda_handler.lambda_handler \
  --zip-file fileb://../superagent-lambda.zip \
  --timeout 900 \
  --memory-size 2048 \
  --environment Variables={ANTHROPIC_API_KEY=your-key}
```

### **Option C: Google Cloud Run**

```bash
# 1. Create Dockerfile (use the one from Docker section)

# 2. Build and push to GCR
gcloud builds submit --tag gcr.io/YOUR_PROJECT/superagent

# 3. Deploy to Cloud Run
gcloud run deploy superagent \
  --image gcr.io/YOUR_PROJECT/superagent \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated \
  --set-env-vars ANTHROPIC_API_KEY=your-key \
  --memory 2Gi \
  --timeout 900
```

### **Option D: Heroku**

```bash
# 1. Create Procfile
echo "web: uvicorn superagent.api:app --host 0.0.0.0 --port \$PORT" > Procfile

# 2. Create runtime.txt
echo "python-3.10.12" > runtime.txt

# 3. Initialize git (if not already)
git init
git add .
git commit -m "Initial commit"

# 4. Create Heroku app
heroku create your-app-name

# 5. Set environment variables
heroku config:set ANTHROPIC_API_KEY=your-key

# 6. Deploy
git push heroku main

# 7. Scale dynos
heroku ps:scale web=1

# 8. Check logs
heroku logs --tail
```

### **Option E: DigitalOcean App Platform**

```yaml
# Create .do/app.yaml
name: superagent
services:
  - name: api
    github:
      repo: your-username/superagent
      branch: main
    run_command: uvicorn superagent.api:app --host 0.0.0.0 --port 8080
    environment_slug: python
    instance_count: 1
    instance_size_slug: basic-xs
    envs:
      - key: ANTHROPIC_API_KEY
        value: ${ANTHROPIC_API_KEY}
        type: SECRET
    http_port: 8080
```

---

## 5️⃣ **API Server Deployment**

### **Start API Server:**

```bash
# Development
uvicorn superagent.api:app --reload --host 0.0.0.0 --port 8000

# Production
uvicorn superagent.api:app \
  --host 0.0.0.0 \
  --port 8000 \
  --workers 4 \
  --log-level info
```

### **With Gunicorn (Production):**

```bash
# Install gunicorn
pip install gunicorn

# Run with multiple workers
gunicorn superagent.api:app \
  --workers 4 \
  --worker-class uvicorn.workers.UvicornWorker \
  --bind 0.0.0.0:8000 \
  --timeout 300 \
  --access-logfile - \
  --error-logfile -
```

### **Test API:**

```bash
# Health check
curl http://localhost:8000/health

# Create project
curl -X POST http://localhost:8000/api/v1/execute \
  -H "Content-Type: application/json" \
  -d '{"instruction": "Create a Python calculator"}'

# List models
curl http://localhost:8000/api/v1/models
```

---

## 6️⃣ **Production Configuration**

### **Optimize config.yaml:**

```yaml
# Production settings
performance:
  async_enabled: true
  parallel_tasks: true
  max_workers: 8
  cache_ttl: 3600
  use_gpu: false

models:
  primary:
    provider: "anthropic"
    name: "claude-sonnet-4-5-20250929"
    temperature: 0.7
    max_tokens: 8000

# Logging
logging:
  level: "INFO"
  file: "/var/log/superagent/app.log"
  max_size: "100MB"
  backup_count: 5

# Security
security:
  rate_limit: 100  # requests per minute
  max_request_size: "10MB"
  allowed_origins: ["https://yourdomain.com"]
```

### **Environment Variables:**

```bash
# Required
export ANTHROPIC_API_KEY="your-key"

# Optional
export REDIS_URL="redis://localhost:6379"
export LOG_LEVEL="INFO"
export MAX_WORKERS=4
export CACHE_TTL=3600

# For production
export ENVIRONMENT="production"
export DEBUG=false
```

### **Setup Logging:**

```python
# In production, configure proper logging
import logging
from logging.handlers import RotatingFileHandler

handler = RotatingFileHandler(
    '/var/log/superagent/app.log',
    maxBytes=100*1024*1024,  # 100MB
    backupCount=5
)
handler.setFormatter(logging.Formatter(
    '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
))
logging.getLogger().addHandler(handler)
```

---

## 7️⃣ **Monitoring & Maintenance**

### **Health Checks:**

```bash
# Check if API is running
curl http://localhost:8000/health

# Check model status
curl http://localhost:8000/api/v1/models/current

# Check system status
curl http://localhost:8000/api/v1/status
```

### **Monitoring Tools:**

```bash
# Install monitoring
pip install prometheus-client

# Add to API
from prometheus_client import make_asgi_app
metrics_app = make_asgi_app()
app.mount("/metrics", metrics_app)
```

### **Log Rotation:**

```bash
# Setup logrotate
sudo nano /etc/logrotate.d/superagent
```

```
/var/log/superagent/*.log {
    daily
    rotate 7
    compress
    delaycompress
    notifempty
    create 0640 www-data www-data
    sharedscripts
    postrotate
        systemctl reload superagent > /dev/null 2>&1 || true
    endscript
}
```

---

## 8️⃣ **Troubleshooting**

### **Common Issues:**

**Issue: "Module not found"**
```bash
# Solution: Reinstall
pip install -e .
```

**Issue: "API key not set"**
```bash
# Solution: Set environment variable
export ANTHROPIC_API_KEY="your-key"
```

**Issue: "Port already in use"**
```bash
# Solution: Change port
uvicorn superagent.api:app --port 8001
```

**Issue: "Memory errors"**
```bash
# Solution: Increase memory limit
# In docker-compose.yml:
deploy:
  resources:
    limits:
      memory: 4G
```

---

## 9️⃣ **Quick Deployment Checklist**

### **Pre-Deployment:**
- [ ] Python 3.10+ installed
- [ ] All dependencies installed
- [ ] API key configured
- [ ] Configuration files reviewed
- [ ] Tests passing
- [ ] Security configured

### **Deployment:**
- [ ] Code deployed to server
- [ ] Virtual environment created
- [ ] Dependencies installed
- [ ] Service/container started
- [ ] Health checks passing
- [ ] Logs verified

### **Post-Deployment:**
- [ ] API accessible
- [ ] SSL configured (if public)
- [ ] Monitoring setup
- [ ] Backups configured
- [ ] Documentation updated

---

## 🎯 **Recommended Deployment**

### **For Development:**
```bash
# Local installation
pip install -e .
superagent create "test"
```

### **For Production (Small):**
```bash
# DigitalOcean Droplet or Heroku
# Docker + Docker Compose
# 1-2 workers
```

### **For Production (Medium):**
```bash
# AWS EC2 or GCP Compute Engine
# Docker + Kubernetes
# 4-8 workers
# Redis caching
# Nginx reverse proxy
```

### **For Production (Large):**
```bash
# AWS ECS/EKS or GCP GKE
# Auto-scaling
# Load balancer
# Redis cluster
# CloudWatch/Stackdriver monitoring
```

---

## 📚 **Additional Resources**

- **Installation:** See `INSTALLATION_AND_TESTING.md`
- **API Docs:** See API section in `README.md`
- **Configuration:** See `config.yaml`
- **Examples:** See `examples/deployment_example.py`

---

## 🚀 **Quick Start Commands**

### **Local:**
```bash
pip install -r requirements.txt && pip install -e .
export ANTHROPIC_API_KEY="your-key"
superagent create "test"
```

### **Docker:**
```bash
docker-compose up -d
curl http://localhost:8000/health
```

### **Production:**
```bash
gunicorn superagent.api:app \
  --workers 4 \
  --worker-class uvicorn.workers.UvicornWorker \
  --bind 0.0.0.0:8000
```

---

**SuperAgent is now deployed and ready to use!** 🎉

For questions or issues, check the troubleshooting section or review the logs.





