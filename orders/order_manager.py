"""Advanced order manager for handling complex order types."""

import asyncio
import logging
import uuid
from datetime import datetime
from typing import Dict, List, Optional, Any
from .order_types import (
    AdvancedOrder, TrailingStopOrder, OCOOrder, BracketOrder,
    StopLimitOrder, IcebergOrder, OrderType, OrderStatus
)

logger = logging.getLogger(__name__)


class AdvancedOrderManager:
    """Manages advanced order types."""
    
    def __init__(self, exchange, config=None):
        self.exchange = exchange
        self.config = config
        self.orders: Dict[str, AdvancedOrder] = {}
        self.running = False
        self.monitor_task: Optional[asyncio.Task] = None
    
    async def create_order(self, order_type: str, order_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new advanced order."""
        order_id = str(uuid.uuid4())
        
        try:
            if order_type == OrderType.TRAILING_STOP.value:
                order = TrailingStopOrder(
                    order_id=order_id,
                    pair=order_data['pair'],
                    side=order_data['side'],
                    size=order_data['size'],
                    trailing_percent=order_data['trailing_percent'],
                    initial_price=order_data['initial_price']
                )
            
            elif order_type == OrderType.OCO.value:
                order = OCOOrder(
                    order_id=order_id,
                    pair=order_data['pair'],
                    side=order_data['side'],
                    size=order_data['size'],
                    stop_loss_price=order_data['stop_loss_price'],
                    take_profit_price=order_data['take_profit_price']
                )
            
            elif order_type == OrderType.BRACKET.value:
                order = BracketOrder(
                    order_id=order_id,
                    pair=order_data['pair'],
                    side=order_data['side'],
                    size=order_data['size'],
                    entry_price=order_data['entry_price'],
                    stop_loss_price=order_data['stop_loss_price'],
                    take_profit_price=order_data['take_profit_price']
                )
            
            elif order_type == OrderType.STOP_LIMIT.value:
                order = StopLimitOrder(
                    order_id=order_id,
                    pair=order_data['pair'],
                    side=order_data['side'],
                    size=order_data['size'],
                    stop_price=order_data['stop_price'],
                    limit_price=order_data['limit_price']
                )
            
            elif order_type == OrderType.ICEBERG.value:
                order = IcebergOrder(
                    order_id=order_id,
                    pair=order_data['pair'],
                    side=order_data['side'],
                    total_size=order_data['total_size'],
                    visible_size=order_data['visible_size'],
                    limit_price=order_data['limit_price']
                )
            
            else:
                raise ValueError(f"Unknown order type: {order_type}")
            
            order.status = OrderStatus.ACTIVE
            self.orders[order_id] = order
            
            logger.info(f"Created {order_type} order {order_id} for {order_data['pair']}")
            
            return {
                'success': True,
                'order_id': order_id,
                'order': order.to_dict()
            }
        
        except Exception as e:
            logger.error(f"Failed to create order: {e}", exc_info=True)
            return {
                'success': False,
                'error': str(e)
            }
    
    async def cancel_order(self, order_id: str) -> bool:
        """Cancel an advanced order."""
        if order_id not in self.orders:
            return False
        
        order = self.orders[order_id]
        order.status = OrderStatus.CANCELLED
        
        logger.info(f"Cancelled order {order_id}")
        return True
    
    async def get_order(self, order_id: str) -> Optional[Dict[str, Any]]:
        """Get order details."""
        if order_id not in self.orders:
            return None
        
        return self.orders[order_id].to_dict()
    
    async def list_orders(
        self,
        pair: Optional[str] = None,
        status: Optional[str] = None,
        order_type: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """List orders with optional filtering."""
        orders = []
        
        for order in self.orders.values():
            # Apply filters
            if pair and order.pair != pair:
                continue
            if status and order.status.value != status:
                continue
            if order_type and order.order_type.value != order_type:
                continue
            
            orders.append(order.to_dict())
        
        return orders
    
    async def start_monitoring(self):
        """Start monitoring orders for execution triggers."""
        if self.running:
            return
        
        self.running = True
        self.monitor_task = asyncio.create_task(self._monitor_loop())
        logger.info("Advanced order monitoring started")
    
    async def stop_monitoring(self):
        """Stop monitoring orders."""
        self.running = False
        if self.monitor_task:
            self.monitor_task.cancel()
            try:
                await self.monitor_task
            except asyncio.CancelledError:
                pass
        logger.info("Advanced order monitoring stopped")
    
    async def _monitor_loop(self):
        """Main monitoring loop for advanced orders."""
        while self.running:
            try:
                await self._check_orders()
                await asyncio.sleep(1)  # Check every second
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in order monitoring loop: {e}", exc_info=True)
                await asyncio.sleep(5)
    
    async def _check_orders(self):
        """Check all active orders for triggers."""
        active_orders = [o for o in self.orders.values() if o.is_active()]
        
        for order in active_orders:
            try:
                # Get current market price
                market_data = await self.exchange.get_market_data([order.pair])
                if order.pair not in market_data:
                    continue
                
                current_price = market_data[order.pair].get('price')
                if not current_price:
                    continue
                
                # Check order-specific triggers
                if isinstance(order, TrailingStopOrder):
                    if order.update_price(current_price):
                        await self._execute_trailing_stop(order, current_price)
                
                elif isinstance(order, OCOOrder):
                    triggered = order.check_triggers(current_price)
                    if triggered:
                        await self._execute_oco(order, current_price, triggered)
                
                elif isinstance(order, StopLimitOrder):
                    if order.check_stop(current_price):
                        await self._execute_stop_limit(order, current_price)
                
                elif isinstance(order, IcebergOrder):
                    if order.chunk_filled():
                        order.create_next_chunk()
                
            except Exception as e:
                logger.error(f"Error checking order {order.order_id}: {e}", exc_info=True)
    
    async def _execute_trailing_stop(self, order: TrailingStopOrder, current_price: float):
        """Execute trailing stop order."""
        try:
            logger.info(f"Executing trailing stop order {order.order_id} at {current_price}")
            
            # Place market order
            result = await self.exchange.place_order(
                order.pair,
                order.side,
                order.size
            )
            
            order.status = OrderStatus.FILLED
            order.filled_size = order.size
            order.filled_at = datetime.utcnow()
            
            logger.info(f"Trailing stop order {order.order_id} executed successfully")
            
        except Exception as e:
            logger.error(f"Failed to execute trailing stop order {order.order_id}: {e}", exc_info=True)
            order.status = OrderStatus.REJECTED
    
    async def _execute_oco(self, order: OCOOrder, current_price: float, triggered: str):
        """Execute OCO order."""
        try:
            order.triggered_order = triggered
            
            if triggered == 'stop_loss':
                target_price = order.stop_loss_price
            else:
                target_price = order.take_profit_price
            
            logger.info(f"Executing OCO order {order.order_id} ({triggered}) at {current_price}")
            
            # Place market order
            result = await self.exchange.place_order(
                order.pair,
                order.side,
                order.size
            )
            
            order.status = OrderStatus.FILLED
            order.filled_size = order.size
            order.filled_at = datetime.utcnow()
            
            logger.info(f"OCO order {order.order_id} executed successfully")
            
        except Exception as e:
            logger.error(f"Failed to execute OCO order {order.order_id}: {e}", exc_info=True)
            order.status = OrderStatus.REJECTED
    
    async def _execute_stop_limit(self, order: StopLimitOrder, current_price: float):
        """Execute stop limit order."""
        try:
            logger.info(f"Executing stop limit order {order.order_id} at {current_price}")
            
            # Place limit order at limit price
            # Note: This would need limit order support in exchange client
            # For now, place market order
            result = await self.exchange.place_order(
                order.pair,
                order.side,
                order.size
            )
            
            order.status = OrderStatus.FILLED
            order.filled_size = order.size
            order.filled_at = datetime.utcnow()
            
            logger.info(f"Stop limit order {order.order_id} executed successfully")
            
        except Exception as e:
            logger.error(f"Failed to execute stop limit order {order.order_id}: {e}", exc_info=True)
            order.status = OrderStatus.REJECTED




