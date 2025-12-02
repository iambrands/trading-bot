# Quick Start Guide

Get Crypto Scalping Trading Bot up and running in 5 minutes!

## Step 1: Install Dependencies

```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

## Step 2: Setup Environment

```bash
# Create .env file
./setup_env.sh

# Or manually create .env file
cp .env.example .env  # Edit with your settings
```

## Step 3: Setup Database

```bash
# Create PostgreSQL database
createdb tradingbot

# Or using psql:
psql -U postgres -c "CREATE DATABASE tradingbot;"
```

## Step 4: Run the Bot

```bash
python main.py
```

The bot will:
- Initialize all components
- Connect to database (creates tables automatically)
- Start paper trading by default
- Launch API server on port 8000
- Begin trading loop

## Step 5: Check Status

```bash
# Get bot status
curl http://localhost:8000/api/status

# Get positions
curl http://localhost:8000/api/positions

# Get performance
curl http://localhost:8000/api/performance
```

## Paper Trading Mode

By default, the bot runs in **paper trading mode** which:
- Simulates order execution
- Tracks virtual balance
- Uses realistic slippage and fees
- Safe for testing without real funds

## Troubleshooting

**Database connection error:**
- Ensure PostgreSQL is running: `sudo systemctl status postgresql`
- Verify database exists: `psql -l | grep tradingbot`
- Check credentials in `.env`

**No trades executing:**
- Check logs: `tail -f tradingbot.log`
- Verify market data is loading
- Review strategy signals in logs

**API not responding:**
- Check if bot is running: `ps aux | grep python`
- Verify port 8000 is available: `netstat -tulpn | grep 8000`
- Check firewall settings

## Next Steps

1. Monitor the bot for a few hours in paper trading
2. Review performance metrics
3. Adjust strategy parameters in `config.py` if needed
4. Read full documentation in `README.md`
5. When ready for production, see `DEPLOYMENT.md`

## Important Reminders

⚠️ Always test thoroughly in paper trading mode before live trading
⚠️ Never trade with more than you can afford to lose
⚠️ Monitor the bot closely during initial live trading
⚠️ Set appropriate daily loss limits
