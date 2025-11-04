# 🚀 SuperAgent - Manual Deployment Instructions

## **Deploy SuperAgent Right Now**

Follow these simple steps to deploy SuperAgent on your Mac.

---

## ⚡ **Quick Start (5 minutes)**

### **Step 1: Install Dependencies**

Open Terminal and run:

```bash
cd "/Users/armotorz/cursor project"

# Install Python packages
pip3 install anthropic langchain openai fastapi uvicorn redis
pip3 install structlog pyyaml pydantic click rich
pip3 install pytest pytest-asyncio radon pylint mypy black bandit
```

### **Step 2: Install SuperAgent**

```bash
pip3 install -e .
```

### **Step 3: Set Your API Key**

Get your Anthropic API key from: https://console.anthropic.com/

Then set it:

```bash
export ANTHROPIC_API_KEY="sk-ant-your-api-key-here"
```

Or create a `.env` file:

```bash
echo "ANTHROPIC_API_KEY=sk-ant-your-key-here" > .env
```

### **Step 4: Verify Installation**

```bash
python3 verify_claude_4_5.py
```

You should see all ✅ checks pass.

### **Step 5: Use SuperAgent!**

```bash
# Check current model
superagent models current

# Create a project
superagent create "Build a Python calculator"

# Use voice interface
superagent voice talk
```

---

## 🔧 **If You Have SSL Certificate Issues**

If you see SSL errors when installing, try:

```bash
# Option 1: Update certificates
pip3 install --upgrade certifi

# Option 2: Use HTTP instead of HTTPS (not recommended for production)
pip3 install --trusted-host pypi.org --trusted-host files.pythonhosted.org anthropic

# Option 3: Fix macOS certificates
/Applications/Python\ 3.13/Install\ Certificates.command
```

---

## 🐳 **Alternative: Use Docker**

If you prefer Docker:

```bash
# Create Dockerfile
cat > Dockerfile << 'EOF'
FROM python:3.10-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
RUN pip install -e .
EXPOSE 8000
CMD ["uvicorn", "superagent.api:app", "--host", "0.0.0.0", "--port", "8000"]
EOF

# Build and run
docker build -t superagent .
docker run -d -p 8000:8000 -e ANTHROPIC_API_KEY="your-key" superagent

# Test
curl http://localhost:8000/health
```

---

## 🚀 **Start API Server**

To run SuperAgent as an API server:

```bash
# Development mode
uvicorn superagent.api:app --reload --host 0.0.0.0 --port 8000

# Production mode
uvicorn superagent.api:app --host 0.0.0.0 --port 8000 --workers 4
```

Test the API:

```bash
# Health check
curl http://localhost:8000/health

# List models
curl http://localhost:8000/api/v1/models

# Create project
curl -X POST http://localhost:8000/api/v1/execute \
  -H "Content-Type: application/json" \
  -d '{"instruction": "Create a Python calculator"}'
```

---

## ✅ **Verify Everything Works**

Run these commands to verify:

```bash
# 1. Check Python
python3 --version  # Should be 3.10+

# 2. Check SuperAgent
superagent --version

# 3. Check model
superagent models current

# 4. Test creation
superagent create "test project"
```

---

## 🎯 **What You Can Do Now**

### **CLI Usage:**
```bash
# Create projects
superagent create "Build a web scraper"

# Debug code
superagent debug ./mycode.py --fix

# Review code
superagent review ./mycode.py

# Generate docs
superagent document ./project

# Use voice
superagent voice talk
```

### **Python API:**
```python
import asyncio
from superagent import SuperAgent

async def main():
    async with SuperAgent() as agent:
        result = await agent.execute_instruction(
            "Create a REST API with authentication"
        )
        print(result)

asyncio.run(main())
```

---

## 📚 **Documentation**

- **Quick Deploy:** `QUICK_DEPLOY.md`
- **Full Deployment:** `DEPLOYMENT_GUIDE.md`
- **Getting Started:** `START_HERE.md`
- **Claude 4.5 Guide:** `CLAUDE_4_5_QUICK_START.md`

---

## 🆘 **Troubleshooting**

### **Issue: "command not found: superagent"**

Solution:
```bash
pip3 install -e .
```

### **Issue: "No module named 'anthropic'"**

Solution:
```bash
pip3 install anthropic
```

### **Issue: "API key not set"**

Solution:
```bash
export ANTHROPIC_API_KEY="your-key"
```

### **Issue: SSL Certificate Error**

Solution:
```bash
/Applications/Python\ 3.13/Install\ Certificates.command
```

---

## 🎉 **You're Ready!**

SuperAgent is now deployed and ready to use with **Claude 4.5 Sonnet**!

### **Quick Commands:**
```bash
superagent models current    # Check model
superagent create "test"     # Create project
superagent voice talk        # Voice mode
```

---

**SuperAgent: Deployed and Ready!** ✅





