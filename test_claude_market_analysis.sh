#!/bin/bash

echo "=========================================="
echo "Testing Claude AI Market Analysis"
echo "=========================================="
echo ""

echo "Step 1: Check AI Status..."
status=$(curl -s https://web-production-f8308.up.railway.app/api/ai/status)
echo "$status" | python3 -m json.tool 2>/dev/null || echo "$status"
echo ""

echo "Step 2: Test Claude Diagnostic (full response)..."
echo "This will show if Claude API is responding correctly:"
echo ""
diag=$(curl -s https://web-production-f8308.up.railway.app/api/test/claude-ai)
echo "$diag" | python3 -m json.tool 2>/dev/null || echo "$diag"
echo ""

echo "=========================================="
echo "Next: Check Railway Logs for:"
echo "  - [_call_claude] messages"
echo "  - [AI_ANALYZE_MARKET] messages"
echo "  - Response structure details"
echo "=========================================="
