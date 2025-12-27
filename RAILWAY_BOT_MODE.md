# Railway Bot Mode Explanation

## Current Setup: API-Only Mode

Railway is currently running `app.py`, which is **API-only mode**:
- ✅ Dashboard works (view data, analytics, charts)
- ✅ Authentication works
- ✅ Database works
- ❌ Bot control doesn't work (start/stop/pause bot)
- ❌ Trading doesn't work (no bot instance)

## Why API-Only Mode?

API-only mode is ideal for Railway because:
- Lightweight - just the web dashboard
- No trading logic running (safer)
- Lower resource usage
- Better for web hosting

## Options

### Option 1: Keep API-Only Mode (Recommended)

This is fine if you just want to:
- View the dashboard
- See analytics
- Monitor performance
- Use the web interface

Bot control features (start/stop) won't work, but everything else does.

### Option 2: Run Full Bot (main.py)

To run the full trading bot on Railway, you would need to:

1. **Change Dockerfile** to run `main.py` instead of `app.py`:
   ```dockerfile
   CMD ["python", "main.py"]
   ```

2. **Add Coinbase API credentials** to Railway variables:
   - `COINBASE_API_KEY`
   - `COINBASE_API_SECRET`
   - `COINBASE_API_PASSPHRASE`

3. **Consider resource usage** - full bot needs more CPU/memory

4. **Understand risks** - bot would actually trade (if not in paper trading mode)

**Note**: Running the full bot on Railway for actual trading is generally not recommended. Railway is better for the dashboard/API, and you'd typically run the trading bot on a dedicated server or VPS.

## Recommendation

Keep API-only mode for Railway. Use the dashboard to:
- View data and analytics
- Monitor performance
- Manage settings
- View trades and positions

If you need to actually run trades, run `main.py` locally or on a dedicated server with proper monitoring and control.


