# Coinbase Advanced Trade API Setup Guide

This guide will help you connect Crypto Scalping Trading Bot to real cryptocurrency market data from Coinbase.

## Option 1: Real Market Data with Paper Trading (Recommended)

Use **real market prices** from Coinbase while still simulating trades. This is the safest way to test your bot with actual market conditions.

### Benefits:
- ✅ Real-time market prices from Coinbase
- ✅ Real historical candle data
- ✅ Actual market volume and trends
- ✅ Safe - no real money at risk
- ✅ Perfect for strategy validation

### Setup Steps:

1. **Get Coinbase API Credentials** (Read-only is fine for market data):
   - Go to [Coinbase Advanced Trade API Settings](https://www.coinbase.com/settings/api)
   - Click "Create API Key"
   - Name it "Crypto Scalping Trading Bot - Read Only"
   - **Important**: Select "View" permissions only (not "Trade")
   - Save your API Key, Secret, and Passphrase

2. **Update .env file**:
   ```env
   COINBASE_API_KEY=your_api_key_here
   COINBASE_API_SECRET=your_api_secret_here
   COINBASE_API_PASSPHRASE=your_passphrase_here
   PAPER_TRADING=true
   USE_REAL_MARKET_DATA=true
   ```

3. **Restart the bot**:
   ```bash
   python main.py
   ```

The bot will now:
- Fetch real market prices from Coinbase
- Use real historical candle data
- Still simulate order execution (paper trading)
- Show actual market conditions in the dashboard

## Option 2: Live Trading (Production)

⚠️ **WARNING**: Live trading uses REAL MONEY. Only enable after extensive paper trading validation!

### Setup Steps:

1. **Get Coinbase API Credentials with Trading Permissions**:
   - Go to [Coinbase Advanced Trade API Settings](https://www.coinbase.com/settings/api)
   - Click "Create API Key"
   - Name it "Crypto Scalping Trading Bot - Live Trading"
   - Select **"Trade"** permissions
   - Enable IP whitelist for security (recommended)
   - Save your credentials securely

2. **Update .env file**:
   ```env
   COINBASE_API_KEY=your_api_key_here
   COINBASE_API_SECRET=your_api_secret_here
   COINBASE_API_PASSPHRASE=your_passphrase_here
   PAPER_TRADING=false
   USE_REAL_MARKET_DATA=true
   ENVIRONMENT=production
   ```

3. **Verify Your Settings**:
   - Double-check risk parameters in `config.py`
   - Ensure daily loss limits are appropriate
   - Review your account balance
   - Test kill switch functionality

4. **Start Small**:
   - Consider reducing account size for initial live trading
   - Monitor closely for first few days
   - Keep kill switch accessible

## Option 3: Public API (No Authentication Required)

For market data only (no trading), you can use Coinbase's public API endpoints without authentication. This is automatically enabled if no API keys are provided.

### Setup:

Simply leave API credentials empty in `.env`:
```env
COINBASE_API_KEY=
COINBASE_API_SECRET=
COINBASE_API_PASSPHRASE=
USE_REAL_MARKET_DATA=true
PAPER_TRADING=true
```

The bot will use public Coinbase endpoints for:
- Real-time price data
- Historical candles
- Market statistics

However, account balance and order execution will be simulated.

## API Key Security Best Practices

1. **Never commit API keys to Git**:
   - `.env` is already in `.gitignore`
   - Double-check before pushing to repositories

2. **Use IP Whitelisting**:
   - Restrict API keys to your server IPs only
   - Prevents unauthorized access

3. **Use Read-Only Keys for Testing**:
   - Start with "View" permissions only
   - Upgrade to "Trade" only when ready for live trading

4. **Rotate Keys Regularly**:
   - Change API keys every 90 days
   - Immediately revoke compromised keys

5. **Store Keys Securely**:
   - Use environment variables (not hardcoded)
   - Consider using a secrets manager for production

## Testing Your Connection

After setting up API keys, test the connection:

```bash
# Check if bot can fetch real market data
curl http://localhost:8001/api/status

# Check logs for connection status
tail -f tradingbot.log | grep -i "coinbase\|market\|api"
```

## Troubleshooting

### "Invalid API Key" Error
- Verify API key, secret, and passphrase are correct
- Check for extra spaces or newlines in `.env` file
- Ensure API key hasn't expired

### "Permission Denied" Error
- Verify API key has required permissions
- For market data: "View" permission is sufficient
- For trading: "Trade" permission required

### "Rate Limit Exceeded"
- Coinbase has rate limits on API calls
- The bot includes retry logic
- If persistent, reduce loop interval in `config.py`

### Market Data Not Updating
- Check WebSocket connection in logs
- Verify network connectivity
- Ensure trading pairs are correctly configured

## Coinbase API Documentation

- [Advanced Trade API Docs](https://docs.cloud.coinbase.com/advanced-trade-api/docs)
- [API Authentication](https://docs.cloud.coinbase.com/advanced-trade-api/docs/auth)
- [Rate Limits](https://docs.cloud.coinbase.com/advanced-trade-api/docs/rate-limits)

## Next Steps

1. ✅ Set up API credentials (Option 1 recommended)
2. ✅ Test with real market data in paper trading
3. ✅ Monitor performance for several days
4. ✅ Adjust strategy parameters if needed
5. ✅ When confident, consider live trading (Option 2)

## Support

If you encounter issues:
- Check `tradingbot.log` for detailed error messages
- Review Coinbase API status page
- Verify network connectivity
- Test API credentials with Coinbase's API explorer
