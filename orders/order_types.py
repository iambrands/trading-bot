"""Advanced order type definitions."""

from enum import Enum
from typing import Dict, Any, Optional
from datetime import datetime


class OrderType(Enum):
    """Types of advanced orders."""
    TRAILING_STOP = "trailing_stop"
    OCO = "oco"  # One-Cancels-Other
    BRACKET = "bracket"
    STOP_LIMIT = "stop_limit"
    ICEBERG = "iceberg"
    STANDARD = "standard"  # Regular market/limit order


class OrderStatus(Enum):
    """Order status."""
    PENDING = "pending"
    ACTIVE = "active"
    FILLED = "filled"
    PARTIALLY_FILLED = "partially_filled"
    CANCELLED = "cancelled"
    REJECTED = "rejected"
    EXPIRED = "expired"


class AdvancedOrder:
    """Base class for advanced orders."""
    
    def __init__(
        self,
        order_id: str,
        order_type: OrderType,
        pair: str,
        side: str,  # BUY or SELL
        size: float,
        status: OrderStatus = OrderStatus.PENDING,
        created_at: Optional[datetime] = None
    ):
        self.order_id = order_id
        self.order_type = order_type
        self.pair = pair
        self.side = side
        self.size = size
        self.status = status
        self.created_at = created_at or datetime.utcnow()
        self.filled_size = 0.0
        self.filled_at: Optional[datetime] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert order to dictionary."""
        return {
            'order_id': self.order_id,
            'order_type': self.order_type.value,
            'pair': self.pair,
            'side': self.side,
            'size': self.size,
            'filled_size': self.filled_size,
            'status': self.status.value,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'filled_at': self.filled_at.isoformat() if self.filled_at else None,
        }
    
    def is_filled(self) -> bool:
        """Check if order is fully filled."""
        return self.status == OrderStatus.FILLED or abs(self.filled_size - self.size) < 0.00000001
    
    def is_active(self) -> bool:
        """Check if order is active."""
        return self.status == OrderStatus.ACTIVE or self.status == OrderStatus.PARTIALLY_FILLED


class TrailingStopOrder(AdvancedOrder):
    """Trailing stop loss order."""
    
    def __init__(
        self,
        order_id: str,
        pair: str,
        side: str,
        size: float,
        trailing_percent: float,  # Percentage to trail
        initial_price: float,
        **kwargs
    ):
        super().__init__(order_id, OrderType.TRAILING_STOP, pair, side, size, **kwargs)
        self.trailing_percent = trailing_percent
        self.initial_price = initial_price
        self.highest_price = initial_price if side == 'SELL' else initial_price
        self.lowest_price = initial_price if side == 'BUY' else initial_price
        self.current_stop_price = self._calculate_stop_price()
    
    def _calculate_stop_price(self) -> float:
        """Calculate current stop price based on trailing percent."""
        if self.side == 'SELL':  # Trailing stop for long position
            trailing_distance = self.highest_price * (self.trailing_percent / 100)
            return self.highest_price - trailing_distance
        else:  # Trailing stop for short position
            trailing_distance = self.lowest_price * (self.trailing_percent / 100)
            return self.lowest_price + trailing_distance
    
    def update_price(self, current_price: float) -> bool:
        """Update order with current price and check if stop should trigger."""
        if self.side == 'SELL':
            if current_price > self.highest_price:
                self.highest_price = current_price
                self.current_stop_price = self._calculate_stop_price()
            return current_price <= self.current_stop_price
        else:
            if current_price < self.lowest_price:
                self.lowest_price = current_price
                self.current_stop_price = self._calculate_stop_price()
            return current_price >= self.current_stop_price
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary with trailing stop specific fields."""
        data = super().to_dict()
        data.update({
            'trailing_percent': self.trailing_percent,
            'initial_price': self.initial_price,
            'highest_price': self.highest_price,
            'lowest_price': self.lowest_price,
            'current_stop_price': self.current_stop_price,
        })
        return data


class OCOOrder(AdvancedOrder):
    """One-Cancels-Other order."""
    
    def __init__(
        self,
        order_id: str,
        pair: str,
        side: str,
        size: float,
        stop_loss_price: float,
        take_profit_price: float,
        **kwargs
    ):
        super().__init__(order_id, OrderType.OCO, pair, side, size, **kwargs)
        self.stop_loss_price = stop_loss_price
        self.take_profit_price = take_profit_price
        self.triggered_order: Optional[str] = None  # Which order triggered
    
    def check_triggers(self, current_price: float) -> Optional[str]:
        """Check if either order should trigger. Returns 'stop_loss' or 'take_profit'."""
        if current_price <= self.stop_loss_price:
            return 'stop_loss'
        elif current_price >= self.take_profit_price:
            return 'take_profit'
        return None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary with OCO specific fields."""
        data = super().to_dict()
        data.update({
            'stop_loss_price': self.stop_loss_price,
            'take_profit_price': self.take_profit_price,
            'triggered_order': self.triggered_order,
        })
        return data


class BracketOrder(AdvancedOrder):
    """Bracket order (entry + stop loss + take profit)."""
    
    def __init__(
        self,
        order_id: str,
        pair: str,
        side: str,
        size: float,
        entry_price: float,
        stop_loss_price: float,
        take_profit_price: float,
        **kwargs
    ):
        super().__init__(order_id, OrderType.BRACKET, pair, side, size, **kwargs)
        self.entry_price = entry_price
        self.stop_loss_price = stop_loss_price
        self.take_profit_price = take_profit_price
        self.entry_filled = False
        self.stop_loss_active = False
        self.take_profit_active = False
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary with bracket specific fields."""
        data = super().to_dict()
        data.update({
            'entry_price': self.entry_price,
            'stop_loss_price': self.stop_loss_price,
            'take_profit_price': self.take_profit_price,
            'entry_filled': self.entry_filled,
            'stop_loss_active': self.stop_loss_active,
            'take_profit_active': self.take_profit_active,
        })
        return data


class StopLimitOrder(AdvancedOrder):
    """Stop limit order."""
    
    def __init__(
        self,
        order_id: str,
        pair: str,
        side: str,
        size: float,
        stop_price: float,
        limit_price: float,
        **kwargs
    ):
        super().__init__(order_id, OrderType.STOP_LIMIT, pair, side, size, **kwargs)
        self.stop_price = stop_price
        self.limit_price = limit_price
        self.stop_triggered = False
    
    def check_stop(self, current_price: float) -> bool:
        """Check if stop price has been hit."""
        if self.side == 'SELL':  # Stop loss for long
            if current_price <= self.stop_price:
                self.stop_triggered = True
                return True
        else:  # Stop loss for short
            if current_price >= self.stop_price:
                self.stop_triggered = True
                return True
        return False
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary with stop limit specific fields."""
        data = super().to_dict()
        data.update({
            'stop_price': self.stop_price,
            'limit_price': self.limit_price,
            'stop_triggered': self.stop_triggered,
        })
        return data


class IcebergOrder(AdvancedOrder):
    """Iceberg order (hidden large order executed in smaller chunks)."""
    
    def __init__(
        self,
        order_id: str,
        pair: str,
        side: str,
        total_size: float,
        visible_size: float,  # Size to show at a time
        limit_price: float,
        **kwargs
    ):
        super().__init__(order_id, OrderType.ICEBERG, pair, side, total_size, **kwargs)
        self.total_size = total_size
        self.visible_size = visible_size
        self.limit_price = limit_price
        self.remaining_size = total_size
        self.current_chunk_size = min(visible_size, self.remaining_size)
        self.remaining_size = total_size
    
    def chunk_filled(self) -> bool:
        """Check if current chunk is filled."""
        return abs(self.current_chunk_size - (self.size - self.remaining_size)) < 0.00000001
    
    def create_next_chunk(self):
        """Create next chunk of the iceberg order."""
        if self.remaining_size > 0:
            self.current_chunk_size = min(self.visible_size, self.remaining_size)
            self.status = OrderStatus.ACTIVE
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary with iceberg specific fields."""
        data = super().to_dict()
        data.update({
            'total_size': self.total_size,
            'visible_size': self.visible_size,
            'limit_price': self.limit_price,
            'remaining_size': self.remaining_size,
            'current_chunk_size': self.current_chunk_size,
        })
        return data

