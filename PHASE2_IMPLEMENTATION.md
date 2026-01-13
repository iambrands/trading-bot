# Phase 2 Implementation - Binance Integration & Profit Targets

## ✅ Changes Completed

### 1. Exchange Configuration

**Added to `config.py`:**
- `EXCHANGE` - Exchange selection (binance or coinbase)
- `BINANCE_API_KEY` - Binance API key from environment
- `BINANCE_API_SECRET` - Binance API secret from environment
- `BINANCE_TESTNET` - Binance testnet mode (default: true for safety)

**Note:** Exchange factory (`exchange/exchange_factory.py`) already supports Binance - no changes needed there.

---

### 2. Profit Targets - FIXED FOR FEES ✅

**CRITICAL FIX:** Profit targets were below exchange fees, causing guaranteed losses!

**Before (BROKEN):**
```python
TAKE_PROFIT_MIN = 0.15%  # Below Coinbase fees (1.2%) ❌
TAKE_PROFIT_MAX = 0.40%  # Still below fees ❌
```

**After (FIXED):**
```python
TAKE_PROFIT_MIN = 0.50%  # Above Binance fees (0.2%) ✅
TAKE_PROFIT_MAX = 0.75%  # Profitable range ✅
```

**Fee Comparison:**
- **Binance:** 0.2% round trip (0.1% x 2)
- **Coinbase:** 1.2% round trip (0.6% x 2)

**Net Profit Calculation:**
- Binance: 0.50% - 0.20% = **0.30% net profit** ✅
- Coinbase: 0.50% - 1.20% = **-0.70% loss** ❌ (still unprofitable on Coinbase)

**Recommendation:** Use Binance for scalping (6x lower fees)

---

### 3. Fee Validation

**Added:**
- `VALIDATE_FEES_BEFORE_TRADE = True` - Validate profitability before trades
- `MIN_PROFIT_AFTER_FEES = 0.25%` - Minimum net profit after fees

**Purpose:** Prevents unprofitable trades from being executed.

---

### 4. Order Execution Settings

**Added:**
- `ORDER_TYPE = 'limit'` - Use limit orders (better fees)
- `LIMIT_ORDER_OFFSET_PCT = 0.02%` - Place orders inside spread
- `ORDER_TIMEOUT_SECONDS = 30` - Cancel unfilled orders
- `USE_POST_ONLY = True` - Maker orders only (lower fees)

**Purpose:** Optimize order execution for better fees and fills.

---

## 📊 Profitability Analysis

### Binance (Recommended)

**Scenario: 0.50% profit target**
- Entry: $100,000
- Exit: $100,500 (0.50% profit)
- Entry fee: $100 (0.1%)
- Exit fee: $100.50 (0.1%)
- Total fees: $200.50
- **Net profit: $299.50 (0.30%)** ✅

**Scenario: 0.75% profit target**
- Entry: $100,000
- Exit: $100,750 (0.75% profit)
- Entry fee: $100 (0.1%)
- Exit fee: $100.75 (0.1%)
- Total fees: $200.75
- **Net profit: $549.25 (0.55%)** ✅

### Coinbase (Not Recommended for Scalping)

**Scenario: 0.50% profit target**
- Entry: $100,000
- Exit: $100,500 (0.50% profit)
- Entry fee: $600 (0.6%)
- Exit fee: $603 (0.6%)
- Total fees: $1,203
- **Net loss: -$703 (-0.70%)** ❌

**Conclusion:** Coinbase fees (1.2%) exceed profit targets (0.50%), making scalping unprofitable.

---

## 🚀 Next Steps

### 1. Configure Binance API Keys

Add to `.env` file:
```bash
# Exchange Selection
EXCHANGE=binance

# Binance API (Get from: https://www.binance.com/en/my/settings/api-management)
BINANCE_API_KEY=your_binance_api_key_here
BINANCE_API_SECRET=your_binance_api_secret_here
BINANCE_TESTNET=true  # Always start with testnet!

# Keep Coinbase keys for backward compatibility (optional)
COINBASE_API_KEY=...
COINBASE_API_SECRET=...
```

### 2. Get Binance Testnet API Keys

1. Go to: https://testnet.binance.vision/
2. Create account (separate from main Binance)
3. Generate API keys
4. Add to `.env` file
5. Test connection before using live keys

### 3. Test Binance Connection

Use the exchange factory test:
```bash
python test_binance_connection.py
```

### 4. Update Trading Pairs (Optional)

Current pairs use Coinbase format (`BTC-USD`). Binance uses different format (`BTC/USDT`).

**Option A:** Keep current format (exchange factory handles conversion)
**Option B:** Update to Binance format in config

The exchange factory wrapper should handle format conversion automatically.

### 5. Monitor First Trades

After switching to Binance:
- Watch for signal generation
- Verify profit targets are 0.50%+
- Confirm trades are profitable after fees
- Monitor for 24-48 hours before going live

---

## ⚠️ Important Warnings

1. **ALWAYS use testnet first** (`BINANCE_TESTNET=true`)
2. **Never use live API keys for testing**
3. **Validate profitability** before going live
4. **Start small** ($1K-$2K) for first live trades
5. **Coinbase is NOT recommended** for scalping (fees too high)

---

## 📝 Configuration Summary

### Current Settings (After Phase 2)

```python
# Exchange
EXCHANGE = 'coinbase'  # Change to 'binance' to use Binance
BINANCE_TESTNET = True  # Start with testnet

# Profit Targets (FIXED)
TAKE_PROFIT_MIN = 0.50%  # Was 0.15% (BROKEN)
TAKE_PROFIT_MAX = 0.75%  # Was 0.40% (BROKEN)
STOP_LOSS_MIN = 0.25%
STOP_LOSS_MAX = 0.50%

# Fee Validation
VALIDATE_FEES_BEFORE_TRADE = True
MIN_PROFIT_AFTER_FEES = 0.25%

# Order Execution
ORDER_TYPE = 'limit'
USE_POST_ONLY = True
ORDER_TIMEOUT_SECONDS = 30
```

---

## ✅ Validation Checklist

- [x] Binance configuration added to config.py
- [x] Profit targets fixed (0.50% minimum)
- [x] Fee validation added
- [x] Order execution settings added
- [ ] Binance API keys configured (user action)
- [ ] Exchange factory tested with Binance (user action)
- [ ] First test trades executed (user action)

---

**Status:** ✅ Configuration Complete | Ready for Binance API Setup

