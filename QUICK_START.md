# SuperAgent v8 - Quick Start Guide

## ✅ API is Now Fixed and Ready to Use!

All dependency issues have been resolved. Follow these steps to get started.

---

## Installation

```bash
# Navigate to the project directory
cd /home/ubuntu/superagent-v8

# Install all dependencies (already done)
pip install -r requirements.txt
```

---

## Starting the API Server

### Option 1: Development Mode (with auto-reload)
```bash
uvicorn superagent.api:app --host 0.0.0.0 --port 8000 --reload
```

### Option 2: Production Mode
```bash
uvicorn superagent.api:app --host 0.0.0.0 --port 8000 --workers 4
```

### Option 3: Background Process
```bash
nohup uvicorn superagent.api:app --host 0.0.0.0 --port 8000 > api.log 2>&1 &
```

---

## Testing the API

### 1. Health Check (No Auth Required)
```bash
curl http://localhost:8000/health
```

**Expected Response:**
```json
{
  "status": "healthy",
  "active_agents": 0,
  "active_jobs": 0,
  "authentication": "enabled"
}
```

### 2. API Information (No Auth Required)
```bash
curl http://localhost:8000/api
```

### 3. View API Documentation
Open in your browser:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

---

## Using Protected Endpoints

All main endpoints require authentication via API key.

**Default Development API Key:** `dev-key-change-in-production`

⚠️ **Important:** Change this in production by setting the `SUPERAGENT_API_KEY` environment variable.

### Example: Generate Code

```bash
curl -X POST http://localhost:8000/generate \
  -H "Content-Type: application/json" \
  -H "X-API-Key: dev-key-change-in-production" \
  -d '{
    "instruction": "Create a Python function to reverse a string",
    "language": "python"
  }'
```

### Example: Get System Stats

```bash
curl -X GET http://localhost:8000/stats \
  -H "X-API-Key: dev-key-change-in-production"
```

### Example: Execute Instruction (Background Job)

```bash
# Submit job
curl -X POST http://localhost:8000/execute \
  -H "Content-Type: application/json" \
  -H "X-API-Key: dev-key-change-in-production" \
  -d '{
    "instruction": "Create a simple Flask REST API",
    "project_name": "my_api",
    "workspace": "./workspace"
  }'

# Response will include a job_id
# Use it to check status:
curl -X GET http://localhost:8000/jobs/{job_id} \
  -H "X-API-Key: dev-key-change-in-production"
```

---

## Environment Variables

### Required for Full Functionality

```bash
# SuperAgent API Key (for authentication)
export SUPERAGENT_API_KEY="your-secure-key-here"

# AI Provider Keys
export GROQ_API_KEY="your-groq-api-key"
export ANTHROPIC_API_KEY="your-anthropic-api-key"
export OPENAI_API_KEY="your-openai-api-key"
export GOOGLE_API_KEY="your-google-api-key"
```

### Optional Configuration

```bash
# Redis (for caching)
export REDIS_HOST="localhost"
export REDIS_PORT="6379"

# Database
export DATABASE_URL="postgresql://user:pass@localhost/dbname"
```

---

## Available Endpoints

### Public Endpoints (No Auth)
- `GET /` - Frontend UI
- `GET /api` - API information
- `GET /health` - Health check
- `GET /docs` - Swagger documentation
- `GET /redoc` - ReDoc documentation

### Protected Endpoints (Require API Key)
- `POST /generate` - Quick code generation
- `POST /execute` - Execute natural language instructions
- `GET /jobs/{job_id}` - Get job status
- `POST /debug` - Debug a project
- `POST /deploy` - Deploy a project
- `POST /test` - Run tests
- `GET /stats` - System statistics
- `POST /hallucination-fixer` - AI hallucination detection

---

## Running the Test Suite

```bash
python3 test_api_fixed.py
```

**Expected Output:**
```
============================================================
SuperAgent v8 API Test Suite
============================================================

--- Public Endpoints ---
✓ Health Check: Status 200
✓ API Info: Status 200
✓ Root Endpoint: Status 200

--- Protected Endpoints (No Auth - Should Fail) ---
✓ Generate Code (No Auth): Auth required (expected)
✓ Stats (No Auth): Auth required (expected)

--- Protected Endpoints (With Auth) ---
✓ Stats (With Auth): Status 200

============================================================
Results: 6/6 tests passed
✓ All tests passed!
============================================================
```

---

## Troubleshooting

### Server Won't Start

1. **Check dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Check for port conflicts:**
   ```bash
   lsof -i :8000
   # Kill any process using port 8000
   kill -9 <PID>
   ```

3. **Check logs:**
   ```bash
   tail -f api.log
   ```

### Authentication Errors

- Verify you're including the `X-API-Key` header
- Check the API key matches `SUPERAGENT_API_KEY` environment variable
- Default dev key: `dev-key-change-in-production`

### Import Errors

If you see `ModuleNotFoundError`, reinstall dependencies:
```bash
pip install -r requirements.txt --force-reinstall
```

---

## Next Steps

1. ✅ API is running
2. 🔑 Set up your API keys in environment variables
3. 📚 Explore the API documentation at `/docs`
4. 🚀 Start building with SuperAgent!

---

## Additional Resources

- **Full Fix Report:** `API_FIX_REPORT.md`
- **Issues Found:** `API_ISSUES_FOUND.md`
- **Main Documentation:** `README.md`

---

**Status:** ✅ All systems operational  
**Last Updated:** November 6, 2025
