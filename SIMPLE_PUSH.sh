#!/bin/bash

# Simple Push Script - Step by Step
# This will help diagnose what's not found

echo "╔════════════════════════════════════════════════════════════════╗"
echo "║          🔍 Diagnosing and Pushing to GitHub                   ║"
echo "╚════════════════════════════════════════════════════════════════╝"
echo ""

# Check 1: Are we in the right directory?
echo "1️⃣  Checking directory..."
if [ -d "/Users/armotorz/cursor project" ]; then
    echo "   ✅ Project directory exists"
    cd "/Users/armotorz/cursor project"
else
    echo "   ❌ Project directory not found"
    echo "   Current directory: $(pwd)"
    echo ""
    echo "   Let's check where we are..."
    ls -la
    exit 1
fi
echo ""

# Check 2: Is git installed?
echo "2️⃣  Checking git..."
if command -v git &> /dev/null; then
    GIT_VERSION=$(git --version)
    echo "   ✅ Git installed: $GIT_VERSION"
else
    echo "   ❌ Git not installed"
    echo "   Installing git..."
    xcode-select --install
    exit 1
fi
echo ""

# Check 3: Is this a git repository?
echo "3️⃣  Checking git repository..."
if [ -d ".git" ]; then
    echo "   ✅ Git repository found"
    COMMIT_COUNT=$(git rev-list --count HEAD 2>/dev/null || echo "0")
    echo "   ✅ Commits: $COMMIT_COUNT"
else
    echo "   ❌ Not a git repository"
    exit 1
fi
echo ""

# Check 4: Is brew installed?
echo "4️⃣  Checking Homebrew..."
if command -v brew &> /dev/null; then
    echo "   ✅ Homebrew installed"
else
    echo "   ⚠️  Homebrew not installed"
    echo "   Installing Homebrew..."
    /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
    
    # Add brew to path
    if [ -f "/opt/homebrew/bin/brew" ]; then
        eval "$(/opt/homebrew/bin/brew shellenv)"
    fi
fi
echo ""

# Check 5: Is gh installed?
echo "5️⃣  Checking GitHub CLI..."
if command -v gh &> /dev/null; then
    echo "   ✅ GitHub CLI installed"
else
    echo "   ⚠️  GitHub CLI not installed"
    echo "   Installing gh..."
    brew install gh
fi
echo ""

# Check 6: Is gh authenticated?
echo "6️⃣  Checking GitHub authentication..."
if gh auth status &> /dev/null; then
    echo "   ✅ Already authenticated with GitHub!"
    echo ""
    echo "7️⃣  Pushing to GitHub..."
    git push -u origin main
    
    if [ $? -eq 0 ]; then
        echo ""
        echo "╔════════════════════════════════════════════════════════════════╗"
        echo "║                    ✅ SUCCESS! ✅                               ║"
        echo "╚════════════════════════════════════════════════════════════════╝"
        echo ""
        echo "Your SuperAgent is now on GitHub!"
        echo "→ https://github.com/jay99ja/superagent1"
        echo ""
    else
        echo ""
        echo "❌ Push failed. See error above."
    fi
else
    echo "   ⚠️  Not authenticated with GitHub"
    echo ""
    echo "   Let's authenticate now..."
    gh auth login
    
    if [ $? -eq 0 ]; then
        echo ""
        echo "7️⃣  Pushing to GitHub..."
        git push -u origin main
        
        if [ $? -eq 0 ]; then
            echo ""
            echo "╔════════════════════════════════════════════════════════════════╗"
            echo "║                    ✅ SUCCESS! ✅                               ║"
            echo "╚════════════════════════════════════════════════════════════════╝"
            echo ""
            echo "Your SuperAgent is now on GitHub!"
            echo "→ https://github.com/jay99ja/superagent1"
            echo ""
        else
            echo ""
            echo "❌ Push failed. See error above."
        fi
    else
        echo ""
        echo "❌ Authentication failed or cancelled"
    fi
fi

