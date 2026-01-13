# Test Trade Endpoint Documentation

## Overview

The `/api/test/force-trade` endpoint allows you to manually execute a test trade to validate the entire trading pipeline, including:
- Exchange API connection
- Order creation logic
- Trade logging to database
- Complete pipeline from order → execution → database storage

## Endpoint Details

**URL:** `POST /api/test/force-trade`

**Authentication:** Required (same as other API endpoints)

**Content-Type:** `application/json`

## Request Parameters

```json
{
  "symbol": "BTC-USD",        // Trading pair (default: "BTC-USD")
  "side": "BUY",              // "BUY" or "SELL" (default: "BUY")
  "amount_usdt": 10.0,        // Amount in USD (default: 10.0)
  "paper_trading": true       // Paper trading mode (default: true, SAFE)
}
```

### Parameter Details

- **symbol** (string, optional): Trading pair in format `BTC-USD`, `ETH-USD`, etc. Default: `BTC-USD`
- **side** (string, optional): `"BUY"` or `"SELL"`. Default: `"BUY"`
- **amount_usdt** (float, optional): Amount in USD to trade. Default: `10.0`
- **paper_trading** (boolean, optional): If `true`, executes paper trade (safe, simulated). If `false`, executes real trade. **Default: `true` (SAFE)**

## Safety Features

✅ **Defaults to Paper Trading** - The endpoint defaults to `paper_trading=true` to prevent accidental real trades

✅ **Real Trade Limits** - Real trades are limited to $100 maximum for safety

✅ **Full Validation** - Validates all inputs before execution

✅ **Comprehensive Logging** - Logs every step of the process for debugging

## Response Format

### Success Response (200 OK)

```json
{
  "success": true,
  "message": "Test trade executed successfully (PAPER mode)",
  "trade": {
    "trade_id": 123,
    "symbol": "BTC-USD",
    "side": "BUY",
    "quantity": 0.0002,
    "price": 50000.00,
    "total_usdt": 10.0,
    "order_id": "paper-1234567890-1234",
    "mode": "PAPER",
    "timestamp": "2025-01-15T10:30:00.000000"
  },
  "order_result": {
    "order_id": "paper-1234567890-1234",
    "status": "FILLED",
    ...
  }
}
```

### Error Responses

**400 Bad Request** - Invalid parameters
```json
{
  "error": "Side must be BUY or SELL"
}
```

**500 Internal Server Error** - Execution failed
```json
{
  "error": "Trade execution failed: Insufficient balance",
  "success": false
}
```

**503 Service Unavailable** - Bot not initialized
```json
{
  "error": "Trading bot is not running. Please start the bot using: python main.py"
}
```

## Usage Examples

### Example 1: Paper Trade Test (Safe)

```bash
curl -X POST "https://your-railway-url.up.railway.app/api/test/force-trade" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -d '{
    "symbol": "BTC-USD",
    "side": "BUY",
    "amount_usdt": 10.0,
    "paper_trading": true
  }'
```

### Example 2: Test with JavaScript/Fetch

```javascript
const response = await fetch('/api/test/force-trade', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
    'Authorization': `Bearer ${authToken}`
  },
  body: JSON.stringify({
    symbol: 'BTC-USD',
    side: 'BUY',
    amount_usdt: 10.0,
    paper_trading: true
  })
});

const result = await response.json();
console.log('Test trade result:', result);
```

### Example 3: Test SELL Order

```bash
curl -X POST "https://your-railway-url.up.railway.app/api/test/force-trade" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -d '{
    "symbol": "ETH-USD",
    "side": "SELL",
    "amount_usdt": 5.0,
    "paper_trading": true
  }'
```

## What Gets Validated

When you call this endpoint, it validates:

1. ✅ **Exchange Connection** - Verifies the bot can connect to the exchange
2. ✅ **Market Data** - Fetches current price for the trading pair
3. ✅ **Order Placement** - Places order via exchange client
4. ✅ **Database Storage** - Saves trade to database
5. ✅ **Complete Pipeline** - Tests the entire flow from request to database

## Important Notes

⚠️ **Paper Trading vs Live Trading**
- `paper_trading: true` (default) - Safe, simulated trades. No real money at risk.
- `paper_trading: false` - **REAL TRADES**. Only use when you want to execute real trades.

⚠️ **Real Trade Safety**
- Real trades are limited to $100 maximum
- Always test with paper trading first
- Verify your exchange API keys are configured correctly

⚠️ **Bot Must Be Running**
- The bot instance must be running (`python main.py`)
- API-only mode (`python app.py`) will return 503 error

## Troubleshooting

### Error: "Trading bot is not running"
- **Solution:** Start the bot using `python main.py` (not `app.py`)

### Error: "Could not fetch market data"
- **Solution:** Check that the trading pair symbol is correct (e.g., `BTC-USD`, not `BTCUSDT`)
- Verify exchange connection is working

### Error: "Insufficient balance"
- **Solution:** In paper trading, check `ACCOUNT_SIZE` in config
- In live trading, ensure you have sufficient funds in your exchange account

### Trade Not Saved to Database
- **Solution:** Check database connection and logs
- Verify `db_manager` is initialized

## Integration with Testing

This endpoint is perfect for:
- ✅ Validating exchange integration after setup
- ✅ Testing order placement logic
- ✅ Verifying database trade logging
- ✅ End-to-end pipeline testing
- ✅ Debugging trade execution issues

## Related Endpoints

- `GET /api/trades` - View all trades (including test trades)
- `GET /api/status` - Check bot status
- `GET /api/positions` - View open positions

