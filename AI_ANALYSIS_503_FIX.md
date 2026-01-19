# AI Analysis 503 Error - Fix & Troubleshooting Guide

## Issue
The AI Analysis feature is returning a `503 Service Unavailable` error on the Market Conditions page.

**Error Message**: `api/ai/analyze-market:1 Failed to load resource: the server responded with a status of 503 ()`

## Fix Applied

Enhanced error handling and diagnostics in `api/rest_api.py`:
- Better API key validation (strips quotes and whitespace)
- More detailed error messages
- Enhanced logging for debugging
- Improved exception handling for JSON parsing and API calls

## Troubleshooting Steps

### Step 1: Check AI Status Endpoint

First, verify the current AI configuration status:

```bash
curl https://your-railway-url.up.railway.app/api/ai/status
```

Or visit in browser:
```
https://your-railway-url.up.railway.app/api/ai/status
```

This will show:
- `configured`: Whether the key exists
- `enabled`: Whether the AI analyst is enabled
- `key_length`: Length of the API key
- `diagnostic`: Detailed diagnostic information

### Step 2: Verify Railway Environment Variables

1. Go to your Railway project dashboard
2. Navigate to **Variables** tab
3. Look for `CLAUDE_API_KEY`
4. Check that:
   - ✅ The variable exists
   - ✅ The value starts with `sk-ant-` (Claude API keys start with this prefix)
   - ✅ The value is **NOT wrapped in quotes** (e.g., `sk-ant-...` not `"sk-ant-..."`)
   - ✅ There's no extra whitespace
   - ✅ The key is at least 50+ characters long

### Step 3: Common Issues & Solutions

#### Issue 1: Key Not Set
**Symptoms**: `configured: false` in `/api/ai/status`

**Solution**:
1. Get a Claude API key from https://console.anthropic.com/
2. Add it to Railway:
   - Variable name: `CLAUDE_API_KEY`
   - Variable value: `sk-ant-api03-...` (your full key, no quotes)
3. Redeploy the application

#### Issue 2: Key Has Quotes
**Symptoms**: `configured: true` but `enabled: false`

**Solution**:
1. Remove quotes from the Railway variable value
2. Should be: `sk-ant-api03-...`
3. NOT: `"sk-ant-api03-..."`
4. Redeploy after fixing

#### Issue 3: Key Too Short
**Symptoms**: `key_length: 10` or less

**Solution**:
- Valid Claude API keys are typically 50+ characters
- Get a new key from Anthropic Console
- Ensure you copy the **entire key**

#### Issue 4: Invalid Key Format
**Symptoms**: `enabled: false` despite valid length

**Solution**:
- Claude API keys start with `sk-ant-api03-` or `sk-ant-api04-`
- If your key doesn't start with `sk-ant-`, it's invalid
- Get a new key from Anthropic Console

#### Issue 5: Key Expired/Revoked
**Symptoms**: `enabled: true` but API calls fail with 401/403

**Solution**:
1. Go to https://console.anthropic.com/
2. Check if your API key is still active
3. Create a new key if needed
4. Update Railway variable and redeploy

### Step 4: Check Railway Logs

After redeploying, check Railway logs for diagnostic messages:

```bash
# Look for these log messages:
[AI_ANALYZE_MARKET] API key check: exists=True, length=XX
[AI_ANALYZE_MARKET] ClaudeAIAnalyst enabled: True/False
[AI_ANALYZE_MARKET] ✅ Analysis successful
[AI_ANALYZE_MARKET] ❌ [error message]
```

### Step 5: Test the Endpoint Directly

Test the endpoint with curl:

```bash
curl -X POST https://your-railway-url.up.railway.app/api/ai/analyze-market \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_AUTH_TOKEN" \
  -d '{
    "market_data": {"test": "data"},
    "trading_signals": {"test": "signals"}
  }'
```

## Error Messages Explained

### "CLAUDE_API_KEY is not configured or is empty"
- **Cause**: The environment variable doesn't exist or is empty
- **Fix**: Add `CLAUDE_API_KEY` to Railway variables

### "CLAUDE_API_KEY appears to be invalid"
- **Cause**: Key exists but is too short or wrong format
- **Fix**: Verify key starts with `sk-ant-` and is 50+ characters

### "Invalid API key. Please check your CLAUDE_API_KEY"
- **Cause**: Anthropic API rejected the key (wrong key, expired, revoked)
- **Fix**: Generate a new key from Anthropic Console

### "Rate limit exceeded"
- **Cause**: Too many API requests
- **Fix**: Wait a few minutes and try again

## Quick Fix Checklist

- [ ] Check `/api/ai/status` endpoint for diagnostics
- [ ] Verify `CLAUDE_API_KEY` exists in Railway variables
- [ ] Ensure key value has **NO quotes** around it
- [ ] Verify key starts with `sk-ant-` and is 50+ characters
- [ ] Redeploy Railway application after any changes
- [ ] Check Railway logs for error messages
- [ ] Try generating a new API key if old one doesn't work

## Testing After Fix

1. Wait for Railway deployment to complete
2. Visit Market Conditions page
3. Click "Get AI Analysis" button
4. Should see AI analysis instead of error message

## Still Not Working?

If the issue persists after following these steps:

1. Check Railway logs for detailed error messages
2. Verify the `/api/ai/status` endpoint response
3. Try creating a brand new Claude API key
4. Ensure Railway deployment completed successfully
5. Clear browser cache and try again

## Notes

- The AI Analysis feature is **optional** - TradePilot works without it
- All other features continue to work even if AI is disabled
- The enhanced error messages now provide specific guidance for each error type

---

**Last Updated**: December 2025  
**Related Files**: `api/rest_api.py`, `ai/claude_ai.py`, `config.py`

