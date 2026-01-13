# Market Conditions Page - Settings Not Updating: Debug Guide

## ✅ Confirmation: Data is Dynamic (NOT Hard-Coded)

The Market Conditions page reads **dynamically** from your settings. Here's the proof:

### Backend (`api/rest_api.py`)

**Line 1003:** `for pair in self.bot.config.TRADING_PAIRS:`
- Reads trading pairs from `self.bot.config.TRADING_PAIRS` (your settings)

**Lines 1087-1148:** All strategy parameters read from config:
- `self.bot.config.RSI_LONG_MIN` / `RSI_LONG_MAX`
- `self.bot.config.RSI_SHORT_MIN` / `RSI_SHORT_MAX`
- `self.bot.config.VOLUME_MULTIPLIER`
- `self.bot.config.MIN_CONFIDENCE_SCORE`
- `self.bot.config.EMA_PERIOD`
- `self.bot.config.RSI_PERIOD`
- `self.bot.config.VOLUME_PERIOD`

**All settings update in real-time when you save** (lines 1294-1363).

---

## 🔍 Why Settings Might Not Be Visible

### Possible Issue #1: Frontend Cache

**Problem:** Browser or page is showing cached data

**Solution:**
1. **Hard refresh the page:**
   - Chrome/Edge: `Ctrl+Shift+R` (Windows) or `Cmd+Shift+R` (Mac)
   - Firefox: `Ctrl+F5` (Windows) or `Cmd+Shift+R` (Mac)
   - Safari: `Cmd+Option+R`

2. **Clear browser cache:**
   - Go to browser settings
   - Clear browsing data
   - Select "Cached images and files"
   - Clear

3. **Check browser console:**
   - Press `F12` to open DevTools
   - Go to Network tab
   - Check if `/api/market-conditions` requests are being made
   - Verify responses contain updated data

### Possible Issue #2: Settings Not Actually Saved

**Problem:** Settings save might have failed silently

**Solution:**
1. **Check Settings page:**
   - Go to Settings page
   - Verify your changes are still there
   - If not, they weren't saved - save again

2. **Check browser console for errors:**
   - Press `F12`
   - Look for errors in Console tab
   - Check Network tab for failed API calls to `/api/settings`

3. **Check save confirmation:**
   - After clicking "Save Settings", you should see a success message
   - If no message appears, save might have failed

### Possible Issue #3: Bot Config Not Updated

**Problem:** Settings saved to database but bot config not reloaded

**Solution:**
1. **Restart the bot:**
   - Settings are saved to config, but sometimes a restart ensures they're fully applied
   - Use "Apply & Restart" button in Settings
   - Or restart Railway service

2. **Check if trading pairs reloaded:**
   - When trading pairs change, the bot should automatically reload them
   - Check Railway logs for: "Trading pairs changed" and "Reloading trading pairs"

### Possible Issue #4: Market Conditions Page Not Refreshing

**Problem:** Page data is stale

**Solution:**
1. **Navigate away and back:**
   - Go to another page (e.g., Overview)
   - Come back to Market Conditions
   - This forces a fresh data fetch

2. **Wait for auto-refresh:**
   - Market Conditions auto-refreshes every 5 seconds
   - Wait a few seconds and check again

3. **Manual refresh:**
   - Click the "Refresh" button if available
   - Or press `F5` to reload the page

### Possible Issue #5: Trading Pairs Need Time to Load Data

**Problem:** New trading pairs need candle data before they appear

**Solution:**
1. **Wait 1-2 minutes:**
   - New pairs need to fetch historical candle data
   - Bot needs 50+ candles for EMA calculation
   - Check logs for "Candle data reloaded"

2. **Check pair status:**
   - If pair shows "Insufficient data", wait for data to load
   - Bot is fetching candles in the background

---

## 🧪 Diagnostic Steps

### Step 1: Verify Settings Were Saved

1. Go to **Settings** page
2. Check if your changes are still visible
3. If YES → Continue to Step 2
4. If NO → Save settings again and check for errors

### Step 2: Check API Response

1. Open browser DevTools (`F12`)
2. Go to **Network** tab
3. Navigate to **Market Conditions** page
4. Find the request to `/api/market-conditions`
5. Click on it and check **Response** tab
6. Look for `conditions` object
7. Verify it contains:
   - Your updated trading pairs
   - Correct RSI ranges
   - Correct volume multiplier
   - Correct confidence threshold

### Step 3: Check Backend Logs

1. Go to Railway logs
2. Search for:
   - `"Saving settings - new trading_pairs"`
   - `"Trading pairs changed"`
   - `"Reloading trading pairs"`
3. Verify settings were saved and applied

### Step 4: Force Refresh

1. **Hard refresh the page** (`Ctrl+Shift+R` or `Cmd+Shift+R`)
2. Navigate away and back to Market Conditions
3. Check if updated data appears

### Step 5: Verify Bot Config

1. Check Railway logs for:
   - `"Settings updated via API"`
   - `"Trading pairs updated"`
   - Any error messages

2. If errors appear, share them for troubleshooting

---

## 🔧 Quick Fixes

### Fix 1: Force Settings Reload

```javascript
// In browser console (F12):
// Clear cache and force reload
location.reload(true);
```

### Fix 2: Restart Bot

1. Go to Settings page
2. Click **"Apply & Restart TradePilot"** button
3. Wait for bot to restart (30-60 seconds)
4. Check Market Conditions page again

### Fix 3: Verify Settings Endpoint

```javascript
// In browser console (F12):
// Check current settings
fetch('/api/settings')
  .then(r => r.json())
  .then(data => console.log('Current settings:', data));
```

Check the response to verify:
- `trading_pairs` contains your pairs
- `rsi_long_min`, `rsi_long_max` match your settings
- `volume_multiplier` matches your settings
- `min_confidence` matches your settings

---

## 📊 What Gets Updated Dynamically

When you save settings, these update **immediately** (no restart needed):

✅ **Strategy Parameters:**
- EMA Period
- RSI Period
- Volume Period
- Volume Multiplier
- RSI Long Min/Max
- RSI Short Min/Max
- Min Confidence Score

✅ **Risk Management:**
- Risk Per Trade
- Max Positions
- Daily Loss Limit
- Max Position Size
- Position Timeout

✅ **Exit Parameters:**
- Take Profit Min/Max
- Stop Loss Min/Max

✅ **Trading Pairs:**
- When trading pairs change, bot automatically:
  - Updates WebSocket connections
  - Reloads candle data for new pairs
  - Removes old pairs from monitoring

---

## 🐛 Known Issues & Workarounds

### Issue: Trading Pairs Not Appearing Immediately

**Cause:** New pairs need time to fetch candle data

**Workaround:**
1. Wait 1-2 minutes after saving
2. Check logs for "Candle data reloaded"
3. Refresh Market Conditions page

### Issue: Strategy Parameters Not Reflecting

**Cause:** Page might be showing cached response

**Workaround:**
1. Hard refresh page (`Ctrl+Shift+R`)
2. Navigate away and back
3. Check browser console for API responses

### Issue: Settings Save But Don't Apply

**Cause:** Bot might need a restart for some changes

**Workaround:**
1. Use "Apply & Restart" button
2. Or manually restart Railway service
3. Wait for bot to fully restart (check logs)

---

## ✅ Verification Checklist

After saving settings, verify:

- [ ] Settings page shows your saved values
- [ ] No errors in browser console
- [ ] No errors in Railway logs
- [ ] Market Conditions page refreshes (wait 5 seconds)
- [ ] Trading pairs appear (if you added new ones)
- [ ] RSI ranges match your settings
- [ ] Volume multiplier matches your settings
- [ ] Confidence threshold matches your settings

If all checked but still not working:
1. Hard refresh the page
2. Restart the bot
3. Check Railway logs for errors
4. Share logs for further troubleshooting

---

## 🔍 Debug Commands

### Check Current Settings (Browser Console)

```javascript
// Get current settings
fetch('/api/settings')
  .then(r => r.json())
  .then(data => {
    console.log('Trading Pairs:', data.trading_pairs);
    console.log('RSI Long:', data.rsi_long_min, '-', data.rsi_long_max);
    console.log('RSI Short:', data.rsi_short_min, '-', data.rsi_short_max);
    console.log('Volume Multiplier:', data.volume_multiplier);
    console.log('Min Confidence:', data.min_confidence);
  });
```

### Check Market Conditions Data (Browser Console)

```javascript
// Get market conditions
fetch('/api/market-conditions')
  .then(r => r.json())
  .then(data => {
    console.log('Trading Pairs:', Object.keys(data.conditions));
    console.log('Bot Config:', {
      pairs: data.summary.total_pairs,
      maxPositions: data.summary.max_positions
    });
  });
```

---

## 📝 Next Steps

If settings still aren't reflecting after trying all fixes:

1. **Share the following information:**
   - What settings did you change?
   - What do you see on Market Conditions page?
   - What should you see?
   - Browser console errors (if any)
   - Railway logs (relevant sections)

2. **Check for specific issues:**
   - Trading pairs not appearing → Check logs for "Trading pairs changed"
   - RSI ranges wrong → Check browser console API response
   - Volume multiplier wrong → Verify settings were saved
   - Confidence threshold wrong → Check both Settings page and Market Conditions

---

**Last Updated:** December 2025  
**Status:** Market Conditions page is dynamic - settings should update automatically

