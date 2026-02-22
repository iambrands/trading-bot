# TradePilot Audit: $0.00 P&L & No Trades Triggering

**Date:** February 2026  
**Scope:** Position P&L display, signal generation, and trade execution flow  
**Status:** Audit complete; fixes applied for critical issues

---

## Fixes Applied

| Issue | Fix |
|-------|-----|
| `should_exit` used wrong key | `strategy/base.py`, `ema_rsi_strategy.py` – use `position.get('side', position.get('signal_type', 'LONG'))` |
| P&L $0 when position pair not in market fetch | `api/rest_api.py` – fetch market data for `TRADING_PAIRS ∪ position pairs` |
| No visibility when fallback used | `api/rest_api.py` – log warning when no market price for position pair |

---

## Executive Summary

Two issues were audited:
1. **Position P&L showing $0.00** – Root cause: fallback to `entry_price` when market data is missing or stale
2. **No trades being executed** – Multiple potential blockers; one confirmed bug in `should_exit`

---

## 1. Position P&L Showing $0.00

### Flow

```
GET /api/positions → get_positions() → get_market_data(TRADING_PAIRS)
→ current_price = market_data[pair].price or entry_price (fallback)
→ pnl = (current_price - entry_price) * size
```

### Root Causes

| Cause | Location | Explanation |
|-------|----------|-------------|
| **Fallback to entry_price** | `api/rest_api.py:734` | When `market_data.get(pair, {}).get('price')` is missing, falls back to `entry_price` → P&L = 0 |
| **Pair not in TRADING_PAIRS** | `rest_api.py:730` | Market data is fetched only for `TRADING_PAIRS`. If position pair was removed from config, no price returned |
| **Coinbase product book** | `exchange/coinbase_client.py:248` | API call format (GET vs POST) may not match Coinbase spec; failures → cached/synthetic data |
| **Stale cache** | `coinbase_client.py:312-321` | Falls back to `self.market_data[pair]` or synthetic price when fetch fails |
| **Display rounding** | Frontend | Tiny P&L (e.g. $0.003) may round to $0.00 |

### Fixes

1. **Add logging** when fallback is used:
   ```python
   if pair not in market_data or not market_data.get(pair, {}).get('price'):
       logger.warning(f"Position {pair}: No market price, using entry_price (P&L=$0)")
   ```
2. **Fetch market data for position pairs** explicitly, not only `TRADING_PAIRS`
3. **Verify Coinbase product_book** endpoint usage (method, params, response parsing)

---

## 2. System Not Triggering Trades

### Flow

```
_trading_loop() every 5s → _check_signals() when status=='running'
→ strategy.generate_signal(candles, pair)
→ validate_trade() → _open_position()
```

### Block Points

| Block Point | File | Condition |
|-------------|------|-----------|
| Candle count | `main.py:381-386` | `len(candles) < 51` (EMA 50 + 1) |
| LONG conditions | `ema_rsi_strategy.py:273-293` | Price > EMA, RSI in [45-80], Volume ≥ 0.9× avg |
| SHORT conditions | `ema_rsi_strategy.py:313-345` | Price < EMA, RSI in [20-55], Volume ≥ 0.9× avg |
| Confidence | `main.py:416-417` | `signal_conf < 60%` |
| Existing position | `main.py:419-423` | Already in same pair |
| Risk validation | `risk/risk_manager.py:84-117` | Daily loss limit, max positions (2), position size |

### Confirmed Bug: `should_exit` uses wrong key

**File:** `strategy/ema_rsi_strategy.py` (and `strategy/base.py`)

Positions store the side as `position['side']`, but `should_exit` uses:
```python
signal_type = position.get('signal_type', 'LONG')  # BUG: should be 'side'
```

Positions are created with `'side': signal['type']` in `main.py`. The key `'signal_type'` does not exist, so SHORT positions are treated as LONG for exit logic.

**Fix:** Use `position.get('side', 'LONG')`.

### Diagnostics

- **GET /api/market-conditions** – Shows indicator values, blockers, and `ready_to_trade` per pair. Use to see why trades aren’t firing.
- **Logs** – `main.py` and `ema_rsi_strategy.py` have `print(..., stderr)` and `logger.info` for signal checks and blockers.

---

## 3. Recommended Actions

### Immediate

1. Fix `should_exit` to use `position.get('side', 'LONG')`
2. Add P&L fallback logging in `get_positions`
3. Ensure `get_market_data` is called with the exact position pairs (or all active pair IDs)

### Short-term

4. Validate Coinbase `product_book` / market data API usage
5. Call `/api/market-conditions` and review blockers for your pairs
6. Check strategy params: `MIN_CONFIDENCE_SCORE` (60), `VOLUME_MULTIPLIER` (0.9), RSI ranges

### Monitoring

7. Confirm `candle_cache` is populated (`_load_candle_data`, WebSocket updates)
8. Confirm bot status is `running` (not `paused` or `stopped`)
