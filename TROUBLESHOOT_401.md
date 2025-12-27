# Troubleshooting 401 Unauthorized Error

## What the 401 Error Means

A 401 error means "Unauthorized" - the server is rejecting your authentication request. This can happen for several reasons:

## Common Causes & Solutions

### 1. JWT_SECRET_KEY Not Set or Incorrect

**Check:**
- Railway Dashboard → Your Service → Variables tab
- Ensure `JWT_SECRET_KEY` is set to: `xvNNDx-G3scNpANLA0d-UcS5tXYFbxkvc3Sq5TvLpGQ`
- Railway must redeploy after adding/updating this variable

**Fix:**
- Add/update JWT_SECRET_KEY in Railway
- Wait for redeployment
- Try again

### 2. Sign-In Failed (Wrong Password or Email)

**Check:**
- Make sure you're using the correct email: `leslie.wilson@gmail.com`
- Make sure you're using the correct password: `CoolGeek56$`
- Check browser console for error messages

**Fix:**
- Double-check credentials
- Try signing in again
- If password doesn't work, we may need to reset it

### 3. Token Not Being Stored (Browser Issues)

**Check:**
- Open browser DevTools (F12)
- Go to Application/Storage → Cookies
- Check if `auth_token` cookie is set after sign-in

**Fix:**
- Clear browser cache and cookies
- Try incognito/private browsing mode
- Try a different browser

### 4. Database Connection Issue

**Check:**
- Railway Dashboard → Your Service → Logs
- Look for database connection errors

**Fix:**
- Verify PostgreSQL database is running
- Check DATABASE_URL is set correctly

## Diagnostic Steps

1. **Check Railway Logs:**
   - Go to Railway Dashboard → Your Service → Deployments → Latest → View Logs
   - Look for authentication errors or database errors

2. **Test Sign-In Directly:**
   ```bash
   curl -X POST https://web-production-f8308.up.railway.app/api/auth/signin \
     -H "Content-Type: application/json" \
     -d '{"email":"leslie.wilson@gmail.com","password":"CoolGeek56$"}'
   ```

3. **Check Browser Console:**
   - Open DevTools (F12)
   - Go to Console tab
   - Look for error messages
   - Go to Network tab to see which request is returning 401

## Next Steps

If you're still getting 401:
1. Share the exact error message from browser console
2. Share Railway logs showing the error
3. Let me know which page/endpoint is returning 401

