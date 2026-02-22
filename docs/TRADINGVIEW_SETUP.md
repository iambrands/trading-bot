# TradingView Webhook Setup

Execute trades from TradingView alerts automatically.

## 1. Configure Environment

Add to Railway (or `.env`):

```
TRADINGVIEW_WEBHOOK_SECRET=your-random-secret-here
TRADINGVIEW_ORDER_SIZE_USD=50
```

- **TRADINGVIEW_WEBHOOK_SECRET**: Generate with `openssl rand -hex 24`. Required in production.
- **TRADINGVIEW_ORDER_SIZE_USD**: Default order size in USD when alert doesn't include amount (default: 50).

## 2. Webhook URL

Your webhook URL (use your Railway URL):

```
https://YOUR-APP.up.railway.app/api/webhooks/tradingview?secret=YOUR_SECRET
```

Or pass secret via header `X-Webhook-Secret: YOUR_SECRET`.

## 3. TradingView Alert Message

In TradingView, create an alert and set the **Webhook URL** to the URL above.

**Message format** (JSON):

```json
{
  "symbol": "{{ticker}}",
  "action": "{{strategy.order.action}}",
  "close": {{close}}
}
```

Or for custom amount:

```json
{
  "symbol": "{{ticker}}",
  "action": "{{strategy.order.action}}",
  "quote_size": 100
}
```

### Field Reference

| Field | Required | Description |
|-------|----------|-------------|
| symbol | Yes | e.g. `BTCUSD`, `BTC-USD`, `ETH/USD` |
| action | Yes | `buy`, `sell`, `long`, `short`, `1` (buy), `-1` (sell) |
| quote_size | No | USD amount (default: TRADINGVIEW_ORDER_SIZE_USD) |
| close | No | Price (informational) |

### Symbol Formats

All supported: `BTCUSD`, `BTC-USD`, `BTC/USD`, `ETHUSD`, etc. Coinbase format (`BTC-USD`) is used internally.

## 4. TradingView Port Restriction

TradingView only allows **ports 80 and 443**. Railway uses 443 by default, so no changes needed.

## 5. Test

Send a test POST:

```bash
curl -X POST "https://YOUR-APP.up.railway.app/api/webhooks/tradingview?secret=YOUR_SECRET" \
  -H "Content-Type: application/json" \
  -d '{"symbol":"BTC-USD","action":"buy","quote_size":50}'
```

Expected response: `{"success": true, "message": "BUY BTC-USD executed", ...}`

## 6. Rate Limit

Webhook is limited to **60 requests per minute per IP** to prevent abuse.
