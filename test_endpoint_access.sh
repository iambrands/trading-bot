#!/bin/bash

echo "Testing endpoint accessibility..."
echo ""

# Test 1: Health check (should work)
echo "1. Testing health check endpoint..."
health_response=$(curl -s -w "\n%{http_code}" https://web-production-f8308.up.railway.app/api/test/trading-health)
health_code=$(echo "$health_response" | tail -n 1)

if [ "$health_code" = "200" ]; then
    echo "✅ Health check works (HTTP 200)"
else
    echo "❌ Health check failed (HTTP $health_code)"
fi

echo ""

# Test 2: Claude diagnostic endpoint
echo "2. Testing Claude diagnostic endpoint..."
claude_response=$(curl -s -w "\n%{http_code}" https://web-production-f8308.up.railway.app/api/test/claude-ai)
claude_code=$(echo "$claude_response" | tail -n 1)

if [ "$claude_code" = "200" ]; then
    echo "✅ Claude diagnostic endpoint responds (HTTP 200)"
    echo ""
    echo "Response preview:"
    echo "$claude_response" | head -n -1 | python3 -m json.tool 2>/dev/null | head -20 || echo "$claude_response" | head -n -1
else
    echo "❌ Claude diagnostic endpoint failed (HTTP $claude_code)"
    echo "Response:"
    echo "$claude_response"
fi

echo ""

# Test 3: Try the market analysis endpoint
echo "3. Testing market analysis endpoint..."
market_response=$(curl -s -w "\n%{http_code}" -X POST https://web-production-f8308.up.railway.app/api/ai/analyze-market \
  -H "Content-Type: application/json" \
  -d '{"market_data": {"BTC-USD": {"price": 92571, "trend": "bearish"}}}')
market_code=$(echo "$market_response" | tail -n 1)

if [ "$market_code" = "200" ]; then
    echo "✅ Market analysis endpoint responds (HTTP 200)"
    echo ""
    echo "Response preview:"
    echo "$market_response" | head -n -1 | python3 -m json.tool 2>/dev/null | head -20 || echo "$market_response" | head -n -1
elif [ "$market_code" = "401" ]; then
    echo "⚠️  Market analysis endpoint requires authentication (HTTP 401) - This is expected"
else
    echo "❌ Market analysis endpoint failed (HTTP $market_code)"
    echo "Response:"
    echo "$market_response"
fi

