#!/bin/bash

echo "=========================================="
echo "COMPREHENSIVE CLAUDE AI TEST"
echo "=========================================="
echo "Date: $(date)"
echo ""

echo "Step 1: Testing diagnostic endpoint..."
echo "This will trigger Claude API call and generate detailed logs"
echo ""

# Call the diagnostic endpoint
response=$(curl -s https://web-production-f8308.up.railway.app/api/test/claude-ai)

# Save response
echo "$response" > diagnostic_response.json

echo "Response received and saved to: diagnostic_response.json"
echo ""

# Parse and display
echo "=========================================="
echo "QUICK SUMMARY"
echo "=========================================="

python3 << 'PYTHON_SCRIPT'
import json
import sys

try:
    with open('diagnostic_response.json', 'r') as f:
        data = json.load(f)
    
    # Environment check
    env = data.get('test_results', {}).get('environment', {})
    print(f"✓ API Key Present: {env.get('CLAUDE_API_KEY_exists')}")
    print(f"✓ API Key Length: {env.get('CLAUDE_API_KEY_length')} chars")
    print()
    
    # Initialization check
    init = data.get('test_results', {}).get('initialization', {})
    print(f"✓ Initialization: {init.get('success')}")
    print()
    
    # API call check
    api = data.get('test_results', {}).get('api_call', {})
    print(f"✓ API Call Success: {api.get('success')}")
    print(f"✓ Response Type: {api.get('response_type')}")
    print(f"✓ Response Length: {api.get('response_length')} chars")
    print(f"✓ Response Empty: {api.get('response_is_empty')}")
    print()
    
    if api.get('response_preview'):
        print("Response Preview:")
        print("-" * 40)
        print(api.get('response_preview')[:300])
        print("-" * 40)
    
    # Check for errors
    if 'error' in data:
        print()
        print(f"❌ ERROR: {data.get('error')}")
    
    # Overall status
    print()
    print("=" * 40)
    if api.get('success') and api.get('response_length', 0) > 0:
        print("🎉 SUCCESS - Claude AI is working!")
    elif api.get('success') and api.get('response_is_empty'):
        print("⚠️  PARTIAL - API works but returns empty response")
    else:
        print("❌ FAILED - See error above")
    print("=" * 40)
    
except Exception as e:
    print(f"Error parsing response: {e}")
    print()
    print("Raw response:")
    with open('diagnostic_response.json', 'r') as f:
        print(f.read())

PYTHON_SCRIPT

echo ""
echo "Step 2: Checking Railway logs..."
echo "(You need to manually check Railway dashboard)"
echo ""
echo "Go to:"
echo "https://railway.app → crypto-trading-bot → Logs"
echo ""
echo "Search for: [_call_claude]"
echo ""
echo "Look for these log lines:"
echo "  - [_call_claude] STARTING CLAUDE API CALL"
echo "  - [_call_claude] Response status: 200"
echo "  - [_call_claude] Response keys: [...]"
echo "  - [_call_claude] Full response preview: {...}"
echo "  - [_call_claude] Content type: ..."
echo "  - [_call_claude] ✅ SUCCESS or ❌ ERROR"
echo ""
echo "=========================================="
echo "TEST COMPLETE"
echo "=========================================="
echo ""
echo "Next steps:"
echo "1. Review diagnostic_response.json"
echo "2. Check Railway logs for [_call_claude] entries"
echo "3. If successful, test the Market Conditions page in the UI"
echo "4. If failed, share the Railway logs for debugging"

