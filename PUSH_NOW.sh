#!/bin/bash

# SuperAgent - Push to GitHub Script
# This will guide you through pushing to GitHub

echo "╔════════════════════════════════════════════════════════════════╗"
echo "║          🚀 Push SuperAgent to GitHub                          ║"
echo "╚════════════════════════════════════════════════════════════════╝"
echo ""
echo "Repository: https://github.com/jay99ja/superagent1.git"
echo "Files ready: 86 files, 21,248 lines"
echo ""

cd "/Users/armotorz/cursor project"

# Check if gh CLI is installed
if command -v gh &> /dev/null; then
    echo "✅ GitHub CLI found!"
    echo ""
    echo "Checking GitHub authentication..."
    
    if gh auth status &> /dev/null; then
        echo "✅ Already authenticated!"
        echo ""
        echo "Pushing to GitHub..."
        git push -u origin main
        
        if [ $? -eq 0 ]; then
            echo ""
            echo "╔════════════════════════════════════════════════════════════════╗"
            echo "║                  ✅ SUCCESS! ✅                                 ║"
            echo "╚════════════════════════════════════════════════════════════════╝"
            echo ""
            echo "Your SuperAgent is now live on GitHub!"
            echo ""
            echo "View it here:"
            echo "→ https://github.com/jay99ja/superagent1"
            echo ""
            echo "Share with others:"
            echo "→ git clone https://github.com/jay99ja/superagent1.git"
            echo ""
        else
            echo ""
            echo "❌ Push failed. Check the error above."
        fi
    else
        echo "⚠️  Not authenticated with GitHub"
        echo ""
        echo "Let's authenticate now..."
        echo ""
        gh auth login
        
        echo ""
        echo "Now pushing to GitHub..."
        git push -u origin main
        
        if [ $? -eq 0 ]; then
            echo ""
            echo "╔════════════════════════════════════════════════════════════════╗"
            echo "║                  ✅ SUCCESS! ✅                                 ║"
            echo "╚════════════════════════════════════════════════════════════════╝"
            echo ""
            echo "Your SuperAgent is now live on GitHub!"
            echo ""
            echo "View it here:"
            echo "→ https://github.com/jay99ja/superagent1"
            echo ""
        fi
    fi
else
    echo "⚠️  GitHub CLI not found"
    echo ""
    echo "OPTION 1: Install GitHub CLI and try again"
    echo "  $ brew install gh"
    echo "  $ ./PUSH_NOW.sh"
    echo ""
    echo "OPTION 2: Use personal access token"
    echo ""
    echo "  1. Get token from: https://github.com/settings/tokens"
    echo "  2. Click 'Generate new token (classic)'"
    echo "  3. Name: SuperAgent"
    echo "  4. Select scope: ✅ repo"
    echo "  5. Generate and copy token"
    echo ""
    echo "  Then run:"
    echo "  $ git push -u origin main"
    echo ""
    echo "  Username: jay99ja"
    echo "  Password: [paste your token]"
    echo ""
fi

