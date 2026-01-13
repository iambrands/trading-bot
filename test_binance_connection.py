#!/usr/bin/env python3
"""
Test script to validate Binance connection and exchange factory

Usage:
    python test_binance_connection.py

Requirements:
    - Binance API keys (testnet recommended)
    - Set environment variables or edit config below
"""

import os
import sys
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def test_imports():
    """Test that all imports work"""
    print("=" * 60)
    print("TEST 1: Testing Imports")
    print("=" * 60)
    
    try:
        from exchange.exchange_factory import (
            ExchangeFactory,
            BinanceClient,
            ExchangeInterface
        )
        print("✅ All imports successful")
        return True
    except ImportError as e:
        print(f"❌ Import error: {e}")
        print("\n💡 Install missing dependencies:")
        print("   pip install ccxt")
        return False

def test_fee_comparison():
    """Test fee comparison utility"""
    print("\n" + "=" * 60)
    print("TEST 2: Testing Fee Comparison")
    print("=" * 60)
    
    try:
        from exchange.exchange_factory import ExchangeFactory
        
        fees = ExchangeFactory.get_fee_comparison()
        
        print("\nFee Comparison:")
        for exchange, fee_info in fees.items():
            recommended = "✅ RECOMMENDED" if fee_info['recommended'] else "❌ NOT RECOMMENDED"
            print(f"\n{exchange.upper()}:")
            print(f"  Taker Fee: {fee_info['taker']}%")
            print(f"  Maker Fee: {fee_info['maker']}%")
            print(f"  Status: {recommended}")
            if 'note' in fee_info:
                print(f"  Note: {fee_info['note']}")
        
        print("\n✅ Fee comparison successful")
        return True
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_factory_creation():
    """Test factory creation (without API keys - should show error handling)"""
    print("\n" + "=" * 60)
    print("TEST 3: Testing Factory Creation (No API Keys)")
    print("=" * 60)
    
    try:
        from exchange.exchange_factory import ExchangeFactory
        
        # Create a mock config object
        class MockConfig:
            BINANCE_API_KEY = ''
            BINANCE_API_SECRET = ''
            BINANCE_TESTNET = True
        
        config = MockConfig()
        
        try:
            factory = ExchangeFactory.create('binance', config)
            print("⚠️  Factory created without API keys (unexpected)")
            return False
        except ValueError as e:
            print(f"✅ Correctly rejected missing API keys: {e}")
            return True
        except Exception as e:
            print(f"❌ Unexpected error: {e}")
            return False
            
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_binance_connection():
    """Test actual Binance connection (requires API keys)"""
    print("\n" + "=" * 60)
    print("TEST 4: Testing Binance Connection (Requires API Keys)")
    print("=" * 60)
    
    api_key = os.getenv('BINANCE_API_KEY', '')
    api_secret = os.getenv('BINANCE_API_SECRET', '')
    testnet = os.getenv('BINANCE_TESTNET', 'true').lower() == 'true'
    
    if not api_key or not api_secret:
        print("⚠️  Skipping: BINANCE_API_KEY and BINANCE_API_SECRET not set")
        print("   Set these in .env file or environment variables to test")
        print("   Get testnet keys from: https://testnet.binance.vision/")
        return None
    
    try:
        from exchange.exchange_factory import BinanceClient
        
        print(f"Connecting to Binance {'TESTNET' if testnet else 'LIVE'}...")
        client = BinanceClient(api_key, api_secret, testnet=testnet)
        
        # Test fee structure
        fees = client.get_fee_structure()
        print(f"\n✅ Connected to {fees['exchange']}")
        print(f"   Taker Fee: {fees['taker']*100:.2f}%")
        print(f"   Maker Fee: {fees['maker']*100:.2f}%")
        
        # Test ticker (public endpoint, no auth needed)
        print("\nTesting ticker fetch...")
        ticker = client.get_ticker('BTC/USDT')
        if ticker:
            print(f"✅ BTC/USDT Price: ${ticker['last']:,.2f}")
            print(f"   Volume: {ticker['volume']:,.2f}")
        else:
            print("⚠️  Could not fetch ticker (might be testnet issue)")
        
        # Test balance (requires auth)
        print("\nTesting balance fetch...")
        balance = client.get_balance()
        if balance:
            print("✅ Balance fetched successfully")
            # Show available balances (non-zero only)
            for currency, amount in balance.get('free', {}).items():
                if amount > 0:
                    print(f"   {currency}: {amount:,.8f}")
        else:
            print("⚠️  Could not fetch balance (check API keys/permissions)")
        
        print("\n✅ Binance connection test completed")
        return True
        
    except Exception as e:
        print(f"❌ Connection error: {e}")
        import traceback
        traceback.print_exc()
        print("\n💡 Troubleshooting:")
        print("   1. Check API keys are correct")
        print("   2. Ensure API keys have correct permissions")
        print("   3. For testnet: https://testnet.binance.vision/")
        print("   4. Check network connectivity")
        return False

def test_coinbase_wrapper():
    """Test Coinbase wrapper (requires existing CoinbaseClient)"""
    print("\n" + "=" * 60)
    print("TEST 5: Testing Coinbase Wrapper (Optional)")
    print("=" * 60)
    
    try:
        from exchange.exchange_factory import CoinbaseClientWrapper
        from exchange.coinbase_client import CoinbaseClient
        from config import Config
        
        # This requires the existing CoinbaseClient to work
        print("⚠️  Coinbase wrapper test skipped (requires existing Coinbase setup)")
        print("   This will be tested during integration")
        return None
        
    except ImportError:
        print("⚠️  Coinbase client not available (this is OK for Binance-only testing)")
        return None
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def main():
    """Run all tests"""
    print("\n" + "=" * 60)
    print("BINANCE EXCHANGE FACTORY - CONNECTION TEST")
    print("=" * 60)
    print("\nThis script validates the exchange factory implementation")
    print("and tests Binance connection (if API keys provided).\n")
    
    results = []
    
    # Test 1: Imports
    results.append(("Imports", test_imports()))
    
    # Test 2: Fee Comparison
    results.append(("Fee Comparison", test_fee_comparison()))
    
    # Test 3: Factory Creation (Error Handling)
    results.append(("Factory Creation", test_factory_creation()))
    
    # Test 4: Binance Connection (Optional - needs API keys)
    connection_result = test_binance_connection()
    if connection_result is not None:
        results.append(("Binance Connection", connection_result))
    
    # Test 5: Coinbase Wrapper (Optional)
    wrapper_result = test_coinbase_wrapper()
    if wrapper_result is not None:
        results.append(("Coinbase Wrapper", wrapper_result))
    
    # Summary
    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)
    
    passed = sum(1 for _, result in results if result is True)
    total = len([r for _, r in results if r is not None])
    
    for test_name, result in results:
        if result is None:
            status = "⏭️  SKIPPED"
        elif result:
            status = "✅ PASSED"
        else:
            status = "❌ FAILED"
        print(f"{status}: {test_name}")
    
    print(f"\nTotal: {passed}/{total} tests passed")
    
    if passed == total and total > 0:
        print("\n🎉 All tests passed! Exchange factory is ready.")
        print("\nNext steps:")
        print("  1. Review exchange_factory.py code")
        print("  2. Review EXCHANGE_FACTORY_REVIEW.md")
        print("  3. Approve before proceeding to config updates")
        return 0
    else:
        print("\n⚠️  Some tests failed or were skipped")
        print("   Review errors above before proceeding")
        return 1

if __name__ == '__main__':
    sys.exit(main())

