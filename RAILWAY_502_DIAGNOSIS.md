# Railway 502 Bad Gateway - Diagnosis & Fix

## Issue
- Trading bot is running (heartbeats visible in logs)
- Web server is NOT responding (502 Bad Gateway on all API endpoints)
- No web server startup logs visible in Railway

## Possible Causes

### 1. **Log Filtering**
Railway may be filtering out startup logs. Check:
- **Build Logs** tab - look for Python startup messages
- **Deploy Logs** tab - should show web server startup
- **HTTP Logs** tab - shows incoming requests

### 2. **Web Server Not Starting**
The web server might be crashing silently after bot starts. Check if you see:
- `✅✅✅ TCPSite started successfully!`
- `✅✅✅ TRADEPILOT IS READY`

### 3. **Port Binding Issue**
Railway might not be able to bind to the PORT. Check:
- Railway's `PORT` environment variable is set
- Server is binding to `0.0.0.0` (not `localhost` or `127.0.0.1`)

## Diagnosis Steps

### Step 1: Check All Log Tabs
In Railway dashboard, check:
1. **Build Logs** - Look for Python startup
2. **Deploy Logs** - Look for `run_api()` and `TCPSite started`
3. **HTTP Logs** - See if requests are reaching the server

### Step 2: Verify Startup Command
Railway should be running: `python app.py`

Check in Railway Settings → Deploy:
- Start Command: `python app.py`

### Step 3: Test Health Endpoint
Try accessing directly (if you can):
```bash
curl https://web-production-f8308.up.railway.app/api/status
```

### Step 4: Check Port Configuration
Verify Railway's PORT environment variable:
- Go to Variables tab
- Check if `PORT` is set (Railway sets this automatically)
- Server should bind to `0.0.0.0:${PORT}`

## Fix Applied

Enhanced logging in `app.py` and `api/rest_api.py`:
- ✅ More verbose startup logging
- ✅ Error handling for port binding
- ✅ Verification that server actually starts
- ✅ Changed wait loop to use `sleep()` instead of `Event().wait()`

## Next Steps After Redeploy

1. **Check Deploy Logs** for:
   ```
   ============================================================
   TRADEPILOT BOOT SEQUENCE
   ============================================================
   Step 1: Importing standard library...
   ...
   run_api() CALLED
   ✅✅✅ TCPSite started successfully!
   ✅✅✅ TRADEPILOT IS READY
   ```

2. **If logs show server starting but 502 persists:**
   - Check Railway's networking/port forwarding
   - Verify Railway health check endpoint
   - Check if Railway expects a different response format

3. **If no startup logs at all:**
   - Railway might be using a different entry point
   - Check `railway.json` startCommand
   - Verify Dockerfile CMD is correct

## Temporary Workaround

If the issue persists, try:
1. **Restart Railway service** - Sometimes fixes port binding issues
2. **Redeploy from scratch** - Creates a fresh container
3. **Check Railway status page** - See if there are known issues

---

**Last Updated**: January 18, 2026
**Status**: Enhanced logging deployed, awaiting redeploy to diagnose

