# Backtest: Compare Binance vs Coinbase Fee Impact

## How It Works

The backtest engine uses `EXCHANGE` from your config to apply exchange-specific fees:
- **EXCHANGE=binance** → 0.2% round trip (0.1% per side)
- **EXCHANGE=coinbase** → 1.2% round trip (0.6% per side)

Same strategy, same candles – only the fee rate changes.

## Steps to Compare

### 1. Set EXCHANGE for Binance backtest

**Local (.env):**
```
EXCHANGE=binance
```

**Railway:** Add variable `EXCHANGE` = `binance` in your project variables.

### 2. Restart the app

Restart so the new `EXCHANGE` value is loaded.

### 3. Run backtest

- Go to **Backtest** in the sidebar
- Pick pair (e.g. BTC-USD), days (e.g. 7), balance
- Click **Run Backtest**

You'll see results using Binance fees (~0.2% round trip).

### 4. Switch to Coinbase and rerun

- Set `EXCHANGE=coinbase` (or remove it; coinbase is default)
- Restart
- Run the same backtest (same pair, same days)

### 5. Compare

| Metric        | EXCHANGE=binance | EXCHANGE=coinbase |
|---------------|------------------|-------------------|
| Fees applied  | 0.2% round trip  | 1.2% round trip   |
| Net per TP hit| ~1.3%            | ~0.3%             |

Binance backtests should show higher P&L; Coinbase backtests show what to expect if you trade on Coinbase.

## Current Strategy (Coinbase-Optimized)

TP: 1.5%–2.0% | SL: 0.5%–0.75%

- **Coinbase:** TP 1.5% − 1.2% fees ≈ **+0.3% net** per winning trade  
- **Binance:** TP 1.5% − 0.2% fees ≈ **+1.3% net** per winning trade  
