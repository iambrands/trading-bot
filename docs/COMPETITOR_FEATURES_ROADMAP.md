# Competitor Features Roadmap

**Focus areas** (by priority):

1. **Strategy Marketplace** — Medium effort, High impact  
2. **TradingView Webhooks** — Low–medium effort, High impact  
3. **Multi-Exchange** — High effort, High impact  

---

## 1. TradingView Webhooks (Start Here — Fastest Win)

### What It Does

- TradingView sends HTTP POST to your URL when an alert fires
- Your bot executes the trade (buy/sell) based on the alert payload
- Supports Pine Script strategies and custom indicators

### Technical Requirements

- **Endpoint**: `POST /api/webhooks/tradingview` (public or token-protected)
- **Port**: 80 or 443 (Railway uses 443)
- **Timeout**: TradingView times out after 3 seconds — respond quickly
- **Auth**: Optional webhook secret or JWT; TradingView allows custom headers

### Payload Format (TradingView sends JSON)

```json
{
  "symbol": "BTCUSD",
  "action": "buy",
  "close": 67500.50,
  "timestamp": "2025-02-22T12:00:00Z"
}
```

Customizable in TradingView alert message: `{"symbol":"{{ticker}}","action":"{{strategy.order.action}}","close":{{close}}}`

### Implementation Tasks

| Task | Est. | Description |
|------|------|-------------|
| 1 | 1h | Add `POST /api/webhooks/tradingview` route |
| 2 | 1h | Parse payload, validate symbol/action, map to exchange format |
| 3 | 1h | Call `exchange.place_order()` with user context (need user_id from token) |
| 4 | 1h | Optional: webhook secret validation (query param or header) |
| 5 | 0.5h | Settings UI: enable/disable TradingView mode, webhook URL display |

### Security

- Require `Authorization: Bearer <token>` or `?secret=<webhook_secret>` to prevent abuse
- Validate symbol is in allowed list
- Rate limit (e.g. 60/min per user)

---

## 2. Strategy Marketplace

### What It Does

- Users browse and enable pre-built strategies (beyond EMA+RSI)
- Each strategy has configurable params (RSI period, EMA period, etc.)
- Admin/curated list or community-contributed (later)

### Current State

- Single strategy: `EMARSIStrategy` in `strategy/ema_rsi_strategy.py`
- Strategy is wired in `main.py` and `config.py`
- Backtest engine uses same strategy interface

### Architecture Change

Introduce a **Strategy Interface** and **Strategy Registry**:

```python
# strategy/base.py
class BaseStrategy(ABC):
    id: str
    name: str
    params_schema: Dict  # { "ema_period": {"type": "int", "default": 50, "min": 5, "max": 200 } }

    @abstractmethod
    def calculate_indicators(self, candles) -> Optional[Dict]: ...

    @abstractmethod
    def get_signal(self, indicators) -> Optional[Tuple[str, float]]: ...
```

### Implementation Tasks

| Task | Est. | Description |
|------|------|-------------|
| 1 | 2h | Create `strategy/base.py` with `BaseStrategy` ABC |
| 2 | 1h | Refactor `EMARSIStrategy` to implement `BaseStrategy` |
| 3 | 2h | Add 2–3 built-in strategies (e.g. RSI-only, Bollinger Bands) |
| 4 | 2h | Strategy registry + API: `GET /api/strategies`, `POST /api/strategies/{id}/activate` |
| 5 | 2h | Settings UI: strategy selector, param forms |
| 6 | 1h | Backtest: run selected strategy |
| 7 | 1h | DB: store `active_strategy_id` and params per user |

### Suggested Starter Strategies

- **EMA+RSI+Volume** (current)
- **RSI Only** — Simple RSI oversold/overbought
- **Bollinger Bands** — Price at lower/upper band

---

## 3. Multi-Exchange Support

### Current State

- `main.py` uses `CoinbaseClient` only
- `exchange/exchange_factory.py` exists with:
  - `BinanceClient` (CCXT)
  - `CoinbaseClient` (wraps existing Coinbase client)
  - Different interfaces: Coinbase uses `get_account_balance`, `get_market_data`, etc.; CCXT uses `fetch_balance`, `fetch_ticker`

### Challenge

- CoinbaseClient API: `get_account_balance()`, `get_market_data(pairs)`, `get_candles()`, `place_order(pair, side, size, quote_size=)`
- CCXT API: `fetch_balance()`, `fetch_ticker(symbol)`, `create_market_order(symbol, side, amount)`
- Need a **unified adapter** so `TradingBot` and API use one interface

### Implementation Tasks

| Task | Est. | Description |
|------|------|-------------|
| 1 | 3h | Define `ExchangeAdapter` interface matching CoinbaseClient methods |
| 2 | 4h | Implement `CoinbaseAdapter` (thin wrapper over existing client) |
| 3 | 4h | Implement `BinanceCCXTAdapter` (CCXT Binance → same interface) |
| 4 | 2h | Config: `EXCHANGE=coinbase|binance`, exchange-specific env vars |
| 5 | 2h | Update `main.py`, grid_manager, dca_manager, orders to use adapter |
| 6 | 2h | Settings UI: exchange selector (switch requires restart) |
| 7 | 2h | Symbol mapping (BTC-USD vs BTC/USDT) per exchange |

### Config Additions

```env
EXCHANGE=coinbase  # or binance
# Coinbase (existing)
COINBASE_API_KEY=...
COINBASE_API_SECRET=...
# Binance (when EXCHANGE=binance)
BINANCE_API_KEY=...
BINANCE_API_SECRET=...
```

---

## Suggested Order of Implementation

1. **TradingView Webhooks** — 1–2 days; immediate value, no core refactor  
2. **Strategy Marketplace** — 3–5 days; clean architecture, enables future strategies  
3. **Multi-Exchange** — 5–7 days; largest change, needs adapter layer and testing  

---

## Files to Create/Modify

### TradingView

- `api/rest_api.py` — add webhook route  
- `static/dashboard.js` — settings UI for webhook URL  
- `docs/TRADINGVIEW_SETUP.md` — user guide  

### Strategy Marketplace

- `strategy/base.py` — new  
- `strategy/ema_rsi_strategy.py` — refactor  
- `strategy/rsi_only.py` — new  
- `strategy/bollinger.py` — new  
- `api/rest_api.py` — strategies endpoints  
- `database/` — migrations for strategy selection  

### Multi-Exchange

- `exchange/adapter.py` — unified interface  
- `exchange/coinbase_adapter.py` — wraps CoinbaseClient  
- `exchange/binance_adapter.py` — CCXT wrapper  
- `config.py` — EXCHANGE, BINANCE_*  
- `main.py` — use adapter from factory  
