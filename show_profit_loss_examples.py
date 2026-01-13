#!/usr/bin/env python3
"""
Show actual profit/loss examples from trades.
Demonstrates what happens when trades execute - wins, losses, and break-evens.
"""

from datetime import datetime, timedelta
import random

TRADING_PAIRS = ['BTC-USD', 'ETH-USD', 'SOL-USD', 'ADA-USD', 'AVAX-USD', 'XRP-USD', 'DOGE-USD', 'MINA-USD', 'TRUMP-USD']

BASE_PRICES = {
    'BTC-USD': 95000.0, 'ETH-USD': 3500.0, 'SOL-USD': 150.0,
    'ADA-USD': 0.50, 'AVAX-USD': 40.0, 'XRP-USD': 0.60,
    'DOGE-USD': 0.15, 'MINA-USD': 1.20, 'TRUMP-USD': 12.0
}

def show_profit_loss_examples():
    """Show actual profit/loss examples from trades."""
    print("=" * 90)
    print(" PROFIT/LOSS EXAMPLES - What Happens When Trades Execute ".center(90))
    print("=" * 90)
    
    # Example 1: WINNING LONG TRADE
    print("\n\n✅ WINNING TRADE EXAMPLE #1: BTC-USD LONG")
    print("-" * 90)
    entry_price = 97500.0
    position_size = 1.0  # 1 BTC (increased from 0.1)
    take_profit = 97743.75  # +0.25%
    stop_loss = 97305.00  # -0.20%
    
    # Trade hits take profit
    exit_price = take_profit
    exit_reason = "TAKE_PROFIT"
    
    profit = (exit_price - entry_price) * position_size
    profit_pct = ((exit_price - entry_price) / entry_price) * 100
    
    print(f"\n📊 Trade Details:")
    print(f"   Entry Price:        ${entry_price:,.2f}")
    print(f"   Position Size:      {position_size} BTC")
    print(f"   Take Profit:        ${take_profit:,.2f} (+0.25%)")
    print(f"   Stop Loss:          ${stop_loss:,.2f} (-0.20%)")
    print(f"\n💰 Trade Outcome:")
    print(f"   Exit Price:         ${exit_price:,.2f}")
    print(f"   Exit Reason:        {exit_reason} ✅")
    print(f"   Profit:             ${profit:,.2f}")
    print(f"   Profit %:           +{profit_pct:.2f}%")
    print(f"   Return on Trade:     ${profit:,.2f} profit")
    
    # Example 2: LOSING LONG TRADE
    print("\n\n❌ LOSING TRADE EXAMPLE #1: ETH-USD LONG")
    print("-" * 90)
    entry_price_eth = 3500.0
    position_size_eth = 5.0  # 5 ETH (increased from 1.0)
    take_profit_eth = 3508.75  # +0.25%
    stop_loss_eth = 3493.00  # -0.20%
    
    # Trade hits stop loss
    exit_price_eth = stop_loss_eth
    exit_reason_eth = "STOP_LOSS"
    
    loss = (exit_price_eth - entry_price_eth) * position_size_eth
    loss_pct = ((exit_price_eth - entry_price_eth) / entry_price_eth) * 100
    
    print(f"\n📊 Trade Details:")
    print(f"   Entry Price:        ${entry_price_eth:,.2f}")
    print(f"   Position Size:      {position_size_eth} ETH")
    print(f"   Take Profit:        ${take_profit_eth:,.2f} (+0.25%)")
    print(f"   Stop Loss:          ${stop_loss_eth:,.2f} (-0.20%)")
    print(f"\n💰 Trade Outcome:")
    print(f"   Exit Price:         ${exit_price_eth:,.2f}")
    print(f"   Exit Reason:        {exit_reason_eth} ❌")
    print(f"   Loss:               ${loss:,.2f}")
    print(f"   Loss %:             {loss_pct:.2f}%")
    print(f"   Return on Trade:    ${loss:,.2f} loss")
    
    # Example 3: WINNING SHORT TRADE
    print("\n\n✅ WINNING TRADE EXAMPLE #2: SOL-USD SHORT")
    print("-" * 90)
    entry_price_sol = 150.00
    position_size_sol = 100.0  # 100 SOL (increased from 10.0)
    take_profit_sol = 149.55  # -0.30% (price goes down for short)
    stop_loss_sol = 150.38  # +0.25% (price goes up = loss for short)
    
    # Trade hits take profit
    exit_price_sol = take_profit_sol
    exit_reason_sol = "TAKE_PROFIT"
    
    profit_sol = (entry_price_sol - exit_price_sol) * position_size_sol  # Short: profit when price goes down
    profit_pct_sol = ((entry_price_sol - exit_price_sol) / entry_price_sol) * 100
    
    print(f"\n📊 Trade Details:")
    print(f"   Entry Price:        ${entry_price_sol:,.2f}")
    print(f"   Position Size:      {position_size_sol} SOL")
    print(f"   Take Profit:        ${take_profit_sol:,.2f} (-0.30%)")
    print(f"   Stop Loss:          ${stop_loss_sol:,.2f} (+0.25%)")
    print(f"\n💰 Trade Outcome:")
    print(f"   Exit Price:         ${exit_price_sol:,.2f}")
    print(f"   Exit Reason:        {exit_reason_sol} ✅")
    print(f"   Profit:             ${profit_sol:,.2f}")
    print(f"   Profit %:           +{profit_pct_sol:.2f}%")
    print(f"   Return on Trade:     ${profit_sol:,.2f} profit")
    
    # Example 4: TIMEOUT TRADE (exits at current price)
    print("\n\n⏱️  TIMEOUT TRADE EXAMPLE: ADA-USD LONG")
    print("-" * 90)
    entry_price_ada = 0.50
    position_size_ada = 10000.0  # 10,000 ADA (increased from 1,000)
    take_profit_ada = 0.50125  # +0.25%
    stop_loss_ada = 0.499  # -0.20%
    
    # Trade times out after 10 minutes, exits at current price
    exit_price_ada = 0.5005  # Price moved slightly but didn't hit TP or SL
    exit_reason_ada = "TIMEOUT"
    
    pnl_ada = (exit_price_ada - entry_price_ada) * position_size_ada
    pnl_pct_ada = ((exit_price_ada - entry_price_ada) / entry_price_ada) * 100
    
    print(f"\n📊 Trade Details:")
    print(f"   Entry Price:        ${entry_price_ada:,.4f}")
    print(f"   Position Size:      {position_size_ada:,.0f} ADA")
    print(f"   Take Profit:        ${take_profit_ada:,.4f} (+0.25%)")
    print(f"   Stop Loss:          ${stop_loss_ada:,.4f} (-0.20%)")
    print(f"   Time Limit:         10 minutes")
    print(f"\n💰 Trade Outcome:")
    print(f"   Exit Price:         ${exit_price_ada:,.4f}")
    print(f"   Exit Reason:        {exit_reason_ada} ⏱️")
    print(f"   P&L:                ${pnl_ada:,.2f}")
    print(f"   P&L %:              {pnl_pct_ada:+.2f}%")
    print(f"   Return on Trade:     ${pnl_ada:,.2f} (small profit)")
    
    # Example 5: BIG WIN
    print("\n\n🎯 BIG WIN EXAMPLE: AVAX-USD LONG")
    print("-" * 90)
    entry_price_avax = 40.00
    position_size_avax = 250.0  # 250 AVAX (increased from 25.0)
    take_profit_avax = 40.10  # +0.25%
    stop_loss_avax = 39.92  # -0.20%
    
    # Price moves strongly and hits take profit quickly
    exit_price_avax = take_profit_avax
    exit_reason_avax = "TAKE_PROFIT"
    time_held = "2 minutes"
    
    profit_avax = (exit_price_avax - entry_price_avax) * position_size_avax
    profit_pct_avax = ((exit_price_avax - entry_price_avax) / entry_price_avax) * 100
    
    print(f"\n📊 Trade Details:")
    print(f"   Entry Price:        ${entry_price_avax:,.2f}")
    print(f"   Position Size:      {position_size_avax} AVAX")
    print(f"   Take Profit:        ${take_profit_avax:,.2f} (+0.25%)")
    print(f"   Stop Loss:          ${stop_loss_avax:,.2f} (-0.20%)")
    print(f"\n💰 Trade Outcome:")
    print(f"   Exit Price:         ${exit_price_avax:,.2f}")
    print(f"   Exit Reason:        {exit_reason_avax} ✅")
    print(f"   Time Held:          {time_held}")
    print(f"   Profit:             ${profit_avax:,.2f}")
    print(f"   Profit %:           +{profit_pct_avax:.2f}%")
    print(f"   Return on Trade:     ${profit_avax:,.2f} profit")
    
    # Example 6: QUICK LOSS
    print("\n\n💥 QUICK LOSS EXAMPLE: XRP-USD SHORT")
    print("-" * 90)
    entry_price_xrp = 0.60
    position_size_xrp = 5000.0  # 5,000 XRP (increased from 500)
    take_profit_xrp = 0.5982  # -0.30%
    stop_loss_xrp = 0.6015  # +0.25%
    
    # Price moves against us quickly, hits stop loss
    exit_price_xrp = stop_loss_xrp
    exit_reason_xrp = "STOP_LOSS"
    time_held_xrp = "45 seconds"
    
    loss_xrp = (entry_price_xrp - exit_price_xrp) * position_size_xrp  # Short: loss when price goes up
    loss_pct_xrp = ((entry_price_xrp - exit_price_xrp) / entry_price_xrp) * 100
    
    print(f"\n📊 Trade Details:")
    print(f"   Entry Price:        ${entry_price_xrp:,.4f}")
    print(f"   Position Size:      {position_size_xrp:,.0f} XRP")
    print(f"   Take Profit:        ${take_profit_xrp:,.4f} (-0.30%)")
    print(f"   Stop Loss:          ${stop_loss_xrp:,.4f} (+0.25%)")
    print(f"\n💰 Trade Outcome:")
    print(f"   Exit Price:         ${exit_price_xrp:,.4f}")
    print(f"   Exit Reason:        {exit_reason_xrp} ❌")
    print(f"   Time Held:          {time_held_xrp}")
    print(f"   Loss:               ${abs(loss_xrp):,.2f}")
    print(f"   Loss %:             {abs(loss_pct_xrp):.2f}%")
    print(f"   Return on Trade:     ${loss_xrp:,.2f} loss")
    
    # Summary table
    print("\n\n" + "=" * 90)
    print(" SUMMARY - All Trade Examples ".center(90))
    print("=" * 90)
    
    trades = [
        ("BTC-USD LONG", "WIN", profit, profit_pct, "Take Profit"),
        ("ETH-USD LONG", "LOSS", loss, loss_pct, "Stop Loss"),
        ("SOL-USD SHORT", "WIN", profit_sol, profit_pct_sol, "Take Profit"),
        ("ADA-USD LONG", "SMALL WIN", pnl_ada, pnl_pct_ada, "Timeout"),
        ("AVAX-USD LONG", "WIN", profit_avax, profit_pct_avax, "Take Profit"),
        ("XRP-USD SHORT", "LOSS", loss_xrp, loss_pct_xrp, "Stop Loss"),
    ]
    
    print(f"\n{'Pair':<20} {'Result':<12} {'P&L':<15} {'P&L %':<12} {'Exit Reason':<15}")
    print("-" * 90)
    
    total_profit = 0
    total_loss = 0
    wins = 0
    losses = 0
    
    for pair, result, pnl, pnl_pct, reason in trades:
        pnl_str = f"${pnl:,.2f}" if pnl >= 0 else f"-${abs(pnl):,.2f}"
        pnl_pct_str = f"+{pnl_pct:.2f}%" if pnl >= 0 else f"{pnl_pct:.2f}%"
        result_icon = "✅" if result == "WIN" else "❌" if result == "LOSS" else "⚪"
        
        print(f"{pair:<20} {result_icon} {result:<10} {pnl_str:<15} {pnl_pct_str:<12} {reason:<15}")
        
        if pnl > 0:
            total_profit += pnl
            wins += 1
        elif pnl < 0:
            total_loss += abs(pnl)
            losses += 1
    
    print("-" * 90)
    print(f"\n📊 Overall Performance:")
    print(f"   Total Wins:         {wins} trades")
    print(f"   Total Losses:       {losses} trades")
    print(f"   Total Profit:       ${total_profit:,.2f}")
    print(f"   Total Loss:         ${total_loss:,.2f}")
    print(f"   Net P&L:            ${total_profit - total_loss:,.2f}")
    print(f"   Win Rate:           {(wins/(wins+losses)*100):.1f}%")
    
    print("\n💡 KEY TAKEAWAYS:")
    print("   • Trades can win (hit take profit) or lose (hit stop loss)")
    print("   • Some trades timeout after 10 minutes if neither TP nor SL hit")
    print("   • Profit/loss depends on position size and price movement")
    print("   • Risk is limited by stop loss, profit is capped by take profit")
    print("   • Even with good strategy, you'll have both wins and losses")
    print("=" * 90)


if __name__ == '__main__':
    show_profit_loss_examples()

