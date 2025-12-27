#!/usr/bin/env python3
"""
Test script to verify backtest flow step by step.
This will help diagnose where the save is failing.
"""
import asyncio
import sys
import json
from datetime import datetime, timedelta

# Add project root to path
sys.path.insert(0, '.')

from config import get_config
from database.db_manager import DatabaseManager
from backtesting import BacktestEngine, HistoricalDataFetcher


async def test_backtest_save():
    """Test backtest execution and save step by step."""
    print("=" * 80)
    print("TESTING BACKTEST FLOW")
    print("=" * 80)
    
    config = get_config()
    db_manager = DatabaseManager(config)
    
    # Step 1: Initialize database
    print("\n[STEP 1] Initializing database...")
    db_initialized = await db_manager.initialize()
    if not db_initialized:
        print("❌ Database initialization failed!")
        return False
    print("✅ Database initialized")
    
    # Step 2: Check initial count
    print("\n[STEP 2] Checking initial backtest count...")
    async with db_manager.pool.acquire() as conn:
        count_before = await conn.fetchval("SELECT COUNT(*) FROM backtests")
        print(f"   Initial count: {count_before}")
    
    # Step 3: Fetch historical data
    print("\n[STEP 3] Fetching historical data...")
    fetcher = HistoricalDataFetcher(config)
    start_date = datetime.utcnow() - timedelta(days=1)
    end_date = datetime.utcnow()
    
    try:
        candles = await asyncio.wait_for(
            fetcher.fetch_candles('BTC-USD', start_date, end_date, granularity='ONE_MINUTE'),
            timeout=30
        )
        print(f"✅ Fetched {len(candles)} candles")
    except Exception as e:
        print(f"❌ Failed to fetch candles: {e}")
        return False
    
    if len(candles) < 100:
        print(f"❌ Insufficient candles: {len(candles)}")
        return False
    
    # Step 4: Run backtest
    print("\n[STEP 4] Running backtest...")
    try:
        engine = BacktestEngine(config, initial_balance=100000.0)
        results = engine.run_backtest(candles, pair='BTC-USD')
        print(f"✅ Backtest completed: {results.get('total_trades', 0)} trades")
    except Exception as e:
        print(f"❌ Backtest failed: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    # Step 5: Prepare backtest data
    print("\n[STEP 5] Preparing backtest data...")
    backtest_data = {
        'name': 'TEST BACKTEST',
        'pair': 'BTC-USD',
        'start_date': start_date,
        'end_date': end_date,
        'initial_balance': 100000.0,
        'final_balance': results.get('final_balance', 100000.0),
        'total_pnl': results.get('total_pnl', 0.0),
        'total_trades': results.get('total_trades', 0),
        'winning_trades': results.get('winning_trades', 0),
        'losing_trades': results.get('losing_trades', 0),
        'win_rate': results.get('win_rate', 0.0),
        'profit_factor': results.get('profit_factor', 0.0),
        'max_drawdown': results.get('max_drawdown', 0.0),
        'roi_pct': results.get('roi_pct', 0.0),
        'results': results
    }
    print(f"✅ Backtest data prepared")
    
    # Step 6: Sanitize data
    print("\n[STEP 6] Sanitizing data (checking for Infinity/NaN/datetime)...")
    def sanitize_value(value):
        import math
        from datetime import datetime, date
        # Handle datetime/date objects
        if isinstance(value, (datetime, date)):
            return value.isoformat()
        elif isinstance(value, float):
            if math.isinf(value) or math.isnan(value):
                return None
        elif isinstance(value, dict):
            return {k: sanitize_value(v) for k, v in value.items()}
        elif isinstance(value, list):
            return [sanitize_value(elem) for elem in value]
        return value
    
    sanitized = sanitize_value(backtest_data['results'])
    backtest_data['results'] = sanitized
    print("✅ Data sanitized")
    
    # Step 7: Try JSON serialization
    print("\n[STEP 7] Testing JSON serialization...")
    try:
        json_str = json.dumps(sanitized)
        print(f"✅ JSON serialization successful (length: {len(json_str)})")
    except Exception as e:
        print(f"❌ JSON serialization failed: {e}")
        return False
    
    # Step 8: Save to database
    print("\n[STEP 8] Saving to database...")
    try:
        user_id = 1
        backtest_id = await db_manager.save_backtest(backtest_data, user_id)
        if backtest_id:
            print(f"✅ Backtest saved! ID: {backtest_id}")
        else:
            print("❌ save_backtest returned None")
            return False
    except Exception as e:
        print(f"❌ Save failed: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    # Step 9: Verify save
    print("\n[STEP 9] Verifying save...")
    async with db_manager.pool.acquire() as conn:
        count_after = await conn.fetchval("SELECT COUNT(*) FROM backtests")
        saved_record = await conn.fetchrow(
            "SELECT id, user_id, name FROM backtests WHERE id = $1",
            backtest_id
        )
        print(f"   Count after save: {count_after} (was {count_before})")
        if saved_record:
            print(f"✅ Record verified: ID={saved_record['id']}, user_id={saved_record['user_id']}, name={saved_record['name']}")
        else:
            print("❌ Record not found in database!")
            return False
    
    # Step 10: Query by user_id
    print("\n[STEP 10] Querying by user_id...")
    backtests = await db_manager.get_backtests(user_id=1, limit=10)
    print(f"   Found {len(backtests)} backtests for user_id=1")
    if len(backtests) > 0:
        print(f"✅ Query successful! Latest: {backtests[0].get('name')}")
    else:
        print("❌ No backtests found for user_id=1")
        return False
    
    print("\n" + "=" * 80)
    print("✅ ALL TESTS PASSED!")
    print("=" * 80)
    return True


if __name__ == '__main__':
    success = asyncio.run(test_backtest_save())
    sys.exit(0 if success else 1)

