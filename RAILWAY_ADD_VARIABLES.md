# Add Required Variables to Railway App Service

## Required Variables

Your app service needs these variables to work:

1. **DATABASE_URL** - Connection to PostgreSQL database
2. **JWT_SECRET_KEY** - For authentication tokens

## Step-by-Step Instructions

### Step 1: Add DATABASE_URL

**Option A: Reference from PostgreSQL Service (Recommended)**

1. In Railway Dashboard, go to your **app service** (`web-production-f8308`)
2. Click **"Variables"** tab
3. Click **"+ New Variable"** or **"Add Variable"**
4. Look for **"Reference Variable"** or **"Link Variable"** option
5. Select your **PostgreSQL service**
6. Select **`DATABASE_URL`** from the list
7. Save

**Option B: Manual Entry**

1. Go to your **PostgreSQL service** → **Variables** tab
2. Find `DATABASE_URL` and copy its value
   - Should be: `postgresql://postgres:MRjbxvYzpOmvyQFmQsuWgcAToEyeCsnn@ballast.proxy.rlwy.net:22003/railway`
3. Go back to your **app service** → **Variables** tab
4. Click **"+ New Variable"**
5. Name: `DATABASE_URL`
6. Value: Paste the copied value
7. Save

### Step 2: Add JWT_SECRET_KEY

1. In your **app service** → **Variables** tab
2. Click **"+ New Variable"**
3. Name: `JWT_SECRET_KEY`
4. Value: `xvNNDx-G3scNpANLA0d-UcS5tXYFbxkvc3Sq5TvLpGQ`
5. Save

### Step 3: Optional Variables (Recommended)

Add these for better configuration:

1. **ENVIRONMENT**
   - Name: `ENVIRONMENT`
   - Value: `production`

2. **PAPER_TRADING**
   - Name: `PAPER_TRADING`
   - Value: `true`

3. **LOG_LEVEL**
   - Name: `LOG_LEVEL`
   - Value: `INFO`

## After Adding Variables

1. Railway will automatically redeploy your service
2. Wait for deployment to complete (check Deployments tab)
3. Check logs to see "Database initialized successfully"
4. Try signing in again!

## Verify Variables Are Set

After adding, your app service Variables tab should show:
- ✅ DATABASE_URL
- ✅ JWT_SECRET_KEY
- ✅ ENVIRONMENT (optional)
- ✅ PAPER_TRADING (optional)
- ✅ LOG_LEVEL (optional)

## Quick Copy-Paste Values

If you prefer to add manually, here are the exact values:

```
DATABASE_URL=postgresql://postgres:MRjbxvYzpOmvyQFmQsuWgcAToEyeCsnn@ballast.proxy.rlwy.net:22003/railway
JWT_SECRET_KEY=xvNNDx-G3scNpANLA0d-UcS5tXYFbxkvc3Sq5TvLpGQ
ENVIRONMENT=production
PAPER_TRADING=true
LOG_LEVEL=INFO
```

