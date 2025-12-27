#!/bin/bash
# Script to add environment variables to Railway

echo "Adding environment variables to Railway..."
echo ""

# Add DATABASE_URL
railway variables set DATABASE_URL="postgresql://postgres:MRjbxvYzpOmvyQFmQsuWgcAToEyeCsnn@ballast.proxy.rlwy.net:22003/railway"
echo "✅ Added DATABASE_URL"

# Add JWT_SECRET_KEY
railway variables set JWT_SECRET_KEY="xvNNDx-G3scNpANLA0d-UcS5tXYFbxkvc3Sq5TvLpGQ"
echo "✅ Added JWT_SECRET_KEY"

# Add ENVIRONMENT
railway variables set ENVIRONMENT="production"
echo "✅ Added ENVIRONMENT"

# Add PAPER_TRADING
railway variables set PAPER_TRADING="true"
echo "✅ Added PAPER_TRADING"

# Add LOG_LEVEL
railway variables set LOG_LEVEL="INFO"
echo "✅ Added LOG_LEVEL"

# Add CLAUDE_API_KEY
railway variables set CLAUDE_API_KEY="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"
echo "✅ Added CLAUDE_API_KEY"

# Add CLAUDE_MODEL (optional)
railway variables set CLAUDE_MODEL="claude-3-haiku-20240307"
echo "✅ Added CLAUDE_MODEL"

echo ""
echo "✅ All variables added! Railway will automatically redeploy."
echo "Wait for deployment to complete, then try signing in!"

