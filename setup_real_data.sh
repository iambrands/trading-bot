#!/bin/bash
# Quick setup script to enable real market data

echo "Crypto Scalping Trading Bot - Real Market Data Setup"
echo "========================================"
echo ""
echo "This will enable real cryptocurrency market data from Coinbase."
echo "You can use real market data even in paper trading mode."
echo ""

# Check if .env exists
if [ ! -f .env ]; then
    echo "Error: .env file not found. Run ./setup_env.sh first."
    exit 1
fi

# Add USE_REAL_MARKET_DATA if not present
if ! grep -q "USE_REAL_MARKET_DATA" .env; then
    echo "" >> .env
    echo "# Use real market data from Coinbase (works without API keys)" >> .env
    echo "USE_REAL_MARKET_DATA=true" >> .env
    echo "✓ Added USE_REAL_MARKET_DATA=true to .env"
else
    # Update existing value
    sed -i '' 's/^USE_REAL_MARKET_DATA=.*/USE_REAL_MARKET_DATA=true/' .env
    echo "✓ Updated USE_REAL_MARKET_DATA to true"
fi

echo ""
echo "Configuration updated!"
echo ""
echo "Option 1: Use real market data WITHOUT API keys (recommended for testing)"
echo "  - Real prices from Coinbase public API"
echo "  - Paper trading still simulated"
echo "  - No authentication required"
echo ""
echo "Option 2: Use real market data WITH API keys (for better data)"
echo "  - Add your Coinbase API credentials to .env"
echo "  - See COINBASE_SETUP.md for details"
echo ""
echo "Current .env settings:"
grep -E "(USE_REAL_MARKET_DATA|PAPER_TRADING|COINBASE_API)" .env | grep -v "^#"
echo ""
echo "Restart the bot to apply changes:"
echo "  pkill -f 'python main.py' && python main.py"
