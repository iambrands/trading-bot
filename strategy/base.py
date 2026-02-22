"""Base strategy interface and registry for Strategy Marketplace."""

import logging
from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional, Tuple

logger = logging.getLogger(__name__)


class BaseStrategy(ABC):
    """Abstract base class for all trading strategies.
    
    All strategies must implement calculate_indicators and generate_signal.
    Override params_schema for Settings UI and get_params_from_config for config binding.
    """

    # Override in subclasses
    id: str = "base"
    name: str = "Base Strategy"
    description: str = ""
    # Schema for Settings UI: { param_name: { "type": "int"|"float"|"bool", "default": value, "min": x, "max": y } }
    params_schema: Dict[str, Dict[str, Any]] = {}

    def __init__(self, config=None):
        """Initialize with config. Strategies should call get_params_from_config()."""
        self.config = config

    @abstractmethod
    def calculate_indicators(self, candles: List[Dict]) -> Optional[Dict]:
        """Compute technical indicators from candles. Return None if insufficient data."""
        pass

    @abstractmethod
    def generate_signal(self, candles: List[Dict], pair: str = "") -> Optional[Dict]:
        """Generate trading signal. Returns None or dict with:
        { type: 'LONG'|'SHORT', price, confidence, take_profit, stop_loss, indicators }
        """
        pass

    def should_exit(
        self, position: Dict, current_price: float
    ) -> Tuple[bool, Optional[str]]:
        """Check if position should be exited. Default: TP/SL/timeout."""
        signal_type = position.get("signal_type", "LONG")
        entry_price = position.get("entry_price", 0)
        take_profit = position.get("take_profit", 0)
        stop_loss = position.get("stop_loss", 0)
        entry_time = position.get("entry_time")

        if signal_type == "LONG":
            if current_price >= take_profit:
                return True, "take_profit"
            if current_price <= stop_loss:
                return True, "stop_loss"
        else:
            if current_price <= take_profit:
                return True, "take_profit"
            if current_price >= stop_loss:
                return True, "stop_loss"

        if entry_time and self.config:
            from datetime import datetime, timedelta

            timeout_min = getattr(self.config, "POSITION_TIMEOUT_MINUTES", 10)
            if isinstance(entry_time, str):
                entry_time = datetime.fromisoformat(entry_time)
            if datetime.now() - entry_time > timedelta(minutes=timeout_min):
                return True, "timeout"

        return False, None

    def get_default_params(self) -> Dict[str, Any]:
        """Return default param values from schema."""
        return {
            k: v.get("default", 0) for k, v in self.params_schema.items()
        }

    def to_info(self) -> Dict[str, Any]:
        """Serialize for API: id, name, description, params_schema."""
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "params_schema": self.params_schema,
        }


# Strategy Registry
_registry: Dict[str, type] = {}


def register_strategy(cls: type) -> type:
    """Decorator to register a strategy class."""
    if not issubclass(cls, BaseStrategy):
        raise TypeError(f"{cls} must inherit from BaseStrategy")
    inst = cls(config=None)
    _registry[inst.id] = cls
    return cls


def get_strategy(id: str, config=None) -> Optional[BaseStrategy]:
    """Create strategy instance by id."""
    cls = _registry.get(id)
    if cls is None:
        return None
    return cls(config)


def list_strategies() -> List[Dict[str, Any]]:
    """List all registered strategies with metadata."""
    return [cls(config=None).to_info() for cls in _registry.values()]
