# Claude AI Key Troubleshooting Guide

## Issue: "AI Analysis Not Available" Error

If you're seeing "AI analysis failed. Please check your CLAUDE_API_KEY configuration" even though it previously worked, this is usually an environment variable issue on Railway.

## Quick Diagnostic Steps

### Step 1: Check AI Status Endpoint

Use the diagnostic endpoint to see the exact status:

```bash
curl "https://web-production-f8308.up.railway.app/api/ai/status" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

This will show:
- Whether the key is detected
- Key length
- If it's considered valid

### Step 2: Verify Railway Environment Variable

1. Go to Railway Dashboard: https://railway.app/dashboard
2. Select your project/service
3. Go to **Variables** tab
4. Look for `CLAUDE_API_KEY`
5. Check if:
   - ✅ It exists
   - ✅ It's not empty
   - ✅ It doesn't have quotes around it (should be: `sk-ant-api03-...` NOT `"sk-ant-api03-..."`)
   - ✅ No extra spaces before/after

### Step 3: Common Issues & Fixes

#### Issue 1: Variable Missing or Deleted
**Symptom**: Variable doesn't exist in Railway
**Fix**: Add it back:
1. Go to Railway → Your Service → Variables
2. Click "New Variable"
3. Name: `CLAUDE_API_KEY`
4. Value: Your actual key (without quotes)
5. Click "Add"
6. Railway will auto-redeploy

#### Issue 2: Quotes Around the Value
**Symptom**: Variable exists but has quotes like `"sk-ant-api03-..."`
**Fix**: Remove the quotes:
1. Edit the variable
2. Remove the quotes (should be: `sk-ant-api03-...`)
3. Save
4. Railway will auto-redeploy

#### Issue 3: Extra Spaces
**Symptom**: Key has leading/trailing spaces
**Fix**: The code strips spaces, but to be safe:
1. Edit the variable
2. Remove any spaces before/after the key
3. Save

#### Issue 4: Key Expired or Revoked
**Symptom**: Key exists but API calls fail
**Fix**: Generate a new key:
1. Go to https://console.anthropic.com/settings/keys
2. Create a new API key
3. Update the Railway variable with the new key
4. Railway will auto-redeploy

#### Issue 5: Recent Deployment Reset Variables
**Symptom**: Variables were lost after a deployment
**Fix**: Re-add the variable (see Issue 1)

## Step 4: Verify the Fix

After updating the variable in Railway:

1. **Wait for redeployment** (usually 1-2 minutes)
2. **Check the diagnostic endpoint again**:
   ```bash
   curl "https://web-production-f8308.up.railway.app/api/ai/status"
   ```
3. **Try the AI Analysis page again** in the browser
4. **Check Railway logs** if it still doesn't work:
   - Railway Dashboard → Your Service → Deployments → Latest → Logs
   - Look for errors related to `CLAUDE_API_KEY`

## Your Claude API Key Format

Your key should look like:
```
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
```

**Important**: 
- NO quotes around it
- NO spaces before/after
- Starts with `sk-ant-api03-`
- Usually 100+ characters long

## Quick Test

After updating, you can test immediately:

```bash
# Test the AI status endpoint
curl "https://web-production-f8308.up.railway.app/api/ai/status" \
  -H "Authorization: Bearer YOUR_TOKEN" | jq

# Should return:
# {
#   "configured": true,
#   "enabled": true,
#   "key_length": 115,
#   "model": "claude-3-haiku-20240307"
# }
```

## Still Not Working?

If it's still not working after following these steps:

1. **Check Railway Logs** for errors
2. **Verify the key is valid** at https://console.anthropic.com
3. **Try creating a fresh key** and updating Railway
4. **Check if Railway auto-redeployed** after variable changes

