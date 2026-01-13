# Testing Settings - See Trades Happen

## 🎯 Goal: Get Trades Executing for Testing

These settings are **for testing only** - they will produce more trades but with lower quality/confidence.

## ⚙️ Recommended Testing Settings

### Go to Settings Page and Change:

#### 1. **Volume Multiplier** (BIGGEST IMPACT)
- **Current**: 1.6 (very strict)
- **For Testing**: **1.2** or even **1.1**
- **Why**: Volume spikes of 1.1x are MUCH more common than 1.6x

#### 2. **Minimum Confidence Score** (HIGH IMPACT)
- **Current**: 70% (strict)
- **For Testing**: **50%** or **55%**
- **Why**: Much easier to meet confidence threshold

#### 3. **RSI Ranges** (MODERATE IMPACT)
- **Long Entry RSI Min**: Change from **55** to **50**
- **Long Entry RSI Max**: Change from **70** to **75**
- **Short Entry RSI Min**: Change from **30** to **25**
- **Short Entry RSI Max**: Change from **45** to **50**
- **Why**: Wider ranges capture more market conditions

#### 4. **Max Positions** (OPTIONAL)
- **Current**: 2
- **For Testing**: **5** or **10**
- **Why**: Allow more simultaneous positions

#### 5. **EMA Period** (OPTIONAL - More Aggressive)
- **Current**: 50
- **For Testing**: **30** or **20**
- **Why**: Shorter EMA responds faster to price changes

## 📋 Quick Copy-Paste Settings for Maximum Trades

These settings will almost certainly produce trades (lower quality, but visible):

```
Volume Multiplier: 1.2
Minimum Confidence Score: 50%
Long Entry RSI Min: 50
Long Entry RSI Max: 75
Short Entry RSI Min: 25
Short Entry RSI Max: 50
Max Positions: 5
EMA Period: 30 (optional)
```

## 🚀 Steps to Test

1. **Go to Settings page**
2. **Update the values above**
3. **Click "Save Settings"**
4. **Restart the bot** (if needed, or wait for next cycle)
5. **Go to Market Conditions page** - should see green checkmarks
6. **Go to Positions page** - should see trades appearing

## ⚠️ Important Notes

### These Settings Are:
- ✅ **Good for testing** - You'll see trades happen
- ✅ **Good for learning** - See how the system works
- ❌ **NOT for live trading** - Lower quality trades
- ❌ **Higher risk** - Less selective = more losing trades

### After Testing:
- **Revert to strict settings** for production:
  - Volume: 1.4-1.5
  - Confidence: 60-65%
  - RSI ranges back to recommended
  - Max positions: 2-3

## 🔍 What to Watch For

Once you apply these settings:

1. **Market Conditions Page**:
   - Should see more green checkmarks ✓
   - Confidence scores above 50%
   - Volume ratio above 1.2x

2. **Positions Page**:
   - Trades should appear within minutes/hours
   - Multiple positions possible (up to your max)

3. **Trade History Page**:
   - Will show completed trades
   - See entry/exit prices, P&L

## 📊 Expected Trade Frequency

With testing settings:
- **Previous (strict)**: 0-2 trades/week
- **Testing (loose)**: 5-20+ trades/day

With current market conditions (BTC RSI 97 = overbought), you might still need to wait for:
- RSI to come down to your ranges
- Volume spike to occur
- Price movement to align with EMA

## 🎯 If Still No Trades

If even with these loose settings you see no trades:

1. **Check Bot Status**: Must be "RUNNING" (not stopped/paused)
2. **Check Market Conditions Page**: See what's blocking
3. **Wait for Market Movement**: Crypto markets can be slow
4. **Try Different Pair**: ETH might have different conditions than BTC

## 🔄 Reverting to Production Settings

When done testing, change back to:

```
Volume Multiplier: 1.4-1.5
Minimum Confidence Score: 60-65%
Long Entry RSI Min: 54-55
Long Entry RSI Max: 70-72
Short Entry RSI Min: 28-30
Short Entry RSI Max: 45-46
Max Positions: 2-3
EMA Period: 50
```

These provide good balance of quality and frequency.

