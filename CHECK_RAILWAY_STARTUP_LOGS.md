# How to Check Railway Startup Logs

## The Issue
- Trading bot is running (heartbeats visible)
- Web server appears not to be responding (502 errors)
- Startup logs from `app.py` not visible

## Where to Look in Railway

### 1. **Build Logs Tab**
Shows the Docker build process. Look for:
- Python installation
- Dependencies installation
- Docker image creation

### 2. **Deploy Logs Tab** ⭐ MOST IMPORTANT
This shows the runtime logs. You should see:
```
============================================================
TRADEPILOT BOOT SEQUENCE
Python: 3.12.x
PORT env: 12345 (or similar)
============================================================
Step 1: Importing standard library...
  ✅ Standard library OK
Step 2: Importing aiohttp...
  ✅ aiohttp OK
...
run_api() CALLED
  ✅✅✅ TCPSite started successfully!
  ✅✅✅ Server is now listening on 0.0.0.0:12345
```

**IF YOU DON'T SEE THESE LOGS:**
- Railway might be filtering them
- The app might be crashing before reaching web server code
- Logs might be in a different stream

### 3. **HTTP Logs Tab**
Shows incoming HTTP requests. If you see:
- Requests appearing → Web server IS running
- No requests → Web server NOT responding

### 4. **Check All Three Tabs Together**
1. Build Logs → Should show successful build
2. Deploy Logs → Should show startup sequence
3. HTTP Logs → Should show incoming requests

## What to Check

### If Deploy Logs Show Trading Bot Only:
- The web server startup might be after the bot starts
- Scroll down in Deploy Logs to see if server logs appear later
- Check if there are errors that stop the server from starting

### If Deploy Logs Show Nothing:
- Railway might be using cached logs
- Try clicking "Refresh" or "Clear Logs"
- Check if Railway is showing "Filtered" or truncated logs

### If You See Errors:
Look for:
- `❌` symbols indicating failures
- `OSError` or `Exception` messages
- Port binding errors

## Quick Test

Try accessing these URLs directly:
1. `https://web-production-f8308.up.railway.app/api/status` - Should return JSON
2. `https://web-production-f8308.up.railway.app/` - Should redirect or show dashboard

If both return 502, the web server definitely isn't running.

## Next Steps

1. **Check Deploy Logs** - Scroll through ALL logs looking for startup messages
2. **Share the full Deploy Logs output** - Especially the beginning of the log stream
3. **Check Railway Settings** - Verify start command is `python app.py`

---

**Current Status**: Trading bot running, but web server startup logs not visible. Need to check Railway Deploy Logs tab to see full startup sequence.

