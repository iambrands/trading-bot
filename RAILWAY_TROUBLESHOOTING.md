# Railway Connection Troubleshooting

## Common Errors & Solutions

### Error 1: "Repository not found" or "Could not connect to repository"

**Causes:**
- Repository is private and Railway doesn't have access
- Wrong repository name/URL
- GitHub permissions not granted

**Solutions:**
1. Check repository visibility:
   - Go to https://github.com/iambrands/trading-bot/settings
   - Ensure Railway has been granted access

2. Re-authorize Railway:
   - In Railway dashboard → Settings → Integrations
   - Disconnect GitHub, then reconnect
   - Grant Railway access to `iambrands/trading-bot`

3. Verify repository URL:
   - Should be: `iambrands/trading-bot`
   - Check it's the correct owner/organization

### Error 2: "Build failed" or "Deployment failed"

**Causes:**
- Missing required files (requirements.txt, app.py)
- Syntax errors in code
- Uncommitted changes not pushed to GitHub

**Solutions:**

1. **Commit and push recent changes:**
```bash
cd /Users/iabadvisors/TradingBot
git add railway.json config.py RAILWAY_*.md QUICK_RAILWAY_START.md .railwayignore
git commit -m "Add Railway deployment configuration and DATABASE_URL support"
git push origin main
```

2. **Verify required files exist:**
   - ✅ `requirements.txt` - Should be present
   - ✅ `app.py` - Entry point (Railway auto-detects)
   - ✅ `config.py` - Configuration (should work)

3. **Check for syntax errors:**
```bash
python3 -m py_compile app.py config.py
```

### Error 3: "No buildpack detected" or "Cannot detect application type"

**Solutions:**
1. Railway should auto-detect Python - if not, ensure:
   - `requirements.txt` exists in root
   - `app.py` exists in root

2. Manually specify build command (if needed):
   - In Railway → Service → Settings → Build Command
   - Set to: `pip install -r requirements.txt`

3. Or create `nixpacks.toml`:
```toml
[phases.setup]
nixPkgs = ['python39']

[phases.install]
cmds = ['pip install -r requirements.txt']

[start]
cmd = 'python app.py'
```

### Error 4: "Port not exposed" or "Application failed to start"

**Solutions:**
1. Ensure `app.py` uses `PORT` environment variable:
```python
port = int(os.environ.get('PORT', 4000))
```
✅ Your `app.py` already does this correctly!

2. Railway automatically sets `PORT` - your app should use it

### Error 5: "Database connection failed"

**Solutions:**
1. Ensure PostgreSQL service is added in Railway
2. Railway automatically sets `DATABASE_URL`
3. Your `config.py` now supports `DATABASE_URL` format
4. If using individual variables, set them in Railway → Variables:
   - `DB_HOST`
   - `DB_PORT`
   - `DB_NAME`
   - `DB_USER`
   - `DB_PASSWORD`

### Error 6: "Module not found" during build

**Solutions:**
1. Check `requirements.txt` has all dependencies:
   ```bash
   cat requirements.txt
   ```
   
2. If missing dependencies, add them:
   ```bash
   pip freeze > requirements.txt
   ```

3. Ensure no version conflicts

## Step-by-Step Connection Process

1. **In Railway Dashboard:**
   - Click "New Project"
   - Select "Deploy from GitHub repo"
   - Search for: `trading-bot`
   - Select: `iambrands/trading-bot`

2. **If repository doesn't appear:**
   - Click "Configure GitHub App"
   - Grant Railway access to your repositories
   - Select "All repositories" or specific repo
   - Re-try connecting

3. **After connection:**
   - Railway will automatically:
     - Detect Python app
     - Run `pip install -r requirements.txt`
     - Run `python app.py`
   - Check "Deployments" tab for status
   - Check "Logs" tab if build fails

## Verify Repository is Ready

Before connecting to Railway, ensure:

```bash
# 1. Repository is up to date
git status
git push origin main  # Push any local changes

# 2. Required files exist
ls -la requirements.txt app.py config.py

# 3. No syntax errors
python3 -m py_compile app.py config.py

# 4. Repository is accessible
# Visit: https://github.com/iambrands/trading-bot
# Ensure it's accessible (not private to Railway's account)
```

## Still Having Issues?

If you're still getting errors:

1. **Share the exact error message** from Railway logs
2. **Check Railway logs:**
   - Service → Deployments → Click latest deployment → View logs
3. **Check build logs:**
   - Look for specific Python/package errors
4. **Verify GitHub connection:**
   - Railway → Settings → Integrations → GitHub
   - Ensure connection is active

## Quick Test Locally First

Test that everything works locally before deploying:

```bash
# Set environment variables
export PORT=4000
export DATABASE_URL="postgresql://user:pass@localhost:5432/dbname"

# Or set individual DB vars
export DB_HOST=localhost
export DB_PORT=5432
export DB_NAME=tradingbot
export DB_USER=postgres
export DB_PASSWORD=yourpassword

# Test run
python app.py
```

If this works locally, Railway should work too!

