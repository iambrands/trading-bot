#!/usr/bin/env python3
"""
Test script to simulate trading signals based on your trading pairs.
This script generates realistic market data and shows what trades would be triggered.
"""

import random
import sys
from datetime import datetime, timedelta
from typing import Dict, List
import numpy as np
import pandas as pd

# Import the actual strategy
sys.path.insert(0, '.')
from strategy.ema_rsi_strategy import EMARSIStrategy
from config import get_config

# Your trading pairs
TRADING_PAIRS = [
    'BTC-USD', 
    'ETH-USD', 
    'SOL-USD', 
    'ADA-USD', 
    'AVAX-USD', 
    'XRP-USD', 
    'DOGE-USD', 
    'MINA-USD', 
    'TRUMP-USD'
]

# Realistic base prices for each pair (approximate current market prices)
BASE_PRICES = {
    'BTC-USD': 95000.0,
    'ETH-USD': 3500.0,
    'SOL-USD': 150.0,
    'ADA-USD': 0.50,
    'AVAX-USD': 40.0,
    'XRP-USD': 0.60,
    'DOGE-USD': 0.15,
    'MINA-USD': 1.20,
    'TRUMP-USD': 12.0  # Meme token - use realistic price
}


def generate_realistic_candles(pair: str, num_candles: int = 200, trend: str = 'neutral') -> List[Dict]:
    """Generate realistic candle data that can trigger trading signals."""
    base_price = BASE_PRICES.get(pair, 100.0)
    
    # Generate price movements with some trend
    candles = []
    prices = []
    volumes = []
    current_price = base_price
    
    for i in range(num_candles):
        # Add some volatility (1-3% per candle for crypto)
        volatility = random.uniform(0.005, 0.03)
        
        # Add trend bias
        if trend == 'bullish':
            trend_bias = random.uniform(0.001, 0.005)  # Slight upward bias
        elif trend == 'bearish':
            trend_bias = random.uniform(-0.005, -0.001)  # Slight downward bias
        else:
            trend_bias = random.uniform(-0.002, 0.002)  # Neutral
        
        # Random price movement
        change = random.uniform(-volatility, volatility) + trend_bias
        current_price = current_price * (1 + change)
        
        # Generate OHLC from current price
        high = current_price * random.uniform(1.001, 1.02)
        low = current_price * random.uniform(0.98, 0.999)
        open_price = current_price * random.uniform(0.995, 1.005)
        close_price = current_price
        
        # Generate volume (higher during volatile moves)
        volume = random.uniform(1000000, 10000000) * (1 + abs(change) * 10)
        
        candles.append({
            'timestamp': datetime.utcnow() - timedelta(minutes=num_candles - i),
            'open': open_price,
            'high': high,
            'low': low,
            'close': close_price,
            'volume': volume
        })
        
        prices.append(close_price)
        volumes.append(volume)
    
    return candles


def generate_bullish_setup(pair: str, num_candles: int = 200) -> List[Dict]:
    """Generate candles that should trigger a LONG signal.
    Creates a scenario where: price > EMA, RSI in 55-70 range, volume > 1.5x average."""
    base_price = BASE_PRICES.get(pair, 100.0)
    candles = []
    
    # Build up history first (need enough candles for EMA calculation)
    # Start with price around EMA, then create bullish momentum
    current_price = base_price
    base_volume = random.uniform(2000000, 4000000)
    
    # First 150 candles - build stable base with price near EMA
    for i in range(150):
        # Small random movements around base price
        change = random.uniform(-0.005, 0.005)
        current_price = current_price * (1 + change)
        
        high = current_price * random.uniform(1.002, 1.008)
        low = current_price * random.uniform(0.992, 0.998)
        open_price = current_price * random.uniform(0.998, 1.002)
        close_price = current_price
        
        volume = base_volume * random.uniform(0.8, 1.2)
        
        candles.append({
            'timestamp': datetime.utcnow() - timedelta(minutes=200 - i),
            'open': open_price,
            'high': high,
            'low': low,
            'close': close_price,
            'volume': volume
        })
    
    # Last 50 candles - create bullish breakout with proper RSI and volume
    # Need: price > EMA, RSI 55-70, volume > 1.5x average
    for i in range(50):
        # Moderate upward movement (not too extreme to keep RSI in range)
        change = random.uniform(0.003, 0.01)
        current_price = current_price * (1 + change)
        
        high = current_price * random.uniform(1.003, 1.012)
        low = current_price * random.uniform(0.995, 0.999)
        open_price = current_price * random.uniform(0.998, 1.003)
        close_price = current_price
        
        # High volume (1.6-2.5x average) to trigger signal
        volume = base_volume * random.uniform(1.6, 2.5)
        
        candles.append({
            'timestamp': datetime.utcnow() - timedelta(minutes=50 - i),
            'open': open_price,
            'high': high,
            'low': low,
            'close': close_price,
            'volume': volume
        })
    
    return candles


def generate_bearish_setup(pair: str, num_candles: int = 200) -> List[Dict]:
    """Generate candles that should trigger a SHORT signal.
    Creates a scenario where: price < EMA, RSI in 30-45 range, volume > 1.5x average."""
    base_price = BASE_PRICES.get(pair, 100.0)
    candles = []
    
    # Build up history first
    current_price = base_price
    base_volume = random.uniform(2000000, 4000000)
    
    # First 150 candles - build stable base with price near EMA
    for i in range(150):
        # Small random movements around base price
        change = random.uniform(-0.005, 0.005)
        current_price = current_price * (1 + change)
        
        high = current_price * random.uniform(1.002, 1.008)
        low = current_price * random.uniform(0.992, 0.998)
        open_price = current_price * random.uniform(0.998, 1.002)
        close_price = current_price
        
        volume = base_volume * random.uniform(0.8, 1.2)
        
        candles.append({
            'timestamp': datetime.utcnow() - timedelta(minutes=200 - i),
            'open': open_price,
            'high': high,
            'low': low,
            'close': close_price,
            'volume': volume
        })
    
    # Last 50 candles - create bearish breakdown with proper RSI and volume
    # Need: price < EMA, RSI 30-45, volume > 1.5x average
    for i in range(50):
        # Moderate downward movement (not too extreme to keep RSI in range)
        change = random.uniform(-0.01, -0.003)
        current_price = current_price * (1 + change)
        
        high = current_price * random.uniform(1.001, 1.005)
        low = current_price * random.uniform(0.988, 0.995)
        open_price = current_price * random.uniform(0.997, 1.002)
        close_price = current_price
        
        # High volume (1.6-2.5x average) to trigger signal
        volume = base_volume * random.uniform(1.6, 2.5)
        
        candles.append({
            'timestamp': datetime.utcnow() - timedelta(minutes=50 - i),
            'open': open_price,
            'high': high,
            'low': low,
            'close': close_price,
            'volume': volume
        })
    
    return candles


def test_strategy_signals():
    """Test the strategy with all trading pairs and show what signals would be generated."""
    config = get_config()
    strategy = EMARSIStrategy(config)
    
    print("=" * 80)
    print("TRADING SIGNAL SIMULATOR")
    print("=" * 80)
    print(f"\nTesting {len(TRADING_PAIRS)} trading pairs...")
    print(f"Strategy Settings:")
    print(f"  - EMA Period: {config.EMA_PERIOD}")
    print(f"  - RSI Period: {config.RSI_PERIOD}")
    print(f"  - Volume Multiplier: {config.VOLUME_MULTIPLIER}x")
    print(f"  - Min Confidence: {config.MIN_CONFIDENCE_SCORE}%")
    print(f"  - RSI Long Range: {config.RSI_LONG_MIN}-{config.RSI_LONG_MAX}")
    print(f"  - RSI Short Range: {config.RSI_SHORT_MIN}-{config.RSI_SHORT_MAX}")
    print("\n" + "=" * 80)
    
    signals_found = []
    
    # Test each pair with different market scenarios
    for pair in TRADING_PAIRS:
        print(f"\n📊 Testing {pair}...")
        
        # Test 1: Neutral market (likely no signal)
        candles = generate_realistic_candles(pair, num_candles=200, trend='neutral')
        signal = strategy.generate_signal(candles)
        if signal:
            signals_found.append((pair, 'NEUTRAL', signal))
            print(f"  ✅ Signal found in NEUTRAL market: {signal['type']} @ ${signal['price']:.2f} (Confidence: {signal['confidence']:.1f}%)")
        else:
            print(f"  ❌ No signal in NEUTRAL market")
        
        # Test 2: Bullish setup (should trigger LONG)
        candles = generate_bullish_setup(pair, num_candles=200)
        signal = strategy.generate_signal(candles)
        if signal:
            signals_found.append((pair, 'BULLISH', signal))
            print(f"  ✅ LONG signal found in BULLISH market: @ ${signal['price']:.2f} (Confidence: {signal['confidence']:.1f}%)")
            print(f"     Take Profit: ${signal['take_profit']:.2f} ({((signal['take_profit']/signal['price']-1)*100):.2f}%)")
            print(f"     Stop Loss: ${signal['stop_loss']:.2f} ({((signal['stop_loss']/signal['price']-1)*100):.2f}%)")
        else:
            print(f"  ❌ No signal in BULLISH market (conditions not met)")
            # Show why no signal
            indicators = strategy.calculate_indicators(candles)
            if indicators:
                print(f"     Price: ${indicators['price']:.2f}, EMA: ${indicators['ema']:.2f}, RSI: {indicators['rsi']:.1f}, Volume Ratio: {indicators['volume_ratio']:.2f}x")
        
        # Test 3: Bearish setup (should trigger SHORT)
        candles = generate_bearish_setup(pair, num_candles=200)
        signal = strategy.generate_signal(candles)
        if signal:
            signals_found.append((pair, 'BEARISH', signal))
            print(f"  ✅ SHORT signal found in BEARISH market: @ ${signal['price']:.2f} (Confidence: {signal['confidence']:.1f}%)")
            print(f"     Take Profit: ${signal['take_profit']:.2f} ({((signal['take_profit']/signal['price']-1)*100):.2f}%)")
            print(f"     Stop Loss: ${signal['stop_loss']:.2f} ({((signal['stop_loss']/signal['price']-1)*100):.2f}%)")
        else:
            print(f"  ❌ No signal in BEARISH market (conditions not met)")
            # Show why no signal
            indicators = strategy.calculate_indicators(candles)
            if indicators:
                print(f"     Price: ${indicators['price']:.2f}, EMA: ${indicators['ema']:.2f}, RSI: {indicators['rsi']:.1f}, Volume Ratio: {indicators['volume_ratio']:.2f}x")
    
    # Summary
    print("\n" + "=" * 80)
    print("SUMMARY")
    print("=" * 80)
    print(f"\nTotal signals found: {len(signals_found)}")
    
    if signals_found:
        print("\n📈 SIGNALS THAT WOULD TRIGGER TRADES:\n")
        for pair, market_type, signal in signals_found:
            print(f"{pair} ({market_type} market):")
            print(f"  Type: {signal['type']}")
            print(f"  Entry: ${signal['price']:.2f}")
            print(f"  Confidence: {signal['confidence']:.1f}%")
            print(f"  Take Profit: ${signal['take_profit']:.2f} ({((signal['take_profit']/signal['price']-1)*100):+.2f}%)")
            print(f"  Stop Loss: ${signal['stop_loss']:.2f} ({((signal['stop_loss']/signal['price']-1)*100):+.2f}%)")
            print()
    else:
        print("\n⚠️  NO SIGNALS GENERATED")
        print("\nThis means the current strategy settings are very conservative.")
        print("To see more trades, you could:")
        print("  1. Lower MIN_CONFIDENCE_SCORE (currently {})".format(config.MIN_CONFIDENCE_SCORE))
        print("  2. Increase VOLUME_MULTIPLIER tolerance (currently {}x)".format(config.VOLUME_MULTIPLIER))
        print("  3. Widen RSI ranges (Long: {}-{}, Short: {}-{})".format(
            config.RSI_LONG_MIN, config.RSI_LONG_MAX, 
            config.RSI_SHORT_MIN, config.RSI_SHORT_MAX
        ))
    
    print("=" * 80)


if __name__ == '__main__':
    test_strategy_signals()

