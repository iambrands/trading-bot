#!/bin/bash
# Setup Git and Deploy Cache Fix to GitHub

set -e  # Exit on error

echo "🚀 Setting up Git and preparing to deploy cache fixes..."
echo ""

# Check if git is installed
if ! command -v git &> /dev/null; then
    echo "❌ Git is not installed. Please install git first."
    exit 1
fi

# Initialize git repository if it doesn't exist
if [ ! -d .git ]; then
    echo "📦 Initializing git repository..."
    git init
    echo "✅ Git repository initialized"
else
    echo "✅ Git repository already exists"
fi

# Add the GitHub remote
GITHUB_REPO="https://github.com/iambrands/trading-bot.git"
echo ""
echo "🔗 Setting up GitHub remote..."
if git remote get-url origin &> /dev/null; then
    echo "⚠️  Remote 'origin' already exists:"
    git remote get-url origin
    read -p "Do you want to update it to $GITHUB_REPO? (y/n) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        git remote set-url origin "$GITHUB_REPO"
        echo "✅ Remote updated"
    else
        echo "ℹ️  Keeping existing remote"
    fi
else
    git remote add origin "$GITHUB_REPO"
    echo "✅ Remote 'origin' added: $GITHUB_REPO"
fi

# Show current status
echo ""
echo "📊 Current git status:"
git status --short || echo "No changes detected"

# List modified files
echo ""
echo "📝 Files that will be committed:"
echo "  • api/rest_api.py (server-side blocking)"
echo "  • static/dashboard.html (cache clearing)"
echo "  • static/landing.html (cache clearing)"
echo "  • static/signin.html (cache clearing)"
echo "  • static/service-worker.js (v2 update)"
echo "  • CACHE_FIX_STATUS.md (documentation)"
echo "  • DEPLOY_INSTRUCTIONS.md (deployment guide)"
echo ""

# Ask for confirmation
read -p "Do you want to stage and commit these changes? (y/n) " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "❌ Cancelled. You can run the commands manually:"
    echo ""
    echo "  git add api/rest_api.py static/dashboard.html static/landing.html static/signin.html static/service-worker.js CACHE_FIX_STATUS.md DEPLOY_INSTRUCTIONS.md"
    echo "  git commit -m 'Fix: Block hashed CSS/JS requests and add cache clearing'"
    echo "  git push -u origin main"
    exit 0
fi

# Stage the files
echo ""
echo "📦 Staging files..."
git add api/rest_api.py
git add static/dashboard.html
git add static/landing.html
git add static/signin.html
git add static/service-worker.js
git add CACHE_FIX_STATUS.md
git add DEPLOY_INSTRUCTIONS.md

# Check if there are changes to commit
if git diff --cached --quiet; then
    echo "⚠️  No changes to commit. Files may already be committed or unchanged."
    exit 0
fi

# Commit
echo ""
echo "💾 Committing changes..."
git commit -m "Fix: Block hashed CSS/JS requests and add cache clearing

- Add server-side middleware to block hashed file requests (main.*.css/js)
- Add aggressive cache-clearing scripts to HTML files
- Update service worker to v2-2024-12 with enhanced cache clearing
- Add cache-control headers to prevent HTML caching
- Fixes 404 errors for main.3e5d15db.css and main.a71a8271.js
- Resolves 'p1 is not defined' error from cached JavaScript"

echo "✅ Changes committed"

# Ask about pushing
echo ""
read -p "Do you want to push to GitHub now? (y/n) " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "ℹ️  Changes committed locally. Push manually with:"
    echo "  git push -u origin main"
    echo "  (or 'git push -u origin master' if your default branch is master)"
    exit 0
fi

# Determine default branch
echo ""
echo "🔍 Checking default branch..."
DEFAULT_BRANCH=$(git branch --show-current 2>/dev/null || echo "main")

if [ -z "$DEFAULT_BRANCH" ]; then
    DEFAULT_BRANCH="main"
    git checkout -b main 2>/dev/null || git branch -M main 2>/dev/null || true
fi

echo "📤 Pushing to GitHub (branch: $DEFAULT_BRANCH)..."
if git push -u origin "$DEFAULT_BRANCH" 2>&1; then
    echo ""
    echo "✅ Successfully pushed to GitHub!"
    echo ""
    echo "🌐 Repository: https://github.com/iambrands/trading-bot"
    echo ""
    echo "📋 Next steps:"
    echo "  1. If Heroku is connected to GitHub, it will auto-deploy"
    echo "  2. Or deploy manually: git push heroku $DEFAULT_BRANCH"
    echo "  3. After deployment, clear your browser cache"
    echo "  4. Hard refresh: Ctrl+Shift+R (or Cmd+Shift+R on Mac)"
else
    echo ""
    echo "⚠️  Push failed. Common reasons:"
    echo "  • Not authenticated with GitHub (run: gh auth login)"
    echo "  • Repository doesn't exist or you don't have access"
    echo "  • Need to set up SSH keys or personal access token"
    echo ""
    echo "You can push manually after setting up authentication:"
    echo "  git push -u origin $DEFAULT_BRANCH"
fi



