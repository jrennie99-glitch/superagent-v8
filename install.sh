#!/bin/bash

# SuperAgent Installation Script
# This script sets up SuperAgent on your system

set -e

echo "╔════════════════════════════════════════╗"
echo "║   SuperAgent Installation Script      ║"
echo "║   Advanced AI Agent Framework          ║"
echo "╚════════════════════════════════════════╝"
echo ""

# Check Python version
echo "→ Checking Python version..."
python_version=$(python3 --version 2>&1 | awk '{print $2}')
required_version="3.10"

if ! python3 -c "import sys; exit(0 if sys.version_info >= (3, 10) else 1)"; then
    echo "✗ Error: Python 3.10+ required. Found: $python_version"
    exit 1
fi
echo "✓ Python $python_version found"

# Create virtual environment
echo ""
echo "→ Creating virtual environment..."
if [ -d "venv" ]; then
    echo "  Virtual environment already exists"
else
    python3 -m venv venv
    echo "✓ Virtual environment created"
fi

# Activate virtual environment
echo ""
echo "→ Activating virtual environment..."
source venv/bin/activate
echo "✓ Virtual environment activated"

# Install dependencies
echo ""
echo "→ Installing dependencies..."
pip install --upgrade pip > /dev/null 2>&1
pip install -r requirements.txt > /dev/null 2>&1
echo "✓ Dependencies installed"

# Install SuperAgent
echo ""
echo "→ Installing SuperAgent..."
pip install -e . > /dev/null 2>&1
echo "✓ SuperAgent installed"

# Setup configuration
echo ""
echo "→ Setting up configuration..."
if [ ! -f ".env" ]; then
    cp .env.example .env 2>/dev/null || true
    echo "✓ Created .env file (please add your API keys)"
else
    echo "  .env already exists"
fi

# Check for Redis (optional)
echo ""
echo "→ Checking for Redis (optional)..."
if command -v redis-cli &> /dev/null; then
    echo "✓ Redis found"
else
    echo "⚠ Redis not found (optional - will use disk cache)"
fi

# Run tests
echo ""
read -p "→ Run tests to verify installation? (y/n) " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo "→ Running tests..."
    pytest tests/test_agent.py -v -k "test_agent_initialization" || true
    echo "✓ Test run complete"
fi

echo ""
echo "╔════════════════════════════════════════╗"
echo "║     Installation Complete! 🎉         ║"
echo "╚════════════════════════════════════════╝"
echo ""
echo "Next steps:"
echo "  1. Edit .env and add your ANTHROPIC_API_KEY"
echo "  2. Activate venv: source venv/bin/activate"
echo "  3. Try an example: python examples/basic_usage.py"
echo "  4. Or use CLI: superagent create 'your instruction'"
echo ""
echo "Documentation:"
echo "  - Quick Start: QUICKSTART.md"
echo "  - Full Docs:   README.md"
echo "  - Examples:    examples/"
echo ""
echo "Need help? Check README.md or open an issue on GitHub"
echo ""





