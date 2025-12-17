"""Grid trading strategy manager."""

import asyncio
import logging
import uuid
from datetime import datetime
from typing import Dict, List, Optional, Any
from decimal import Decimal, ROUND_DOWN

logger = logging.getLogger(__name__)


class GridLevel:
    """Represents a single grid level (buy/sell zone)."""
    
    def __init__(self, price: float, side: str, order_id: Optional[str] = None):
        self.price = price
        self.side = side  # 'BUY' or 'SELL'
        self.order_id = order_id
        self.filled = False
        self.filled_at: Optional[datetime] = None
        self.filled_price: Optional[float] = None


class GridStrategy:
    """Grid trading strategy configuration."""
    
    def __init__(
        self,
        grid_id: str,
        pair: str,
        lower_price: float,
        upper_price: float,
        grid_count: int,
        order_size: float,
        side: str = 'BOTH'  # 'BOTH', 'LONG', 'SHORT'
    ):
        self.grid_id = grid_id
        self.pair = pair
        self.lower_price = lower_price
        self.upper_price = upper_price
        self.grid_count = grid_count
        self.order_size = order_size
        self.side = side
        self.grid_spacing = (upper_price - lower_price) / grid_count
        self.levels: List[GridLevel] = []
        self.status = 'active'  # active, paused, stopped
        self.created_at = datetime.utcnow()
        
        # Generate grid levels
        self._generate_levels()
    
    def _generate_levels(self):
        """Generate grid levels based on configuration."""
        self.levels = []
        
        for i in range(self.grid_count + 1):
            price = self.lower_price + (i * self.grid_spacing)
            
            if self.side == 'BOTH':
                # Create both buy and sell levels
                if i < self.grid_count:
                    self.levels.append(GridLevel(price, 'BUY'))
                if i > 0:
                    self.levels.append(GridLevel(price, 'SELL'))
            elif self.side == 'LONG':
                # Only buy levels (accumulating)
                self.levels.append(GridLevel(price, 'BUY'))
            else:  # SHORT
                # Only sell levels (distributing)
                self.levels.append(GridLevel(price, 'SELL'))
    
    def get_next_buy_level(self, current_price: float) -> Optional[GridLevel]:
        """Get next buy level below current price."""
        available_levels = [l for l in self.levels if l.side == 'BUY' and not l.filled and l.price < current_price]
        if available_levels:
            return max(available_levels, key=lambda x: x.price)  # Closest to current price
        return None
    
    def get_next_sell_level(self, current_price: float) -> Optional[GridLevel]:
        """Get next sell level above current price."""
        available_levels = [l for l in self.levels if l.side == 'SELL' and not l.filled and l.price > current_price]
        if available_levels:
            return min(available_levels, key=lambda x: x.price)  # Closest to current price
        return None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert grid strategy to dictionary."""
        return {
            'grid_id': self.grid_id,
            'pair': self.pair,
            'lower_price': float(self.lower_price),
            'upper_price': float(self.upper_price),
            'grid_count': self.grid_count,
            'order_size': float(self.order_size),
            'side': self.side,
            'grid_spacing': float(self.grid_spacing),
            'status': self.status,
            'created_at': self.created_at.isoformat(),
            'levels': [
                {
                    'price': float(l.price),
                    'side': l.side,
                    'filled': l.filled,
                    'order_id': l.order_id,
                    'filled_at': l.filled_at.isoformat() if l.filled_at else None,
                    'filled_price': float(l.filled_price) if l.filled_price else None
                }
                for l in self.levels
            ]
        }


class GridTradingManager:
    """Manages grid trading strategies."""
    
    def __init__(self, exchange, config=None):
        self.exchange = exchange
        self.config = config
        self.grids: Dict[str, GridStrategy] = {}
        self.running = False
        self.monitor_task: Optional[asyncio.Task] = None
    
    async def create_grid(
        self,
        pair: str,
        lower_price: float,
        upper_price: float,
        grid_count: int,
        order_size: float,
        side: str = 'BOTH'
    ) -> Dict[str, Any]:
        """Create a new grid trading strategy."""
        grid_id = str(uuid.uuid4())
        
        try:
            grid = GridStrategy(
                grid_id=grid_id,
                pair=pair,
                lower_price=lower_price,
                upper_price=upper_price,
                grid_count=grid_count,
                order_size=order_size,
                side=side
            )
            
            self.grids[grid_id] = grid
            
            # Place initial orders
            await self._place_initial_orders(grid)
            
            logger.info(f"Created grid strategy {grid_id} for {pair}")
            
            return {
                'success': True,
                'grid_id': grid_id,
                'grid': grid.to_dict()
            }
        
        except Exception as e:
            logger.error(f"Failed to create grid: {e}", exc_info=True)
            return {
                'success': False,
                'error': str(e)
            }
    
    async def _place_initial_orders(self, grid: GridStrategy):
        """Place initial orders for grid levels."""
        # Get current market price
        market_data = await self.exchange.get_market_data([grid.pair])
        if grid.pair not in market_data:
            logger.warning(f"Could not get market price for {grid.pair}")
            return
        
        current_price = market_data[grid.pair].get('price', 0)
        
        # Place orders at levels near current price (within range)
        for level in grid.levels:
            # Only place orders within a reasonable distance from current price
            price_diff_pct = abs((level.price - current_price) / current_price) * 100
            
            if price_diff_pct <= 10:  # Within 10% of current price
                try:
                    # Place limit order (would need limit order support in exchange)
                    # For now, we'll just mark as ready
                    pass
                except Exception as e:
                    logger.warning(f"Failed to place order at {level.price}: {e}")
    
    async def stop_grid(self, grid_id: str) -> bool:
        """Stop a grid trading strategy."""
        if grid_id not in self.grids:
            return False
        
        grid = self.grids[grid_id]
        grid.status = 'stopped'
        
        # Cancel all pending orders
        await self._cancel_all_orders(grid)
        
        logger.info(f"Stopped grid strategy {grid_id}")
        return True
    
    async def pause_grid(self, grid_id: str) -> bool:
        """Pause a grid trading strategy."""
        if grid_id not in self.grids:
            return False
        
        self.grids[grid_id].status = 'paused'
        logger.info(f"Paused grid strategy {grid_id}")
        return True
    
    async def resume_grid(self, grid_id: str) -> bool:
        """Resume a paused grid trading strategy."""
        if grid_id not in self.grids:
            return False
        
        grid = self.grids[grid_id]
        if grid.status == 'paused':
            grid.status = 'active'
            await self._place_initial_orders(grid)
            logger.info(f"Resumed grid strategy {grid_id}")
        return True
    
    async def _cancel_all_orders(self, grid: GridStrategy):
        """Cancel all orders for a grid."""
        for level in grid.levels:
            if level.order_id and not level.filled:
                try:
                    await self.exchange.cancel_order(level.order_id)
                except Exception as e:
                    logger.warning(f"Failed to cancel order {level.order_id}: {e}")
    
    async def get_grid(self, grid_id: str) -> Optional[Dict[str, Any]]:
        """Get grid strategy details."""
        if grid_id not in self.grids:
            return None
        
        return self.grids[grid_id].to_dict()
    
    async def list_grids(
        self,
        pair: Optional[str] = None,
        status: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """List grid strategies with optional filtering."""
        grids = []
        
        for grid in self.grids.values():
            if pair and grid.pair != pair:
                continue
            if status and grid.status != status:
                continue
            
            grids.append(grid.to_dict())
        
        return grids
    
    async def start_monitoring(self):
        """Start monitoring grids for order fills and adjustments."""
        if self.running:
            return
        
        self.running = True
        self.monitor_task = asyncio.create_task(self._monitor_loop())
        logger.info("Grid trading monitoring started")
    
    async def stop_monitoring(self):
        """Stop monitoring grids."""
        self.running = False
        if self.monitor_task:
            self.monitor_task.cancel()
            try:
                await self.monitor_task
            except asyncio.CancelledError:
                pass
        logger.info("Grid trading monitoring stopped")
    
    async def _monitor_loop(self):
        """Main monitoring loop for grid trading."""
        while self.running:
            try:
                await self._check_grids()
                await asyncio.sleep(5)  # Check every 5 seconds
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in grid monitoring loop: {e}", exc_info=True)
                await asyncio.sleep(10)
    
    async def _check_grids(self):
        """Check all active grids for price movements."""
        active_grids = [g for g in self.grids.values() if g.status == 'active']
        
        for grid in active_grids:
            try:
                # Get current market price
                market_data = await self.exchange.get_market_data([grid.pair])
                if grid.pair not in market_data:
                    continue
                
                current_price = market_data[grid.pair].get('price')
                if not current_price:
                    continue
                
                # Check if price has moved to trigger grid levels
                await self._process_grid_levels(grid, current_price)
                
            except Exception as e:
                logger.error(f"Error checking grid {grid.grid_id}: {e}", exc_info=True)
    
    async def _process_grid_levels(self, grid: GridStrategy, current_price: float):
        """Process grid levels and execute trades."""
        # Check for filled orders
        for level in grid.levels:
            if not level.filled and level.order_id:
                # In production, check order status from exchange
                # For now, we'll simulate based on price crossing
                if level.side == 'BUY' and current_price <= level.price:
                    await self._execute_grid_level(grid, level, current_price)
                elif level.side == 'SELL' and current_price >= level.price:
                    await self._execute_grid_level(grid, level, current_price)
    
    async def _execute_grid_level(self, grid: GridStrategy, level: GridLevel, price: float):
        """Execute a grid level trade."""
        try:
            logger.info(f"Executing grid level: {grid.pair} {level.side} at {price}")
            
            # Place market order
            result = await self.exchange.place_order(
                grid.pair,
                level.side,
                grid.order_size
            )
            
            level.filled = True
            level.filled_at = datetime.utcnow()
            level.filled_price = price
            
            # If it was a buy, create a sell order at next level
            # If it was a sell, create a buy order at next level
            if level.side == 'BUY':
                next_sell = grid.get_next_sell_level(price)
                if next_sell:
                    # Place sell order at next level
                    pass
            else:
                next_buy = grid.get_next_buy_level(price)
                if next_buy:
                    # Place buy order at next level
                    pass
            
            logger.info(f"Grid level executed successfully")
            
        except Exception as e:
            logger.error(f"Failed to execute grid level: {e}", exc_info=True)




