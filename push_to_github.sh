#!/bin/bash
# Auto-push to GitHub using Replit OAuth connection
# No password required!

set -e

echo "🚀 SuperAgent GitHub Push"
echo "=========================="
echo ""

# Get GitHub credentials from API
echo "📡 Getting GitHub credentials..."
STATUS=$(curl -s http://localhost:5000/api/v1/github/status)
CONFIGURED=$(echo $STATUS | grep -o '"configured":[^,]*' | cut -d':' -f2)
USERNAME=$(echo $STATUS | grep -o '"username":"[^"]*"' | cut -d'"' -f4)

if [ "$CONFIGURED" != "true" ]; then
    echo "❌ GitHub not configured. Please connect GitHub first."
    echo "Visit: /project-manager to connect"
    exit 1
fi

echo "✓ Connected as: $USERNAME"
echo ""

# Get repository name
read -p "📦 Repository name (default: SuperAgent): " REPO_NAME
REPO_NAME=${REPO_NAME:-SuperAgent}

echo ""
echo "📝 Adding files..."
git add .

echo "✍️  Creating commit..."
git commit -m "🚀 SuperAgent - GitHub integration and multi-platform deployment

✅ Dual-mode GitHub service (Replit OAuth + manual token)
✅ Automatic username fetching from GitHub API  
✅ One-click deployment to Vercel, Railway, Render, Fly.io
✅ Project import/export with intelligent scaffolding
✅ Mobile PWA, Memory Viewer, Runway ML video generation
✅ Production-ready and architect-approved" || echo "No changes to commit"

# Check if remote exists
if git remote get-url origin 2>/dev/null; then
    echo "📍 Remote already configured"
else
    echo "🔗 Adding GitHub remote..."
    git remote add origin "https://github.com/$USERNAME/$REPO_NAME.git"
fi

echo ""
echo "🚀 Pushing to GitHub..."
echo "Repository: https://github.com/$USERNAME/$REPO_NAME"
echo ""

# Use GitHub CLI if available, otherwise use git push
if command -v gh &> /dev/null; then
    gh repo create "$REPO_NAME" --public --source=. --push || git push -u origin main
else
    echo "💡 Tip: Use the Replit Git pane for OAuth authentication"
    echo "   Or run: git push -u origin main"
    echo ""
    git push -u origin main
fi

echo ""
echo "✅ Successfully pushed to GitHub!"
echo "🌐 View at: https://github.com/$USERNAME/$REPO_NAME"
