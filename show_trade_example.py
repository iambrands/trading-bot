#!/usr/bin/env python3
"""
Show exactly what a triggered trade looks like with your 9 trading pairs.
Uses relaxed settings to demonstrate actual trades.
"""

import sys
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from typing import Dict, List

sys.path.insert(0, '.')
from strategy.ema_rsi_strategy import EMARSIStrategy
from config import get_config

TRADING_PAIRS = [
    'BTC-USD', 'ETH-USD', 'SOL-USD', 'ADA-USD', 'AVAX-USD',
    'XRP-USD', 'DOGE-USD', 'MINA-USD', 'TRUMP-USD'
]

BASE_PRICES = {
    'BTC-USD': 95000.0, 'ETH-USD': 3500.0, 'SOL-USD': 150.0,
    'ADA-USD': 0.50, 'AVAX-USD': 40.0, 'XRP-USD': 0.60,
    'DOGE-USD': 0.15, 'MINA-USD': 1.20, 'TRUMP-USD': 12.0
}


def create_candles_with_signal(pair: str, signal_type: str = 'LONG') -> List[Dict]:
    """Create realistic candles that will trigger a signal."""
    base_price = BASE_PRICES[pair]
    base_volume = 3000000
    
    # Create 200 candles (need enough for EMA 50)
    candles = []
    prices = []
    volumes = []
    
    # First 100 candles: stable price around base
    current_price = base_price
    for i in range(100):
        # Very small random movements
        change = np.random.uniform(-0.001, 0.001)
        current_price = current_price * (1 + change)
        prices.append(current_price)
        volumes.append(base_volume * np.random.uniform(0.8, 1.2))
        
        candles.append({
            'timestamp': datetime.now() - timedelta(minutes=200-i),
            'open': current_price * np.random.uniform(0.999, 1.001),
            'high': current_price * np.random.uniform(1.001, 1.003),
            'low': current_price * np.random.uniform(0.997, 0.999),
            'close': current_price,
            'volume': volumes[-1]
        })
    
    # Next 100 candles: create trend based on signal type
    if signal_type == 'LONG':
        # Create bullish momentum
        trend_change = np.random.uniform(0.0005, 0.002)  # 0.05% to 0.2% per candle
        volume_multiplier = np.random.uniform(1.3, 1.8)  # Higher volume
    else:  # SHORT
        # Create bearish momentum
        trend_change = np.random.uniform(-0.002, -0.0005)  # -0.2% to -0.05% per candle
        volume_multiplier = np.random.uniform(1.3, 1.8)  # Higher volume
    
    for i in range(100):
        # Add trend
        current_price = current_price * (1 + trend_change)
        # Add some randomness
        noise = np.random.uniform(-0.001, 0.001)
        current_price = current_price * (1 + noise)
        
        prices.append(current_price)
        volumes.append(base_volume * volume_multiplier * np.random.uniform(0.9, 1.1))
        
        if signal_type == 'LONG':
            # Close near high for bullish RSI
            close = current_price
            high = current_price * np.random.uniform(1.002, 1.005)
            low = current_price * np.random.uniform(0.997, 0.999)
            open_price = current_price * np.random.uniform(0.998, 1.001)
        else:  # SHORT
            # Close near low for bearish RSI
            close = current_price
            high = current_price * np.random.uniform(1.001, 1.003)
            low = current_price * np.random.uniform(0.995, 0.998)
            open_price = current_price * np.random.uniform(0.999, 1.002)
        
        candles.append({
            'timestamp': datetime.now() - timedelta(minutes=100-i),
            'open': open_price,
            'high': high,
            'low': low,
            'close': close,
            'volume': volumes[-1]
        })
    
    return candles


def demonstrate_trades():
    """Show what trades look like when triggered."""
    config = get_config()
    
    # Temporarily use relaxed settings for demo
    original_min_confidence = config.MIN_CONFIDENCE_SCORE
    original_volume_multiplier = config.VOLUME_MULTIPLIER
    
    config.MIN_CONFIDENCE_SCORE = 50.0  # Lower to 50%
    config.VOLUME_MULTIPLIER = 1.2  # Lower to 1.2x
    config.RSI_LONG_MIN = 50
    config.RSI_LONG_MAX = 75
    config.RSI_SHORT_MIN = 25
    config.RSI_SHORT_MAX = 50
    
    strategy = EMARSIStrategy(config)
    
    print("=" * 90)
    print(" TRADE DEMONSTRATION - What A Triggered Trade Looks Like".center(90))
    print("=" * 90)
    print(f"\n📊 Testing {len(TRADING_PAIRS)} Trading Pairs")
    print(f"\n⚙️  Demo Settings (relaxed to show trades):")
    print(f"   • Min Confidence: {config.MIN_CONFIDENCE_SCORE}% (vs {original_min_confidence}% in your app)")
    print(f"   • Volume Multiplier: {config.VOLUME_MULTIPLIER}x (vs {original_volume_multiplier}x in your app)")
    print(f"   • RSI Long: {config.RSI_LONG_MIN}-{config.RSI_LONG_MAX} (vs 55-70 in your app)")
    print(f"   • RSI Short: {config.RSI_SHORT_MIN}-{config.RSI_SHORT_MAX} (vs 30-45 in your app)")
    print("\n" + "=" * 90)
    
    signals_found = []
    
    # Test each pair with multiple attempts until we get a signal
    for pair in TRADING_PAIRS:
        print(f"\n📈 {pair}:")
        
        # Try LONG signal (up to 5 attempts)
        for attempt in range(5):
            candles = create_candles_with_signal(pair, 'LONG')
            signal = strategy.generate_signal(candles)
            if signal:
                indicators = strategy.calculate_indicators(candles)
                signals_found.append((pair, 'LONG', signal, indicators))
                
                print(f"  ✅ LONG TRADE TRIGGERED!")
                print(f"     ┌─ Entry Price: ${signal['price']:,.2f}")
                print(f"     ├─ Confidence: {signal['confidence']:.1f}%")
                print(f"     ├─ Take Profit: ${signal['take_profit']:,.2f} ({((signal['take_profit']/signal['price']-1)*100):+.2f}%)")
                print(f"     └─ Stop Loss: ${signal['stop_loss']:,.2f} ({((signal['stop_loss']/signal['price']-1)*100):+.2f}%)")
                print(f"     Market Conditions:")
                print(f"        • Price: ${indicators['price']:,.2f} | EMA: ${indicators['ema']:,.2f} (Price > EMA ✓)")
                print(f"        • RSI: {indicators['rsi']:.1f} (in range {config.RSI_LONG_MIN}-{config.RSI_LONG_MAX} ✓)")
                print(f"        • Volume: {indicators['volume_ratio']:.2f}x average (>{config.VOLUME_MULTIPLIER}x ✓)")
                break
        
        # Try SHORT signal (up to 5 attempts)
        for attempt in range(5):
            candles = create_candles_with_signal(pair, 'SHORT')
            signal = strategy.generate_signal(candles)
            if signal:
                indicators = strategy.calculate_indicators(candles)
                signals_found.append((pair, 'SHORT', signal, indicators))
                
                print(f"  ✅ SHORT TRADE TRIGGERED!")
                print(f"     ┌─ Entry Price: ${signal['price']:,.2f}")
                print(f"     ├─ Confidence: {signal['confidence']:.1f}%")
                print(f"     ├─ Take Profit: ${signal['take_profit']:,.2f} ({((signal['take_profit']/signal['price']-1)*100):+.2f}%)")
                print(f"     └─ Stop Loss: ${signal['stop_loss']:,.2f} ({((signal['stop_loss']/signal['price']-1)*100):+.2f}%)")
                print(f"     Market Conditions:")
                print(f"        • Price: ${indicators['price']:,.2f} | EMA: ${indicators['ema']:,.2f} (Price < EMA ✓)")
                print(f"        • RSI: {indicators['rsi']:.1f} (in range {config.RSI_SHORT_MIN}-{config.RSI_SHORT_MAX} ✓)")
                print(f"        • Volume: {indicators['volume_ratio']:.2f}x average (>{config.VOLUME_MULTIPLIER}x ✓)")
                break
        
        if len([s for s in signals_found if s[0] == pair]) == 0:
            print(f"  ⚠️  No signals after 10 attempts (conditions too strict)")
    
    # Restore original settings
    config.MIN_CONFIDENCE_SCORE = original_min_confidence
    config.VOLUME_MULTIPLIER = original_volume_multiplier
    
    # Summary
    print("\n" + "=" * 90)
    print(" SUMMARY".center(90))
    print("=" * 90)
    print(f"\n✅ Total Trades Generated: {len(signals_found)}\n")
    
    if signals_found:
        print("📋 TRADE DETAILS:\n")
        for i, (pair, direction, signal, indicators) in enumerate(signals_found, 1):
            potential_profit_pct = ((signal['take_profit'] / signal['price'] - 1) * 100)
            potential_loss_pct = abs((signal['stop_loss'] / signal['price'] - 1) * 100)
            
            print(f"{i}. {pair} {direction} Trade:")
            print(f"   Entry: ${signal['price']:,.2f}")
            print(f"   Take Profit: ${signal['take_profit']:,.2f} (+{potential_profit_pct:.2f}%)")
            print(f"   Stop Loss: ${signal['stop_loss']:,.2f} (-{potential_loss_pct:.2f}%)")
            print(f"   Risk/Reward: 1:{potential_profit_pct/potential_loss_pct:.2f}")
            print(f"   Confidence: {signal['confidence']:.1f}%")
            print()
        
        print("\n💡 WHAT THIS SHOWS:")
        print("   • When ALL conditions align, the bot generates a trade signal")
        print("   • Each trade has entry price, take profit, and stop loss")
        print("   • Higher confidence = better risk/reward ratio")
        print(f"\n⚠️  YOUR CURRENT SETTINGS ({original_min_confidence}% confidence, {original_volume_multiplier}x volume)")
        print("   are MUCH more conservative, which is why you're not seeing trades.")
        print("   All 4 conditions must align perfectly, which is rare.")
    else:
        print("⚠️  No trades generated even with relaxed settings.")
        print("   This indicates the test data generation needs refinement.")
    
    print("=" * 90)


if __name__ == '__main__':
    np.random.seed(42)  # For reproducible results
    demonstrate_trades()

