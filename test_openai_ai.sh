#!/bin/bash

echo "=========================================="
echo "OPENAI AI INTEGRATION TEST"
echo "=========================================="
echo "Date: $(date)"
echo ""

echo "Step 1: Testing AI status endpoint..."
echo ""

# Test AI status
status_response=$(curl -s https://web-production-f8308.up.railway.app/api/ai/status)
echo "$status_response" | python3 -m json.tool 2>/dev/null || echo "$status_response"
echo ""

echo "Step 2: Testing market analysis endpoint..."
echo ""

# Test market analysis with sample data
analysis_response=$(curl -s -X POST https://web-production-f8308.up.railway.app/api/ai/analyze-market \
  -H "Content-Type: application/json" \
  -d '{
    "market_data": {
      "BTC-USD": {
        "price": 92571.0,
        "ema": 92000.0,
        "rsi": 65.0,
        "volume_ratio": 1.5
      }
    },
    "trading_signals": {
      "BTC-USD": {
        "long_signal": {"confidence": 75.0, "conditions_met": true},
        "short_signal": {"confidence": 0.0, "conditions_met": false}
      }
    }
  }')

echo "Response:"
echo "$analysis_response" | python3 -m json.tool 2>/dev/null || echo "$analysis_response"
echo ""

# Check if successful
success=$(echo "$analysis_response" | python3 -c "import sys, json; data = json.load(sys.stdin); print(data.get('success', False))" 2>/dev/null)

if [ "$success" = "True" ]; then
    echo "✅ SUCCESS - OpenAI AI is working!"
    analysis=$(echo "$analysis_response" | python3 -c "import sys, json; data = json.load(sys.stdin); print(data.get('analysis', '')[:200])" 2>/dev/null)
    echo ""
    echo "Analysis preview:"
    echo "$analysis..."
else
    echo "❌ FAILED - Check the error message above"
fi

echo ""
echo "=========================================="
echo "TEST COMPLETE"
echo "=========================================="

