# Verify Railway Setup - Password Not Working

## The Problem
Password verification shows the password IS correct in the database, but sign-in is failing. This is likely a JWT_SECRET_KEY issue.

## Quick Fix

### Step 1: Verify JWT_SECRET_KEY is Set in Railway

1. Go to Railway Dashboard → Your Service (`web-production-f8308`)
2. Click "Variables" tab
3. Check if `JWT_SECRET_KEY` is set
4. If not, add it with the value: `xvNNDx-G3scNpANLA0d-UcS5tXYFbxkvc3Sq5TvLpGQ`
   (Or generate a new one if you prefer)

### Step 2: Redeploy After Adding Variable

After adding/updating JWT_SECRET_KEY:
- Railway will automatically redeploy
- Or manually trigger a redeploy

### Step 3: Try Sign-In Again

1. Visit: https://web-production-f8308.up.railway.app
2. Click "Sign In"
3. Enter:
   - Email: `leslie.wilson@gmail.com`
   - Password: `CoolGeek56$`

## Why This Happens

The password hash is correct, but JWT token generation/verification requires JWT_SECRET_KEY. If it's missing or different:
- Tokens can't be generated
- Tokens can't be verified
- Sign-in fails even with correct password

## Verify Everything is Set

Make sure these Railway variables are set:
- ✅ `JWT_SECRET_KEY` (CRITICAL - must be set)
- ✅ `DATABASE_URL` (auto-provided by Railway when you add PostgreSQL)
- ✅ `ENVIRONMENT=production` (optional but recommended)
- ✅ `PAPER_TRADING=true` (optional)

## Still Not Working?

If it still doesn't work after setting JWT_SECRET_KEY:
1. Check Railway logs for errors
2. Clear browser cache/cookies
3. Try in incognito/private browsing mode

