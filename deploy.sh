#!/bin/bash

# SuperAgent Deployment Script
# This script will deploy SuperAgent locally on your machine

set -e  # Exit on error

echo "╔════════════════════════════════════════════════════════════════╗"
echo "║           SuperAgent - Local Deployment Script                ║"
echo "╚════════════════════════════════════════════════════════════════╝"
echo ""

# Check Python version
echo "1️⃣  Checking Python version..."
PYTHON_VERSION=$(python3 --version 2>&1 | awk '{print $2}')
echo "   ✅ Found Python $PYTHON_VERSION"
echo ""

# Check if pip is available
echo "2️⃣  Checking pip..."
if command -v pip3 &> /dev/null; then
    echo "   ✅ pip3 is available"
else
    echo "   ❌ pip3 not found. Please install pip3 first."
    exit 1
fi
echo ""

# Install dependencies
echo "3️⃣  Installing dependencies..."
echo "   This may take a few minutes..."
pip3 install --upgrade pip setuptools wheel
pip3 install anthropic langchain openai fastapi uvicorn redis structlog pyyaml pydantic click rich
pip3 install pytest pytest-asyncio radon pylint mypy black bandit
echo "   ✅ Dependencies installed"
echo ""

# Install SuperAgent
echo "4️⃣  Installing SuperAgent..."
pip3 install -e .
echo "   ✅ SuperAgent installed"
echo ""

# Check for API key
echo "5️⃣  Checking API configuration..."
if [ -z "$ANTHROPIC_API_KEY" ]; then
    echo "   ⚠️  ANTHROPIC_API_KEY not set"
    echo ""
    echo "   To set your API key, run:"
    echo "   export ANTHROPIC_API_KEY='sk-ant-your-key-here'"
    echo ""
    echo "   Or create a .env file with:"
    echo "   ANTHROPIC_API_KEY=sk-ant-your-key-here"
    echo ""
else
    echo "   ✅ API key is set"
fi
echo ""

# Run verification
echo "6️⃣  Running verification..."
python3 verify_claude_4_5.py
echo ""

# Show next steps
echo "╔════════════════════════════════════════════════════════════════╗"
echo "║                  ✅ DEPLOYMENT COMPLETE!                       ║"
echo "╚════════════════════════════════════════════════════════════════╝"
echo ""
echo "🚀 SuperAgent is now deployed!"
echo ""
echo "📋 Next Steps:"
echo ""
echo "   1. Set your API key (if not done):"
echo "      export ANTHROPIC_API_KEY='sk-ant-your-key-here'"
echo ""
echo "   2. Test SuperAgent:"
echo "      superagent models current"
echo "      superagent create 'Hello World app'"
echo ""
echo "   3. Use voice interface:"
echo "      superagent voice talk"
echo ""
echo "   4. Start API server:"
echo "      uvicorn superagent.api:app --reload"
echo ""
echo "📚 Documentation:"
echo "   - Quick Start: QUICK_DEPLOY.md"
echo "   - Full Guide: DEPLOYMENT_GUIDE.md"
echo "   - Getting Started: START_HERE.md"
echo ""
echo "✨ You're using Claude 4.5 Sonnet - the latest model!"
echo ""





