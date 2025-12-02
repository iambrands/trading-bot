# Deployment Instructions - Cache Fix

## Files Modified

The following files have been changed to fix the 404 errors for hashed CSS/JS files:

### Backend Changes
1. **`api/rest_api.py`**
   - Added `_setup_static_blocker()` method to block hashed file requests
   - Added cache-control headers to all HTML file responses
   - Modified `__init__` to call static blocker setup

### Frontend Changes
2. **`static/dashboard.html`**
   - Added aggressive cache-clearing script at the top of `<head>`
   - Clears all caches and unregisters service workers on page load

3. **`static/landing.html`**
   - Added aggressive cache-clearing script at the top of `<head>`

4. **`static/signin.html`**
   - Added aggressive cache-clearing script at the top of `<head>`

5. **`static/service-worker.js`**
   - Updated cache version from `v1` to `v2-2024-12`
   - Enhanced cache clearing logic
   - Added blocking for hashed file requests

### Documentation
6. **`CACHE_FIX_STATUS.md`** (new file)
   - Complete documentation of the fixes

7. **`DEPLOY_INSTRUCTIONS.md`** (this file)
   - Deployment instructions

## Steps to Deploy

### Step 1: Commit Changes to Git

```bash
# If not already a git repository, initialize it
git init

# Add all changed files
git add api/rest_api.py
git add static/dashboard.html
git add static/landing.html
git add static/signin.html
git add static/service-worker.js
git add CACHE_FIX_STATUS.md
git add DEPLOY_INSTRUCTIONS.md

# Commit the changes
git commit -m "Fix: Block hashed CSS/JS file requests and add aggressive cache clearing

- Add server-side middleware to block hashed file requests
- Add cache-clearing scripts to HTML files
- Update service worker to v2-2024-12
- Add cache-control headers to prevent HTML caching
- Fixes 404 errors for main.3e5d15db.css and main.a71a8271.js"
```

### Step 2: Push to GitHub

```bash
# If you don't have a remote yet, add it
git remote add origin https://github.com/iambrands/trading-bot.git

# Or if remote already exists, verify it
git remote -v

# Push to GitHub
git push -u origin main
# OR if your branch is called 'master'
git push -u origin master
```

**Quick Option**: Run the automated script:
```bash
./setup-git-and-deploy.sh
```

This script will:
- Initialize git (if needed)
- Set up the GitHub remote
- Stage and commit the changes
- Push to GitHub (with your confirmation)

### Step 3: Deploy to Heroku

If Heroku is configured to auto-deploy from GitHub:

1. Go to your Heroku dashboard
2. Select your app
3. Go to "Deploy" tab
4. If GitHub is connected, click "Deploy Branch"
5. Wait for deployment to complete

OR deploy manually via Heroku CLI:

```bash
# Install Heroku CLI if not already installed
# Then login
heroku login

# Add Heroku remote if not already added
heroku git:remote -a <your-heroku-app-name>

# Push to Heroku
git push heroku main
# OR
git push heroku master
```

### Step 4: Verify Deployment

After deployment:

1. **Clear your browser cache**:
   - Press `Ctrl+Shift+Delete` (Windows/Linux) or `Cmd+Shift+Delete` (Mac)
   - Select "Cached images and files"
   - Select "All time"
   - Click "Clear data"

2. **Hard refresh the page**:
   - `Ctrl+Shift+R` (Windows/Linux) or `Cmd+Shift+R` (Mac)

3. **Check the console**:
   - Open DevTools (F12)
   - Look for cache-clearing messages
   - Verify no 404 errors for hashed files

## Expected Behavior After Deployment

✅ No more 404 errors for `main.3e5d15db.css` or `main.a71a8271.js`
✅ Cache-clearing messages in console on page load
✅ Service worker updates to v2-2024-12
✅ All old caches cleared automatically

## Troubleshooting

If errors persist after deployment:

1. **Check Heroku logs**:
   ```bash
   heroku logs --tail -a <your-app-name>
   ```

2. **Clear browser cache completely** (see Step 4)

3. **Unregister service worker manually**:
   - Open DevTools (F12)
   - Go to Application tab → Service Workers
   - Click "Unregister"

4. **Try incognito/private window** to test without cache

## Quick Deployment Commands

If you already have git and Heroku set up:

```bash
# Quick commit and push
git add -A
git commit -m "Fix cache 404 errors"
git push origin main

# Deploy to Heroku (if auto-deploy is disabled)
git push heroku main
```

---

**Note**: I cannot deploy to GitHub or Heroku for you. You'll need to run these commands yourself or use your deployment interface.

