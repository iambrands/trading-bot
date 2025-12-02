# Heroku Deployment Setup - What's Needed

## Current Status

✅ **Completed:**
- Procfile created
- app.py entry point created
- Favicon route handler added
- Cache fixes deployed
- Dynos scaled up

❌ **Issue:** App is crashing (dyno crashes)

## What's Needed to Fix

### 1. Required Environment Variables

The app needs these environment variables set in Heroku:

```bash
# JWT Authentication (REQUIRED)
JWT_SECRET_KEY=your-secret-key-here

# Database (REQUIRED for full functionality)
DATABASE_URL=postgresql://user:password@host:port/database

# Or individual DB settings:
DB_HOST=your-db-host
DB_PORT=5432
DB_NAME=tradingbot
DB_USER=your-user
DB_PASSWORD=your-password
```

### 2. Set Environment Variables

Run these commands:

```bash
# Set JWT secret (generate a random one)
heroku config:set JWT_SECRET_KEY=$(python -c "import secrets; print(secrets.token_urlsafe(32))") -a iab-optionsbot

# If using Heroku Postgres addon
heroku addons:create heroku-postgresql:mini -a iab-optionsbot

# Or manually set database URL
heroku config:set DATABASE_URL=your-database-url -a iab-optionsbot
```

### 3. Check Current Config

```bash
heroku config -a iab-optionsbot
```

### 4. View Logs to Diagnose

```bash
heroku logs --tail -a iab-optionsbot
```

## Common Issues

1. **Missing JWT_SECRET_KEY** - App will crash when trying to create auth manager
2. **Database connection errors** - App might fail if DB not accessible
3. **Missing dependencies** - All packages must be in requirements.txt

## Next Steps

1. Set JWT_SECRET_KEY environment variable
2. Set up database (Heroku Postgres addon or external)
3. Check logs for specific errors
4. Restart dynos after setting config

