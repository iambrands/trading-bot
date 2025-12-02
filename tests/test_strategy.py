"""Tests for trading strategy."""

import pytest
from strategy.ema_rsi_strategy import EMARSIStrategy
from config import get_config


@pytest.fixture
def strategy():
    """Create strategy instance."""
    return EMARSIStrategy(get_config())


@pytest.fixture
def sample_candles():
    """Generate sample candle data."""
    candles = []
    base_price = 50000.0
    for i in range(100):
        candles.append({
            'timestamp': 1000000 + i * 60,
            'open': base_price + i * 10,
            'high': base_price + i * 10 + 50,
            'low': base_price + i * 10 - 50,
            'close': base_price + i * 10 + 20,
            'volume': 1000000 + i * 10000
        })
    return candles


def test_calculate_ema(strategy, sample_candles):
    """Test EMA calculation."""
    prices = [c['close'] for c in sample_candles]
    ema_values = strategy.calculate_ema(prices, 50)
    
    assert len(ema_values) == len(prices)
    assert ema_values[-1] > 0


def test_calculate_rsi(strategy, sample_candles):
    """Test RSI calculation."""
    prices = [c['close'] for c in sample_candles]
    rsi_values = strategy.calculate_rsi(prices, 14)
    
    assert len(rsi_values) == len(prices)
    assert 0 <= rsi_values[-1] <= 100


def test_calculate_volume_avg(strategy, sample_candles):
    """Test volume average calculation."""
    volumes = [c['volume'] for c in sample_candles]
    avg_volume = strategy.calculate_volume_avg(volumes, 20)
    
    assert avg_volume > 0


def test_calculate_indicators(strategy, sample_candles):
    """Test indicator calculation."""
    indicators = strategy.calculate_indicators(sample_candles)
    
    assert 'price' in indicators
    assert 'ema' in indicators
    assert 'rsi' in indicators
    assert 'volume' in indicators
    assert indicators['price'] > 0


def test_generate_signal(strategy, sample_candles):
    """Test signal generation."""
    signal = strategy.generate_signal(sample_candles)
    
    # Signal may or may not be generated depending on conditions
    if signal:
        assert signal['type'] in ['LONG', 'SHORT']
        assert 'price' in signal
        assert 'confidence' in signal
        assert signal['confidence'] >= strategy.min_confidence
