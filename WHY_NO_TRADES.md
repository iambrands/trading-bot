# Why Am I Not Seeing Trades?

## 🔍 Diagnostic Endpoint

Check the **Market Conditions** endpoint to see exactly why trades aren't triggering:

```bash
curl http://localhost:8001/api/market-conditions | python3 -m json.tool
```

Or visit in browser:
```
http://localhost:8001/api/market-conditions
```

This shows:
- Current indicators (price, EMA, RSI, volume)
- Which conditions are met/not met
- Confidence scores
- Blockers preventing trades

## 📊 Trading Entry Requirements

### For a LONG (Buy) Trade:

1. ✅ **Price > EMA(50)** - Price must be above moving average
2. ✅ **RSI between 55-70** - Not too weak, not overbought
3. ✅ **Volume > 1.5x average** - Volume spike needed
4. ✅ **Confidence ≥ 70%** - Must meet minimum threshold

### For a SHORT (Sell) Trade:

1. ✅ **Price < EMA(50)** - Price must be below moving average
2. ✅ **RSI between 30-45** - Not too strong, not oversold
3. ✅ **Volume > 1.5x average** - Volume spike needed
4. ✅ **Confidence ≥ 70%** - Must meet minimum threshold

## 🚫 Common Blockers

### 1. **Insufficient Data**
- Need at least 50+ candles for EMA(50)
- Need 20+ candles for volume average
- Bot needs time to accumulate data

**Check**: Look at `candles_count` in market-conditions endpoint

### 2. **RSI Not in Range**
- Long needs RSI 55-70 (currently might be 45 or 75)
- Short needs RSI 30-45 (currently might be 50 or 25)

**Solution**: Market needs to be in right momentum state

### 3. **Volume Too Low**
- Needs volume spike (1.5x average)
- Low volume = low confidence signal

**Check**: Look at `volume_ratio` - needs to be ≥ 1.5

### 4. **Confidence Too Low**
- Even if conditions met, confidence might be < 70%
- This is by design to only trade high-quality setups

**Check**: Look at `confidence` score in market-conditions

### 5. **Bot Not Running**
- Bot status must be "running"
- Check `/api/status` endpoint

### 6. **Already at Max Positions**
- Max 2 positions allowed
- Won't open new position if limit reached

## 🛠️ How to Debug

1. **Check Market Conditions**:
   ```bash
   curl http://localhost:8001/api/market-conditions | python3 -m json.tool
   ```

2. **Check Bot Status**:
   ```bash
   curl http://localhost:8001/api/status
   ```

3. **Check Logs**:
   ```bash
   tail -f tradingbot.log | grep -i "signal\|confidence\|entry"
   ```

4. **Lower Thresholds** (if needed):
   Edit `config.py`:
   - Lower `MIN_CONFIDENCE_SCORE` (default: 70)
   - Lower `VOLUME_MULTIPLIER` (default: 1.5)
   - Widen RSI ranges (default: 55-70 for long, 30-45 for short)

## ⚙️ Adjusting Strategy Parameters

If you want to see more trades (with lower quality), edit `config.py`:

```python
# Make it easier to trigger trades
MIN_CONFIDENCE_SCORE = 60  # Lower from 70
VOLUME_MULTIPLIER = 1.2    # Lower from 1.5
RSI_LONG_MIN = 50          # Widen from 55
RSI_LONG_MAX = 75          # Widen from 70
```

⚠️ **Warning**: Lower thresholds = more trades but lower quality signals

## 📈 Current Strategy Values

- **EMA Period**: 50
- **RSI Period**: 14
- **Volume Period**: 20
- **Volume Multiplier**: 1.5x
- **RSI Long Range**: 55-70
- **RSI Short Range**: 30-45
- **Min Confidence**: 70%
- **Max Positions**: 2

## 🎯 Expected Behavior

- **Crypto markets move fast** - conditions change quickly
- **Quality over quantity** - bot waits for high-probability setups
- **May not trade daily** - depends on market conditions
- **This is normal** - strict criteria = fewer but better trades

## 💡 Tips

1. **Be Patient**: Crypto markets may not meet criteria daily
2. **Monitor Dashboard**: Watch indicators in real-time
3. **Check Conditions**: Use `/api/market-conditions` regularly
4. **Adjust if Needed**: Lower thresholds if you want more activity
5. **Review Strategy**: Current settings prioritize quality over frequency
