"""Tests for risk management."""

import pytest
from risk.risk_manager import RiskManager
from config import get_config


@pytest.fixture
def risk_manager():
    """Create risk manager instance."""
    return RiskManager(get_config())


def test_calculate_position_size_long(risk_manager):
    """Test position sizing for long positions."""
    account_balance = 100000.0
    entry_price = 50000.0
    stop_loss = 49900.0  # $100 stop loss
    
    size = risk_manager.calculate_position_size(
        account_balance,
        entry_price,
        stop_loss,
        'LONG'
    )
    
    # Risk per trade: $100,000 * 0.25% = $250
    # Price difference: $100
    # Expected size: $250 / $100 = 2.5 BTC
    assert size > 0
    assert size <= account_balance / entry_price * 0.5  # Max 50%


def test_calculate_position_size_short(risk_manager):
    """Test position sizing for short positions."""
    account_balance = 100000.0
    entry_price = 50000.0
    stop_loss = 50100.0  # $100 stop loss
    
    size = risk_manager.calculate_position_size(
        account_balance,
        entry_price,
        stop_loss,
        'SHORT'
    )
    
    assert size > 0


def test_validate_trade(risk_manager):
    """Test trade validation."""
    account_balance = 100000.0
    positions = []
    position_size = 0.5
    entry_price = 50000.0
    
    is_valid, message = risk_manager.validate_trade(
        account_balance,
        positions,
        position_size,
        entry_price
    )
    
    assert isinstance(is_valid, bool)
    assert isinstance(message, str)


def test_max_positions_limit(risk_manager):
    """Test maximum positions limit."""
    account_balance = 100000.0
    positions = [
        {'size': 0.5, 'entry_price': 50000.0},
        {'size': 0.5, 'entry_price': 50000.0}
    ]
    position_size = 0.5
    entry_price = 50000.0
    
    is_valid, message = risk_manager.validate_trade(
        account_balance,
        positions,
        position_size,
        entry_price
    )
    
    assert not is_valid
    assert 'maximum positions' in message.lower()


def test_get_risk_metrics(risk_manager):
    """Test risk metrics calculation."""
    account_balance = 100000.0
    positions = [
        {'size': 0.5, 'entry_price': 50000.0, 'stop_loss': 49900.0, 'side': 'LONG'}
    ]
    
    metrics = risk_manager.get_risk_metrics(account_balance, positions)
    
    assert 'total_exposure' in metrics
    assert 'risk_exposure' in metrics
    assert 'daily_pnl' in metrics
    assert 'open_positions' in metrics
