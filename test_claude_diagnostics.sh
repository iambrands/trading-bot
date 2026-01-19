#!/bin/bash

# Claude AI Diagnostic Test Script
# Tests the Claude AI integration endpoint on Railway

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Get Railway URL from environment or use default
RAILWAY_URL="${RAILWAY_URL:-https://web-production-f8308.up.railway.app}"

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}Claude AI Diagnostic Test${NC}"
echo -e "${BLUE}========================================${NC}"
echo ""
echo "Railway URL: $RAILWAY_URL"
echo ""

# Test 1: Check if server is reachable
echo -e "${YELLOW}[TEST 1] Checking server connectivity...${NC}"
if curl -s -f -o /dev/null "${RAILWAY_URL}/api/status" > /dev/null 2>&1; then
    echo -e "${GREEN}✅ Server is reachable${NC}"
else
    echo -e "${RED}❌ Server is not reachable${NC}"
    echo "Please check if Railway deployment is running"
    exit 1
fi
echo ""

# Test 2: Check AI Status endpoint
echo -e "${YELLOW}[TEST 2] Checking AI status endpoint...${NC}"
STATUS_RESPONSE=$(curl -s "${RAILWAY_URL}/api/ai/status")
echo "$STATUS_RESPONSE" | jq '.' 2>/dev/null || echo "$STATUS_RESPONSE"
echo ""

# Check if API key is configured
CONFIGURED=$(echo "$STATUS_RESPONSE" | jq -r '.configured // false' 2>/dev/null || echo "false")
ENABLED=$(echo "$STATUS_RESPONSE" | jq -r '.enabled // false' 2>/dev/null || echo "false")

if [ "$CONFIGURED" = "true" ]; then
    echo -e "${GREEN}✅ API key is configured${NC}"
else
    echo -e "${RED}❌ API key is NOT configured${NC}"
    echo "Please add CLAUDE_API_KEY to Railway environment variables"
    exit 1
fi

if [ "$ENABLED" = "true" ]; then
    echo -e "${GREEN}✅ Claude AI is enabled${NC}"
else
    echo -e "${YELLOW}⚠️  Claude AI is configured but disabled${NC}"
    echo "Check API key format - should start with 'sk-ant-' and be 50+ characters"
fi
echo ""

# Test 3: Run comprehensive diagnostic endpoint
echo -e "${YELLOW}[TEST 3] Running comprehensive Claude AI diagnostic...${NC}"
DIAGNOSTIC_RESPONSE=$(curl -s "${RAILWAY_URL}/api/test/claude-ai")
echo "$DIAGNOSTIC_RESPONSE" | jq '.' 2>/dev/null || echo "$DIAGNOSTIC_RESPONSE"
echo ""

# Parse diagnostic results
ENV_TEST=$(echo "$DIAGNOSTIC_RESPONSE" | jq -r '.test_results.environment.api_key_to_use // "UNKNOWN"' 2>/dev/null || echo "UNKNOWN")
IMPORT_TEST=$(echo "$DIAGNOSTIC_RESPONSE" | jq -r '.test_results.import.success // false' 2>/dev/null || echo "false")
INIT_TEST=$(echo "$DIAGNOSTIC_RESPONSE" | jq -r '.test_results.initialization.success // false' 2>/dev/null || echo "false")
API_TEST=$(echo "$DIAGNOSTIC_RESPONSE" | jq -r '.test_results.api_call.success // false' 2>/dev/null || echo "false")

# Display results
echo -e "${BLUE}Diagnostic Results:${NC}"
echo -e "  Environment: ${ENV_TEST}"
echo -e "  Import: $([ "$IMPORT_TEST" = "true" ] && echo -e "${GREEN}✅${NC}" || echo -e "${RED}❌${NC}")"
echo -e "  Initialization: $([ "$INIT_TEST" = "true" ] && echo -e "${GREEN}✅${NC}" || echo -e "${RED}❌${NC}")"
echo -e "  API Call: $([ "$API_TEST" = "true" ] && echo -e "${GREEN}✅${NC}" || echo -e "${RED}❌${NC}")"
echo ""

# Test 4: Check response details
if [ "$API_TEST" = "true" ]; then
    RESPONSE_LENGTH=$(echo "$DIAGNOSTIC_RESPONSE" | jq -r '.test_results.api_call.response_length // 0' 2>/dev/null || echo "0")
    RESPONSE_PREVIEW=$(echo "$DIAGNOSTIC_RESPONSE" | jq -r '.test_results.api_call.response_preview // ""' 2>/dev/null || echo "")
    
    if [ "$RESPONSE_LENGTH" -gt 0 ]; then
        echo -e "${GREEN}✅ API returned ${RESPONSE_LENGTH} characters${NC}"
        if [ -n "$RESPONSE_PREVIEW" ]; then
            echo -e "${BLUE}Response preview:${NC}"
            echo "$RESPONSE_PREVIEW" | head -5
        fi
    else
        echo -e "${YELLOW}⚠️  API call succeeded but returned empty response${NC}"
        echo "Check Railway logs for '[_call_claude]' messages"
    fi
fi
echo ""

# Summary
echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}Summary${NC}"
echo -e "${BLUE}========================================${NC}"

if [ "$API_TEST" = "true" ] && [ "$RESPONSE_LENGTH" -gt 0 ]; then
    echo -e "${GREEN}✅ All tests passed! Claude AI is working correctly.${NC}"
    exit 0
elif [ "$API_TEST" = "true" ] && [ "$RESPONSE_LENGTH" -eq 0 ]; then
    echo -e "${YELLOW}⚠️  API call works but returns empty response.${NC}"
    echo "Check Railway logs for response parsing issues."
    exit 1
else
    echo -e "${RED}❌ Some tests failed. Check the diagnostic output above.${NC}"
    exit 1
fi

