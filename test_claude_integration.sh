#!/bin/bash

echo "=========================================="
echo "CLAUDE AI INTEGRATION TEST"
echo "=========================================="
echo "Date: $(date)"
echo ""

echo "Step 1: Testing AI status endpoint..."
echo ""

# Test AI status
status_response=$(curl -s https://web-production-f8308.up.railway.app/api/ai/status)
echo "$status_response" | python3 -m json.tool 2>/dev/null || echo "$status_response"
echo ""

echo "Step 2: Testing Claude diagnostic endpoint..."
echo ""

# Test Claude diagnostic
diag_response=$(curl -s https://web-production-f8308.up.railway.app/api/test/claude-ai)
echo "$diag_response" | python3 -m json.tool 2>/dev/null | head -50 || echo "$diag_response" | head -20
echo ""

echo "Step 3: Testing market analysis endpoint (requires auth)..."
echo "Note: This will return 401 without auth token, but confirms endpoint exists"
echo ""

# Test market analysis (will fail auth but confirms endpoint exists)
analysis_response=$(curl -s -X POST https://web-production-f8308.up.railway.app/api/ai/analyze-market \
  -H "Content-Type: application/json" \
  -d '{"market_data": {"BTC-USD": {"price": 92571}}, "trading_signals": {}}')

status_code=$(echo "$analysis_response" | python3 -c "import sys, json; data = json.load(sys.stdin); print(data.get('error', 'SUCCESS')[:50])" 2>/dev/null || echo "Response received")

if [[ "$status_code" == *"Authentication required"* ]]; then
    echo "✅ Endpoint exists (auth required as expected)"
elif [[ "$status_code" == *"SUCCESS"* ]]; then
    echo "✅ Endpoint working!"
else
    echo "Response: $status_code"
fi

echo ""
echo "=========================================="
echo "TEST COMPLETE"
echo "=========================================="
echo ""
echo "Next steps:"
echo "1. Check Railway logs for [AI_ANALYZE_MARKET] and [_call_claude] messages"
echo "2. Test the Market Conditions page in the browser"
echo "3. Verify AI analysis appears on the page"

