# Debug AI Endpoint Not Being Called

## Issue
No `[AI_ANALYZE_MARKET]` or `[_call_openai]` logs appear in Railway, suggesting the endpoint is not being called.

## Possible Causes

### 1. Frontend Not Calling the Endpoint
- Check browser console (F12) for errors
- Check Network tab to see if `/api/ai/analyze-market` request is being made
- Check if request is being blocked (CORS, auth, etc.)

### 2. Endpoint Route Not Registered
- The route should be: `POST /api/ai/analyze-market`
- Check Railway startup logs for "REGISTERED ROUTES" section
- Look for: `POST /api/ai/analyze-market`

### 3. Authentication Blocking Request
- The endpoint requires authentication
- Check if user is logged in
- Check if auth token is being sent in request

### 4. Frontend JavaScript Error
- Check browser console for JavaScript errors
- The `getAIAnalysis()` function might be failing silently

## How to Debug

### Step 1: Check Browser Console
1. Open Market Conditions page
2. Press F12 to open Developer Tools
3. Go to Console tab
4. Look for:
   - Errors when page loads
   - Errors when AI analysis should trigger
   - Any messages about API calls

### Step 2: Check Network Tab
1. Open Developer Tools (F12)
2. Go to Network tab
3. Filter by "analyze-market"
4. Reload Market Conditions page
5. Check if request appears:
   - If YES: Check response status and body
   - If NO: Frontend is not calling the endpoint

### Step 3: Check Railway Logs
After the fix is deployed, you should see:
```
[AI_ANALYZE_MARKET] ENDPOINT CALLED
[AI_ANALYZE_MARKET] Timestamp: ...
[AI_ANALYZE_MARKET] Attempting to import OpenAIAnalyst...
[AI_ANALYZE_MARKET] ✅ OpenAIAnalyst imported successfully
```

If you don't see these logs, the endpoint is not being called.

### Step 4: Manual Test
Test the endpoint directly:
```bash
# Get auth token first (from browser localStorage)
# Then test:
curl -X POST https://web-production-f8308.up.railway.app/api/ai/analyze-market \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -d '{"market_data": {"BTC-USD": {"price": 92571}}, "trading_signals": {}}'
```

## Expected Behavior

When the Market Conditions page loads:
1. `updateMarketConditions()` is called
2. `getAIAnalysis()` is called after 500ms delay
3. Frontend makes POST request to `/api/ai/analyze-market`
4. Backend logs `[AI_ANALYZE_MARKET] ENDPOINT CALLED`
5. Backend calls OpenAI API
6. Backend logs `[_call_openai] STARTING OPENAI API CALL`
7. Response is returned to frontend

## Next Steps

1. Check browser console for errors
2. Check Network tab for the API request
3. Share what you find so we can fix the issue

