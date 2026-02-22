# TradePilot Infrastructure Checklist

**Phase 8** — Production deployment verification and operational readiness.

---

## Environment Variables

| Variable | Required | Purpose |
|----------|----------|---------|
| `DATABASE_URL` | ✅ Yes | PostgreSQL connection (Railway provides) |
| `JWT_SECRET_KEY` | ✅ Yes | Token signing; set in production or tokens invalid on restart |
| `PORT` | No | Railway sets automatically |
| `ENVIRONMENT` | Recommended | `production` for prod |
| `OPENAI_API_KEY` | Optional | AI analysis on Market Conditions, Backtest |
| `COINBASE_API_KEY` | Optional | Live trading (paper trading works without) |
| `COINBASE_API_SECRET` | Optional | Live trading |
| `COINBASE_API_PASSPHRASE` | Optional | Live trading |

### Railway Setup

1. Dashboard → Service → Variables
2. Ensure `JWT_SECRET_KEY` is set (generate: `openssl rand -hex 32`)
3. Verify `DATABASE_URL` is linked from PostgreSQL add-on

---

## Backup Strategy

- **Railway PostgreSQL**: Railway manages automatic backups for paid plans
- **Manual backup**: `pg_dump $DATABASE_URL > backup.sql`
- **Recommended**: Configure periodic backups if on free tier

---

## Monitoring & Health

| Endpoint | Purpose |
|----------|---------|
| `/api/status` | Bot status, balance, positions |
| `/api/test/trading-health` | Full health check (DB, exchange, bot) |

### Suggested Alerts

- HTTP 5xx on `/api/status` or `/api/test/trading-health`
- Database connection failures (check Railway logs)
- Bot status `stopped` when expected `running`

---

## Rate Limiting

- **Auth endpoints** (`/api/auth/signin`, `/api/auth/signup`): 10 requests per minute per IP
- Protects against brute-force and credential stuffing

---

## Security Headers (Applied)

- `X-Content-Type-Options: nosniff`
- `X-Frame-Options: SAMEORIGIN`
- `X-XSS-Protection: 1; mode=block`
- `Referrer-Policy: strict-origin-when-cross-origin`
- `Content-Security-Policy`: Restricts scripts/styles to self + CDNs (Chart.js, LightweightCharts)

---

## Deployment

- **Platform**: Railway (auto-deploy from GitHub)
- **Start command**: `python app.py` (Procfile)
- **Build**: Nixpacks (Python detected automatically)
