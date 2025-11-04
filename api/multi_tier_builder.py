"""
Multi-Tier Application Builder
Builds complete full-stack applications with frontend, backend, and database
"""
import os
import asyncio
from typing import Dict, List, Any, Optional
from pathlib import Path
import google.generativeai as genai

from .architecture_planner import architecture_planner
from .schema_designer import schema_designer
from .api_generator import api_generator


class MultiTierBuilder:
    """Builds complete multi-tier enterprise applications"""
    
    def __init__(self):
        api_key = os.getenv("GEMINI_API_KEY")
        if api_key:
            genai.configure(api_key=api_key)
            self.model = genai.GenerativeModel('gemini-2.0-flash')
        else:
            self.model = None
    
    async def generate_frontend_code(self, app_type: str, features: List[str]) -> str:
        """Generate React frontend code"""
        
        if not self.model:
            return "// Frontend generation requires AI model"
        
        features_str = ", ".join(features)
        
        prompt = f"""Generate a production-ready React application for:

APP TYPE: {app_type}
FEATURES: {features_str}

Generate complete React code with:
- TypeScript
- Tailwind CSS for styling
- React Router for navigation
- State management (Zustand or Redux)
- API integration
- Error handling
- Loading states

Return complete, runnable React code."""
        
        try:
            response = self.model.generate_content(prompt)
            return response.text.strip()
        except Exception as e:
            return f"// Error generating frontend: {str(e)}"
    
    async def generate_backend_code(self, app_type: str, features: List[str], entities: List[str]) -> str:
        """Generate FastAPI backend code"""
        
        if not self.model:
            return "# Backend generation requires AI model"
        
        features_str = ", ".join(features)
        entities_str = ", ".join(entities)
        
        prompt = f"""Generate a production-ready FastAPI backend for:

APP TYPE: {app_type}
FEATURES: {features_str}
ENTITIES: {entities_str}

Generate complete FastAPI code with:
- Proper project structure
- Database models (SQLAlchemy)
- API routes with CRUD operations
- Authentication (JWT)
- Error handling
- Logging
- Database migrations
- Input validation (Pydantic)
- CORS configuration

Return complete, runnable FastAPI code."""
        
        try:
            response = self.model.generate_content(prompt)
            return response.text.strip()
        except Exception as e:
            return f"# Error generating backend: {str(e)}"
    
    async def generate_docker_compose(self, services: List[str]) -> str:
        """Generate Docker Compose configuration"""
        
        compose = """version: '3.8'

services:
  # PostgreSQL Database
  postgres:
    image: postgres:15-alpine
    container_name: app_postgres
    environment:
      POSTGRES_DB: ${DB_NAME:-app_db}
      POSTGRES_USER: ${DB_USER:-postgres}
      POSTGRES_PASSWORD: ${DB_PASSWORD:-postgres}
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U postgres"]
      interval: 10s
      timeout: 5s
      retries: 5

  # Redis Cache
  redis:
    image: redis:7-alpine
    container_name: app_redis
    ports:
      - "6379:6379"
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 10s
      timeout: 5s
      retries: 5

  # FastAPI Backend
  backend:
    build:
      context: .
      dockerfile: Dockerfile.backend
    container_name: app_backend
    environment:
      DATABASE_URL: postgresql://${DB_USER:-postgres}:${DB_PASSWORD:-postgres}@postgres:5432/${DB_NAME:-app_db}
      REDIS_URL: redis://redis:6379
      JWT_SECRET: ${JWT_SECRET:-your-secret-key}
    ports:
      - "8000:8000"
    depends_on:
      postgres:
        condition: service_healthy
      redis:
        condition: service_healthy
    volumes:
      - ./backend:/app
    command: uvicorn main:app --host 0.0.0.0 --port 8000 --reload

  # React Frontend
  frontend:
    build:
      context: ./frontend
      dockerfile: Dockerfile
    container_name: app_frontend
    ports:
      - "3000:3000"
    environment:
      REACT_APP_API_URL: http://backend:8000
    depends_on:
      - backend
    volumes:
      - ./frontend:/app
      - /app/node_modules

  # Nginx Reverse Proxy
  nginx:
    image: nginx:alpine
    container_name: app_nginx
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf:ro
    depends_on:
      - backend
      - frontend

volumes:
  postgres_data:
  redis_data:

networks:
  default:
    name: app_network
"""
        
        return compose
    
    async def generate_dockerfile_backend(self) -> str:
        """Generate Dockerfile for FastAPI backend"""
        
        dockerfile = """FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \\
    gcc \\
    postgresql-client \\
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create non-root user
RUN useradd -m -u 1000 appuser && chown -R appuser:appuser /app
USER appuser

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \\
    CMD python -c "import requests; requests.get('http://localhost:8000/health')"

# Run application
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
"""
        
        return dockerfile
    
    async def generate_dockerfile_frontend(self) -> str:
        """Generate Dockerfile for React frontend"""
        
        dockerfile = """# Build stage
FROM node:18-alpine AS builder

WORKDIR /app

COPY package*.json ./

RUN npm ci

COPY . .

RUN npm run build

# Production stage
FROM node:18-alpine

WORKDIR /app

RUN npm install -g serve

COPY --from=builder /app/build ./build

EXPOSE 3000

CMD ["serve", "-s", "build", "-l", "3000"]
"""
        
        return dockerfile
    
    async def generate_github_actions_ci_cd(self) -> str:
        """Generate GitHub Actions CI/CD workflow"""
        
        workflow = """name: CI/CD Pipeline

on:
  push:
    branches: [main, develop]
  pull_request:
    branches: [main, develop]

jobs:
  test:
    runs-on: ubuntu-latest
    
    services:
      postgres:
        image: postgres:15-alpine
        env:
          POSTGRES_PASSWORD: postgres
        options: >-
          --health-cmd pg_isready
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5
        ports:
          - 5432:5432
    
    steps:
      - uses: actions/checkout@v3
      
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      
      - name: Install dependencies
        run: |
          python -m pip install --upgrade pip
          pip install -r requirements.txt
      
      - name: Run tests
        run: pytest tests/ --cov=api --cov-report=xml
      
      - name: Upload coverage
        uses: codecov/codecov-action@v3
        with:
          files: ./coverage.xml

  build:
    needs: test
    runs-on: ubuntu-latest
    
    steps:
      - uses: actions/checkout@v3
      
      - name: Set up Docker Buildx
        uses: docker/setup-buildx-action@v2
      
      - name: Build Docker images
        run: docker-compose build
      
      - name: Run containers
        run: docker-compose up -d
      
      - name: Health check
        run: sleep 10 && curl http://localhost:8000/health

  deploy:
    needs: build
    runs-on: ubuntu-latest
    if: github.ref == 'refs/heads/main' && github.event_name == 'push'
    
    steps:
      - uses: actions/checkout@v3
      
      - name: Deploy to production
        run: |
          echo "Deploying to production..."
          # Add your deployment commands here
"""
        
        return workflow
    
    async def build_complete_application(self, requirements: str) -> Dict[str, Any]:
        """Build complete multi-tier application"""
        
        try:
            # Step 1: Plan architecture
            arch_result = await architecture_planner.plan_complete_architecture(requirements)
            if "error" in arch_result:
                return arch_result
            
            architecture = arch_result.get("architecture", {})
            analysis = arch_result.get("analysis", {})
            
            # Extract entities from analysis
            entities = analysis.get("data_requirements", {}).get("primary_data", [])
            features = analysis.get("key_features", [])
            app_type = analysis.get("app_type", "general")
            
            # Step 2: Design database schema
            schema_result = await schema_designer.design_complete_schema(requirements, entities)
            if "error" in schema_result:
                return schema_result
            
            # Step 3: Generate API
            api_result = await api_generator.generate_complete_api(requirements, entities)
            if "error" in api_result:
                return api_result
            
            # Step 4: Generate frontend code
            frontend_code = await self.generate_frontend_code(app_type, features)
            
            # Step 5: Generate backend code
            backend_code = await self.generate_backend_code(app_type, features, entities)
            
            # Step 6: Generate Docker configuration
            docker_compose = await self.generate_docker_compose(["postgres", "redis", "backend", "frontend"])
            dockerfile_backend = await self.generate_dockerfile_backend()
            dockerfile_frontend = await self.generate_dockerfile_frontend()
            
            # Step 7: Generate CI/CD workflow
            github_actions = await self.generate_github_actions_ci_cd()
            
            return {
                "success": True,
                "app_type": app_type,
                "architecture": architecture,
                "schema": schema_result.get("schema"),
                "api_spec": api_result.get("spec"),
                "files_to_create": {
                    "backend": {
                        "main.py": backend_code,
                        "requirements.txt": "fastapi==0.104.1\\nuvicorn==0.24.0\\nsqlalchemy==2.0.23\\nalembic==1.12.1\\npydantic==2.5.0\\npython-dotenv==1.0.0\\npsycopg2-binary==2.9.9\\nredis==5.0.1\\npyjwt==2.8.1",
                        "Dockerfile": dockerfile_backend,
                        "models.py": schema_result.get("sqlalchemy_models"),
                        "migrations/versions/001_initial.py": schema_result.get("alembic_migration")
                    },
                    "frontend": {
                        "App.tsx": frontend_code,
                        "Dockerfile": dockerfile_frontend,
                        "package.json": '{"name": "app", "version": "1.0.0", "dependencies": {"react": "^18.0.0", "react-router-dom": "^6.0.0", "zustand": "^4.0.0"}}'
                    },
                    "infrastructure": {
                        "docker-compose.yml": docker_compose,
                        ".github/workflows/ci-cd.yml": github_actions,
                        "nginx.conf": self._generate_nginx_config()
                    }
                },
                "deployment_steps": [
                    "1. Clone repository",
                    "2. Create .env file with database credentials",
                    "3. Run: docker-compose up",
                    "4. Access frontend at http://localhost:3000",
                    "5. API available at http://localhost:8000",
                    "6. Push to GitHub to trigger CI/CD"
                ]
            }
        
        except Exception as e:
            return {"error": str(e), "success": False}
    
    def _generate_nginx_config(self) -> str:
        """Generate Nginx configuration"""
        
        return """user nginx;
worker_processes auto;
error_log /var/log/nginx/error.log warn;
pid /var/run/nginx.pid;

events {
    worker_connections 1024;
}

http {
    include /etc/nginx/mime.types;
    default_type application/octet-stream;

    log_format main '$remote_addr - $remote_user [$time_local] "$request" '
                    '$status $body_bytes_sent "$http_referer" '
                    '"$http_user_agent" "$http_x_forwarded_for"';

    access_log /var/log/nginx/access.log main;

    sendfile on;
    tcp_nopush on;
    tcp_nodelay on;
    keepalive_timeout 65;
    types_hash_max_size 2048;
    client_max_body_size 20M;

    # Gzip compression
    gzip on;
    gzip_vary on;
    gzip_proxied any;
    gzip_comp_level 6;
    gzip_types text/plain text/css text/xml text/javascript application/json application/javascript application/xml+rss;

    # Rate limiting
    limit_req_zone $binary_remote_addr zone=api_limit:10m rate=10r/s;
    limit_req_zone $binary_remote_addr zone=general_limit:10m rate=30r/s;

    # Upstream backends
    upstream backend {
        server backend:8000;
    }

    upstream frontend {
        server frontend:3000;
    }

    # HTTP redirect to HTTPS
    server {
        listen 80;
        server_name _;
        return 301 https://$host$request_uri;
    }

    # HTTPS server
    server {
        listen 443 ssl http2;
        server_name _;

        # SSL certificates (replace with your own)
        ssl_certificate /etc/nginx/ssl/cert.pem;
        ssl_certificate_key /etc/nginx/ssl/key.pem;

        # Security headers
        add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;
        add_header X-Content-Type-Options "nosniff" always;
        add_header X-Frame-Options "SAMEORIGIN" always;
        add_header X-XSS-Protection "1; mode=block" always;

        # API routes
        location /api/ {
            limit_req zone=api_limit burst=20 nodelay;
            proxy_pass http://backend;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
        }

        # Frontend
        location / {
            limit_req zone=general_limit burst=50 nodelay;
            proxy_pass http://frontend;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        }

        # Health check endpoint
        location /health {
            access_log off;
            return 200 "healthy\\n";
            add_header Content-Type text/plain;
        }
    }
}
"""


# Global instance
multi_tier_builder = MultiTierBuilder()
