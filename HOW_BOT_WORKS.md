# How TradePilot Stays Running & What It Looks For

## 🔄 How the Bot Stays Running

### Main Execution Loop
The bot runs continuously in a **trading loop** that repeats every **3-5 seconds** (configurable via `LOOP_INTERVAL_SECONDS`):

```
1. Bot Starts (main.py)
   ↓
2. Initialize Components
   - Database connection
   - Exchange/Coinbase connection
   - WebSocket for real-time data
   - Load initial candle data (last 24 hours)
   ↓
3. Enter Trading Loop (_trading_loop)
   ↓
4. Repeat Every 3-5 Seconds:
   ├─ Update candle data (if needed)
   ├─ Check & manage existing positions
   ├─ Check daily loss limit
   ├─ Check for NEW trading signals (if running)
   ├─ Update performance metrics
   └─ Wait 3-5 seconds, repeat
   ↓
5. Bot Stops (when stopped manually or error)
```

### Key Components That Keep It Running:

1. **Trading Loop** (`main.py`, line 199-256)
   - Runs in `while self.running` loop
   - Checks conditions every `LOOP_INTERVAL_SECONDS` (default: 5 seconds, yours: 3 seconds)
   - Continues until `bot.stop()` is called or error occurs

2. **Market Data Updates**
   - WebSocket connection for real-time price updates
   - Candle data cached in memory
   - Refreshed periodically (when cache < 100 candles)

3. **Position Management**
   - Continuously monitors open positions
   - Checks exit conditions (stop loss, take profit, timeout)
   - Updates prices in real-time

4. **Status Check**
   - Bot must be in `status = 'running'` to generate new signals
   - If `status = 'paused'` or `'stopped'`, it only manages existing positions

---

## 🎯 What the Bot Looks For to Create a Trade

The bot uses a **EMA + RSI + Volume** strategy with strict confidence scoring. Here's exactly what it checks:

### For a LONG (Buy) Trade - ALL conditions must be true:

1. **Price Above EMA(50)**
   - Current price > 50-period Exponential Moving Average
   - Indicates uptrend

2. **RSI in Range (55-70)**
   - RSI must be between 55 and 70
   - Your settings: Min=55, Max=70
   - Below 55 = not bullish enough
   - Above 70 = overbought (too risky)

3. **Volume Spike**
   - Current volume ≥ **Volume Multiplier × Average Volume**
   - Your setting: **1.6×** (very strict!)
   - Default: 1.5×
   - Confirms the move has momentum

4. **Confidence Score ≥ Minimum Threshold**
   - Your setting: **70%** (very strict!)
   - Confidence calculated from:
     - **Price distance from EMA** (0-30 points)
       - Needs price to be far enough from EMA
       - ~2%+ distance for full points
     - **RSI position in range** (0-40 points)
       - Peaks at middle of range (62.5 for LONG)
       - Fewer points near edges (55 or 70)
     - **Volume confirmation** (0-30 points)
       - Requires volume_ratio ≥ volume_multiplier
       - More volume = more points (up to 30)

5. **Risk Management Checks**
   - Not at max positions limit (your setting: 2)
   - Not exceeded daily loss limit ($2,000)
   - Position size calculated and validated
   - Sufficient account balance

6. **No Existing Position**
   - Won't open duplicate position in same pair

### For a SHORT (Sell) Trade - ALL conditions must be true:

1. **Price Below EMA(50)**
   - Current price < 50-period EMA
   - Indicates downtrend

2. **RSI in Range (30-45)**
   - RSI must be between 30 and 45
   - Your settings: Min=30, Max=45
   - Above 45 = not bearish enough
   - Below 30 = oversold (too risky)

3. **Volume Spike**
   - Same as LONG: Volume ≥ 1.6× average

4. **Confidence Score ≥ 70%**
   - Same calculation, but for SHORT conditions

5. **Same Risk Management Checks**

6. **No Existing Position**

---

## 📊 Confidence Score Calculation

The confidence score is the **total points** from three factors:

### For LONG:
- **Price Distance** (0-30 pts): `((price - EMA) / EMA) × 100`
  - 0% distance = 0 points
  - 2%+ distance = 30 points max
  
- **RSI Position** (0-40 pts): Position within your RSI range (55-70)
  - Middle (62.5) = 40 points (peak)
  - Edges (55 or 70) = 0 points
  
- **Volume** (0-30 pts): `((volume_ratio - multiplier) / multiplier) × 30`
  - Exactly 1.6× = 0 points (minimum)
  - Higher volume = more points (up to 30)

**Total = Price + RSI + Volume (max 100%)**

### For SHORT:
- Same calculation, but price distance is `(EMA - price) / EMA`
- RSI range is 30-45 (peak at 37.5)

---

## 🔍 Why You Might Not See Trades

Your current settings are **very strict**, which limits trade frequency:

1. **Volume Multiplier: 1.6** ⚠️
   - More restrictive than default (1.5)
   - 1.6× volume spikes are less common
   - **Biggest limiting factor**

2. **Minimum Confidence: 70%** ⚠️
   - Requires ALL three factors to be strong
   - Price must be far from EMA
   - RSI must be near middle of range
   - Volume must be well above threshold

3. **Narrow RSI Ranges**
   - Long: Only 55-70 (15 point window)
   - Short: Only 30-45 (15 point window)
   - Market might not stay in these ranges long

4. **Max Positions: 2**
   - Once you have 2 positions, no new trades until one closes

5. **Market Conditions**
   - Needs trending market with volume spikes
   - Choppy/consolidating markets won't trigger

6. **Insufficient Data**
   - Needs 50+ candles for EMA(50)
   - Needs 20+ candles for volume average
   - Bot needs time to accumulate data

---

## 🎛️ The Complete Flow

```
Every 3-5 Seconds:
│
├─ 1. Update Market Data
│   └─ Get latest prices, update candles
│
├─ 2. Manage Existing Positions
│   ├─ Check current price vs stop loss/take profit
│   ├─ Check position timeout (10 min max)
│   └─ Close position if exit condition met
│
├─ 3. Check Daily Loss Limit
│   └─ If exceeded → Close all positions, pause bot
│
├─ 4. If Status = "running" → Check for NEW Signals
│   │
│   └─ For Each Trading Pair (BTC-USD, ETH-USD, etc):
│       ├─ Load candle data (50+ candles needed)
│       ├─ Calculate indicators:
│       │   ├─ EMA(50)
│       │   ├─ RSI(14)
│       │   └─ Volume average (20-period)
│       │
│       ├─ Check Entry Conditions:
│       │   ├─ Price vs EMA ✓
│       │   ├─ RSI in range ✓
│       │   ├─ Volume ≥ 1.6× average ✓
│       │   ├─ Calculate confidence score
│       │   └─ Confidence ≥ 70% ✓
│       │
│       ├─ Risk Management Checks:
│       │   ├─ Not at max positions (2)
│       │   ├─ Not exceeded daily loss limit
│       │   ├─ Calculate position size
│       │   └─ Validate trade
│       │
│       └─ If ALL pass → Open Position
│           ├─ Place order on exchange
│           ├─ Create position record
│           ├─ Save to database
│           └─ Send alert
│
└─ 5. Wait 3-5 seconds, repeat
```

---

## 💡 Key Takeaways

1. **Bot runs continuously** - Checks every 3-5 seconds while running
2. **Very strict entry criteria** - All 4+ conditions must be perfect
3. **Your settings are conservative** - Volume 1.6 and Confidence 70% limit trades
4. **Needs trending markets** - Choppy/consolidating markets won't trigger
5. **Position management is separate** - Exit checks happen independently

The bot is designed to wait for **high-quality setups only**. Your current settings make it even more selective, which is why you might not see many trades.

