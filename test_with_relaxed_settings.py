#!/usr/bin/env python3
"""
Test trading with relaxed settings to see low-to-mid quality trades.
This will actually generate trade signals so you can see trades in action.
"""

import sys
from datetime import datetime, timedelta
from typing import Dict, List
import pandas as pd
import numpy as np

sys.path.insert(0, '.')
from strategy.ema_rsi_strategy import EMARSIStrategy
from config import get_config

TRADING_PAIRS = ['BTC-USD', 'ETH-USD', 'SOL-USD', 'ADA-USD', 'AVAX-USD', 'XRP-USD', 'DOGE-USD', 'MINA-USD', 'TRUMP-USD']

BASE_PRICES = {
    'BTC-USD': 95000.0, 'ETH-USD': 3500.0, 'SOL-USD': 150.0,
    'ADA-USD': 0.50, 'AVAX-USD': 40.0, 'XRP-USD': 0.60,
    'DOGE-USD': 0.15, 'MINA-USD': 1.20, 'TRUMP-USD': 12.0
}


def create_trending_price_series(base_price: float, trend_direction: str, num_points: int = 200):
    """Create price series with a clear trend using pandas/numpy."""
    if trend_direction == 'up':
        # Bullish: start low, end high, RSI should be moderate (50-75)
        trend = np.linspace(-0.03, 0.03, num_points)  # Gradually go from -3% to +3%
        noise = np.random.normal(0, 0.005, num_points)  # Small random noise
        returns = trend + noise
    else:  # down
        # Bearish: start high, end low, RSI should be moderate (25-50)
        trend = np.linspace(0.03, -0.03, num_points)  # Gradually go from +3% to -3%
        noise = np.random.normal(0, 0.005, num_points)
        returns = trend + noise
    
    # Convert to prices
    prices = [base_price]
    for ret in returns:
        prices.append(prices[-1] * (1 + ret))
    
    return prices[1:]  # Return without initial base


def create_candles_with_trend(pair: str, signal_type: str = 'LONG'):
    """Create realistic candles that will trigger a signal with relaxed settings."""
    base_price = BASE_PRICES[pair]
    base_volume = 3000000
    
    # Generate price series with trend
    prices = create_trending_price_series(base_price, 'up' if signal_type == 'LONG' else 'down', 200)
    
    candles = []
    for i, price in enumerate(prices):
        # Volume: higher for recent candles to trigger signal
        if i >= 150:
            volume = base_volume * np.random.uniform(1.3, 2.0)  # 1.3-2.0x for signal
        else:
            volume = base_volume * np.random.uniform(0.7, 1.3)  # Normal volume
        
        # Create OHLC
        if signal_type == 'LONG':
            high = price * np.random.uniform(1.001, 1.004)
            low = price * np.random.uniform(0.997, 0.9995)
            open_price = price * np.random.uniform(0.999, 1.001)
            close = price  # Close near high for bullish
        else:  # SHORT
            high = price * np.random.uniform(1.001, 1.002)
            low = price * np.random.uniform(0.996, 0.9985)
            open_price = price * np.random.uniform(0.9995, 1.001)
            close = price  # Close near low for bearish
        
        candles.append({
            'timestamp': datetime.now() - timedelta(minutes=200-i),
            'open': open_price,
            'high': high,
            'low': low,
            'close': close,
            'volume': volume
        })
    
    return candles


def test_relaxed_trades():
    """Test with relaxed settings to see low-to-mid quality trades."""
    config = get_config()
    
    # Save original settings
    original = {
        'min_confidence': config.MIN_CONFIDENCE_SCORE,
        'volume_multiplier': config.VOLUME_MULTIPLIER,
        'rsi_long_min': config.RSI_LONG_MIN,
        'rsi_long_max': config.RSI_LONG_MAX,
        'rsi_short_min': config.RSI_SHORT_MIN,
        'rsi_short_max': config.RSI_SHORT_MAX
    }
    
    # RELAXED SETTINGS for testing (low-to-mid quality)
    print("=" * 90)
    print(" TESTING WITH RELAXED SETTINGS - Low to Mid Quality Trades ".center(90))
    print("=" * 90)
    print(f"\n⚙️  Original Settings (High Quality):")
    print(f"   • Min Confidence: {original['min_confidence']}%")
    print(f"   • Volume Multiplier: {original['volume_multiplier']}x")
    print(f"   • RSI Long: {original['rsi_long_min']}-{original['rsi_long_max']}")
    print(f"   • RSI Short: {original['rsi_short_min']}-{original['rsi_short_max']}")
    
    # Use relaxed settings
    config.MIN_CONFIDENCE_SCORE = 40.0  # Much lower (was 70%)
    config.VOLUME_MULTIPLIER = 1.1  # Lower threshold (was 1.5x)
    config.RSI_LONG_MIN = 45  # Wider range (was 55-70)
    config.RSI_LONG_MAX = 80
    config.RSI_SHORT_MIN = 20  # Wider range (was 30-45)
    config.RSI_SHORT_MAX = 55
    
    print(f"\n⚙️  Relaxed Settings (Testing - Lower Quality):")
    print(f"   • Min Confidence: {config.MIN_CONFIDENCE_SCORE}% ⚠️  (LOW)")
    print(f"   • Volume Multiplier: {config.VOLUME_MULTIPLIER}x ⚠️  (LOW)")
    print(f"   • RSI Long: {config.RSI_LONG_MIN}-{config.RSI_LONG_MAX} ⚠️  (WIDE)")
    print(f"   • RSI Short: {config.RSI_SHORT_MIN}-{config.RSI_SHORT_MAX} ⚠️  (WIDE)")
    print(f"\n📊 Testing {len(TRADING_PAIRS)} trading pairs...")
    print("=" * 90)
    
    strategy = EMARSIStrategy(config)
    signals_found = []
    
    # Test each pair
    for pair in TRADING_PAIRS:
        print(f"\n📈 {pair}:")
        
        # Try LONG
        for attempt in range(5):
            candles = create_candles_with_trend(pair, 'LONG')
            signal = strategy.generate_signal(candles)
            if signal:
                indicators = strategy.calculate_indicators(candles)
                signals_found.append((pair, 'LONG', signal, indicators, 'relaxed'))
                
                print(f"  ✅ LONG TRADE GENERATED!")
                print(f"     Entry: ${signal['price']:,.2f} | Confidence: {signal['confidence']:.1f}%")
                print(f"     Take Profit: ${signal['take_profit']:,.2f} ({((signal['take_profit']/signal['price']-1)*100):+.2f}%)")
                print(f"     Stop Loss: ${signal['stop_loss']:,.2f} ({((signal['stop_loss']/signal['price']-1)*100):+.2f}%)")
                print(f"     Conditions: Price=${indicators['price']:,.2f}, EMA=${indicators['ema']:,.2f}, RSI={indicators['rsi']:.1f}, Vol={indicators['volume_ratio']:.2f}x")
                break
        
        # Try SHORT
        for attempt in range(5):
            candles = create_candles_with_trend(pair, 'SHORT')
            signal = strategy.generate_signal(candles)
            if signal:
                indicators = strategy.calculate_indicators(candles)
                signals_found.append((pair, 'SHORT', signal, indicators, 'relaxed'))
                
                print(f"  ✅ SHORT TRADE GENERATED!")
                print(f"     Entry: ${signal['price']:,.2f} | Confidence: {signal['confidence']:.1f}%")
                print(f"     Take Profit: ${signal['take_profit']:,.2f} ({((signal['take_profit']/signal['price']-1)*100):+.2f}%)")
                print(f"     Stop Loss: ${signal['stop_loss']:,.2f} ({((signal['stop_loss']/signal['price']-1)*100):+.2f}%)")
                print(f"     Conditions: Price=${indicators['price']:,.2f}, EMA=${indicators['ema']:,.2f}, RSI={indicators['rsi']:.1f}, Vol={indicators['volume_ratio']:.2f}x")
                break
    
    # Restore original settings
    config.MIN_CONFIDENCE_SCORE = original['min_confidence']
    config.VOLUME_MULTIPLIER = original['volume_multiplier']
    config.RSI_LONG_MIN = original['rsi_long_min']
    config.RSI_LONG_MAX = original['rsi_long_max']
    config.RSI_SHORT_MIN = original['rsi_short_min']
    config.RSI_SHORT_MAX = original['rsi_short_max']
    
    # Summary
    print("\n" + "=" * 90)
    print(" SUMMARY ".center(90))
    print("=" * 90)
    print(f"\n✅ Total Trades Generated: {len(signals_found)}\n")
    
    if signals_found:
        print("📋 ALL TRADES GENERATED:\n")
        for i, (pair, direction, signal, indicators, quality) in enumerate(signals_found, 1):
            profit_pct = abs((signal['take_profit']/signal['price']-1)*100)
            loss_pct = abs((signal['stop_loss']/signal['price']-1)*100)
            
            # Classify quality based on confidence
            if signal['confidence'] < 50:
                quality_label = "LOW QUALITY"
            elif signal['confidence'] < 65:
                quality_label = "MID QUALITY"
            else:
                quality_label = "HIGH QUALITY"
            
            print(f"{i}. {pair} {direction} - {quality_label} (Confidence: {signal['confidence']:.1f}%)")
            print(f"   Entry: ${signal['price']:,.2f}")
            print(f"   Take Profit: ${signal['take_profit']:,.2f} (+{profit_pct:.2f}%)")
            print(f"   Stop Loss: ${signal['stop_loss']:,.2f} (-{loss_pct:.2f}%)")
            print(f"   Risk/Reward: 1:{profit_pct/loss_pct:.2f}")
            print(f"   Market: Price=${indicators['price']:,.2f}, EMA=${indicators['ema']:,.2f}, RSI={indicators['rsi']:.1f}, Vol={indicators['volume_ratio']:.2f}x")
            print()
        
        print("💡 QUALITY COMPARISON:")
        print(f"\n   With ORIGINAL settings ({original['min_confidence']}% confidence, {original['volume_multiplier']}x volume):")
        print("   • Only HIGH quality trades (70%+ confidence) would trigger")
        print("   • Very selective - only best setups")
        print("   • Fewer trades, but higher win probability")
        print(f"\n   With RELAXED settings ({config.MIN_CONFIDENCE_SCORE}% confidence, {config.VOLUME_MULTIPLIER}x volume):")
        print("   • LOW-MID quality trades (40%+ confidence) trigger")
        print("   • Less selective - more setups qualify")
        print("   • More trades, but lower win probability")
        print("\n⚠️  To see more trades in the app, consider adjusting settings:")
        print(f"   • Lower confidence from {original['min_confidence']}% to 50-60%")
        print(f"   • Lower volume from {original['volume_multiplier']}x to 1.2-1.3x")
        print("   • Widen RSI ranges slightly")
        print("\n   Remember: More trades = Lower quality. Quality vs Quantity trade-off!")
    else:
        print("⚠️  No trades generated even with relaxed settings.")
        print("   This shows how strict the strategy is.")
    
    print("=" * 90)


if __name__ == '__main__':
    np.random.seed(123)  # For reproducible results
    test_relaxed_trades()

