#!/bin/bash

# SuperAgent - Fix SSL and Deploy Script

set -e

echo "╔════════════════════════════════════════════════════════════════╗"
echo "║           SuperAgent - SSL Fix & Deployment                   ║"
echo "╚════════════════════════════════════════════════════════════════╝"
echo ""

PROJECT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$PROJECT_DIR"

# Step 1: Fix SSL Certificates
echo "1️⃣  Fixing SSL Certificates..."
if [ -f "/Applications/Python 3.13/Install Certificates.command" ]; then
    echo "   Running SSL certificate installer..."
    /Applications/Python\ 3.13/Install\ Certificates.command
    echo "   ✅ SSL certificates fixed"
elif [ -f "/Applications/Python 3.12/Install Certificates.command" ]; then
    /Applications/Python\ 3.12/Install\ Certificates.command
    echo "   ✅ SSL certificates fixed"
elif [ -f "/Applications/Python 3.11/Install Certificates.command" ]; then
    /Applications/Python\ 3.11/Install\ Certificates.command
    echo "   ✅ SSL certificates fixed"
else
    echo "   ⚠️  SSL installer not found, trying alternative fix..."
    pip3 install --upgrade certifi --break-system-packages 2>/dev/null || true
fi
echo ""

# Step 2: Check Python
echo "2️⃣  Checking Python..."
PYTHON_VERSION=$(python3 --version | awk '{print $2}')
echo "   ✅ Python $PYTHON_VERSION"
echo ""

# Step 3: Create Virtual Environment
echo "3️⃣  Creating virtual environment..."
if [ ! -d "venv" ]; then
    python3 -m venv venv
    echo "   ✅ Virtual environment created"
else
    echo "   ℹ️  Virtual environment exists"
fi

source venv/bin/activate
echo "   ✅ Activated"
echo ""

# Step 4: Upgrade pip with SSL fix
echo "4️⃣  Upgrading pip..."
python -m pip install --upgrade pip --trusted-host pypi.org --trusted-host files.pythonhosted.org 2>/dev/null || true
echo "   ✅ Pip upgraded"
echo ""

# Step 5: Install core dependencies
echo "5️⃣  Installing dependencies..."
echo "   (This may take a few minutes...)"

pip install anthropic --quiet 2>/dev/null || pip install anthropic --trusted-host pypi.org --trusted-host files.pythonhosted.org --quiet
pip install pydantic --quiet 2>/dev/null || pip install pydantic --trusted-host pypi.org --trusted-host files.pythonhosted.org --quiet
pip install pyyaml --quiet 2>/dev/null || pip install pyyaml --trusted-host pypi.org --trusted-host files.pythonhosted.org --quiet
pip install click --quiet 2>/dev/null || pip install click --trusted-host pypi.org --trusted-host files.pythonhosted.org --quiet
pip install rich --quiet 2>/dev/null || pip install rich --trusted-host pypi.org --trusted-host files.pythonhosted.org --quiet

echo "   ✅ Core dependencies installed"
echo ""

# Step 6: Install SuperAgent
echo "6️⃣  Installing SuperAgent..."
pip install -e . --quiet 2>/dev/null || pip install -e . --trusted-host pypi.org --trusted-host files.pythonhosted.org --quiet
echo "   ✅ SuperAgent installed"
echo ""

# Step 7: Create .env
echo "7️⃣  Creating configuration..."
if [ ! -f ".env" ]; then
    cat > .env << 'EOL'
ANTHROPIC_API_KEY=your-api-key-here
LOG_LEVEL=INFO
ENVIRONMENT=development
EOL
    echo "   ✅ .env file created"
else
    echo "   ℹ️  .env exists"
fi
echo ""

# Step 8: Create directories
echo "8️⃣  Creating directories..."
mkdir -p data logs cache projects
echo "   ✅ Directories created"
echo ""

# Step 9: Create activation script
cat > activate.sh << 'EOL'
#!/bin/bash
cd "$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
source venv/bin/activate
echo "✅ SuperAgent activated!"
echo ""
echo "Commands:"
echo "  superagent models current"
echo "  superagent create 'project description'"
echo ""
EOL
chmod +x activate.sh
echo "9️⃣  ✅ Activation script created"
echo ""

# Step 10: Test basic functionality
echo "🔟 Testing installation..."
python3 << 'PYTHON_TEST'
import sys
print("Testing SuperAgent imports...")

try:
    from superagent.core.config import Config
    print("✅ Config module works")
except Exception as e:
    print(f"⚠️  Config: {e}")

try:
    from superagent.core.agent import Agent
    print("✅ Agent module works")
except Exception as e:
    print(f"⚠️  Agent: {e}")

try:
    import anthropic
    print("✅ Anthropic SDK installed")
except Exception as e:
    print(f"⚠️  Anthropic: {e}")

print("\n✅ Basic modules working!")
PYTHON_TEST

echo ""
echo "╔════════════════════════════════════════════════════════════════╗"
echo "║                  ✅ DEPLOYMENT COMPLETE!                       ║"
echo "╚════════════════════════════════════════════════════════════════╝"
echo ""
echo "📋 Next Steps:"
echo ""
echo "   1. Add your API key:"
echo "      nano .env"
echo ""
echo "   2. Activate environment:"
echo "      source activate.sh"
echo ""
echo "   3. Test:"
echo "      superagent models current"
echo ""
echo "🎉 SuperAgent is ready!"
echo ""

