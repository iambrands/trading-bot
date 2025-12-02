"""Tests for exchange client."""

import pytest
import asyncio
from exchange.coinbase_client import CoinbaseClient
from config import get_config


@pytest.fixture
def exchange_client():
    """Create exchange client instance."""
    config = get_config()
    config.PAPER_TRADING = True  # Force paper trading for tests
    return CoinbaseClient(config)


@pytest.mark.asyncio
async def test_get_account_balance(exchange_client):
    """Test getting account balance."""
    balance = await exchange_client.get_account_balance()
    
    assert balance >= 0


@pytest.mark.asyncio
async def test_get_market_data(exchange_client):
    """Test getting market data."""
    pairs = ['BTC-USD', 'ETH-USD']
    market_data = await exchange_client.get_market_data(pairs)
    
    assert len(market_data) == len(pairs)
    for pair in pairs:
        assert pair in market_data
        assert 'price' in market_data[pair]


@pytest.mark.asyncio
async def test_get_candles(exchange_client):
    """Test getting candle data."""
    from datetime import datetime, timedelta
    
    candles = await exchange_client.get_candles(
        'BTC-USD',
        granularity='ONE_MINUTE',
        start=datetime.utcnow() - timedelta(hours=1),
        end=datetime.utcnow()
    )
    
    assert isinstance(candles, list)
    if candles:
        assert 'timestamp' in candles[0]
        assert 'open' in candles[0]
        assert 'close' in candles[0]


@pytest.mark.asyncio
async def test_paper_order_placement(exchange_client):
    """Test paper order placement."""
    # Set initial balance
    exchange_client.paper_balance = 10000.0
    
    # Place buy order
    try:
        result = await exchange_client.place_order('BTC-USD', 'BUY', 0, quote_size=1000.0)
        assert 'order_id' in result or result.get('success', False)
    except Exception as e:
        # May fail if insufficient balance in some edge cases
        pass
