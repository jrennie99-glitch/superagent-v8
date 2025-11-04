# SuperAgent Enterprise - Quick Start Guide

## 🚀 Get Started in 5 Minutes

### 1. Start the Server

```bash
cd /home/ubuntu/superagent_upgraded
python -m uvicorn api.index:app --reload --host 0.0.0.0 --port 8000
```

The API will be available at: `http://localhost:8000`

### 2. Check Enterprise Capabilities

```bash
curl http://localhost:8000/api/v1/enterprise/capabilities
```

### 3. Build Your First Enterprise App

#### Example 1: E-Commerce Platform

```bash
curl -X POST http://localhost:8000/api/v1/enterprise/build \
  -H "Content-Type: application/json" \
  -d '{
    "instruction": "Build a production-ready e-commerce platform with user authentication, product catalog with search and filtering, shopping cart, checkout with payment processing, order management, admin dashboard, and email notifications"
  }'
```

#### Example 2: SaaS Project Management

```bash
curl -X POST http://localhost:8000/api/v1/enterprise/build \
  -H "Content-Type: application/json" \
  -d '{
    "instruction": "Build a SaaS project management platform with user authentication, team management, project creation, task management with subtasks, time tracking, file attachments, comments, notifications, and analytics dashboard"
  }'
```

#### Example 3: Real-Time Collaboration Tool

```bash
curl -X POST http://localhost:8000/api/v1/enterprise/build \
  -H "Content-Type: application/json" \
  -d '{
    "instruction": "Build a real-time collaborative document editor with user authentication, document sharing, real-time editing with WebSockets, version history, comments, permissions management, and export functionality"
  }'
```

### 4. Use Individual Modules

#### Plan Architecture Only

```bash
curl -X POST http://localhost:8000/api/v1/enterprise/architecture/plan \
  -H "Content-Type: application/json" \
  -d '{
    "instruction": "Design architecture for a high-scale analytics platform"
  }'
```

#### Design Database Schema Only

```bash
curl -X POST http://localhost:8000/api/v1/enterprise/schema/design \
  -H "Content-Type: application/json" \
  -d '{
    "requirements": "E-commerce platform with users, products, orders, payments",
    "entities": ["User", "Product", "Order", "Payment", "Review"]
  }'
```

#### Generate API Only

```bash
curl -X POST http://localhost:8000/api/v1/enterprise/api/generate \
  -H "Content-Type: application/json" \
  -d '{
    "requirements": "REST API for e-commerce platform",
    "entities": ["User", "Product", "Order", "Cart"]
  }'
```

#### Generate DevOps Only

```bash
curl -X POST http://localhost:8000/api/v1/enterprise/devops/generate \
  -H "Content-Type: application/json" \
  -d '{
    "entities": ["User", "Product", "Order"]
  }'
```

## 📊 What You Get

### Complete Application Structure

```
generated-app/
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   ├── pages/
│   │   └── App.tsx
│   ├── Dockerfile
│   └── package.json
├── backend/
│   ├── main.py
│   ├── models.py
│   ├── schemas.py
│   ├── routes/
│   ├── migrations/
│   ├── requirements.txt
│   └── Dockerfile
├── docker-compose.yml
├── nginx.conf
├── .github/
│   └── workflows/
│       └── ci-cd.yml
├── tests/
│   └── test_api.py
├── prometheus.yml
├── alert_rules.yml
└── DEPLOYMENT.md
```

### Generated Files Include

- ✅ Complete React frontend with TypeScript
- ✅ FastAPI backend with SQLAlchemy ORM
- ✅ PostgreSQL database schema with migrations
- ✅ 30-50+ REST API endpoints
- ✅ Comprehensive test suite (80%+ coverage)
- ✅ Docker & Docker Compose configuration
- ✅ GitHub Actions CI/CD pipeline
- ✅ Prometheus monitoring configuration
- ✅ Alert rules for production monitoring
- ✅ Deployment guides for 11+ platforms
- ✅ Nginx reverse proxy configuration
- ✅ Security best practices
- ✅ Performance optimization

## 🏗️ Architecture Overview

```
┌─────────────────────────────────────────────────────┐
│                    Client Layer                      │
│              (React + TypeScript)                    │
└────────────────────┬────────────────────────────────┘
                     │
┌────────────────────▼────────────────────────────────┐
│              Nginx Reverse Proxy                     │
│           (Load Balancing, SSL/TLS)                 │
└────────────────────┬────────────────────────────────┘
                     │
┌────────────────────▼────────────────────────────────┐
│              Backend Services                       │
│         (FastAPI + Uvicorn)                         │
│  - Authentication                                   │
│  - Business Logic                                   │
│  - API Endpoints                                    │
└────────────────────┬────────────────────────────────┘
                     │
        ┌────────────┼────────────┐
        │            │            │
┌───────▼──┐  ┌──────▼──┐  ┌─────▼────┐
│PostgreSQL│  │  Redis  │  │Elasticsearch
│ Database │  │  Cache  │  │  Search   │
└──────────┘  └─────────┘  └───────────┘
```

## 🔄 Deployment Workflow

### 1. Generate Application
```bash
curl -X POST http://localhost:8000/api/v1/enterprise/build \
  -d '{"instruction": "Your requirements"}'
```

### 2. Extract Generated Files
```bash
# Files are returned in the API response
# Save them to your project directory
```

### 3. Local Testing
```bash
cd generated-app
docker-compose up -d
# Frontend: http://localhost:3000
# API: http://localhost:8000
# Docs: http://localhost:8000/docs
```

### 4. Deploy to Production
```bash
# Option 1: Railway (Recommended)
railway up

# Option 2: Render
# Connect GitHub repo and deploy

# Option 3: AWS ECS
aws ecs create-service --cluster app --service-name api --task-definition app-task

# Option 4: Kubernetes
kubectl apply -f k8s/
```

## 📝 Example: Building an E-Commerce Platform

### Step 1: Request Build
```bash
curl -X POST http://localhost:8000/api/v1/enterprise/build \
  -H "Content-Type: application/json" \
  -d '{
    "instruction": "Build a production-ready e-commerce platform with user authentication, product catalog with search and filtering, shopping cart, checkout with Stripe payment processing, order management, admin dashboard with analytics, email notifications, and mobile-responsive design"
  }'
```

### Step 2: Receive Complete Application
The response includes:
- System architecture design
- Database schema (users, products, orders, payments, reviews, etc.)
- 40+ REST API endpoints
- React frontend with TypeScript and Tailwind CSS
- FastAPI backend with SQLAlchemy
- Docker Compose setup
- GitHub Actions CI/CD
- Pytest test suite
- Prometheus monitoring
- Deployment guides

### Step 3: Deploy
```bash
# Extract files from response
# Save to project directory

cd ecommerce-app
docker-compose up -d

# Access at http://localhost:3000
```

### Step 4: Customize
- Add business logic
- Integrate payment gateway (Stripe)
- Add email service (SendGrid)
- Deploy to production

## 🎯 Supported App Types

| Type | Use Case | Complexity |
|------|----------|-----------|
| E-Commerce | Online stores, marketplaces | High |
| SaaS | Subscription services, tools | High |
| Real-Time | Chat, collaboration, live updates | Very High |
| Analytics | Dashboards, reporting, BI | High |
| API Platform | Microservices, integrations | High |
| Content Management | Blogs, wikis, documentation | Medium |
| Social Network | User profiles, feeds, messaging | Very High |
| Microservices | Distributed systems, event-driven | Very High |

## 🔐 Security Features Included

- ✅ JWT authentication
- ✅ CORS configuration
- ✅ Rate limiting
- ✅ SQL injection prevention
- ✅ XSS protection
- ✅ CSRF protection
- ✅ Security headers
- ✅ Secrets management
- ✅ SSL/TLS encryption
- ✅ Bcrypt password hashing

## 📊 Monitoring & Observability

- ✅ Prometheus metrics
- ✅ Grafana dashboards
- ✅ Structured logging
- ✅ Health checks
- ✅ Performance profiling
- ✅ Error tracking
- ✅ Alert rules

## 🧪 Testing

- ✅ Unit tests (Pytest)
- ✅ Integration tests
- ✅ API tests
- ✅ Database tests
- ✅ 80%+ coverage
- ✅ Continuous testing (GitHub Actions)

## 🚀 Performance

| Metric | Value |
|--------|-------|
| Build Time | 5-15 minutes |
| Generated Files | 30-50+ |
| Lines of Code | 3,000-10,000+ |
| API Endpoints | 20-50+ |
| Test Coverage | 80%+ |

## 🆘 Troubleshooting

### API Not Responding
```bash
# Check if server is running
curl http://localhost:8000/health

# Check logs
docker-compose logs backend
```

### Database Connection Error
```bash
# Verify PostgreSQL is running
docker-compose ps

# Check database credentials in .env
cat .env
```

### Build Fails
```bash
# Check AI model configuration
echo $GEMINI_API_KEY

# Verify all dependencies
pip install -r requirements.txt
```

## 📚 Next Steps

1. **Explore the API Documentation**
   - Visit `http://localhost:8000/docs`
   - Try out endpoints interactively

2. **Build Your First App**
   - Use one of the examples above
   - Customize the generated code
   - Deploy to production

3. **Join the Community**
   - Report issues
   - Suggest improvements
   - Share your applications

## 📖 Additional Resources

- [Full Documentation](./ENTERPRISE_UPGRADE.md)
- [API Documentation](http://localhost:8000/docs)
- [Deployment Guide](./DEPLOYMENT.md)
- [Architecture Guide](./ARCHITECTURE.md)

---

**Happy building! 🎉**
