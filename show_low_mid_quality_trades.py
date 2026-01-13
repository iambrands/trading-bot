#!/usr/bin/env python3
"""
Show what low-to-mid quality trades look like with relaxed settings.
These are the types of trades you'd see if you relaxed your current settings.
"""

from config import get_config

TRADING_PAIRS = ['BTC-USD', 'ETH-USD', 'SOL-USD', 'ADA-USD', 'AVAX-USD', 'XRP-USD', 'DOGE-USD', 'MINA-USD', 'TRUMP-USD']

BASE_PRICES = {
    'BTC-USD': 95000.0, 'ETH-USD': 3500.0, 'SOL-USD': 150.0,
    'ADA-USD': 0.50, 'AVAX-USD': 40.0, 'XRP-USD': 0.60,
    'DOGE-USD': 0.15, 'MINA-USD': 1.20, 'TRUMP-USD': 12.0
}

def show_trade_examples():
    """Show examples of low-to-mid quality trades."""
    config = get_config()
    
    print("=" * 90)
    print(" LOW TO MID QUALITY TRADES - Examples with Relaxed Settings ".center(90))
    print("=" * 90)
    print(f"\n⚙️  Your Current Settings (HIGH QUALITY):")
    print(f"   • Min Confidence: {config.MIN_CONFIDENCE_SCORE}%")
    print(f"   • Volume Multiplier: {config.VOLUME_MULTIPLIER}x")
    print(f"   • RSI Long: {config.RSI_LONG_MIN}-{config.RSI_LONG_MAX}")
    print(f"   • RSI Short: {config.RSI_SHORT_MIN}-{config.RSI_SHORT_MAX}")
    print("\n" + "=" * 90)
    
    # Example LOW QUALITY trades (with relaxed settings)
    print("\n\n🔴 LOW QUALITY TRADES (40-55% Confidence)")
    print("   Settings: 40% confidence, 1.1x volume, RSI 45-80 (long), 20-55 (short)")
    print("   These would trigger with VERY relaxed settings:\n")
    
    low_quality_trades = [
        {
            'pair': 'BTC-USD',
            'type': 'LONG',
            'entry': 95200.0,
            'confidence': 45.0,
            'price': 95200.0,
            'ema': 95100.0,  # Price just slightly above EMA
            'rsi': 68.0,  # RSI near top of relaxed range
            'volume_ratio': 1.15,  # Just barely above 1.1x threshold
            'take_profit_pct': 0.20,
            'stop_loss_pct': 0.35
        },
        {
            'pair': 'ETH-USD',
            'type': 'SHORT',
            'entry': 3480.0,
            'confidence': 42.0,
            'price': 3480.0,
            'ema': 3490.0,  # Price just slightly below EMA
            'rsi': 48.0,  # RSI in middle of relaxed range
            'volume_ratio': 1.12,  # Barely above threshold
            'take_profit_pct': 0.18,
            'stop_loss_pct': 0.40
        },
        {
            'pair': 'SOL-USD',
            'type': 'LONG',
            'entry': 151.50,
            'confidence': 48.0,
            'price': 151.50,
            'ema': 150.80,
            'rsi': 72.0,
            'volume_ratio': 1.18,
            'take_profit_pct': 0.22,
            'stop_loss_pct': 0.38
        }
    ]
    
    for i, trade in enumerate(low_quality_trades, 1):
        tp = trade['entry'] * (1 + trade['take_profit_pct']/100) if trade['type'] == 'LONG' else trade['entry'] * (1 - trade['take_profit_pct']/100)
        sl = trade['entry'] * (1 - trade['stop_loss_pct']/100) if trade['type'] == 'LONG' else trade['entry'] * (1 + trade['stop_loss_pct']/100)
        
        print(f"\n{i}. {trade['pair']} {trade['type']} - LOW QUALITY (Confidence: {trade['confidence']:.1f}%)")
        print(f"   📊 Trade Details:")
        print(f"      Entry Price:        ${trade['entry']:,.2f}")
        print(f"      Confidence:         {trade['confidence']:.1f}% ⚠️  (LOW)")
        print(f"      Take Profit:        ${tp:,.2f} ({trade['take_profit_pct']:+.2f}%)")
        print(f"      Stop Loss:          ${sl:,.2f} ({-trade['stop_loss_pct']:+.2f}%)")
        print(f"      Risk/Reward:        1:{trade['take_profit_pct']/trade['stop_loss_pct']:.2f} ⚠️  (POOR)")
        print(f"   📈 Market Conditions:")
        print(f"      Price: ${trade['price']:,.2f} | EMA: ${trade['ema']:,.2f} (Difference: {((trade['price']-trade['ema'])/trade['ema']*100):+.2f}%)")
        print(f"      RSI: {trade['rsi']:.1f} (near edge of relaxed range)")
        print(f"      Volume: {trade['volume_ratio']:.2f}x (barely above {1.1:.1f}x threshold)")
        print(f"   ⚠️  Why it's LOW QUALITY:")
        print(f"      • Low confidence score ({trade['confidence']:.1f}%)")
        print(f"      • Price barely above/below EMA")
        print(f"      • Volume just barely meets threshold")
        print(f"      • Poor risk/reward ratio")
    
    # Example MID QUALITY trades
    print("\n\n" + "=" * 90)
    print("\n🟡 MID QUALITY TRADES (55-70% Confidence)")
    print("   Settings: 55% confidence, 1.2x volume, RSI 50-75 (long), 25-50 (short)")
    print("   These would trigger with moderately relaxed settings:\n")
    
    mid_quality_trades = [
        {
            'pair': 'BTC-USD',
            'type': 'LONG',
            'entry': 96200.0,
            'confidence': 62.0,
            'price': 96200.0,
            'ema': 95500.0,  # Price noticeably above EMA
            'rsi': 65.0,  # RSI in good range
            'volume_ratio': 1.35,  # Good volume
            'take_profit_pct': 0.25,
            'stop_loss_pct': 0.25
        },
        {
            'pair': 'ETH-USD',
            'type': 'SHORT',
            'entry': 3420.0,
            'confidence': 58.0,
            'price': 3420.0,
            'ema': 3480.0,  # Price noticeably below EMA
            'rsi': 38.0,
            'volume_ratio': 1.28,
            'take_profit_pct': 0.28,
            'stop_loss_pct': 0.30
        },
        {
            'pair': 'SOL-USD',
            'type': 'LONG',
            'entry': 154.20,
            'confidence': 65.0,
            'price': 154.20,
            'ema': 151.50,
            'rsi': 68.0,
            'volume_ratio': 1.42,
            'take_profit_pct': 0.27,
            'stop_loss_pct': 0.23
        },
        {
            'pair': 'ADA-USD',
            'type': 'SHORT',
            'entry': 0.495,
            'confidence': 60.0,
            'price': 0.495,
            'ema': 0.505,
            'rsi': 42.0,
            'volume_ratio': 1.32,
            'take_profit_pct': 0.26,
            'stop_loss_pct': 0.28
        }
    ]
    
    for i, trade in enumerate(mid_quality_trades, 1):
        tp = trade['entry'] * (1 + trade['take_profit_pct']/100) if trade['type'] == 'LONG' else trade['entry'] * (1 - trade['take_profit_pct']/100)
        sl = trade['entry'] * (1 - trade['stop_loss_pct']/100) if trade['type'] == 'LONG' else trade['entry'] * (1 + trade['stop_loss_pct']/100)
        
        print(f"\n{i}. {trade['pair']} {trade['type']} - MID QUALITY (Confidence: {trade['confidence']:.1f}%)")
        print(f"   📊 Trade Details:")
        print(f"      Entry Price:        ${trade['entry']:,.2f}")
        print(f"      Confidence:         {trade['confidence']:.1f}% (MODERATE)")
        print(f"      Take Profit:        ${tp:,.2f} ({trade['take_profit_pct']:+.2f}%)")
        print(f"      Stop Loss:          ${sl:,.2f} ({-trade['stop_loss_pct']:+.2f}%)")
        print(f"      Risk/Reward:        1:{trade['take_profit_pct']/trade['stop_loss_pct']:.2f}")
        print(f"   📈 Market Conditions:")
        print(f"      Price: ${trade['price']:,.2f} | EMA: ${trade['ema']:,.2f} (Difference: {((trade['price']-trade['ema'])/trade['ema']*100):+.2f}%)")
        print(f"      RSI: {trade['rsi']:.1f} (good range)")
        print(f"      Volume: {trade['volume_ratio']:.2f}x (above {1.2:.1f}x threshold)")
        print(f"   ✓ Better quality than low quality trades:")
        print(f"      • Moderate confidence score ({trade['confidence']:.1f}%)")
        print(f"      • Clear price trend vs EMA")
        print(f"      • Good volume confirmation")
        print(f"      • Reasonable risk/reward")
    
    # Comparison
    print("\n\n" + "=" * 90)
    print(" QUALITY COMPARISON ".center(90))
    print("=" * 90)
    
    print(f"\n📊 YOUR CURRENT SETTINGS (HIGH QUALITY):")
    print(f"   • Min Confidence: {config.MIN_CONFIDENCE_SCORE}%")
    print(f"   • Volume Multiplier: {config.VOLUME_MULTIPLIER}x")
    print(f"   • RSI Long: {config.RSI_LONG_MIN}-{config.RSI_LONG_MAX}")
    print(f"   • RSI Short: {config.RSI_SHORT_MIN}-{config.RSI_SHORT_MAX}")
    print(f"   ✅ Only HIGH quality trades (70%+ confidence) trigger")
    print(f"   ✅ Very selective - only best setups")
    print(f"   ⚠️  Result: Few trades, but highest win probability")
    
    print(f"\n📊 RELAXED SETTINGS (LOW-MID QUALITY):")
    print(f"   • Min Confidence: 40-55%")
    print(f"   • Volume Multiplier: 1.1-1.2x")
    print(f"   • RSI Long: 45-80 (wider)")
    print(f"   • RSI Short: 20-55 (wider)")
    print(f"   ⚠️  LOW-MID quality trades (40-70% confidence) trigger")
    print(f"   ⚠️  Less selective - more setups qualify")
    print(f"   ✅ Result: More trades, but lower win probability")
    
    print(f"\n💡 TO SEE MORE TRADES IN YOUR APP:")
    print(f"   1. Lower confidence from {config.MIN_CONFIDENCE_SCORE}% to 50-60%")
    print(f"   2. Lower volume from {config.VOLUME_MULTIPLIER}x to 1.2-1.3x")
    print(f"   3. Widen RSI ranges slightly (e.g., Long: 50-75, Short: 25-50)")
    print(f"\n   ⚠️  TRADE-OFF: More trades = Lower quality = Lower win rate")
    print(f"   ✅ CURRENT: Few trades = High quality = Higher win rate")
    
    print("=" * 90)


if __name__ == '__main__':
    show_trade_examples()

