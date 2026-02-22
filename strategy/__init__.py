"""Strategy module for trading signals."""

from .base import BaseStrategy, get_strategy, list_strategies, register_strategy
from .ema_rsi_strategy import EMARSIStrategy
from .rsi_only import RSIOnlyStrategy
from .bollinger import BollingerStrategy
from .custom_strategy import CustomStrategy

__all__ = [
    "BaseStrategy",
    "EMARSIStrategy",
    "RSIOnlyStrategy",
    "BollingerStrategy",
    "CustomStrategy",
    "get_strategy",
    "list_strategies",
    "register_strategy",
]
