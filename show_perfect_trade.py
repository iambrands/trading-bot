#!/usr/bin/env python3
"""
Show what a perfect trade looks like - creates exact scenario that triggers signals.
"""

import sys
from datetime import datetime, timedelta
from typing import Dict, List

sys.path.insert(0, '.')
from strategy.ema_rsi_strategy import EMARSIStrategy
from config import get_config

TRADING_PAIRS = ['BTC-USD', 'ETH-USD', 'SOL-USD', 'ADA-USD', 'AVAX-USD', 'XRP-USD', 'DOGE-USD', 'MINA-USD', 'TRUMP-USD']

BASE_PRICES = {
    'BTC-USD': 95000.0, 'ETH-USD': 3500.0, 'SOL-USD': 150.0,
    'ADA-USD': 0.50, 'AVAX-USD': 40.0, 'XRP-USD': 0.60,
    'DOGE-USD': 0.15, 'MINA-USD': 1.20, 'TRUMP-USD': 12.0
}


def create_perfect_candles_for_signal(pair: str, signal_type: str = 'LONG'):
    """Create candles with exact values that will trigger a signal."""
    base_price = BASE_PRICES[pair]
    base_volume = 3000000
    
    candles = []
    
    # Create 150 candles with stable price to establish EMA baseline
    stable_price = base_price
    for i in range(150):
        candles.append({
            'timestamp': datetime.now() - timedelta(minutes=200-i),
            'open': stable_price,
            'high': stable_price * 1.001,
            'low': stable_price * 0.999,
            'close': stable_price,
            'volume': base_volume
        })
    
    # Now create 50 candles with perfect signal conditions
    if signal_type == 'LONG':
        # For LONG: price > EMA, RSI 50-75, volume > 1.2x
        # Start price slightly above EMA, gradual uptrend
        start_price = base_price * 1.02  # 2% above base
        trend = 1.001  # 0.1% per candle
        close_bias = 0.999  # Close near high for bullish RSI
        
        for i in range(50):
            current_price = start_price * (trend ** i)
            candles.append({
                'timestamp': datetime.now() - timedelta(minutes=50-i),
                'open': current_price * 0.9995,
                'high': current_price * 1.003,
                'low': current_price * close_bias,
                'close': current_price,  # Close near high
                'volume': base_volume * 1.5  # 1.5x volume (above 1.2x threshold)
            })
    else:  # SHORT
        # For SHORT: price < EMA, RSI 25-50, volume > 1.2x
        start_price = base_price * 0.98  # 2% below base
        trend = 0.999  # -0.1% per candle
        close_bias = 1.001  # Close near low for bearish RSI
        
        for i in range(50):
            current_price = start_price * (trend ** i)
            candles.append({
                'timestamp': datetime.now() - timedelta(minutes=50-i),
                'open': current_price * 1.0005,
                'high': current_price * close_bias,
                'low': current_price * 0.997,
                'close': current_price,  # Close near low
                'volume': base_volume * 1.5  # 1.5x volume
            })
    
    return candles


def show_trades():
    """Show what trades look like."""
    config = get_config()
    
    # Use relaxed settings for demo
    original_settings = {
        'min_confidence': config.MIN_CONFIDENCE_SCORE,
        'volume_multiplier': config.VOLUME_MULTIPLIER,
        'rsi_long_min': config.RSI_LONG_MIN,
        'rsi_long_max': config.RSI_LONG_MAX,
        'rsi_short_min': config.RSI_SHORT_MIN,
        'rsi_short_max': config.RSI_SHORT_MAX
    }
    
    config.MIN_CONFIDENCE_SCORE = 50.0
    config.VOLUME_MULTIPLIER = 1.2
    config.RSI_LONG_MIN = 50
    config.RSI_LONG_MAX = 75
    config.RSI_SHORT_MIN = 25
    config.RSI_SHORT_MAX = 50
    
    strategy = EMARSIStrategy(config)
    
    print("=" * 90)
    print(" PERFECT TRADE EXAMPLE - What A Trade Looks Like ".center(90))
    print("=" * 90)
    print(f"\n📊 Your Trading Pairs: {', '.join(TRADING_PAIRS)}")
    print(f"\n⚙️  Demo Settings:")
    print(f"   • Min Confidence: {config.MIN_CONFIDENCE_SCORE}% (vs {original_settings['min_confidence']}% in your app)")
    print(f"   • Volume Multiplier: {config.VOLUME_MULTIPLIER}x (vs {original_settings['volume_multiplier']}x)")
    print(f"   • RSI Long: {config.RSI_LONG_MIN}-{config.RSI_LONG_MAX} (vs {original_settings['rsi_long_min']}-{original_settings['rsi_long_max']})")
    print(f"   • RSI Short: {config.RSI_SHORT_MIN}-{config.RSI_SHORT_MAX} (vs {original_settings['rsi_short_min']}-{original_settings['rsi_short_max']})")
    print("\n" + "=" * 90)
    
    signals_found = []
    
    # Test first 3 pairs as examples
    for pair in TRADING_PAIRS[:3]:
        print(f"\n📈 {pair}:\n")
        
        # Try LONG
        candles = create_perfect_candles_for_signal(pair, 'LONG')
        signal = strategy.generate_signal(candles)
        indicators = strategy.calculate_indicators(candles)
        
        if signal:
            signals_found.append((pair, 'LONG', signal, indicators))
            print(f"  ✅ LONG TRADE SIGNAL GENERATED!")
            print(f"\n     📊 Trade Details:")
            print(f"        Entry Price:      ${signal['price']:,.2f}")
            print(f"        Confidence:       {signal['confidence']:.1f}%")
            print(f"        Take Profit:      ${signal['take_profit']:,.2f} ({((signal['take_profit']/signal['price']-1)*100):+.2f}%)")
            print(f"        Stop Loss:        ${signal['stop_loss']:,.2f} ({((signal['stop_loss']/signal['price']-1)*100):+.2f}%)")
            profit_pct = (signal['take_profit']/signal['price']-1)*100
            loss_pct = abs((signal['stop_loss']/signal['price']-1)*100)
            print(f"        Risk/Reward:      1:{profit_pct/loss_pct:.2f}")
            
            print(f"\n     📈 Market Conditions (all met):")
            print(f"        ✓ Price: ${indicators['price']:,.2f} > EMA: ${indicators['ema']:,.2f} (${((indicators['price']-indicators['ema'])/indicators['ema']*100):+.2f}%)")
            print(f"        ✓ RSI: {indicators['rsi']:.1f} (in range {config.RSI_LONG_MIN}-{config.RSI_LONG_MAX})")
            print(f"        ✓ Volume: {indicators['volume_ratio']:.2f}x average (>{config.VOLUME_MULTIPLIER}x threshold)")
        else:
            print(f"  ❌ No LONG signal (conditions not perfect)")
            if indicators:
                print(f"        Price: ${indicators['price']:,.2f}, EMA: ${indicators['ema']:,.2f}, RSI: {indicators['rsi']:.1f}, Vol: {indicators['volume_ratio']:.2f}x")
        
        # Try SHORT
        candles = create_perfect_candles_for_signal(pair, 'SHORT')
        signal = strategy.generate_signal(candles)
        indicators = strategy.calculate_indicators(candles)
        
        if signal:
            signals_found.append((pair, 'SHORT', signal, indicators))
            print(f"\n  ✅ SHORT TRADE SIGNAL GENERATED!")
            print(f"\n     📊 Trade Details:")
            print(f"        Entry Price:      ${signal['price']:,.2f}")
            print(f"        Confidence:       {signal['confidence']:.1f}%")
            print(f"        Take Profit:      ${signal['take_profit']:,.2f} ({((signal['take_profit']/signal['price']-1)*100):+.2f}%)")
            print(f"        Stop Loss:        ${signal['stop_loss']:,.2f} ({((signal['stop_loss']/signal['price']-1)*100):+.2f}%)")
            profit_pct = abs((signal['take_profit']/signal['price']-1)*100)
            loss_pct = (signal['stop_loss']/signal['price']-1)*100
            print(f"        Risk/Reward:      1:{profit_pct/loss_pct:.2f}")
            
            print(f"\n     📉 Market Conditions (all met):")
            print(f"        ✓ Price: ${indicators['price']:,.2f} < EMA: ${indicators['ema']:,.2f} (${((indicators['price']-indicators['ema'])/indicators['ema']*100):+.2f}%)")
            print(f"        ✓ RSI: {indicators['rsi']:.1f} (in range {config.RSI_SHORT_MIN}-{config.RSI_SHORT_MAX})")
            print(f"        ✓ Volume: {indicators['volume_ratio']:.2f}x average (>{config.VOLUME_MULTIPLIER}x threshold)")
        else:
            print(f"\n  ❌ No SHORT signal (conditions not perfect)")
            if indicators:
                print(f"        Price: ${indicators['price']:,.2f}, EMA: ${indicators['ema']:,.2f}, RSI: {indicators['rsi']:.1f}, Vol: {indicators['volume_ratio']:.2f}x")
    
    # Restore settings
    config.MIN_CONFIDENCE_SCORE = original_settings['min_confidence']
    config.VOLUME_MULTIPLIER = original_settings['volume_multiplier']
    config.RSI_LONG_MIN = original_settings['rsi_long_min']
    config.RSI_LONG_MAX = original_settings['rsi_long_max']
    config.RSI_SHORT_MIN = original_settings['rsi_short_min']
    config.RSI_SHORT_MAX = original_settings['rsi_short_max']
    
    print("\n" + "=" * 90)
    print(" SUMMARY ".center(90))
    print("=" * 90)
    print(f"\n✅ Trades Generated: {len(signals_found)}\n")
    
    if signals_found:
        print("💡 THIS IS WHAT HAPPENS WHEN A TRADE IS TRIGGERED:")
        print("   1. Bot detects all 4 conditions are met")
        print("   2. Calculates confidence score (higher = better)")
        print("   3. Sets take profit and stop loss based on confidence")
        print("   4. Trade is executed at entry price")
        print("   5. Bot monitors for exit conditions (TP, SL, or timeout)")
        print(f"\n⚠️  Your current settings ({original_settings['min_confidence']}% confidence, {original_settings['volume_multiplier']}x volume)")
        print("   are MUCH stricter, so trades are rare. This is actually GOOD for quality,")
        print("   but means you'll see fewer trades overall.")
    
    print("=" * 90)


if __name__ == '__main__':
    show_trades()

