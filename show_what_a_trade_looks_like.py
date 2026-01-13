#!/usr/bin/env python3
"""
Show exactly what a triggered trade looks like - creates realistic example.
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


def create_realistic_candles(pair: str, signal_type: str = 'LONG'):
    """Create realistic candles using pandas to get proper RSI values."""
    base_price = BASE_PRICES[pair]
    base_volume = 3000000
    
    # Generate price series with proper statistics for RSI calculation
    np.random.seed(42)  # For reproducibility
    
    # Create 200 price points
    if signal_type == 'LONG':
        # Bullish: start low, trend up, create RSI in 50-75 range
        returns = np.random.normal(0.001, 0.01, 200)  # Small positive trend
        # Add some upward bias
        returns[:100] += np.random.normal(-0.0005, 0.008, 100)  # First half: slight down/mixed
        returns[100:] += np.random.normal(0.002, 0.008, 100)   # Second half: upward trend
    else:  # SHORT
        # Bearish: start high, trend down, create RSI in 25-50 range
        returns = np.random.normal(-0.001, 0.01, 200)  # Small negative trend
        returns[:100] += np.random.normal(0.0005, 0.008, 100)   # First half: slight up/mixed
        returns[100:] += np.random.normal(-0.002, 0.008, 100)  # Second half: downward trend
    
    # Convert returns to prices
    prices = [base_price]
    for ret in returns:
        prices.append(prices[-1] * (1 + ret))
    
    # Ensure prices stay realistic
    prices = np.array(prices[1:201])  # Take last 200
    
    # Create candles
    candles = []
    volumes = []
    
    for i, price in enumerate(prices):
        if signal_type == 'LONG' and i >= 150:
            # High volume for last 50 candles (1.5-2x)
            volume = base_volume * np.random.uniform(1.5, 2.0)
        elif signal_type == 'SHORT' and i >= 150:
            volume = base_volume * np.random.uniform(1.5, 2.0)
        else:
            volume = base_volume * np.random.uniform(0.8, 1.2)
        
        volumes.append(volume)
        
        # Create OHLC
        if signal_type == 'LONG':
            high = price * np.random.uniform(1.001, 1.005)
            low = price * np.random.uniform(0.997, 0.999)
            open_price = price * np.random.uniform(0.998, 1.001)
            close = price
        else:  # SHORT
            high = price * np.random.uniform(1.001, 1.003)
            low = price * np.random.uniform(0.995, 0.998)
            open_price = price * np.random.uniform(0.999, 1.002)
            close = price
        
        candles.append({
            'timestamp': datetime.now() - timedelta(minutes=200-i),
            'open': open_price,
            'high': high,
            'low': low,
            'close': close,
            'volume': volume
        })
    
    return candles


def show_trade_example():
    """Show what a trade looks like when triggered."""
    config = get_config()
    
    # Temporarily use relaxed settings
    original_min_confidence = config.MIN_CONFIDENCE_SCORE
    original_volume_multiplier = config.VOLUME_MULTIPLIER
    
    config.MIN_CONFIDENCE_SCORE = 50.0
    config.VOLUME_MULTIPLIER = 1.2
    config.RSI_LONG_MIN = 50
    config.RSI_LONG_MAX = 75
    config.RSI_SHORT_MIN = 25
    config.RSI_SHORT_MAX = 50
    
    strategy = EMARSIStrategy(config)
    
    print("=" * 90)
    print(" WHAT A TRADE LOOKS LIKE - Example with Your Trading Pairs ".center(90))
    print("=" * 90)
    print(f"\n📊 Testing pairs: {', '.join(TRADING_PAIRS[:5])}...")
    print(f"\n⚙️  Using Relaxed Settings for Demo:")
    print(f"   • Min Confidence: {config.MIN_CONFIDENCE_SCORE}% (your app: {original_min_confidence}%)")
    print(f"   • Volume Multiplier: {config.VOLUME_MULTIPLIER}x (your app: {original_volume_multiplier}x)")
    print(f"   • RSI Long: {config.RSI_LONG_MIN}-{config.RSI_LONG_MAX}")
    print(f"   • RSI Short: {config.RSI_SHORT_MIN}-{config.RSI_SHORT_MAX}")
    print("\n" + "=" * 90)
    
    signals_found = []
    
    # Test multiple pairs with multiple attempts
    for pair in TRADING_PAIRS[:5]:
        for direction in ['LONG', 'SHORT']:
            for attempt in range(10):  # Try up to 10 times
                candles = create_realistic_candles(pair, direction)
                signal = strategy.generate_signal(candles)
                
                if signal:
                    indicators = strategy.calculate_indicators(candles)
                    signals_found.append((pair, direction, signal, indicators))
                    
                    print(f"\n✅ {pair} {direction} TRADE TRIGGERED! (Attempt {attempt+1})\n")
                    print(f"   📊 TRADE DETAILS:")
                    print(f"      Entry Price:        ${signal['price']:,.2f}")
                    print(f"      Confidence Score:   {signal['confidence']:.1f}%")
                    print(f"      Take Profit:        ${signal['take_profit']:,.2f} ({((signal['take_profit']/signal['price']-1)*100):+.2f}%)")
                    print(f"      Stop Loss:          ${signal['stop_loss']:,.2f} ({((signal['stop_loss']/signal['price']-1)*100):+.2f}%)")
                    
                    profit_pct = abs((signal['take_profit']/signal['price']-1)*100)
                    loss_pct = abs((signal['stop_loss']/signal['price']-1)*100)
                    print(f"      Risk/Reward Ratio:  1:{profit_pct/loss_pct:.2f}")
                    
                    print(f"\n   📈 MARKET CONDITIONS (All Met):")
                    price_vs_ema = ((indicators['price'] - indicators['ema']) / indicators['ema']) * 100
                    print(f"      ✓ Price vs EMA:     ${indicators['price']:,.2f} vs ${indicators['ema']:,.2f} ({price_vs_ema:+.2f}%)")
                    print(f"      ✓ RSI:              {indicators['rsi']:.1f}")
                    print(f"      ✓ Volume Ratio:     {indicators['volume_ratio']:.2f}x average")
                    print(f"      ✓ Confidence:       {signal['confidence']:.1f}%")
                    
                    break  # Found a signal, move to next pair/direction
    
    # Restore settings
    config.MIN_CONFIDENCE_SCORE = original_min_confidence
    config.VOLUME_MULTIPLIER = original_volume_multiplier
    
    print("\n" + "=" * 90)
    print(" SUMMARY ".center(90))
    print("=" * 90)
    print(f"\n✅ Total Trades Generated: {len(signals_found)}\n")
    
    if signals_found:
        print("💡 THIS IS WHAT A TRADE LOOKS LIKE:\n")
        print("   When the bot detects all conditions are met, it creates a trade signal with:")
        print("   • Entry Price - The price to enter the trade")
        print("   • Take Profit - Target price to exit with profit")
        print("   • Stop Loss - Safety exit if trade goes wrong")
        print("   • Confidence Score - How strong the signal is (0-100%)")
        print("\n   The bot then:")
        print("   1. Places an order at the entry price")
        print("   2. Sets take profit and stop loss orders")
        print("   3. Monitors the position until it hits TP, SL, or times out")
        print("\n⚠️  Your current settings are MUCH stricter ({original_min_confidence}% confidence, {original_volume_multiplier}x volume),")
        print("   which is why you're not seeing trades. This is actually GOOD - it means")
        print("   only very high-quality setups trigger trades.")
    else:
        print("⚠️  Even with relaxed settings, no signals were generated.")
        print("   This shows how rare it is for all conditions to align perfectly.")
        print("\n💡 To see trades in the app, consider:")
        print(f"   • Lowering confidence from {original_min_confidence}% to 50-60%")
        print(f"   • Lowering volume multiplier from {original_volume_multiplier}x to 1.2-1.3x")
        print("   • Widening RSI ranges slightly")
    
    print("=" * 90)


if __name__ == '__main__':
    show_trade_example()

