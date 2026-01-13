#!/usr/bin/env python3
"""
Test Coinbase API Connection

Tests if the bot can connect to Coinbase API and fetch data.

Usage:
    python diagnostics/test_api_connection.py
"""

import asyncio
import os
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from config import get_config
from exchange.coinbase_client import CoinbaseClient

async def test_connection():
    """Test if API connection works"""
    
    print("=" * 60)
    print("Coinbase API Connection Test")
    print("=" * 60 + "\n")
    
    config = get_config()
    
    # 1. Check credentials
    print("1. Checking API credentials...")
    if not config.COINBASE_API_KEY or not config.COINBASE_API_SECRET:
        print("   ⚠️  WARNING: API keys not set in environment")
        print("   This is OK if using paper trading mode")
        print("   Set COINBASE_API_KEY and COINBASE_API_SECRET for live trading")
    else:
        key_preview = config.COINBASE_API_KEY[:10] + "..." if len(config.COINBASE_API_KEY) > 10 else config.COINBASE_API_KEY
        print(f"   ✓ API Key found: {key_preview}")
        print(f"   ✓ API Secret found: {'*' * 20}")
    
    print(f"\n   Paper Trading: {'ENABLED ✅' if config.PAPER_TRADING else 'DISABLED ⚠️'}")
    print(f"   Use Real Market Data: {'YES' if config.USE_REAL_MARKET_DATA else 'NO (synthetic)'}")
    
    # 2. Initialize client
    print("\n2. Initializing Coinbase client...")
    try:
        client = CoinbaseClient(config)
        print("   ✓ Client initialized successfully")
    except Exception as e:
        print(f"   ❌ Failed to initialize client: {e}")
        return False
    
    # 3. Test account balance
    print("\n3. Testing account balance fetch...")
    try:
        balance = await client.get_account_balance()
        print(f"   ✓ Balance: ${balance:,.2f}")
    except Exception as e:
        print(f"   ⚠️  Could not fetch balance: {e}")
        if config.PAPER_TRADING:
            print("   (This is expected in paper trading mode)")
        else:
            print("   ❌ This indicates an API connection issue!")
    
    # 4. Test market data
    print("\n4. Testing market data fetch...")
    try:
        test_pair = config.TRADING_PAIRS[0] if config.TRADING_PAIRS else 'BTC-USD'
        market_data = await client.get_market_data([test_pair])
        
        if test_pair in market_data:
            data = market_data[test_pair]
            price = data.get('price', 0)
            volume = data.get('volume_24h', 0)
            print(f"   ✓ {test_pair} Price: ${price:,.2f}")
            print(f"   ✓ 24h Volume: ${volume:,.2f}")
        else:
            print(f"   ⚠️  Could not fetch data for {test_pair}")
    except Exception as e:
        print(f"   ❌ Failed to fetch market data: {e}")
        return False
    
    # 5. Test candle data
    print("\n5. Testing historical candle data fetch...")
    try:
        from datetime import datetime, timedelta
        test_pair = config.TRADING_PAIRS[0] if config.TRADING_PAIRS else 'BTC-USD'
        
        candles = await client.get_candles(
            test_pair,
            granularity='ONE_MINUTE',
            start=datetime.utcnow() - timedelta(hours=1),
            end=datetime.utcnow()
        )
        
        if candles:
            print(f"   ✓ Fetched {len(candles)} candles")
            if len(candles) > 0:
                last_candle = candles[-1]
                print(f"   ✓ Last candle: ${last_candle.get('close', 0):,.2f}")
        else:
            print(f"   ⚠️  No candles returned (might be using synthetic data)")
    except Exception as e:
        print(f"   ⚠️  Could not fetch candles: {e}")
        if config.PAPER_TRADING:
            print("   (This is expected if using synthetic data)")
    
    # 6. Test API authentication (only if not paper trading)
    if not config.PAPER_TRADING and config.COINBASE_API_KEY:
        print("\n6. Testing API authentication...")
        try:
            # Try to fetch accounts endpoint (requires auth)
            result = await client._make_request('GET', '/accounts')
            if 'accounts' in result:
                print(f"   ✓ Authentication successful")
                print(f"   ✓ Found {len(result.get('accounts', []))} accounts")
            else:
                print(f"   ⚠️  Unexpected response format")
        except Exception as e:
            error_str = str(e)
            if '401' in error_str or 'Unauthorized' in error_str:
                print(f"   ❌ Authentication failed: Invalid API keys")
            elif '403' in error_str or 'Forbidden' in error_str:
                print(f"   ❌ Permission denied: Check API key permissions")
            elif '429' in error_str:
                print(f"   ⚠️  Rate limited: Too many requests")
            else:
                print(f"   ⚠️  Error: {e}")
    
    print("\n" + "=" * 60)
    print("✅ API Connection Test Complete")
    print("=" * 60)
    
    return True

def main():
    """Run the test"""
    try:
        result = asyncio.run(test_connection())
        sys.exit(0 if result else 1)
    except KeyboardInterrupt:
        print("\n\nTest cancelled by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == '__main__':
    main()

