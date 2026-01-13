# Diagnostic Scripts

This directory contains diagnostic scripts to troubleshoot why the bot isn't trading.

## Available Scripts

### 1. `check_bot_status.py`
**Purpose:** Check if the bot process is running and examine recent logs.

**Usage:**
```bash
python diagnostics/check_bot_status.py
```

**What it checks:**
- Is the bot process running?
- Log file location and age
- Recent log entries
- Errors in logs
- API server status (if running)

**When to use:** First step - verify bot is actually running.

---

### 2. `test_api_connection.py`
**Purpose:** Test Coinbase API connection and data fetching.

**Usage:**
```bash
python diagnostics/test_api_connection.py
```

**What it tests:**
- API credentials present
- Client initialization
- Account balance fetch
- Market data fetch
- Historical candle data fetch
- API authentication (if not paper trading)

**When to use:** If bot is running but not getting data, or to verify API keys work.

---

### 3. `test_strategy_signals.py`
**Purpose:** Test if the strategy generates any signals with recent market data.

**Usage:**
```bash
# Test last 7 days (default)
python diagnostics/test_strategy_signals.py

# Test last 14 days
python diagnostics/test_strategy_signals.py --days 14

# Test specific pair
python diagnostics/test_strategy_signals.py --pair ETH-USD

# Combine options
python diagnostics/test_strategy_signals.py --days 30 --pair BTC-USD
```

**What it tests:**
- Fetches recent candle data
- Runs strategy on historical data
- Counts signals generated
- Shows why signals aren't being generated (if none)
- Displays current market indicators

**When to use:** If bot is running and API works, but no trades are happening. This is the MOST IMPORTANT diagnostic.

---

## Recommended Diagnostic Flow

Run these scripts in order:

### Step 1: Check if bot is running
```bash
python diagnostics/check_bot_status.py
```

**If bot is NOT running:**
- Start the bot: `python main.py`
- Check for startup errors
- Then proceed to Step 2

**If bot IS running:**
- Proceed to Step 2

### Step 2: Test API connection
```bash
python diagnostics/test_api_connection.py
```

**If API fails:**
- Check API keys in `.env` file
- Verify keys are valid in Coinbase dashboard
- Check API key permissions
- Fix API issues, then proceed

**If API works:**
- Proceed to Step 3

### Step 3: Test strategy signals
```bash
python diagnostics/test_strategy_signals.py
```

**If signals are generated:**
- ✅ Strategy is working
- Issue is likely:
  - Risk management blocking trades
  - Bot logic not executing trades
  - Position limits reached
  - Check bot logs for trade attempts

**If NO signals generated:**
- ❌ This is why bot isn't trading
- Strategy conditions aren't being met
- Possible fixes:
  - Relax strategy thresholds (RSI range, volume multiplier)
  - Check if market conditions have changed
  - Strategy may not be suited for current market

---

## Understanding Results

### Bot Status Check Results

**✅ Bot Running + Recent Logs:**
- Bot is active
- Proceed to API test

**❌ No Process Found:**
- Bot crashed or never started
- Check startup errors
- Verify configuration

**⚠️ Old Log File:**
- Log file hasn't been updated in hours/days
- Bot may have stopped
- Check process status

---

### API Connection Test Results

**✅ All Tests Pass:**
- API is working correctly
- Can fetch data
- Proceed to strategy test

**❌ Authentication Failed:**
- Invalid API keys
- Keys expired
- Fix: Create new API keys

**❌ Permission Denied:**
- API keys don't have required permissions
- Fix: Enable trading permissions in Coinbase

**⚠️ Paper Trading Mode:**
- Using simulated data (expected)
- API test may show warnings (normal)
- Strategy test will still work

---

### Strategy Signal Test Results

**✅ Signals Generated:**
- Strategy IS working
- Found X signals in last 7 days
- Shows signal details
- **If bot still not trading:** Check risk management, logs, position limits

**❌ No Signals Generated:**
- Strategy conditions not being met
- Shows current indicators and why signals fail
- **This is why bot isn't trading**
- **Fix:** Relax thresholds or adjust strategy

**Current Indicators Shown:**
- Price, EMA, RSI, Volume Ratio
- Entry condition checks (what's passing/failing)
- Clear indication of why no signals

---

## Common Issues & Fixes

### Issue 1: Bot Not Running
**Symptoms:** `check_bot_status.py` shows no process
**Fix:**
```bash
python main.py
# Or if using systemd:
systemctl start trading-bot
```

### Issue 2: API Connection Failed
**Symptoms:** `test_api_connection.py` shows authentication errors
**Fix:**
1. Check `.env` file has correct keys
2. Verify keys in Coinbase dashboard
3. Create new keys if expired
4. Enable trading permissions

### Issue 3: No Signals Generated
**Symptoms:** `test_strategy_signals.py` shows 0 signals
**Fix:**
- Relax RSI ranges (widen from 55-70 to 50-75)
- Reduce volume multiplier (from 1.5x to 1.2x)
- Lower confidence threshold (from 70% to 60%)
- Check if market conditions changed

### Issue 4: Signals Generated But No Trades
**Symptoms:** Strategy generates signals but bot doesn't trade
**Fix:**
- Check risk management settings
- Verify daily loss limit not hit
- Check max positions not reached
- Review bot logs for trade attempts
- Check if bot status is "running" (not "paused")

---

## Quick Reference

```bash
# Run all diagnostics in order
python diagnostics/check_bot_status.py
python diagnostics/test_api_connection.py
python diagnostics/test_strategy_signals.py

# Most important (if bot is running):
python diagnostics/test_strategy_signals.py
```

---

## Need More Help?

If diagnostics don't reveal the issue:
1. Check bot logs: `tail -n 100 tradingbot.log`
2. Review configuration: `config.py`
3. Check database for risk flags
4. Verify bot status endpoint: `curl http://localhost:4000/api/status`

