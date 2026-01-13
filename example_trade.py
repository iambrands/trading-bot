#!/usr/bin/env python3
"""
Show what a trade looks like with example values.
This demonstrates the structure of a trade signal.
"""

from config import get_config

TRADING_PAIRS = ['BTC-USD', 'ETH-USD', 'SOL-USD', 'ADA-USD', 'AVAX-USD', 'XRP-USD', 'DOGE-USD', 'MINA-USD', 'TRUMP-USD']

BASE_PRICES = {
    'BTC-USD': 95000.0, 'ETH-USD': 3500.0, 'SOL-USD': 150.0,
    'ADA-USD': 0.50, 'AVAX-USD': 40.0, 'XRP-USD': 0.60,
    'DOGE-USD': 0.15, 'MINA-USD': 1.20, 'TRUMP-USD': 12.0
}

def show_example_trades():
    """Show example trade structures."""
    config = get_config()
    
    print("=" * 90)
    print(" EXAMPLE TRADES - What A Trade Looks Like ".center(90))
    print("=" * 90)
    print(f"\n📊 Your Trading Pairs: {', '.join(TRADING_PAIRS)}")
    print(f"\n⚙️  Current Settings:")
    print(f"   • Min Confidence: {config.MIN_CONFIDENCE_SCORE}%")
    print(f"   • Volume Multiplier: {config.VOLUME_MULTIPLIER}x")
    print(f"   • RSI Long Range: {config.RSI_LONG_MIN}-{config.RSI_LONG_MAX}")
    print(f"   • RSI Short Range: {config.RSI_SHORT_MIN}-{config.RSI_SHORT_MAX}")
    print("\n" + "=" * 90)
    
    # Show example LONG trade
    print("\n📈 EXAMPLE LONG TRADE (BTC-USD):")
    print("\n   When these conditions are met:")
    print(f"   ✓ Price ($97,500) > EMA ($95,000)")
    print(f"   ✓ RSI (62) is in range {config.RSI_LONG_MIN}-{config.RSI_LONG_MAX}")
    print(f"   ✓ Volume (1.6x) >= {config.VOLUME_MULTIPLIER}x average")
    print(f"   ✓ Confidence score (75%) >= {config.MIN_CONFIDENCE_SCORE}%")
    
    entry_price = 97500.0
    confidence = 75.0
    take_profit_pct = 0.25  # 0.25% take profit
    stop_loss_pct = 0.20    # 0.20% stop loss
    
    take_profit = entry_price * (1 + take_profit_pct / 100)
    stop_loss = entry_price * (1 - stop_loss_pct / 100)
    
    print(f"\n   📊 TRADE DETAILS:")
    print(f"      Entry Price:        ${entry_price:,.2f}")
    print(f"      Confidence:         {confidence:.1f}%")
    print(f"      Take Profit:        ${take_profit:,.2f} (+{take_profit_pct:.2f}%)")
    print(f"      Stop Loss:          ${stop_loss:,.2f} (-{stop_loss_pct:.2f}%)")
    print(f"      Risk/Reward Ratio:  1:{take_profit_pct/stop_loss_pct:.2f}")
    print(f"      Max Profit:         ${take_profit - entry_price:,.2f} per unit")
    print(f"      Max Loss:           ${entry_price - stop_loss:,.2f} per unit")
    
    # Show example SHORT trade
    print("\n\n📉 EXAMPLE SHORT TRADE (ETH-USD):")
    print("\n   When these conditions are met:")
    print(f"   ✓ Price ($3,400) < EMA ($3,500)")
    print(f"   ✓ RSI (38) is in range {config.RSI_SHORT_MIN}-{config.RSI_SHORT_MAX}")
    print(f"   ✓ Volume (1.7x) >= {config.VOLUME_MULTIPLIER}x average")
    print(f"   ✓ Confidence score (72%) >= {config.MIN_CONFIDENCE_SCORE}%")
    
    entry_price_short = 3400.0
    confidence_short = 72.0
    take_profit_pct_short = 0.30
    stop_loss_pct_short = 0.25
    
    take_profit_short = entry_price_short * (1 - take_profit_pct_short / 100)
    stop_loss_short = entry_price_short * (1 + stop_loss_pct_short / 100)
    
    print(f"\n   📊 TRADE DETAILS:")
    print(f"      Entry Price:        ${entry_price_short:,.2f}")
    print(f"      Confidence:         {confidence_short:.1f}%")
    print(f"      Take Profit:        ${take_profit_short:,.2f} (-{take_profit_pct_short:.2f}%)")
    print(f"      Stop Loss:          ${stop_loss_short:,.2f} (+{stop_loss_pct_short:.2f}%)")
    print(f"      Risk/Reward Ratio:  1:{take_profit_pct_short/stop_loss_pct_short:.2f}")
    print(f"      Max Profit:         ${entry_price_short - take_profit_short:,.2f} per unit")
    print(f"      Max Loss:           ${stop_loss_short - entry_price_short:,.2f} per unit")
    
    print("\n" + "=" * 90)
    print(" HOW IT WORKS ".center(90))
    print("=" * 90)
    print("\n1. Bot continuously monitors all 9 trading pairs")
    print("2. For each pair, calculates:")
    print("   • EMA(50) - Exponential Moving Average")
    print("   • RSI(14) - Relative Strength Index")
    print("   • Volume Ratio - Current volume vs 20-period average")
    print("   • Confidence Score - Composite score based on all factors")
    print("\n3. When ALL conditions align:")
    print("   • Entry condition met (price vs EMA, RSI in range, volume high)")
    print("   • Confidence score >= minimum threshold")
    print("   • Trade signal is generated")
    print("\n4. Trade execution:")
    print("   • Order placed at entry price")
    print("   • Take profit order set (target profit)")
    print("   • Stop loss order set (risk limit)")
    print("   • Position monitored until exit (TP, SL, or 10-minute timeout)")
    print(f"\n⚠️  WHY YOU'RE NOT SEEING TRADES:")
    print(f"   Your settings require ALL 4 conditions to align perfectly:")
    print(f"   • Price vs EMA must be correct")
    print(f"   • RSI must be in tight range ({config.RSI_LONG_MIN}-{config.RSI_LONG_MAX} for long, {config.RSI_SHORT_MIN}-{config.RSI_SHORT_MAX} for short)")
    print(f"   • Volume must be ≥ {config.VOLUME_MULTIPLIER}x average")
    print(f"   • Confidence must be ≥ {config.MIN_CONFIDENCE_SCORE}%")
    print(f"\n   This is RARE in real markets, which is why you're not seeing trades.")
    print(f"   Your strategy is very conservative - only the best setups trigger.")
    print("=" * 90)

if __name__ == '__main__':
    show_example_trades()

