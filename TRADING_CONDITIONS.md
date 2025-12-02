# Trading Conditions & Metrics

## 📊 Entry Requirements for Trades

Your bot uses **EMA + RSI + Volume** strategy with strict confidence scoring. Here are the exact requirements:

### 🔵 LONG Entry Conditions (Buy Signal)

ALL of these must be true:

1. **Price > EMA(50)**
   - Current price must be above the 50-period Exponential Moving Average
   - This indicates an uptrend

2. **RSI between 55-70**
   - Relative Strength Index must be between 55 and 70
   - Below 55 = not bullish enough
   - Above 70 = overbought (too risky)

3. **Volume > 1.5x Average**
   - Current volume must be at least 1.5 times the 20-period average
   - Confirms the move has momentum

4. **Confidence Score ≥ 70%**
   - Must meet minimum confidence threshold
   - Confidence is calculated from:
     - Price distance from EMA: 0-30 points
     - RSI position in range: 0-40 points (peaks at middle)
     - Volume confirmation: 0-30 points

### 🔴 SHORT Entry Conditions (Sell Signal)

ALL of these must be true:

1. **Price < EMA(50)**
   - Current price must be below the 50-period EMA
   - This indicates a downtrend

2. **RSI between 30-45**
   - Relative Strength Index must be between 30 and 45
   - Above 45 = not bearish enough
   - Below 30 = oversold (too risky)

3. **Volume > 1.5x Average**
   - Current volume must be at least 1.5 times the 20-period average

4. **Confidence Score ≥ 70%**
   - Must meet minimum confidence threshold

## 🎯 Why You Might Not See Trades

### Common Reasons:

1. **Not Enough Historical Data**
   - Needs at least 50+ candles for EMA(50) calculation
   - Needs 20+ candles for volume average
   - Bot needs time to accumulate candle data

2. **Market Conditions Don't Meet Criteria**
   - RSI might be outside the 55-70 (long) or 30-45 (short) range
   - Volume might not be 1.5x average (needs volume spike)
   - Price might be too close to EMA (low confidence)

3. **Confidence Score Too Low**
   - Even if basic conditions met, confidence might be < 70%
   - This is by design to only trade high-probability setups

4. **Bot Status**
   - Bot must be in "running" status (not paused/stopped)
   - Check dashboard or API status

5. **Already Has Positions**
   - Max 2 positions allowed
   - Won't open new position if already at max

## 🔍 How to Check Current Conditions

I'll create a diagnostic endpoint to show current market conditions vs requirements.
