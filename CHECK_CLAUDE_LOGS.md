# How to Check Claude AI Logs in Railway

## Current Issue

The Market Conditions page shows:
> "AI analysis temporarily unavailable. The AI service responded but didn't generate analysis content."

This means:
- ✅ The endpoint is being called
- ✅ Claude API responds (HTTP 200)
- ❌ Response parsing returns None/empty

## Where to Find Claude AI Logs

### Option 1: HTTP Logs (Recommended)

1. In Railway dashboard, click on your service
2. Go to **"Logs"** tab
3. Click **"HTTP Logs"** (separate from Deploy Logs)
4. Look for requests to `/api/ai/analyze-market`
5. Check the response status and any error messages

### Option 2: Filter Deploy Logs

1. In Railway dashboard, click on your service
2. Go to **"Logs"** tab → **"Deploy Logs"**
3. Use the search/filter box at the top
4. Search for: `[_call_claude]` or `[AI_ANALYZE_MARKET]`
5. These logs show:
   - When the endpoint is called
   - Claude API request details
   - Response structure
   - Parsing steps

### Option 3: Check Browser Console

1. Open Market Conditions page
2. Press **F12** to open Developer Tools
3. Go to **Console** tab
4. Look for:
   - `[getAIAnalysis] Function called`
   - `[getAIAnalysis] Response received: 200`
   - Any error messages

### Option 4: Test Diagnostic Endpoint

```bash
curl https://web-production-f8308.up.railway.app/api/test/claude-ai
```

This shows:
- API key configuration
- Import status
- Initialization status
- Test API call with response details

## What to Look For

In the logs, search for these patterns:

```
[_call_claude] STARTING CLAUDE API CALL
[_call_claude] Response keys: [...]
[_call_claude] Content type: ...
[_call_claude] Extracted from dict.text: ...
```

If you see:
- `response_is_none: true` → Parsing issue
- `No 'content' field in response` → Unexpected response structure
- `Content list is empty` → Empty content array

## Next Steps

1. **Trigger the AI Analysis:**
   - Open Market Conditions page in browser
   - The page should automatically call `/api/ai/analyze-market`
   - Or refresh the page to trigger it again

2. **Check Railway Logs Immediately After:**
   - Look in HTTP Logs for the POST request
   - Look in Deploy Logs for `[_call_claude]` messages
   - Copy any error messages or unusual response structures

3. **Share the Logs:**
   - Copy the relevant log entries (especially any `[_call_claude]` messages)
   - Share them so we can see the actual Claude API response structure
   - This will help fix the parsing logic

## Expected Log Flow

When AI analysis is triggered, you should see:

```
[AI_ANALYZE_MARKET] ENDPOINT CALLED
[AI_ANALYZE_MARKET] ✅ ClaudeAIAnalyst imported successfully
[_call_claude] STARTING CLAUDE API CALL
[_call_claude] Response keys: ['id', 'type', 'role', 'content', ...]
[_call_claude] Content type: <class 'list'>
[_call_claude] Content is list with 1 items
[_call_claude] First item keys: ['type', 'text']
[_call_claude] Extracted from dict.text: length=XXX
```

If any step is missing or shows errors, that's where the issue is.

