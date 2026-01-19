#!/bin/bash

echo "Checking Railway deployment status..."
echo ""

# Test if the server is responding
response=$(curl -s -o /dev/null -w "%{http_code}" https://web-production-f8308.up.railway.app/api/test/trading-health)

if [ "$response" = "200" ]; then
    echo "✅ Server is responding (HTTP $response)"
    echo ""
    
    # Get the latest commit from health check
    health_data=$(curl -s https://web-production-f8308.up.railway.app/api/test/trading-health)
    echo "Server Status:"
    echo "$health_data" | python3 -m json.tool | head -20
    
    echo ""
    echo "✅ Deployment appears ready for testing"
    exit 0
else
    echo "❌ Server not responding (HTTP $response)"
    echo "Wait a bit longer for deployment to complete..."
    exit 1
fi

