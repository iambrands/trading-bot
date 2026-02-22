# Backtest Strategy Overrides & CryptoHopper Comparison

## Strategy Overrides When Running Backtests

You can test different strategy parameters **without changing global Settings** by using **Strategy overrides** on the Backtest page.

### Where to find it

1. Go to **Backtest** in the sidebar.
2. In the **Custom Backtest** form, click **▶ Strategy overrides (optional)** to expand.
3. Fill only the fields you want to override; leave others blank to use your current Settings.

### Overridable parameters

| Field | Description | Example |
|-------|-------------|---------|
| **EMA period** | EMA lookback (e.g. 50) | 50 |
| **RSI period** | RSI lookback (e.g. 14) | 14 |
| **Volume mult.** | Min volume vs average (e.g. 0.9 = 90%) | 0.9 |
| **Min confidence %** | Minimum signal confidence to enter | 60 |
| **RSI long min/max** | RSI range for long entries | 45–80 |
| **RSI short min/max** | RSI range for short entries | 20–55 |
| **TP min % / TP max %** | Take profit range | 1.5–2 |
| **SL min % / SL max %** | Stop loss range | 0.5–0.75 |
| **Max positions** | Max open positions in the backtest | 2 |

- **Quick Run** (1/3/7 day) uses current Settings only (no overrides).
- **Custom Backtest** sends overrides only for fields you fill in; the rest come from Settings.

This lets you compare runs (e.g. EMA 30 vs 50, or different RSI ranges) to see what works best.

---

## What CryptoHopper Does (Comparison)

CryptoHopper is a third-party crypto trading bot platform. Here’s how it compares to TradePilot for backtesting and strategy tuning:

| Feature | CryptoHopper | TradePilot |
|--------|----------------|------------|
| **Backtest parameters** | Pair, strategy, take profit %, stop loss, trailing stop, date range | Pair, days, balance, name, plus **optional strategy overrides** (EMA, RSI, volume, TP/SL, confidence, etc.) |
| **Strategy design** | Strategy Designer with required/optional indicators, JSON editing | Built-in strategies (e.g. EMA+RSI); overrides per backtest run |
| **Comparing strategies** | Algorithm Intelligence: score/compare strategies, validation time, min profit % | Run multiple backtests with different overrides and compare results in the Previous Backtests table (Gross/Fees/Net, ROI, Win rate) |
| **Check interval** | Backtester checks every 5 min; live bot interval varies by plan (e.g. 2–20 min) | Backtest uses candle data (e.g. 1-min); live loop interval in Settings |
| **Fee model** | Depends on exchange / plan | Exchange-aware (Binance 0.2% rt / Coinbase 1.2% rt), shown in Fee model column |

TradePilot gives you **per-run strategy overrides** (EMA, RSI, TP/SL, etc.) so you can test “what if” scenarios without changing your live Settings, similar in spirit to tuning strategy parameters in CryptoHopper’s backtester and Strategy Designer.
