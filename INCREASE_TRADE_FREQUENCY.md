# How to Increase Trade Frequency in TradePilot

Based on your current settings and the trading strategy logic, here are specific recommendations to get more trades:

## 🎯 Current Settings Analysis

Your current settings that are limiting trades:
- **Volume Multiplier: 1.6** ⚠️ (More restrictive than default 1.5)
- **Minimum Confidence Score: 70%** (Default, but can be lowered)
- **RSI Ranges**: Long 55-70, Short 30-45 (Standard ranges)
- **Max Positions: 2** (Limits simultaneous trades)

## 📊 How Confidence Score Works

The confidence score is calculated from three factors (max 100 points):
1. **Price Distance from EMA** (0-30 points)
   - Price must be far enough from EMA to get full points
   - Needs ~2%+ distance for full 30 points
2. **RSI Position in Range** (0-40 points)
   - Peaks at the middle of your RSI range (62.5 for LONG, 37.5 for SHORT)
   - Gets fewer points near the edges
3. **Volume Confirmation** (0-30 points)
   - Requires volume_ratio >= volume_multiplier
   - More volume = more points (up to 30)

**All three conditions must be met, AND total confidence must be ≥ your minimum threshold.**

## ✅ Recommended Changes to Get More Trades

### Priority 1: Lower Volume Multiplier ⭐ (Biggest Impact)
**Current: 1.6 → Recommended: 1.4**

Why: Your volume multiplier of 1.6 is actually MORE restrictive than the default (1.5). Volume spikes of 1.6x are less common than 1.5x. Lowering to 1.4 will:
- Increase the number of volume-confirmed signals
- Still maintain quality (1.4x is still significant volume)
- **Estimated impact: +30-50% more trade opportunities**

### Priority 2: Lower Minimum Confidence Score ⭐⭐ (Very High Impact)
**Current: 70% → Recommended: 60-65%**

Why: The 70% threshold is quite strict. Lowering to 60-65% will:
- Allow trades when conditions are good but not perfect
- Still filter out poor-quality setups
- **Estimated impact: +40-70% more trades**

**Conservative approach**: Start with 65%, then adjust to 60% if you want even more trades.

### Priority 3: Widen RSI Entry Ranges (Moderate Impact)
**Current Ranges:**
- Long: 55-70 (15 point range)
- Short: 30-45 (15 point range)

**Recommended Ranges:**
- Long: 52-72 (20 point range) - More bullish opportunities
- Short: 28-48 (20 point range) - More bearish opportunities

Why: Wider ranges capture more market conditions while still avoiding extremes (overbought/oversold zones).
- **Estimated impact: +20-30% more trade opportunities**

### Priority 4: Increase Max Positions (If you want more simultaneous trades)
**Current: 2 → Recommended: 3-4**

Why: Allows more simultaneous positions, so when multiple pairs meet criteria, all can trade.
- Only increases trades if multiple pairs are signaling at once
- **Estimated impact: +0-50% depending on market conditions**

## 🎯 Quick Action Plan

### For Maximum Trades (More Aggressive):
1. Volume Multiplier: **1.4** (from 1.6)
2. Minimum Confidence: **60%** (from 70%)
3. Long RSI Range: **52-72** (from 55-70)
4. Short RSI Range: **28-48** (from 30-45)
5. Max Positions: **3** (from 2)

### For Balanced (Moderate Increase):
1. Volume Multiplier: **1.5** (from 1.6) - Back to default
2. Minimum Confidence: **65%** (from 70%)
3. Long RSI Range: **54-72** (from 55-70)
4. Short RSI Range: **28-46** (from 30-45)
5. Max Positions: **2** (keep as is)

### For Conservative (Slight Increase):
1. Volume Multiplier: **1.5** (from 1.6) - Back to default
2. Minimum Confidence: **68%** (from 70%)
3. Keep RSI ranges as is
4. Max Positions: **2** (keep as is)

## 📈 Expected Trade Frequency Changes

**Current settings** (Volume 1.6, Confidence 70%):
- Very selective, high-quality signals only
- May see 0-2 trades per day in normal market conditions

**Balanced settings** (Volume 1.5, Confidence 65%):
- Good quality with more opportunities
- May see 3-8 trades per day

**Maximum settings** (Volume 1.4, Confidence 60%):
- More frequent signals, slightly lower average quality
- May see 5-15+ trades per day

## ⚠️ Important Notes

1. **More trades ≠ Better performance**: Lower quality trades may reduce overall win rate
2. **Test first**: Use paper trading to test new settings before going live
3. **Monitor win rate**: If win rate drops below 50%, increase confidence back up
4. **Volume multiplier matters most**: Your current 1.6 is the biggest limiting factor
5. **Bot must be running**: Ensure bot status is "running" (not stopped/paused)

## 🔍 How to Check Current Market Conditions

1. Go to **Market Conditions** page
2. Check the confidence scores for each pair
3. See which conditions are blocking trades
4. Adjust settings based on what you see

## 💡 Pro Tips

- **Volume Multiplier of 1.6** is your biggest blocker - this alone will significantly increase trades
- **Confidence 60-65%** is still quite selective (80+ is very conservative, 50-55 is aggressive)
- **RSI ranges** - Slightly wider ranges capture more opportunities without sacrificing much quality
- **Monitor the Market Conditions page** to see real-time why trades aren't triggering

## 🚀 Recommended Starting Point

**Best balance of frequency and quality:**
- Volume Multiplier: **1.4** ⭐
- Minimum Confidence: **65%** ⭐
- Long RSI: **54-72**
- Short RSI: **28-46**
- Max Positions: **3**

This should increase your trade frequency by 2-3x while maintaining reasonable quality standards.

