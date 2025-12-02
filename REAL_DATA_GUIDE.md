# Using Real Cryptocurrency Data - Quick Guide

## 🚀 Quick Start (Easiest Method)

**No API keys needed!** The bot can use Coinbase's public API for real market data.

### Step 1: Enable Real Market Data

```bash
./setup_real_data.sh
```

This automatically adds `USE_REAL_MARKET_DATA=true` to your `.env` file.

### Step 2: Restart the Bot

```bash
pkill -f "python main.py"
python main.py
```

**That's it!** Your bot will now use real Bitcoin and Ethereum prices from Coinbase.

## What You Get

✅ **Real-time prices** from Coinbase Exchange  
✅ **Real historical candle data** for strategy calculations  
✅ **Actual market volume** for volume confirmation  
✅ **Paper trading safety** - orders are still simulated  
✅ **No API keys required** - uses public endpoints  

## Verify It's Working

1. **Check the dashboard**: http://localhost:8001
   - Prices should match current Coinbase prices
   - Market data should update in real-time

2. **Check the logs**:
   ```bash
   tail -f tradingbot.log | grep -i "market\|candle\|price"
   ```
   You should see real data being fetched.

3. **Test with curl**:
   ```bash
   curl http://localhost:8001/api/status
   ```
   Balance will show your paper trading balance, but prices are real.

## Option 2: Use API Keys (Optional)

For more reliable data and higher rate limits, you can add Coinbase API keys:

### Steps:

1. **Get API Keys** (Read-only is fine):
   - Go to: https://www.coinbase.com/settings/api
   - Create API Key with "View" permissions
   - Save: Key, Secret, Passphrase

2. **Update .env file**:
   ```env
   COINBASE_API_KEY=your_key_here
   COINBASE_API_SECRET=your_secret_here
   COINBASE_API_PASSPHRASE=your_passphrase_here
   USE_REAL_MARKET_DATA=true
   PAPER_TRADING=true
   ```

3. **Restart bot**:
   ```bash
   pkill -f "python main.py" && python main.py
   ```

## Current Configuration

Check your current settings:

```bash
grep -E "(USE_REAL_MARKET_DATA|PAPER_TRADING|COINBASE_API)" .env
```

## Troubleshooting

### Prices Not Updating?

1. **Check network connection**:
   ```bash
   curl https://api.exchange.coinbase.com/products/BTC-USD/ticker
   ```
   Should return JSON with current BTC price.

2. **Check bot logs**:
   ```bash
   tail -f tradingbot.log | grep -i error
   ```

3. **Verify configuration**:
   ```bash
   grep USE_REAL_MARKET_DATA .env
   ```
   Should show `USE_REAL_MARKET_DATA=true`

### Still Using Synthetic Data?

The bot falls back to synthetic data if:
- Real API is unreachable
- Network issues
- Rate limiting

Check logs for fallback messages.

## Live Trading (Production)

⚠️ **Warning**: Only enable after extensive testing!

To switch to live trading with real money:

1. **Update .env**:
   ```env
   PAPER_TRADING=false
   USE_REAL_MARKET_DATA=true
   COINBASE_API_KEY=your_key
   COINBASE_API_SECRET=your_secret
   COINBASE_API_PASSPHRASE=your_passphrase
   ```

2. **Use trading-enabled API keys** (not just "View" permission)

3. **Review risk settings** in `config.py`

4. **Start with small amounts**

See `COINBASE_SETUP.md` for detailed instructions.

## Summary

| Mode | Real Prices? | Real Orders? | Risk |
|------|-------------|--------------|------|
| Paper Trading + Real Data | ✅ Yes | ❌ Simulated | None |
| Live Trading | ✅ Yes | ✅ Yes | Real Money |

**Recommended**: Start with Paper Trading + Real Data to test your strategy with real market conditions safely.

## Next Steps

1. ✅ Enable real market data: `./setup_real_data.sh`
2. ✅ Restart bot: `python main.py`
3. ✅ Monitor dashboard: http://localhost:8001
4. ✅ Watch bot trade with real market data
5. ✅ Review performance over time
6. ✅ When confident, consider live trading

For detailed API setup, see `COINBASE_SETUP.md`
