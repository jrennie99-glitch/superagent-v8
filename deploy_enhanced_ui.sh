#!/bin/bash
# Deploy Enhanced UI to SuperAgent v8

echo "🚀 SuperAgent v8 - Enhanced UI Deployment Script"
echo "================================================"
echo ""

# Backup current index.html
echo "📦 Creating backup of current index.html..."
cp index.html index_backup_$(date +%Y%m%d_%H%M%S).html
echo "✅ Backup created"
echo ""

# Copy enhanced version
echo "📝 Deploying enhanced interface..."
cp index_enhanced_logging.html index.html
echo "✅ Enhanced interface deployed"
echo ""

# Git operations
echo "📤 Committing to Git..."
git add index.html index_enhanced_logging.html ENHANCED_BUILD_SYSTEM_GUIDE.md
git add index_fixed.html agent_demo_fixed.html COPY_PASTE_FIX_GUIDE.md
git commit -m "feat: Deploy enhanced build system with detailed logging

- Add 3-column professional interface
- Detailed build log with timestamps and color coding
- Live preview panel with controls
- Build options (Plan Mode, Enterprise Mode, Live Preview, Auto Deploy)
- Copy-paste fixes included
- Comprehensive documentation"

echo "✅ Changes committed"
echo ""

echo "🎯 Next steps:"
echo "1. Push to GitHub: git push origin main"
echo "2. Render will auto-deploy (if enabled)"
echo "3. Visit: https://supermen-v8.onrender.com"
echo ""
echo "✨ Deployment preparation complete!"
