# Claude AI Diagnostic Test Scripts

## Overview
These scripts test the Claude AI integration on your Railway deployment to diagnose issues with the AI Analysis feature.

## Prerequisites
- Railway deployment is running
- `CLAUDE_API_KEY` is set in Railway environment variables (or configured locally)

## Scripts

### 1. Bash Script: `test_claude_diagnostics.sh`
Simple bash script that uses `curl` and `jq` (optional).

**Usage:**
```bash
# Use default Railway URL
./test_claude_diagnostics.sh

# Or specify custom URL
RAILWAY_URL=https://your-app.up.railway.app ./test_claude_diagnostics.sh
```

**Requirements:**
- `curl` (usually pre-installed)
- `jq` (optional, for JSON formatting - install with `brew install jq` on macOS)

### 2. Python Script: `test_claude_diagnostics.py`
More robust Python script with better error handling.

**Usage:**
```bash
# Use default Railway URL
python3 test_claude_diagnostics.py

# Or specify custom URL
RAILWAY_URL=https://your-app.up.railway.app python3 test_claude_diagnostics.py
```

**Requirements:**
- Python 3.6+
- `requests` library (install with `pip install requests`)

## What the Tests Check

### Test 1: Server Connectivity
- Verifies the Railway server is reachable
- Tests `/api/status` endpoint

### Test 2: AI Status
- Checks `/api/ai/status` endpoint
- Verifies `CLAUDE_API_KEY` is configured
- Checks if Claude AI is enabled

### Test 3: Comprehensive Diagnostic
- Tests `/api/test/claude-ai` endpoint
- Runs through all diagnostic checks:
  1. **Environment Variables** - API key detection
  2. **Module Import** - Can import `ClaudeAIAnalyst`
  3. **Initialization** - Can create instance
  4. **API Call** - Makes actual test call to Claude API
  5. **Response Parsing** - Verifies response can be extracted

## Expected Output

### Success Case:
```
✅ Server is reachable
✅ API key is configured
✅ Claude AI is enabled
✅ Import: ✅
✅ Initialization: ✅
✅ API Call: ✅
✅ API returned 500 characters
```

### Failure Cases:

**No API Key:**
```
❌ API key is NOT configured
Please add CLAUDE_API_KEY to Railway environment variables
```

**Empty Response:**
```
✅ API Call: ✅
⚠️  API call succeeded but returned empty response
Check Railway logs for '[_call_claude]' messages
```

**API Call Failed:**
```
❌ API Call: ❌
Check Railway logs for detailed error messages
```

## Troubleshooting

### If Server is Not Reachable:
1. Check Railway deployment status
2. Verify the URL is correct
3. Check if the service is healthy in Railway dashboard

### If API Key is Not Configured:
1. Go to Railway dashboard → Your service → Variables
2. Add `CLAUDE_API_KEY` (no quotes around the value)
3. Redeploy the service

### If API Returns Empty Response:
1. Check Railway logs for `[_call_claude]` messages
2. Visit `/api/test/claude-ai` in browser to see full diagnostic
3. Verify the API key format (should start with `sk-ant-`)

### If API Call Fails:
1. Check Railway logs for error messages
2. Verify API key is valid and not expired
3. Check Anthropic API status: https://status.anthropic.com/

## Manual Testing

You can also test the endpoints manually:

### 1. Check AI Status:
```bash
curl https://web-production-f8308.up.railway.app/api/ai/status
```

### 2. Run Full Diagnostic:
```bash
curl https://web-production-f8308.up.railway.app/api/test/claude-ai
```

### 3. Test in Browser:
Open these URLs in your browser:
- `https://web-production-f8308.up.railway.app/api/ai/status`
- `https://web-production-f8308.up.railway.app/api/test/claude-ai`

## Next Steps

After running the tests:
1. If all tests pass → Claude AI is working correctly
2. If tests fail → Check the error messages and Railway logs
3. Share the diagnostic output if you need help troubleshooting

## Integration with CI/CD

These scripts can be integrated into CI/CD pipelines:

```yaml
# Example GitHub Actions
- name: Test Claude AI
  run: |
    RAILWAY_URL=${{ secrets.RAILWAY_URL }} python3 test_claude_diagnostics.py
```

