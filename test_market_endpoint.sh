#!/bin/bash

echo "=========================================="
echo "MARKET CONDITIONS ENDPOINT TEST"
echo "=========================================="
echo ""

echo "Sending real market data to AI analysis endpoint..."

curl -s -X POST https://web-production-f8308.up.railway.app/api/ai/analyze-market \
  -H "Content-Type: application/json" \
  -d '{
    "market_data": {
      "BTC-USD": {
        "price": 92643.0,
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
  }' > market_analysis_response.json

echo "Response saved to: market_analysis_response.json"
echo ""

python3 << 'PYTHON_SCRIPT'
import json

try:
    with open('market_analysis_response.json', 'r') as f:
        data = json.load(f)
    
    success = data.get('success')
    analysis = data.get('analysis', '')
    error = data.get('error')
    
    print("=" * 40)
    print("RESULT")
    print("=" * 40)
    print(f"Success: {success}")
    print(f"Analysis Length: {len(analysis)} chars")
    print()
    
    if success and analysis:
        print("✅ AI Analysis Generated!")
        print()
        print("Analysis:")
        print("-" * 40)
        print(analysis)
        print("-" * 40)
    elif error:
        print(f"❌ Error: {error}")
    else:
        print("⚠️  Success=True but no analysis content")
    
except Exception as e:
    print(f"Error: {e}")
    with open('market_analysis_response.json', 'r') as f:
        print(f.read())

PYTHON_SCRIPT

echo ""
echo "Test complete!"

