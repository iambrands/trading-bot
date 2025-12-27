# Quick Start: Enable Paper Trading on Railway

## What You Need

To enable paper trading on Railway, you need to:

### 1. Update Dockerfile ✅ (Already Done)

The Dockerfile has been updated to run `main.py` instead of `app.py`:
```dockerfile
CMD ["python", "main.py"]
```

### 2. Add Environment Variables to Railway

Go to Railway → Your Service → Variables tab and add:

#### Required:
```bash
PAPER_TRADING=true
USE_REAL_MARKET_DATA=true
```

#### Coinbase API (Read-Only Recommended):

**Option A: With API Keys** (Better reliability)
```bash
COINBASE_API_KEY=your_key_here
COINBASE_API_SECRET=your_secret_here
COINBASE_API_PASSPHRASE=your_passphrase_here
```

Get keys from: https://www.coinbase.com/settings/api
- Click "Create API Key"
- Name: "Trading Bot - Paper Trading"
- Select **"View"** permissions only (NOT "Trade")
- Copy Key, Secret, and Passphrase

**Option B: Without API Keys** (Uses public endpoints)
```bash
# Leave empty or don't set these
COINBASE_API_KEY=
COINBASE_API_SECRET=
COINBASE_API_PASSPHRASE=
```

#### Already Set (Keep These):
```bash
DATABASE_URL=postgresql://...  # Already configured
JWT_SECRET_KEY=...              # Already configured
```

### 3. Deploy Changes

```bash
git add Dockerfile
git commit -m "Enable paper trading on Railway"
git push
```

Railway will automatically redeploy.

### 4. Test Paper Trading

1. Wait for Railway deployment to complete
2. Log into your Railway dashboard
3. Click "Start" button to begin paper trading
4. Bot will use real Coinbase market data but simulate trades

## What Works Now

✅ Real market prices from Coinbase  
✅ Real market conditions and data  
✅ Simulated trading (no real money)  
✅ Performance tracking  
✅ Full bot control (start/stop/pause)  

## Documentation

- Full setup guide: `RAILWAY_PAPER_TRADING_SETUP.md`
- Environment variables: `RAILWAY_ENV_VARIABLES_PAPER_TRADING.md`


