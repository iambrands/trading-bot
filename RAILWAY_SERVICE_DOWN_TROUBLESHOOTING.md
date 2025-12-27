# Railway Service Not Accessible - Troubleshooting

If Railway shows your service as "online" but the browser won't load, follow these steps:

## Step 1: Check Railway Deployment Logs

1. Go to Railway → Your Project → Your Web Service
2. Click on **"Deployments"** tab
3. Click on the **latest deployment**
4. Check the **logs** for:
   - Startup errors
   - Port binding issues
   - Database connection failures
   - Any Python exceptions

**Look for:**
- `Starting API server on port 8080` (or whatever port Railway assigned)
- Any `ERROR` or `Exception` messages
- Database connection errors
- Import errors

## Step 2: Verify Public Domain is Configured

1. Go to Railway → Your Web Service → **Settings** tab
2. Scroll to **"Networking"** section
3. Check if **"Generate Domain"** is enabled
4. Note the public domain (should be something like `web-production-xxxx.up.railway.app`)

**If no domain is shown:**
- Click **"Generate Domain"** 
- Wait for it to be created
- Try accessing that domain

## Step 3: Check Service Health

1. Go to Railway → Your Web Service → **Metrics** tab
2. Check if:
   - CPU usage is normal (not 0% or 100%)
   - Memory usage is within limits
   - Requests are being received

## Step 4: Verify Port Binding

Your code should be using Railway's `PORT` environment variable. Check logs for:

```
Starting API server on port 8080
API server started on 0.0.0.0:8080
```

**If you see:**
- `Starting API server on port 4000` → Railway's PORT env var isn't being used
- `Starting API server on port None` → PORT env var isn't set

## Step 5: Test Direct API Endpoint

Try accessing these directly:

1. **Health check endpoint** (if you have one):
   ```
   https://your-railway-domain.up.railway.app/api/runtime
   ```

2. **Status endpoint**:
   ```
   https://your-railway-domain.up.railway.app/api/status
   ```

3. **Root endpoint**:
   ```
   https://your-railway-domain.up.railway.app/
   ```

**If these return 502/503/504:**
- Service might be crashing on startup
- Check logs for Python errors

**If these return 404:**
- Routes might not be registered correctly
- Check if service is actually running

## Step 6: Common Issues & Fixes

### Issue: Service crashes on startup

**Symptoms:** Logs show error then service restarts repeatedly

**Common causes:**
- Database connection failure (check `DATABASE_URL`)
- Missing environment variables
- Python import errors
- Port already in use

**Fix:** Check logs for the specific error and fix accordingly

### Issue: Service binds to wrong port

**Symptoms:** Logs show `Starting API server on port 4000` instead of Railway's port

**Fix:** Ensure your code uses `os.environ.get('PORT', ...)` (it should already do this)

### Issue: No public domain

**Symptoms:** Service is running but no URL to access it

**Fix:** 
1. Go to Settings → Networking
2. Click "Generate Domain"
3. Wait for domain to be created

### Issue: Service restarts repeatedly

**Symptoms:** Service status shows as "Restarting" or "Deploying"

**Fix:**
- Check logs for crash reasons
- Verify all required environment variables are set
- Check database connectivity

### Issue: "Bad Gateway" or "Service Unavailable"

**Symptoms:** Browser shows 502/503 error

**Possible causes:**
- Service crashed after startup
- Health check failing
- Service not binding to `0.0.0.0` (only `localhost`)

**Fix:** 
- Check logs for startup errors
- Ensure code binds to `0.0.0.0` not `127.0.0.1`

## Step 7: Manual Verification

If you have Railway CLI access, you can SSH into the container:

```bash
railway connect
railway shell
```

Then check:
```bash
# Check if Python process is running
ps aux | grep python

# Check if port is listening
netstat -tuln | grep :8080

# Check environment variables
env | grep PORT
```

## Quick Checklist

- [ ] Service status shows "Active" or "Deployed"
- [ ] Latest deployment logs show "API server started successfully"
- [ ] Public domain is configured and shows in Settings
- [ ] No errors in deployment logs
- [ ] PORT environment variable is set (Railway sets this automatically)
- [ ] Service binds to `0.0.0.0`, not `127.0.0.1`
- [ ] Database connection is working (check logs)
- [ ] All required environment variables are set

## If Still Not Working

1. **Redeploy the service:**
   - Go to Deployments tab
   - Click "Redeploy" on latest deployment

2. **Check Railway status page:**
   - https://status.railway.app/
   - See if Railway is experiencing issues

3. **Review recent code changes:**
   - Check if recent commits introduced breaking changes
   - Try reverting to a known working commit

4. **Check Railway community/support:**
   - Railway Discord: https://discord.gg/railway
   - Railway docs: https://docs.railway.app/


