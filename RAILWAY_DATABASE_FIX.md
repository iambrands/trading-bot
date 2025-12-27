# Railway Database Connection Issue - Sign-In Failing

## Problem
Sign-in returns "Invalid email or password" even though:
- ✅ Password hash is correct in database
- ✅ Password verification works when tested directly
- ✅ User exists in Railway database

This suggests Railway app isn't connecting to the database correctly.

## Most Likely Cause

Railway's app service needs to have `DATABASE_URL` environment variable set, pointing to the PostgreSQL service.

## Fix Steps

### Step 1: Verify DATABASE_URL is Set

1. Go to Railway Dashboard
2. Select your **app service** (web-production-f8308)
3. Go to **"Variables"** tab
4. Check if `DATABASE_URL` exists

### Step 2: If DATABASE_URL is Missing

**Option A: Railway Auto-Link (Recommended)**
1. In Railway project, both services (app + PostgreSQL) should be visible
2. Railway automatically shares variables between linked services
3. If not linked, manually add DATABASE_URL:
   - Go to app service → Variables
   - Click "Reference Variable"
   - Select PostgreSQL service → DATABASE_URL

**Option B: Manual Setup**
1. Go to PostgreSQL service → Variables
2. Copy the `DATABASE_URL` value
3. Go to app service → Variables
4. Add new variable:
   - Name: `DATABASE_URL`
   - Value: (paste the copied value)

### Step 3: Use Public Connection String

Make sure DATABASE_URL uses the **public** connection string:
```
postgresql://postgres:password@ballast.proxy.rlwy.net:22003/railway
```

NOT the internal one:
```
postgresql://postgres:password@postgres.railway.internal:5432/railway
```

### Step 4: Redeploy

After adding/updating DATABASE_URL:
- Railway will automatically redeploy
- Wait for deployment to complete
- Try signing in again

## Verify It's Working

Check Railway logs after redeploy:
1. Railway Dashboard → App Service → Deployments → Latest → View Logs
2. Look for: "Database initialized successfully"
3. Should NOT see: "Database initialization failed"

## Still Not Working?

If DATABASE_URL is set correctly and sign-in still fails:
1. Check Railway logs for database errors
2. Verify PostgreSQL service is running
3. Try the sign-in again after ensuring DATABASE_URL is correct

