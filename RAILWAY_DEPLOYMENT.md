# Railway Deployment Guide

## Why Railway?

Railway is an excellent choice for this trading bot application because:

1. **Better Async Support**: Railway handles async Python applications (aiohttp) much better than Heroku
2. **Simpler Configuration**: No Procfile needed - Railway auto-detects Python apps
3. **Better Logging**: Built-in real-time logs with better formatting
4. **Database Integration**: Seamless PostgreSQL integration with automatic connection string
5. **More Stable**: Better handling of long-running processes and async connections
6. **Cost Effective**: Generous free tier + usage-based pricing
7. **Zero Config Deployment**: Just connect your GitHub repo and deploy

## Migration from Heroku to Railway

### Step 1: Create Railway Account & Project

1. Go to [railway.app](https://railway.app)
2. Sign up with GitHub
3. Click "New Project"
4. Select "Deploy from GitHub repo"
5. Choose your repository: `iambrands/trading-bot`

### Step 2: Add PostgreSQL Database

1. In your Railway project, click "+ New"
2. Select "Database" → "PostgreSQL"
3. Railway will automatically provision a PostgreSQL database
4. The `DATABASE_URL` environment variable will be automatically set

### Step 3: Configure Environment Variables

In Railway, go to your service → "Variables" tab and add:

#### Required Variables

```bash
# Database (use Railway's DATABASE_URL or configure separately)
DB_HOST=<railway-postgres-host>
DB_PORT=5432
DB_NAME=railway
DB_USER=postgres
DB_PASSWORD=<railway-postgres-password>

# Or use Railway's auto-provided DATABASE_URL (recommended)
# You'll need to parse it in config.py or use it directly

# JWT Authentication
JWT_SECRET_KEY=<generate-a-secure-random-key>

# Coinbase API (if using real trading)
COINBASE_API_KEY=<your-api-key>
COINBASE_API_SECRET=<your-api-secret>
COINBASE_API_PASSPHRASE=<your-passphrase>

# Environment
ENVIRONMENT=production
PAPER_TRADING=true  # Set to false for live trading
LOG_LEVEL=INFO

# AI Settings (optional)
CLAUDE_API_KEY=<your-claude-api-key>
CLAUDE_MODEL=claude-3-haiku-20240307

# Alert Settings (optional)
SLACK_WEBHOOK_URL=<your-webhook-url>
TELEGRAM_BOT_TOKEN=<your-bot-token>
TELEGRAM_CHAT_ID=<your-chat-id>
```

#### Generate JWT Secret Key

```bash
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

### Step 4: Configure Database Connection

Railway provides a `DATABASE_URL` automatically. You have two options:

#### Option A: Use Railway's DATABASE_URL (Recommended)

Update `config.py` to parse `DATABASE_URL`:

```python
import os
from urllib.parse import urlparse

# In Config class __init__ or get_config():
if 'DATABASE_URL' in os.environ:
    db_url = urlparse(os.environ['DATABASE_URL'])
    DB_HOST = db_url.hostname
    DB_PORT = db_url.port or 5432
    DB_NAME = db_url.path[1:]  # Remove leading '/'
    DB_USER = db_url.username
    DB_PASSWORD = db_url.password
else:
    # Fallback to individual env vars
    DB_HOST = os.getenv('DB_HOST', 'localhost')
    DB_PORT = int(os.getenv('DB_PORT', '5432'))
    DB_NAME = os.getenv('DB_NAME', 'tradingbot')
    DB_USER = os.getenv('DB_USER', 'postgres')
    DB_PASSWORD = os.getenv('DB_PASSWORD', '')
```

#### Option B: Use Individual Variables

Just set `DB_HOST`, `DB_PORT`, `DB_NAME`, `DB_USER`, `DB_PASSWORD` from Railway's database settings.

### Step 5: Deploy

1. Railway will automatically detect `app.py` as the entry point
2. It will run `pip install -r requirements.txt`
3. Then run `python app.py`
4. Railway will assign a public URL automatically (e.g., `your-app.up.railway.app`)

### Step 6: Configure Custom Domain (Optional)

1. Go to your service → "Settings" → "Domains"
2. Click "Generate Domain" or "Add Custom Domain"
3. Railway provides free SSL certificates automatically

### Step 7: Monitor & Logs

1. Go to your service → "Deployments" to see deployment status
2. Click "View Logs" for real-time logs
3. Railway provides better log formatting than Heroku

## Railway vs Heroku Comparison

| Feature | Heroku | Railway |
|---------|--------|---------|
| Async Python Support | Limited | Excellent |
| Configuration | Procfile needed | Auto-detected |
| Database | Add-on required | Built-in integration |
| Logging | Basic | Advanced with search |
| Cold Starts | Frequent | Rare |
| Free Tier | Limited hours | Generous usage |
| Deployment | git push | Automatic on git push |
| Environment Variables | Manual setup | Auto from database |

## Troubleshooting

### Database Connection Issues

If you see database connection errors:

1. Check that the database service is running in Railway
2. Verify `DATABASE_URL` is set (or individual DB variables)
3. Check the database logs in Railway dashboard
4. Ensure your database has proper network access

### Port Configuration

Railway automatically sets the `PORT` environment variable. Your `app.py` already uses this:

```python
port = int(os.environ.get('PORT', 4000))
```

This will work automatically with Railway.

### Memory Issues

If you encounter memory issues:

1. Railway provides better resource allocation
2. Check your service → "Settings" → "Resources"
3. Increase memory if needed (usage-based pricing)

### Long-Running Processes

Railway is better suited for long-running async processes than Heroku. Your `app.py` with `asyncio.Event().wait()` will work perfectly.

## Post-Migration Checklist

- [ ] All environment variables configured
- [ ] Database connection working
- [ ] App starts successfully (check logs)
- [ ] Public URL accessible
- [ ] Authentication working
- [ ] API endpoints responding
- [ ] Database tables created automatically
- [ ] Logs accessible and readable

## Rollback Plan

If you need to rollback:

1. Railway keeps deployment history
2. Go to "Deployments" → select previous deployment → "Redeploy"
3. Or keep Heroku running in parallel during migration

## Cost Comparison

### Railway
- **Free Tier**: $5 credit/month (covers small apps)
- **Usage-Based**: Pay for what you use (CPU, memory, bandwidth)
- **Database**: Included in usage

### Heroku
- **Free Tier**: Removed (now paid only)
- **Hobby**: $7/month + database costs
- **Standard**: $25/month + database costs

**Railway is typically more cost-effective** for this type of application.

## Next Steps

1. Set up Railway project
2. Add PostgreSQL database
3. Configure environment variables
4. Deploy and test
5. Update DNS (if using custom domain)
6. Monitor logs and performance
7. Once stable, consider removing Heroku deployment

---

**Note**: Keep Heroku deployment running during migration for zero-downtime transition. Once Railway is stable and tested, you can deprecate Heroku.

