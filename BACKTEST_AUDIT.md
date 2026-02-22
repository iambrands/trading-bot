# Backtest Engine Audit: Why Only Losses

## Root Cause: Fee vs Profit Target Mismatch

The backtest applies **1.2% round-trip fees** (0.6% per side, Coinbase) but the strategy uses **0.50%–0.75% take-profit** targets.

### The Math

| Scenario | Price Move | Fees | Net P&L |
|----------|------------|------|---------|
| **Take profit hit** | +0.5% to +0.75% | -1.2% | **-0.45% to -0.70% (LOSS)** |
| **Stop loss hit** | -0.25% to -0.50% | -1.2% | **-1.45% to -1.70% (LOSS)** |
| **Timeout exit** | ~0% | -1.2% | **~-1.2% (LOSS)** |

**Every single trade loses money** because profit targets are below fee cost.

### Code Location

- **backtest_engine.py:219-221** – Hardcoded `fee_rate = 0.006` (Coinbase)
- **config.py** – `TAKE_PROFIT_MIN = 0.50`, `TAKE_PROFIT_MAX = 0.75`
- **config.py** – `EXCHANGE` can be `binance` (0.1%) or `coinbase` (0.6%)

### Strategy Was Designed for Binance

- Binance: 0.2% round trip → TP 0.5% = **+0.3% net profit** ✓
- Coinbase: 1.2% round trip → TP 0.5% = **-0.7% net loss** ✗

The backtest always used Coinbase fees regardless of `config.EXCHANGE`.

## Fix Applied

The backtest now uses exchange-aware fees:
- `EXCHANGE=binance` → 0.1% per side (0.2% round trip) → TP 0.5% yields ~+0.3% net
- `EXCHANGE=coinbase` or default → 0.6% per side (1.2% round trip) → TP 0.5% yields ~-0.7% net

**To get profitable backtest results:** Set `EXCHANGE=binance` in your env (or Railway variables). The strategy is tuned for Binance fees.

**If using Coinbase:** Backtest losses are accurate – the strategy would need higher TP targets (e.g. 1.5%+) to overcome 1.2% fees.
