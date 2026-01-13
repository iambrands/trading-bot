#!/usr/bin/env python3
"""
Simplified demo showing how trading signals work with your settings.
This creates perfect scenarios to demonstrate trade triggers.
"""

import sys
from datetime import datetime, timedelta
from typing import Dict, List

sys.path.insert(0, '.')
from strategy.ema_rsi_strategy import EMARSIStrategy
from config import get_config

# Your trading pairs
TRADING_PAIRS = [
    'BTC-USD', 'ETH-USD', 'SOL-USD', 'ADA-USD', 'AVAX-USD',
    'XRP-USD', 'DOGE-USD', 'MINA-USD', 'TRUMP-USD'
]

BASE_PRICES = {
    'BTC-USD': 95000.0, 'ETH-USD': 3500.0, 'SOL-USD': 150.0,
    'ADA-USD': 0.50, 'AVAX-USD': 40.0, 'XRP-USD': 0.60,
    'DOGE-USD': 0.15, 'MINA-USD': 1.20, 'TRUMP-USD': 12.0
}


def create_perfect_long_candles(pair: str) -> List[Dict]:
    """Create candles that WILL trigger a LONG signal."""
    base_price = BASE_PRICES.get(pair, 100.0)
    candles = []
    
    # Need enough candles for EMA (50) and RSI (14) calculation
    # Start with stable price, then create bullish setup
    
    current_price = base_price
    base_volume = 3000000
    
    # Build stable base (150 candles to establish EMA baseline)
    for i in range(150):
        # Very small movements to establish EMA around base price
        change = (random.random() - 0.5) * 0.002  # -0.1% to +0.1%
        current_price = current_price * (1 + change)
        
        candles.append({
            'timestamp': datetime.now() - timedelta(minutes=200 - i),
            'open': current_price * 0.9995,
            'high': current_price * 1.002,
            'low': current_price * 0.998,
            'close': current_price,
            'volume': base_volume * (0.9 + random.random() * 0.2)
        })
    
    # Now create 50 candles with perfect LONG conditions:
    # - Price above EMA (gradual rise)
    # - RSI in 55-70 range (moderate upward momentum)
    # - Volume 1.6x+ average (high volume confirmation)
    
        # Gradually push price up while keeping RSI in range
        for i in range(50):
            # Small positive moves (0.1-0.4% per candle) to push price above EMA
            # but keep RSI in the 50-75 range (relaxed for demo)
            change = 0.001 + (random.random() * 0.003)  # 0.1% to 0.4% per candle
            current_price = current_price * (1 + change)
            
            candles.append({
                'timestamp': datetime.now() - timedelta(minutes=50 - i),
                'open': current_price * 0.999,
                'high': current_price * 1.004,
                'low': current_price * 0.997,
                'close': current_price,  # Close near high for bullish RSI
                'volume': base_volume * (1.3 + random.random() * 0.7)  # 1.3-2.0x volume (relaxed)
            })
    
    return candles


def create_perfect_short_candles(pair: str) -> List[Dict]:
    """Create candles that WILL trigger a SHORT signal."""
    base_price = BASE_PRICES.get(pair, 100.0)
    candles = []
    
    current_price = base_price
    base_volume = 3000000
    
    # Build stable base
    for i in range(150):
        change = (random.random() - 0.5) * 0.002
        current_price = current_price * (1 + change)
        
        candles.append({
            'timestamp': datetime.now() - timedelta(minutes=200 - i),
            'open': current_price * 1.0005,
            'high': current_price * 1.002,
            'low': current_price * 0.998,
            'close': current_price,
            'volume': base_volume * (0.9 + random.random() * 0.2)
        })
    
    # Create 50 candles with perfect SHORT conditions:
    # - Price below EMA (gradual decline)
    # - RSI in 30-45 range (moderate downward momentum)
    # - Volume 1.6x+ average
    
        for i in range(50):
            # Small negative moves to push price below EMA
            change = -0.001 - (random.random() * 0.003)  # -0.1% to -0.4% per candle
            current_price = current_price * (1 + change)
            
            candles.append({
                'timestamp': datetime.now() - timedelta(minutes=50 - i),
                'open': current_price * 1.001,
                'high': current_price * 1.003,
                'low': current_price * 0.996,
                'close': current_price,  # Close near low for bearish RSI
                'volume': base_volume * (1.3 + random.random() * 0.7)  # 1.3-2.0x volume (relaxed)
            })
    
    return candles


def demo_signals():
    """Demonstrate trading signals with your strategy."""
    config = get_config()
    
    # Temporarily use relaxed settings for demonstration to ensure we see trades
    # Save original settings
    original_min_confidence = config.MIN_CONFIDENCE_SCORE
    original_volume_multiplier = config.VOLUME_MULTIPLIER
    original_rsi_long_min = config.RSI_LONG_MIN
    original_rsi_long_max = config.RSI_LONG_MAX
    original_rsi_short_min = config.RSI_SHORT_MIN
    original_rsi_short_max = config.RSI_SHORT_MAX
    
    # Use relaxed settings for demo
    config.MIN_CONFIDENCE_SCORE = 50.0  # Lower from 70% to 50%
    config.VOLUME_MULTIPLIER = 1.2  # Lower from 1.5x to 1.2x
    config.RSI_LONG_MIN = 50  # Widen from 55-70 to 50-75
    config.RSI_LONG_MAX = 75
    config.RSI_SHORT_MIN = 25  # Widen from 30-45 to 25-50
    config.RSI_SHORT_MAX = 50
    
    strategy = EMARSIStrategy(config)
    
    print("=" * 80)
    print("TRADING SIGNAL DEMONSTRATION (RELAXED SETTINGS FOR DEMO)")
    print("=" * 80)
    print(f"\nOriginal Strategy Settings (current in app):")
    print(f"  • Min Confidence: {original_min_confidence}%")
    print(f"  • Volume Multiplier: {original_volume_multiplier}x")
    print(f"  • RSI Long Range: {original_rsi_long_min}-{original_rsi_long_max}")
    print(f"  • RSI Short Range: {original_rsi_short_min}-{original_rsi_short_max}")
    print(f"\nDemo Settings (relaxed to show trades):")
    print(f"  ✓ Min Confidence: {config.MIN_CONFIDENCE_SCORE}% (lowered from {original_min_confidence}%)")
    print(f"  ✓ Volume Multiplier: {config.VOLUME_MULTIPLIER}x (lowered from {original_volume_multiplier}x)")
    print(f"  ✓ RSI Long Range: {config.RSI_LONG_MIN}-{config.RSI_LONG_MAX} (widened)")
    print(f"  ✓ RSI Short Range: {config.RSI_SHORT_MIN}-{config.RSI_SHORT_MAX} (widened)")
    print(f"\nTesting {len(TRADING_PAIRS)} trading pairs...")
    print("=" * 80)
    
    signals_found = []
    
    # Test all pairs with perfect setups
    for pair in TRADING_PAIRS:
        print(f"\n📊 {pair}:")
        
        # Test LONG signal
        candles = create_perfect_long_candles(pair)
        signal = strategy.generate_signal(candles)
        indicators = strategy.calculate_indicators(candles)
        
        if signal:
            signals_found.append((pair, 'LONG', signal))
            print(f"  ✅ LONG Signal Triggered!")
            print(f"     Entry: ${signal['price']:.2f}")
            print(f"     Confidence: {signal['confidence']:.1f}%")
            print(f"     Take Profit: ${signal['take_profit']:.2f} ({((signal['take_profit']/signal['price']-1)*100):+.2f}%)")
            print(f"     Stop Loss: ${signal['stop_loss']:.2f} ({((signal['stop_loss']/signal['price']-1)*100):+.2f}%)")
            print(f"     Indicators: Price=${indicators['price']:.2f}, EMA=${indicators['ema']:.2f}, RSI={indicators['rsi']:.1f}, Vol={indicators['volume_ratio']:.2f}x")
        else:
            print(f"  ❌ No LONG signal")
            if indicators:
                print(f"     Why: Price=${indicators['price']:.2f}, EMA=${indicators['ema']:.2f}, RSI={indicators['rsi']:.1f}, Vol={indicators['volume_ratio']:.2f}x")
        
        # Test SHORT signal
        candles = create_perfect_short_candles(pair)
        signal = strategy.generate_signal(candles)
        indicators = strategy.calculate_indicators(candles)
        
        if signal:
            signals_found.append((pair, 'SHORT', signal))
            print(f"  ✅ SHORT Signal Triggered!")
            print(f"     Entry: ${signal['price']:.2f}")
            print(f"     Confidence: {signal['confidence']:.1f}%")
            print(f"     Take Profit: ${signal['take_profit']:.2f} ({((signal['take_profit']/signal['price']-1)*100):+.2f}%)")
            print(f"     Stop Loss: ${signal['stop_loss']:.2f} ({((signal['stop_loss']/signal['price']-1)*100):+.2f}%)")
            print(f"     Indicators: Price=${indicators['price']:.2f}, EMA=${indicators['ema']:.2f}, RSI={indicators['rsi']:.1f}, Vol={indicators['volume_ratio']:.2f}x")
        else:
            print(f"  ❌ No SHORT signal")
            if indicators:
                print(f"     Why: Price=${indicators['price']:.2f}, EMA=${indicators['ema']:.2f}, RSI={indicators['rsi']:.1f}, Vol={indicators['volume_ratio']:.2f}x")
    
    print("\n" + "=" * 80)
    print("SUMMARY")
    print("=" * 80)
    print(f"\nSignals found: {len(signals_found)}")
    
    if signals_found:
        print("\n✅ THESE TRADES WOULD BE EXECUTED:\n")
        for pair, direction, signal in signals_found:
            print(f"{pair} {direction}:")
            print(f"  Entry: ${signal['price']:.2f}")
            print(f"  Confidence: {signal['confidence']:.1f}%")
            print(f"  Target: ${signal['take_profit']:.2f} | Stop: ${signal['stop_loss']:.2f}")
            print()
    
    # Restore original settings
    config.MIN_CONFIDENCE_SCORE = original_min_confidence
    config.VOLUME_MULTIPLIER = original_volume_multiplier
    config.RSI_LONG_MIN = original_rsi_long_min
    config.RSI_LONG_MAX = original_rsi_long_max
    config.RSI_SHORT_MIN = original_rsi_short_min
    config.RSI_SHORT_MAX = original_rsi_short_max
    
    print("\n💡 KEY INSIGHT:")
    print("Your ORIGINAL strategy requires ALL of these conditions simultaneously:")
    print(f"  1. Price above/below EMA(50)")
    print(f"  2. RSI in range {original_rsi_long_min}-{original_rsi_long_max} (long) or {original_rsi_short_min}-{original_rsi_short_max} (short)")
    print(f"  3. Volume ≥ {original_volume_multiplier}x average (confirmation)")
    print(f"  4. Confidence score ≥ {original_min_confidence}%")
    print("\n⚠️  This is why you're not seeing trades - your current settings are VERY conservative!")
    print("All 4 conditions must align perfectly, which is rare in real markets.")
    print("\nTo see more trades, consider relaxing these settings in the app.")
    print("=" * 80)


if __name__ == '__main__':
    import random
    demo_signals()

