# How to Execute Your First Test Trade

## Quick Solution: Use the Existing API Endpoint

The `/api/test/force-trade` endpoint is **already implemented** and ready to use! You don't need to create a script - just call the endpoint.

## Method 1: Use the API Endpoint (Recommended)

### Option A: Using curl (Terminal)

```bash
# Replace YOUR_TOKEN with your authentication token
curl -X POST "https://web-production-f8308.up.railway.app/api/test/force-trade" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -d '{
    "symbol": "BTC-USD",
    "side": "BUY",
    "amount_usdt": 100.0,
    "paper_trading": true
  }'
```

### Option B: Using Browser Console

1. Open your TradePilot dashboard
2. Open browser console (F12)
3. Run this JavaScript:

```javascript
// Get your auth token from localStorage
const token = localStorage.getItem('auth_token');

// Execute a test trade
fetch('/api/test/force-trade', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
    'Authorization': `Bearer ${token}`
  },
  body: JSON.stringify({
    symbol: 'BTC-USD',
    side: 'BUY',
    amount_usdt: 100.0,
    paper_trading: true
  })
})
.then(r => r.json())
.then(data => {
  console.log('Trade executed:', data);
  alert('Trade executed! Check Trade History page.');
})
.catch(err => {
  console.error('Error:', err);
  alert('Error executing trade. Check console for details.');
});
```

### Option C: Using a Simple HTML Page (Easiest)

1. Create a file `test_trade.html` on your local machine:

```html
<!DOCTYPE html>
<html>
<head>
    <title>Execute Test Trade</title>
</head>
<body>
    <h1>Execute Test Trade</h1>
    <button onclick="executeTrade()">Execute Test Trade</button>
    <pre id="result"></pre>
    
    <script>
    async function executeTrade() {
        // Replace with your Railway URL
        const url = 'https://web-production-f8308.up.railway.app/api/test/force-trade';
        
        // Get token - you'll need to copy this from your browser localStorage
        const token = prompt('Enter your auth token (get from browser localStorage):');
        
        if (!token) {
            alert('Token required');
            return;
        }
        
        try {
            const response = await fetch(url, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${token}`
                },
                body: JSON.stringify({
                    symbol: 'BTC-USD',
                    side: 'BUY',
                    amount_usdt: 100.0,
                    paper_trading: true
                })
            });
            
            const data = await response.json();
            document.getElementById('result').textContent = JSON.stringify(data, null, 2);
            
            if (data.success) {
                alert('✅ Trade executed successfully! Check your dashboard.');
            } else {
                alert('❌ Trade failed: ' + (data.error || 'Unknown error'));
            }
        } catch (error) {
            document.getElementById('result').textContent = 'Error: ' + error.message;
            alert('❌ Error: ' + error.message);
        }
    }
    </script>
</body>
</html>
```

2. Open the file in your browser
3. Enter your auth token (get it from browser localStorage when logged into TradePilot)
4. Click the button

## Method 2: Create a Standalone Python Script (Optional)

If you prefer a standalone script, here's one that uses the existing bot infrastructure:

```python
#!/usr/bin/env python3
"""
Force execute a paper trade to populate the system with data.
Run this locally (not on Railway) with database access.
"""
import asyncio
import logging
import sys
from datetime import datetime
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from config import get_config
from exchange.coinbase_client import CoinbaseClient
from database.db_manager import DatabaseManager

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def force_paper_trade():
    """Execute a paper trade immediately."""
    
    logger.info("=" * 50)
    logger.info("FORCING PAPER TRADE")
    logger.info("=" * 50)
    
    config = get_config()
    
    # Initialize exchange
    exchange = CoinbaseClient(config)
    await exchange.initialize()
    
    # Initialize database
    db = DatabaseManager(config)
    await db.initialize()
    
    try:
        # Get current BTC price
        symbol = "BTC-USD"
        market_data = await exchange.get_market_data([symbol])
        
        if symbol not in market_data:
            logger.error(f"Could not fetch market data for {symbol}")
            return
        
        current_price = market_data[symbol]['price']
        logger.info(f"Current {symbol} price: ${current_price:.2f}")
        
        # Execute paper buy
        trade_amount_usd = 100.0
        quantity = trade_amount_usd / current_price
        
        # Create trade data
        trade_data = {
            'pair': symbol,
            'side': 'BUY',
            'entry_price': current_price,
            'size': quantity,
            'entry_time': datetime.utcnow(),
            'order_id': f'manual-test-{int(datetime.utcnow().timestamp())}',
            'confidence_score': 85.0,
            'stop_loss': current_price * 0.9975,  # 0.25% stop loss
            'take_profit': current_price * 1.005  # 0.5% take profit
        }
        
        # Save trade to database
        trade_id = await db.save_trade(trade_data)
        
        if trade_id:
            logger.info(f"✅ Trade created: {trade_id}")
            logger.info(f"   Symbol: {symbol}")
            logger.info(f"   Side: BUY")
            logger.info(f"   Quantity: {quantity:.6f}")
            logger.info(f"   Price: ${current_price:.2f}")
            logger.info(f"   Total: ${trade_amount_usd:.2f}")
            
            logger.info("=" * 50)
            logger.info("PIPELINE VALIDATION COMPLETE")
            logger.info("Check dashboard - you should now see:")
            logger.info("  - 1 trade in Trade History")
            logger.info("  - Performance metrics populated")
            logger.info("=" * 50)
        else:
            logger.error("❌ Failed to save trade to database")
            
    except Exception as e:
        logger.error(f"Error executing trade: {e}", exc_info=True)
    finally:
        # Clean up
        if exchange.session:
            await exchange.session.close()

if __name__ == "__main__":
    asyncio.run(force_paper_trade())
```

**Note**: This script requires:
- Local database access (won't work if Railway DB is private)
- Python environment with all dependencies
- Database connection configured

## Recommended: Use the API Endpoint

**The API endpoint is the easiest method** because:
- ✅ Works immediately (already deployed)
- ✅ No local setup required
- ✅ Uses existing authentication
- ✅ Saves to database automatically
- ✅ Creates real trade records

## What Happens After Execution

After successfully executing a test trade, you should see:

1. **Trade History Page**: 1 new trade entry
2. **Performance Page**: Metrics populated (1 trade, win rate, etc.)
3. **Portfolio Page**: Balance updated
4. **Overview Dashboard**: Trade count and metrics visible

## Verify It Worked

1. Go to Trade History page in your dashboard
2. You should see a new trade with:
   - Symbol: BTC-USD
   - Side: BUY
   - Entry price: Current BTC price
   - Status: OPEN (or CLOSED if simulated exit)

## Troubleshooting

### Error: "Trading bot is not running"
- **Fix**: The endpoint requires the bot to be running
- Make sure Railway is running the full bot (`python main.py`)
- Check Railway logs to verify bot status

### Error: "Database not initialized"
- **Fix**: Database connection issue
- Check Railway database is accessible
- Verify DATABASE_URL is set correctly

### Error: Authentication failed
- **Fix**: Need valid auth token
- Get token from browser localStorage when logged in
- Or log in to TradePilot and use browser console method

## Next Steps

After executing your first test trade:

1. **Check all dashboard pages** to see populated data
2. **Execute multiple trades** to build up data:
   - Try different symbols (ETH-USD, SOL-USD)
   - Try different sides (BUY, SELL)
   - Try different amounts
3. **Close a trade** to test P&L calculations (if needed, you can manually update via database or create a close endpoint)

