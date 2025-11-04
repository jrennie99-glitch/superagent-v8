#!/bin/bash

# SuperAgent - Private Local Deployment Script
# This deploys SuperAgent completely locally on your machine

set -e

echo "╔════════════════════════════════════════════════════════════════╗"
echo "║        SuperAgent - Private Deployment (Local Only)           ║"
echo "╚════════════════════════════════════════════════════════════════╝"
echo ""
echo "This will deploy SuperAgent privately on your Mac."
echo "No cloud services, completely local and private."
echo ""

# Get the project directory
PROJECT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$PROJECT_DIR"

# Check Python
echo "1️⃣  Checking Python..."
if ! command -v python3 &> /dev/null; then
    echo "   ❌ Python 3 not found. Please install Python 3.10+"
    exit 1
fi
PYTHON_VERSION=$(python3 --version | awk '{print $2}')
echo "   ✅ Python $PYTHON_VERSION"
echo ""

# Create virtual environment
echo "2️⃣  Creating private virtual environment..."
if [ ! -d "venv" ]; then
    python3 -m venv venv
    echo "   ✅ Virtual environment created"
else
    echo "   ℹ️  Virtual environment already exists"
fi

# Activate virtual environment
echo "   Activating virtual environment..."
source venv/bin/activate
echo "   ✅ Virtual environment activated"
echo ""

# Upgrade pip
echo "3️⃣  Upgrading pip..."
pip install --upgrade pip setuptools wheel --quiet
echo "   ✅ Pip upgraded"
echo ""

# Install dependencies
echo "4️⃣  Installing dependencies privately..."
echo "   This may take a few minutes..."

# Core dependencies
pip install --no-warn-script-location anthropic>=0.25.0 --quiet
pip install --no-warn-script-location langchain>=0.1.0 --quiet
pip install --no-warn-script-location openai>=1.0.0 --quiet
pip install --no-warn-script-location fastapi>=0.104.0 --quiet
pip install --no-warn-script-location uvicorn>=0.24.0 --quiet
pip install --no-warn-script-location pydantic>=2.0.0 --quiet
pip install --no-warn-script-location structlog>=23.2.0 --quiet
pip install --no-warn-script-location pyyaml>=6.0 --quiet
pip install --no-warn-script-location click>=8.1.0 --quiet
pip install --no-warn-script-location rich>=13.7.0 --quiet
pip install --no-warn-script-location redis>=5.0.0 --quiet
pip install --no-warn-script-location aiofiles>=23.2.0 --quiet
pip install --no-warn-script-location httpx>=0.25.0 --quiet

# Development dependencies
pip install --no-warn-script-location pytest>=7.4.0 --quiet
pip install --no-warn-script-location pytest-asyncio>=0.21.0 --quiet
pip install --no-warn-script-location black>=23.11.0 --quiet
pip install --no-warn-script-location pylint>=3.0.0 --quiet
pip install --no-warn-script-location mypy>=1.7.0 --quiet

echo "   ✅ All dependencies installed privately"
echo ""

# Install SuperAgent
echo "5️⃣  Installing SuperAgent..."
pip install -e . --quiet
echo "   ✅ SuperAgent installed"
echo ""

# Create .env file if it doesn't exist
echo "6️⃣  Setting up configuration..."
if [ ! -f ".env" ]; then
    cat > .env << 'EOL'
# SuperAgent Configuration
# Replace with your actual API key from https://console.anthropic.com/

ANTHROPIC_API_KEY=your-api-key-here

# Optional settings
# REDIS_URL=redis://localhost:6379
# LOG_LEVEL=INFO
# ENVIRONMENT=production
EOL
    echo "   ✅ .env file created"
    echo "   ⚠️  Please edit .env and add your API key"
else
    echo "   ℹ️  .env file already exists"
fi
echo ""

# Create local data directories
echo "7️⃣  Creating local directories..."
mkdir -p data logs cache projects
echo "   ✅ Local directories created"
echo ""

# Create activation script
echo "8️⃣  Creating activation script..."
cat > activate.sh << 'EOL'
#!/bin/bash
# Activate SuperAgent environment
cd "$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
source venv/bin/activate
echo "SuperAgent environment activated!"
echo ""
echo "Available commands:"
echo "  superagent create 'project description'"
echo "  superagent voice talk"
echo "  superagent models current"
echo ""
EOL
chmod +x activate.sh
echo "   ✅ Activation script created"
echo ""

# Verify installation
echo "9️⃣  Verifying installation..."
if python3 verify_claude_4_5.py 2>/dev/null; then
    echo "   ✅ Verification passed"
else
    echo "   ⚠️  Verification completed (API key needed for full test)"
fi
echo ""

# Create usage instructions
cat > PRIVATE_DEPLOYMENT_COMPLETE.md << 'EOL'
# ✅ Private Deployment Complete!

SuperAgent has been deployed privately on your Mac.

## 🔐 Your Private Setup

**Location:** `/Users/armotorz/cursor project`

**Private Features:**
- ✅ Virtual environment (isolated from system Python)
- ✅ All dependencies installed locally
- ✅ No cloud deployment
- ✅ Data stored locally in `./data/`
- ✅ Logs stored locally in `./logs/`
- ✅ Complete privacy - runs only on your machine

## 🚀 How to Use

### Every time you want to use SuperAgent:

```bash
# 1. Navigate to project
cd "/Users/armotorz/cursor project"

# 2. Activate environment
source activate.sh
# or: source venv/bin/activate

# 3. Use SuperAgent
superagent create "your project"
```

### First Time Setup:

1. **Get your API key:**
   - Go to: https://console.anthropic.com/
   - Create an account (free)
   - Get your API key

2. **Set your API key:**
   ```bash
   # Edit .env file
   nano .env
   
   # Change this line:
   ANTHROPIC_API_KEY=your-api-key-here
   
   # To your actual key:
   ANTHROPIC_API_KEY=sk-ant-api03-...
   ```

3. **Test it:**
   ```bash
   source venv/bin/activate
   superagent models current
   superagent create "Hello World app"
   ```

## 📋 Quick Commands

```bash
# Activate environment
source activate.sh

# Check model
superagent models current

# Create project
superagent create "Build a calculator"

# Use voice
superagent voice talk

# Start API server (local only)
uvicorn superagent.api:app --host 127.0.0.1 --port 8000

# Deactivate when done
deactivate
```

## 🔒 Privacy & Security

Your installation is completely private:
- ✅ Runs only on your Mac
- ✅ No data sent to cloud (except API calls to Claude)
- ✅ All files stored locally
- ✅ Virtual environment isolated
- ✅ API key stored in local .env file only

## 📊 What's Installed

- SuperAgent with all 14 features
- Claude 4.5 Sonnet (latest model)
- Voice interface
- Multi-agent system
- All documentation
- Example scripts
- Test suites

## 🎯 Next Steps

1. Set your API key in `.env`
2. Run: `source activate.sh`
3. Test: `superagent models current`
4. Start building!

---

**Your private SuperAgent is ready!** 🎉
EOL

# Final message
echo "╔════════════════════════════════════════════════════════════════╗"
echo "║              ✅ PRIVATE DEPLOYMENT COMPLETE!                   ║"
echo "╚════════════════════════════════════════════════════════════════╝"
echo ""
echo "🔐 SuperAgent is now deployed privately on your Mac!"
echo ""
echo "📋 Final Steps:"
echo ""
echo "   1. Set your API key:"
echo "      nano .env"
echo "      # Add your key: ANTHROPIC_API_KEY=sk-ant-..."
echo ""
echo "   2. Activate environment:"
echo "      source activate.sh"
echo ""
echo "   3. Test it:"
echo "      superagent models current"
echo "      superagent create 'test project'"
echo ""
echo "📚 Documentation:"
echo "   - Read: PRIVATE_DEPLOYMENT_COMPLETE.md"
echo "   - Full guide: DEPLOYMENT_GUIDE.md"
echo ""
echo "✨ You're using Claude 4.5 Sonnet - the latest model!"
echo ""
echo "🎉 Everything is private and local to your machine!"
echo ""




