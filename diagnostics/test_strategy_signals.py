#!/usr/bin/env python3
"""
Test Strategy Signal Generation

Tests if the strategy generates any signals with recent market data.

Usage:
    python diagnostics/test_strategy_signals.py [--days 7] [--pair BTC-USD]
"""

import asyncio
import sys
import argparse
from pathlib import Path
from datetime import datetime, timedelta

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from config import get_config
from exchange.coinbase_client import CoinbaseClient
from strategy.ema_rsi_strategy import EMARSIStrategy

async def test_strategy_signals(days=7, pair='BTC-USD'):
    """Test if strategy generates signals with recent data"""
    
    print("=" * 60)
    print("Strategy Signal Generation Test")
    print("=" * 60 + "\n")
    
    config = get_config()
    client = CoinbaseClient(config)
    strategy = EMARSIStrategy(config)
    
    print(f"Testing pair: {pair}")
    print(f"Testing period: Last {days} days")
    print(f"\nStrategy Settings:")
    print(f"  EMA Period: {config.EMA_PERIOD}")
    print(f"  RSI Period: {config.RSI_PERIOD}")
    print(f"  Volume Multiplier: {config.VOLUME_MULTIPLIER}x")
    print(f"  RSI Long Range: {config.RSI_LONG_MIN}-{config.RSI_LONG_MAX}")
    print(f"  RSI Short Range: {config.RSI_SHORT_MIN}-{config.RSI_SHORT_MAX}")
    print(f"  Min Confidence: {config.MIN_CONFIDENCE_SCORE}%")
    print()
    
    # Fetch candle data
    print(f"Fetching last {days} days of candle data for {pair}...")
    try:
        start_time = datetime.utcnow() - timedelta(days=days)
        end_time = datetime.utcnow()
        
        candles = await client.get_candles(
            pair,
            granularity='ONE_MINUTE',
            start=start_time,
            end=end_time
        )
        
        if not candles or len(candles) < 100:
            print(f"⚠️  Only {len(candles) if candles else 0} candles fetched")
            print("   Strategy needs at least 50+ candles for EMA(50)")
            print("   Trying to fetch more data...")
            
            # Try to get more data with 5-minute candles
            candles = await client.get_candles(
                pair,
                granularity='FIVE_MINUTE',
                start=start_time - timedelta(days=2),
                end=end_time
            )
            print(f"   Fetched {len(candles) if candles else 0} candles (5-min)")
        
        if not candles:
            print("❌ Could not fetch candle data")
            return False
        
        print(f"✓ Fetched {len(candles)} candles")
        print(f"  Date range: {candles[0].get('timestamp')} to {candles[-1].get('timestamp')}")
        
    except Exception as e:
        print(f"❌ Error fetching candles: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    # Check if we have enough data
    min_candles = max(config.EMA_PERIOD, config.RSI_PERIOD, config.VOLUME_PERIOD) + 1
    if len(candles) < min_candles:
        print(f"\n⚠️  Not enough candles: {len(candles)} < {min_candles} required")
        print("   Strategy needs more historical data")
        return False
    
    # Test signal generation on recent candles
    print(f"\nTesting signal generation on last {len(candles)} candles...")
    
    signals_found = []
    long_signals = 0
    short_signals = 0
    
    # Test signals on chunks of candles (simulating real-time)
    chunk_size = min_candles
    for i in range(chunk_size, len(candles)):
        chunk = candles[i-chunk_size:i+1]
        signal = strategy.generate_signal(chunk)
        
        if signal:
            signals_found.append({
                'signal': signal,
                'candle_index': i,
                'timestamp': chunk[-1].get('timestamp'),
                'price': chunk[-1].get('close')
            })
            
            if signal['type'] == 'LONG':
                long_signals += 1
            else:
                short_signals += 1
    
    # Results
    print("\n" + "=" * 60)
    print("RESULTS")
    print("=" * 60)
    print(f"\nTotal candles analyzed: {len(candles) - chunk_size}")
    print(f"Signals generated: {len(signals_found)}")
    print(f"  - Long signals: {long_signals}")
    print(f"  - Short signals: {short_signals}")
    
    if signals_found:
        print("\n✅ Strategy IS generating signals!")
        print("\nMost recent signals:")
        for sig_data in signals_found[-5:]:  # Last 5 signals
            sig = sig_data['signal']
            print(f"\n  {sig_data['timestamp']}")
            print(f"    Type: {sig['type']}")
            print(f"    Price: ${sig['price']:,.2f}")
            print(f"    Confidence: {sig['confidence']:.1f}%")
            print(f"    Take Profit: ${sig['take_profit']:,.2f} ({((sig['take_profit']/sig['price'] - 1) * 100):.2f}%)")
            print(f"    Stop Loss: ${sig['stop_loss']:,.2f} ({((sig['stop_loss']/sig['price'] - 1) * 100):.2f}%)")
            print(f"    Indicators:")
            ind = sig['indicators']
            print(f"      EMA: ${ind.get('ema', 0):,.2f}")
            print(f"      RSI: {ind.get('rsi', 0):.2f}")
            print(f"      Volume Ratio: {ind.get('volume_ratio', 0):.2f}x")
    else:
        print("\n❌ Strategy is NOT generating signals")
        print("\nPossible reasons:")
        print("  1. Market conditions don't meet entry criteria")
        print("  2. Thresholds too strict:")
        print(f"     - RSI must be {config.RSI_LONG_MIN}-{config.RSI_LONG_MAX} (long) or {config.RSI_SHORT_MIN}-{config.RSI_SHORT_MAX} (short)")
        print(f"     - Volume must be {config.VOLUME_MULTIPLIER}x average")
        print(f"     - Confidence must be >= {config.MIN_CONFIDENCE_SCORE}%")
        print("  3. EMA/price relationship not triggering")
        print("  4. Strategy not suited for current market conditions")
        
        # Show current indicators
        print("\nCurrent market indicators (last candle):")
        last_chunk = candles[-min_candles:]
        signal = strategy.generate_signal(last_chunk)
        
        if last_chunk:
            indicators = strategy.calculate_indicators(last_chunk)
            if indicators:
                price = indicators.get('price', 0)
                ema = indicators.get('ema', 0)
                rsi = indicators.get('rsi', 0)
                volume_ratio = indicators.get('volume_ratio', 0)
                
                print(f"  Price: ${price:,.2f}")
                print(f"  EMA({config.EMA_PERIOD}): ${ema:,.2f}")
                print(f"  Price vs EMA: {((price/ema - 1) * 100):+.2f}%")
                print(f"  RSI({config.RSI_PERIOD}): {rsi:.2f}")
                print(f"  RSI in Long Range ({config.RSI_LONG_MIN}-{config.RSI_LONG_MAX}): {'YES ✅' if config.RSI_LONG_MIN <= rsi <= config.RSI_LONG_MAX else 'NO ❌'}")
                print(f"  RSI in Short Range ({config.RSI_SHORT_MIN}-{config.RSI_SHORT_MAX}): {'YES ✅' if config.RSI_SHORT_MIN <= rsi <= config.RSI_SHORT_MAX else 'NO ❌'}")
                print(f"  Volume Ratio: {volume_ratio:.2f}x")
                print(f"  Volume sufficient ({config.VOLUME_MULTIPLIER}x+): {'YES ✅' if volume_ratio >= config.VOLUME_MULTIPLIER else f'NO ❌ (need {config.VOLUME_MULTIPLIER}x)'}")
                
                # Check conditions
                print("\n  Entry Conditions Check:")
                long_price_ok = price > ema
                long_rsi_ok = config.RSI_LONG_MIN <= rsi <= config.RSI_LONG_MAX
                long_volume_ok = volume_ratio >= config.VOLUME_MULTIPLIER
                
                short_price_ok = price < ema
                short_rsi_ok = config.RSI_SHORT_MIN <= rsi <= config.RSI_SHORT_MAX
                short_volume_ok = volume_ratio >= config.VOLUME_MULTIPLIER
                
                print(f"    LONG:")
                print(f"      Price > EMA: {'YES ✅' if long_price_ok else 'NO ❌'}")
                print(f"      RSI in range: {'YES ✅' if long_rsi_ok else 'NO ❌'}")
                print(f"      Volume OK: {'YES ✅' if long_volume_ok else 'NO ❌'}")
                
                print(f"    SHORT:")
                print(f"      Price < EMA: {'YES ✅' if short_price_ok else 'NO ❌'}")
                print(f"      RSI in range: {'YES ✅' if short_rsi_ok else 'NO ❌'}")
                print(f"      Volume OK: {'YES ✅' if short_volume_ok else 'NO ❌'}")
    
    print("\n" + "=" * 60)
    
    return len(signals_found) > 0

def main():
    """Run the test"""
    parser = argparse.ArgumentParser(description='Test strategy signal generation')
    parser.add_argument('--days', type=int, default=7, help='Number of days to test (default: 7)')
    parser.add_argument('--pair', type=str, default='BTC-USD', help='Trading pair to test (default: BTC-USD)')
    
    args = parser.parse_args()
    
    try:
        result = asyncio.run(test_strategy_signals(args.days, args.pair))
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

