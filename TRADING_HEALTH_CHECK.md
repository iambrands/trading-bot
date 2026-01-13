# Trading System Health Check Endpoint

## Overview

The `/api/test/trading-health` endpoint provides a comprehensive health check for all trading system components. It's a single endpoint that shows the current state of:
- Exchange connection and balance
- Trading configuration/thresholds
- Recent trading activity
- Market data availability
- Database connectivity
- Bot status

## Endpoint Details

**URL:** `GET /api/test/trading-health`

**Authentication:** Required (same as other API endpoints)

**Method:** GET (no request body needed)

## Response Format

### Success Response (200 OK)

```json
{
  "timestamp": "2025-01-15T10:30:00.000000",
  "status": "ok",
  "bot_status": {
    "status": "running",
    "mode": "full-bot",
    "paper_trading": true
  },
  "exchange_connection": {
    "status": "ok",
    "balance_usdt": 100000.0,
    "paper_trading": true
  },
  "thresholds": {
    "rsi_long_range": "50-75",
    "rsi_short_range": "25-50",
    "volume_multiplier": 1.2,
    "min_confidence_score": 65,
    "take_profit_min": 0.5,
    "take_profit_max": 0.75,
    "stop_loss_min": 0.25,
    "stop_loss_max": 0.5
  },
  "trades_24h": {
    "count": 5,
    "status": "ok"
  },
  "market_data": {
    "status": "ok",
    "btc_price_usd": 50000.0,
    "timestamp": "2025-01-15T10:29:45.000000"
  },
  "database": {
    "status": "ok",
    "initialized": true
  },
  "positions": {
    "count": 2,
    "status": "ok"
  }
}
```

### Degraded Status (200 OK, but status="degraded")

When some components are unavailable (e.g., API-only mode):

```json
{
  "timestamp": "2025-01-15T10:30:00.000000",
  "status": "degraded",
  "bot_status": {
    "status": "not_initialized",
    "message": "Trading bot instance not available (API-only mode)"
  },
  "exchange_connection": {
    "status": "not_available",
    "message": "Bot not initialized - cannot check exchange",
    "balance_usdt": 100000.0
  },
  "thresholds": {
    "rsi_long_range": "50-75",
    ...
  },
  ...
}
```

### Error Status (500 Internal Server Error)

When critical errors occur:

```json
{
  "timestamp": "2025-01-15T10:30:00.000000",
  "status": "error",
  "exchange_connection": {
    "status": "error",
    "error": "Connection timeout"
  },
  ...
}
```

## Response Fields

### Overall Status

- **`status`** (string): Overall system status
  - `"ok"` - All components healthy
  - `"degraded"` - Some components unavailable (e.g., API-only mode)
  - `"error"` - Critical errors detected

### Component Status Objects

Each component returns a status object with:
- **`status`** (string): Component status (`"ok"`, `"error"`, `"not_available"`, etc.)
- **Component-specific fields**: Additional data for that component
- **`error`** (string, optional): Error message if status is "error"
- **`message`** (string, optional): Informational message

### Components Checked

1. **`bot_status`**
   - Bot initialization status
   - Current bot status (running/stopped/paused)
   - Mode (full-bot/api-only)
   - Paper trading status

2. **`exchange_connection`**
   - Exchange API connectivity
   - Account balance (USD)
   - Paper trading mode indicator

3. **`thresholds`**
   - Current trading configuration
   - RSI ranges (long/short)
   - Volume multiplier
   - Confidence score threshold
   - Profit/stop loss ranges

4. **`trades_24h`**
   - Count of trades in last 24 hours
   - Database connectivity status

5. **`market_data`**
   - Current BTC-USD price
   - Market data timestamp
   - Data availability status

6. **`database`**
   - Database connection status
   - Initialization status

7. **`positions`**
   - Count of active/open positions
   - Position tracking status

## Usage Examples

### Example 1: Basic Health Check

```bash
curl -X GET "https://your-railway-url.up.railway.app/api/test/trading-health" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

### Example 2: JavaScript/Fetch

```javascript
const response = await fetch('/api/test/trading-health', {
  method: 'GET',
  headers: {
    'Authorization': `Bearer ${authToken}`
  }
});

const health = await response.json();
console.log('System status:', health.status);
console.log('Balance:', health.exchange_connection.balance_usdt);
console.log('Recent trades:', health.trades_24h.count);
```

### Example 3: Monitoring Script

```bash
#!/bin/bash
HEALTH_URL="https://your-railway-url.up.railway.app/api/test/trading-health"
TOKEN="YOUR_TOKEN"

response=$(curl -s -X GET "$HEALTH_URL" \
  -H "Authorization: Bearer $TOKEN")

status=$(echo $response | jq -r '.status')
balance=$(echo $response | jq -r '.exchange_connection.balance_usdt')
trades=$(echo $response | jq -r '.trades_24h.count')

echo "Status: $status"
echo "Balance: \$$balance"
echo "Trades (24h): $trades"

if [ "$status" != "ok" ]; then
  echo "⚠️  WARNING: System status is $status"
  exit 1
fi
```

## Status Interpretation

### Status: "ok"
- All components are functioning normally
- Bot is running (if applicable)
- Exchange connection is active
- Database is accessible
- Market data is available

### Status: "degraded"
- Some components are unavailable but not critical
- Common causes:
  - API-only mode (bot not initialized)
  - Database not initialized
  - Some services unavailable but system still functional

### Status: "error"
- Critical errors detected
- Common causes:
  - Exchange connection failure
  - Database connection error
  - Configuration errors

## Use Cases

### 1. Quick System Check
Use this endpoint to quickly verify all system components are working:

```bash
curl "https://your-url/api/test/trading-health" | jq '.status'
```

### 2. Monitoring & Alerts
Set up monitoring to check this endpoint periodically and alert on errors:

```bash
# Check every 5 minutes
*/5 * * * * curl -s "https://your-url/api/test/trading-health" | jq -e '.status == "ok"' || send_alert
```

### 3. Debugging
When troubleshooting issues, check this endpoint to identify which component is failing:

```bash
curl "https://your-url/api/test/trading-health" | jq '{
  status: .status,
  exchange: .exchange_connection.status,
  database: .database.status,
  bot: .bot_status.status
}'
```

### 4. Dashboard Integration
Display key metrics from the health check in your dashboard:

```javascript
const health = await fetch('/api/test/trading-health').then(r => r.json());

// Display metrics
document.getElementById('balance').textContent = `$${health.exchange_connection.balance_usdt}`;
document.getElementById('trades-24h').textContent = health.trades_24h.count;
document.getElementById('btc-price').textContent = `$${health.market_data.btc_price_usd}`;
```

## Related Endpoints

- `GET /api/status` - Basic bot status
- `GET /api/trades` - List all trades
- `GET /api/positions` - View open positions
- `POST /api/test/force-trade` - Execute test trade
- `GET /api/market-conditions` - Detailed market analysis

## Notes

- **No Side Effects**: This endpoint is read-only and doesn't modify any system state
- **Fast Response**: Designed to return quickly for monitoring purposes
- **Authentication Required**: Same authentication as other API endpoints
- **User-Specific Data**: Trades count is filtered by authenticated user (if applicable)

