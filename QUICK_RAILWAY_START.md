# Quick Railway Setup (5 Minutes)

## Step 1: Sign Up (1 min)
1. Go to https://railway.app
2. Click "Start a New Project"
3. Sign up with GitHub
4. Authorize Railway

## Step 2: Connect Repo (1 min)
1. Click "Deploy from GitHub repo"
2. Select: `iambrands/trading-bot`
3. Railway will detect it's a Python app automatically

## Step 3: Add Database (1 min)
1. In your project, click "+ New"
2. Select "Database" → "PostgreSQL"
3. Railway automatically creates and connects it

## Step 4: Set Variables (2 min)
Go to your service → "Variables" tab, add:

```bash
JWT_SECRET_KEY=<run: python -c "import secrets; print(secrets.token_urlsafe(32))">
ENVIRONMENT=production
PAPER_TRADING=true
```

Copy any other env vars from Heroku (COINBASE_API_KEY, etc.)

## Step 5: Deploy! (automatic)
- Railway auto-deploys when you connect repo
- Get your URL: `your-app.up.railway.app`
- Check logs: Click "View Logs" in Railway dashboard

## Done! 🎉

Your app is now running on Railway with:
- ✅ Auto-detected Python app
- ✅ PostgreSQL database connected
- ✅ Public URL provided
- ✅ SSL certificate included
- ✅ Real-time logs

**That's it!** Railway handles the rest automatically.

See `RAILWAY_DEPLOYMENT.md` for detailed guide.
