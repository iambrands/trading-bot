# Railway Environment Variables for Paper Trading

## Required Variables

Add these to your Railway service in the "Variables" tab:

### Paper Trading Configuration
```bash
PAPER_TRADING=true
USE_REAL_MARKET_DATA=true
```

### Coinbase API Credentials (Read-Only Recommended)

**Option 1: With API Keys (Recommended)**
Provides better data access and reliability:

```bash
COINBASE_API_KEY=your_api_key_here
COINBASE_API_SECRET=your_api_secret_here
COINBASE_API_PASSPHRASE=your_passphrase_here
```

**How to Get API Keys:**
1. Go to https://www.coinbase.com/settings/api
2. Click "Create API Key"
3. Name: "Trading Bot - Paper Trading (Read-Only)"
4. Select **"View"** permissions only (NOT "Trade")
5. Copy the Key, Secret, and Passphrase

**Option 2: Without API Keys (Public Data Only)**
You can also run without API keys - it will use public Coinbase endpoints:
```bash
# Leave these empty or don't set them
COINBASE_API_KEY=
COINBASE_API_SECRET=
COINBASE_API_PASSPHRASE=
```

### Database (Already Configured)
```bash
DATABASE_URL=postgresql://user:pass@host:port/dbname
```

### Authentication (Already Configured)
```bash
JWT_SECRET_KEY=your_secret_key
```

### Optional Configuration
```bash
# Starting account size for paper trading (default: 100000 = $100,000)
ACCOUNT_SIZE=100000

# Environment
ENVIRONMENT=production

# Logging
LOG_LEVEL=INFO
```

## Quick Setup Checklist

- [ ] Set `PAPER_TRADING=true`
- [ ] Set `USE_REAL_MARKET_DATA=true`
- [ ] Get Coinbase API credentials (read-only)
- [ ] Add `COINBASE_API_KEY`, `COINBASE_API_SECRET`, `COINBASE_API_PASSPHRASE`
- [ ] Verify `DATABASE_URL` is set
- [ ] Verify `JWT_SECRET_KEY` is set
- [ ] Update Dockerfile to run `main.py` (already done)
- [ ] Commit and push changes
- [ ] Wait for Railway to redeploy
- [ ] Test paper trading in dashboard

## Security Notes

1. **Read-Only Keys**: Even if keys are exposed, they cannot execute trades
2. **Paper Trading**: No real money is at risk
3. **Keep Keys Secret**: Don't share API keys publicly
4. **Monitor Usage**: Watch Railway logs for any issues


