# Railway Paper Trading Setup Guide

This guide will help you enable paper trading on Railway so users can test the trading bot with real market data from Coinbase.

## What is Paper Trading?

Paper trading allows users to:
- ✅ Test the bot with **real market prices** from Coinbase
- ✅ See actual market conditions and data
- ✅ Simulate trades without risking real money
- ✅ Track performance and learn how the bot works
- ✅ Safe testing environment

## Changes Required

### 1. Update Dockerfile

The Dockerfile has been updated to run `main.py` instead of `app.py`:
```dockerfile
CMD ["python", "main.py"]
```

This enables the full trading bot with paper trading support.

### 2. Required Environment Variables

Add these environment variables to your Railway service:

#### Required for Paper Trading:
```bash
# Enable paper trading mode
PAPER_TRADING=true

# Use real market data from Coinbase
USE_REAL_MARKET_DATA=true
```

#### Coinbase API Credentials (Read-Only is Fine):

You need Coinbase API credentials to fetch real market data. **Read-only ("View") permissions are sufficient** - no trading permissions needed.

Get your credentials from: https://www.coinbase.com/settings/api

```bash
# Coinbase API credentials (read-only is fine)
COINBASE_API_KEY=your_api_key_here
COINBASE_API_SECRET=your_api_secret_here
COINBASE_API_PASSPHRASE=your_passphrase_here
```

#### Already Configured (Keep These):
```bash
# Database (already set)
DATABASE_URL=postgresql://...

# JWT Secret (already set)
JWT_SECRET_KEY=your_secret_key

# Optional: Account size for paper trading (default: $100,000)
ACCOUNT_SIZE=100000
```

## Step-by-Step Setup

### Step 1: Get Coinbase API Credentials

1. Go to [Coinbase Advanced Trade API Settings](https://www.coinbase.com/settings/api)
2. Click "Create API Key"
3. Name it "Trading Bot - Paper Trading (Read-Only)"
4. **Important**: Select **"View"** permissions only (NOT "Trade")
5. Copy the API Key, Secret, and Passphrase

**Why Read-Only?**
- Read-only keys can fetch real market prices and data
- They cannot execute trades (perfect for paper trading)
- Safer - no risk of accidental trades

### Step 2: Update Railway Environment Variables

1. Go to your Railway project
2. Select your service
3. Go to the "Variables" tab
4. Add/update these variables:

```
PAPER_TRADING=true
USE_REAL_MARKET_DATA=true
COINBASE_API_KEY=<your_key>
COINBASE_API_SECRET=<your_secret>
COINBASE_API_PASSPHRASE=<your_passphrase>
```

### Step 3: Update Dockerfile (Already Done)

The Dockerfile has been updated to run `main.py`:
```dockerfile
CMD ["python", "main.py"]
```

This change will be deployed automatically when you push to GitHub.

### Step 4: Redeploy

1. Commit and push the Dockerfile changes:
   ```bash
   git add Dockerfile
   git commit -m "Enable paper trading mode on Railway"
   git push
   ```

2. Railway will automatically redeploy

3. Wait for deployment to complete (check Railway logs)

### Step 5: Verify Paper Trading is Active

1. Log into your Railway dashboard URL
2. Go to the Dashboard page
3. You should see:
   - Real market prices updating
   - Bot status showing "stopped" (start it to begin trading)
   - Paper trading mode indicated in status

4. Click "Start" to begin paper trading
5. The bot will use real Coinbase market data but simulate trades

## How Paper Trading Works

### Real Market Data:
- ✅ Real-time prices from Coinbase
- ✅ Real historical candle data
- ✅ Actual market volume and trends
- ✅ Live market conditions

### Simulated Trading:
- ✅ Order execution is simulated (not real)
- ✅ Balance tracking (starts at ACCOUNT_SIZE)
- ✅ Position management (simulated)
- ✅ Slippage simulation (0.01-0.05%)
- ✅ Fee simulation (0.6% maker/taker)

### What Gets Tracked:
- Paper account balance
- Paper positions
- Simulated trades
- Performance metrics
- P&L calculations

## User Experience

Users can now:
1. **Sign up/Log in** to the dashboard
2. **View real market data** from Coinbase
3. **Start the bot** to begin paper trading
4. **See trades execute** (simulated)
5. **Track performance** with real market data
6. **Learn how the bot works** without risk

## Troubleshooting

### Bot Won't Start
- Check Railway logs for errors
- Verify all environment variables are set
- Ensure DATABASE_URL is correct
- Check Coinbase API credentials are valid

### No Market Data
- Verify `USE_REAL_MARKET_DATA=true`
- Check Coinbase API credentials
- Check Railway logs for API errors
- Ensure `COINBASE_API_KEY` is set

### "Trading bot is not running" Error
- This should be fixed now that we're running `main.py`
- If you still see this, check Railway logs
- Verify the deployment completed successfully

### Database Errors
- Ensure `DATABASE_URL` is set correctly
- Check PostgreSQL service is running in Railway
- Verify database connection in logs

## Security Notes

1. **API Keys are Read-Only**: Even if keys are exposed, they can't execute trades
2. **Paper Trading is Safe**: No real money at risk
3. **Monitor Usage**: Keep an eye on Railway logs and metrics
4. **Set Limits**: Consider adding rate limiting if many users

## Next Steps

After paper trading is working:
- Users can test different strategies
- Monitor performance metrics
- Learn how the bot works
- Build confidence before live trading (if desired)

## Resources

- [Coinbase API Documentation](https://docs.cloud.coinbase.com/advanced-trade-api/docs)
- [Railway Documentation](https://docs.railway.app/)
- [Project README](../README.md)

